"""
Utility functions and classes.
"""
import json

class Venue:
    """
    Class used to store venue data.
    Attributes include id, location, and name.
    """
    def __init__(self, venue_dictionary):
        self.id = venue_dictionary["id"]
        self.location = venue_dictionary["location"]
        self.name = venue_dictionary["name"]

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

    def to_dict(self):
        # Returns dictionary representation of Venue object.
        return {
            "id" : self.id,
            "location" : self.location,
            "name" : self.name}

    def __str__(self):
        return "Venue(id = {0}, address = {1}, name = {2})".format(self.id, self.get_address(), self.name)

    def __repr__(self):
        return "Venue(id = {0}, address = {1}, name = {2})".format(self.id, self.get_address(), self.name)

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
    list: A list of dictionaries.
    """
    return [venue.to_dict() for venue in venue_list]

def dicts_to_venues(dicts_list):
    """
    Returns list of Veune objects given list of dictionaries.

    Parameters:
    -----------
    dicts_list (list): A list of dictionaries corresponding to venue data.

    Returns:
    --------
    list: A list of Venue objects.
    """
    return [Venue(d["venue"]) for d in dicts_list]
