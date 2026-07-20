import os
import pickle

import numpy as np
import pandas as pd
import xgboost as xgb
from dotenv import load_dotenv

from modules.data_collector import fetch_waqi

load_dotenv()

_model = None
_feat_cols = None


def _load_models():
    """
    Load the trained XGBoost model and feature list only once.
    """

    global _model, _feat_cols

    if _model is not None:
        return

    try:
        _model = xgb.XGBRegressor()
        _model.load_model("models/xgboost_model.json")

        with open("models/xgb_feature_cols.pkl", "rb") as f:
            _feat_cols = pickle.load(f)

    except Exception as e:
        print(f"[api_bridge] Model load failed: {e}. Using demo mode.")


def get_forecast(
    city: str,
    lat: float,
    lon: float,
) -> dict:
    """
    Person A calls this function to obtain an AQI forecast.
    No ML implementation details are exposed.
    """

    _load_models()

    try:
        live = fetch_waqi(city)

        current_aqi = float(live["aqi"])
        pm25 = live.get("pm25")

    except Exception:
        # Demo fallback if WAQI is unavailable
        current_aqi = 142.0
        pm25 = 65.0

    if _model is not None:
        try:
            df = pd.read_csv(
                "data/processed/aqi_processed.csv",
                index_col=0,
            )

            sample = df[_feat_cols].iloc[-1:].values

            forecast_6h = [
                max(
                    0,
                    min(
                        500,
                        float(_model.predict(sample)[0]),
                    ),
                )
                for _ in range(6)
            ]

        except Exception:
            forecast_6h = _demo_forecast(current_aqi)

    else:
        forecast_6h = _demo_forecast(current_aqi)

    return {
        "current_aqi": round(current_aqi, 1),
        "pm25": pm25,
        "forecast_6h": [
            round(v, 1) for v in forecast_6h
        ],
        "trend": "fluctuating",
        "city": city,
    }


def _demo_forecast(base_aqi):
    """
    Generate a demo forecast when the ML model
    or live API is unavailable.
    """

    import random

    random.seed(42)

    return [
        max(
            0,
            base_aqi + random.gauss(i * 2, 6),
        )
        for i in range(6)
    ]