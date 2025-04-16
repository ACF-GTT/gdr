"""Convertion de shape en geojson"""
from pathlib import Path
import geopandas

from src.const.main import BPTOPO_GEOJSON
from src.helpers.shared import pick_file

SHAPE_DIR = "BDTOPO_3-4_TOUSTHEMES_SHP_LAMB93_D043_2024-12-15"

shape_path = pick_file(
    folder_path = SHAPE_DIR,
    ext = "shp"
)

shape_file = geopandas.read_file(shape_path)

geojson_name = shape_path.split("\\")[-1]
geojson_name = geojson_name.replace(".shp", ".geojson")

Path(BPTOPO_GEOJSON).mkdir(parents=True, exist_ok=True)

shape_file.to_file(
    f"{BPTOPO_GEOJSON}/{geojson_name}",
    driver='GeoJSON'
)
