import string

from flask import Flask, render_template, redirect, make_response, jsonify, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session, artist_api
from data.users import User
from data.artist import Artist
from data.paint_form import PaintForm
import datetime
from random import shuffle, randint
from data.login_form import LoginForm
from data.register import RegisterForm
from data.gallery import Gallery
import json
import re
import os
from script.make_img import color_bar, favorite_colour


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# Основная страница с картинами
@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated and current_user.favorite:
        art = db_sess.query(Gallery).filter(Gallery.id.notin_(current_user.favorite.split(', ')), Gallery.public).all()
    else:
        art = db_sess.query(Gallery).all()
    shuffle(art)
    return render_template("index.html", title='Work log', art=art)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()

    return db_sess.query(User).get(user_id)


# Авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Страница пользователя
@app.route('/page/<name>')
@login_required
def my_wall(name):
    db_sess = db_session.create_session()
    # Получение массива из имени и фамилии пользователя
    if name[0] not in string.ascii_letters:
        name = re.findall('[А-Я][а-я]*', name)
    else:
        name = re.findall('[A-Z][a-z]*', name)
    user = db_sess.query(User).filter(User.surname == name[1].strip(), User.name == name[0].strip()).first()
    if not user.favorite:
        return render_template('wall.html', message='Здесь пока что пусто', name=user)
    favorite_list = user.favorite.split(', ')
    art = []
    for wish in favorite_list:
        paint = db_sess.query(Gallery).filter(Gallery.unique_number == wish).first()
        art.append(paint)
    shuffle(art)

    return render_template('wall.html', art=art, name=user)


# Добавление в избранное
@app.route('/add/<unique>', methods=['POST'])
@login_required
def add_to_favorite(unique):
    db_sess = db_session.create_session()
    art = db_sess.query(Gallery).filter(Gallery.unique_number == unique).first()
    user = db_sess.query(User).get(current_user.id)
    if current_user.favorite:
        paints = db_sess.query(Gallery).filter(Gallery.artist == art.artist,
                                               Gallery.unique_number.notin_(art.unique_number.split(', ')),
                                               Gallery.unique_number.notin_(current_user.favorite.split(', '))).all()
    else:
        paints = db_sess.query(Gallery).filter(Gallery.artist == art.artist,
                                               Gallery.unique_number.notin_(art.unique_number.split(', '))).all()
    if user.favorite:
        user.favorite = current_user.favorite + ', ' + str(art.unique_number)
    else:
        user.favorite = str(art.unique_number)
    artist = db_sess.query(Artist).filter(Artist.name == art.artist).first()
    artist.in_favorite += 1
    db_sess.commit()
    return render_template('add_to_wish.html', message='Добавлено', paint=art, art=paints)


# Если дабовление в избранное идет со страницы друго пользователя
@app.route('/add_from/<unique>', methods=['POST'])
@login_required
def add_from(unique):
    for n, i in enumerate(unique.lower()):
        if i in string.digits and unique[n + 1] in string.ascii_letters or unique[n + 1] \
                in 'ёйцукенгшщзхъфывапролджэячсмитьбю':
            number = unique[:n]
            name = unique[n:]
            break
    db_sess = db_session.create_session()
    # Получение массива из имени и фамилии
    if name[0] not in string.ascii_letters:
        name = re.findall('[А-Я][а-я]*', name)
    else:
        name = re.findall('[A-Z][a-z]*', name)
    user = db_sess.query(User).filter(User.surname == name[1], User.name == name[0]).first()
    current = db_sess.query(User).get(current_user.id)
    paint = db_sess.query(Gallery).filter(Gallery.unique_number == number).first()
    if current.favorite and paint.unique_number in current.favorite:
        pass
    elif current.favorite:
        current.favorite = current_user.favorite + ', ' + str(paint.unique_number)
    else:
        current.favorite = str(paint.unique_number)
    # Чтобы нельзя было жульничать, проверка на то, что картина впервые добавляется в избранное
    with open('dataset/pull_from_user.json', 'r') as js:
        pull_data = json.load(js)
        if str(user.id) in pull_data.keys():
            pull_paint = pull_data[str(user.id)]
            if str(current.id) in pull_paint.keys():
                if paint.unique_number in pull_paint[str(current.id)]:
                    pass
                else:
                    pull_paint[str(current.id)] = pull_paint[str(current.id)] + ', ' + paint.unique_number
                    user.pull = user.pull + 1 if user.pull else 1
            else:
                pull_paint[str(current.id)] = paint.unique_number
                user.pull = user.pull + 1 if user.pull else 1
        else:
            user.pull = user.pull + 1 if user.pull else 1
            pull_data[str(user.id)] = {str(current.id): paint.unique_number}
    # Записываем обнавленные данные в json файл
    with open('dataset/pull_from_user.json', 'w') as son:
        json.dump(pull_data, son)
    artist = db_sess.query(Artist).filter(Artist.name == paint.artist).first()
    artist.in_favorite += 1
    db_sess.commit()
    art = []
    favorite_list = user.favorite.split(', ')
    for wish in favorite_list:
        paint = db_sess.query(Gallery).filter(Gallery.unique_number == wish).first()
        art.append(paint)
    shuffle(art)
    return render_template('wall.html', art=art, name=user)


