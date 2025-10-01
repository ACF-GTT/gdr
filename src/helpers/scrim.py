"""Traitement des fichiers SCRIM (abscisse, CFT)."""

import csv
import os
from helpers.road_mesure import SITitle, RoadMeasure

def get_generic_absdatatop_csv(
    file_name: str,
    unit: str = "CFT",
    force_sens: str | None = None
) -> RoadMeasure | None:
    """
    Ouvre un fichier SCRIM (2 colonnes séparées par ';' : abscisse, CFT).
    Retourne un RoadMeasure prêt à être tracé en schéma itinéraire.
    """
    y_datas = []
    abscisses = []
    step = None
    tops = {}

    with open(file_name, encoding="utf-8") as csvfile:
        csv_data = csv.reader(csvfile, delimiter=';')  # séparateur ;
        for i, row in enumerate(csv_data):
            if i == 0:
                # ligne d'entête ("abscisses;CFT") → on skip
                continue
            try:
                x_val = float(row[0])
                y_val = float(row[1])
                if len(row) >= 3:
                    tops[str(row[2]).lower()] = (x_val, 0.0)
            except (ValueError, IndexError):
                continue  # ignore lignes invalides

            abscisses.append(x_val)
            y_datas.append(y_val)

            # calcul du pas (différence entre les 2 premières abscisses)
            if step is None and len(abscisses) >= 2:
                step = abscisses[-1] - abscisses[-2]

    if step is None or not y_datas:
        return None

    # titre = SCRIM + nom fichier
    title = SITitle("CFT")
    title.add(os.path.basename(file_name))

    return RoadMeasure(
        step=step,
        datas=y_datas,
        tops=tops,
        unit=unit,
        title=title.title,
        force_sens=force_sens
    )
