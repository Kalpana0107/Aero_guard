# 🌍 AeroGuard – AI-Powered Hyper-Local Air Quality Forecasting System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-XGBoost%20%7C%20LSTM%20%7C%20SARIMA-success)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Predict. Visualize. Protect.**

An AI-powered air quality forecasting platform that predicts upcoming AQI, explains the reasons behind pollution changes using Explainable AI (SHAP), visualizes pollution hotspots on an interactive map, and provides personalized health recommendations.

</div>

---

# 📖 Overview

AeroGuard is an intelligent environmental monitoring system designed to forecast Air Quality Index (AQI) using Machine Learning and Time Series models.

Instead of only displaying current pollution levels, AeroGuard predicts future AQI for the next six hours, helping users take preventive measures before air quality deteriorates.

The system combines multiple forecasting techniques with Explainable AI to make predictions transparent and trustworthy.

---

# ✨ Features

- 🌫️ Hyper-local AQI forecasting
- 📈 6-hour AQI prediction
- 🤖 Ensemble prediction using:
  - SARIMA
  - XGBoost
  - LSTM
- 🧠 Explainable AI using SHAP values
- 🗺️ Interactive pollution heatmap
- ❤️ Personalized health recommendations
- 👨‍👩‍👧 Multiple user personas:
  - General Public
  - Children & Elderly
  - Athletes
  - Outdoor Workers
- 📊 AQI trend visualization
- ⚡ Fast and lightweight Streamlit interface

---

# 🏗️ Tech Stack

## Programming Language

- Python

## Machine Learning

- XGBoost
- TensorFlow / Keras
- SARIMA (StatsModels)

## Data Processing

- Pandas
- NumPy
- Scikit-learn

## Explainable AI

- SHAP

## Visualization

- Streamlit
- Folium
- Matplotlib
- Altair

## APIs

- WAQI (World Air Quality Index)
- OWM (Open Weather Map)
---

# 📂 Project Structure

```
AeroGuard/
│
├── app.py
├── api_bridge.py
├── requirements.txt
├── .env.example
│
├── modules/
│   ├── data_collector.py
│   ├── preprocessor.py
│   ├── forecaster.py
│   ├── explainer.py
│   ├── health_risk.py
│   └── spatial.py
│
├── models/
│   ├── xgboost_model.json
│   ├── lstm_model.keras
│   └── *.pkl
│
├── data/
│   └── processed/
│
└── README.md
```

---

# ⚙️ Installation

## Clone the repository

```bash
git clone https://github.com/yourusername/AeroGuard.git

cd AeroGuard
```

## Create a virtual environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
WAQI_API_KEY=YOUR_API_KEY
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

The application will launch in your browser.

---

# 🧠 Machine Learning Pipeline

```
AQI Data
     │
     ▼
Data Collection
     │
     ▼
Preprocessing
     │
     ▼
Feature Engineering
     │
     ▼
 ┌───────────────┐
 │   SARIMA      │
 ├───────────────┤
 │   XGBoost     │
 ├───────────────┤
 │    LSTM       │
 └───────────────┘
      │
      ▼
 Ensemble Prediction
      │
      ▼
 SHAP Explanation
      │
      ▼
 Interactive Dashboard
```

---

# 📊 Forecasting Models

### SARIMA

Captures seasonal and temporal trends in AQI data.

### XGBoost

Learns complex nonlinear relationships between environmental variables.

### LSTM

Captures long-term sequential dependencies for improved forecasting.

### Ensemble

Combines predictions from all three models to improve overall accuracy and robustness.

---

# 🧠 Explainable AI

AeroGuard uses **SHAP (SHapley Additive Explanations)** to explain every prediction.

Users can understand:

- Which features increased AQI
- Which features reduced AQI
- Overall contribution of each environmental factor

This improves transparency and trust in the model.

---

# ❤️ Health Advisory

Based on the predicted AQI, AeroGuard provides personalized recommendations for:

- 👨 General Public
- 👶 Children
- 👵 Elderly
- 🏃 Athletes
- 👷 Outdoor Workers



---

# 📦 Main Dependencies

- Streamlit
- TensorFlow
- XGBoost
- SHAP
- Pandas
- NumPy
- Scikit-learn
- StatsModels
- Folium
- Matplotlib

---

# 🚀 Future Improvements

- Live satellite pollution integration
- Weather-aware AQI forecasting
- Mobile application
- Multi-city support
- Push notifications
- Pollution trend analytics
- Historical comparison dashboard
- IoT sensor integration

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👩‍💻 Author

**Kalpana Naikodi**

If you found this project useful, consider giving it a ⭐ on GitHub!         

