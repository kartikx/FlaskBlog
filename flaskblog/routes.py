from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required

posts = [
    {
        'author': 'Kartik Ramesh',
        'title': 'First Post',
        'content': 'This is my first post, welcome to my blog!',
        'date_posted': 'May 27, 2020'
    },
    {
        'author': 'Kartik Ramesh',
        'title': 'Second Post',
        'content': 'This is my second post!',
        'date_posted': 'May 29, 2020'
    }
]

db.create_all()

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title = "About Page")

# the methods argument, specifies the requests
# allowed on this page.
@app.route('/register', methods=["GET", "POST"])
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
        return redirect(url_for("login"))

    return render_template('register.html', title = 'Register', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
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
            if not is_safe_url(next_page):
                return flask.abort(400)
            return redirect(next_page or url_for("home"))

        else :
          flash("Login Failed, please check your username and password", "danger")

    return render_template('login.html', title = 'Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/account")
@login_required # to be able to use this, you need to add a login_view to login_manager.
def account():
    return render_template("account.html", title=current_user.username)
