"""
Gets current location of device using ipdata.  
Source: ipdata.co 
""" 

import config 
from ipdata import ipdata
import requests
import json

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

def main():
    location_data = get_location_data()
    write_to_json(location_data, "location_data.json")

if __name__ == "__main__":
    main()
