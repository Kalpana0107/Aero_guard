import pandas as pd
import pickle
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import mean_absolute_error, mean_squared_error

from statsmodels.tsa.statespace.sarimax import SARIMAX
import xgboost as xgb
from sklearn.model_selection import train_test_split


def train_sarima(
    series: pd.Series,
    order=(2, 1, 2),
    seasonal_order=(1, 1, 1, 24),
):
    """
    Train a SARIMA model.

    order = (p, d, q):
        Non-seasonal AR, differencing, and MA terms.

    seasonal_order:
        The seasonal period of 24 represents one full day of
        hourly AQI data, allowing the model to learn daily
        pollution patterns such as rush hours.
    """

    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    fitted = model.fit(disp=False)
    return fitted


def sarima_forecast(fitted_model, steps: int = 6) -> list:
    """
    Forecast future AQI values using the trained SARIMA model.
    """

    forecast = fitted_model.forecast(steps=steps)

    # Clip AQI values to the valid range (0–500)
    return [max(0, min(500, float(v))) for v in forecast]


# ---------------------------------------------------------
# XGBoost
# ---------------------------------------------------------

def prepare_xy(df: pd.DataFrame, target_col: str = "aqi"):
    """
    Split the processed dataframe into
    features (X) and target (y).
    """

    feature_cols = [c for c in df.columns if c != target_col]

    X = df[feature_cols]
    y = df[target_col]

    return X, y, feature_cols


def train_xgboost(df: pd.DataFrame, target_col: str = "aqi"):
    """
    Train an XGBoost regressor for AQI prediction.
    """

    X, y, feature_cols = prepare_xy(df, target_col)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=False,  # Preserve time-series order
    )

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Save trained model
    model.save_model("models/xgboost_model.json")

    # Save feature names
    with open("models/xgb_feature_cols.pkl", "wb") as f:
        pickle.dump(feature_cols, f)

    return model, X_test, y_test, feature_cols


if __name__ == "__main__":
    df = pd.read_csv(
        "data/processed/aqi_processed.csv",
        index_col=0,
        parse_dates=True,
    )

    print("Training SARIMA...")
    sarima_model = train_sarima(df["aqi"])

    with open("models/sarima_model.pkl", "wb") as f:
        pickle.dump(sarima_model, f)

    print("SARIMA 6h forecast:")
    print(sarima_forecast(sarima_model))

    print("\nTraining XGBoost...")

    xgb_model, X_test, y_test, feature_cols = train_xgboost(df)

    print("XGBoost trained on", len(feature_cols), "features")

# modules/forecaster.py — Part 3: LSTM

def create_sequences(
    data: np.ndarray,
    seq_len: int = 24,
    horizon: int = 6,
):
    """
    Turns a flat array into (X, y) sequence pairs.

    X = previous `seq_len` hours
    y = next `horizon` hours

    LSTMs expect input in the shape:
    (samples, timesteps, features)
    """

    X = []
    y = []

    for i in range(len(data) - seq_len - horizon):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len : i + seq_len + horizon])

    return np.array(X), np.array(y)


def build_lstm(seq_len: int = 24, horizon: int = 6):
    """
    Build and compile the LSTM model.
    """

    model = keras.Sequential(
        [
            layers.Input(shape=(seq_len, 1)),
            layers.LSTM(64, return_sequences=True),
            layers.LSTM(32),
            layers.Dense(horizon),  # Predict all forecast hours at once
        ]
    )

    model.compile(
        optimizer="adam",
        loss="mse",
        metrics=["mae"],
    )

    return model


def train_lstm(
    df,
    target_col="aqi",
    seq_len=24,
    horizon=6,
    epochs=20,
):
    """
    Train the LSTM model on AQI time-series data.
    """

    values = df[target_col].values.reshape(-1, 1).astype("float32")

    scale_max = values.max() or 1

    # Scale values to the range 0–1
    scaled = values / scale_max

    X, y = create_sequences(
        scaled.flatten(),
        seq_len,
        horizon,
    )

    X = X.reshape((X.shape[0], X.shape[1], 1))

    split = int(len(X) * 0.85)

    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    model = build_lstm(seq_len, horizon)

    model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=32,
        verbose=0,
    )

    model.save("models/lstm_model.keras")

    return model, scale_max


# ---------------------------------------------------------
# Model Evaluation
# ---------------------------------------------------------

def evaluate_model(y_true, y_pred, name: str) -> dict:
    """
    Calculate common regression metrics.
    """

    mae = mean_absolute_error(y_true, y_pred)

    rmse = np.sqrt(
        mean_squared_error(y_true, y_pred)
    )

    # Guard against division by zero when AQI = 0
    mape = (
        np.mean(
            np.abs(
                (np.array(y_true) - np.array(y_pred))
                / np.where(np.array(y_true) == 0, 1, y_true)
            )
        )
        * 100
    )

    return {
        "model": name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
    }


if __name__ == "__main__":
    import pandas as pd
    import pickle

    df = pd.read_csv(
        "data/processed/aqi_processed.csv",
        index_col=0,
        parse_dates=True,
    )

    print("Training LSTM...")

    lstm_model, scale_max = train_lstm(df)

    # Evaluate all three models on the same held-out test set.
    results = []

    # ---------------------------------------------------------
    # Example:
    # results.append(evaluate_model(...))
    # ---------------------------------------------------------

    with open("models/results.txt", "w") as f:
        for r in results:
            f.write(
                f"{r['model']}: "
                f"MAE={r['MAE']}  "
                f"RMSE={r['RMSE']}  "
                f"MAPE={r['MAPE']}%\n"
            )

    print("Saved comparison to models/results.txt")