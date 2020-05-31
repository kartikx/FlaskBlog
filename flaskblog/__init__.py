# I think this is the file, first called when we do
# from flaskblog import .. Read up more on packaging.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# A secret key protects your website from attacks. Read more in future.
app.config['SECRET_KEY'] = 'b4fc4568f2af568f30f20d92385ced86'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# this is going to be the same as the function name,
# i.e. the thing you'd pass in to url_for,
# DOUBT confused regarding this, does the route name and function name
# always have to match? read more on this
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# At the end to prevent Circular Imports
from flaskblog import routes

