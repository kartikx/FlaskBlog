import os
import secrets
from flaskblog import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CreatePostForm,
                             UpdatePostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
from is_safe_url import is_safe_url
from PIL import Image
from flask_mail import Message
db.create_all()


# ? Since the page variable is not compulsory, we aren't defining a 
# ? variable in the route as in update_post, delete_post.
# ? Instead we're taking in from the query. In home.html, the links
# ? at the bottom of the page are setup so that they pass in a page
# ? parameter to the url_for method. This results in the proper search query.

@app.route('/')
@app.route('/home')
def home():
    # We're getting the page from the URL query, where the default is 1.
    # Setting the type will throw an error,
    # if someone passes a value other than an integer as a page num.
    page  = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=3)

    # So our home.html is always passed in a single page, corresponding to the search query number.
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
    return render_template("create_post.html", title="Create Post", form=form,
                            legend="Create Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    # This will return the Post if a post with that postId exists
    # Else it will redirect to a 404 page.
    post = Post.query.get_or_404(post_id);
    return render_template("post.html", title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id):
    form = UpdatePostForm()
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        # This is an error for unauthorized access.
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # No need to add it to db, as it's already there.
        db.session.commit()
        flash("Your post has been edited successfully!", "success")
        return redirect(url_for("post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template("create_post.html", title="Update Post", form=form,
                            legend="Update Post")


# ? This takes in only a POST Request because you should only
# ? be able to reach this route by filling in the modal.
@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.commit()
    flash("Your post has been successfully deleted!", "success")
    return redirect(url_for("home"))

# ? Route for posts by a particular user
@app.route("/home/<string:username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(per_page=3, page=page)
    return render_template("user_posts.html", posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
{url_for("reset_password", token=token, _external=True)}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)


# ? This route is the page where user request a password reset.
@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    # User should be logged out in order to request password reset
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # No need to check here whether user exists, validate_email does that for us.
        send_reset_email(user)
        flash("An email has been sent to you with instruction on how to reset your password", "info")
        return redirect(url_for("login"))
    return render_template("request_reset.html", title = "Reset Password", form=form)

# The user gets this link through the email we sent him.
# We'll use this to now verify it.
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    # Verifying whether the token is correct.
    user = User.verify_reset_token(token)
    if user is None:
        flash("That token is either invalid or expired", "warning")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been changed", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", title="Reset Password", form=form)
