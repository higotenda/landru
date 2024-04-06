import os
import requests
import random
import csv
import logging

logging.basicConfig(level=logging.DEBUG)
API_KEY = "fsq3aF6dxwEZGpyjST6Nh7cY/loYxiaOxCFDPSxfNVJ15Ew="


def get_coordinates(place):
    lat = place["geocodes"]["main"]["latitude"]
    lng = place["geocodes"]["main"]["longitude"]
    return lat, lng


def get_nearby_places(api_key, ll, radius=1500, place_type="restaurant"):
    url = "https://api.foursquare.com/v3/places/search"
    llstr = str(ll[0]) + "," + str(ll[1])
    params = {
        "query": place_type,
        "ll": llstr,
        "radius": radius,
        "client_id": api_key,  # Use API key as client_id
    }
    logging.debug(f"params: {params}")
    headers = {"Accept": "application/json", "Authorization": api_key}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the API: {e}")
        return

    if "results" in data and data["results"]:
        nearby_places = data["results"]
        return nearby_places
    else:
        return []


# def get_location_from_user():
#     while True:
#         user_location = input("Enter the coordinates (latitude,longitude) of the crowded place: ")
#         if ',' in user_location and len(user_location.split(',')) == 2:
#             return user_location
#         else:
#             print("Invalid input format. Please enter the coordinates in the format 'latitude,longitude'.")


def save_to_csv(crowded_place_coords, nearby_places_coords, csvfile):
    writer = csv.writer(csvfile)
    crowded_place_lat, crowded_place_lng = crowded_place_coords
    writer.writerow(["in", crowded_place_lat, crowded_place_lng])

    for coords in nearby_places_coords:
        lat, lng = coords
        writer.writerow(["out", lat, lng])

    writer.writerow([])


def gen_csv(ll, fp, place_type="cafe"):
    csvfile = open(fp, "w")
    nearby_places = get_nearby_places(API_KEY, ll, place_type=place_type)
    if nearby_places:
        crowded_place_coords = get_coordinates(nearby_places[0])
        nearby_places_coords = [get_coordinates(place) for place in nearby_places[1:]]

        save_to_csv(crowded_place_coords, nearby_places_coords, csvfile)
        print(f"Generated In-Out CSV.")
    else:
        print(f"No {place_type}s found nearby.")


if __name__ == "__main__":
    gen_csv((13.0064, 77.5694), "./raw_demands.csv")
