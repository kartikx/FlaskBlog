from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config


# We don't initialize db with app, this enables
# the usage of same db variables with multiple 
# app configs.
db            = SQLAlchemy()
bcrypt        = Bcrypt()
login_manager = LoginManager()
mail          = Mail()

# this is going to be the same as the function name,
# i.e. the thing you'd pass in to url_for,
# DOUBT confused regarding this, does the route name and function name
# always have to match? read more on this

# You need to specify this, so that login restricted sites
# know what page to show.
login_manager.login_view = 'user.login'

# Specifying this enables a bootstrap-style message.
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    # We have delegated config information to a separate class

    app.config.from_object(config_class)
    db.init_app(app)            
    bcrypt.init_app(app)   
    login_manager.init_app(app) 
    mail.init_app(app)

    from flaskblog.user.routes import user
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    app.register_blueprint(user)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app