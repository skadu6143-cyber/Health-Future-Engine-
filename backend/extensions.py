from flask_jwt_extended import JWTManager
from pymongo import MongoClient

from config import Config

jwt = JWTManager()

_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
db = _client[Config.MONGO_DB_NAME]

# Collections
users_col = db["users"]
health_profiles_col = db["health_profiles"]
health_predictions_col = db["health_predictions"]
recommendations_col = db["recommendations"]
appointments_col = db["appointments"]
health_history_col = db["health_history"]


def init_indexes():
    """Create useful indexes. Call once at startup."""
    users_col.create_index("email", unique=True)
    health_profiles_col.create_index("user_id")
    health_predictions_col.create_index("user_id")
    recommendations_col.create_index("user_id")
    appointments_col.create_index("user_id")
    health_history_col.create_index("user_id")
