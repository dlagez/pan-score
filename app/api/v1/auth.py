from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import v1_bp
from ...models.user import User
from ...services import auth_service

@v1_bp.post("/auth/register")
def register():
    data = request.get_json(force=True)
    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password or len(password) < 8:
        return {"error": "INVALID_INPUT"}, 400

    try:
        user = auth_service.register(email, password)
        return {"id": user.id, "email": user.email}, 201
    except ValueError as e:
        if str(e) == "EMAIL_EXISTS":
            return {"error": "EMAIL_EXISTS"}, 409
        return {"error": "UNKNOWN"}, 500

@v1_bp.post("/auth/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email", "")
    password = data.get("password", "")

    try:
        token = auth_service.login(email, password)
        return {"access_token": token}
    except ValueError:
        return {"error": "INVALID_CREDENTIALS"}, 401

@v1_bp.get("/auth/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return {"error": "UNAUTHORIZED"}, 401
    return {"id": user.id, "email": user.email}
