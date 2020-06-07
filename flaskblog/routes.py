import os
import secrets
from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreatePostForm
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
from is_safe_url import is_safe_url
from PIL import Image

db.create_all()

@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
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
            return redirect(next_page or url_for("home"))

        else:
            flash("Login Failed, please check your username and password", "danger")

    return render_template('login.html', title = 'Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

def save_picture(form_picture):

    #Randomizing file name, to prevent overwrites.
    # ? Is this correct? Isn't there still a possibility to overwrite?
    f_name = secrets.token_hex(8)

    # Using an unnamed variable as splitext returns the fname and the ext
    _, f_ext = os.path.splitext(form_picture.filename)

    picture_fn = f_name + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)
    
    # Resizing the image to save space
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # Instead of saving the original picture,
    # Save the resized picture instead.
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=["GET", "POST"])
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
        return redirect(url_for('account'))
    
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

@app.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        # ! If you don't add post.user_id it fails the NOT NULL integrity constant.
        # ? We can set this using the author backref.
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post created succesfully!", "success")
        return redirect(url_for("home"))
    return render_template("create_post.html", title="New Post", form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    # This will return the Post if a post with that postId exists
    # Else it will redirect to a 404 page.
    post = Post.query.get_or_404(post_id);
    return render_template("post.html", title=post.title, post=post)
