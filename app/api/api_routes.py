from collections import deque
from http import HTTPStatus

from flask import g, jsonify, request

from app import db
from app.api import bp
from config import NUMBER_OF_LOG_LINES

from app.auth.auth import basic_auth, token_auth
from app.errors.error_handlers import APIError
from app.models import Link, User
from app.utils import add_links_to_db_from_file, add_link_to_db


@bp.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        raise APIError('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        raise APIError('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        raise APIError('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    return response, HTTPStatus.CREATED


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@bp.route('/link', methods=['POST'])
@token_auth.login_required
def add_link():
    data = request.get_json()
    if not data:
        raise APIError('Отсутствует тело запроса.')
    url = data.get('url')
    if not url:
        raise APIError('В запросе отсутствует URL.')
    new_link = add_link_to_db(url)
    return jsonify(new_link.to_dict()), HTTPStatus.CREATED


@bp.route('/load_csv', methods=['POST'])
@token_auth.login_required
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


@bp.route('/link', methods=['GET'])
@token_auth.login_required
def get_list():
    query = Link.query
    if request.args:
        for param in request.args.keys():
            if param not in ('uuid', 'id', 'domain_zone'):
                raise APIError('Недопустимый ключ поиска.')
        query = query.filter_by(**request.args)
    return jsonify([link.to_dict() for link in query.all()]), HTTPStatus.OK


@bp.route('/get_log', methods=['GET'])
@token_auth.login_required
def get_log():
    with open('app/application.log', encoding='utf-8') as file:
        return jsonify(list(deque(file, NUMBER_OF_LOG_LINES))), HTTPStatus.OK
