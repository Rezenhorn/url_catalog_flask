import logging
from logging.handlers import RotatingFileHandler

from flask import jsonify, request

from app import app
from config import MAX_LOGFILE_SIZE_IN_BYTES

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s',
    '%Y-%m-%d %H:%M:%S'
)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'app/log.txt', maxBytes=MAX_LOGFILE_SIZE_IN_BYTES, encoding="utf-8"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@app.before_request
def log_request_info():
    logger.info(f'{request.method} /{request.endpoint}')


@app.after_request
def log_response_info(response):
    logger.info(f'status: {response.status}, '
                f'{jsonify(response.data.decode("utf-8"))}')
    return response
