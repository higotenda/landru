import os
import requests
import random
import csv

API_KEY = "fsq3aF6dxwEZGpyjST6Nh7cY/loYxiaOxCFDPSxfNVJ15Ew=";

def get_coordinates(place):
    lat = place['geocodes']['main']['latitude']
    lng = place['geocodes']['main']['longitude']
    return lat, lng

def get_nearby_places(api_key, location, radius=1500, place_type="restaurant"):
    url = "https://api.foursquare.com/v3/places/search"
    params = {
        "query": place_type,
        "ll": location,
        "radius": radius,
        "client_id": api_key  # Use API key as client_id
    }
    headers = {
        "Accept": "application/json",
        "Authorization": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from the API: {e}"

    if 'results' in data and data['results']:
        nearby_places = data['results']
        return nearby_places
    else:
        return []

def get_location_from_user():
    while True:
        user_location = input("Enter the coordinates (latitude,longitude) of the crowded place: ")
        if ',' in user_location and len(user_location.split(',')) == 2:
            return user_location
        else:
            print("Invalid input format. Please enter the coordinates in the format 'latitude,longitude'.")

def save_to_csv(crowded_place_coords, nearby_places_coords):
    with open(r"C:\Users\Admin\AppData\Local\Programs\Python\Python311\inout.csv", 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        crowded_place_lat, crowded_place_lng = crowded_place_coords
        writer.writerow(['in', crowded_place_lat, crowded_place_lng])
       
        for coords in nearby_places_coords:
            lat, lng = coords
            writer.writerow(['out', lat, lng])
         
        writer.writerow([])

def main():
    if not API_KEY:
        print("Error: Foursquare API key not found. Please set the FOURSQUARE_API_KEY environment variable.")
        return

    user_location = get_location_from_user()
    place_type = input("Enter the type of place to search for (e.g., 'restaurant', 'cafe'): ").strip().lower()

    nearby_places = get_nearby_places(API_KEY, user_location, place_type=place_type)

    if isinstance(nearby_places, str):
        print(nearby_places)
        return

    if nearby_places:
        crowded_place_coords = get_coordinates(nearby_places[0])
        nearby_places_coords = [get_coordinates(place) for place in nearby_places[1:]]
     
        save_to_csv(crowded_place_coords, nearby_places_coords)


        print(f"The coordinates of the crowded place and nearby places have been saved to Csv FIle")
    else:
        print(f"No {place_type}s found nearby.")

if __name__ == "__main__":
    main()
