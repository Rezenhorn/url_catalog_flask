from collections import deque
from http import HTTPStatus

from flask import flash, redirect, render_template, url_for

from app import app, db
from config import LINKS_PER_PAGE, NUMBER_OF_LOG_LINES

from .forms import LinkForm, SearchForm
from .models import Link
from .utils import add_links_to_db_from_file, add_link_to_db


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = LinkForm()
    file = form.data.get('csv_file')
    if file:
        result = add_links_to_db_from_file(file)
        flash(f'Обработано {result["links_to_process"]} URL из csv-файла. '
              f'{result["success_additions"]} URL успешно добавлено в БД.')
        return (render_template('add_link.html', form=form),
                HTTPStatus.CREATED)
    if form.validate_on_submit():
        url = form.link.data
        form.link.data = ''
        try:
            add_link_to_db(url)
            flash('URL добавлен в БД.')
            return (render_template('add_link.html', form=form),
                    HTTPStatus.CREATED)
        except ValueError as error:
            flash(f'Ошибка: {error}.', 'error')
    return render_template('add_link.html', form=form), HTTPStatus.OK


@app.route('/links_table', methods=['GET', 'POST'])
@app.route('/links_table/<int:page>', methods=['GET', 'POST'])
def links_table_view(page=1):
    form = SearchForm()
    domain, domain_zone = form.domain.data, form.domain_zone.data
    if form.validate_on_submit() and (domain or domain_zone):
        result = Link.query
        if domain:
            result = result.filter(Link.domain.like(form.domain.data + '%'))
            flash(f'Домен: {domain}')
        if domain_zone:
            result = result.filter_by(domain_zone=domain_zone)
            flash(f'Доменная зона: {domain_zone}')
        if result.first():
            links = result.paginate(
                page=page, per_page=LINKS_PER_PAGE, error_out=False
            )
            return (render_template('links_table.html',
                                    form=form,
                                    links=links),
                    HTTPStatus.OK)
        flash('URL с указанными параметрами не найдены.', 'error')
    links = Link.query.paginate(
        page=page, per_page=LINKS_PER_PAGE, error_out=False
    )
    return (render_template('links_table.html', form=form, links=links),
            HTTPStatus.OK)


@app.route('/delete_link/<int:id>')
def delete_link(id):
    db.session.delete(Link.query.get_or_404(id))
    db.session.commit()
    flash('URL удален из ДБ.')
    return redirect(url_for('links_table_view'), HTTPStatus.MOVED_PERMANENTLY)


@app.route('/logs', methods=['GET'])
def logs_view():
    with open('app/log.txt', encoding='utf-8') as file:
        logs = list(deque(file, NUMBER_OF_LOG_LINES))
        return render_template('logs.html', logs=logs), HTTPStatus.OK


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), HTTPStatus.NOT_FOUND
