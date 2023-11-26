from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

CORS(app, origins="http://127.0.0.1:5001", allow_headers="*", supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados.db'
app.config['SECRET_KEY'] = '1234'

# Configurações para uploads
app.config['UPLOAD_FOLDER'] = 'app\static\imagens'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login_post'
login_manager.init_app(app)

from .models import Usuario
from app import routes

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))