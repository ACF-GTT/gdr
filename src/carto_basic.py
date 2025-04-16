"""Produit une carte HTML
Habillage d'un fichier de mesure GRIP
avec de la donnée en provenance de la BDTOPO
"""
import json
import branca.colormap as cm

import folium
from folium.plugins import MousePosition
from folium.plugins import MeasureControl

from const.grip import POOR, GOOD, EXCELLENT, COLORS
from helpers.shared import pick_files

file_names = pick_files(
    measure={
        "folder_path": "datas",
        "ext": "geojson",
        "message": "choix du fichier de mesure"
    }
)

geojson_name = file_names["measure"]

with open(geojson_name, encoding="utf-8") as geojson_file:

    geojson_data = json.loads(geojson_file.read())
    coordinates = geojson_data["features"][0]["geometry"]["coordinates"]
    lon_start = coordinates[0]
    lat_start = coordinates[1]
    m = folium.Map(
        location=[lat_start, lon_start],
        zoom_start=16
    )
    folium.GeoJson(
        geojson_data,
        name="CFT",
        marker=folium.CircleMarker(
            radius=3,
            stroke=None,
            fill_color="black",
            fill_opacity=1
        ),
        style_function=lambda x: {
            "fillColor": x['properties']['color']
        },
    ).add_to(m)
    folium.LayerControl().add_to(m)
    legend = cm.StepColormap(
        COLORS.values(),
        vmin=0,
        vmax=100,
        index=[0, POOR, GOOD, EXCELLENT, 100],
        caption="niveaux de CFT"
    )
    legend.add_to(m)
    MousePosition().add_to(m)
    MeasureControl().add_to(m)
    # sauvergarde de la map en HTML
    map_name = geojson_name.replace(".geojson", "_basic.html")
    m.save(map_name)
