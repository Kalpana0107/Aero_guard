# 🌫️ AeroGuard — Hyper-Local Air Quality Forecaster

AeroGuard is a full-stack AI web app that forecasts hourly air quality (AQI) for your exact location, explains *why* pollution levels are changing using SHAP, and gives persona-specific health advice — all rendered on an interactive city heatmap.


---

## ✨ Features

- **6-hour AQI forecasting** using an ensemble of 3 models — SARIMA, XGBoost, and LSTM
- **Persona-aware health advice** — General Public, Children/Elderly, Outdoor Workers, Athletes
- **Explainable AI** — SHAP values translated into a plain-English "why is AQI high right now?" summary
- **Live city heatmap** — real monitoring stations interpolated (IDW) into a smooth pollution gradient via Folium
- **Graceful demo-mode fallback** — the app never crashes even if a live API or model is temporarily unavailable

---

## 🧱 Tech Stack

| Layer | Tools |
|---|---|
| Frontend | Streamlit, Matplotlib, Folium + streamlit-folium |
| Backend / ML | Python, XGBoost, statsmodels (SARIMA), PyTorch (LSTM), SHAP, scikit-learn |
| Data Sources | WAQI API (live AQI), OpenWeatherMap (weather), Open-Meteo (historical AQI) |
| Deployment | Streamlit Community Cloud |

---

## 📁 Project Structure

```
Aero_guard/
├── app.py                  # Streamlit frontend — entry point
├── api_bridge.py           # Shared contract — the ONLY file the frontend imports from the backend
├── modules/
│   ├── data_collector.py   # WAQI / OpenWeatherMap / Open-Meteo API calls
│   ├── preprocessor.py     # Cleaning, lag features, normalization
│   ├── forecaster.py       # SARIMA + XGBoost + LSTM training & inference
│   ├── health_risk.py      # EPA AQI breakpoints + persona-specific advice
│   ├── explainer.py        # SHAP values → natural-language explanations
│   └── spatial.py          # IDW interpolation + Folium heatmap generation
├── data/
│   ├── raw/                # Untouched API responses (gitignored)
│   └── processed/          # Cleaned, model-ready CSVs
├── models/                 # Saved trained models (.pkl / .json / .pt)
├── .env.example             # Template for required API keys
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Setup

### 1. Clone and enter the project
```bash
git clone https://github.com/YOUR_ORG/aeroguard.git
cd Aero_guard
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy the template and fill in your real API keys:
```bash
cp .env.example .env
```

```env
WAQI_TOKEN=your_waqi_token_here
OWM_KEY=your_openweathermap_key_here
DEFAULT_CITY=mumbai
DEFAULT_LAT=19.0760
DEFAULT_LON=72.8777
```

Get free API keys here:
- WAQI Token → https://aqicn.org/data-platform/token/
- OpenWeatherMap Key → https://openweathermap.org/api

### 5. Run the app
```bash
streamlit run app.py
```
Visit `http://localhost:8501` in your browser.

---

## 🧠 Training the Models

Before the forecast tab shows real predictions, train and save each model at least once:

```bash
python modules/data_collector.py      # sanity-check API keys
python modules/preprocessor.py        # build data/processed/aqi_processed.csv
python modules/forecaster.py          # train SARIMA + XGBoost + LSTM, save to models/
```

Model comparison metrics (MAE / RMSE / MAPE) are written to `models/results.txt`.

---

## 🔌 The API Contract

The frontend never imports backend logic directly — it only calls these 4 functions from `api_bridge.py`:

| Function | Returns |
|---|---|
| `get_forecast(city, lat, lon)` | `{current_aqi, pm25, forecast_6h[6], trend, city}` |
| `get_risk_timeline(forecast_6h, persona)` | `[{aqi, category, color, advice, hour_offset}] × 6` |
| `get_explanation(current_aqi, forecast_6h)` | `{explanation, trend}` |
| `get_map(lat, lon, token)` | `folium.Map` object |

This keeps frontend and backend development fully decoupled — either side can change their internals without breaking the other.

---

## 🚀 Deployment

Deployed on **Streamlit Community Cloud**:

1. Push to GitHub `main` branch
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo + `app.py`
3. Add `WAQI_TOKEN` and `OWM_KEY` under **Advanced Settings → Secrets**
4. Deploy

Live app: `<add your deployed URL here once live>`

---

## 👥 Team

| Role | Responsibilities |
|---|---|
| **Frontend** | Streamlit UI, charts, heatmap embed, styling, deployment |
| **Backend** | Data collection, model training, health-risk logic, SHAP explainability, spatial interpolation |

---

## 📌 Roadmap

- [ ] Ensemble all 3 models instead of picking one
- [ ] Real-time threshold-based alerts
- [ ] Multi-city comparison dashboard
- [ ] Historical forecast-accuracy tracking

---

## 📄 License

This project was built for educational and hackathon purposes.
