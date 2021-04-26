from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class PaintForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    artist = StringField('Художник', validators=[DataRequired()])
    link_on_info = StringField('Ссылка на wiki', validators=[DataRequired()])
    link_on_paint = StringField('Ссылка на изображение', validators=[DataRequired()])
    submit = SubmitField('Отправить')