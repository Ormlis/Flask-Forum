from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from flask_ckeditor import CKEditor
from data import global_init
from config import Config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

ckeditor = CKEditor()
ckeditor.init_app(app)

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

from app.blueprint_pages import blueprint
from app import resources

app.register_blueprint(blueprint)
api = Api(app)

api.add_resource(resources.CommentResource, '/api/comment', '/api/comment/<int:comment_id>')

global_init('db/web.db')
app.run(port=8080, host='127.0.0.1')
