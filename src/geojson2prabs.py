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
    _date = datas["date"]
    tab_pr = []
    features = datas["features"]
    longueur = max(el["properties"]["abs"] for el in features)
    _STEP = abs(
        features[1]["properties"]["abs"] - features[0]["properties"]["abs"]
    )
    print(f"on a mesuré {longueur} mètres au pas de {_STEP} mètre(s)")
    for feature in features:
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
    # est-on dans le sens des pr croissants ?
    SENS = "D" if tab_pr[1]["pr"] - tab_pr[0]["pr"] > 0 else "G"
    if SENS == "G":
        tab_pr.reverse()
        for _pr in tab_pr:
            _pr["abs"] = longueur - _pr["abs"]
    print(tab_pr)
    # on est forcément dans le sens des abscisses curvilignes croissantes
    # si on n'est pas dans le sens des pr croissants, on renverse les abscisses curvilignes
    if SENS == "G":
        for feature in features:
            abs_original = feature["properties"]["abs"]
            feature["properties"]["abs"] = longueur - abs_original
        features = reversed(list(features))
    INDEX = 0
    NB_PR = len(tab_pr)
    _CFT = None
    _PRD = None
    _ABD = None
    print(f"{NB_PR} points repères sont présents")
    input("appuyer sur une touche pour créer le fichier csv en PR + abscisse")
    csv_name = file_name.replace(".geojson", "_prabs.csv")
    with open(csv_name, 'w', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(["CFT", "PRD", "ABD", "PRF", "ABF", "SENS", "DATE"])
        for feature in features:
            prop = feature["properties"]
            if INDEX < NB_PR - 1 and prop["abs"] >= tab_pr[INDEX+1]["abs"]:
                INDEX += 1
            _prf = tab_pr[INDEX]["pr"]
            _abf = prop["abs"] - tab_pr[INDEX]["abs"]
            if None not in (_CFT, _PRD, _ABD):
                writer.writerow([_CFT, _PRD, _ABD, _prf, _abf, SENS, _date])
            _CFT = prop["CFT"]
            _PRD = _prf
            _ABD = _abf
        _prf = _PRD
        _abf = _ABD + _STEP
        writer.writerow([_CFT, _PRD, _ABD, _prf, _abf, SENS, _date])
