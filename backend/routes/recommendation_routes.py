from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.health_model import list_recommendations, mark_recommendation_complete

recommendation_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


@recommendation_bp.get("")
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    return jsonify({"recommendations": list_recommendations(user_id)}), 200


@recommendation_bp.patch("/<rec_id>")
@jwt_required()
def update_recommendation(rec_id):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    completed = bool(data.get("completed", True))
    mark_recommendation_complete(user_id, rec_id, completed)
    return jsonify({"ok": True}), 200
