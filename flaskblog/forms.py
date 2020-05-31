from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username         = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email            = StringField('Email', validators=[DataRequired(), Email()])
    password         = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit           = SubmitField('Register')

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
    username            = StringField('Username', validators=[DataRequired()])
    password         = PasswordField('Password', validators=[DataRequired()])
    # This uses a secure cookie in the browser.
    remember         = BooleanField('Remember Me')
    submit           = SubmitField('Login')



