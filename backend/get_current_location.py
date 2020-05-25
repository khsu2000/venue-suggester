"""
Gets current location of device using ipdata.
Source: ipdata.co
"""

import config
from ipdata import ipdata
import requests

def get_location_data():
    """
    Gets location data using current IP address from ipdata.

    Parameters:
    -----------
    None

    Returns:
    --------
    dictionary: A dictionary of location data from the ipinfo request. Keys include
        'city', 'country_name', 'latitude', 'longitude', 'postal', 'region', 'timezone', and 'timestamp'.
        Any entry that was not included is replaced with an empty string.
    """
    try:
        public_ip = requests.get("http://ip.42.pl/raw").text
        ipd = ipdata.IPData(config.ipdata_api_key)
        response = ipd.lookup(public_ip)
        keys = ["city", "country_name", "latitude", "longitude", "postal", "region"]
        location_data = {}
        for key in keys:
            location_data[key] = response.get(key, "")
        location_data["time zone"] = response["time_zone"]["name"]
        location_data["timestamp"] = response["time_zone"]["current_time"]
        return location_data
    except Exception as e:
        print("Failed to get location:", e)
        return {}

if __name__ == "__main__":
    main()
