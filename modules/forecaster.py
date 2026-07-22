import pandas as pd
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
import xgboost as xgb
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------
# SARIMA
# ---------------------------------------------------------
def train_sarima(series: pd.Series, order=(2, 1, 2), seasonal_order=(1, 1, 1, 24)):
    model = SARIMAX(series, order=order, seasonal_order=seasonal_order,
                     enforce_stationarity=False, enforce_invertibility=False)
    return model.fit(disp=False)


def sarima_forecast(fitted_model, steps: int = 6) -> list:
    forecast = fitted_model.forecast(steps=steps)
    return [max(0, min(500, float(v))) for v in forecast]


# ---------------------------------------------------------
# XGBoost
# ---------------------------------------------------------
def prepare_xy(df: pd.DataFrame, target_col: str = "aqi"):
    feature_cols = [c for c in df.columns if c != target_col]
    return df[feature_cols], df[target_col], feature_cols


def train_xgboost(df: pd.DataFrame, target_col: str = "aqi"):
    X, y, feature_cols = prepare_xy(df, target_col)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05,
                              subsample=0.8, colsample_bytree=0.8, random_state=42)
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    model.save_model("models/xgboost_model.json")
    with open("models/xgb_feature_cols.pkl", "wb") as f:
        pickle.dump(feature_cols, f)

    return model, X_test, y_test, feature_cols


# ---------------------------------------------------------
# LSTM (Keras)
# ---------------------------------------------------------
def create_sequences(data: np.ndarray, seq_len: int = 24, horizon: int = 6):
    X, y = [], []
    for i in range(len(data) - seq_len - horizon):
        X.append(data[i:i + seq_len])
        y.append(data[i + seq_len:i + seq_len + horizon])
    return np.array(X), np.array(y)


def build_lstm(seq_len: int = 24, horizon: int = 6):
    model = Sequential([
        LSTM(64, input_shape=(seq_len, 1), return_sequences=True),
        LSTM(32, return_sequences=False),
        Dense(horizon)
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def train_lstm(df, target_col="aqi", seq_len=24, horizon=6, epochs=20):
    values = df[target_col].values.reshape(-1, 1).astype("float32")
    scale_max = values.max() or 1
    scaled = values / scale_max

    X, y = create_sequences(scaled.flatten(), seq_len, horizon)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    split = int(len(X) * 0.85)
    X_train = X[:split]
    y_train = y[:split]
    X_val = X[split:]
    y_val = y[split:]

    model = build_lstm(seq_len, horizon)
    
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, verbose=0)
    
    val_loss = model.evaluate(X_val, y_val, verbose=0)[0]
    print(f"LSTM trained — final validation MSE: {val_loss:.4f}")

    model.save("models/lstm_model.keras")
    with open("models/lstm_scale_max.pkl", "wb") as f:
        pickle.dump(scale_max, f)

    return model, scale_max


# ---------------------------------------------------------
# Model Evaluation
# ---------------------------------------------------------
def evaluate_model(y_true, y_pred, name: str) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((np.array(y_true) - np.array(y_pred)) /
                           np.where(np.array(y_true) == 0, 1, y_true))) * 100
    return {"model": name, "MAE": round(mae, 2), "RMSE": round(rmse, 2), "MAPE": round(mape, 2)}


# ---------------------------------------------------------
# Run all training + evaluation
# ---------------------------------------------------------
if __name__ == "__main__":
    df = pd.read_csv("data/processed/aqi_processed.csv", index_col=0, parse_dates=True)

    print("Training SARIMA...")
    sarima_model = train_sarima(df["aqi"])
    with open("models/sarima_model.pkl", "wb") as f:
        pickle.dump(sarima_model, f)

    print("\nTraining XGBoost...")
    xgb_model, X_test, y_test, feature_cols = train_xgboost(df)

    print("\nTraining LSTM...")
    lstm_model, scale_max = train_lstm(df)

    print("\nAll 3 models trained. Check models/ folder for saved files.")