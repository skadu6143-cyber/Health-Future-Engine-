import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from config import Config
from extensions import init_indexes, jwt

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
    )
    app.config.from_object(Config)

    CORS(app)
    jwt.init_app(app)

    try:
        init_indexes()
    except Exception as exc:  # pragma: no cover
        app.logger.warning("Could not initialize MongoDB indexes: %s", exc)

    # Blueprints
    from routes.auth_routes import auth_bp
    from routes.profile_routes import profile_bp
    from routes.prediction_routes import prediction_bp
    from routes.recommendation_routes import recommendation_bp
    from routes.appointment_routes import appointment_bp
    from routes.history_routes import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(history_bp)

    # ---- JWT error handlers ----
    @jwt.unauthorized_loader
    def unauthorized(reason):
        return jsonify({"error": "authentication required", "detail": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "invalid token", "detail": reason}), 422

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify({"error": "token expired"}), 401

    # ---- Page routes (server-rendered templates) ----
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/register")
    def register_page():
        return render_template("register.html")

    @app.get("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.get("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.get("/timeline")
    def timeline_page():
        return render_template("timeline.html")

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "service": "Health Future Engine API"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)
