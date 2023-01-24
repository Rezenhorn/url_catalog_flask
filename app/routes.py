from collections import deque
from http import HTTPStatus

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

from app import app, db
from config import LINKS_PER_PAGE, NUMBER_OF_LOG_LINES

from .forms import LinkForm, LoginForm, RegistrationForm, SearchForm
from .models import Link, User
from .utils import add_links_to_db_from_file, add_link_to_db


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_view'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index_view')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index_view'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index_view'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index_view():
    form = LinkForm()
    if form.validate_on_submit():
        try:
            file = form.data.get('csv_file')
            if file:
                result = add_links_to_db_from_file(file)
                flash(f'Обработано {result["links_to_process"]} URL из файла. '
                      f'{result["success_additions"]} URL добавлено в БД.')
                return (render_template('add_link.html', form=form),
                        HTTPStatus.CREATED)
            url = form.link.data
            form.link.data = ''
            add_link_to_db(url)
            flash('URL добавлен в БД.')
            return render_template('add_link.html', form=form)
        except Exception as error:
            flash(f'Ошибка: {error}.', 'error')
    return render_template('add_link.html', form=form)


@app.route('/links_table', methods=['GET', 'POST'])
@app.route('/links_table/<int:page>', methods=['GET', 'POST'])
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


@app.route('/delete_link/<int:id>')
@login_required
def delete_link(id):
    db.session.delete(Link.query.get_or_404(id))
    db.session.commit()
    flash('URL удален из ДБ.')
    return redirect(url_for('links_table_view'))


@app.route('/logs', methods=['GET'])
@login_required
def logs_view():
    with open('app/log.txt', encoding='utf-8') as file:
        logs = reversed(list(deque(file, NUMBER_OF_LOG_LINES)))
        return render_template('logs.html', logs=logs)
