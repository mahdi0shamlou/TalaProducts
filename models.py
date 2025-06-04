from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
import configparser
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


# SQLAlchemy Setup
Base = declarative_base()

class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_address = Column(Text, nullable=False)
    name_product = Column(String(191), nullable=False)
    fee = Column(Integer, nullable=False)
    profit = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

config = configparser.ConfigParser()
config.read('Config.ini')
# Database Config
DB_USER = config.get('mysql', 'user')
DB_PASSWORD = config.get('mysql', 'password')
DB_HOST = config.get('mysql', 'host')
DB_PORT = config.get('mysql', 'port', fallback='3306')
DB_NAME = config.get('mysql', 'database')
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)