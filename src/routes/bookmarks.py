import json
from flask import Blueprint, jsonify, request, redirect
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


@bookmarks.route("/", methods=["POST", "GET"])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()

    if request.method == "POST":
        body = request.get_json().get("body", "")
        url = request.get_json().get("url", "")

        if not validators.url(url):
            return jsonify({"error": "Enter a valid URL"}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({"error": "URL already exists"}), HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": bookmark.id,
                    "url": bookmark.url,
                    "shortUrl": bookmark.short_url,
                    "visits": bookmark.visits,
                    "body": bookmark.body,
                    "createdAt": bookmark.created_at,
                    "updatedAt": bookmark.updated_at,
                }
            ),
            HTTP_201_CREATED,
        )
    else:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("perPage", 5, type=int)

        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(
            page=page, per_page=per_page
        )

        data = []

        for item in bookmarks.items:
            data.append(
                {
                    "id": item.id,
                    "url": item.url,
                    "shortUrl": item.short_url,
                    "visits": item.visits,
                    "body": item.body,
                    "createdAt": item.created_at,
                    "updatedAt": item.updated_at,
                }
            )

        meta = {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "totalCount": bookmarks.total,
            "prevPage": bookmarks.prev_num,
            "nextPage": bookmarks.next_num,
            "hasNext": bookmarks.has_next,
            "hasPrev": bookmarks.has_prev,
        }

        return jsonify({"data": data, "meta": meta}), HTTP_200_OK


@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id: int):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"msg": "Bookmark not found"}), HTTP_404_NOT_FOUND

    return (
        jsonify(
            {
                "id": bookmark.id,
                "url": bookmark.url,
                "shortUrl": bookmark.short_url,
                "visits": bookmark.visits,
                "body": bookmark.body,
                "createdAt": bookmark.created_at,
                "updatedAt": bookmark.updated_at,
            }
        ),
        HTTP_200_OK,
    )


@bookmarks.put("/<int:id>")
@jwt_required()
def update_bookmark(id: int):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        # doesn't exist or is owned by someone else
        return jsonify({"msg": "Bookmark not found"}), HTTP_404_NOT_FOUND

    body = request.get_json().get("body", "")
    url = request.get_json().get("url", "")

    if not validators.url(url):
        return jsonify({"error": "Enter a valid URL"}), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return (
        jsonify(
            {
                "id": bookmark.id,
                "url": bookmark.url,
                "shortUrl": bookmark.short_url,
                "visits": bookmark.visits,
                "body": bookmark.body,
                "createdAt": bookmark.created_at,
                "updatedAt": bookmark.updated_at,
            }
        ),
        HTTP_200_OK,
    )


@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id: int):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        # doesn't exist or is owned by someone else
        return jsonify({"message": "Bookmark not found"}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get("/stats")
@jwt_required()
@swag_from("./docs/bookmarks/stats.yml")
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            "vists": item.visits,
            "url": item.url,
            "id": item.id,
            "shortUrl": item.short_url,
        }
        data.append(new_link)

    return (
        jsonify(
            {
                "data": data,
            }
        ),
        HTTP_200_OK,
    )


@bookmarks.get("/<short_url>")
@swag_from("./docs/short_url.yml")
def redirect_to_url(short_url: str):
    bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

    if bookmark:
        bookmark.visits = bookmark.visits + 1
        db.session.commit()

        return redirect(bookmark.url)
