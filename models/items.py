from db import db

class ItemModel(db.Model):
    __tablename__ = 'items'
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), unique=False, nullable=False)
    store = db.relationship('StoreModel', back_populates='items')
    tags = db.relationship('TagModel', secondary='items_tags', back_populates='items')

