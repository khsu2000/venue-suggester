"""
Utility functions and classes.
"""
import json
from urllib.parse import quote

DEFAULT_METER_CNT = 8046

class Venue:
    """
    Class used to store venue data.
    Attributes include id, location, and name.
    """
    def __init__(self, venue_dictionary):
        self.id = venue_dictionary["id"]
        self.location = venue_dictionary["location"]
        self.name = venue_dictionary["name"]
        self.details = venue_dictionary.get("details", None) 
        self.description = venue_dictionary.get("description", None)
        self.url = venue_dictionary.get("url", None)
        self.canonical_url = venue_dictionary.get("canonical_url", None)
        self.rating = venue_dictionary.get("rating", None)
        self.contacts = venue_dictionary.get("contacts", None)
        self.hours = venue_dictionary.get("hours", None)

    def assign_members(self):
        # Assigns values to all attributes
        # Calls all get functions at once to try to improve caching
        self.description = self.get_description()
        self.url = self.get_url()
        self.canonical_url = self.get_canonical_url()
        self.rating = self.get_rating()
        self.contacts = self.get_contacts()
        self.hours = self.get_hours()

    def get_name(self):
        # Returns name (string)
        return self.name

    def get_id(self):
        # Returns id (string)
        return self.id

    def get_location(self):
        # Returns location (dictionary)
        return self.location

    def get_latlng(self):
        # Returns latitude, longitude coordinates (tuple (float, float))
        return (self.location["lat"], self.location["lng"])

    def get_address(self):
        # Returns formatted address (list of strings)
        return self.location["formattedAddress"]

    def get_hours(self):
        # Returns string in the form of Open "day range" from "time range".
        # Returns empty string if day range or time range not found 
        if self.hours != None:
            return self.hours
        if self.details == None:
            self.hours = "Hours not listed."
            return self.hours
        try:
            days = self.details.get("hours", {}).get("timeframes", [{}])[0].get("days", "")
            hours = self.details.get("hours", {}).get("timeframes", [{}])[0].get("open", [{}])[0].get("renderedTime", "")
            if not days or not hours:
                return "Hours not listed."
            self.hours = "".join(["Open ", days, " for/from ", hours, "."])
            return self.hours
        except:
            self.hours = "Hours not listed."
            return self.hours

    def get_description(self):
        # Returns provided description extracted from details (string)
        # Returns empty string if 'details' is None or no description provided
        if self.description != None:
            return self.description
        if self.details == None or not self.details.get("description", None):
            self.description = ""
        else:
            self.description = self.details["description"]
        return self.description

    def get_url(self):
        # Returns provided url extracted from details (string) 
        # Returns empty string if 'details' is None or no url provided
        if self.url != None: 
            return self.url 
        if self.details == None or not self.details.get("url", None):
            self.url = ""
        else:
            self.url = self.details["url"]
        return self.url

    def get_canonical_url(self):
        # Returns provided canonical url extracted from details (string) 
        # Returns empty string if 'details' is None or no canonical url provided
        if self.canonical_url != None:
            return self.canonical_url
        if self.details == None or not self.details.get("canonicalUrl", None):
            self.canonical_url = ""
        else:
            self.canonical_url = self.details["canonicalUrl"]
        return self.canonical_url

    def get_rating(self):
        # Returns provided rating extracted from details (int)
        # Returns -1 if 'details' is None or no rating provided
        if self.rating != None:
            return self.rating
        if self.details == None:
            self.rating = -1
        else:
            self.rating = self.details.get("rating", -1)
        return self.rating

    def get_contacts(self):
        # Returns dictionary of contact links and phone number (string, string) 
        # Returns empty dictionary if 'details' is None or no contacts provided
        if self.contacts != None:
            return self.contacts
        self.contacts = {}
        if self.details != None and self.details.get("contact", None):
            self.contacts = {}
            media_prefixes = ["https://www.facebook.com/", "https://twitter.com/", "https://www.instagram.com/"]
            old_media_keys = ["facebookUsername", "twitter", "instagram"]
            new_media_keys = ["Facebook", "Twitter", "Instagram"] 
            for i in range(3):
                media_contact = self.details["contact"].get(old_media_keys[i], "")
                if media_contact:
                    self.contacts[new_media_keys[i]] = "".join([media_prefixes[i], media_contact])
            self.contacts["Phone Number"] = self.details["contact"].get("formattedPhone", "")
            unformatted_number = self.details["contact"].get("phone", "")
            if len(unformatted_number) == 10:
                self.contacts["Phone Number href"] = "".join([unformatted_number[0:3], "-", unformatted_number[3:6], "-", unformatted_number[6:]])
            else:
                self.contacts["Phone Number href"] = ""
        return self.contacts

    def get_maps_link(self):
        # Returns google maps link (string) 
        full_address = ", ".join(self.get_address())
        query = quote(" ".join([self.name, full_address]))
        return "".join(["https://www.google.com/maps/search/?api=1&query=", query])

    def to_dict(self):
        # Returns dictionary representation of Venue object.
        d = {
            "id": self.id,
            "location": self.location,
            "name": self.name
        }
        remaining_attribute_names = ["details", "description", "url", "canonical_url", "rating", "contacts", "hours"]
        remaining_attribute_vals = [self.details, self.description, self.url, self.canonical_url, self.rating, self.contacts, self.hours]
        for i in range(len(remaining_attribute_names)):
            if remaining_attribute_vals[i]:
                d[remaining_attribute_names[i]] = remaining_attribute_vals[i]
        return d

    def __str__(self):
        return "Venue(id = {0}, address = {1}, name = {2})".format(self.id, self.get_address(), self.name)

    def __repr__(self):
        return "Venue(id = {0}, address = {1}, name = {2})".format(self.id, self.get_address(), self.name)

