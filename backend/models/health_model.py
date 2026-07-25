from datetime import datetime, timezone

from bson import ObjectId

from extensions import (
    appointments_col,
    health_history_col,
    health_predictions_col,
    health_profiles_col,
    recommendations_col,
)


def serialize(doc: dict) -> dict:
    """Convert a Mongo document into a JSON-friendly dict."""
    if not doc:
        return {}
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    if "user_id" in out:
        out["user_id"] = str(out["user_id"])
    for key, value in out.items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
    return out


# ---- Health profile ----

def upsert_health_profile(user_id: str, data: dict) -> dict:
    data = dict(data)
    data["user_id"] = ObjectId(user_id)
    data["updated_at"] = datetime.now(timezone.utc)
    health_profiles_col.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": data, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return serialize(health_profiles_col.find_one({"user_id": ObjectId(user_id)}))


def get_health_profile(user_id: str):
    return health_profiles_col.find_one({"user_id": ObjectId(user_id)})


# ---- Predictions ----

def save_prediction(user_id: str, prediction: dict) -> dict:
    doc = dict(prediction)
    doc["user_id"] = ObjectId(user_id)
    doc["created_at"] = datetime.now(timezone.utc)
    result = health_predictions_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def list_predictions(user_id: str, limit: int = 20):
    cursor = (
        health_predictions_col.find({"user_id": ObjectId(user_id)})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [serialize(d) for d in cursor]


# ---- Recommendations ----

def save_recommendations(user_id: str, items: list) -> list:
    now = datetime.now(timezone.utc)
    docs = []
    for item in items:
        doc = dict(item)
        doc["user_id"] = ObjectId(user_id)
        doc["created_at"] = now
        doc["completed"] = False
        docs.append(doc)
    if docs:
        result = recommendations_col.insert_many(docs)
        for doc, _id in zip(docs, result.inserted_ids):
            doc["_id"] = _id
    return [serialize(d) for d in docs]


def list_recommendations(user_id: str):
    cursor = recommendations_col.find({"user_id": ObjectId(user_id)}).sort(
        "created_at", -1
    )
    return [serialize(d) for d in cursor]


def mark_recommendation_complete(user_id: str, rec_id: str, completed: bool = True):
    recommendations_col.update_one(
        {"_id": ObjectId(rec_id), "user_id": ObjectId(user_id)},
        {"$set": {"completed": completed}},
    )


# ---- Appointments ----

def create_appointment(user_id: str, data: dict) -> dict:
    doc = dict(data)
    doc["user_id"] = ObjectId(user_id)
    doc["created_at"] = datetime.now(timezone.utc)
    doc.setdefault("status", "scheduled")
    result = appointments_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def list_appointments(user_id: str):
    cursor = appointments_col.find({"user_id": ObjectId(user_id)}).sort(
        "date", 1
    )
    return [serialize(d) for d in cursor]


def delete_appointment(user_id: str, appointment_id: str):
    appointments_col.delete_one(
        {"_id": ObjectId(appointment_id), "user_id": ObjectId(user_id)}
    )


# ---- Health history (timeline) ----

def add_history_entry(user_id: str, data: dict) -> dict:
    doc = dict(data)
    doc["user_id"] = ObjectId(user_id)
    doc.setdefault("recorded_at", datetime.now(timezone.utc))
    result = health_history_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def list_history(user_id: str):
    cursor = health_history_col.find({"user_id": ObjectId(user_id)}).sort(
        "recorded_at", 1
    )
    return [serialize(d) for d in cursor]
