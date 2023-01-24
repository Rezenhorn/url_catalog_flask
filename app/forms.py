from flask_wtf import FlaskForm  # flask-wtf это обертка пакета wtforms
from flask_wtf.file import FileField, FileAllowed
from wtforms import (PasswordField,
                     BooleanField,
                     StringField,
                     SubmitField,
                     URLField)
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Optional,
                                ValidationError,
                                URL)

from .models import User


class LinkForm(FlaskForm):
    link = URLField(
        'Ccылка',
        validators=[Optional(), URL(message='Неверный URL')]
    )
    csv_file = FileField(
        'CSV файл с ссылками',
        validators=[
            Optional(), FileAllowed(['csv'], 'Разрешены только .csv файлы.')
        ]
    )
    submit = SubmitField('Отправить')


class SearchForm(FlaskForm):
    domain = StringField('Домен')
    domain_zone = StringField('Доменная зона')
    submit = SubmitField('Найти')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
