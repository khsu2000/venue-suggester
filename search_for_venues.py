"""
Uses Foursquare's Places API to search for nearby venues given location data and other parameters. 
""" 

import config
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
    dictionary: List of venues and info from GET request. Upon failure, returns empty dictionary.
    """
    try:
        url = "https://api.foursquare.com/v2/venues/search"
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
        data = json.loads(resp.text) 
        return data
    except Exception as e: 
        print("Explore request failed: {0}".format(e))
        return dict([]) 

def main():
    location_data = read_from_json("location_data.json")
    data = nearby_venues(location_data, query = "library")
    write_to_json(data, "venues.json")

if __name__ == "__main__":
    main()
