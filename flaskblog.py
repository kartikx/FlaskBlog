from flask import Flask, render_template, url_for

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

app = Flask(__name__)


@app.route('/')  # / is the root page
@app.route('/home')  # it's easy to stack up routes similar to switch cases
def hello_world():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about_me():
    return render_template('about.html', title = "About Page")


if __name__ == "__main__":
    app.run(debug=True)
