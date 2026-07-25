from datetime import datetime, timezone

from bson import ObjectId

from extensions import users_col
from utils.security import hash_password


def create_user(name: str, email: str, password: str) -> str:
    """Insert a new user document with a hashed password. Returns the user id."""
    doc = {
        "name": name,
        "email": email.lower().strip(),
        "password_hash": hash_password(password),
        "created_at": datetime.now(timezone.utc),
    }
    result = users_col.insert_one(doc)
    return str(result.inserted_id)


def find_user_by_email(email: str):
    return users_col.find_one({"email": email.lower().strip()})


def find_user_by_id(user_id: str):
    try:
        return users_col.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def public_user(user_doc: dict) -> dict:
    """Strip sensitive fields before returning a user to the client."""
    if not user_doc:
        return {}
    return {
        "id": str(user_doc["_id"]),
        "name": user_doc.get("name"),
        "email": user_doc.get("email"),
        "created_at": user_doc.get("created_at").isoformat()
        if user_doc.get("created_at")
        else None,
    }
