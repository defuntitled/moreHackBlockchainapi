import enum
import sqlalchemy
from db_session import SqlalchemyBase


class TypeEnum(enum.Enum):
    FILE = 1
    FOLDER = 2


class Product(SqlalchemyBase):
    __tablename__ = "products"
    item_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    seller_id = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Float)
    token_id = sqlalchemy.Column(sqlalchemy.Float)
