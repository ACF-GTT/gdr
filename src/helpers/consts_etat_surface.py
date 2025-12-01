"""Constantes pour l'analyse de l'état de surface des routes."""

from helpers.tools_file import parent_dir

FILE = f"{parent_dir(__file__, 2)}/datas/AIGLE_3D/Table_Indicateurs_Etat_surface_DIRMC.xlsx"

# Couleurs du niveau 0 (meilleur) au niveau 4 (pire)
COLORS_VARIANT = [
    "#7CFC00",  # vert clair
    "#228B22",  # vert foncé
    "#FFFF00",  # jaune
    "#FFA500",  # orange
    "#FF0000"   # rouge
]
COLORS = [
    "green",
    "#b8dfaf",
    "orange",
    "red",
    "purple"
]

# noms de colonnes du fichier xls de la DTEC ITM
PLOD = "plod"
PLOF = "plof"
ROUTE = "route"
DEP = "sectionnement_departement"
SENS = "sens"
SURF_EVAL = "S_evaluee"
ABD = "abs_debut"
ABF = "abs_fin"
LONGUEUR_TRONCON= "longueur_troncon"
STATES = {
    "ies": "SURFACE",
    "iep": "PROFOND",
    "ietp": "TRES PROFOND"
}

# regexp pour l'extraction des PR
PR_REGEX = r"^(\d{2})PR(\d+)[A-Z]?$"

Y_SCALE = 100
Y_SCALE_W_PR = 120

# noms des colonnes créées
CURV_START = "curv_start"
CURV_END = "curv_end"
PRD_NUM = "prd_num"
PRF_NUM = "prf_num"
# uniquement pour affichage des PR
PRD = "PRD"
PRF = "PRF"

# seulement pour un affichage CLI
FIELDS_SELECTION = [
    PRD,
    ABD,
    LONGUEUR_TRONCON,
    CURV_START,
    CURV_END
]

SENS_LIST = ["P", "M"]

MESSAGE_NO_DF = "Pas de DataFrame, impossible de continuer."
