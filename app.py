# app.py — Day 2: full skeleton with dummy data
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="AeroGuard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS — teal gradient sidebar, styled cards
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
    }
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

    PERSONAS = {
        "General Public": "general",
        "Children / Elderly": "children_elderly",
        "Outdoor Workers": "outdoor_workers",
        "Athletes": "athletes",
    }
    persona_label = st.selectbox("Who are you?", list(PERSONAS.keys()))
    persona = PERSONAS[persona_label]

    run = st.button("▶ Generate Forecast", use_container_width=True)

# ---- Main area ----
st.title(f"🌫️ AeroGuard — {city_name}")

if run:
    # DUMMY DATA — replaced with real api_bridge calls at Sync 1 (Day 4)
    dummy_forecast = [78, 82, 91, 105, 98, 87]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current AQI", dummy_forecast[0])
    c2.metric("PM2.5", "42 µg/m³")
    c3.metric("6h Peak AQI", max(dummy_forecast))
    c4.metric("Trend", "Fluctuating")

    tab1, tab2, tab3 = st.tabs(["📊 Forecast & Risk", "🗺️ City Heatmap", "🧠 Why is AQI High?"])

    with tab1:
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.bar(range(1, 7), dummy_forecast, color="#ff7e00")
        ax.set_title(f"Forecasted AQI — {city_name} (dummy data)")
        st.pyplot(fig)

    with tab2:
        st.info("Heatmap arrives Day 7, once spatial.py is ready.")

    with tab3:
        st.info("Explanation text arrives Day 6, once explainer.py is ready.")

else:
    st.info("👈 Select your city and persona, then click Generate Forecast.")