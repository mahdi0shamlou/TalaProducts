# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_address = Column(Text, unique=True, nullable=False)
    name_product = Column(String(191), nullable=False)
    fee = Column(Integer, nullable=False)
    profit = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)