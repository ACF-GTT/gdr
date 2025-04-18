"""geocodage des fichiers grip MK2 au format geojson.
latitude : colonne 7
longitude : colonne 8
altitude : colonne 9
"""
import csv
import json
import os

from const.grip import BALISE_RESULTS, correle, define_color
from helpers.shared import pick_file

def create_point(value, **kwargs):
    """coordinates should be an array 
    The first two elements are longitude and latitude,
    precisely in that order and using decimal numbers.
    Altitude  MAY be included as an optional third element
    cf https://datatracker.ietf.org/doc/html/rfc7946
    """
    el_lon = kwargs.get("lon")
    el_lat = kwargs.get("lat")
    el_alt = kwargs.get("alt")
    el_name = kwargs.get("name", "CFT")
    el_color = kwargs.get("color", None)
    el_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [el_lon, el_lat, el_alt]
        },
        "properties": {
            el_name: value
        }
    }
    if el_color is not None:
        el_feature["properties"]["color"] = el_color
    return el_feature

geojson_collection = {
    "type":"FeatureCollection",
    "features": []
}

file_name = pick_file(f"{os.path.dirname(__file__)}/datas")

with open(file_name, encoding="utf-8") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    INDEX_START = None
    for i,row in enumerate(spamreader):
        if row[0].strip() == BALISE_RESULTS:
            INDEX_START = i
        if INDEX_START and i > INDEX_START + 1:
            x = float(row[0])
            y = correle(float(row[1]))
            lat = float(row[7])
            lon = float(row[8])
            alt = float(row[9])
            feature = create_point(
                y,
                lat=lat,
                lon=lon,
                alt=alt,
                color=define_color(y)
            )
            geojson_collection["features"].append(feature)

geojson_name = file_name.replace(" ", "_")
geojson_name = file_name.replace(".csv", ".geojson")
with open(geojson_name, encoding="utf-8", mode="w") as geojsonfile:
    geojsonfile.write(
        json.dumps(
            geojson_collection,
            indent=None
        )
    )
