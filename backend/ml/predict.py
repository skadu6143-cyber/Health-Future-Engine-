"""
Inference layer for the Health Future Engine.

Wraps the trained Random Forest model and adds:
  - Disease Risk Prediction  (predict_risk)
  - Explainable AI            (explain_prediction)
  - Future Health Simulation  (simulate_future)
  - Preventive Recommendations(generate_recommendations)
"""
import os

import joblib
import numpy as np
import pandas as pd

from ml.train_model import FEATURES, RISK_LABELS, MODEL_PATH, train

_bundle = None


def _load_bundle():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            # Auto-train on first run so the app works out of the box.
            train()
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def _vectorize(profile: dict) -> pd.DataFrame:
    row = {f: float(profile.get(f, 0) or 0) for f in FEATURES}
    return pd.DataFrame([row], columns=FEATURES)


def predict_risk(profile: dict) -> dict:
    """Returns predicted risk label + class probabilities."""
    bundle = _load_bundle()
    model = bundle["model"]
    x = _vectorize(profile)

    label = model.predict(x)[0]
    proba = model.predict_proba(x)[0]
    proba_map = {cls: round(float(p) * 100, 1) for cls, p in zip(model.classes_, proba)}
    # Ensure all labels present even if 0
    for lbl in RISK_LABELS:
        proba_map.setdefault(lbl, 0.0)

    return {
        "risk_label": label,
        "probabilities": proba_map,
        "confidence": max(proba_map.values()),
    }


def explain_prediction(profile: dict) -> list:
    """
    Explainable AI: combines global Random Forest feature importances with the
    user's own values to produce a ranked, human-readable list of the factors
    driving their prediction (a lightweight, dependency-free stand-in for
    SHAP-style explanations).
    """
    bundle = _load_bundle()
    model = bundle["model"]
    importances = model.feature_importances_

    thresholds = {
        "age": (50, "Age over 50 increases baseline risk."),
        "bmi": (30, "BMI above 30 (obesity range) raises cardiometabolic risk."),
        "systolic_bp": (135, "Systolic blood pressure above 135 mmHg indicates hypertension risk."),
        "glucose": (125, "Fasting glucose above 125 mg/dL suggests diabetes risk."),
        "cholesterol": (240, "Total cholesterol above 240 mg/dL is considered high."),
        "smoker": (0.5, "Smoking significantly increases risk of chronic disease."),
        "exercise_hours_week": (1.5, "Less than 1.5 hours/week of exercise is a risk factor.", "low"),
        "sleep_hours": (6, "Under 6 hours of sleep nightly impairs recovery and metabolism.", "low"),
        "stress_level": (7, "Self-reported stress above 7/10 is linked to elevated cortisol and blood pressure."),
        "family_history": (0.5, "A family history of chronic disease raises genetic predisposition."),
    }

    explanations = []
    for feat, importance in zip(FEATURES, importances):
        value = float(profile.get(feat, 0) or 0)
        rule = thresholds.get(feat)
        if not rule:
            continue
        threshold, message = rule[0], rule[1]
        direction_low = len(rule) > 2 and rule[2] == "low"
        triggered = value < threshold if direction_low else value >= threshold
        if triggered:
            explanations.append(
                {
                    "factor": feat,
                    "impact_weight": round(float(importance) * 100, 1),
                    "value": value,
                    "message": message,
                }
            )

    explanations.sort(key=lambda e: e["impact_weight"], reverse=True)
    return explanations[:6]


