from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def render_homepage():
    return '<h1>Hello, World!</h1>'
    return render_template("home.html")

@app.route('/menu')
def render_menu_page():
    return render_template("menu.html")

@app.route('/contact')
def render_contact():
    return render_template("contact.html")

@app.route('/menu')
def render_homepage():
     return render_template("menu.html")

@app.route('/contact')
def render_homepage():
     return render_template("contact.html")

app.run(host="0.0.0.0")