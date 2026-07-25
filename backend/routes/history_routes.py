from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.health_model import add_history_entry, list_history

history_bp = Blueprint("health_history", __name__, url_prefix="/api/history")


@history_bp.get("")
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    return jsonify({"history": list_history(user_id)}), 200


@history_bp.post("")
@jwt_required()
def add_entry():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    if not data.get("event"):
        return jsonify({"error": "event is required"}), 400
    entry = add_history_entry(
        user_id,
        {
            "event": data["event"],
            "category": data.get("category", "General"),
            "notes": data.get("notes", ""),
            "recorded_at": data.get("recorded_at"),
        },
    )
    return jsonify({"entry": entry}), 201
