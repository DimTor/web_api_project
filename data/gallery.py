import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Gallery(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'gallery'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    artist = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('artists.name'), nullable=True)
    link_on_paint = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link_on_web = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    unique_number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    public = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    art = orm.relation('Artist')
