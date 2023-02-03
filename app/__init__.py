import logging
from logging.handlers import RotatingFileHandler

from flask import jsonify, request

from config import MAX_LOGFILE_SIZE_IN_BYTES

from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Войдите для доступа к странице.'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    handler = RotatingFileHandler('app/application.log',
                                  maxBytes=MAX_LOGFILE_SIZE_IN_BYTES,
                                  encoding="utf-8")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def log_request_info():
        app.logger.info(f'{request.method} /{request.endpoint}')

    @app.after_request
    def log_response_info(response):
        app.logger.info(f'status: {response.status}, '
                        f'{jsonify(response.data.decode("utf-8"))}')
        return response

    return app


from app import models, utils
