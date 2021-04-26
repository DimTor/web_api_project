import csv
from data import db_session
from data.gallery import Gallery


with open('dataset/van_gogh.csv', encoding='utf-8') as van_gogh:
    reader = csv.reader(van_gogh, delimiter=',', quotechar='"')
    db_session.global_init("db/masterpieces.sqlite")
    db_sess = db_session.create_session()
    for index, row in enumerate(reader):
        if index == 1 or index == 0:
            continue
        print(row[2], row[7], row[1])
        paint = Gallery(
            artist=row[7],
            link_on_paint=row[2],
            link_on_web=row[1]
        )
        db_sess.add(paint)
        db_sess.commit()