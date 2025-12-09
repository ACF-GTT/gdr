"""Constantes pour l'analyse de l'état de surface des routes."""
from helpers.tools_file import parent_dir
FILE = f"{parent_dir(__file__, 2)}/datas/Aigle3D/Table_Indicateurs_Etat_surface_DIRMC.xlsx"

# Couleurs du niveau 0  au niveau 4
COLORS = [
    "green",
    "#b8dfaf",
    "orange",
    "red",
    "purple"
]

# noms des colonnes du fichier xlsx fourni par la DTECITM
ABD = "abs_debut"
ABF = "abs_fin"
DEP = "sectionnement_departement"
LONGUEUR_TRONCON= "longueur_troncon"
PLOD = "plod"
PLOF = "plof"
ROUTE = "route"
SENS = "sens"
SURF_EVAL = "S_evaluee"

STATES = {
    "ies": "SURFACE",
    "iep": "PROFOND",
    "ietp": "TRES PROFOND"
}

# Création du PR avec regex
PR_REGEX = r"^(\d{2})PR(\d+)[A-Z]?$"

# Echelles pour les graphiques

Y_SCALE = 100
Y_SCALE_W_PR = 120

# Création des colonnes (utiles pour avoir le curviligne)
CURV_START = "curv_start"
CURV_END = "curv_end"
PRD_NUM = "prd_num"
PRF_NUM = "prf_num"
PRD = "PRD"
PRF = "PRF"

FIELDS_SELECTION = [
    PRD,
    ABD,
    LONGUEUR_TRONCON,
    CURV_START,
    CURV_END
]

SENS_LIST = ["P", "M"]

SUP = "sup"
LEVEL = "level"
PCT = "pct"

NB_LEVELS = 5

D_SUP = {
    state: [f"S_{state}_{SUP}_{level}" for level in range(NB_LEVELS)]
    for state in STATES
}

def level_name(state: str, level: int) -> str:
    """name"""
    return f"S_{state}_{LEVEL}_{level}"

def pct_name(state: str, level: int) -> str:
    """name"""
    return f"{PCT}_{state}_{LEVEL}_{level}"


MESSAGE_NO_DF = "Pas de DataFrame, impossible de continuer"
