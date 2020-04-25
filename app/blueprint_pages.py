import os

from flask_mail import Message
from sqlalchemy_pagination import paginate

from app import login_manager, ckeditor, app, mail
from flask import Blueprint, redirect, render_template, flash, abort, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from data import User, Topic, SubTopic, create_session, Post, Comment
from app.forms import LoginForm, RegisterForm, TopicForm, PostForm, CommentForm, \
    ProfileEditForm, ChangePasswordForm
from config import Config
from app.tokenmail import confirm_token, send_mail_to_certify

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
            subtopic_id=subtopic_id,
            published=True if current_user.role >= 1 else False
        )
        session.add(new_post)
        session.commit()
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
@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/page/<int:page>')
def subtopic_page(topic_id, subtopic_id, page=1):
    session = create_session()
    subtopic = session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                              SubTopic.topic_id == topic_id).first()
    if not subtopic:
        abort(404)
    topic = session.query(Topic).filter(Topic.id == topic_id).first()
    lvl_access = current_user.role if current_user.is_authenticated else -1
    current_page = paginate(session.query(Post).filter(Post.subtopic_id == subtopic_id, Post.lvl_access <= lvl_access), page, 3)
    return render_template('subtopic.html', title=topic.title + ' - ' + subtopic.title, topic=topic,
                           subtopic=subtopic, current_page=current_page)


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/<int:post_id>',
                 methods=['GET', 'POST'])
@blueprint.route(
    '/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/<int:post_id>/page/<int:page>',
    methods=['GET', 'POST'])
def post_page(topic_id, subtopic_id, post_id, page=1):
    session = create_session()
    post = session.query(Post).filter(Post.id == post_id,
                                      Post.subtopic_id == subtopic_id).first()
    subtopic = session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                              SubTopic.topic_id == topic_id).first()
    topic = session.query(Topic).filter(Topic.id == topic_id).first()
    if not (post and subtopic and topic):
        abort(404)
    if post.lvl_access > 1 and (current_user.is_authenticated and
                                current_user.role < post.lvl_access and
                                current_user.id != post.author_id):
        abort(403)
    if (not current_user.is_authenticated) or (post.author_id != current_user.id and
                                               not post.published):
        abort(404)

    current_page = paginate(session.query(Comment).filter(Comment.post_id == post_id), page, 20)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            author_id=current_user.id,
            text=form.text.data,
            post_id=post_id
        )
        session.add(comment)
        session.commit()
        return redirect('#')
    liked = list(map(lambda x: x.id,
                     current_user.liked.all())) if current_user.is_authenticated else []
    disliked = list(map(lambda x: x.id,
                        current_user.disliked.all())) if current_user.is_authenticated else []
    return render_template('post.html',
                           title=topic.title + ' - ' + subtopic.title + ' - ' + post.title,
                           topic=topic, subtopic=subtopic, post=post,
                           User=User, session=session, form=form, current_page=current_page,
                           liked=liked, disliked=disliked)


@blueprint.route('/topic/<int:topic_id>/delete', methods=['GET', 'POST'])
@login_required
def topic_delete(topic_id):
    if current_user.role < 3:
        abort(403)
    session = create_session()
    topic = session.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        abort(404)
    session.delete(topic)
    session.commit()
    return redirect('/')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/delete', methods=['GET', 'POST'])
@login_required
def subtopic_delete(topic_id, subtopic_id):
    if current_user.role < 2:
        abort(403)
    session = create_session()
    subtopic = session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                              SubTopic.topic_id == topic_id).first()
    if not subtopic:
        abort(404)
    session.delete(subtopic)
    session.commit()
    return redirect('/')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/<int:post_id>/delete',
                 methods=['GET', 'POST'])
