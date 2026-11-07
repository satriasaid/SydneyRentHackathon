# 🚀 Quick Start Guide

## Project Overview

Production-grade ML system for predicting Sydney rental prices with:
- **6 trained models** (XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, Neural Network)
- **GPU acceleration** (CUDA support)
- **Interactive web app** (Streamlit)
- **REST API** (FastAPI)
- **MLflow tracking** (Experiment management)

**Best Model:** XGBoost with MAE of $111.43

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (optional, for acceleration)
- 4GB+ RAM
- 1GB disk space

### Setup

```bash
# Clone repository (or use existing)
cd SydneyRentHackathon

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 Usage

### 1. Train Models (Already Done!)

Models are already trained and saved in `saved_models/`. To retrain:

```bash
python3 src/pipeline.py --data-path ./data --output-path ./
```

**Output:**
- `rents_said.csv` - 65,777 predictions
- `saved_models/*.pkl` - Trained models
- `saved_models/model_comparison.json` - Performance metrics

### 2. Launch Streamlit Web App

```bash
cd src/streamlit_app
streamlit run app.py
```

Opens at `http://localhost:8501`

**Features:**
- 🔮 **Predict Tab:** Interactive rent calculator
- 📊 **Model Performance:** Compare all 6 models
- 📈 **Data Insights:** Dataset visualizations

### 3. Launch FastAPI Backend

```bash
cd src/api
python3 main.py
```

API at `http://localhost:8000`

**Endpoints:**
- `GET /` - Health check
- `POST /predict` - Get rent prediction
- `GET /suburbs` - List available suburbs
- `GET /stats` - Model statistics
- `GET /docs` - Interactive API documentation

#### Example API Usage

```bash
# Using curl
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 2,
    "bathrooms": 2,
    "suburb": "Surry Hills",
    "property_type": "apartment",
    "floor_level": 5,
    "flats_in_building": 50
  }'

# Response:
# {
#   "rent_without_parking": 850.50,
#   "rent_with_parking": 890.75,
#   "parking_premium": 40.25,
#   "parking_premium_percent": 4.73
# }
```

```python
# Using Python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "bedrooms": 2,
        "bathrooms": 2,
        "suburb": "Surry Hills",
        "property_type": "apartment",
        "floor_level": 5,
        "flats_in_building": 50
    }
)

prediction = response.json()
print(f"Rent without parking: ${prediction['rent_without_parking']}/week")
print(f"Rent with parking: ${prediction['rent_with_parking']}/week")
print(f"Parking premium: ${prediction['parking_premium']}/week")
```

---

## 📊 Model Performance

| Model | MAE ($) | R² | Within $100 |
|-------|---------|-----|-------------|
| **XGBoost** ⭐ | **111.43** | **0.782** | **59.6%** |
| Gradient Boosting | 113.24 | 0.775 | 58.9% |
| Random Forest | 113.44 | 0.772 | 59.2% |
| LightGBM | 115.69 | 0.766 | 58.0% |
| CatBoost | 120.58 | 0.753 | 55.9% |
| Neural Network | 127.54 | 0.721 | 53.4% |

---

## 📁 Project Structure

```
SydneyRentHackathon/
├── src/
│   ├── features/
│   │   └── feature_engineering.py    # Feature pipeline
│   ├── models/
│   │   └── train_models.py          # Multi-model trainer
│   ├── api/
│   │   └── main.py                  # FastAPI backend
│   ├── streamlit_app/
│   │   └── app.py                   # Streamlit web app
│   └── pipeline.py                  # Main training script
│
├── data/                            # Training data
│   ├── rents-past-leases-city-of-sydney.csv
│   ├── rents-input-flats-city-of-sydney.csv
│   └── blocks-homes-and-people-2021-2026.csv
│
├── saved_models/                    # Trained models
│   ├── xgboost.pkl                 # Best model
│   ├── lightgbm.pkl
│   ├── catboost.pkl
│   ├── random_forest.pkl
│   ├── gradient_boosting.pkl
│   ├── neural_net_best.pth
│   └── model_comparison.json
│
├── requirements.txt                 # Dependencies
├── setup.sh                        # Setup script
├── README.md                       # Full documentation
├── QUICKSTART.md                   # This file
└── TRAINING_RESULTS.md            # Training summary
```

---

## 🎨 Screenshots

### Streamlit App
- **Predict Tab:** Enter property details, get instant rent predictions
- **Model Performance:** Visual comparison of all models
- **Data Insights:** Explore the dataset

### FastAPI
- **Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🔧 Customization

### Use Different Model

```python
# In Streamlit or API, change model loading:
model = joblib.load('saved_models/lightgbm.pkl')  # Use LightGBM instead
```

### Retrain with Custom Parameters

Edit `src/models/train_models.py`:

```python
'xgboost': xgb.XGBRegressor(
    n_estimators=500,      # More trees
    learning_rate=0.03,    # Slower learning
    max_depth=8,           # Deeper trees
    ...
)
```

Then retrain:
```bash
python3 src/pipeline.py --data-path ./data
```

---

## 🐛 Troubleshooting

### Issue: CUDA not available

**Solution:** Models automatically fall back to CPU. To force GPU:
```python
import torch
print(torch.cuda.is_available())  # Should be True
```

### Issue: Import errors

**Solution:** Ensure you're in the project root and virtual environment is activated:
```bash
source venv/bin/activate
cd SydneyRentHackathon
```

### Issue: Streamlit won't start

**Solution:**
```bash
cd src/streamlit_app
streamlit run app.py --server.port 8501
```

### Issue: Model file not found

**Solution:** Train models first:
```bash
python3 src/pipeline.py --data-path ./data
```

---

## 📚 Next Steps

1. ✅ **Explore Streamlit App** - Interactive predictions
2. ✅ **Test FastAPI** - Build integrations
3. ✅ **Review Training Results** - See `TRAINING_RESULTS.md`
4. 🎬 **Create Demo Video** - For hackathon submission
5. 🚀 **Deploy to Cloud** - Streamlit Cloud, Heroku, or AWS

---

## 💡 Key Features

- **Multi-model comparison** - 6 models trained automatically
- **GPU acceleration** - 3-5× faster with CUDA
- **Production-ready** - Error handling, logging, validation
- **Interactive UI** - Streamlit for demos
- **REST API** - FastAPI for integrations
- **MLflow tracking** - Experiment management
- **Reproducible** - Complete pipeline

---

## 🏆 Hackathon Deliverables

✅ **rents_said.csv** - 65,777 predictions  
✅ **report.html** - Methodology report  
✅ **README.md** - Full documentation  
✅ **Source code** - Production-grade  
✅ **Web app** - Streamlit demo  
✅ **API** - FastAPI backend  
✅ **Multiple models** - 6 trained models  

---

## 📞 Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review `TRAINING_RESULTS.md` for model details
3. Check logs in console output

---

**Built with ❤️ for Microburbs Hackathon 2026**
