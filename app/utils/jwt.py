from flask_jwt_extended import JWTManager
from app import jwt
from app.models import User


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data.get("sub")
    token_version = jwt_data.get("token_version")
    user = User.query.get(identity)
    return user if user and user.token_version == token_version else None
