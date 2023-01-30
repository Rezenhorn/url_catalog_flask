import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')


MAX_LOGFILE_SIZE_IN_BYTES = 2 ** 20  # 1 Мегабайт
NUMBER_OF_LOG_LINES = 20
LINKS_PER_PAGE = 10
AUTH_TOKEN_LIFETIME = 3600
