import json
from flask import Blueprint, jsonify, request
import validators
from src.db.database import Bookmark, db
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

