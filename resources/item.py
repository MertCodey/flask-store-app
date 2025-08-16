import uuid
from flask import request
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from schemas import ItemSchema, ItemUpdateSchema
from models.items import ItemModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models.stores import StoreModel
from models.tags import TagModel  # add this
from flask_jwt_extended import jwt_required

# Initialize Flask-Smorest Blueprint
blp = Blueprint("items",__name__,description="Operations on items")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get an item by ID"""
        item = ItemModel.query.get_or_404(item_id)
        return item
    @jwt_required()  # Ensure that only authenticated users can delete items
    @blp.response(200, ItemSchema)
    def delete(self, item_id):
        """Delete an item by ID"""
        item = ItemModel.query.get_or_404(item_id)
        raise NotImplementedError("Delete operation is not implemented yet")
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item= ItemModel.query.get_or_404(item_id)
        raise NotImplementedError("Update operation is not implemented yet")
        
@blp.route("/items")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items"""
        items = ItemModel.query.all()
        return items, 200
    @jwt_required(fresh=True)  # Ensure that only authenticated users can create items
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create a new item"""
        item=ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while inserting the item: {str(e)}")
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f"An error occurred while inserting the item: {str(e)}")

        return item, 201
    
