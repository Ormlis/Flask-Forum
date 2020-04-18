from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from flask_ckeditor import CKEditor
from data import global_init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key_secret_a_lot'

ckeditor = CKEditor()
ckeditor.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

from app.blueprint_pages import blueprint

app.register_blueprint(blueprint)
api = Api(app)

global_init('db/web.db')
app.run(port=8080, host='127.0.0.1')
