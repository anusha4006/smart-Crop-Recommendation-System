# 🌾 Sensorless Smart Crop Recommendation System

> **A Machine Learning-driven Precision Agriculture Platform that predicts optimal crops based on Temperature, Humidity, Soil pH, and Rainfall — with 0 Physical Hardware Sensors.**

---

## 📌 Project Overview & Motivation

In traditional smart agriculture projects, farmers or researchers rely on physical IoT sensor probes (such as DHT22 for temperature/humidity, tipping buckets for rainfall, and glass-electrode pH meters). However, in real-world agrarian settings, **physical sensors present severe drawbacks**:
1. **High Expense & Calibration Drift**: Soil pH probes degrade rapidly (3–6 months) due to chemical reactions with soil minerals and require constant laboratory recalibration.
2. **Limited Sampling Radius**: A physical soil probe measures only a few cubic centimeters of soil, failing to represent an entire farm plot.
3. **Power & Hardware Overhead**: Microcontrollers (Arduino/ESP32), solar units, and cellular GSM modules are vulnerable to weather, theft, and rural connectivity blackouts.

### The Sensorless Solution:
This project demonstrates how **Meteorological Open Data APIs (Open-Meteo)** and **Agro-Climatic Soil Taxonomy** can completely replace physical hardware sensors while maintaining high predictive accuracy (**96.14% with 4 core parameters, 99.55% when soil nutrients are supplemented**).

---

## 🎯 Target Parameters & Sensorless Replacements

| Parameter | Traditional IoT Sensor | Sensorless Alternative (This Project) | Source / Reliability |
| :--- | :--- | :--- | :--- |
| **Temperature (°C)** | DHT11 / DHT22 / DS18B20 | **Open-Meteo Real-time Forecast API** (2m Air Temp) | Satellite reanalysis (ECMWF, NOAA, DWD) updated hourly |
| **Humidity (%)** | DHT22 / Capacitive Sensor | **Open-Meteo Atmospheric Telemetry** | Global hydrological satellite models |
| **Soil pH** | Glass-Electrode Soil Probe | **Regional Agro-Soil Taxonomy & City Presets** | ICAR & ISRIC Soil Classification Database |
| **Rainfall (mm)** | Tipping Bucket Rain Gauge | **Precipitation Telemetry & Seasonal Aggregation** | Satellite microwave & Doppler radar precipitation sums |

---

## 🧠 Machine Learning Engine

- **Dataset**: Standard Agricultural Crop Recommendation Dataset (2,200 verified records, 22 crops).
- **Algorithm**: **Random Forest Classifier** (`n_estimators=100`, `max_depth=15`).
- **Performance**:
  - **4-Parameter Model (Pure Sensorless: Temp, Humidity, pH, Rainfall)**: **96.14% Accuracy**
  - **7-Parameter Model (With N, P, K Soil Nutrients)**: **99.55% Accuracy**
- **Supported Crops (22)**:
  - *Cereals*: Rice, Maize
  - *Pulses / Legumes*: Chickpea, Kidney Beans, Pigeonpeas, Mothbeans, Mungbean, Blackgram, Lentil
  - *Fruits*: Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut
  - *Cash / Fiber / Plantation*: Cotton, Jute, Coffee

---

## 🏗️ System Architecture

```
User Browser (Farmer / Agri-officer)
        │
        ├── 1. Enter City / District (or adjust sliders)
        │
        ▼
   Flask Web App (app.py)
        │
        ├──► Open-Meteo Weather API ──► Retrieves Temp, Humidity, Seasonal Rainfall
        │
        ├──► Regional Soil Database ──► Retrieves Soil Type & Baseline pH
        │
        ├──► Random Forest Classifier ──► Evaluates multi-class probabilities
        │
        ▼
Interactive Recommendation Result:
  • Best Crop with Confidence Percentage
  • Top-3 Ranked Alternatives
  • Parameter Compatibility Check (Optimal / High / Low)
  • Sowing Season, Water Requirement & Cultivation Advice
```

---

## 📁 Project Directory Structure

```
MINI PROJECT1/
│
├── app.py                      # Flask Application & REST API endpoints
├── train_model.py              # ML Training Pipeline (generates models & metadata)
├── requirements.txt            # Python dependencies
├── Crop_recommendation.csv     # Agricultural dataset (2200 samples)
│
├── model/
│   ├── crop_model_4p.pkl       # 4-Parameter Model (Temp, Humidity, pH, Rainfall)
│   ├── crop_model_7p.pkl       # 7-Parameter Model (with N, P, K)
│   ├── label_encoder.pkl       # Scikit-learn Label Encoder
│   └── model_metrics.json      # Accuracies, feature importances & crop stats
│
├── data/
│   ├── crop_info.json          # Agricultural guides, sowing seasons, water needs
│   └── soil_profiles.json      # Soil classifications & regional district presets
│
├── services/
│   ├── weather_service.py      # Geocoding & Open-Meteo weather integration
│   ├── soil_service.py         # Soil pH & classification service
│   └── recommender.py          # ML inference engine & agronomic validation
│
├── static/
│   ├── css/style.css           # Modern agricultural responsive stylesheet
│   └── js/app.js               # Dynamic sliders, async fetch & UI rendering
│
└── templates/
    ├── base.html               # Navigation, Bootstrap 5 & shared layout
    ├── index.html              # Main Interactive Recommendation Dashboard
    ├── dataset.html            # Model Analytics, Feature Importances & Crop Catalog
    └── guide.html              # Technical Documentation & Viva Voce Q&A
```

---

## 🚀 How to Run the Project

### 1. Prerequisites
Ensure Python (3.9 - 3.13) is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Re-train the Machine Learning Models
```bash
python train_model.py
```
*Output will display model training progress and accuracy scores (96.14% and 99.55%).*

### 4. Start the Application
```bash
python app.py
```

### 5. Access the Web Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 💡 Key Features of the Dashboard

1. **One-Click Sensorless Auto-Fetch**: Type any city or district name (e.g., `Bangalore`, `Pune`, `Jaipur`, `Lucknow`, `Hyderabad`) or click quick chips. The system instantly queries the Open-Meteo API and regional soil tables.
2. **Interactive Range Sliders**: Adjust Temperature (°C), Relative Humidity (%), Soil pH, and Rainfall (mm) with real-time numeric badges and acidic/neutral/alkaline indicators.
3. **Top Recommendation with Confidence Score**: Displays the highest-matching crop along with its category, sowing season, and water requirements.
4. **Parameter Compatibility Matrix**: Verifies whether the input values fall within the optimal agronomic range for the predicted crop.
5. **Alternative Suitable Crops**: Ranks the top-3 candidate crops with comparative confidence progress bars.
6. **Built-in Model Insights Page (`/dataset`)**: Visualizes feature importances and catalogs all 22 supported crops.
7. **Technical Architecture Guide (`/sensorless-guide`)**: Outlines the sensor replacement strategy and provides ready answers for project viva evaluations.

---

## 🎓 Academic Viva / Defense Highlights

- **Q: How does the system handle rural areas with no internet?**  
  *A: The system includes a built-in offline fallback database (`FALLBACK_CLIMATE` and `regional_presets`) covering major agricultural agro-climatic zones, and allows manual parameter entry from Soil Health Cards.*
- **Q: Why is Rainfall the most important feature?**  
  *A: Agricultural crops have distinct water footprints (e.g., Rice requires >180mm of standing water, whereas Mothbeans and Chickpeas thrive in <60mm of dry conditions). Random Forest feature importance identifies Rainfall as contributing ~38% to classification decisions.*
