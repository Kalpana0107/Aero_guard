# app.py — AeroGuard Frontend (Final — Day 8)
# Person A owns this file. Calls ONLY api_bridge.py — never modules/ directly.

import os
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from dotenv import load_dotenv

from api_bridge import get_forecast, get_risk_timeline, get_explanation, get_map

load_dotenv()

# Works both locally (.env) and on Streamlit Cloud (Secrets)
try:
    WAQI_TOKEN = st.secrets["WAQI_TOKEN"]
except (FileNotFoundError, KeyError, AttributeError):
    WAQI_TOKEN = os.getenv("WAQI_TOKEN", "")

st.set_page_config(
    page_title="AeroGuard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)
import os
import subprocess
import sys

if not os.path.exists("models/xgboost_model.json"):
    with st.spinner("First-time setup: fetching data & training models (this can take a minute)..."):
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        subprocess.run([sys.executable, "modules/preprocessor.py"], check=True)
        subprocess.run([sys.executable, "modules/forecaster.py"], check=True)

# ---- Custom CSS ----
st.markdown("""
<style>
    [data-testid='stSidebar'] { background: linear-gradient(180deg, #005f5f, #008080); }
    [data-testid='stSidebar'] * { color: white !important; }
    .risk-card {
        border-radius: 10px; padding: 12px 8px; text-align: center;
        background: #f4f6f8; border: 1px solid #d0d7de; margin: 2px;
    }
    .explain-box {
        background: #e0f5f5; border-left: 5px solid #008080;
        border-radius: 6px; padding: 16px; font-size: 14px; line-height: 1.6;
        color: #003333;
    }
    .badge-good { background:#00e400; color:#000; border-radius:12px; padding:2px 10px; }
    .badge-moderate { background:#ffff00; color:#000; border-radius:12px; padding:2px 10px; }
    .badge-sensitive { background:#ff7e00; color:#fff; border-radius:12px; padding:2px 10px; }
    .badge-unhealthy { background:#ff0000; color:#fff; border-radius:12px; padding:2px 10px; }
    .badge-very { background:#8f3f97; color:#fff; border-radius:12px; padding:2px 10px; }
    .badge-hazardous { background:#7e0023; color:#fff; border-radius:12px; padding:2px 10px; }
</style>
""", unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.title("🌫️ AeroGuard")
    st.caption("Hyper-Local Air Quality Forecaster")
    st.divider()

    CITIES = {
        "Mumbai": (19.0760, 72.8777, "mumbai"),
        "Delhi": (28.6139, 77.2090, "delhi"),
        "Pune": (18.5204, 73.8567, "pune"),
        "Chennai": (13.0827, 80.2707, "chennai"),
    }
    city_name = st.selectbox("Select City", list(CITIES.keys()))
    lat, lon, city_code = CITIES[city_name]

    if st.checkbox("Custom coordinates"):
        lat = st.number_input("Latitude", value=lat, format="%.4f")
        lon = st.number_input("Longitude", value=lon, format="%.4f")

    PERSONAS = {
        "General Public": "general",
        "Children / Elderly": "children_elderly",
        "Outdoor Workers": "outdoor_workers",
        "Athletes": "athletes",
    }
    persona_label = st.selectbox("Who are you?", list(PERSONAS.keys()))
    persona = PERSONAS[persona_label]

    model_label = st.selectbox("Forecast model", ["XGBoost", "SARIMA", "LSTM"])
    model_choice = model_label.lower()

    if st.button("▶ Generate Forecast", use_container_width=True):
        st.session_state.forecast_generated = True
        st.session_state.city_name = city_name
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.session_state.city_code = city_code
        st.session_state.persona = persona
        st.session_state.persona_label = persona_label
        st.session_state.model_choice = model_choice

# ---- Main area ----
if not st.session_state.get("forecast_generated", False):
    st.title("🌫️ AeroGuard")
    st.info("👈 Select your city and persona in the sidebar, then click **Generate Forecast**.")
else:
    # Pull the values that were locked in at the moment the button was clicked
    city_name = st.session_state.city_name
    lat = st.session_state.lat
    lon = st.session_state.lon
    city_code = st.session_state.city_code
    persona = st.session_state.persona
    persona_label = st.session_state.persona_label
    model_choice = st.session_state.model_choice

    st.title(f"🌫️ AeroGuard — {city_name}")

    with st.spinner("Fetching live AQI & running forecast..."):
        result = get_forecast(city_code, lat, lon, model_choice=model_choice)

    # ---- Metrics row ----
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current AQI", result["current_aqi"])
    c2.metric("PM2.5", f"{result.get('pm25', 'N/A')} µg/m³")
    c3.metric("6h Peak AQI", f"{max(result['forecast_6h']):.0f}")
    c4.metric("Trend", result["trend"].capitalize())
    st.caption(f"Model used: **{result.get('model_used', model_choice).upper()}**")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📊 Forecast & Risk", "🗺️ City Heatmap", "🧠 Why is AQI High?"])

    # =====================================================================
    # TAB 1 — Forecast chart + Risk cards
    # =====================================================================
    with tab1:
        st.subheader(f"6-Hour Forecast — {persona_label}")

        AQI_COLORS = [
            (50, "#00e400"), (100, "#ffff00"), (150, "#ff7e00"),
            (200, "#ff0000"), (300, "#8f3f97"), (500, "#7e0023"),
        ]

        def aqi_color(val):
            for threshold, color in AQI_COLORS:
                if val <= threshold:
                    return color
            return "#7e0023"

        hours = list(range(1, 7))
        values = result["forecast_6h"]
        bar_colors = [aqi_color(v) for v in values]

        fig, ax = plt.subplots(figsize=(10, 3.5))
        bars = ax.bar(hours, values, color=bar_colors, edgecolor="#333", linewidth=0.8, width=0.6)

        ax.axhline(100, color="#ff7e00", linestyle="--", alpha=0.7, linewidth=1.2,
                   label="Sensitive group threshold (100)")
        ax.axhline(150, color="#ff0000", linestyle="--", alpha=0.7, linewidth=1.2,
                   label="Unhealthy threshold (150)")

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 3, f"{val:.0f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

        ax.set_ylabel("AQI", fontsize=10)
        ax.set_title(f"Forecasted AQI — {city_name}", fontsize=11, fontweight="bold")
        ax.legend(fontsize=8)
        ax.set_facecolor("#f8f9fa")
        fig.patch.set_facecolor("#f8f9fa")
        ax.spines[["top", "right"]].set_visible(False)

        st.pyplot(fig)
        plt.close(fig)

        # ---- Real risk timeline from api_bridge ----
        timeline = get_risk_timeline(result["forecast_6h"], persona)

        st.subheader("Hour-by-Hour Risk")
        cols = st.columns(6)
        badge_map = {
            "Good": "badge-good", "Moderate": "badge-moderate",
            "Unhealthy (Sensitive)": "badge-sensitive",
            "Unhealthy": "badge-unhealthy",
            "Very Unhealthy": "badge-very", "Hazardous": "badge-hazardous",
        }
        for col, risk in zip(cols, timeline):
            css = badge_map.get(risk["category"], "badge-unhealthy")
            with col:
                st.markdown(f"""
                <div class='risk-card'>
                    <div style='font-weight:bold;'>{risk['hour_offset']}</div>
                    <div style='font-size:22px;font-weight:bold;'>{risk['aqi']}</div>
                    <span class='{css}'>{risk['category']}</span>
                </div>
                """, unsafe_allow_html=True)

        worst = max(timeline, key=lambda x: x["aqi"])
        st.info(f"📌 **{persona_label} Advice ({worst['hour_offset']}):** {worst['advice']}")

    # =====================================================================
    # TAB 2 — Real Heatmap from api_bridge.get_map()
    # =====================================================================
    with tab2:
        st.subheader("City AQI Heatmap")
        with st.spinner("Generating map..."):
            m = get_map(lat, lon, WAQI_TOKEN)
        st_folium(m, width=720, height=460)
        st.caption(f"AQI monitoring stations within ~20km of {city_name}. Hotter colors = higher pollution.")

    # =====================================================================
    # TAB 3 — Real Explanation from api_bridge.get_explanation()
    # =====================================================================
    with tab3:
        exp_data = get_explanation(result["current_aqi"], result["forecast_6h"])

        st.subheader("Why is AQI Changing?")
        st.markdown(f"<div class='explain-box'>{exp_data['explanation']}</div>",
                    unsafe_allow_html=True)
        st.caption("Powered by SHAP (SHapley Additive exPlanations) — XGBoost model")

        trend_desc = {
            "persistent": "📈 AQI will keep rising — plan indoor activities.",
            "temporary": "📉 AQI peaks then improves — wait it out if possible.",
            "fluctuating": "↔️ Mixed signals — check again in 2 hours.",
            "unknown": "❓ Not enough data for trend classification.",
        }
        st.info(trend_desc.get(exp_data["trend"], ""))