# modules/explainer.py
import shap
import pandas as pd
import numpy as np


def compute_shap_values(model, X: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Runs SHAP's TreeExplainer against the trained XGBoost model.
    Returns one row per sample, one column per feature, values = each
    feature's contribution (positive = pushed AQI up, negative = pushed it down).
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    return pd.DataFrame(shap_values, columns=feature_cols)


def get_top_drivers(shap_df: pd.DataFrame, n: int = 3) -> list:
    """
    Ranks features by absolute SHAP impact on the most recent row and
    returns the top N as (feature_name, direction, magnitude) tuples.
    """
    last_row = shap_df.iloc[-1]
    ranked = last_row.reindex(last_row.abs().sort_values(ascending=False).index)
    drivers = []
    for feature, value in ranked.head(n).items():
        direction = "increasing" if value > 0 else "decreasing"
        drivers.append((feature, direction, abs(round(value, 2))))
    return drivers


FEATURE_LABELS = {
    "aqi_lag_1": "AQI one hour ago",
    "aqi_lag_24": "AQI at this time yesterday",
    "wind_speed": "wind speed",
    "humidity": "humidity",
    "hour_sin": "time of day",
    "is_weekend": "weekend effect",
    "aqi_rolling_mean_6": "the 6-hour average trend",
}


def generate_nl_explanation(drivers: list, current_aqi: float, forecast_peak: float) -> str:
    """Converts SHAP driver tuples into a plain-English sentence."""
    parts = []
    for feature, direction, _ in drivers:
        label = FEATURE_LABELS.get(feature, feature.replace("_", " "))
        parts.append(f"{label} ({direction} the forecast)")

    driver_text = ", ".join(parts)
    trend_word = "rising" if forecast_peak > current_aqi else "falling"
    return (
        f"AQI is currently {current_aqi:.0f} and is {trend_word} toward a "
        f"6-hour peak of {forecast_peak:.0f}. The main contributors are: {driver_text}."
    )


def classify_trend(forecast_6h: list) -> str:
    """
    Buckets the 6-hour forecast shape into one of three labels the
    frontend uses for its trend badge and messaging.
    """
    if len(forecast_6h) < 2:
        return "unknown"

    diffs = np.diff(forecast_6h)
    if np.all(diffs >= -2):        # roughly monotonic upward (small noise tolerated)
        return "persistent"
    if forecast_6h[-1] < max(forecast_6h) - 10:
        return "temporary"          # rises then meaningfully falls back
    return "fluctuating"


if __name__ == "__main__":
    import xgboost as xgb
    import pickle

    model = xgb.XGBRegressor()
    model.load_model("models/xgboost_model.json")

    with open("models/xgb_feature_cols.pkl", "rb") as f:
        feature_cols = pickle.load(f)

    df = pd.read_csv("data/processed/aqi_processed.csv", index_col=0)
    sample = df[feature_cols].iloc[-5:]
    shap_df = compute_shap_values(model, sample, feature_cols)
    drivers = get_top_drivers(shap_df, n=3)
    print(generate_nl_explanation(drivers, current_aqi=142, forecast_peak=158))