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
