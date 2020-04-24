from flask import jsonify
from flask_restful import reqparse, abort, Resource
from data import create_session, User, Topic, SubTopic, Post, Comment


def abort_if_object_not_found(object_id, object_type):
    session = create_session()
    find_object = session.query(object_type).get(object_id)
    if not find_object:
        abort(404, message=f"{object_type.__name__} {object_id} not found")


class UserResource(Resource):

    def get(self, user_id):
        abort_if_object_not_found(user_id, User)
        session = create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict()})

    def delete(self, user_id):
        abort_if_object_not_found(user_id, User)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('nickname', required=True)
    parser.add_argument('surname', required=True)
    parser.add_argument('name', required=True)
    parser.add_argument('email', required=True)
    parser.add_argument('age', required=True, type=int)

    def get(self):
        session = create_session()
        users = session.query(User).all()
        return jsonify({'comments': [item.to_dict() for item in users]})

    def post(self):
        args = self.parser.parse_args()
        session = create_session()
        user = User(
            nickname=args['nickname'],
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            email=args['email']
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('text')
    parser.add_argument('post_id', type=int)
    parser.add_argument('author_id', type=int)
    parser.add_argument('reputation', type=int)
    parser.add_argument('by_user', type=int)

    def get(self, comment_id):
        abort_if_object_not_found(comment_id, Comment)
        session = create_session()
        comment = session.query(Comment).get(comment_id)
        return jsonify({'comment': comment.to_dict(
            only=('text', 'author_id', 'post_id'))})

    def delete(self, comment_id):
        abort_if_object_not_found(comment_id, Comment)
        session = create_session()
        comment = session.query(Comment).get(comment_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, comment_id):
        args = self.parser.parse_args()
        abort_if_object_not_found(comment_id, Comment)
        session = create_session()
        comment = session.query(Comment).get(comment_id)
        user = comment.user
        by_user_id = args.get('by_user', 0)
        byuser = session.query(User).get(by_user_id)
        if user and byuser:
            if comment in byuser.liked:
                user.reputation -= 1
                byuser.liked.remove(comment)
            elif comment in byuser.disliked:
                user.reputation += 1
                byuser.disliked.remove(comment)
            if args.get('reputation', 0) == 1:
                user.reputation += 1
                byuser.liked.append(comment)
            elif args.get('reputation', 0) == -1:
                user.reputation -= 1
                byuser.disliked.append(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('text', required=True)
    parser.add_argument('post_id', required=True, type=int)
    parser.add_argument('author_id', required=True, type=int)

    def get(self):
        session = create_session()
        comments = session.query(Comment).all()
        return jsonify({'comments': [item.to_dict(
            only=('text', 'author_id', 'post_id')) for item in comments]})

    def post(self):
        args = self.parser.parse_args()
        session = create_session()
        comment = Comment(
            author_id=args['author_id'],
            post_id=args['post_id'],
            text=args['text']
        )
        session.add(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class PostResource(Resource):
    def get(self, post_id):
        abort_if_object_not_found(post_id, Post)
        session = create_session()
        post = session.query(Post).get(post_id)
        return jsonify({'post': post.to_dict(
            only=('title', 'author_id', 'lvl_access'))})

    def delete(self, post_id):
        abort_if_object_not_found(post_id, Post)
        session = create_session()
        post = session.query(Post).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


class PostListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('subtopic_id', required=True, type=int)
    parser.add_argument('author_id', required=True, type=int)
    parser.add_argument('lvl_access', required=True, type=int)

    def get(self):
        session = create_session()
        posts = session.query(Post).all()
        return jsonify({'posts': [item.to_dict(
            only=('title', 'author_id', 'lvl_access')) for item in posts]})

    def post(self):
        args = self.parser.parse_args()
        session = create_session()
        post = Post(
            title=args['title'],
            subtopic_id=args['subtopic_id'],
            author_id=args['author_id'],
            lvl_access=args['lvl_access'],
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})


class SubtopicResource(Resource):
    def get(self, subtopic_id):
        abort_if_object_not_found(subtopic_id, SubTopic)
        session = create_session()
        subtopic = session.query(SubTopic).get(subtopic_id)
        return jsonify({'subtopic': subtopic.to_dict(
            only=('title', 'topic_id'))})

    def delete(self, subtopic_id):
        abort_if_object_not_found(subtopic_id, SubTopic)
        session = create_session()
        subtopic = session.query(SubTopic).get(subtopic_id)
        session.delete(subtopic)
        session.commit()
        return jsonify({'success': 'OK'})


class SubtopicListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('topic_id', required=True, type=int)

    def get(self):
        session = create_session()
        subtopics = session.query(SubTopic).all()
        return jsonify({'subtopics': [item.to_dict(
            only=('title', 'topic_id')) for item in subtopics]})

    def post(self):
        args = self.parser.parse_args()
        session = create_session()
        subtopic = SubTopic(
            title=args['title'],
            topic_id=args['topic_id']
        )
        session.add(subtopic)
        session.commit()
        return jsonify({'success': 'OK'})


class TopicResource(Resource):
    def get(self, topic_id):
        abort_if_object_not_found(topic_id, Topic)
        session = create_session()
        topic = session.query(Topic).get(topic_id)
        return jsonify({'topic': topic.to_dict(
            only=('title',))})

    def delete(self, topic_id):
        abort_if_object_not_found(topic_id, Topic)
        session = create_session()
        topic = session.query(Topic).get(topic_id)
        session.delete(topic)
        session.commit()
        return jsonify({'success': 'OK'})


class TopicListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)

    def get(self):
        session = create_session()
        topics = session.query(Topic).all()
        return jsonify({'topics': [item.to_dict(
            only=('title',)) for item in topics]})

    def post(self):
        args = self.parser.parse_args()
        session = create_session()
        topic = Topic(
            title=args['title'],
        )
        session.add(topic)
        session.commit()
        return jsonify({'success': 'OK'})
