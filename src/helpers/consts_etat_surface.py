"""Constantes pour l'analyse de l'état de surface des routes."""
import matplotlib.patches as mpatches

from helpers.tools_file import CheckConf
from helpers.consts_commun_pr_curv import (
    COLORS, CURV_START, CURV_END,PRD, PRF, PRD_NAT,
    ABD, ABF, LONGUEUR_TRONCON, SENS, PLOD, PLOF,
    LEVEL, PCT
)

FILE = CheckConf().aigle3d_xls()

# noms des colonnes du fichier xlsx fourni par la DTECITM
IES = "ies"
IEP = "iep"
IETP = "ietp"

STATES = {
    IES: "SURF.",
    IEP: "PROF.",
    IETP: "T.PROF."
}

SI ="si"
CFT_MOYEN = "cft_moyen"

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



def surface_state_legend():
    """Retourne les patches de légende pour les états de surface A3D"""
    return [
        mpatches.Patch(color=color, label=f">={lvl}")
        for lvl, color in enumerate(COLORS)
    ]
