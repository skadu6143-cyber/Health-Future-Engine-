from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.health_model import get_health_profile, serialize, upsert_health_profile

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")

PROFILE_FIELDS = [
    "age",
    "gender",
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


@profile_bp.get("")
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = get_health_profile(user_id)
    return jsonify({"profile": serialize(profile)}), 200


@profile_bp.put("")
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    clean = {k: data[k] for k in PROFILE_FIELDS if k in data}
    if not clean:
        return jsonify({"error": "no valid profile fields supplied"}), 400
    profile = upsert_health_profile(user_id, clean)
    return jsonify({"profile": profile}), 200
