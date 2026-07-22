import pandas as pd 
import numpy as np 
def load_and_merge(aqi_df: pd.DataFrame, weather_df: pd.DataFrame = None) -> pd.DataFrame: 
    """Merge AQI history with weather data on timestamp (if weather provided).""" 
    df = aqi_df.copy().set_index("timestamp").sort_index() 
    if weather_df is not None: 
        w = weather_df.copy().set_index("timestamp").sort_index() 
        df = df.join(w, how="left")
    return df 
def handle_missing(df: pd.DataFrame) -> pd.DataFrame: 
    """ Forward-fill short gaps (sensor dropout for a few hours), then back-fill any remaining gap at the very start of the series. """ 
    df = df.ffill(limit=3)   # only trust forward-fill for short gaps 
    df = df.bfill()          # covers leading NaNs 
    return df.dropna()       # drop anything still missing (rare) 
def add_time_features(df: pd.DataFrame) -> pd.DataFrame: 
    """ Pollution has strong daily rhythm: traffic rush hours, overnight stagnation. These cyclical features let tree/NN models learn that 23:00 and 00:00 are numerically close, unlike raw hour-of-day (23 vs 0). """ 
    df = df.copy() 
    hour = df.index.hour 
    df["hour_sin"] = np.sin(2 * np.pi * hour / 24) 
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24) 
    df["day_of_week"] = df.index.dayofweek 
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int) 
    return df 
def add_lag_features(df: pd.DataFrame, target_col: str = "aqi", lags=(1, 2, 3, 6, 24)) -> pd.DataFrame: 
    """ Adds "AQI N hours ago" columns. Air quality is highly autocorrelated — the single strongest predictor of AQI right now is AQI an hour ago. """ 
    df = df.copy() 
    for lag in lags: 
        df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag) 
    df["aqi_rolling_mean_6"] = df[target_col].rolling(6).mean() 
    df["aqi_rolling_std_6"] = df[target_col].rolling(6).std() 
    return df.dropna()   # lag features create NaNs in the first N rows 

def normalize(df: pd.DataFrame, cols: list) -> tuple: 
    """ Min-max scales the given columns to [0, 1]. Returns the scaled df AND the scaler stats, so we can inverse-transform predictions later. """ 
    df = df.copy() 
    stats = {} 
    for col in cols:
        col_min, col_max = df[col].min(), df[col].max() 
        stats[col] = {"min": col_min, "max": col_max} 
        span = (col_max - col_min) or 1  # avoid divide-by-zero on flat columns 
        df[col] = (df[col] - col_min) / span 
    return df, stats 

if __name__ == "__main__": 
    from data_collector import fetch_open_meteo_history 
    raw = fetch_open_meteo_history(19.07, 72.87, days=7) 
    df = load_and_merge(raw) 
    df = handle_missing(df) 
    df = add_time_features(df) 
    df = add_lag_features(df) 
    df.to_csv("data/processed/aqi_processed.csv") 
    print(f"Saved {len(df)} rows to data/processed/aqi_processed.csv") 
    print(df.tail())