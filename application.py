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
from search_for_venues import nearby_venues, get_details, distance_weighted_order
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
    next_query = SubmitField("Next Suggestion")

class PrevVenue(FlaskForm):
    prev_query = SubmitField("Previous Suggestion")

@app.route("/home")
@app.route("/", methods = ["POST", "GET"])
def home():
    global location_data
    global venues
    global original_location
    global query
        
    # Instantiation of forms 
    form = TakeQuery()
    next_venue = NextVenue()
    prev_venue = PrevVenue()
    
    # Repeatedly attempt to get IP address until successful 
    location_data = {}
    while "timestamp" not in location_data.keys()\
        or "latitude" not in location_data.keys()\
        or "longitude" not in location_data.keys()\
        or "city" not in location_data.keys():
        location_data = get_location_data()
    original_location = (location_data["latitude"], location_data["longitude"])
    
    if form.validate_on_submit():
        # Case where main button is clicked 
        venues = []

        # No venues observed yet, get list of venues
        while len(venues) == 0:
            query = form.query.data
            venues = nearby_venues(location_data, query)
            if venues == "API Usage Exceeded":
                # Case that API does not allow new requests, nothing to do 
                return render_template("home.html", form = form, suggested = None, exhausted = False, exceeded = True)
            if venues == []:
                # Case that there are no venues found 
                return render_template("home.html", form = form, suggested = None, exhausted = True)
            venues = distance_weighted_order(venues, original_location)
        
        # Successfully acquired list of venues at this point 
        suggested = venues.pop(0)
        if get_details(suggested) == "API Usage Exceeded":
            # Case that API does not allow new requests, nothing to do 
            return render_template("home.html", form = form, suggested = None, exhausted = False, exceeded = True)
        return render_template("home.html", form = form, next_venue = next_venue, suggested = suggested)

    if next_venue.validate_on_submit():
        # Case where 'next venue' button is clicked
        if len(venues) == 0:
            # Case where there are no more venues remaining 
            return render_template("home.html", form = form, suggested = None, exhausted = True)
        suggested = venues.pop(0)
        if get_details(suggested) == "API Usage Exceeded":
            # Case that API does not allow new requests, nothing to do 
            return render_template("home.html", form = form, suggested = None, exhausted = False, exceeded = True)
        return render_template("home.html", form = form, next_venue = next_venue, suggested = suggested)

    # Default case where neither button has been clicked
    return render_template("home.html", form = form, suggested = None, exhausted = False)

@app.route("/about", methods = ["POST", "GET"])
def about():
    return render_template("about.html", title = "About")
