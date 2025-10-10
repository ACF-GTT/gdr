"""Traitement des fichiers apl"""
import csv
from helpers.road_mesure import RoadMeasure

# Lecture du fichier APL avec différents encodages possibles car il y avait un pb avec utf-8
ENCODINGS = ["utf-8", "windows-1250", "windows-1252"]
GAUCHE = "Gauche"
DROITE = "Droite"
# indices des colonnes dans le fichier SBO de l'apl
COLUMN_INDEXES = {
    "PO": {GAUCHE: 1, DROITE: 2},
    "MO": {GAUCHE: 3, DROITE: 4},
    "GO": {GAUCHE: 5, DROITE: 6},
}

# pylint: disable=too-many-locals
def get_po_mo_go_datas(
    file_name:str,
    force_sens: str | None = None
) -> dict[str, dict[str, RoadMeasure]] | None:
    """ouvre un fichier de mesure SBO"""
    # l'APL a deux remorques
    # > 2 colones : gauche et droite par type d'onde
    datas: dict[str, dict[str, list[float]]] = {
        onde: {
            GAUCHE: [],
            DROITE: []
        }
        for onde in COLUMN_INDEXES
    }
    abscisses = []

    # Lecture du fichier avec ≠ encodages possibles
    for encoding in ENCODINGS:
        try:
            with open(file_name, encoding=encoding, newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=";")
                next(reader, None)  # on passe les en-têtes
                # Lecture des données, si ligne mal formée, on l'ignore
                for row in reader:
                    if len(row) == 0:
                        continue
                    # Extraction de l'abscisse
                    try:
                        abscisses.append(float(row[0]))
                    except (ValueError, IndexError):
                        continue

                    # Extraction des valeurs pour chaque onde et sens
                    for onde, value in COLUMN_INDEXES.items():
                        for direction, column_index in value.items():
                            if column_index >= len(row):
                                continue
                            val_str = row[column_index].strip()
                            if val_str:
                                try:
                                    val = float(val_str)
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
    steps = {
        "PO": step,
        "MO": 4 * step,
        "GO": 16 * step
    }
    return {
        onde: {
            direction: RoadMeasure(
                step=steps[onde] ,
                datas=datas[onde][direction],
                tops={},
                unit="APL",
                title=f"APL_{onde}",
                force_sens=force_sens,
            )
            for direction in directions
        }
        for onde, directions in COLUMN_INDEXES.items()
    }
