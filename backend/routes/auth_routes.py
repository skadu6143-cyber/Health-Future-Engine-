from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from models.user_model import create_user, find_user_by_email, find_user_by_id, public_user
from utils.security import verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    if find_user_by_email(email):
        return jsonify({"error": "an account with this email already exists"}), 409

    user_id = create_user(name, email, password)
    token = create_access_token(identity=user_id)
    user = find_user_by_id(user_id)
    return jsonify({"token": token, "user": public_user(user)}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "invalid email or password"}), 401

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token, "user": public_user(user)}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"user": public_user(user)}), 200
