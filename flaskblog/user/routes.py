from flask import Blueprint, render_template, flash, redirect, abort, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from is_safe_url import is_safe_url
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.user.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                  RequestResetForm, ResetPasswordForm)
from flaskblog.user.utils import save_picture, send_reset_email

user = Blueprint('user', __name__)

#? We're going to create all routes, for this user blueprint
#? and then later link them with the app.

# the methods argument, specifies the requests
# allowed on this page.
@user.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    '''
    The form submission yields a POST request, to the
    same page. Now if the user entered everything properly,
    then we would want to redirect him to the Home Page. Hence,
    we add some functionality, right before the render_template.
    '''
    if form.validate_on_submit() :
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created successfully.", "success")
        return redirect(url_for("user.login"))

    return render_template('register.html', title = 'Register', form=form)

@user.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Read up on Flashing, and how to link-ize this.
        if not user :
          flash("That username does not exist, create an account?", "info")

        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Welcome Back!", "success")

            # At times you'll end up on the Login Page, if you were trying to
            # access some page, that was restricted. It would be nice if after
            # you do Login it takes you to that page, instead of the Home Page.
            # If you wanna understand next page, remove references to next page here,
            # and then try accessing /account without logging in, and look at the
            # search bar query.

            next_page = request.args.get("next")

            # If a next_page exists, you should check if it's safe.
            # Otherwise, someone can add in custom query, and force
            # a redirect to malicious websites.
            if next_page and not is_safe_url(next_page, "localhost:5000"):
                return abort(400)
            return redirect(next_page or url_for("main.home"))

        else:
            flash("Login Failed, please check your username and password", "danger")

    return render_template('login.html', title = 'Login', form=form)

@user.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

@user.route("/account", methods=["GET", "POST"])
@login_required # to be able to use this, you need to add a login_view to login_manager.
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Since profile picture isn't necessary, add a check here to see if
        # anything was put in
        if form.picture.data :
            picture_fn = save_picture(form.picture.data)
            current_user.image_file = picture_fn
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your details have been updated", "success")
        return redirect(url_for('user.account'))
    
    # this will be reached, if the user directly reached this page
    # as opposed to having reached it back by filling the form on it
    # that would have been a POST request.
    # We keep the user's current details prefilled.
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    '''
    It is a good idea, to do as much computation in your py
    files, and then send to your html as a parameter,
    instead of crowding your html with if blocks.
    You can send as many as you want after all.
    '''
    image_src = url_for('static', filename='profilepics/' + current_user.image_file)
    return render_template("account.html", title=current_user.username,
                            image_src=image_src, form=form)


# ? Route for posts by a particular user
@user.route("/home/<string:username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(per_page=3, page=page)
    return render_template("user_posts.html", posts=posts, user=user)

# ? This route is the page where user request a password reset.
@user.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    # User should be logged out in order to request password reset
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # No need to check here whether user exists, validate_email does that for us.
        send_reset_email(user)
        flash("An email has been sent to you with instruction on how to reset your password", "info")
        return redirect(url_for("user.login"))
    return render_template("request_reset.html", title = "Reset Password", form=form)

# The user gets this link through the email we sent him.
# We'll use this to now verify it.
@user.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    # Verifying whether the token is correct.
    user = User.verify_reset_token(token)
    if user is None:
        flash("That token is either invalid or expired", "warning")
        return redirect(url_for("user.reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been changed", "success")
        return redirect(url_for("user.login"))
    return render_template("reset_password.html", title="Reset Password", form=form)
