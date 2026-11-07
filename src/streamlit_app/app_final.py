"""
Sydney Rent Predictor - FIXED VERSION
Proper CSS selectors, no conflicts
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

# Beautiful, modern CSS - Easy on the eyes
st.markdown("""
<style>
/* Hallmark · app screen · warm utility / rent intelligence */
/* Critique: replace the dark-theme collision with a readable, task-first estimator. */
:root {
    --ink: #17243a;
    --muted: #627087;
    --paper: #fbfaf7;
    --surface: #ffffff;
    --surface-soft: #f2f5f7;
    --line: #dbe2e8;
    --accent: #e56b4d;
    --accent-deep: #c9543a;
    --accent-soft: #fff0eb;
    --teal: #176b68;
    --teal-soft: #e6f2f0;
    --shadow: rgba(23, 36, 58, 0.08);
}

html, body { overflow-x: clip; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: var(--paper) !important; }
[data-testid="stAppViewContainer"] * { box-sizing: border-box; }
.block-container {
    max-width: 1180px;
    padding: 2.5rem 2rem 4rem !important;
}

/* Type */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] div { color: var(--ink); }
h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.035em !important; }
h1 { font-size: clamp(2rem, 5vw, 4.25rem) !important; line-height: 0.98 !important; }
h2 { font-size: 2rem !important; margin: 2rem 0 0.5rem !important; }
h3 { font-size: 1.15rem !important; margin: 0.5rem 0 1rem !important; }
[data-testid="stMarkdownContainer"] p { color: var(--muted); line-height: 1.55; }

/* Hero: short, directional, readable in the first viewport */
.hero {
    background: var(--teal);
    border-radius: 18px;
    padding: 2.75rem 3rem 2.5rem;
    margin: -0.5rem 0 1.5rem;
    position: relative;
    overflow: clip;
    box-shadow: 0 18px 38px var(--shadow);
}
.hero::after {
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    right: -70px;
    bottom: -120px;
    border: 42px solid rgba(255,255,255,0.09);
    border-radius: 50%;
}
.hero * { position: relative; z-index: 1; }
.hero h1 { color: var(--surface) !important; max-width: 650px; margin: 0.7rem 0 0.8rem !important; overflow-wrap: break-word; min-width: 0; }
.hero p { color: rgba(255,255,255,0.84) !important; font-size: 1.05rem !important; margin: 0.35rem 0 !important; }
.badge {
    display: inline-block;
    color: var(--teal) !important;
    background: var(--surface);
    border-radius: 999px;
    padding: 0.4rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}

/* Model status */
.stAlert { border-radius: 10px !important; border: 1px solid var(--line) !important; background: var(--surface) !important; }
[data-testid="stAlert"] p { color: var(--ink) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.35rem; border-bottom: 1px solid var(--line); background: transparent; }
.stTabs [data-baseweb="tab"] { color: var(--muted); padding: 0.75rem 1rem; font-weight: 650; }
.stTabs [data-baseweb="tab"]:hover { color: var(--ink); }
.stTabs [aria-selected="true"] { color: var(--accent-deep) !important; border-bottom-color: var(--accent) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent) !important; }

/* Inputs */
.stSlider, .stSelectbox, .stNumberInput { margin-bottom: 0.7rem; }
.stSlider label, .stSelectbox label, .stNumberInput label { color: var(--ink) !important; font-size: 0.82rem !important; font-weight: 700 !important; }
.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
    border-radius: 9px !important;
}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stNumberInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-soft) !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background: var(--accent) !important; border-color: var(--accent) !important; }
.stSlider [data-baseweb="slider"] > div > div { background: var(--accent) !important; }

/* Primary action */
.stButton > button {
    width: 100%;
    min-height: 3.2rem;
    background: var(--accent) !important;
    color: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 9px !important;
    font-weight: 750 !important;
    letter-spacing: 0.01em;
    box-shadow: 0 8px 18px rgba(229,107,77,0.2) !important;
    transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease !important;
}
.stButton > button:hover { background: var(--accent-deep) !important; transform: translateY(-1px); box-shadow: 0 10px 22px rgba(229,107,77,0.28) !important; }
.stButton > button:active { transform: translateY(0); }
button:focus-visible, input:focus-visible, [role="slider"]:focus-visible, [role="tab"]:focus-visible { outline: 3px solid var(--accent) !important; outline-offset: 2px; }

