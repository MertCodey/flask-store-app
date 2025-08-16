from db import db

class TagModel(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    items = db.relationship('ItemModel', secondary='items_tags', back_populates='tags')
    store = db.relationship('StoreModel', back_populates='tags')
    