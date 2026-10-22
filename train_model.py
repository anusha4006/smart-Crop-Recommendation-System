"""
Crop Recommendation Model Training Pipeline
Trains both:
1. 4-Parameter Model (Temperature, Humidity, pH, Rainfall) - Sensorless Meteorological & Soil Baseline
2. 7-Parameter Model (N, P, K, Temperature, Humidity, pH, Rainfall) - Nutrient Enhanced Model
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def train():
    os.makedirs('model', exist_ok=True)
    csv_path = 'Crop_recommendation.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    print("--> Loading dataset...")
    df = pd.read_csv(csv_path)
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Crops present ({df['label'].nunique()}): {list(df['label'].unique())}")

    # Compute crop-level statistical profiles (min, mean, max for each parameter)
    crop_stats = {}
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    for crop in df['label'].unique():
        sub = df[df['label'] == crop]
        crop_stats[crop] = {
            feat: {
                "min": round(float(sub[feat].min()), 2),
                "mean": round(float(sub[feat].mean()), 2),
                "max": round(float(sub[feat].max()), 2)
            } for feat in features
        }

    # Encode labels
    le = LabelEncoder()
    df['encoded_label'] = le.fit_transform(df['label'])
    label_mapping = {int(idx): str(name) for idx, name in enumerate(le.classes_)}

    # -------------------------------------------------------------
    # 1. Train 4-Feature Model (Temp, Humidity, pH, Rainfall)
    # -------------------------------------------------------------
    print("\n--> Training 4-Parameter Model (Sensorless Features: Temp, Humidity, pH, Rainfall)...")
    X4 = df[['temperature', 'humidity', 'ph', 'rainfall']]
    y = df['encoded_label']

    X4_train, X4_test, y4_train, y4_test = train_test_split(
        X4, y, test_size=0.2, random_state=42, stratify=y
    )

    rf4 = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=1)
    rf4.fit(X4_train, y4_train)

    y4_pred = rf4.predict(X4_test)
    acc4 = accuracy_score(y4_test, y4_pred)
    print(f"--> 4-Parameter Model Test Accuracy: {acc4 * 100:.2f}%")

    # Feature importances for 4-feature model
    fi4 = {feat: round(float(imp), 4) for feat, imp in zip(['temperature', 'humidity', 'ph', 'rainfall'], rf4.feature_importances_)}

    # -------------------------------------------------------------
    # 2. Train 7-Feature Model (N, P, K, Temp, Humidity, pH, Rainfall)
    # -------------------------------------------------------------
    print("\n--> Training 7-Parameter Model (Nutrients + Climate Features)...")
    X7 = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]

    X7_train, X7_test, y7_train, y7_test = train_test_split(
        X7, y, test_size=0.2, random_state=42, stratify=y
    )

    rf7 = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=1)
    rf7.fit(X7_train, y7_train)

    y7_pred = rf7.predict(X7_test)
    acc7 = accuracy_score(y7_test, y7_pred)
    print(f"--> 7-Parameter Model Test Accuracy: {acc7 * 100:.2f}%")

    fi7 = {feat: round(float(imp), 4) for feat, imp in zip(features, rf7.feature_importances_)}

    # -------------------------------------------------------------
    # Save Model Artifacts
    # -------------------------------------------------------------
    joblib.dump(rf4, 'model/crop_model_4p.pkl')
    joblib.dump(rf7, 'model/crop_model_7p.pkl')
    joblib.dump(le, 'model/label_encoder.pkl')

    metadata = {
        "model_type": "RandomForestClassifier",
        "n_samples": len(df),
        "crops_count": len(label_mapping),
        "crops": sorted(list(label_mapping.values())),
        "accuracy_4param": round(acc4 * 100, 2),
        "accuracy_7param": round(acc7 * 100, 2),
        "feature_importances_4param": fi4,
        "feature_importances_7param": fi7,
        "crop_optimal_ranges": crop_stats
    }

    with open('model/model_metrics.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n[SUCCESS] Both models trained and saved to 'model/' directory.")
    print(f"4-Parameter Accuracy: {acc4 * 100:.2f}%")
    print(f"7-Parameter Accuracy: {acc7 * 100:.2f}%")

if __name__ == '__main__':
    train()
