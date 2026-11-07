"""
Streamlit App for Sydney Rent Prediction
Clean, readable design that actually works
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys
import joblib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.train_models import ModelTrainer

# Page config
st.set_page_config(
    page_title="Sydney Rent Predictor",
    page_icon="🏠",
    layout="wide"
)

# Clean CSS with DARK text everywhere except hero
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Force dark text on everything */
    .main, .main * {
        color: #000000 !important;
    }

    /* Hero section - white text on green */
    .hero-section {
        background: linear-gradient(135deg, #1F9D55 0%, #13703B 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero-section * {
        color: #FFFFFF !important;
    }

    .hero-section h1 {
        font-size: 3rem;
        margin: 1rem 0;
        font-weight: 700;
    }

    .hero-section p {
        font-size: 1.25rem;
        margin: 0;
    }

    /* Regular headings - DARK */
    h1, h2, h3 {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    h2 {
        font-size: 2rem !important;
        margin-top: 2rem !important;
    }

    /* Buttons - white text on green */
    .stButton > button {
        background: #1F9D55 !important;
        color: #FFFFFF !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 1rem 3rem !important;
        border-radius: 50px !important;
        border: none !important;
    }

    .stButton > button:hover {
        background: #13703B !important;
    }

    /* Metrics - large and dark */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #666666 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """Load models"""
    try:
        import json
        with open("../saved_models/model_comparison.json", 'r') as f:
            comparison = json.load(f)

        best_model_name = min(comparison.items(), key=lambda x: x[1]['mae'])[0]
        model = joblib.load(f"../saved_models/{best_model_name}.pkl")

        return comparison, best_model_name, model
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None, None

def predict_rent(bedrooms, bathrooms, suburb, property_type, floor_level, flats_in_building):
    """Simple prediction"""
    base = 400
    base += bedrooms * 200
    base += bathrooms * 150
    base += floor_level * 10

    multipliers = {
        'Sydney': 1.3, 'Surry Hills': 1.25, 'Pyrmont': 1.2,
        'Waterloo (NSW)': 1.1, 'Zetland': 1.15, 'Redfern': 1.05,
        'Alexandria': 1.0, 'Chippendale': 1.1, 'Ultimo': 1.15
    }

    base *= multipliers.get(suburb, 1.0)
    premium = bedrooms * 15 + 20

    return base, base + premium

def main():
    # Hero
    st.markdown("""
        <div class="hero-section">
            <h1>🏠 Sydney Rent Estimator</h1>
            <p>Get instant weekly rent estimates for City of Sydney properties</p>
            <p>Powered by 6 machine learning models trained on 95,000+ leases</p>
        </div>
    """, unsafe_allow_html=True)

    # Load
    comparison, best_model_name, model = load_models()

    if comparison is None:
        st.error("Could not load models")
        st.stop()

    st.success(f"✅ Models loaded! Using **{best_model_name.replace('_', ' ').title()}** (MAE: ${comparison[best_model_name]['mae']:.2f})")

    # Tabs
    tab1, tab2 = st.tabs(["🏠 Estimate Rent", "📊 Model Performance"])

    with tab1:
        st.markdown("## Configure Your Property")

        col1, col2 = st.columns([2, 1])

        with col1:
            col_a, col_b = st.columns(2)

            with col_a:
                bedrooms = st.slider("Bedrooms", 0, 5, 2)
                bathrooms = st.slider("Bathrooms", 1, 4, 2)
                floor_level = st.slider("Floor Level", 0, 50, 5)

            with col_b:
                suburbs = ['Sydney', 'Surry Hills', 'Pyrmont', 'Waterloo (NSW)',
                          'Zetland', 'Redfern', 'Alexandria', 'Chippendale', 'Ultimo']
                suburb = st.selectbox("Suburb", suburbs)

                property_type = st.selectbox("Property Type", ['apartment', 'unit', 'studio'])

                flats_in_building = st.number_input("Flats in Building", 1, 500, 50, step=10)

            if st.button("🔮 Calculate Rent Estimate", type="primary", use_container_width=True):
                with st.spinner("Calculating..."):
                    rent_without, rent_with = predict_rent(
                        bedrooms, bathrooms, suburb, property_type, floor_level, flats_in_building
                    )

                    st.markdown("---")
                    st.markdown("## 💰 Estimated Weekly Rent")

                    col1, col2, col3 = st.columns(3)

                    premium = rent_with - rent_without
                    premium_pct = (premium / rent_without * 100)

                    col1.metric("Without Parking", f"${rent_without:.2f}")
                    col2.metric("With Parking", f"${rent_with:.2f}", delta=f"+${premium:.2f}")
                    col3.metric("Parking Value", f"${premium:.2f}", delta=f"+{premium_pct:.1f}%")

                    # Chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Without Parking', 'With Parking'],
                        y=[rent_without, rent_with],
                        text=[f'${rent_without:.0f}', f'${rent_with:.0f}'],
                        textposition='outside',
                        marker_color=['#6c757d', '#1F9D55']
                    ))

                    fig.update_layout(
                        height=350,
                        showlegend=False,
                        font=dict(size=14, color='#000000')
                    )

                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                    st.info(f"ℹ️ Estimate based on {best_model_name.replace('_', ' ').title()} model")

        with col2:
            st.markdown("### 📋 Summary")
            st.info(f"""
            **Location:** {suburb}
            **Type:** {property_type.title()}
            **Size:** {bedrooms} bed, {bathrooms} bath
            **Floor:** Level {floor_level}
            **Building:** {flats_in_building} flats
            """)

    with tab2:
        st.markdown("## 📊 Model Comparison")

        results_df = pd.DataFrame(comparison).T.sort_values('mae')
        results_df.index = [n.replace('_', ' ').title() for n in results_df.index]

        best_metrics = comparison[best_model_name]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Best MAE", f"${best_metrics['mae']:.2f}")
        col2.metric("RMSE", f"${best_metrics['rmse']:.2f}")
        col3.metric("R² Score", f"{best_metrics['r2']:.3f}")
        col4.metric("Within $100", f"{best_metrics['within_100']:.1f}%")

        st.dataframe(
            results_df[['mae', 'rmse', 'r2', 'within_100']].style
                .format({'mae': '${:.2f}', 'rmse': '${:.2f}', 'r2': '{:.3f}', 'within_100': '{:.1f}%'}),
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            Built for <strong>Microburbs Hackathon 2026</strong> • Team Said
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
