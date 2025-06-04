from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    image_address = db.Column(db.Text, unique=True, nullable=False)
    name_product = db.Column(db.String(191), nullable=False)
    fee = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
