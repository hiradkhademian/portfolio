from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_object="app.config.Config"):
    # Serve frontend from /frontend folder
    app = Flask(__name__, static_folder="../../frontend", static_url_path="/static")
    app.config.from_object(config_object)

    # ----------------------------------------------------
    # JWT TOKEN CONFIG (30 days expiration)
    # ----------------------------------------------------
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ----------------------------------------------------
    # Register Blueprints
    # ----------------------------------------------------
    from .api.farms import bp as farms_bp
    from .api.zones import bp as zones_bp
    from .api.devices import bp as devices_bp
    from .api.telemetry import bp as telemetry_bp
    from .api.rules import bp as rules_bp
    from .auth import auth_bp
    from .api.alerts import bp as alerts_bp
    from .api.commands import bp as commands_bp
    from .api.reports import bp as reports_bp
    from .api.dashboard import bp as dashboard_bp
    from .api.alerts_full import bp as alerts_full_bp

    # New alert system (main)
    app.register_blueprint(alerts_full_bp, url_prefix="/api/alerts")

    # Legacy alerts (kept for compatibility)
    app.register_blueprint(alerts_bp, url_prefix="/api/alerts/legacy")

    # Other endpoints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(farms_bp, url_prefix="/api/farms")
    app.register_blueprint(zones_bp, url_prefix="/api/zones")
    app.register_blueprint(devices_bp, url_prefix="/api/devices")
    app.register_blueprint(telemetry_bp, url_prefix="/api/telemetry")
    app.register_blueprint(rules_bp, url_prefix="/api/rules")
    app.register_blueprint(commands_bp, url_prefix="/api/commands")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Default landing page (for frontend)
    @app.route("/")
    def index():
        return app.send_static_file("zone_detail.html")

    return app