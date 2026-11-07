"""
Feature Engineering Pipeline for Sydney Rent Prediction
Handles data loading, cleaning, and feature generation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Production-grade feature engineering pipeline"""

    def __init__(self, data_path: str = "./data"):
        self.data_path = Path(data_path)
        self.feature_names_ = None
        self.top_suburbs_ = None

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all datasets"""
        logger.info("Loading datasets...")

        past_leases = pd.read_csv(self.data_path / 'rents-past-leases-city-of-sydney.csv')
        input_flats = pd.read_csv(self.data_path / 'rents-input-flats-city-of-sydney.csv')
        blocks = pd.read_csv(self.data_path / 'blocks-homes-and-people-2021-2026.csv')

        # Filter to training cutoff date
        past_leases['listing_date'] = pd.to_datetime(past_leases['listing_date'])
        past_leases = past_leases[past_leases['listing_date'] <= '2026-07-31']

        logger.info(f"Past leases: {len(past_leases):,}")
        logger.info(f"Input flats: {len(input_flats):,}")
        logger.info(f"Blocks: {len(blocks):,}")

        return past_leases, input_flats, blocks

    def engineer_features(
        self,
        df: pd.DataFrame,
        blocks: pd.DataFrame,
        parking_value: Optional[int] = None,
        fit: bool = False
    ) -> pd.DataFrame:
        """
        Generate features for modeling

        Args:
            df: Input dataframe
            blocks: Block demographics
            parking_value: Override parking (0=no, 1=yes, None=actual)
            fit: Whether to fit transformers (training only)
        """
        df = df.copy()

        # Merge block data
        blocks_subset = blocks.drop(columns=['suburb'], errors='ignore')
        df = df.merge(blocks_subset, on='mb', how='left')

        # === Parking Features ===
        if 'car_space' not in df.columns and 'car_spaces' in df.columns:
            df['car_space'] = (df['car_spaces'] > 0).astype(float)
        if 'car_space' not in df.columns:
            df['car_space'] = 0.0

        if parking_value is not None:
            df['has_parking'] = parking_value
        else:
            df['has_parking'] = df['car_space'].fillna(0.5)

        # === Basic Property Features ===
        df['bedrooms'] = df['bedrooms'].fillna(df['bedrooms'].median())
        df['bathrooms'] = df['bathrooms'].fillna(df['bathrooms'].median())

        # Floor and building
        for col in ['floor_level', 'flats_in_building']:
            if col not in df.columns:
                df[col] = 0
            else:
                fill_val = df[col].median() if col == 'flats_in_building' else 0
                df[col] = df[col].fillna(fill_val)

        # === Block Demographics ===
        block_cols = ['homes_2021', 'homes_2026', 'people_2021', 'people_2026', 'new_homes']
        for col in block_cols:
            df[col] = df[col].fillna(0)

        # === Derived Features ===
        # Location
        df['dist_from_cbd'] = np.sqrt((df['latitude'] + 33.865)**2 + (df['longitude'] - 151.209)**2)

        # Demographics
        df['people_per_home'] = df['people_2026'] / (df['homes_2026'] + 1)
        df['home_growth_rate'] = (df['homes_2026'] - df['homes_2021']) / (df['homes_2021'] + 1)
        df['density'] = df['flats_in_building'] / (df['homes_2026'] + 1)

        # Property features
        df['rooms_total'] = df['bedrooms'] + df['bathrooms']
        df['bath_bed_ratio'] = df['bathrooms'] / (df['bedrooms'] + 1)

        # Parking interactions
        df['parking_bedrooms'] = df['has_parking'] * df['bedrooms']
        df['parking_bathrooms'] = df['has_parking'] * df['bathrooms']
        df['parking_floor'] = df['has_parking'] * df['floor_level']

        # === Property Type Encoding ===
        df['is_apartment'] = (df['property_type'] == 'apartment').astype(int)
        df['is_unit'] = (df['property_type'] == 'unit').astype(int)
        df['is_studio'] = (df['property_type'] == 'studio').astype(int)

        # === Location: Top Suburbs ===
        if fit:
            self.top_suburbs_ = df['suburb'].value_counts().head(15).index.tolist()

        if self.top_suburbs_ is not None:
            for suburb in self.top_suburbs_:
                df[f'suburb_{suburb}'] = (df['suburb'] == suburb).astype(int)

        # === Spatial Features ===
        # Quadrant (relative to CBD)
        df['north_of_cbd'] = (df['latitude'] > -33.865).astype(int)
        df['east_of_cbd'] = (df['longitude'] > 151.209).astype(int)

        # Distance bins
        df['dist_bin_cbd'] = pd.cut(df['dist_from_cbd'], bins=5, labels=False)

        return df

    def get_feature_columns(self) -> list:
        """Return list of feature columns for modeling"""
        base_features = [
            # Property
            'bedrooms', 'bathrooms', 'rooms_total', 'bath_bed_ratio',
            'has_parking', 'parking_bedrooms', 'parking_bathrooms', 'parking_floor',
            'floor_level', 'flats_in_building',

            # Location
            'latitude', 'longitude', 'dist_from_cbd',
            'north_of_cbd', 'east_of_cbd', 'dist_bin_cbd',

            # Demographics
            'homes_2026', 'people_2026', 'new_homes',
            'people_per_home', 'home_growth_rate', 'density',

            # Property type
            'is_apartment', 'is_unit', 'is_studio',
        ]

        # Add suburb features
        if self.top_suburbs_ is not None:
            suburb_features = [f'suburb_{s}' for s in self.top_suburbs_]
            base_features.extend(suburb_features)

        return base_features

    def prepare_training_data(
        self,
        past_leases: pd.DataFrame,
        blocks: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target for training"""
        # Engineer features
        df = self.engineer_features(past_leases, blocks, parking_value=None, fit=True)

        # Filter to known parking only
        df = df[df['car_space'].notna()].copy()
        logger.info(f"Training samples with known parking: {len(df):,}")

        # Get features and target
        feature_cols = self.get_feature_columns()
        X = df[feature_cols].fillna(0)
        y = df['weekly_rent']

        self.feature_names_ = feature_cols

        return X, y

    def prepare_prediction_data(
        self,
        input_flats: pd.DataFrame,
        blocks: pd.DataFrame,
        parking_value: int
    ) -> pd.DataFrame:
        """Prepare features for prediction"""
        df = self.engineer_features(input_flats, blocks, parking_value=parking_value, fit=False)

        feature_cols = self.get_feature_columns()
        X = df[feature_cols].fillna(0)

        return X