def miles_to_meters(miles):
    """
    Converts miles to meters. 

    Parameters:
    -----------
    miles (float): Miles to be converted. 

    Returns:
    --------
    int: Number of equivalent meters. If it encounters an error, returns DEFAULT_METER_CNT. 
    """
    try:
        return int(miles * 1609.34)
    except:
        return DEFAULT_METER_CNT

def write_to_json(data, filename):
    """
    Saves data to json file specified by filename.

    Parameters:
    -----------
    data (dictionary): Data to be saved to file.
    filename (string): Name of file to save data to.

    Returns:
    --------
    None
    """
    try:
        with open(filename, "w+") as f:
          json.dump(data, f, sort_keys = True, indent = 4)
        f.close()
    except Exception as e:
        print("Failed to save to {0}: {1}".format(filename, e))

def read_from_json(filename):
    """
    Reads location data from json file.

    Parameters:
    -----------
    filename (string): Name of file that data is read from.

    Returns:
    --------
    dictionary: A dictionary containing data stored from filename.json.
    """
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        f.close()
        return data
    except Exception as e:
        print("Failed to load from {0}: {1}".format(filename, e))

def venues_to_dicts(venue_list):
    """
    Returns list of dictionaries given list of Venue objects.

    Parameters:
    -----------
    venue_list (list): A list of Venue objects.

    Returns:
    --------
    list: A list of dictionaries. Returns original object if encounters failure.
    """
    try:
        return [venue.to_dict() for venue in venue_list]
    except Exception as e:
        return venue_list

def dicts_to_venues(dicts_list):
    """
    Returns list of Veune objects given list of dictionaries.

    Parameters:
    -----------
    dicts_list (list): A list of dictionaries corresponding to venue data.

    Returns:
    --------
    list: A list of Venue objects. Returns original object if encounters failure. 
    """
    try: 
        return [Venue(d) for d in dicts_list]
    except Exception as e:
        try:
            return [Venue(d["venue"]) for d in dicts_list]
        except Exception as e:
            return dicts_list
