"""
Multi-Model Training Pipeline with MLflow Tracking
Trains and evaluates: XGBoost, LightGBM, CatBoost, Random Forest, and Neural Network
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple
import logging
import joblib
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import mlflow
import mlflow.sklearn
import mlflow.pytorch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RentDataset(Dataset):
    """PyTorch Dataset for rent prediction"""

    def __init__(self, X, y=None):
        self.X = torch.FloatTensor(X.values if isinstance(X, pd.DataFrame) else X)
        self.y = torch.FloatTensor(y.values if y is not None else np.zeros(len(X)))
        self.has_labels = y is not None

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.has_labels:
            return self.X[idx], self.y[idx]
        return self.X[idx]


class RentNeuralNet(nn.Module):
    """Deep Neural Network for rent prediction"""

    def __init__(self, input_dim: int, hidden_dims: list = [256, 128, 64]):
        super().__init__()
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x).squeeze()


class ModelTrainer:
    """Train and evaluate multiple models with MLflow tracking"""

    def __init__(self, model_path: str = "./saved_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        self.models = {}
        self.results = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")

    def get_models(self) -> Dict[str, Any]:
        """Initialize all model configurations"""
        return {
            'xgboost': xgb.XGBRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=7,
                min_child_weight=3,
                subsample=0.8,
                colsample_bytree=0.8,
                gamma=0.1,
                random_state=42,
                device='cuda' if torch.cuda.is_available() else 'cpu',
                tree_method='hist',
                n_jobs=-1
            ),

            'lightgbm': lgb.LGBMRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=7,
                num_leaves=31,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                device='gpu' if torch.cuda.is_available() else 'cpu',
                n_jobs=-1,
                verbose=-1
            ),

            'catboost': cb.CatBoostRegressor(
                iterations=300,
                learning_rate=0.05,
                depth=7,
                l2_leaf_reg=3,
                random_seed=42,
                task_type='GPU' if torch.cuda.is_available() else 'CPU',
                verbose=False
            ),

            'random_forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            ),

            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=250,
                learning_rate=0.08,
                max_depth=6,
                min_samples_split=20,
                min_samples_leaf=10,
                subsample=0.8,
                random_state=42
            )
        }

    def evaluate_model(
        self,
        model: Any,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Calculate comprehensive evaluation metrics"""
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)

        # Calculate percentage within $100
        within_100 = (np.abs(y_val - y_pred) <= 100).mean() * 100

        # MAPE
        mape = np.mean(np.abs((y_val - y_pred) / y_val)) * 100

        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'within_100': within_100,
            'mape': mape
        }

    def train_neural_network(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        epochs: int = 100,
        batch_size: int = 256
    ) -> Tuple[RentNeuralNet, Dict[str, float]]:
        """Train PyTorch neural network"""
        logger.info("Training Neural Network...")

        # Prepare data
        train_dataset = RentDataset(X_train, y_train)
        val_dataset = RentDataset(X_val, y_val)

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        # Initialize model
        model = RentNeuralNet(input_dim=X_train.shape[1]).to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(epochs):
            # Training
            model.train()
            train_loss = 0
            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)

                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            # Validation
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                    outputs = model(X_batch)
                    val_loss += criterion(outputs, y_batch).item()

            avg_val_loss = val_loss / len(val_loader)
            scheduler.step(avg_val_loss)

            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Val Loss: {avg_val_loss:.2f}")

            # Early stopping
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                torch.save(model.state_dict(), self.model_path / 'neural_net_best.pth')
            else:
                patience_counter += 1
                if patience_counter >= 10:
                    logger.info(f"Early stopping at epoch {epoch+1}")
                    break

        # Load best model
        model.load_state_dict(torch.load(self.model_path / 'neural_net_best.pth'))

        # Evaluate
        model.eval()
        with torch.no_grad():
            X_val_tensor = torch.FloatTensor(X_val.values).to(self.device)
            y_pred = model(X_val_tensor).cpu().numpy()

        metrics = self.evaluate_model(model, X_val, y_val, y_pred)

        return model, metrics

    def train_all_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        use_mlflow: bool = True
    ) -> Dict[str, Dict[str, float]]:
        """Train all models and track with MLflow"""

        results = {}

        if use_mlflow:
            mlflow.set_experiment("sydney_rent_prediction")

        models_config = self.get_models()

        # Train traditional ML models
        for name, model in models_config.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Training {name}...")
            logger.info(f"{'='*50}")

            if use_mlflow:
                with mlflow.start_run(run_name=name):
                    # Train
                    model.fit(X_train, y_train)

                    # Predict
                    y_pred = model.predict(X_val)

                    # Evaluate
                    metrics = self.evaluate_model(model, X_val, y_val, y_pred)

                    # Log to MLflow
                    mlflow.log_params(model.get_params() if hasattr(model, 'get_params') else {})
                    mlflow.log_metrics(metrics)
                    mlflow.sklearn.log_model(model, "model")

                    # Save locally
                    joblib.dump(model, self.model_path / f'{name}.pkl')

                    logger.info(f"{name} Results:")
                    for metric, value in metrics.items():
                        logger.info(f"  {metric}: {value:.4f}")

                    results[name] = metrics
                    self.models[name] = model
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                metrics = self.evaluate_model(model, X_val, y_val, y_pred)
                joblib.dump(model, self.model_path / f'{name}.pkl')
                results[name] = metrics
                self.models[name] = model

        # Train Neural Network
        logger.info(f"\n{'='*50}")
        logger.info("Training Neural Network...")
        logger.info(f"{'='*50}")

        if use_mlflow:
            with mlflow.start_run(run_name='neural_network'):
                nn_model, nn_metrics = self.train_neural_network(X_train, y_train, X_val, y_val)

                mlflow.log_metrics(nn_metrics)
                mlflow.pytorch.log_model(nn_model, "model")

                logger.info("Neural Network Results:")
                for metric, value in nn_metrics.items():
                    logger.info(f"  {metric}: {value:.4f}")

                results['neural_network'] = nn_metrics
                self.models['neural_network'] = nn_model
        else:
            nn_model, nn_metrics = self.train_neural_network(X_train, y_train, X_val, y_val)
            results['neural_network'] = nn_metrics
            self.models['neural_network'] = nn_model

        self.results = results

        # Save results summary
        with open(self.model_path / 'model_comparison.json', 'w') as f:
            json.dump(results, f, indent=2)

        return results

    def get_best_model(self) -> Tuple[str, Any]:
        """Return the best performing model based on MAE"""
        if not self.results:
            raise ValueError("No models trained yet")

        best_name = min(self.results.items(), key=lambda x: x[1]['mae'])[0]
        best_model = self.models[best_name]

        logger.info(f"\nBest model: {best_name} (MAE: {self.results[best_name]['mae']:.2f})")

        return best_name, best_model

    def predict(self, model_name: str, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with a specific model"""
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not found")

        if model_name == 'neural_network':
            model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X.values).to(self.device)
                predictions = model(X_tensor).cpu().numpy()
        else:
            predictions = model.predict(X)

        return predictions
