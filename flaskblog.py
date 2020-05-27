from flask import Flask
'''
__name__ is a special variable in python
that stores the name of the module
'''
app = Flask(__name__)

'''
route is a complicated function, that is
recommended to dive deeper into only much later.
It handles much of the complicated backend. In
essence, it allows us to create a function, that
executes on our website, on the particular route
provided to it
'''


@app.route('/')  # / is the root page
@app.route('/home') #it's easy to stack up routes similar to switch cases
def hello_world():
    return '<h1> Hello, Kartik! </h1>'

@app.route('/about')
def about_me():
    return '<h2> Hello! </h2> I\'m a programmer from Faridabad!'
