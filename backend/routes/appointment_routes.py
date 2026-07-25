from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.health_model import create_appointment, delete_appointment, list_appointments

appointment_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


@appointment_bp.get("")
@jwt_required()
def get_appointments():
    user_id = get_jwt_identity()
    return jsonify({"appointments": list_appointments(user_id)}), 200


@appointment_bp.post("")
@jwt_required()
def add_appointment():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    required = ["title", "date"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "title and date are required"}), 400
    appt = create_appointment(
        user_id,
        {
            "title": data["title"],
            "date": data["date"],
            "doctor": data.get("doctor", ""),
            "notes": data.get("notes", ""),
            "type": data.get("type", "Checkup"),
        },
    )
    return jsonify({"appointment": appt}), 201


@appointment_bp.delete("/<appointment_id>")
@jwt_required()
def remove_appointment(appointment_id):
    user_id = get_jwt_identity()
    delete_appointment(user_id, appointment_id)
    return jsonify({"ok": True}), 200
