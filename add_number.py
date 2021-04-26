from data import db_session
from data.gallery import Gallery

db_session.global_init("db/masterpieces.sqlite")
db_sess = db_session.create_session()
gl = db_sess.query(Gallery).all()
for n, i in enumerate(gl):
    i.unique_number = 'pic' + str(n)
    db_sess.commit()

