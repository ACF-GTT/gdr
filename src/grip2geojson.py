"""geocodage des fichiers grip MK2 au format geojson.
latitude : colonne 7
longitude : colonne 8
altitude : colonne 9
"""
import csv
import json
import os
import re
from typing import Any

from helpers.consts import BALISE_HEADER, BALISE_RESULTS, correle, define_color
from helpers.road_mesure import DATE_REGEXP
from helpers.shared import pick_file

def create_point(x_val, y_val, **kwargs):
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
            el_name: y_val,
            "abs": x_val
        }
    }
    if el_color is not None:
        el_feature["properties"]["color"] = el_color
    el_feature["properties"]["pr"] = -1
    return el_feature

geojson_collection: dict[str, Any] = {
    "type":"FeatureCollection",
    "features": list
}
geojson_collection["features"] = []

file_name = pick_file(f"{os.path.dirname(__file__)}/datas")

with open(file_name, encoding="utf-8") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    INDEX_START = None
    INDEX_HEADER = None
    for i,row in enumerate(spamreader):
        if row[0].strip() == BALISE_HEADER:
            INDEX_HEADER = i
        if row[0].strip() == BALISE_RESULTS:
            INDEX_START = i
        if INDEX_HEADER is not None:
            if i == INDEX_HEADER + 2:
                pattern_found = re.search(
                    DATE_REGEXP,
                    "".join(row)
                )
                if pattern_found:
                    geojson_collection["date"] = pattern_found[0]
        if INDEX_START and i > INDEX_START + 1:
            x = float(row[0])
            y = correle(float(row[1]))
            lat = float(row[7])
            lon = float(row[8])
            alt = float(row[9])
            feature = create_point(
                x,
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