@login_required
def post_delete(topic_id, subtopic_id, post_id):
    if current_user.role < 1:
        abort(403)
    session = create_session()
    post = session.query(Post).filter(Post.id == post_id,
                                      Post.subtopic_id == subtopic_id).first()
    if not (post and session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                                    SubTopic.topic_id == topic_id).first()):
        abort(404)
    if current_user.role == 1 and post.author_id != current_user.id:
        abort(403)
    session.delete(post)
    session.commit()
    return redirect(f'/topic/{topic_id}/subtopic/{subtopic_id}')


@blueprint.route('/user/<int:user_id>')
@login_required
def user_page(user_id):
    session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404)
    if user.role > current_user.role:
        abort(403)
    return render_template('user.html', title=user.nickname, user=user)


@blueprint.route('/user/<int:user_id>/edit',
                 methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404)
    if user.role > current_user.role or (user.id != current_user.id and current_user.role < 3):
        abort(403)
    form = ProfileEditForm()
    if request.method == "GET":
        form.name.data = user.name
        form.surname.data = user.surname
        form.age.data = user.age
    if form.validate_on_submit():
        user.age = form.age.data
        user.surname = form.surname.data
        user.name = form.name.data
        if form.avatar.data:
            user.image = f'{user_id}.jpg'
            form.avatar.data.save(
                os.path.join('app/static', f'img/avatars_users/{user.image}')
            )
        session.merge(user)
        session.commit()
        return redirect(f'/user/{user_id}')
    return render_template('edit_user.html', title='Edit profile', form=form)


@blueprint.route('/user/certify/<token>')
@login_required
def email_certify(token):
    email = confirm_token(token)

    if not email:
        abort(404)

    session = create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        abort(404)

    if user.role >= 1:
        abort(404)

    user.role = 1
    session.merge(user)
    session.commit()
    return redirect(f'/user/{user.id}')


@blueprint.route('/user/certify')
@login_required
def send_mail_page():
    if current_user.role > 0:
        abort(404)
    send_mail_to_certify(current_user)
    return render_template('certify.html', title='Confirmation email')


@blueprint.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        session = create_session()
        current_user.set_password(form.new_password.data)
        session.merge(current_user)
        session.commit()
        return redirect(f'/user/{current_user.id}')
    return render_template('change_password.html', title='Change password', form=form,
                           title_form='Change password')


@blueprint.route('/topic/<int:topic_id>/subtopic/<int:subtopic_id>/post/<int:post_id>/publish"')
@login_required
def publish(topic_id, subtopic_id, post_id):
    if current_user.role < 1:
        abort(403)
    session = create_session()
    post = session.query(Post).filter(Post.id == post_id,
                                      Post.subtopic_id == subtopic_id).first()
    if not (post and session.query(SubTopic).filter(SubTopic.id == subtopic_id,
                                                    SubTopic.topic_id == topic_id).first()):
        abort(404)
    if current_user.role == 1 and post.author_id != current_user.id:
        abort(403)
    post.published = True
    session.merge(post)
    session.commit()
    return redirect(f'/topic/{topic_id}/subtopic/{subtopic_id}')


@blueprint.route('/user/<int:user_id>/downgrade')
@login_required
def downgrade(user_id):
    session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user or user.role <= 0:
        abort(404)
    if current_user.role < 3:
        abort(403)
    user.role -= 1
    session.merge(user)
    session.commit()
    return redirect(f'/user/{user_id}')


@blueprint.route('/user/<int:user_id>/upgrade')
@login_required
def upgrade(user_id):
    session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user or user.role >= 3:
        abort(404)
    if current_user.role < 3:
        abort(403)
    user.role += 1
    session.merge(user)
    session.commit()
    return redirect(f'/user/{user_id}')


@blueprint.route('/users')
@blueprint.route('/users/page/<int:page>')
@login_required
def users_page(page=1):
    if current_user.role < 3:
        abort(403)
    session = create_session()
    current_page = paginate(session.query(User), page, 30)
    return render_template('users.html', title='', current_page=current_page)
