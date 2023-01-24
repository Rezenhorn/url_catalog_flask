from collections import deque
from http import HTTPStatus

from flask import jsonify, request

from app import app
from config import NUMBER_OF_LOG_LINES

from .error_handlers import APIError
from .models import Link
from .utils import add_links_to_db_from_file, add_link_to_db


@app.route('/api/link', methods=['POST'])
def add_link():
    data = request.get_json()
    if not data:
        raise APIError('Отсутствует тело запроса.')
    url = data.get('url')
    if not url:
        raise APIError('В запросе отсутствует URL.')
    new_link = add_link_to_db(url)
    return jsonify(new_link.to_dict()), HTTPStatus.CREATED


@app.route('/api/load_csv', methods=['POST'])
def load_csv():
    file = request.files.get('file')
    if not file:
        raise APIError('В запросе отсутствует файл.')
    if file.filename.rsplit('.', 1)[1] != 'csv':
        raise APIError('Допустимы только .csv файлы.')
    result = add_links_to_db_from_file(file)
    return (jsonify([{'links_to_process': result['links_to_process'],
                      'errors': result['total_errors'],
                      'success_additions': result['success_additions']},
                    result['added_links']]),
            HTTPStatus.CREATED)


@app.route('/api/link', methods=['GET'])
def get_list():
    query = Link.query
    if request.args:
        for param in request.args.keys():
            if param not in ('uuid', 'id', 'domain_zone'):
                raise APIError('Недопустимый ключ поиска.')
        query = query.filter_by(**request.args)
    return jsonify([link.to_dict() for link in query.all()]), HTTPStatus.OK


@app.route('/api/get_log', methods=['GET'])
def get_log():
    with open('app/log.txt', encoding='utf-8') as file:
        return jsonify(list(deque(file, NUMBER_OF_LOG_LINES))), HTTPStatus.OK
