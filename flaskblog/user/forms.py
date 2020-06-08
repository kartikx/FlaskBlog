from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import User

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

class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[Email()])
    submit = SubmitField("Request Password Reset")

    # Note that the validator is passed in the email Field not the email data.
    # ? Need to read up on custom validators and how they work.
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(message="That email is not registered.")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")