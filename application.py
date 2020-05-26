from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

app = Flask(__name__, template_folder = "templates")
app.config["SECRET_KEY"] = "d3b157034a1d5e676a229d3c9653042c"

"""
Accessing Backend Functions
"""
import sys
sys.path.insert(0, "./backend")
from get_current_location import get_location_data
from search_for_venues import nearby_venues, get_details, distance_weighted_order
from utils import Venue, venues_to_dicts, dicts_to_venues, miles_to_meters

"""
Constants for Errors 
"""
API_REQUEST = 0
NO_VENUES = 1

"""
Form Class for Main Page
"""
class TakeQuery(FlaskForm):
    query = StringField("What's in store today?", validators = [DataRequired(message = "Please enter at least one keyword.")])
    radius = FloatField("Maximum Distance (miles)", validators = [NumberRange(0, 50, "Please enter a distance between 0 and 50."), Optional()])
    submit = SubmitField("Give me some suggestions!")

class NextVenue(FlaskForm):
    next_query = SubmitField("Next Suggestion")

class PrevVenue(FlaskForm):
    prev_query = SubmitField("Previous Suggestion")

@app.route("/home")
@app.route("/", methods = ["POST", "GET"])
def home():
    # global location_data
    # global venues
    # global original_location
    # global query
    # global suggested_index
    # global radius
        
    # Instantiation of forms 
    form = TakeQuery()
    next_venue = NextVenue()
    prev_venue = PrevVenue()
    
    # Repeatedly attempt to get IP address until successful 
    session["location_data"] = {}
    while "timestamp" not in session["location_data"].keys()\
        or "latitude" not in session["location_data"].keys()\
        or "longitude" not in session["location_data"].keys()\
        or "city" not in session["location_data"].keys():
        session["location_data"] = get_location_data()
    session["original_location"] = (session["location_data"]["latitude"], session["location_data"]["longitude"])
    
    if form.validate_on_submit():
        # Case where main button is clicked 
        session["venues"] = []

        # No venues observed yet, get list of venues
        while len(session["venues"]) == 0:
            session["query"] = form.query.data
            session["radius"] = miles_to_meters(form.radius.data)
            session["venues"] = nearby_venues(session["location_data"], session["query"], session["radius"])
            if session["venues"] == "API Usage Exceeded":
                # Case that API does not allow new requests, nothing to do 
                return render_template("home.html", form = form, error_status = API_REQUEST)
            if session["venues"] == []:
                # Case that there are no venues found 
                return render_template("home.html", form = form, error_status = NO_VENUES)
            session["venues"] = distance_weighted_order(session["venues"], session["original_location"])

        # Successfully acquired list of venues at this point 
        session["suggested_index"] = 0
        suggested = session["venues"][session["suggested_index"]]
        if suggested.details == None:
            if get_details(suggested) == "API Usage Exceeded":
                # Case that API does not allow new requests, nothing to do 
                return render_template("home.html", form = form, error_status = API_REQUEST)
        suggested.assign_members()
        if len(session["venues"]) == 1:
            return render_template("home.html", form = form, suggested = suggested)
        return render_template("home.html", form = form, next_venue = next_venue, suggested = suggested)

    if prev_venue.prev_query.data and prev_venue.validate():
        # Case where 'prev venue' button is clicked
        if session["suggested_index"] <= 1:
            # Case where there are no prev venues following this query
            session["suggested_index"] = max(session["suggested_index"] - 1, 0)
            return render_template("home.html", form = form, next_venue = next_venue, suggested = session["venues"][session["suggested_index"]])
        session["suggested_index"] -= 1
        suggested = session["venues"][session["suggested_index"]]
        if suggested.details == None:
            if get_details(suggested) == "API Usage Exceeded":
                # Case that API does not allow new requests, nothing to do 
                return render_template("home.html", form = form, error_status = API_REQUEST)
        return render_template("home.html", form = form, prev_venue = prev_venue, next_venue = next_venue, suggested = suggested)

    if next_venue.next_query.data and next_venue.validate():
        # Case where 'next venue' button is clicked
        if session["suggested_index"] >= len(session["venues"]) - 2:
            # Case where there are no next venues following this query
            session["suggested_index"] = min(session["suggested_index"] + 1, len(session["venues"]) - 1)
            return render_template("home.html", form = form, prev_venue = prev_venue, suggested = session["venues"][session["suggested_index"]])
        session["suggested_index"] += 1
        suggested = session["venues"][session["suggested_index"]]
        if suggested.details == None:
            if get_details(suggested) == "API Usage Exceeded":
                # Case that API does not allow new requests, nothing to do 
                return render_template("home.html", form = form, error_status = API_REQUEST)
        return render_template("home.html", form = form, prev_venue = prev_venue, next_venue = next_venue, suggested = suggested)

    # Default case where neither button has been clicked
    return render_template("home.html", form = form)

@app.route("/about", methods = ["POST", "GET"])
def about():
    return render_template("about.html", title = "Venue Suggester - About Page")
