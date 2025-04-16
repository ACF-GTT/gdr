"""Convert a geojson from lambert93 to WGS84."""
import json

from pyproj import Transformer

from src.const.main import BPTOPO_GEOJSON
from src.helpers.shared import pick_file

# transformation EPSG:2154 (Lambert 93) vers EPSG:4326 (WGS 84)
transformer = Transformer.from_crs(
    crs_from = "EPSG:2154",
    crs_to = "EPSG:4326",
    always_xy=True
)

geojson_name = pick_file(
    folder_path=BPTOPO_GEOJSON,
    ext="geojson"
)

with open(
    geojson_name,
    encoding="utf-8"
) as geojson_file:
    geojson_data = json.loads(geojson_file.read())
    for feature in geojson_data["features"]:
        if feature["geometry"]["type"] == "Point":
            x, y = feature["geometry"]["coordinates"]
            lon, lat = transformer.transform(x, y)
            feature["geometry"]["coordinates"] = [
                lon,
                lat
            ]
        if feature["geometry"]["type"] == "Polygon":
            polygon = []
            for sf in feature["geometry"]["coordinates"][0]:
                lon, lat = transformer.transform(sf[0], sf[1])
                polygon.append( [lon, lat] )
            feature["geometry"]["coordinates"] = [polygon]
        if feature["geometry"]["type"] == "LineString":
            polygon = []
            for sf in feature["geometry"]["coordinates"]:
                lon, lat = transformer.transform(sf[0], sf[1])
                polygon.append( [lon, lat] )
            feature["geometry"]["coordinates"] = polygon


geojson_name_wgs84 = geojson_name.replace(
    ".geojson",
    "_WGS84.geojson"
)

with open(
    geojson_name_wgs84,
    encoding="utf-8",
    mode="w"
) as geojson_file_wgs84:
    geojson_file_wgs84.write(
        json.dumps(
            geojson_data,
            indent=None
        )
    )
