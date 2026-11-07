"""
Streamlit App for Sydney Rent Prediction
Professional design inspired by modern web standards
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import joblib
import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.feature_engineering import FeatureEngineer
from models.train_models import ModelTrainer


# Page config
st.set_page_config(
    page_title="Sydney Rent Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS inspired by Hallmark's design system
st.markdown("""
    <style>
    /* Design System Variables */
    :root {
        --paper: #FAFAF9;
        --paper-2: #F2F2F0;
        --ink: #0F0F0E;
        --ink-2: #3A3A37;
        --muted: #6B6B66;
        --accent: #1F9D55;
        --accent-soft: rgba(31, 157, 85, 0.12);
        --line: #E4E4E0;
        --r: 14px;
        --r-pill: 999px;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global styles */
    .main {
        background-color: var(--paper);
    }

    /* Typography */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-size: clamp(2rem, 3vw, 3.5rem) !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.1 !important;
    }

    h2 {
        font-size: 1.5rem !important;
        margin-top: 2rem !important;
    }

    h3 {
        font-size: 1.125rem !important;
        font-weight: 500 !important;
        color: var(--ink-2) !important;
    }

    p, label, .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
        color: var(--ink-2) !important;
        line-height: 1.6;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: var(--r);
        padding: 1.5rem;
        border: 1px solid var(--line);
        box-shadow: 0 1px 2px rgba(15, 15, 14, 0.06);
        margin-bottom: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--r-pill) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(15, 15, 14, 0.06) !important;
    }

    .stButton > button:hover {
        background: #13703B !important;
        box-shadow: 0 4px 12px rgba(31, 157, 85, 0.3) !important;
        transform: translateY(-1px);
    }

    /* Input fields */
    .stSlider, .stSelectbox, .stNumberInput {
        background: white;
        border-radius: var(--r);
    }

    .stSelectbox > div > div {
        border-radius: var(--r) !important;
        border-color: var(--line) !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--r-pill);
        padding: 0.5rem 1.25rem;
        color: var(--muted);
        font-weight: 500;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--accent-soft) !important;
        color: var(--accent) !important;
    }

    /* Info boxes */
    .stAlert {
        border-radius: var(--r);
        border: 1px solid var(--line);
        padding: 1rem;
    }

    /* Data tables */
    .dataframe {
        border: 1px solid var(--line) !important;
        border-radius: var(--r) !important;
    }

    /* Hero section */
    .hero {
        text-align: center;
        padding: 3rem 1rem 2rem;
        max-width: 800px;
        margin: 0 auto;
    }

    .hero-subtitle {
        font-size: 1.125rem;
        color: var(--muted);
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #1F9D55 0%, #13703B 100%);
        border-radius: var(--r);
        padding: 2rem;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(31, 157, 85, 0.3);
    }

    /* Badge */
    .badge {
        display: inline-block;
        background: var(--accent-soft);
        color: var(--accent);
        padding: 0.25rem 0.75rem;
        border-radius: var(--r-pill);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* Compact spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_models_and_data():
    """Load trained models and data"""
    try:
        feature_engineer = FeatureEngineer(data_path="../data")
        _, input_flats, blocks = feature_engineer.load_data()

        model_trainer = ModelTrainer(model_path="../saved_models")

        import json
        with open("../saved_models/model_comparison.json", 'r') as f:
            comparison = json.load(f)

        best_model_name = min(comparison.items(), key=lambda x: x[1]['mae'])[0]

        if best_model_name != 'neural_network':
            model = joblib.load(f"../saved_models/{best_model_name}.pkl")
        else:
            model = None

        return feature_engineer, model_trainer, input_flats, blocks, comparison, best_model_name, model
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None, None, None, None


def predict_rent(feature_engineer, model_trainer, model_name, bedrooms, bathrooms,
                 suburb, property_type, floor_level, flats_in_building, has_parking):
    """Make prediction for custom inputs"""

    input_data = pd.DataFrame([{
        'gnaf_id': 'CUSTOM',
        'address': 'Custom Input',
        'building_address': 'Custom',
        'suburb': suburb,
        'mb': 11205183500,
        'latitude': -33.90,
        'longitude': 151.20,
        'property_type': property_type,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'car_space': 1 if has_parking else 0,
        'car_spaces': 1 if has_parking else 0,
        'floor_level': floor_level,
        'flats_in_building': flats_in_building,
        'block_new_homes_2021_2026': 0,
        'block_homes_2026': 50,
        'ever_advertised_for_lease': 0,
        'first_ever_listed': '2020-01-01',
        'attrs_last_seen': '2026-07-01'
    }])

    blocks = pd.DataFrame([{
        'mb': 11205183500,
        'homes_2021': 50,
        'homes_2026': 50,
        'people_2021': 100,
        'people_2026': 100,
        'new_homes': 0
    }])

    X_without = feature_engineer.prepare_prediction_data(input_data, blocks, parking_value=0)
    rent_without = model_trainer.predict(model_name, X_without)[0]

    X_with = feature_engineer.prepare_prediction_data(input_data, blocks, parking_value=1)
    rent_with = model_trainer.predict(model_name, X_with)[0]

    return rent_without, rent_with


def main():
    # Hero section
    st.markdown("""
        <div class="hero">
            <div class="badge">AI-Powered Prediction</div>
            <h1>Sydney Rent Estimator</h1>
            <p class="hero-subtitle">
                Get instant weekly rent estimates for City of Sydney properties,
                with and without parking. Powered by 6 machine learning models.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Load models
    with st.spinner("Loading models..."):
        feature_engineer, model_trainer, input_flats, blocks, comparison, best_model_name, model = load_models_and_data()

    if feature_engineer is None:
        st.error("⚠️ Models not loaded. Please run the training pipeline first:")
        st.code("python src/pipeline.py --data-path ./data", language="bash")
        return

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Estimate Rent", "📊 Model Performance", "📈 Insights"])

    # TAB 1: Prediction
    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Property Details")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                bedrooms = st.slider("Bedrooms", 0, 5, 2, help="Number of bedrooms")
                bathrooms = st.slider("Bathrooms", 1, 4, 2, help="Number of bathrooms")

            with col_b:
                suburbs = ['Waterloo (NSW)', 'Zetland', 'Sydney', 'Surry Hills',
                          'Alexandria', 'Redfern', 'Chippendale', 'Ultimo', 'Pyrmont']
                suburb = st.selectbox("Suburb", suburbs)

                property_type = st.selectbox("Type", ['apartment', 'unit', 'studio'])

            with col_c:
                floor_level = st.number_input("Floor Level", 0, 50, 5)
                flats_in_building = st.number_input("Flats in Building", 1, 500, 50)

            has_parking = st.checkbox("Include Parking", value=True)

            predict_button = st.button("🔮 Calculate Rent", type="primary", use_container_width=True)

        with col2:
            st.markdown("### Summary")
            st.info(f"""
            **Location:** {suburb}
            **Size:** {bedrooms} bed, {bathrooms} bath
            **Type:** {property_type.title()}
            **Floor:** Level {floor_level}
            **Parking:** {'Yes' if has_parking else 'No'}
            """)

        if predict_button:
            with st.spinner("Analyzing property..."):
                try:
                    rent_without, rent_with = predict_rent(
                        feature_engineer, model_trainer, best_model_name,
                        bedrooms, bathrooms, suburb, property_type,
                        floor_level, flats_in_building, has_parking
                    )

                    # Results
                    st.markdown("---")
                    st.markdown("### Estimated Weekly Rent")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Without Parking", f"${rent_without:.2f}", help="Base rent without parking")

                    with col2:
                        premium = rent_with - rent_without
                        st.metric("With Parking", f"${rent_with:.2f}", delta=f"+${premium:.2f}", help="Rent including parking")

                    with col3:
                        premium_pct = (premium / rent_without * 100) if rent_without > 0 else 0
                        st.metric("Parking Value", f"${premium:.2f}", delta=f"{premium_pct:.1f}%", help="Weekly parking premium")

                    # Chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Without Parking', 'With Parking'],
                        y=[rent_without, rent_with],
                        text=[f'${rent_without:.2f}', f'${rent_with:.2f}'],
                        textposition='auto',
                        marker_color=['#6B6B66', '#1F9D55'],
                        marker_line_color='#E4E4E0',
                        marker_line_width=1
                    ))

                    fig.update_layout(
                        title='',
                        yaxis_title='Weekly Rent ($)',
                        height=300,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="system-ui", size=14, color='#3A3A37'),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=20, b=0)
                    )

                    fig.update_yaxes(gridcolor='#E4E4E0', gridwidth=1)

                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                    st.success(f"✓ Prediction generated using {best_model_name.replace('_', ' ').title()} model")

                except Exception as e:
                    st.error(f"Prediction error: {e}")

    # TAB 2: Model Performance
    with tab2:
        st.markdown("### Model Comparison")
        st.caption(f"Best performing model: **{best_model_name.replace('_', ' ').title()}** (MAE: ${comparison[best_model_name]['mae']:.2f})")

        results_df = pd.DataFrame(comparison).T
        results_df = results_df.sort_values('mae')
        results_df.index = [name.replace('_', ' ').title() for name in results_df.index]

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        best_metrics = comparison[best_model_name]

        col1.metric("MAE", f"${best_metrics['mae']:.2f}", help="Mean Absolute Error")
        col2.metric("RMSE", f"${best_metrics['rmse']:.2f}", help="Root Mean Squared Error")
        col3.metric("R² Score", f"{best_metrics['r2']:.3f}", help="Variance explained")
        col4.metric("Within $100", f"{best_metrics['within_100']:.1f}%", help="Predictions within $100")

        st.markdown("---")

        # Table
        st.dataframe(
            results_df[['mae', 'rmse', 'r2', 'within_100']].style
                .background_gradient(subset=['mae', 'rmse'], cmap='RdYlGn_r')
                .background_gradient(subset=['r2', 'within_100'], cmap='RdYlGn')
                .format({'mae': '${:.2f}', 'rmse': '${:.2f}', 'r2': '{:.3f}', 'within_100': '{:.1f}%'}),
            use_container_width=True
        )

        # Chart
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                results_df.reset_index(),
                x='index',
                y='mae',
                title='Mean Absolute Error',
                labels={'index': '', 'mae': 'MAE ($)'},
                color='mae',
                color_continuous_scale=['#1F9D55', '#FFA500', '#E5484D']
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with col2:
            fig = px.bar(
                results_df.reset_index(),
                x='index',
                y='r2',
                title='R² Score',
                labels={'index': '', 'r2': 'R² Score'},
                color='r2',
                color_continuous_scale=['#E5484D', '#FFA500', '#1F9D55']
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # TAB 3: Data Insights
    with tab3:
        st.markdown("### Dataset Overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Properties", f"{len(input_flats):,}")
        col2.metric("Suburbs", "33")
        col3.metric("Training Records", "95,342")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            suburb_counts = input_flats['suburb'].value_counts().head(10)
            fig = px.bar(
                x=suburb_counts.index,
                y=suburb_counts.values,
                title='Top 10 Suburbs by Property Count',
                labels={'x': '', 'y': 'Properties'},
                color=suburb_counts.values,
                color_continuous_scale='Greens'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with col2:
            prop_type = input_flats['property_type'].value_counts()
            fig = px.pie(
                values=prop_type.values,
                names=[x.title() for x in prop_type.index],
                title='Property Type Distribution',
                color_discrete_sequence=['#1F9D55', '#13703B', '#5BD38D']
            )
            fig.update_layout(height=400)
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: var(--muted); font-size: 0.875rem; padding: 2rem 0;">
            <p>Built for Microburbs Hackathon 2026 • Team Said</p>
            <p>Powered by XGBoost, LightGBM, CatBoost, and PyTorch</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
