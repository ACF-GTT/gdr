"""Traitement de fichiers csv reflétant le niveau de gravité des descripteurs
première ligne avec des entêtes
colonne 0 : id
colonne 1 : id_ref
colonne 2 : niveau de gravité (0 à 4)
colonne 3 : PR (point kilométrique)
colonne 4 : distance (en m par rapport au PR)
"""

import csv
import os
from helpers.road_mesure import SITitle, RoadMeasure

def get_etat_gravite_descripteur(
    file_name: str,
    force_sens: str | None = None,
    unit: str = "GRAV"
) -> RoadMeasure | None:
    """
    Ouvre un fichier de niveau de gravité des descripteurs.
    Calcule un PR+abscisse = PR + distance arrondie.
    Retourne un RoadMeasure prêt à être tracé.
    """
    y_datas = []
    abscisses = []
    step = None
    tops = {}

    with open(file_name, encoding="utf-8") as csvfile:
        csv_data = csv.reader(csvfile, delimiter=';')
        for i, row in enumerate(csv_data):
            if i == 0:
                continue  # ignore ligne d'entête
            try:
                pr = int(row[3]) if row[3].strip() != "" else 0
                dist = round(float(row[4])) if row[4].strip() != "" else 0
                y_val = int(row[2])  # gravité entière (0 à 4)
                x_val = pr + dist  # PR exprimé en kilomètres
                pr_label = f"PR{pr}+{dist}"
                tops[pr_label.lower()] = (x_val, y_val)
                print(f"x_val: {x_val}, y_val: {y_val}")

            except (ValueError, IndexError):
                continue

            abscisses.append(x_val)
            y_datas.append(y_val)

            if step is None and len(abscisses) >= 2:
                step = abscisses[-1] - abscisses[-2]

    if step is None or not y_datas:
        return None

    title = SITitle(unit)
    title.add(os.path.basename(file_name))

    return RoadMeasure(
        step=step,
        datas=y_datas,
        tops=tops,
        unit=unit,
        title=title.title,
        force_sens=force_sens
    )
