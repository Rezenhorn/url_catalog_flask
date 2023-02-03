from collections import deque

from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app import db
from config import LINKS_PER_PAGE, NUMBER_OF_LOG_LINES
from app.main.forms import CSVForm, LinkForm, SearchForm
from app.models import Link
from app.utils import add_links_to_db_from_file, add_link_to_db
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index_view():
    form_link = LinkForm()
    form_file = CSVForm()
    try:
        if form_file.validate_on_submit():
            file = form_file.data.get('csv_file')
            if file:
                result = add_links_to_db_from_file(file)
                flash(f'Обработано {result["links_to_process"]} URL из файла. '
                      f'{result["success_additions"]} URL добавлено в БД.')
                return render_template(
                    'add_link.html', form_link=form_link, form_file=form_file)
        if form_link.validate_on_submit():
            url = form_link.link.data
            form_link.link.data = ''
            add_link_to_db(url)
            flash('URL добавлен в БД.')
            return render_template(
                'add_link.html', form_link=form_link, form_file=form_file)
    except Exception as error:
        flash(f'Ошибка: {error}.', 'error')
    return render_template(
        'add_link.html', form_link=form_link, form_file=form_file)


@bp.route('/links_table', methods=['GET', 'POST'])
@bp.route('/links_table/<int:page>', methods=['GET', 'POST'])
@login_required
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
            return render_template('links_table.html', form=form, links=links)
        flash('URL с указанными параметрами не найдены.', 'error')
    links = Link.query.paginate(
        page=page, per_page=LINKS_PER_PAGE, error_out=False
    )
    return render_template('links_table.html', form=form, links=links)


@bp.route('/delete_link/<int:id>')
@login_required
def delete_link(id):
    db.session.delete(Link.query.get_or_404(id))
    db.session.commit()
    flash('URL удален из ДБ.')
    return redirect(url_for('main.links_table_view'))


@bp.route('/logs', methods=['GET'])
@login_required
def logs_view():
    with open('app/application.log', encoding='utf-8') as file:
        logs = reversed(list(deque(file, NUMBER_OF_LOG_LINES)))
        return render_template('logs.html', logs=logs)
