"""
Crop Recommender Service: Machine Learning inference engine.
Supports both 4-Parameter (sensorless climate & pH) and 7-Parameter (with NPK nutrients) models.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Load trained models & encoders
model_4p_path = os.path.join(MODEL_DIR, 'crop_model_4p.pkl')
model_7p_path = os.path.join(MODEL_DIR, 'crop_model_7p.pkl')
encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
metrics_path = os.path.join(MODEL_DIR, 'model_metrics.json')
crop_info_path = os.path.join(DATA_DIR, 'crop_info.json')

model_4p = joblib.load(model_4p_path) if os.path.exists(model_4p_path) else None
model_7p = joblib.load(model_7p_path) if os.path.exists(model_7p_path) else None
label_encoder = joblib.load(encoder_path) if os.path.exists(encoder_path) else None

with open(metrics_path, 'r') as f:
    METRICS = json.load(f)

with open(crop_info_path, 'r') as f:
    CROP_INFO = json.load(f)

def get_model_metadata():
    return METRICS

def get_crop_details(crop_label: str):
    key = crop_label.lower().strip()
    return CROP_INFO.get(key, {
        "name": crop_label.capitalize(),
        "category": "Agricultural Crop",
        "season": "Seasonal Kharif/Rabi",
        "water_requirement": "Moderate",
        "soil_type": "Well-drained agricultural soil",
        "optimal_temp": "20°C - 30°C",
        "optimal_humidity": "60% - 80%",
        "optimal_ph": "6.0 - 7.5",
        "optimal_rainfall": "60 - 150 mm",
        "tips": "Follow standard regional agricultural package of practices."
    })

def calculate_suitability(crop_name: str, temp: float, humidity: float, ph: float, rainfall: float):
    """
    Evaluates how closely the input parameters align with the statistical optimum for the crop.
    Returns a score out of 100 and per-parameter status (Optimal, High, Low).
    """
    stats = METRICS.get("crop_optimal_ranges", {}).get(crop_name, {})
    if not stats:
        return {"overall_score": 92, "parameter_status": {}}

    scores = []
    status = {}

    for param, val in [("temperature", temp), ("humidity", humidity), ("ph", ph), ("rainfall", rainfall)]:
        p_stat = stats.get(param, {})
        p_min = p_stat.get("min", val * 0.7)
        p_max = p_stat.get("max", val * 1.3)
        p_mean = p_stat.get("mean", val)

        if p_min <= val <= p_max:
            score = 100 - (abs(val - p_mean) / (p_max - p_min + 1e-5)) * 25
            scores.append(max(75, min(100, score)))
            status[param] = {"state": "Optimal", "badge": "success", "user_val": val, "optimal_range": f"{p_min} - {p_max}"}
        elif val < p_min:
            diff_ratio = (p_min - val) / (p_min + 1e-5)
            score = max(40, 75 - diff_ratio * 40)
            scores.append(score)
            status[param] = {"state": "Low", "badge": "warning", "user_val": val, "optimal_range": f"{p_min} - {p_max}"}
        else:
            diff_ratio = (val - p_max) / (p_max + 1e-5)
            score = max(40, 75 - diff_ratio * 40)
            scores.append(score)
            status[param] = {"state": "High", "badge": "warning", "user_val": val, "optimal_range": f"{p_min} - {p_max}"}

    avg_score = round(sum(scores) / len(scores), 1) if scores else 90.0
    return {"overall_score": avg_score, "parameter_status": status}

def recommend(temperature: float, humidity: float, ph: float, rainfall: float,
              n: float = None, p: float = None, k: float = None):
    """
    Perform crop recommendation.
    If N, P, K are provided, uses 7-parameter model (99.55% accuracy).
    Otherwise uses 4-parameter model (96.14% accuracy).
    """
    use_7p = (n is not None and p is not None and k is not None)

    if use_7p and model_7p:
        cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        features = pd.DataFrame([[float(n), float(p), float(k), float(temperature), float(humidity), float(ph), float(rainfall)]], columns=cols)
        clf = model_7p
        model_name = "7-Parameter Nutrient & Climate Model"
        accuracy = METRICS.get("accuracy_7param", 99.55)
    else:
        cols = ['temperature', 'humidity', 'ph', 'rainfall']
        features = pd.DataFrame([[float(temperature), float(humidity), float(ph), float(rainfall)]], columns=cols)
        clf = model_4p
        model_name = "4-Parameter Sensorless Meteorological & Soil Model"
        accuracy = METRICS.get("accuracy_4param", 96.14)

    # Probabilities for all crops
    probabilities = clf.predict_proba(features)[0]
    class_indices = np.argsort(probabilities)[::-1]

    # Get Top-3 recommendations
    top_recommendations = []
    for rank, idx in enumerate(class_indices[:3]):
        crop_label = label_encoder.inverse_transform([idx])[0]
        prob = round(float(probabilities[idx]) * 100, 2)
        crop_details = get_crop_details(crop_label)
        suitability = calculate_suitability(crop_label, temperature, humidity, ph, rainfall)

        top_recommendations.append({
            "rank": rank + 1,
            "crop": crop_label,
            "display_name": crop_details.get("name", crop_label.capitalize()),
            "confidence": prob,
            "suitability_score": suitability["overall_score"],
            "details": crop_details,
            "parameter_checks": suitability["parameter_status"]
        })

    primary = top_recommendations[0]

    return {
        "success": True,
        "model_used": model_name,
        "model_accuracy": accuracy,
        "primary_crop": primary["crop"],
        "primary_display_name": primary["display_name"],
        "confidence": primary["confidence"],
        "top_recommendations": top_recommendations,
        "inputs": {
            "temperature": temperature,
            "humidity": humidity,
            "ph": ph,
            "rainfall": rainfall,
            "n": n,
            "p": p,
            "k": k,
            "mode": "7-Parameter (NPK + Climate)" if use_7p else "4-Parameter (Pure Sensorless)"
        }
    }
