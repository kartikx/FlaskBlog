from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

# The Post model and the User Model have a
# many to one relationship. Also, Models are
# representative of tables in the database. Each class
# that you inherit from db.Model,
# leads to the creation of a table with the
# same name (except lowercased)

#This is a function required for login.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# UserMixin adds a lot of methods to your class,
# needed for log-in
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20) , unique = True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # The backref allows the Post class to access the corresponding User
    # through the name 'author'. Read up on Lazy.
    # Posts does NOT get assigned a column in the Database.
    # You can use user.author to access posts of this user.
    posts = db.relationship('Post', backref=('author'), lazy=True)

    # Example of a magic function, read up.
    # Function responsible for printing when
    # we use CLI to access Database.
    def __repr__(self):
        return f"User('{self.username}','{self.email})"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # We aren't using () after utcnow,
    # because we don't wanna call the function here.
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    # Using lowercase (user), because Foreign Key accesses the table name.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}, {self.date_posted}')"