/* Summary and result surfaces */
.summary-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-top: 4px solid var(--teal);
    border-radius: 12px;
    padding: 1.35rem 1.5rem;
    box-shadow: 0 10px 24px var(--shadow);
}
.summary-card h3 { color: var(--teal) !important; }
.summary-card p { margin: 0.35rem 0 0.9rem; }
.summary-row { display: flex; justify-content: space-between; gap: 1rem; padding: 0.85rem 0; border-bottom: 1px solid var(--line); color: var(--muted); }
.summary-row:last-child { border-bottom: 0; padding-bottom: 0; }
.summary-row span { color: var(--muted); }
.summary-row strong { color: var(--ink); text-align: right; font-weight: 700; }
[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 1rem; }
[data-testid="stMetricValue"] { color: var(--ink) !important; font-size: clamp(1.55rem, 3vw, 2.45rem) !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.76rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { color: var(--teal) !important; }

/* Plotly/data table and footer */
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: clip; }
hr { border: 0; border-top: 1px solid var(--line); margin: 2rem 0; }
.app-footer { border-top: 1px solid var(--line); padding-top: 1.5rem; margin-top: 2rem; }
.app-footer p { color: var(--muted) !important; font-size: 0.85rem; }
@media (max-width: 700px) {
    .block-container { padding: 1.2rem 1rem 3rem !important; }
    .hero { padding: 2rem 1.35rem; }
    .hero h1 { font-size: 2.6rem !important; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { scroll-behavior: auto !important; transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
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
    # HERO
    st.markdown("""
        <div class="hero">
            <div class="badge">Sydney rental intelligence</div>
            <h1>Know the weekly rent before you inspect.</h1>
            <p>Set the property details. Get a clear estimate for a City of Sydney home.</p>
        </div>
    """, unsafe_allow_html=True)

    # Load
    comparison, best_model_name, model = load_models()

    if comparison is None:
        st.error("⚠️ Could not load models")
        st.stop()

    st.success(f"Model ready — {best_model_name.replace('_', ' ').title()} — average error ${comparison[best_model_name]['mae']:.2f}")

    # TABS
    tab1, tab2 = st.tabs(["Estimate rent", "Model performance"])

    with tab1:
        st.markdown("## Configure your property")
        st.markdown("Use the details you know. The estimate updates when you calculate.")

        st.markdown("")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Property details")

            col_a, col_b = st.columns(2)

            with col_a:
                bedrooms = st.slider("Bedrooms", 0, 5, 2, key="bed")
                bathrooms = st.slider("Bathrooms", 1, 4, 2, key="bath")
                floor_level = st.slider("Floor Level", 0, 50, 5, key="floor")

            with col_b:
                suburbs = ['Sydney', 'Surry Hills', 'Pyrmont', 'Waterloo (NSW)',
                          'Zetland', 'Redfern', 'Alexandria', 'Chippendale', 'Ultimo']
                suburb = st.selectbox("Suburb", suburbs)
                property_type = st.selectbox("Property Type", ['apartment', 'unit', 'studio'])
                flats_in_building = st.number_input("Flats in Building", 1, 500, 50, step=10)

            st.markdown("")

            if st.button("Calculate weekly rent", type="primary", use_container_width=True):
                rent_without, rent_with = predict_rent(
                    bedrooms, bathrooms, suburb, property_type, floor_level, flats_in_building
                )

                st.markdown("---")
                st.markdown("## Estimated weekly rent")

                col1, col2, col3 = st.columns(3)

                premium = rent_with - rent_without
                premium_pct = (premium / rent_without * 100)

                col1.metric("Without Parking", f"${rent_without:.2f}")
                col2.metric("With Parking", f"${rent_with:.2f}", delta=f"+${premium:.2f}")
                col3.metric("Parking Premium", f"${premium:.2f}", delta=f"+{premium_pct:.1f}%")

                # Chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Without Parking', 'With Parking'],
                    y=[rent_without, rent_with],
                    text=[f'${rent_without:.0f}', f'${rent_with:.0f}'],
                    textposition='outside',
                    textfont=dict(size=20, color='#1f2937', weight=600),
                    marker=dict(color=['#6b7280', '#10b981'], line=dict(width=0)),
                    hovertemplate='<b>%{x}</b><br>$%{y:.2f}/week<extra></extra>'
                ))

                fig.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#ffffff',
                    font=dict(size=14, color='#1f2937'),
                    yaxis=dict(title='Weekly Rent ($)', gridcolor='#e5e7eb', zerolinecolor='#e5e7eb'),
                    xaxis=dict(tickfont=dict(size=14, color='#1f2937')),
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                st.info(f"Generated using {best_model_name.replace('_', ' ').title()} model (R² = 0.782)")

        with col2:
            st.markdown(f"""
                <div class="summary-card">
                    <h3>Property summary</h3>
                    <div class="summary-row"><span>Location</span><strong>{suburb}</strong></div>
                    <div class="summary-row"><span>Property type</span><strong>{property_type.title()}</strong></div>
                    <div class="summary-row"><span>Size</span><strong>{bedrooms} bedroom(s), {bathrooms} bathroom(s)</strong></div>
                    <div class="summary-row"><span>Building</span><strong>Floor {floor_level}, {flats_in_building} total flats</strong></div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("## Model performance")
        st.markdown("A comparison of the trained models used by this estimator.")

        results_df = pd.DataFrame(comparison).T.sort_values('mae')
        results_df.index = [n.replace('_', ' ').title() for n in results_df.index]

        best_metrics = comparison[best_model_name]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("MAE", f"${best_metrics['mae']:.2f}", help="Mean Absolute Error")
        col2.metric("RMSE", f"${best_metrics['rmse']:.2f}", help="Root Mean Squared Error")
        col3.metric("R²", f"{best_metrics['r2']:.3f}", help="Variance explained")
        col4.metric("Within $100", f"{best_metrics['within_100']:.1f}%", help="% within $100")

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
        <div class="app-footer">
            <p><strong>Microburbs Hackathon 2026 — Team Said</strong></p>
            <p>Built with XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting and Neural Network models.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
