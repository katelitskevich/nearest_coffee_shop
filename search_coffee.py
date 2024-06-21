import os
import requests
import json
import folium
from geopy import distance
from flask import Flask


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return [lon, lat]


def get_distance_to_coffees(coffee, coords):
    finally_list = []
    for coffee_obj in coffee:
        latitude = coffee_obj["geoData"]["coordinates"][0]
        longitude = coffee_obj["geoData"]["coordinates"][1]

        one_caffe = {
            "title": coffee_obj["Name"],
            "latitude": latitude,
            "longitude": longitude,
            "distance": distance.distance(coords, (latitude, longitude)).km,
        }
        finally_list.append(one_caffe)
    return finally_list


def get_distance(coffee):
    return coffee["distance"]


def creat_map(coords, min_distance_coffee_list):
    m = folium.Map(location=[coords[1], coords[0]])

    for one_coffee in min_distance_coffee_list:
        folium.Marker(
            location=[one_coffee["longitude"], one_coffee["latitude"]],
            tooltip="Click me!",
            popup=one_coffee["title"],
            icon=folium.Icon(icon="cloud"),
        ).add_to(m)
    m.save("index.html")


def coffee_map():
    with open("index.html") as file:
        return file.read()


def prepare_map():
    address = input("Где вы находитесь?")
    coords = fetch_coordinates(os.environ["API_KEY"], address)

    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()

    raw_coffee_list = json.loads(file_contents)
    coffee_list_with_distance = get_distance_to_coffees(raw_coffee_list, coords)
    min_distance_coffee_list = sorted(coffee_list_with_distance, key=get_distance)[:5]
    creat_map(coords, min_distance_coffee_list)


if __name__ == "__main__":
    prepare_map()
    app = Flask(__name__)
    app.add_url_rule("/", "map", coffee_map)
    app.run("0.0.0.0")
