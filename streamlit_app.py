# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_excel("pcp_with_affinity.xlsx")

df = load_data()

st.title("CRIS-CROS Experiment Designer")

# --- Map affinity text labels to numeric kD ---
affinity_map = {'low': 59, 'medium': 13, 'high': 2}
df['Affinity_kD'] = df['Affinity'].map(affinity_map)

# Sidebar sliders
st.sidebar.header("Select Parameters")

moles = st.sidebar.select_slider("Moles of surface protein", options=sorted(df['moles_surf.proteins'].unique()))
capture = st.sidebar.select_slider("Capture concentration (µg/ml)", options=sorted(df['capture'].unique()))
probe = st.sidebar.select_slider("Probe concentration (µg/ml)", options=sorted(df['probe'].unique()))
affinity_label = st.sidebar.select_slider("Affinity (kD)", options=['high', 'medium', 'low'], value='medium')
kd = affinity_map[affinity_label]

# --- Filter for exact match ---
exact_match = df[
    (np.isclose(df['moles_surf.proteins'], moles, rtol=0.2)) &
    (np.isclose(df['capture'], capture, rtol=0.2)) &
    (np.isclose(df['probe'], probe, rtol=0.2)) &
    (np.isclose(df['Affinity_kD'], kd, rtol=0.2))
]

st.subheader("Predicted log10(S/N):")
if not exact_match.empty:
    st.success(f"{exact_match['log10_SN1'].values[0]:.2f}")
else:
    st.warning("No exact match found. Try adjusting the sliders.")

# --- Optional: Show nearby parameter space ---
st.subheader("Nearby parameter space (optional)")
tolerance = 0.3
nearby = df[
    (np.isclose(df['moles_surf.proteins'], moles, rtol=tolerance)) &
    (np.isclose(df['capture'], capture, rtol=tolerance)) &
    (np.isclose(df['probe'], probe, rtol=tolerance)) &
    (np.isclose(df['Affinity_kD'], kd, rtol=tolerance))
]

if not nearby.empty:
    st.dataframe(nearby[[
        'moles_surf.proteins', 'capture', 'probe', 'Affinity', 'log10_SN1'
    ]].sort_values('log10_SN1', ascending=False))
else:
    st.info("No nearby points found within tolerance.")

st.subheader("3D Parameter Space Visualization")

fig = px.scatter_3d(
    df,
    x='moles_surf.proteins',
    y='capture',
    z='probe',
    color='log10_SN1',
    symbol='Affinity',
    opacity=0.7
)

st.plotly_chart(fig)