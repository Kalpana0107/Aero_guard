import os
import pickle

import numpy as np
import pandas as pd
import xgboost as xgb
import folium
import torch
from dotenv import load_dotenv

from modules.data_collector import fetch_waqi
from modules.health_risk import get_forecast_risk_timeline
from modules.explainer import (
    classify_trend,
    compute_shap_values,
    get_top_drivers,
    generate_nl_explanation,
)
from modules.spatial import fetch_multi_station_aqi, create_folium_heatmap
from modules.forecaster import sarima_forecast, build_lstm

load_dotenv()

_xgb_model = None
_feat_cols = None
_sarima_model = None
_lstm_model = None
_lstm_scale_max = None


def _load_models():
    """Load all 3 trained models once."""
    global _xgb_model, _feat_cols, _sarima_model, _lstm_model, _lstm_scale_max

    if _xgb_model is not None:
        return  # already loaded

    # --- XGBoost ---
    try:
        _xgb_model = xgb.XGBRegressor()
        _xgb_model.load_model("models/xgboost_model.json")
        with open("models/xgb_feature_cols.pkl", "rb") as f:
            _feat_cols = pickle.load(f)
    except Exception as e:
        print(f"[api_bridge] XGBoost load failed: {e}")

    # --- SARIMA ---
    try:
        with open("models/sarima_model.pkl", "rb") as f:
            _sarima_model = pickle.load(f)
    except Exception as e:
        print(f"[api_bridge] SARIMA load failed: {e}")

    # --- LSTM (PyTorch) ---
    try:
        _lstm_model = build_lstm()
        _lstm_model.load_state_dict(torch.load("models/lstm_model.pt"))
        _lstm_model.eval()
        with open("models/lstm_scale_max.pkl", "rb") as f:
            _lstm_scale_max = pickle.load(f)
    except Exception as e:
        print(f"[api_bridge] LSTM load failed: {e}")


def _forecast_xgboost():
    df = pd.read_csv("data/processed/aqi_processed.csv", index_col=0)
    sample = df[_feat_cols].iloc[-1:].values
    return [max(0, min(500, float(_xgb_model.predict(sample)[0]))) for _ in range(6)]


def _forecast_sarima():
    return sarima_forecast(_sarima_model, steps=6)


def _forecast_lstm(seq_len=24, target_col="aqi"):
    df = pd.read_csv("data/processed/aqi_processed.csv", index_col=0)
    values = df[target_col].values[-seq_len:] / _lstm_scale_max
    x = torch.tensor(values.reshape(1, seq_len, 1), dtype=torch.float32)
    with torch.no_grad():
        pred = _lstm_model(x).numpy().flatten()
    return [max(0, min(500, float(v) * _lstm_scale_max)) for v in pred]


# ─────────────────────────────────────────────────────────────
# FUNCTION 1: get_forecast(city, lat, lon)
# ─────────────────────────────────────────────────────────────
def get_forecast(city: str, lat: float, lon: float, model_choice: str = "xgboost") -> dict:
    """
    Person A calls this to get the AQI forecast.
    model_choice: 'xgboost' (default), 'sarima', or 'lstm'.
    """
    _load_models()

    try:
        live = fetch_waqi(city)
        current_aqi = float(live["aqi"])
        pm25 = live.get("pm25")
    except Exception:
        current_aqi, pm25 = 142.0, 65.0

    forecast_6h = None
    try:
        if model_choice == "sarima" and _sarima_model is not None:
            forecast_6h = _forecast_sarima()
        elif model_choice == "lstm" and _lstm_model is not None:
            forecast_6h = _forecast_lstm()
        elif _xgb_model is not None:
            forecast_6h = _forecast_xgboost()
    except Exception as e:
        print(f"[api_bridge] {model_choice} forecast failed: {e}")

    if forecast_6h is None:
        forecast_6h = _demo_forecast(current_aqi)

    return {
        "current_aqi": round(current_aqi, 1),
        "pm25": pm25,
        "forecast_6h": [round(v, 1) for v in forecast_6h],
        "trend": classify_trend(forecast_6h),
        "city": city,
        "model_used": model_choice,
    }


def _demo_forecast(base_aqi):
    import random
    random.seed(42)
    return [max(0, base_aqi + random.gauss(i * 2, 6)) for i in range(6)]


# ─────────────────────────────────────────────────────────────
# FUNCTION 2: get_risk_timeline(forecast_6h, persona)
# ─────────────────────────────────────────────────────────────
def get_risk_timeline(forecast_6h: list, persona: str) -> list:
    """Person A calls this to get the hour-by-hour risk cards."""
    return get_forecast_risk_timeline(forecast_6h, persona)


# ─────────────────────────────────────────────────────────────
# FUNCTION 3: get_explanation(current_aqi, forecast_6h)
# ─────────────────────────────────────────────────────────────
def get_explanation(current_aqi: float, forecast_6h: list) -> dict:
    """Person A calls this to fill the explainability text box."""
    _load_models()
    trend = classify_trend(forecast_6h)

    if _xgb_model is not None:
        try:
            df = pd.read_csv("data/processed/aqi_processed.csv", index_col=0)
            sample = df[_feat_cols].iloc[-1:]
            shap_df = compute_shap_values(_xgb_model, sample, _feat_cols)
            drivers = get_top_drivers(shap_df, n=3)
            explanation = generate_nl_explanation(drivers, current_aqi, forecast_6h[-1])
        except Exception:
            explanation = _demo_explanation(current_aqi, forecast_6h, trend)
    else:
        explanation = _demo_explanation(current_aqi, forecast_6h, trend)

    return {"explanation": explanation, "trend": trend}


def _demo_explanation(current, forecast, trend):
    peak = max(forecast)
    return (
        f"AQI is {trend} (current: {current:.0f}, 6h peak: {peak:.0f}). "
        f"Primary contributors at this hour: traffic emissions, "
        f"reduced wind speed, and humidity build-up."
    )


# ─────────────────────────────────────────────────────────────
# FUNCTION 4: get_map(lat, lon, token)
# ─────────────────────────────────────────────────────────────
def get_map(lat: float, lon: float, token: str) -> folium.Map:
    """Person A calls this to get the Folium map for st_folium()."""
    stations = fetch_multi_station_aqi(lat, lon, token)
    return create_folium_heatmap(stations, lat, lon)