def simulate_future(profile: dict, years: int = 10) -> dict:
    """
    Future Health Simulation: projects key vitals and overall risk score
    forward year-by-year given the person's current trajectory and lifestyle
    multipliers. This is a transparent, rule-based simulation (not the
    classifier) so its trend line can be explained to the user.
    """
    age = float(profile.get("age", 30) or 30)
    bmi = float(profile.get("bmi", 24) or 24)
    systolic_bp = float(profile.get("systolic_bp", 118) or 118)
    glucose = float(profile.get("glucose", 90) or 90)
    cholesterol = float(profile.get("cholesterol", 180) or 180)

    smoker = float(profile.get("smoker", 0) or 0)
    exercise = float(profile.get("exercise_hours_week", 2) or 2)
    sleep = float(profile.get("sleep_hours", 7) or 7)
    stress = float(profile.get("stress_level", 5) or 5)

    # Lifestyle multiplier: healthier habits slow the yearly drift, poor
    # habits accelerate it. Centered so a "neutral" lifestyle ~= 1.0
    lifestyle_multiplier = (
        1.0
        + (smoker * 0.6)
        + (max(0, 2 - exercise) * 0.08)
        + (max(0, 6.5 - sleep) * 0.05)
        + (max(0, stress - 5) * 0.04)
        - (min(exercise, 5) * 0.03)
    )
    lifestyle_multiplier = max(0.4, lifestyle_multiplier)

    timeline = []
    bundle = _load_bundle()
    model = bundle["model"]

    for year in range(0, years + 1):
        projected = {
            "year": year,
            "age": round(age + year, 1),
            "bmi": round(bmi + year * 0.15 * lifestyle_multiplier, 1),
            "systolic_bp": round(systolic_bp + year * 0.5 * lifestyle_multiplier, 1),
            "glucose": round(glucose + year * 0.6 * lifestyle_multiplier, 1),
            "cholesterol": round(cholesterol + year * 0.4 * lifestyle_multiplier, 1),
        }
        feature_row = {
            **projected,
            "smoker": smoker,
            "exercise_hours_week": exercise,
            "sleep_hours": sleep,
            "stress_level": stress,
            "family_history": float(profile.get("family_history", 0) or 0),
        }
        x = _vectorize(feature_row)
        proba = model.predict_proba(x)[0]
        proba_map = dict(zip(model.classes_, proba))
        high_risk_pct = round(float(proba_map.get("High", 0)) * 100, 1)
        projected["high_risk_probability"] = high_risk_pct
        timeline.append(projected)

    return {
        "years_simulated": years,
        "lifestyle_multiplier": round(lifestyle_multiplier, 2),
        "timeline": timeline,
    }


def generate_recommendations(profile: dict, explanations: list) -> list:
    """Preventive Recommendations: turns triggered risk factors into
    concrete, prioritized actions for the AI Health Coach to present."""
    catalog = {
        "bmi": {
            "title": "Move toward a healthier weight range",
            "detail": "Aim for 150 min/week of moderate cardio plus two strength sessions; small, sustained changes outperform crash diets.",
            "category": "Nutrition & Activity",
        },
        "systolic_bp": {
            "title": "Bring blood pressure back into range",
            "detail": "Reduce sodium intake, monitor BP weekly, and discuss medication options with your doctor if readings stay above 135/85.",
            "category": "Cardiovascular",
        },
        "glucose": {
            "title": "Stabilize blood sugar",
            "detail": "Cut refined sugar, favor high-fiber meals, and schedule an HbA1c test to rule out prediabetes.",
            "category": "Metabolic",
        },
        "cholesterol": {
            "title": "Lower LDL cholesterol",
            "detail": "Increase soluble fiber and unsaturated fats, reduce saturated fat, and recheck your lipid panel in 3 months.",
            "category": "Cardiovascular",
        },
        "smoker": {
            "title": "Start a quit-smoking plan",
            "detail": "Even a 1-year quit meaningfully lowers cardiovascular and cancer risk; ask about nicotine-replacement or cessation programs.",
            "category": "Lifestyle",
        },
        "exercise_hours_week": {
            "title": "Add movement to your week",
            "detail": "Start with 20-minute walks 4x/week and build up gradually — consistency matters more than intensity.",
            "category": "Activity",
        },
        "sleep_hours": {
            "title": "Protect your sleep window",
            "detail": "Target 7-8 hours nightly with a consistent wind-down routine; poor sleep worsens nearly every other risk factor.",
            "category": "Recovery",
        },
        "stress_level": {
            "title": "Build a stress-management habit",
            "detail": "Try daily breathing exercises, short walks, or journaling; chronic stress elevates blood pressure and cortisol.",
            "category": "Mental Wellbeing",
        },
        "family_history": {
            "title": "Increase screening frequency",
            "detail": "With a family history present, talk to your doctor about earlier or more frequent screenings for related conditions.",
            "category": "Preventive Screening",
        },
    }

    recs = []
    seen = set()
    for exp in explanations:
        item = catalog.get(exp["factor"])
        if item and exp["factor"] not in seen:
            recs.append({**item, "priority": "High" if exp["impact_weight"] > 10 else "Medium"})
            seen.add(exp["factor"])

    if not recs:
        recs.append(
            {
                "title": "Keep up the good work",
                "detail": "Your current profile shows no major risk flags — maintain your habits and recheck in 6-12 months.",
                "category": "Maintenance",
                "priority": "Low",
            }
        )
    return recs
