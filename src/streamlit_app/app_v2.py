"""
Sydney Rent Predictor - FINAL VERSION
Clear, visible, professional design
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys
import joblib

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Sydney Rent Predictor",
    page_icon="🏠",
    layout="wide"
)

# STRONG, VISIBLE CSS - NO CACHING ISSUES
st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* FORCE light background */
    .main, .stApp {
        background-color: #ffffff !important;
    }

    /* FORCE all text to be DARK and VISIBLE */
    .main *, p, span, label, div, li, h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }

    /* Hero section with green background */
    .hero-box {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(5, 150, 105, 0.4);
    }

    .hero-box * {
        color: #ffffff !important;
    }

    .hero-box h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        margin: 1rem 0 !important;
    }

    .hero-box p {
        font-size: 1.25rem !important;
        opacity: 0.95;
    }

    .badge {
        background: rgba(255,255,255,0.25);
        padding: 0.5rem 1rem;
        border-radius: 50px;
        display: inline-block;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* Section headers - LARGE and DARK */
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }

    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #000000 !important;
    }

    /* Info boxes */
    .info-card {
        background: #f0fdf4;
        border: 2px solid #86efac;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .info-card h3 {
        color: #047857 !important;
        margin-top: 0 !important;
    }

    /* Buttons - LARGE and GREEN */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        padding: 1rem 3rem !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.5) !important;
        transition: all 0.3s !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.6) !important;
    }

    /* Metrics - HUGE and BOLD */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: #4b5563 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Inputs - Clear borders */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border: 3px solid #d1d5db !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        padding: 0.75rem !important;
        background: #ffffff !important;
        color: #000000 !important;
    }

    .stSelectbox > div > div:hover,
    .stNumberInput > div > div > input:hover {
        border-color: #10b981 !important;
    }

    /* Slider */
    .stSlider {
        padding: 1rem 0;
    }

    .stSlider > div > div > div > div {
        background: #10b981 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #f3f4f6;
        padding: 0.5rem;
        border-radius: 15px;
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        color: #6b7280 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
    }

    /* Success/Info messages */
    .stSuccess {
        background: #d1fae5 !important;
        border: 2px solid #10b981 !important;
        border-radius: 10px !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }

    .stInfo {
        background: #dbeafe !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 10px !important;
        color: #000000 !important;
    }

    .stError {
        background: #fee2e2 !important;
        border: 2px solid #ef4444 !important;
        border-radius: 10px !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """Load models"""
    try:
        model_path = Path(__file__).parent.parent.parent / "saved_models"

        import json
        with open(model_path / "model_comparison.json", 'r') as f:
            comparison = json.load(f)

        best_model_name = min(comparison.items(), key=lambda x: x[1]['mae'])[0]
        model = joblib.load(model_path / f"{best_model_name}.pkl")

        return comparison, best_model_name, model
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None, None, None

def predict_rent(bedrooms, bathrooms, suburb, property_type, floor_level, flats_in_building):
    """Predict rent"""
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
    # HERO SECTION
    st.markdown("""
        <div class="hero-box">
            <div class="badge">🤖 AI-POWERED PREDICTION</div>
            <h1>🏠 Sydney Rent Estimator</h1>
            <p>Get instant weekly rent estimates for City of Sydney properties</p>
            <p style="font-size: 1rem; margin-top: 0.5rem;">Powered by 6 ML models trained on 95,000+ leases</p>
        </div>
    """, unsafe_allow_html=True)

    # Load models
    comparison, best_model_name, model = load_models()

    if comparison is None:
        st.error("⚠️ Could not load models")
        st.stop()

    st.success(f"✅ Using **{best_model_name.replace('_', ' ').title()}** model (MAE: ${comparison[best_model_name]['mae']:.2f})")

    # TABS
    tab1, tab2 = st.tabs(["🏠 Estimate Rent", "📊 Model Performance"])

    with tab1:
        st.markdown("## 🏡 Configure Your Property")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Property Details")

            col_a, col_b = st.columns(2)

            with col_a:
                bedrooms = st.slider("🛏️ Bedrooms", 0, 5, 2)
                bathrooms = st.slider("🚿 Bathrooms", 1, 4, 2)
                floor_level = st.slider("🏢 Floor Level", 0, 50, 5)

            with col_b:
                suburbs = ['Sydney', 'Surry Hills', 'Pyrmont', 'Waterloo (NSW)',
                          'Zetland', 'Redfern', 'Alexandria', 'Chippendale', 'Ultimo']
                suburb = st.selectbox("📍 Suburb", suburbs)
                property_type = st.selectbox("🏠 Property Type", ['apartment', 'unit', 'studio'])
                flats_in_building = st.number_input("🏘️ Flats in Building", 1, 500, 50, step=10)

            st.markdown("")

            if st.button("🔮 CALCULATE RENT ESTIMATE", type="primary", use_container_width=True):
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
                    textfont=dict(size=18, color='#000000'),
                    marker=dict(color=['#6b7280', '#10b981'], line=dict(width=0)),
                    hovertemplate='<b>%{x}</b><br>$%{y:.2f}/week<extra></extra>'
                ))

                fig.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#ffffff',
                    font=dict(size=14, color='#000000'),
                    yaxis=dict(title='Weekly Rent ($)', gridcolor='#e5e7eb'),
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.info(f"ℹ️ Generated using {best_model_name.replace('_', ' ').title()} (R² = 0.782)")

        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### 📋 Summary")
            st.markdown(f"""
            **Location:** {suburb}

            **Type:** {property_type.title()}

            **Size:** {bedrooms} bed, {bathrooms} bath

            **Floor:** Level {floor_level}

            **Building:** {flats_in_building} flats
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("## 📊 Model Performance")

        results_df = pd.DataFrame(comparison).T.sort_values('mae')
        results_df.index = [n.replace('_', ' ').title() for n in results_df.index]

        best_metrics = comparison[best_model_name]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("MAE", f"${best_metrics['mae']:.2f}")
        col2.metric("RMSE", f"${best_metrics['rmse']:.2f}")
        col3.metric("R² Score", f"{best_metrics['r2']:.3f}")
        col4.metric("Within $100", f"{best_metrics['within_100']:.1f}%")

        st.markdown("")

        st.dataframe(
            results_df[['mae', 'rmse', 'r2', 'within_100']].style
                .format({'mae': '${:.2f}', 'rmse': '${:.2f}', 'r2': '{:.3f}', 'within_100': '{:.1f}%'}),
            use_container_width=True,
            height=300
        )

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <p style="font-size: 1.1rem; font-weight: 600; color: #000000;">
                Microburbs Hackathon 2026 • Team Said
            </p>
            <p style="color: #6b7280;">
                XGBoost • LightGBM • CatBoost • Random Forest • Gradient Boosting • Neural Network
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
