import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Artist(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'artists'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    in_favorite = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    artist = orm.relation("Gallery", back_populates='art')

