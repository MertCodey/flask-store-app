from flask import Flask
import os
import secrets
from dotenv import load_dotenv
from db import db
from blocklist import BLOCKLIST
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_migrate import Migrate
import models  # ensure models are imported to register them with SQLAlchemy
from models.stores import StoreModel
from models.items import ItemModel
from models.tags import TagModel
from models.item_tags import item_tags  # ensure association table is registered
from flask_jwt_extended import JWTManager

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Store API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    db_url = db_url or os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    api = Api(app)
    Migrate(app, db)
    app.config["JWT_SECRET_KEY"] = 123  # Change this to a secure key in production

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"message": "The token has been revoked."}, 401

    @jwt.needs_fresh_token_loader
    def fresh_token_required_callback(jwt_header, jwt_payload):
        return {"message": "Fresh token required."}, 401

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app