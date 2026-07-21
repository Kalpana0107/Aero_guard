import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "")
OWM_KEY = os.getenv("OWM_KEY", "")

def fetch_waqi(city: str) -> dict:
    """Fetch the current AQI reading for a city from the WAQI API.
    Returns a dict with aqi, pm25, pm10, and station info.
    Raises an exception on failure — callers decide the fallback.
    """
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    resp = requests.get(url, timeout=8)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("status") != "ok":
        raise ValueError(f"WAQI returned non-ok status: {payload.get('status')}")
    data = payload["data"]
    iaqi = data.get("iaqi", {})
    return {
        "aqi": data.get("aqi"),
        "pm25": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "station": data.get("city", {}).get("name"),
        "timestamp": data.get("time", {}).get("s"),
    }

def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current weather (wind speed, humidity, temp) from OpenWeatherMap.
    Weather strongly influences AQI — wind disperses pollutants, still air
    lets them build up — so this feeds directly into our features.
    """
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OWM_KEY}&units=metric"
    )
    resp = requests.get(url, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    return {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "wind_deg": data["wind"].get("deg", 0),
        "pressure": data["main"]["pressure"],
    }

def fetch_open_meteo_history(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    """Fetch hourly historical air-quality data from Open-Meteo (free, no key required).
    This is our training data source — WAQI only gives the current reading,
    but we need history to train a forecasting model.
    """
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=pm10,pm2_5,us_aqi"
        f"&past_days={days}"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    df = pd.DataFrame({
        "timestamp": payload["hourly"]["time"],
        "pm10": payload["hourly"]["pm10"],
        "pm25": payload["hourly"]["pm2_5"],
        "aqi": payload["hourly"]["us_aqi"],
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

if __name__ == "__main__":
    # Quick manual test — run this file directly to sanity-check your keys.
    print("Testing fetch_waqi('mumbai')...")
    print(fetch_waqi("mumbai"))
    print("\nTesting fetch_weather(19.07, 72.87)...")
    print(fetch_weather(19.07, 72.87))
    print("\nTesting fetch_open_meteo_history(19.07, 72.87, days=3)...")
    print(fetch_open_meteo_history(19.07, 72.87, days=3).head())