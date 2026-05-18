from flask import Blueprint, request, jsonify
from .models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import secrets

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg":"username/password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"msg":"user exists"}), 400
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "bad credentials"}), 401

    # identity MUST be a string
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"username": user.username}
    )

    return jsonify({
        "access_token": access_token,
    }), 200
