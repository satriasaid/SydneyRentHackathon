"""
FastAPI Backend for Sydney Rent Prediction
REST API for serving model predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from features.feature_engineering import FeatureEngineer

# Initialize FastAPI
app = FastAPI(
    title="Sydney Rent Prediction API",
    description="AI-powered rent estimation for City of Sydney properties",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and feature engineer
MODEL_PATH = Path("../saved_models/xgboost.pkl")
model = None
feature_engineer = None


@app.on_event("startup")
async def load_model():
    """Load model and feature engineer on startup"""
    global model, feature_engineer

    try:
        model = joblib.load(MODEL_PATH)
        feature_engineer = FeatureEngineer(data_path="../data")
        _, _, blocks = feature_engineer.load_data()

        # Store blocks globally
        app.state.blocks = blocks

        print("✅ Model and feature engineer loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise


class PropertyInput(BaseModel):
    """Property input schema"""
    bedrooms: int = Field(..., ge=0, le=10, description="Number of bedrooms")
    bathrooms: int = Field(..., ge=1, le=5, description="Number of bathrooms")
    suburb: str = Field(..., description="Suburb name")
    property_type: str = Field(..., description="apartment, unit, or studio")
    floor_level: Optional[int] = Field(0, ge=0, le=100, description="Floor level")
    flats_in_building: Optional[int] = Field(50, ge=1, le=1000, description="Flats in building")
    latitude: Optional[float] = Field(-33.90, description="Latitude")
    longitude: Optional[float] = Field(151.20, description="Longitude")

    class Config:
        json_schema_extra = {
            "example": {
                "bedrooms": 2,
                "bathrooms": 2,
                "suburb": "Surry Hills",
                "property_type": "apartment",
                "floor_level": 5,
                "flats_in_building": 50
            }
        }


class PredictionOutput(BaseModel):
    """Prediction output schema"""
    rent_without_parking: float = Field(..., description="Weekly rent without parking")
    rent_with_parking: float = Field(..., description="Weekly rent with parking")
    parking_premium: float = Field(..., description="Parking premium")
    parking_premium_percent: float = Field(..., description="Parking premium as percentage")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Sydney Rent Prediction API",
        "status": "running",
        "model": "XGBoost",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "feature_engineer_loaded": feature_engineer is not None
    }


@app.post("/predict", response_model=PredictionOutput)
async def predict(property_input: PropertyInput):
    """
    Predict weekly rent for a property

    Returns predictions with and without parking
    """
    if model is None or feature_engineer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Create input dataframe
        input_data = pd.DataFrame([{
            'gnaf_id': 'API_REQUEST',
            'address': 'API Input',
            'building_address': 'API',
            'suburb': property_input.suburb,
            'mb': 11205183500,  # Default mesh block
            'latitude': property_input.latitude,
            'longitude': property_input.longitude,
            'property_type': property_input.property_type,
            'bedrooms': property_input.bedrooms,
            'bathrooms': property_input.bathrooms,
            'car_space': 1,
            'car_spaces': 1,
            'floor_level': property_input.floor_level,
            'flats_in_building': property_input.flats_in_building,
            'block_new_homes_2021_2026': 0,
            'block_homes_2026': 50,
            'ever_advertised_for_lease': 0,
            'first_ever_listed': '2020-01-01',
            'attrs_last_seen': '2026-07-01'
        }])

        blocks = app.state.blocks

        # Predict without parking
        X_without = feature_engineer.prepare_prediction_data(input_data, blocks, parking_value=0)
        rent_without = float(model.predict(X_without)[0])

        # Predict with parking
        X_with = feature_engineer.prepare_prediction_data(input_data, blocks, parking_value=1)
        rent_with = float(model.predict(X_with)[0])

        # Ensure with >= without
        rent_with = max(rent_with, rent_without)

        # Calculate premium
        premium = rent_with - rent_without
        premium_percent = (premium / rent_without * 100) if rent_without > 0 else 0

        return PredictionOutput(
            rent_without_parking=round(rent_without, 2),
            rent_with_parking=round(rent_with, 2),
            parking_premium=round(premium, 2),
            parking_premium_percent=round(premium_percent, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/suburbs")
async def get_suburbs():
    """Get list of available suburbs"""
    suburbs = [
        'Alexandria', 'Beaconsfield', 'Camperdown', 'Centennial Park',
        'Chippendale', 'Darlinghurst', 'Darlington', 'Dawes Point',
        'Elizabeth Bay', 'Erskineville', 'Eveleigh', 'Forest Lodge',
        'Glebe', 'Haymarket', 'Kings Cross', 'Millers Point',
        'Moore Park', 'Newtown', 'Paddington', 'Potts Point',
        'Pyrmont', 'Redfern', 'Rosebery', 'Rushcutters Bay',
        'Surry Hills', 'Sydney', 'The Rocks', 'Ultimo',
        'Waterloo (NSW)', 'Woolloomooloo', 'Zetland'
    ]
    return {"suburbs": suburbs}


@app.get("/stats")
async def get_stats():
    """Get model statistics"""
    return {
        "model": "XGBoost",
        "mae": 111.43,
        "rmse": 172.13,
        "r2": 0.782,
        "within_100_percent": 59.6,
        "training_samples": 76273,
        "validation_samples": 19069,
        "features": 40
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
