"""
Uses Foursquare's Places API to search for nearby venues given location data and other parameters. 
""" 

import config
import numpy as np
import json
import requests
from get_current_location import write_to_json, read_from_json

def nearby_venues(location_data, query, radius = 16000, limit = 50):
    """
    Makes request to Foursquare Places explore and returns the results. 

    Parameters:
    -----------
    location_data (dictionary): Contains location data from ipinfo and timestamp. 
    query (string): A category used to select venues (eg. coffee).
    radius (int / float): Radius to search within in meters. Defaults to 16,000 meters, or about 10 miles. 
        The maximum valid value of radius is 100,000 meters. 
    limit (int): Number of results to return. Default value is 50, which is also the maximum number.

    Returns:
    --------
    list: List of venues and info from GET request. Upon failure, returns empty dictionary.
    """
    try:
        url = "https://api.foursquare.com/v2/venues/explore"
        year = location_data["timestamp"][0:4]
        month = location_data["timestamp"][5:7]
        day = location_data["timestamp"][8:10]
        params = dict(
            client_id = config.foursquare_client_id,
            client_secret = config.foursquare_client_secret, 
            ll = ",".join([str(location_data["latitude"]), str(location_data["longitude"])]),
            near = location_data["city"],
            v = "".join([year, month, day]),
            radius = radius, 
            query = query, 
            limit = limit, 
            openNow = 1 
        )
        resp = requests.get(url = url, params = params)
        data = json.loads(resp.text)["response"]["groups"][0]["items"]
        data = [d["venue"] for d in data]
        return data
    except Exception as e: 
        print("Explore request failed: {0}".format(e))
        return dict([]) 

def select_venue(venues_data, *args, p = [], distribution_generator = None):
    """
    Randomly selects a single venue from provided list of venues or reads venue list from specified file. 

    Parameters:
    -----------
    venues_data (list / string): Either a list of dictionaries produced by api request, or the name of a .json
        file that stores the venue data. If a string is provided, this function will read from the file.  
    *args (optional): Optional, additional arguments that are passed into distribution_generator along with 
        venues_data.
    p (list): A list of probabilities, where each probability corresponds with a venue's chance of selection.
        Must sum to 1. 
    distribution_generator (function, optional): function that maps venue data to probability distribution. This 
        distribution is used to select the venue.
    
    Returns:
    --------
    dictionary: Information on a single venue. If this function fails, it will return None instead. 
    """
    if type(venues_data) == str: 
        venues_data = read_from_json(venues_data) 
    try:
        if len(p) > 0:
            return np.random.choice(venues_data, p = p)
        if distribution_generator != None:
            p = distribution_generator(venues_data, *args)
            return np.random.choice(venues_data, p = p)
        return np.random.choice(venues_data)
    except Exception as e:
        print("Failed to select venue:", e)
        
def latlng_distribution(venues_data, original_location, smoothing_coeff = 0.2):
    """
    Uses each venue's distance from original location to create a probability distribution. 
    Probability of selection scales inversely with distance. Optional smoothing coefficient to 
    influence how much impact distance has. 

    Parameters:
    -----------
    venues_data (list): A list of dictionaries produced by api request.
    original_location (tuple): A tuple of (lat, lon) coordinates that serves as home location. Each venue's distance 
        is calculated from this location.
    smoothing_coeff (float, optional): A number between 0 and 1 inclusive. If the coefficient is 0, the probability of 
        selecting a venue is directly related. If the coefficient is 1, the distribution is uniform. The default 
        value is 0.2.

    Returns:
    --------
    list: A probability distribution for selecting each venue. 
    """ 
    # Use of euclidean_distance approximation valid for small radii. 
    euclidean_distance = lambda coord1, coord2: np.sqrt(np.sum((np.array(coord1) - np.array(coord2)) ** 2)) 
    distances = np.array([])
    try:
        for venue in venues_data:
            venue_latlng = (venue["location"]["lat"], venue["location"]["lng"])
            distances = np.append(distances, 1 / euclidean_distance(original_location, venue_latlng))
        smoothed_distances = (1 - smoothing_coeff) * distances + smoothing_coeff * np.sum(distances)
        smoothed_distances /= np.sum(smoothed_distances)
        return smoothed_distances
    except Exception as e:
        print("Failed to create distribution:", e, "; returning uniform distribution.")
        return np.ones(len(venues_data)) / len(venues_data)

def main():
    location_data = read_from_json("location_data.json")
    write_to_json(nearby_venues(location_data, query = "library"), "venues.json")
    original_location = (location_data["latitude"], location_data["longitude"])
    p = latlng_distribution(read_from_json("venues.json"), original_location)
    write_to_json(select_venue("venues.json", p = p), "selected_venue.json")

if __name__ == "__main__":
    main()
