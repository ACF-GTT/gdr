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
import argparse
import csv
import json
import os
from helpers.shared import pick_file

file_name = pick_file(
    f"{os.path.dirname(__file__)}/datas",
    ext="geojson"
)

class Geojson2PrAbs:
    """transcodage d'un geojson en PR + abscisse."""
    def __init__(self, name):
        """Initialisation."""
        with open(name, encoding="utf-8") as geojsonfile:
            datas = json.load(geojsonfile)
            self.date = datas["date"]
            self.tab_pr = []
            self.features = datas["features"]
            self.longueur = max(
                el["properties"]["abs"] for el in self.features
            )
            # Les abscisses curvilignes sont forcément croissantes
            self.step = self._abs(1) - self._abs(0)
            print(f"On a mesuré {self.longueur} mètres")
            print(f"Le pas est de {self.step} mètre(s)")
            for feature in self.features:
                prop = feature["properties"]
                if prop["pr"] != -1:
                    self.tab_pr.append({
                        "pr": prop["pr"],
                        "abs": prop["abs"],
                        "CFT": prop["CFT"]
                    })
            self.sens = "D" if self._pr(1) - self._pr(0) > 0 else "G"
            if self.sens == "G":
                self.reverse()
            print(self.tab_pr)

    def _abs(self, i):
        """retourne l'abscisse curviligne à la position i.""" 
        return self.features[i]["properties"]["abs"]

    def _pr(self, i):
        """Retourne le numéro du PR en position i."""
        return self.tab_pr[i]["pr"]

    def _prabs(self, i):
        """retourne l'abscisse du PR en position i"""
        return self.tab_pr[i]["abs"]

    def reverse(self):
        """renverse les abscisses curvilignes."""
        self.tab_pr.reverse()
        for pr in self.tab_pr:
            pr["abs"] = self.longueur - pr["abs"]
        for feature in self.features:
            abs_original = feature["properties"]["abs"]
            feature["properties"]["abs"] = self.longueur - abs_original
        self.features = reversed(list(self.features))

    def complete(self, line: list, route: str=None):
        """Ajoute les paramètres complémentaires"""
        line.append(self.date)
        line.append(self.sens)
        if route is not None:
            line.insert(0, route)
        return line

    def convert2prd_abd_prf_abf(self, route=None):
        """Produit des tronçons avec les champs prd, abd, prf, abf."""
        nb_pr = len(self.tab_pr)
        print(f"{nb_pr} points repères")
        index = 0
        datas = []
        cft = None
        prd = None
        abd = None
        for feature in self.features:
            prop = feature["properties"]
            if index < nb_pr - 1 and prop["abs"] >= self._prabs(index+1):
                index += 1
            prf = self._pr(index)
            abf = prop["abs"] - self._prabs(index)
            if self.sens == "D" and prd is None:
                prd = prf
                abd = abf - self.step
            if self.sens == "D":
                cft = prop["CFT"]
            if None not in (cft, prd, abd):
                line = [prd, abd, prf, abf, cft]
                datas.append(
                    self.complete(line, route=route)
                )
            if self.sens == "G":
                cft = prop["CFT"]
            prd = prf
            abd = abf
        if self.sens == "G":
            prf = prd
            abf = abd + self.step
            line = [prd, abd, prf, abf, cft]
            datas.append(
                self.complete(line, route=route)
            )
        return datas

parser = argparse.ArgumentParser(description='transcodage en PR+ABS')
parser.add_argument(
    "--nom_csv",
    action="store",
    help="nom du csv à utiliser",
    default=None
)
parser.add_argument(
    "--route",
    action="store",
    help="nom de la route",
    default=None
)
args = parser.parse_args()

transcoder = Geojson2PrAbs(file_name)
datas_in_prabs = transcoder.convert2prd_abd_prf_abf(route=args.route)

MODE = "w"
if args.nom_csv is not None:
    if args.nom_csv[-3:] != ".csv":
        args.nom_csv = f"{args.nom_csv}.csv"
    CSV_NAME = f"{os.path.dirname(__file__)}/{args.nom_csv}"
    if os.path.isfile(CSV_NAME):
        MODE = "a"
else:
    CSV_NAME = file_name.replace(".geojson", "_prabs.csv")

WRITE = True
if MODE == "a":
    with open(CSV_NAME, encoding="utf-8") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        for j,row in enumerate(csv_data):
            EXIST = True
            for j, el in enumerate(datas_in_prabs[0]):
                if str(el) != row[j]:
                    EXIST = False
                    break
            if EXIST:
                WRITE = False
                break
if not WRITE:
    print("écriture dans le csv annulée pour cause de doublon")
else:
    with open(CSV_NAME, MODE, encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        if MODE == "w":
            entete = ["PRD", "ABD", "PRF", "ABF", "CFT", "DATE", "SENS"]
            if args.route is not None:
                entete.insert(0, "ROUTE")
            writer.writerow(entete)
        writer.writerows(datas_in_prabs)
