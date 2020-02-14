from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators

app = Flask(__name__, template_folder = "templates")
app.config["SECRET_KEY"] = "d3b157034a1d5e676a229d3c9653042c"

"""
Global Variables
"""

"""
Form Class for Main Page
"""
class MainForm(FlaskForm):
    query = StringField("Any Ideas ig?", validators = [validators.DataRequired()])
    submit = SubmitField("Go bears!!!!!")

@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/going_places", methods = ["POST", "GET"])
def get_suggestion():
    form = MainForm()
    return render_template("suggest.html", form = form)
