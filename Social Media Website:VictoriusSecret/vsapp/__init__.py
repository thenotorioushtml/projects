from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

# App configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomcharachters'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///victorious_secret.db'
# Database initialization and password crypting
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)

# from vsapp import routes
from vsapp import routes
