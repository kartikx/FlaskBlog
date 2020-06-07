from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username         = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email            = StringField('Email', validators=[DataRequired(), Email()])
    password         = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit           = SubmitField('Register')

    # Who calls these methods?
    def validate_username(self, username):
        user = User.query.filter_by(username=(username.data)).first()
        if user:
            raise ValidationError(message="That username is unavailable")

    def validate_email(self, email):
        user = User.query.filter_by(email=(email.data)).first()
        if user:
            # I'd like to change the small text below email, to Login for this case.
            raise ValidationError(message="That email is in use. Login?")

class LoginForm(FlaskForm):
    #in the future, add link, login by email instead?
    username         = StringField('Username', validators=[DataRequired()])
    password         = PasswordField('Password', validators=[DataRequired()])
    # This uses a secure cookie in the browser.
    remember         = BooleanField('Remember Me')
    submit           = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField("Change Username to", validators=[DataRequired()])
    email    = StringField("Change Email to", validators=[DataRequired(), Email()])
    picture  = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])]) 
    submit   = SubmitField("Update")

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(message= "That username is unavailable")

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=(email.data)).first()
            if user:
                raise ValidationError(message="That email is unavailable.")

class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create")

class UpdatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Update")