import os
from flask import Flask, jsonify

from config import config_by_name
from extensions import db, bcrypt, jwt, cors


def create_app(env_name=None):
    env_name = env_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(env_name, config_by_name["development"]))

    # --- Init extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # --- Ensure folders exist ---
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)

    # --- Register blueprints ---
    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.review import review_bp
    from routes.report import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(report_bp)

    # --- Import models so create_all() sees them ---
    from models import User, Project, Review, ReviewFinding  # noqa: F401

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "file too large"}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error"}), 500

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
