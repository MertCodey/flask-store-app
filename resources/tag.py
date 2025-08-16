from db import db
from models.tags import TagModel
from models.items import ItemModel
from models.stores import StoreModel
from schemas import TagSchema, PlainTagSchema
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

blp = Blueprint('tags', __name__, description='Operations on tags')

@blp.route('/store/<int:store_id>/tag')
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(PlainTagSchema)  # only needs {"name": "..."}
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(name=tag_data["name"], store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
            return tag
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Tag name already exists in this DB.")

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        # link
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag in item.tags:
            abort(409, message="Tag already linked to item.")
        item.tags.append(tag)
        db.session.commit()
        return tag

    @blp.response(204)
    def delete(self, item_id, tag_id):
        # unlink
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag in item.tags:
            item.tags.remove(tag)
            db.session.commit()
        return {}