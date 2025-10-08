"""Traitement des fichiers apl"""
import csv
from helpers.road_mesure import RoadMeasure

# Lecture du fichier APL avec différents encodages possibles car il y avait un pb avec utf-8
ENCODINGS = ["utf-8", "windows-1250", "windows-1252"]

def get_apl_datas(file_name:str,force_sens: str|None = None) -> RoadMeasure|None: # pylint: disable=too-many-locals
    """ouvre un fichier de mesure.SBO"""
    unit_column = {
        "PO": {"Gauche": 1, "Droite": 2},
        "MO": {"Gauche": 3, "Droite": 4},
        "GO": {"Gauche": 5, "Droite": 6},
    }

    # chaque unité a deux colonnes : gauche et droite
    datas = {u: {"Gauche": [], "Droite": []} for u in unit_column}
    abscisses = []

    # Lecture du fichier avec ≠ encodages possibles
    for encoding in ENCODINGS:
        try:
            with open(file_name, encoding=encoding, newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=";")
                next(reader, None)  # on passe les en-têtes
                # Lecture des données, si une ligne est mal formée, on l'ignore
                for row in reader:
                    if len(row) == 0:
                        continue
                    # Extraction de l'abscisse
                    try:
                        abscisse = float(row[0])
                    except (ValueError, IndexError):
                        continue  # on ignore la ligne si pas de valeur valide en abscisse

                    abscisses.append(abscisse)

                    # Extraction des valeurs pour chaque unité et chaque sens
                    for onde, sens in unit_column.items():
                        for direction, column_index in sens.items():
                            # On Vérifie que la colonne à lire existe bien dans la ligne actuelle
                            if column_index >= len(row):
                                continue
                            val_str = row[column_index].strip() # indice de la colonne
                            if val_str:
                                try:
                                    val = float(val_str) #conversion en float
                                except ValueError:
                                    val = None
                                if val is not None:
                                    datas[onde][direction].append(val)
            break  # si encodage OK, on sort
        except UnicodeDecodeError:
            continue

    if not abscisses:
        return None

    step = abscisses[1] - abscisses[0] if len(abscisses) > 1 else 1.0

    return RoadMeasure(
        step=step,
        datas=datas,
        tops={},
        unit="APL",
        title="APL",
        force_sens=force_sens
    )