# Удаление из избранного
@app.route('/delete/<unique>', methods=['POST'])
def delete_from_favorite(unique):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    paint = db_sess.query(Gallery).filter(Gallery.unique_number == unique).first()
    fav = user.favorite
    new_faw = []
    for i in fav.split(', '):
        if i != str(paint.unique_number):
            new_faw.append(i)
    user.favorite = ', '.join(new_faw)
    artist = db_sess.query(Artist).filter(Artist.name == paint.artist).first()
    artist.in_favorite -= 1
    db_sess.commit()
    return redirect(f'/page/{current_user.name + current_user.surname}')


# Вывод списка всех пользователей
@app.route('/list')
@login_required
def users_list():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id != current_user.id).all()
    return render_template('list_users.html', users=users)


# Топ пользователей по количеству добавления в избранное другими пользователями
@app.route('/top')
@login_required
def users_top():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    list_users = []
    for user in users:
        if user.pull:
            list_users.append([user.surname + ' ' + user.name, user.pull])
        else:
            list_users.append([user.surname + ' ' + user.name, 0])
    return render_template('top.html', users=sorted(list_users, key=lambda x: x[1], reverse=True), us=users)


# Топ самых популярных художников по количеству добавления в избранное
@app.route('/top_of_artist')
@login_required
def artist_top():
    db_sess = db_session.create_session()
    artists = db_sess.query(Artist).all()
    list_artists = []
    for artist in artists:
        if artist:
            link = f'/show_artist/{artist.id}'
            list_artists.append([artist.name, artist.in_favorite, link])
    return render_template('top_artists.html', artists=sorted(list_artists, key=lambda x: x[1], reverse=True))


# Разложения картин на самые популярные цвета
@app.route('/analytics/<name>')
@login_required
def analytics(name):
    if 'favorite' + name + '.png' in os.listdir('static/img'):
        os.remove(f'static/img/{"favorite" + name + ".png"}')
    db_sess = db_session.create_session()
    if name[0] not in string.ascii_letters:
        name = re.findall('[А-Я][а-я]*', name)
    else:
        name = re.findall('[A-Z][a-z]*', name)
    user = db_sess.query(User).filter(User.surname == name[1], User.name == name[0]).first()
    if not user.favorite:
        return render_template('analysis.html', message='Здесь пока что пусто', name=user)
    favorite_list = user.favorite.split(', ')
    art = []
    for wish in favorite_list:
        paint = db_sess.query(Gallery).filter(Gallery.unique_number == wish).first()
        if paint.unique_number + '.png' not in os.listdir('static/img'):
            # создаем цветной батончик
            color_bar(paint.link_on_paint, paint.unique_number)
        art.append([paint, url_for('static', filename=f'img/{paint.unique_number + ".png"}')])
    return render_template('analysis.html', art=art, name=user)


