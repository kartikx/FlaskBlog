from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

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

# A secret key protects your website from attacks. Read more in future.
app.config['SECRET_KEY'] = 'b4fc4568f2af568f30f20d92385ced86'

@app.route('/')  # / is the root page
@app.route('/home')  # it's easy to stack up routes similar to switch cases
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
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))

    return render_template('register.html', title = 'Register', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "kartik@test.com" and form.password.data == "password" :
            flash("Welcome Back!", "success")
            return redirect(url_for('home'))
        else :
            flash("Login Failed, please check your username and password", "danger")
    return render_template('login.html', title = 'Login', form=form)


if __name__ == "__main__":
    app.run(debug=True)
