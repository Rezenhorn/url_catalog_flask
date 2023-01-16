from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, URLField
from wtforms.validators import URL


class LinkForm(FlaskForm):
    link = URLField('Ccылка', validators=[URL(message='Неверный URL')])
    csv_file = FileField('CSV файл с ссылками')
    submit = SubmitField('Отправить')


class SearchForm(FlaskForm):
    domain = StringField('Домен')
    domain_zone = StringField('Доменная зона')
    submit = SubmitField('Найти')
