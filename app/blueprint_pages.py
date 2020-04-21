from app import login_manager, ckeditor
from flask import Blueprint, redirect, render_template, flash, abort, request
from flask_login import login_user, logout_user, login_required, current_user
from data import User, Topic, SubTopic, create_session, Post
from app.forms import LoginForm, RegisterForm, TopicForm, PostForm

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


@blueprint.route('/topic/new', methods=['GET', 'POST'])
@login_required
def add_topic():
    if current_user.role < 3:
        abort(403)
    form = TopicForm()
    if form.validate_on_submit():
        session = create_session()
        topic = Topic(
            title=form.title.data,
            description=form.description.data,
        )
        session.add(topic)
        session.commit()
        flash(f'Topic {form.title.data} successfully created')
        return redirect('/')
    return render_template('edit_topic.html', title='Создание топика', form=form,
                           title_form='Create new topic')


@blueprint.route('/topic/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    if current_user.role < 3:
        abort(403)
    form = TopicForm()
    session = create_session()
    topic = session.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        abort(404)
    if request.method == "GET":
        form.title.data = topic.title
        form.description.data = topic.description
    if form.validate_on_submit():
        topic.title = form.title.data
        topic.description = form.description.data
        session.merge(topic)
        session.commit()
        return redirect('/')
    return render_template('edit_topic.html', title='Редактирование топика', form=form,
                           title_form='Edit topic')


@blueprint.route('/topic/<int:topic_id>/subtopic/new', methods=['GET', 'POST'])
@login_required
def add_subtopic(topic_id):
    if current_user.role < 2:
        abort(403)
    form = TopicForm()
    session = create_session()
    if not session.query(Topic).filter(Topic.id == topic_id).first():
        abort(404)
    if form.validate_on_submit():
        subtopic = SubTopic(
            title=form.title.data,
            description=form.description.data,
            topic_id=topic_id
        )
        session.add(subtopic)
        session.commit()
        flash(f'SubTopic {form.title.data} successfully created')
        return redirect(f'/topic/{topic_id}/subtopic/{subtopic.id}')
    return render_template('edit_topic.html', title='Создание раздела', form=form,
                           title_form='Create new subtopic')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subtopic(topic_id, subtopic_id):
    if current_user.role < 2:
        abort(403)
    session = create_session()
    subtopic = session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                              SubTopic.topic_id == topic_id).first()
    if not subtopic:
        abort(404)
    form = TopicForm()
    if request.method == "GET":
        form.title.data = subtopic.title
        form.description.data = subtopic.description
    if form.validate_on_submit():
        subtopic.title = form.title.data
        subtopic.description = form.description.data
        session.merge(subtopic)
        session.commit()
        return redirect(f'/topic/{topic_id}/subtopic/{subtopic.id}')
    return render_template('edit_topic.html', title='Редактирование раздела', form=form,
                           title_form='Edit subtopic')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/new',
                 methods=['GET', 'POST'])
@login_required
def add_post(topic_id, subtopic_id):
    if current_user.role < 1:
        abort(403)
    session = create_session()
    if not session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                          SubTopic.topic_id == topic_id).first():
        abort(404)
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            description=form.description.data,
            author_id=current_user.id,
            lvl_access=form.lvl_access.data,
            subtopic_id=subtopic_id
        )
        session.add(new_post)
        session.commit()
        flash(f'Post {form.title.data} successfully created')
        return redirect(f'/topic/{topic_id}/subtopic/{subtopic_id}/post/{new_post.id}')
    return render_template('edit_post.html', title='Post creation', form=form,
                           title_form='Create new post')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/<int:post_id>/edit',
                 methods=['GET', 'POST'])
@login_required
def edit_post(topic_id, subtopic_id, post_id):
    if current_user.role < 1:
        abort(403)
    session = create_session()
    current_post = session.query(Post).filter(Post.id == post_id,
                                              Post.subtopic_id == subtopic_id).first()
    if not (current_post and session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                                            SubTopic.topic_id == topic_id).first()):
        abort(404)
    if current_user.role == 1 and current_post.author_id != current_user.id:
        abort(403)
    form = PostForm()
    if request.method == "GET":
        form.title.data = current_post.title
        form.description.data = current_post.description
        form.lvl_access.data = current_post.lvl_access
    if form.validate_on_submit():
        current_post.title = form.title.data
        current_post.description = form.description.data
        current_post.lvl_access = form.lvl_access.data
        session.merge(current_post)
        session.commit()
        return redirect(f'/topic/{topic_id}/subtopic/{subtopic_id}/post/{current_post.id}')
    return render_template('edit_post.html', title='w', form=form,
                           title_form='Edit post')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>')
def subtopic_page(topic_id, subtopic_id):
    session = create_session()
    subtopic = session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                              SubTopic.topic_id == topic_id).first()
    if not subtopic:
        abort(404)
    topic = session.query(Topic).filter(Topic.id == topic_id).first()
    return render_template('subtopic.html', title=topic.title + ' - ' + subtopic.title, topic=topic,
                           subtopic=subtopic)


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/<int:post_id>')
def post_page(topic_id, subtopic_id, post_id):
    pass


@blueprint.route('/user/<int:user_id>')
def user_page(user_id):
    session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404)
