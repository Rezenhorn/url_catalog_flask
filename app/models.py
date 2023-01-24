from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


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

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))
