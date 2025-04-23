"""Conversion geojson vers csv PR + abscisse.
l'objet properties de chaque feature du geojson doit contenir les champs :
- abs pour l'abscisse curviligne
- pr qui vaut -1 si le point n'est pas un PR
{
  "type": "Feature", 
  "properties": {
    "CFT": 56.0755,
    "abs": 10.0,
    "color": "#ee7a0e",
    "pr": -1 
  }, 
  "geometry": {
    "type": "Point",
    "coordinates": [ 3.798883, 45.0994, 751.25 ] 
  }
}
il faut au moins 2 PR
"""
import csv
import json
import os
from helpers.shared import pick_file

file_name = pick_file(
    f"{os.path.dirname(__file__)}/datas",
    ext="geojson"
)

with open(file_name, encoding="utf-8") as geojsonfile:
    datas = json.load(geojsonfile)
    tab_pr = []
    longueur = max(el["properties"]["abs"] for el in datas["features"])
    print(f"on a mesuré {longueur} mètres")
    for feature in datas["features"]:
        prop = feature["properties"]
        coord = feature["geometry"]["coordinates"]
        if prop["pr"] != -1:
            tab_pr.append({
                "pr": prop["pr"],
                "abs": prop["abs"],
                "CFT": prop["CFT"],
                "lon": coord[0],
                "lat": coord[1]
            })
    print(tab_pr)
    # est-on dans le sens des pr croissants ?
    SENS = "D" if tab_pr[1]["pr"] - tab_pr[0]["pr"] > 0 else "G"
    # on est forcément dans le sens des abscisses curvilignes croissantes
    # si on n'est pas dans le sens des pr croissants, on renverse les abscisses curvilignes
    if SENS == "G":
        for data in datas["features"]:
            abs_original = data["properties"]["abs"]
            data["properties"]["abs"] = longueur - abs_original
        datas["features"] = reversed(list(datas["features"]))
    INDEX = 0
    NB_PR = len(tab_pr)
    print(f"{NB_PR} points repères sont présents")
    input("appuyer sur une touche pour créer le fichier csv en PR + abscisse")
    csv_name = file_name.replace(".geojson", "_prabs.csv")
    with open(csv_name, 'w', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(["CFT", "PR", "ABS", "SENS", "COULEUR"])
        for data in datas["features"]:
            prop = data["properties"]
            if INDEX < NB_PR - 1 and prop["abs"] >= tab_pr[INDEX+1]["abs"]:
                INDEX += 1
            _cft = prop["CFT"]
            _color = prop["color"]
            _pr = tab_pr[INDEX]["pr"]
            _abs = prop["abs"] - tab_pr[INDEX]["abs"]
            writer.writerow([_cft, _pr, _abs, SENS, _color])
