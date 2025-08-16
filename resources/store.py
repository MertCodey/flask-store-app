import uuid
from flask import request
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from models.stores import StoreModel
from schemas import StoreSchema
from db import db
from sqlalchemy.exc import IntegrityError
from models.items import ItemModel
from models.tags import TagModel  # add this
from flask_jwt_extended import jwt_required

# Initialize Flask-Smorest Blueprint
blp = Blueprint('stores', __name__, description='Operations on stores')

@blp.route("/store")
class Store(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        stores = StoreModel.query.all()
        return stores
    @jwt_required()  # Ensure that only authenticated users can create stores
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)        
    def post(self, store_data):
        """Create a new store"""
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while inserting the store: {str(e)}")
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An unexpected error occurred: {str(e)}")
        return store, 201
    
@blp.route("/store/<string:store_id>")
class StoreDetail(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        """Get a store by ID"""
        store = StoreModel.query.get_or_404(store_id)
        return store

    @blp.response(200, StoreSchema)
    def delete(self, store_id):
        """Delete a store by ID"""
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, 200