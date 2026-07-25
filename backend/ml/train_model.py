"""
Trains the Disease Risk Prediction model used by the Health Future Engine.

Since no proprietary clinical dataset is bundled with this project, this
script generates a realistic *synthetic* dataset using well known risk-factor
relationships (age, BMI, blood pressure, glucose, cholesterol, smoking,
exercise, sleep, stress, family history) and trains a Random Forest
classifier on it.

Run this once before starting the Flask app:
    python ml/train_model.py

Swap `generate_synthetic_dataset()` for a loader over your real / licensed
clinical dataset when you have one -- the rest of the pipeline (feature
list, training, saving) does not need to change.
"""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

FEATURES = [
    "age",
    "bmi",
    "systolic_bp",
    "glucose",
    "cholesterol",
    "smoker",
    "exercise_hours_week",
    "sleep_hours",
    "stress_level",
    "family_history",
]

RISK_LABELS = ["Low", "Moderate", "High"]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_model.joblib")


def generate_synthetic_dataset(n_samples: int = 6000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.integers(18, 85, n_samples)
    bmi = np.clip(rng.normal(26, 5, n_samples), 15, 50)
    systolic_bp = np.clip(rng.normal(120, 15, n_samples) + (age - 40) * 0.3, 90, 200)
    glucose = np.clip(rng.normal(95, 20, n_samples) + (bmi - 25) * 0.8, 60, 300)
    cholesterol = np.clip(rng.normal(190, 30, n_samples) + (age - 40) * 0.4, 100, 350)
    smoker = rng.binomial(1, 0.2, n_samples)
    exercise_hours_week = np.clip(rng.normal(3, 2, n_samples), 0, 15)
    sleep_hours = np.clip(rng.normal(6.8, 1.2, n_samples), 3, 10)
    stress_level = rng.integers(1, 11, n_samples)  # 1-10 self reported
    family_history = rng.binomial(1, 0.3, n_samples)

    # Weighted risk score built from known-direction risk factors
    score = (
        (age > 50).astype(int) * 1.2
        + (bmi > 30).astype(int) * 1.4
        + (systolic_bp > 135).astype(int) * 1.6
        + (glucose > 125).astype(int) * 1.8
        + (cholesterol > 240).astype(int) * 1.3
        + smoker * 2.0
        + (exercise_hours_week < 1.5).astype(int) * 1.1
        + (sleep_hours < 6).astype(int) * 0.8
        + (stress_level > 7).astype(int) * 0.9
        + family_history * 1.5
        + rng.normal(0, 1.0, n_samples)  # noise
    )

    risk = pd.cut(
        score,
        bins=[-np.inf, 3.0, 6.0, np.inf],
        labels=RISK_LABELS,
    )

    df = pd.DataFrame(
        {
            "age": age,
            "bmi": bmi.round(1),
            "systolic_bp": systolic_bp.round(0),
            "glucose": glucose.round(0),
            "cholesterol": cholesterol.round(0),
            "smoker": smoker,
            "exercise_hours_week": exercise_hours_week.round(1),
            "sleep_hours": sleep_hours.round(1),
            "stress_level": stress_level,
            "family_history": family_history,
            "risk_label": risk.astype(str),
        }
    )
    return df


def train():
    df = generate_synthetic_dataset()
    X = df[FEATURES]
    y = df["risk_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))

    joblib.dump({"model": model, "features": FEATURES, "labels": RISK_LABELS}, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
