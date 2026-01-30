# pylint: disable=duplicate-code
"""Constantes décrivant les couches, colonnes, types et niveaux des descripteurs
extraits depuis le fichier GPKG ou XLSX.
"""
from typing import Any, Dict, List, Literal, TypedDict
import matplotlib.patches as mpatches
from helpers.tools_file import parent_dir

DATAS = f"{parent_dir(__file__, 2)}/datas/"

# Nom du fichier source (GPKG)
FILE_DESCRIPTEURS = f"{DATAS}/2024_IQRN_descripteurs_DIRMC.gpkg"
FILE_SURFACE = f"{DATAS}/Table_Indicateurs_Etat_surface_DIRMC.xlsx"

# Colonnes de ref "surface"
CLE_TRONCON = "cle_unique_plod"
CLE_TRONCON_LEFT = "cle_troncon_plod"  # côté gpkg
ABD = "abs_debut"
ABF = "abs_fin"
LONGUEUR_TRONCON = "longueur_troncon"
PLOD = "plod"
PLOF = "plof"
ROUTE = "route"
DEP = "sectionnement_departement"
SENS = "sens"
S_EVALUEE = "S_evaluee"


# Champs curvilignes + PR (réutilise logique iq3d)
CURV_START = "curv_start"
CURV_END = "curv_end"
PR_REGEX = r"^([A-Z]*)(\d{2})PR(\d+)[A-Z]?$"
PRD_NUM = "prd_num"
PRF_NUM = "prf_num"
PRD = "PRD"
PRF = "PRF"
PRD_NAT = "PRD_NAT"

# Échelle graph
Y_SCALE = 100
Y_SCALE_W_PR = 120

# Couleurs "surface" base (5)
BASE_COLORS = [
    "green",
    "#b8dfaf",
    "orange",
    "red",
    "purple",
]

MESSAGE_NO_DF = "Pas de DataFrame, impossible de continuer"

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

class DescSpec(TypedDict):
    """Spécification d'un descripteur."""
    layer: str
    column: str
    gravite_type: Literal["bool", "int", "str"]
    gravites: List[Any]  # list[int] ou list[str] selon type


DESCRIPTEURS: Dict[DescTypes, Dict[str, Any]] = {
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
        "gravites": [
            1, 2, 3, 4
        ]
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
            "0,25 cm3", "0,50 cm3", "1,00 cm3", "4,00 cm3"
        ]
    },

    "EMO": {
        "layer": "Descr_gravite_EMO_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            "02,5 cm3", "05,0 cm3", "07,5 cm3", "10,0 cm3", "20,0 cm3", "25,0 cm3", "40,0 cm3"
        ]
    },

    "ESTEX": {
        "layer": "Descr_gravite_eSTex_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            "0,025 cm3", "0,050 cm3", "0,100 cm3", "0,250 cm3"
        ]
    },
    "RAVELING": {
        "layer": "Descr_gravite_Raveling_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            "080 cm3/m2", "120 cm3/m2", "150 cm3/cm", "250 cm3/m2", "500 cm3/m2", "750 cm3/m2"
        ]
    },
    "ORNIERAGE_GRAND_RAYON": {
        "layer": "Descr_gravite_Orniere_Grand_Rayon_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            "07 mm", "10 mm", "15 mm", "20 mm", "25 mm", "30 mm"
        ]
    },
    "ORNIERAGE_PETIT_RAYON": {
        "layer": "Descr_gravite_Orniere_Petit_Rayon_2024 — DIRMC",
        "column": "niveau_gravite_str",
        "gravite_type": "str",
        "gravites": [
            "07 mm", "10 mm", "15 mm", "20 mm"
        ]
    },
}

# Noms colonnes calculées
LEVEL = "level"
PCT = "pct"
DESC = "desc"

def level_name(desc_key: str, level: int) -> str:
    """Nom de la colonne niveau i pour un descripteur donné."""
    return f"{DESC}_{desc_key}_{LEVEL}_{level}"

def pct_name(desc_key: str, level: int) -> str:
    """Nom de la colonne % niveau i pour un descripteur donné."""
    return f"{PCT}_{DESC}_{desc_key}_{LEVEL}_{level}"

# spec pour le type DescTypes
def nb_levels(desc_key: DescTypes) -> int:
    """Niveaux au total = 1 (niveau 0) + nb gravités."""
    spec = DESCRIPTEURS[desc_key]
    if spec["gravite_type"] == "bool":
        return 2
    return 1 + len(spec["gravites"])

def colors_for_levels(n_levels: int, desc_key: DescTypes | None = None) -> List[str]:
    """
    Retourne une liste de couleurs pour les niveaux.
    Si le descripteur est bool, le niveau 1 (présence) est forcé en purple.
    """
    if n_levels <= len(BASE_COLORS):
        cols = BASE_COLORS[:n_levels]
    else:
        cols = BASE_COLORS[:4]

        purple_shades = [
            "#c77cff",
            "#9b4dca",
            "#6a0dad",
            "#4b0082",
            "#2B002B",
            "#0A000A",
        ]
        # On ajoute des nuances de purple si besoin
        needed = n_levels - 4
        cols.extend(purple_shades[:needed])

    #  couleur purple pour bool
    if desc_key is not None:
        spec = DESCRIPTEURS.get(desc_key)
        if spec and spec["gravite_type"] == "bool" and len(cols) > 1:
            cols = cols.copy()
            cols[1] = "purple"

    return cols

def legend_patches(desc_key: DescTypes) -> list[mpatches.Patch]:
    """
    Légende: level 0 = tronçon, level 1.. = gravités.
    """
    nlv = nb_levels(desc_key)
    cols = colors_for_levels(nlv, desc_key=desc_key)
    spec = DESCRIPTEURS[desc_key]

    labels: list[str] = ["Niveau 0 (tronçon)"]
    if spec["gravite_type"] == "bool":
        labels.append(">=1 (présence)")
    else:
        labels.extend([
            f">={g}" if not str(g).startswith(">=") else str(g)
            for g in spec["gravites"]
        ])

    return [mpatches.Patch(color=cols[i], label=labels[i]) for i in range(nlv)]
