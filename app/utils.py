import uuid
from urllib.parse import urlparse

from app import db

from flask import current_app
from app.models import Link


def create_link_model(url: str) -> Link:
    '''Парсит строку с url и возвращает модель Link с данными из url.'''
    if Link.query.filter_by(initial_url=url).first():
        raise ValueError(f'URL {url} уже есть в БД')
    url_parced = urlparse(url)
    if not all([url_parced.scheme, url_parced.netloc]):
        raise ValueError(f'"{url}" не соответствует формату URL')
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


def add_link_to_db(url: str) -> Link:
    '''Добавляет url в БД и логгирует результат.
    Возвращает созданный в БД объект.'''
    new_link = create_link_model(url)
    db.session.add(new_link)
    db.session.commit()
    current_app.logger.info(f'URL "{url}" добавлен в БД.')
    return new_link


def add_links_to_db_from_file(file) -> dict:
    '''Добавляет url из csv файла в БД, логгирует результат
    и возвращает словарь с числом обработанных url, успешных добавлений
    и ошибок.'''
    error_count = 0
    added_links = []
    url_list = file.read().decode('utf-8').split()
    links_to_process = len(url_list)
    for url in url_list:
        try:
            new_link = add_link_to_db(url)
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
