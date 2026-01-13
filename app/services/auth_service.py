from flask_jwt_extended import create_access_token
from ..extensions import db
from ..models.user import User
from ..common.security import hash_password, verify_password

def register(email: str, password: str) -> User:
    email = email.strip().lower()
    if User.query.filter_by(email=email).first():
        raise ValueError("EMAIL_EXISTS")

    user = User(email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    return user

def login(email: str, password: str) -> str:
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.is_active:
        raise ValueError("INVALID_CREDENTIALS")

    if not verify_password(password, user.password_hash):
        raise ValueError("INVALID_CREDENTIALS")

    # 把 token_version 放进 JWT，后续可用于 logout_all/改密后全失效
    access_token = create_access_token(identity=str(user.id), additional_claims={"tv": user.token_version})
    return access_token
