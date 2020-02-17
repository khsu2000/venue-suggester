"""
Uses Foursquare's Places API to search for nearby venues given location data and other parameters.
"""

from pprint import pprint
import config
import numpy as np
import json
import requests
from utils import write_to_json, read_from_json, Venue, venues_to_dicts, dicts_to_venues

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
    list: List of Venue objects with data from GET request. Upon failure, returns empty list.
    """
    print("making api query")
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
        resp_loaded = json.loads(resp.text)
        if resp_loaded["meta"]["code"] == 429:
            return "API Usage Exceeded"
        data = dicts_to_venues(resp_loaded["response"]["groups"][0]["items"])
        return data
    except Exception as e:
        print("Explore request failed: {0}".format(e))
        return []

def latlng_distribution(venues_data, original_location, smoothing_coeff = 0.25):
    """
    Uses each venue's distance from original location to create a probability distribution.
    Probability of selection scales inversely with distance. Optional smoothing coefficient to
    influence how much impact distance has.

    Parameters:
    -----------
    venues_data (list): A list of dictionaries produced by api request.
    original_location (tuple): A tuple of (lat, lng) coordinates that serves as home location. Each venue's distance
        is calculated with respect to this location.
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
            distances = np.append(distances, 1 / euclidean_distance(original_location, venue.get_latlng()))
        smoothed_distances = (1 - smoothing_coeff) * distances + smoothing_coeff * np.sum(distances)
        smoothed_distances /= np.sum(smoothed_distances)
        return smoothed_distances
    except Exception as e:
        print("Failed to create distribution:", e, "; returning uniform distribution.")
        return np.ones(len(venues_data)) / len(venues_data)

def distance_weighted_order(venues_data, original_location, smoothing_coeff = 0.25):
    """
    Given a list of venues, reorders the randomly list using the latlng_distribution function as
    an initial seed.

    Parameters:
    -----------
    venues_data (list): A list of dictionaries produced by api request.
    original_location (tuple): A tuple of (lat, lng) coordinates that serves as home location. Each venue's distance
        is calculated with respect to this location.
    smoothing_coeff (float, optional): A number between 0 and 1 inclusive. If the coefficient is 0, the probability of
        selecting a venue is directly related. If the coefficient is 1, the distribution is uniform. The default
        value is 0.25.

    Returns:
    --------
    list: A reordered list of dictionaries corresponding to venue data.
    """
    p = latlng_distribution(venues_data, original_location, smoothing_coeff)
    if len(set(p)) == 1:
        venues_data = venues_data.copy()
        return np.random.shuffle(venues_data)
    d = dict(zip(venues_data, p))
    reordered = []
    while len(reordered) < len(venues_data):
        venue = np.random.choice(list(d.keys()), p = list(d.values()))
        reordered.append(venue)
        last_weight = d.pop(venue)
        d = dict(zip(d.keys(), np.array(list(d.values())) / (1 - last_weight)))
    return reordered

def main():
    location_data = read_from_json("location_data.json")
    venues_list = nearby_venues(location_data, query = "can't possibly be valid")
    original_location = (location_data["latitude"], location_data["longitude"])
    write_to_json(venues_to_dicts(venues_list), "venues.json")
    write_to_json(venues_to_dicts(distance_weighted_order(venues_list, original_location)), "reordered_venues.json")

if __name__ == "__main__":
    main()
