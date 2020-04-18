from app import login_manager, ckeditor
from flask import Blueprint, redirect, render_template, flash, abort, request
from flask_login import login_user, logout_user, login_required, current_user
from data import User, Topic, SubTopic, create_session, Post
from app.forms import LoginForm, RegisterForm

blueprint = Blueprint('blueprint_pages',
                      __name__,
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('/')
@blueprint.route('/index')
def index():
    session = create_session()
    topics = session.query(Topic).all()
    return render_template('index.html', title='TechnoForum', topics=topics)


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@blueprint.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong email or password",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@blueprint.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        session = create_session()
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            nickname=form.nickname.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('registration.html', title='Registration', form=form)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
