import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from extensions import db, socketio
from routes import api
from dotenv import load_dotenv
from flask import send_from_directory

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Mac/Windows compatible pathing for SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'emergency.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-key-123' # for later
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-later'

    # Extensions
    db.init_app(app)
    socketio.init_app(app)
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def _jwt_unauthorized(_callback):
        return jsonify({
            "success": False,
            "message": "Missing or invalid token"
        }), 401

    @jwt.invalid_token_loader
    def _jwt_invalid(_callback):
        return jsonify({
            "success": False,
            "message": "Missing or invalid token"
        }), 401

    @jwt.expired_token_loader
    def _jwt_expired(_jwt_header, _jwt_payload):
        return jsonify({
            "success": False,
            "message": "Missing or invalid token"
        }), 401

    @app.route('/')
    def tracker():
        return send_from_directory('.', 'tracker.html')

    @app.route('/admin')
    def admin():
        return send_from_directory('.', 'admin.html')

    # Registering the routes
    app.register_blueprint(api, url_prefix='/api')

    # Create the database file automatically
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, port=5000)
