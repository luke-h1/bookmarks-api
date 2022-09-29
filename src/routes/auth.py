from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)
import validators
from src.db.database import User, db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from flasgger import swag_from

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
@swag_from("./docs/auth/register.yml")
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if len(password) < 6:
        return (
            jsonify({"error": "password must be more than 6 characters"}),
            HTTP_400_BAD_REQUEST,
        )

    if len(username) < 3:
        return (
            jsonify({"error": "username must be more than 6 characters"}),
            HTTP_400_BAD_REQUEST,
        )

    # would use custom serializers in bigger applications to parse this instead
    # of writing directly in the blueprint
    if not username.isalnum() or " " in username:
        return jsonify(
            {"error": "username should be alphanumeric & include no spaces"},
            HTTP_400_BAD_REQUEST,
        )

    if not validators.email(email):
        return jsonify({"error": "email must be a valid email"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Username or email already exists"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "Username or email already exists"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = User(username=username, password=pwd_hash, email=email)

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created", "user": user}), HTTP_201_CREATED
