import base64
from datetime import datetime, timedelta
import os

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from config import AUTH_TOKEN_LIFETIME


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    initial_url = db.Column(db.String(200), nullable=False, unique=True)
    uuid = db.Column(db.String(36), nullable=False, unique=True)
    protocol = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(200), nullable=False)
    domain_zone = db.Column(db.String(200), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    parameters = db.Column(db.JSON(), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'protocol': self.protocol,
            'domain': self.domain,
            'domain_zone': self.domain_zone,
            'path': self.path,
            'parameters': self.parameters
        }


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

    def get_token(self, expires_in=AUTH_TOKEN_LIFETIME):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
