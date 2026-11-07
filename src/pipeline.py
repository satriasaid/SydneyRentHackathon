"""
Main Pipeline: Train multiple models and generate predictions
"""

import sys
from pathlib import Path
import argparse
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.feature_engineering import FeatureEngineer
from models.train_models import ModelTrainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(data_path: str = "./data", output_path: str = "./", use_mlflow: bool = True):
    """
    Main pipeline for training and prediction

    Args:
        data_path: Path to data directory
        output_path: Path for output files
        use_mlflow: Whether to use MLflow tracking
    """

    logger.info("="*70)
    logger.info("Sydney Rent Prediction - Multi-Model Pipeline")
    logger.info("="*70)

    # Initialize components
    feature_engineer = FeatureEngineer(data_path=data_path)
    model_trainer = ModelTrainer(model_path="./saved_models")

    # Load data
    logger.info("\n[1/5] Loading data...")
    past_leases, input_flats, blocks = feature_engineer.load_data()

    # Prepare training data
    logger.info("\n[2/5] Engineering features...")
    X, y = feature_engineer.prepare_training_data(past_leases, blocks)

    logger.info(f"Feature dimensions: {X.shape}")
    logger.info(f"Target stats - Mean: ${y.mean():.2f}, Median: ${y.median():.2f}")

    # Split data
    logger.info("\n[3/5] Splitting data (80/20)...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info(f"Training samples: {len(X_train):,}")
    logger.info(f"Validation samples: {len(X_val):,}")

    # Train all models
    logger.info("\n[4/5] Training models...")
    results = model_trainer.train_all_models(X_train, y_train, X_val, y_val, use_mlflow=use_mlflow)

    # Print comparison
    logger.info("\n" + "="*70)
    logger.info("MODEL COMPARISON")
    logger.info("="*70)

    results_df = pd.DataFrame(results).T
    results_df = results_df.sort_values('mae')

    print("\n" + results_df.to_string())

    # Get best model
    best_model_name, best_model = model_trainer.get_best_model()

    # Generate predictions with best model
    logger.info(f"\n[5/5] Generating predictions with {best_model_name}...")

    # Predict WITHOUT parking
    logger.info("  - Predicting WITHOUT parking...")
    X_without = feature_engineer.prepare_prediction_data(input_flats, blocks, parking_value=0)
    rent_without = model_trainer.predict(best_model_name, X_without)

    # Predict WITH parking
    logger.info("  - Predicting WITH parking...")
    X_with = feature_engineer.prepare_prediction_data(input_flats, blocks, parking_value=1)
    rent_with = model_trainer.predict(best_model_name, X_with)

    # Ensure with >= without
    rent_with = np.maximum(rent_with, rent_without)

    # Create output
    output = pd.DataFrame({
        'gnaf_id': input_flats['gnaf_id'],
        'rent_with_car_space': np.round(rent_with, 2),
        'rent_without_car_space': np.round(rent_without, 2)
    })

    # Save predictions
    output_file = Path(output_path) / 'rents_said.csv'
    output.to_csv(output_file, index=False)

    logger.info(f"\n✅ Predictions saved to: {output_file}")
    logger.info(f"   Total predictions: {len(output):,}")

    # Statistics
    premium = output['rent_with_car_space'] - output['rent_without_car_space']

    logger.info("\n" + "="*70)
    logger.info("PREDICTION SUMMARY")
    logger.info("="*70)

    logger.info(f"\nRent WITHOUT parking:")
    logger.info(f"  Mean:   ${output['rent_without_car_space'].mean():.2f}")
    logger.info(f"  Median: ${output['rent_without_car_space'].median():.2f}")
    logger.info(f"  Range:  ${output['rent_without_car_space'].min():.2f} - ${output['rent_without_car_space'].max():.2f}")

    logger.info(f"\nRent WITH parking:")
    logger.info(f"  Mean:   ${output['rent_with_car_space'].mean():.2f}")
    logger.info(f"  Median: ${output['rent_with_car_space'].median():.2f}")
    logger.info(f"  Range:  ${output['rent_with_car_space'].min():.2f} - ${output['rent_with_car_space'].max():.2f}")

    logger.info(f"\nParking Premium:")
    logger.info(f"  Mean:   ${premium.mean():.2f}")
    logger.info(f"  Median: ${premium.median():.2f}")
    logger.info(f"  Range:  ${premium.min():.2f} - ${premium.max():.2f}")

    logger.info("\n" + "="*70)
    logger.info("Pipeline completed successfully!")
    logger.info("="*70)

    return output, results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train models and generate predictions')
    parser.add_argument('--data-path', type=str, default='./data', help='Path to data directory')
    parser.add_argument('--output-path', type=str, default='./', help='Path for output files')
    parser.add_argument('--no-mlflow', action='store_true', help='Disable MLflow tracking')

    args = parser.parse_args()

    main(
        data_path=args.data_path,
        output_path=args.output_path,
        use_mlflow=not args.no_mlflow
    )
