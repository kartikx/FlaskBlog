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
    # through the name 'author'.
    # Posts does NOT get assigned a column in the Database.
    posts = db.relationship('Post', backref=('author'), lazy=True)

    # Example of a magic function, read up.
    # Function responsible for printing when
    # we use CLI to access Database.
    def __repr__(self):
        return f"User('{self.username}','{self.email})"

    # ? There are no security issues here, even if multiple 
    # ? Users try to simult. try reset passwords, because
    # ? of the simple reason that this is a method (segregation of OOP)
    # ? Each user will be given different tokens.
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode('utf-8')
    
    # * This method returns a user if valid token, or None if invalid.
    # ? You need to explicitly define as static, if not using the self variable.
    @staticmethod 
    def verify_reset_token(token):
        # No need to pass in expiration timer here. This just verifies.
        s = Serializer(app.config["SECRET_KEY"])
        try:
            # ? The token that this method is passed, will only have a single user_id
            # ? associated with it. Multiple tokens may exist however if multiple users
            # ? try to reset passwords.
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id) 
        
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
