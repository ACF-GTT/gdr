"""Constantes pour l'analyse de l'état de surface des routes."""
import matplotlib.patches as mpatches

from helpers.tools_file import CheckConf
FILE = CheckConf().aigle3d_xls()
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
IES = "ies"
IEP = "iep"
IETP = "ietp"

STATES = {
    IES: "SURFACE",
    IEP: "PROFOND",
    IETP: "TRES PROFOND"
}

# Création du PR avec regex
# Explication du pattern : nature+n°dep+PR+n°PR+Sens
PR_REGEX = r"^([A-Z]*)(\d{2})PR(\d+)[A-Z]?$"

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
PRD_NAT = "PRD_NAT"

FIELDS_SELECTION = [
    PRD,
    ABD,
    LONGUEUR_TRONCON,
    CURV_START,
    CURV_END
]
FIELDS_SELECTION_B = [
    PRD, PRD_NAT, ABD,
    PRF, ABF,
    SENS, LONGUEUR_TRONCON,
    PLOD, PLOF
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

def surface_state_legend():
    """Retourne les patches de légende pour les états de surface A3D"""
    return [
        mpatches.Patch(color=color, label=f">={lvl}")
        for lvl, color in enumerate(COLORS)
    ]
