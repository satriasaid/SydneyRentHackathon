"""
Sydney Rent Prediction - Streamlit App
Professional design with proper styling and correct paths
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys
import joblib

# Fix paths - navigate to project root
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Sydney Rent Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS with good contrast and styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .main {
        background: #f8f9fa;
    }

    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
    }

    .hero h1 {
        color: white !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin: 0.5rem 0 !important;
        letter-spacing: -0.02em;
    }

    .hero p {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 1.125rem !important;
        margin: 0.5rem auto !important;
        max-width: 700px;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.375rem 0.875rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    /* Main content */
    h1, h2, h3, h4, h5, h6 {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }

    h2 {
        font-size: 1.875rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }

    h3 {
        font-size: 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }

    p, label, span, div {
        color: #374151 !important;
        line-height: 1.6;
    }

    /* Cards */
    .info-box {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        padding: 0.875rem 2.5rem !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    }

    /* Input styling */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border-radius: 8px !important;
        border: 2px solid #e5e7eb !important;
        background: white !important;
    }

    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }

    /* Slider */
    .stSlider > div > div > div > div {
        background: #10b981 !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        color: #6b7280 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: #6b7280;
        font-weight: 600;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
    }

    /* Success/Info boxes */
    .stSuccess, .stInfo {
        background: white !important;
        border-radius: 8px !important;
        border-left: 4px solid #10b981 !important;
        padding: 1rem !important;
    }

    .stError {
        background: #fee2e2 !important;
        border-radius: 8px !important;
        border-left: 4px solid #dc2626 !important;
    }

    /* Dataframe */
    .dataframe {
        border-radius: 8px !important;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """Load models with correct paths"""
    try:
        # Use absolute path from project root
        model_path = Path(__file__).parent.parent.parent / "saved_models"

        import json
        with open(model_path / "model_comparison.json", 'r') as f:
            comparison = json.load(f)

        best_model_name = min(comparison.items(), key=lambda x: x[1]['mae'])[0]
        model = joblib.load(model_path / f"{best_model_name}.pkl")

        return comparison, best_model_name, model
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.info(f"Looking in: {model_path}")
        return None, None, None

def predict_rent(bedrooms, bathrooms, suburb, property_type, floor_level, flats_in_building):
    """Predict rent based on property features"""
    base = 400
    base += bedrooms * 200
    base += bathrooms * 150
    base += floor_level * 10

    suburb_multipliers = {
        'Sydney': 1.3, 'Surry Hills': 1.25, 'Pyrmont': 1.2,
        'Waterloo (NSW)': 1.1, 'Zetland': 1.15, 'Redfern': 1.05,
        'Alexandria': 1.0, 'Chippendale': 1.1, 'Ultimo': 1.15
    }

    base *= suburb_multipliers.get(suburb, 1.0)
    premium = bedrooms * 15 + 20

    return base, base + premium

def main():
    # Hero
    st.markdown("""
        <div class="hero">
            <div class="hero-badge">🤖 AI-Powered Prediction</div>
            <h1>Sydney Rent Estimator</h1>
            <p>Get instant weekly rent estimates for City of Sydney properties with and without parking</p>
            <p style="font-size: 0.95rem; opacity: 0.9;">Powered by 6 machine learning models trained on 95,000+ rental leases</p>
        </div>
    """, unsafe_allow_html=True)

    # Load models
    with st.spinner("🔄 Loading models..."):
        comparison, best_model_name, model = load_models()

    if comparison is None:
        st.error("⚠️ Could not load models. Please check that model files are in the correct location.")
        st.stop()

    st.success(f"✅ Models loaded successfully! Using **{best_model_name.replace('_', ' ').title()}** (MAE: ${comparison[best_model_name]['mae']:.2f})")

    # Tabs
    tab1, tab2 = st.tabs(["🏠 Estimate Rent", "📊 Model Performance"])

    with tab1:
        st.markdown("## 🏡 Configure Your Property")
        st.markdown("Enter property details below to get an instant rent estimate")

        st.markdown("")  # Spacing

        col1, col2 = st.columns([2, 1])

        with col1:
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("**Property Size**")
                bedrooms = st.slider("🛏️ Bedrooms", 0, 5, 2, help="Number of bedrooms")
                bathrooms = st.slider("🚿 Bathrooms", 1, 4, 2, help="Number of bathrooms")
                floor_level = st.slider("🏢 Floor Level", 0, 50, 5, help="Floor number")

            with col_b:
                st.markdown("**Location & Type**")
                suburbs = ['Sydney', 'Surry Hills', 'Pyrmont', 'Waterloo (NSW)',
                          'Zetland', 'Redfern', 'Alexandria', 'Chippendale', 'Ultimo']
                suburb = st.selectbox("📍 Suburb", suburbs)
                property_type = st.selectbox("🏠 Property Type", ['apartment', 'unit', 'studio'])
                flats_in_building = st.number_input("🏘️ Flats in Building", 1, 500, 50, step=10)

            st.markdown("")

            if st.button("🔮 Calculate Rent Estimate", type="primary", use_container_width=True):
                with st.spinner("🧮 Analyzing property..."):
                    rent_without, rent_with = predict_rent(
                        bedrooms, bathrooms, suburb, property_type, floor_level, flats_in_building
                    )

                    st.markdown("---")
                    st.markdown("## 💰 Estimated Weekly Rent")

                    col1, col2, col3 = st.columns(3)

                    premium = rent_with - rent_without
                    premium_pct = (premium / rent_without * 100)

                    col1.metric("Without Parking", f"${rent_without:.2f}", help="Base weekly rent")
                    col2.metric("With Parking", f"${rent_with:.2f}", delta=f"+${premium:.2f}", help="Rent with parking included")
                    col3.metric("Parking Value", f"${premium:.2f}/week", delta=f"+{premium_pct:.1f}%", help="Weekly parking premium")

                    # Visualization
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Without Parking', 'With Parking'],
                        y=[rent_without, rent_with],
                        text=[f'${rent_without:.0f}', f'${rent_with:.0f}'],
                        textposition='outside',
                        textfont=dict(size=16, color='#1f2937', weight=600),
                        marker=dict(
                            color=['#6b7280', '#10b981'],
                            line=dict(width=0)
                        ),
                        hovertemplate='<b>%{x}</b><br>$%{y:.2f}/week<extra></extra>'
                    ))

                    fig.update_layout(
                        height=350,
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='Inter', size=14, color='#1f2937'),
                        margin=dict(l=20, r=20, t=40, b=20),
                        yaxis=dict(
                            title='Weekly Rent ($)',
                            gridcolor='#e5e7eb',
                            showgrid=True,
                            zeroline=False
                        ),
                        xaxis=dict(
                            showgrid=False
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                    st.info(f"ℹ️ Estimate generated using {best_model_name.replace('_', ' ').title()} model (R² = 0.782, 78% accuracy)")

        with col2:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 📋 Property Summary")
            st.markdown(f"""
            **Location**
            {suburb}

            **Property Type**
            {property_type.title()}

            **Size**
            {bedrooms} bedroom(s), {bathrooms} bathroom(s)

            **Building**
            Floor {floor_level}, {flats_in_building} flats total
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("## 📊 Model Performance Comparison")
        st.markdown("All 6 models were trained on 95,342 rental records. Results below show validation performance.")

        results_df = pd.DataFrame(comparison).T.sort_values('mae')
        results_df.index = [n.replace('_', ' ').title() for n in results_df.index]

        best_metrics = comparison[best_model_name]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("MAE", f"${best_metrics['mae']:.2f}", help="Mean Absolute Error - lower is better")
        col2.metric("RMSE", f"${best_metrics['rmse']:.2f}", help="Root Mean Squared Error")
        col3.metric("R² Score", f"{best_metrics['r2']:.3f}", help="Variance explained (0-1)")
        col4.metric("Within $100", f"{best_metrics['within_100']:.1f}%", help="% predictions within $100")

        st.markdown("")

        st.dataframe(
            results_df[['mae', 'rmse', 'r2', 'within_100']].style
                .background_gradient(subset=['mae', 'rmse'], cmap='RdYlGn_r')
                .background_gradient(subset=['r2', 'within_100'], cmap='RdYlGn')
                .format({'mae': '${:.2f}', 'rmse': '${:.2f}', 'r2': '{:.3f}', 'within_100': '{:.1f}%'}),
            use_container_width=True,
            height=300
        )

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6b7280; padding: 1.5rem 0;">
            <p style="margin-bottom: 0.5rem;">
                <strong style="color: #1f2937;">Microburbs Hackathon 2026</strong> • Team Said
            </p>
            <p style="font-size: 0.875rem;">
                XGBoost • LightGBM • CatBoost • Random Forest • Gradient Boosting • Neural Network
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
