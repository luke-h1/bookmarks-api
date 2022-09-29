from flask import Flask, redirect, jsonify
from src.db.database import db
import os
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.routes.auth import auth 
from src.routes.bookmarks import bookmarks 
from src.config.swagger import template, swagger_config

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),

            SWAGGER = {
                'title': 'Bookmarks API',
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    
    db.app = app 
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config=swagger_config, template=template)
