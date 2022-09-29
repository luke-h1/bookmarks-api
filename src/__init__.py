from flask import Flask, redirect, jsonify
from src.db.database import db
import os
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.routes.auth import auth
from src.routes.bookmarks import bookmarks
from src.config.swagger import template, swagger_config
from src.constants.http_status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            SWAGGER={"title": "Bookmarks API", "uiversion": 3},
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config=swagger_config, template=template)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def page_not_found(error):
        return jsonify({"error": f"{error}"}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def server_error(error):
        return jsonify({"error": f"{error}"}), HTTP_500_INTERNAL_SERVER_ERROR

    return app