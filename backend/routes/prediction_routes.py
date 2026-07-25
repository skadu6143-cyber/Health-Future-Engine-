from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ml.predict import (
    explain_prediction,
    generate_recommendations,
    predict_risk,
    simulate_future,
)
from models.health_model import (
    get_health_profile,
    list_predictions,
    save_prediction,
    save_recommendations,
)

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api/predict")


def _profile_or_body(user_id: str) -> dict:
    """Use stored profile as a base, override with any fields in the request body."""
    stored = get_health_profile(user_id) or {}
    body = request.get_json(silent=True) or {}
    merged = {**stored, **body}
    return merged


@prediction_bp.post("/risk")
@jwt_required()
def risk():
    user_id = get_jwt_identity()
    profile = _profile_or_body(user_id)
    if not profile:
        return jsonify({"error": "no health profile on file — submit one first"}), 400

    result = predict_risk(profile)
    explanations = explain_prediction(profile)
    result["explanations"] = explanations

    saved = save_prediction(user_id, result)

    recs = generate_recommendations(profile, explanations)
    saved_recs = save_recommendations(user_id, recs)

    return jsonify({"prediction": saved, "recommendations": saved_recs}), 200


@prediction_bp.post("/simulate")
@jwt_required()
def simulate():
    user_id = get_jwt_identity()
    profile = _profile_or_body(user_id)
    if not profile:
        return jsonify({"error": "no health profile on file — submit one first"}), 400

    years = int(request.args.get("years", 10))
    years = max(1, min(years, 30))
    simulation = simulate_future(profile, years=years)
    return jsonify({"simulation": simulation}), 200


@prediction_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    preds = list_predictions(user_id)
    return jsonify({"predictions": preds}), 200
