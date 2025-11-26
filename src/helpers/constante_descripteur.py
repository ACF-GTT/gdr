
"""Constantes décrivant les couches, colonnes, types et niveaux des descripteurs
d'état de surface extraits depuis le fichier GPKG ou XLSX.
"""
# pylint: disable=consider-using-from-import
from typing import Any, Literal
import matplotlib.cm as cm
from helpers.tools_file import parent_dir

DATAS = f"{parent_dir(__file__, 2)}/datas/"

# Nom du fichier source (GPKG)
FILE_DESCRIPTEURS = f"{DATAS}/2024_IQRN_descripteurs_DIRMC.gpkg"
FILE_SURFACE = f"{DATAS}/Table_Indicateurs_Etat_surface_DIRMC.xlsx"


# Définition des descripteurs et de leurs caractéristiques
FieldTypes = Literal["layer", "column", "gravite_type", "gravites"]
DescTypes = Literal[
    "DELAMINATION",
    "DENSITE_FISSURATION",
    "MACROTEXTURE",
    "EPO", "EMO",
    "ESTEX",
    "RAVELING",
    "ORNIERAGE_GRAND_RAYON", "ORNIERAGE_PETIT_RAYON"
]

DESCRIPTEURS: dict[DescTypes, dict[FieldTypes, Any]] = {
    "DELAMINATION": {
        "layer": "Descr_final_Delamination_2024 — DIRMC",
        "column": None,               # Pas de gravité = présent/absent
        "gravite_type": "bool",
        "gravites": []
    },

    "DENSITE_FISSURATION": {
        "layer": "Descr_gravite_Densite_Fissuration_2024 — DIRMC",
        "column": "niveau_gravite",
        "gravite_type": "int",
        "gravites": [1, 2, 3, 4]
    },

    "MACROTEXTURE": {
        "layer": "Descr_final_Macrotexture_Fermee_2024 — DIRMC",
        "column": None,
        "gravite_type": "bool",
        "gravites": []
    },

    "EPO": {
        "layer": "Descr_gravite_EPO_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            ">=0.25cm3", ">=0.50cm3", ">=1cm3", ">=4cm3"
        ]
    },

    "EMO": {
        "layer": "Descr_gravite_EMO_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            ">=2.5cm3", ">=5.0cm3", ">=7.5cm3", ">=10cm3", ">=20cm3", ">=25cm3", ">=40cm3"
        ]
    },

    "ESTEX": {
        "layer": "Descr_gravite_eSTex_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            ">=0.025cm3", ">=0.050cm3", ">=0.1cm3", ">=0.25cm3"
        ]
    },

    "RAVELING": {
        "layer": "Descr_gravite_Raveling_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            "080 cm3/m2", "120 cm3/m2", "150 cm3/m", "250 cm3/m2", "500cm3/m2", "750cm3/m2"
        ]
    },

    "ORNIERAGE_GRAND_RAYON": {
        "layer": "Descr_gravite_Orniere_Grand_Rayon_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            ">=7mm", ">=10mm", ">=15mm", ">=20mm", ">=25mm", ">=30mm", ">=50mm"
        ]
    },

    "ORNIERAGE_PETIT_RAYON": {
        "layer": "Descr_gravite_Orniere_Petit_Rayon_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            ">=7mm", ">=10mm", ">=15mm", ">=20mm"
        ]
    },
}


#Extraction PRD ROUTE DEP SENS ABD

CLE_TRONCON_REGEX = (
    r"^(?P<route>[A-Z]\d+?)_"
    r"(?P<cote>[A-Z])_"
    r"(?P<sens>[A-Z])_"
    r"(?:[A-Za-z]*?)"       # ignorer toutes lettres avant le dep (cas DF)
    r"(?P<dep>[0-9]{2})"    # capturer les 2 chiffres de dep
    r"(?P<pr>PR[0-9]+)"     # capturer PR + chiffres
    r"(?P<suffixe>[A-Z]?)_"
    r"(?P<abd>[0-9]+)$"
)



# === Colonnes extraites ===
ROUTE   = "ROUTE"
SENS    = "SENS"
DEP     = "DEP"
PRD     = "PRD"
ABD     = "ABD"
CLE_TRONCON_PLOD = "cle_troncon_plod"




def generate_palette(n):
    """
    Génère une palette de n couleurs allant du vert (bon) au violet (pire).
    """
    base_colors = ["green", "#b8dfaf", "orange", "red", "purple"]

    if n <= len(base_colors):
        # Prendre simplement les n premières couleurs
        return base_colors[:n]

    # Générer un gradient entre les 5 couleurs existantes
    cmap = cm.get_cmap("turbo", n)   # ajout de turbo pour faire un gradient multicolore
    return [cmap(i) for i in range(n)]
