from flask_wtf import FlaskForm  # flask-wtf это обертка пакета wtforms
from flask_wtf.file import FileField, FileAllowed
from wtforms import (PasswordField,
                     BooleanField,
                     StringField,
                     SubmitField,
                     URLField)
from wtforms.validators import (DataRequired,
                                Optional,
                                Email,
                                EqualTo,
                                ValidationError,
                                URL)

from .models import User


class LinkForm(FlaskForm):
    link = URLField(
        'Ccылка',
        validators=[Optional(), URL(message='Неверный URL')]
    )
    submit = SubmitField('Отправить')


class CSVForm(FlaskForm):
    csv_file = FileField(
        'CSV файл с ссылками',
        validators=[
            Optional(), FileAllowed(['csv'], 'Разрешены только .csv файлы')
        ]
    )
    submit = SubmitField('Отправить')


class SearchForm(FlaskForm):
    domain = StringField('Домен')
    domain_zone = StringField('Доменная зона')
    submit = SubmitField('Найти')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другое имя.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другой email.')
