import logging
import os
import uuid
from collections import deque
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse

from flask import Flask, flash, jsonify, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from forms import LinkForm

MAX_LOGFILE_SIZE_IN_BYTES = 2 ** 20  # 1 Мегабайт
NUMBER_OF_LOG_LINES = 20
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s',
    '%Y-%m-%d %H:%M:%S'
)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'log.txt', maxBytes=MAX_LOGFILE_SIZE_IN_BYTES, encoding="utf-8"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

from models import *

Base.metadata.create_all(bind=engine)


@app.before_request
def log_request_info():
    app.logger.info(f'{request.method} /{request.endpoint}')


@app.after_request
def log_response_info(response):
    app.logger.info(f'status: {response.status}, '
                    f'{jsonify(response.data.decode("utf-8"))}')
    return response


def create_link_model(url: str):
    '''Парсит строку с url и возвращает модель Link с данными из url.'''
    if Link.query.filter_by(initial_url=url).first():
        raise ValueError(f'URL {url} уже есть в БД')
    url_parced = urlparse(url)
    if not all([url_parced.scheme, url_parced.netloc]):
        raise ValueError(f'"{url}" не соответствует формату url.')
    url_parts_dict = dict(url_parced._asdict())
    parameters = {}
    if url_parts_dict['query']:
        parameters_list = url_parts_dict['query'].split('&')
        for parameter in parameters_list:
            key, value = parameter.split('=')
            parameters[key] = value
    new_link = Link(
        uuid=str(uuid.uuid4()),
        initial_url=url,
        protocol=url_parts_dict['scheme'],
        domain=url_parts_dict['netloc'],
        domain_zone=url_parts_dict['netloc'].split('.')[-1],
        path=url_parts_dict['path'],
        parameters=parameters
    )
    return new_link


def add_single_url(url: str):
    '''Добавляет url в БД и логгирует результат.
    Возвращает созданный в БД объект.'''
    new_link = create_link_model(url)
    session.add(new_link)
    session.commit()
    app.logger.info(f'URL "{url}" добавлен в БД.')
    return new_link


def add_link_to_db_from_file(file) -> dict:
    '''Добавляет url из csv файла в БД, логгирует результат
    и возвращает словарь с числом обработанных url, успешных добавлений
    и ошибок.'''
    error_count = 0
    added_links = []
    url_list = file.read().decode('utf-8').split()
    links_to_process = len(url_list)
    for url in url_list:
        try:
            new_link = add_single_url(url)
        except ValueError:
            error_count += 1
            continue
        added_links.append(new_link.to_dict())
    return {
        'added_links': added_links,
        'links_to_process': links_to_process,
        'total_errors': error_count,
        'success_additions': len(added_links)
    }


@app.route('/api/link', methods=['POST'])
def add_link():
    data = request.get_json()
    if not data:
        raise KeyError('Отсутствует тело запроса.')
    url = data.get('url')
    if not url:
        raise KeyError('"url" является обязательным полем!')
    new_link = add_single_url(url)
    return jsonify(new_link.to_dict()), HTTPStatus.CREATED


@app.route('/api/load_csv', methods=['POST'])
def load_csv():
    file = request.files['file']
    result = add_link_to_db_from_file(file)
    return (jsonify([{'links_to_process': result['links_to_process'],
                      'errors': result['total_errors'],
                      'success_additions': result['success_additions']},
                    result['added_links']]),
            HTTPStatus.CREATED)


@app.route('/api/link', methods=['GET'])
def get_list():
    return (jsonify([link.to_dict() for link in Link.query.all()]),
            HTTPStatus.OK)


@app.route('/api/get_log', methods=['GET'])
def get_log():
    with open('log.txt', encoding='utf-8') as file:
        return jsonify(list(deque(file, NUMBER_OF_LOG_LINES))), HTTPStatus.OK


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = LinkForm()
    file = form.data.get('csv_file')
    if file:
        result = add_link_to_db_from_file(file)
        flash(f'{result["success_additions"]} URL из csv-файла добавлено в БД')
        return (render_template('add_link.html', form=form),
                HTTPStatus.CREATED)
    if form.validate_on_submit():
        url = form.link.data
        try:
            add_single_url(url)
            flash('URL добавлен в БД.')
            return (render_template('add_link.html', form=form),
                    HTTPStatus.CREATED)
        except ValueError as error:
            flash(f'Ошибка: {error}.')
    return render_template('add_link.html', form=form)


@app.route('/links_table', methods=['GET'])
def links_table_view():
    return render_template('links_table.html', links=Link.query.all())


@app.route('/logs', methods=['GET'])
def logs_view():
    with open('log.txt', encoding='utf-8') as file:
        logs = list(deque(file, NUMBER_OF_LOG_LINES))
        return render_template('logs.html', logs=logs)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
