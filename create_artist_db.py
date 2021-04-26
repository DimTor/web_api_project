from data.artist import Artist
from data.gallery import Gallery
from data import db_session

db_session.global_init("db/masterpieces.sqlite")
db_sess = db_session.create_session()
art = db_sess.query(Gallery).all()
artists = []
for i in art:
    if i.artist not in artists:
        artists.append(i.artist)
for a in artists:
    artist = Artist(
        name=a,
        in_favorite=0
    )
    db_sess.add(artist)
db_sess.commit()
