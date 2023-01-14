from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, URLField
from wtforms.validators import URL


class LinkForm(FlaskForm):
    link = URLField('Ccылка', validators=[URL(message='Неверный URL')])
    csv_file = FileField('CSV файл с ссылками')
    submit = SubmitField('Отправить')
