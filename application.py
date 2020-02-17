from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators

app = Flask(__name__, template_folder = "templates")
app.config["SECRET_KEY"] = "d3b157034a1d5e676a229d3c9653042c"

"""
Accessing Backend Functions
"""
import sys
sys.path.insert(0, "./backend")
from get_current_location import get_location_data
from search_for_venues import nearby_venues, distance_weighted_order
from utils import Venue, venues_to_dicts, dicts_to_venues

"""
Global Variables
"""
location_data = {}
venues = []
original_location = ()
query = ""

"""
Form Class for Main Page
"""
class TakeQuery(FlaskForm):
    query = StringField("What's in store today?", validators = [validators.DataRequired()])
    submit = SubmitField("Go bears!!!!!")

class NextVenue(FlaskForm):
    next_query = SubmitField("That's Not It. Another one!")

@app.route("/home")
@app.route("/", methods = ["POST", "GET"])
def home():
    global location_data
    global venues
    global original_location
    global query
    form = TakeQuery()
    next = NextVenue()
    if form.validate_on_submit():
        location_data = {}
        venues = []
        while "timestamp" not in location_data.keys()\
            or "latitude" not in location_data.keys()\
            or "longitude" not in location_data.keys()\
            or "city" not in location_data.keys():
            location_data = get_location_data()
        original_location = (location_data["latitude"], location_data["longitude"])
        while len(venues) == 0:
            query = form.query.data
            venues = nearby_venues(location_data, query)
            venues = distance_weighted_order(venues, original_location)
            if venues == []:
                return render_template("home.html", form = form, exhausted = True)
        suggested = venues.pop(0)
        return render_template("home.html", form = form, next = next, suggestion_name = suggested.get_name(), suggestion_address = suggested.get_address())
    if next.validate_on_submit():
        if len(venues) == 0 and query != "":
            return render_template("home.html", form = form, exhausted = True)
        elif len(venues) == 0:
            return render_template("home.html", form = form)
        suggested = venues.pop(0)
        return render_template("home.html", form = form, next = next, suggestion_name = suggested.get_name(), suggestion_address = suggested.get_address())
    return render_template("home.html", form = form)

@app.route("/about", methods = ["POST", "GET"])
def about():
    return render_template("about.html", title = "About")
