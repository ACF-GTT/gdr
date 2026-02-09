"""Constantes communes aux analyses état de surface et descripteurs
(liées au PR, curviligne, affichage et conventions DataFrame).
"""

# PR / REGEX
PR_REGEX = r"^([A-Z]*)(\d{2})PR(\d+)[A-Z]?$"

# CHAMPS CURVILIGNES
CURV_START = "curv_start"
CURV_END = "curv_end"
PRD_NUM = "prd_num"
PRF_NUM = "prf_num"
PRD = "PRD"
PRF = "PRF"
PRD_NAT = "PRD_NAT"

# Colonnes de ref "surface"
ABD = "abs_debut"
ABF = "abs_fin"
LONGUEUR_TRONCON = "longueur_troncon"
PLOD = "plod"
PLOF = "plof"
ROUTE = "route"
DEP = "sectionnement_departement"
SENS = "sens"
SURF_EVAL = "S_evaluee"


# Constantes pour niveaux
LEVEL = "level"
PCT = "pct"

# AFFICHAGE / GRAPHIQUES
Y_SCALE = 100
Y_SCALE_W_PR = 120

# MESSAGES COMMUNS
MESSAGE_NO_DF = "Pas de DataFrame, impossible de continuer"

COLORS = [
    "green",
    "#b8dfaf",
    "orange",
    "red",
    "purple",
]
