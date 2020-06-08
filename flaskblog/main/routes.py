from flask import Blueprint, request, render_template
from flaskblog.models import Post

main = Blueprint("main", __name__)

# ! where does this go? should be initialized
# ? I don't think this is needed, once we've initialized our database.
# db.create_all()

# ? Since the page variable is not compulsory, we aren't defining a 
# ? variable in the route as in update_post, delete_post.
# ? Instead we're taking in from the query. In home.html, the links
# ? at the bottom of the page are setup so that they pass in a page
# ? parameter to the url_for method. This results in the proper search query.

@main.route('/')
@main.route('/home')
def home():
    # We're getting the page from the URL query, where the default is 1.
    # Setting the type will throw an error,
    # if someone passes a value other than an integer as a page num.
    page  = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=3)

    # So our home.html is always passed in a single page, corresponding to the search query number.
    return render_template('home.html', posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title = "About Page")
