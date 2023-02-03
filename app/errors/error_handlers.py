from http import HTTPStatus

from flask import jsonify, render_template

from app.errors import bp
from app import db


class APIError(Exception):
    '''Ошибка при использовании API приложения.'''
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {"error": self.message}


@bp.app_errorhandler(APIError)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@bp.app_errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND


@bp.app_errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
