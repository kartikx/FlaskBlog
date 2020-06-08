from flask import Blueprint, render_template, flash, redirect, abort, url_for, request
from flaskblog import db
from flask_login import current_user, login_required
from flaskblog.models import Post
from flaskblog.posts.forms import CreatePostForm, UpdatePostForm


posts = Blueprint("posts", __name__)

@posts.route("/post/new", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="Create Post", form=form,
                            legend="Create Post")

@posts.route("/post/<int:post_id>")
def post(post_id):
    # This will return the Post if a post with that postId exists
    # Else it will redirect to a 404 page.
    post = Post.query.get_or_404(post_id);
    return render_template("post.html", title=post.title, post=post)

@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
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
        return redirect(url_for("posts.post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template("create_post.html", title="Update Post", form=form,
                            legend="Update Post")


# ? This takes in only a POST Request because you should only
# ? be able to reach this route by filling in the modal.
@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been successfully deleted!", "success")
    return redirect(url_for("main.home"))
