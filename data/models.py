import datetime
import sqlalchemy as sa
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname = sa.Column(sa.String, unique=True, nullable=True)
    surname = sa.Column(sa.String, nullable=True)
    name = sa.Column(sa.String, nullable=True)
    age = sa.Column(sa.Integer, nullable=True)
    email = sa.Column(sa.String, unique=True, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    role = sa.Column(sa.Integer, default=0)
    first_visit = sa.Column(sa.Date, default=datetime.datetime.today())

    posts = orm.relation('Post', back_populates='user')
    comments = orm.relation('Comment', back_populates='user')

    def __repr__(self):
        return f'<{self.nickname}>'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Topic(SqlAlchemyBase):
    __tablename__ = 'topics'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String)
    description = sa.Column(sa.Text)

    subtopics = orm.relation('SubTopic', back_populates='topic')


class SubTopic(SqlAlchemyBase):
    __tablename__ = 'subtopics'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    topic_id = sa.Column(sa.Integer, sa.ForeignKey('topics.id'), nullable=True)
    title = sa.Column(sa.String)
    description = sa.Column(sa.Text)

    topic = orm.relation('Topic')
    posts = orm.relation('Post', back_populates='subtopic')


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    subtopic_id = sa.Column(sa.Integer, sa.ForeignKey('subtopics.id'), nullable=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    title = sa.Column(sa.String)
    lvl_access = sa.Column(sa.Integer)
    description = sa.Column(sa.Text)

    user = orm.relation('User')
    subtopic = orm.relation('SubTopic')
    comments = orm.relation('Comment', back_populates='post')


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'), nullable=True)
    text = sa.Column(sa.TEXT, nullable=True)

    user = orm.relation('User')
    post = orm.relation('Post')