# Анализ самого популярного цвета
@app.route('/favorite_color/<name>')
@login_required
def favorite_color(name):
    db_sess = db_session.create_session()
    if name[0] not in string.ascii_letters:
        name = re.findall('[А-Я][а-я]*', name)
    else:
        name = re.findall('[A-Z][a-z]*', name)
    user = db_sess.query(User).filter(User.surname == name[1], User.name == name[0]).first()
    favorite_list = user.favorite.split(', ')
    favorite_colour(favorite_list, user.name + user.surname)
    return render_template('favorite_color.html',
                           name=user, paint=url_for('static', filename=f'img/{"favorite" + name[0] + name[1] + ".png"}'))


# Добавление или смена аватарки
@app.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def avatar():
    if request.method == 'GET':
        if current_user.avatar:
            path = url_for('static', filename=f'avatars/{current_user.avatar}')
        else:
            path = None
        return render_template('avatar.html', file=path, success=False)
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        user.avatar = f'{current_user.name + current_user.surname + ".png"}'
        db_sess.commit()
        f = request.files['file']
        z = open(f'static/avatars/{current_user.name + current_user.surname + ".png"}', 'wb')
        z.write(f.read())
        z.close()
        return render_template('avatar.html', success=True,
                               file=url_for('static', filename=f'avatars/{current_user.avatar}'))


# Предложения новой картины, которой нет в базе данных
@app.route('/paints',  methods=['GET', 'POST'])
@login_required
def add_paint():
    form = PaintForm()
    if form.validate_on_submit():
        d = datetime.datetime.now().timetuple()
        unique = str(d.tm_year) + str(d.tm_mon) + str(d.tm_mday) + str(d.tm_hour) + str(d.tm_min) + str(d.tm_sec)
        db_sess = db_session.create_session()
        paints = db_sess.query(Gallery).filter(Gallery.name == form.title.data, Gallery.artist == form.artist.data).all()
        if not paints:
            paint = Gallery()
            paint.name = form.title.data
            paint.artist = form.artist.data
            paint.link_on_web = form.link_on_info.data
            paint.link_on_paint = form.link_on_paint.data
            paint.unique_number = 'pic' + unique
            paint.public = False
            db_sess.add(paint)
            db_sess.commit()
            return redirect('/')
        else:
            return render_template('add_paint.html', title='Добавление картины',
                                   form=form, messag='Такая картина уже существует')
    return render_template('add_paint.html', title='Добавление картины',
                           form=form)


# Поиск по сайту. Можно искать как картины, так и художников
@app.route('/search', methods=['GET', 'POST'])
def search():
    db_sess = db_session.create_session()
    if request.method == 'GET':
        paints = db_sess.query(Gallery).all()
        artists = db_sess.query(Artist).all()
        return render_template('search.html', paints=paints, artists=artists)
    elif request.method == 'POST':
        paints = db_sess.query(Gallery).all()
        paints_name = []
        for paint in paints:
            if paint.name:
                paints_name.append(paint.name)
        if request.form['search'] in paints_name:
            paint = db_sess.query(Gallery).filter(Gallery.name == request.form['search']).first()
            return redirect(f'/show_art/{paint.unique_number}')
        artists_name = []
        artists = db_sess.query(Artist).all()
        for artist in artists:
            artists_name.append(artist.name)
        if request.form['search'] in artists_name:
            artist = db_sess.query(Artist).filter(Artist.name == request.form['search']).first()
            return redirect(f'/show_artist/{artist.id}')
        return render_template('search.html', message='Ничего не найдено')


# Показа определенной картины по id
@app.route('/show_art/<unique>')
def show_art(unique):
    db_sess = db_session.create_session()
    paint = db_sess.query(Gallery).filter(Gallery.unique_number == unique).first()
    return render_template('show_art.html', paint=paint)


# Показ определенного художника по id
@app.route('/show_artist/<int:artist_id>')
def show_artist(artist_id):
    db_sess = db_session.create_session()
    artist = db_sess.query(Artist).filter(Artist.id == artist_id).first()
    paints = db_sess.query(Gallery).filter(Gallery.artist == artist.name).all()
    return render_template('show_artist.html', paints=paints, artist=artist)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/masterpieces.sqlite")
    app.register_blueprint(artist_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()