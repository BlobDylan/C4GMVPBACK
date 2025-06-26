from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User
from app import db
from app.constants import ROLE_OPTIONS

bp = Blueprint("auth", __name__)


@bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    required_fields = ["firstName", "lastName", "email", "password", "role"]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    role = data.get("role")
    if role and role not in ROLE_OPTIONS:
        return jsonify({"message": "Invalid role"}), 400
    
    user = User(
        first_name=data["firstName"],
        last_name=data["lastName"],
        email=data["email"],
        phone_number=data.get("phoneNumber"),
        preferredLanguages=(
            str(data["preferredLanguages"]) if "preferredLanguages" in data else ""
        ),
<<<<<<< HEAD
=======
        role=role,
>>>>>>> 2567e62635875ebdfa52a956ba371e02e2089f8c
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not user.check_password(data.get("password")):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"token_version": user.token_version},
    )

    return (
        jsonify(
            {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "permissions": user.permission_type,
                    "role": user.role,
                },
            }
        ),
        200,
    )


@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    user = User.query.get(get_jwt_identity())
    user.token_version += 1
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200
