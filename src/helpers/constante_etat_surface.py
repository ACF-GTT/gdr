# === CONFIGURATION ===

"""Constantes pour l'analyse de l'état de surface des routes."""
FILE = r"C:/Users/hugo-h.perez/Desktop/Table_Indicateurs_Etat_surface_DIRMC.xlsx"

STATES = {
    "ies": "Superficiel",
    "iep": "Profond",
    "ietp": "Très profond"
}

# Couleurs du niveau 0 (meilleur) au niveau 4 (pire)
COLORS = [
    "green",  
    "#b8dfaf",  
    "orange",  
    "red",  
    "purple"  
]



# Colonnes du DataFrame
PLOD = "plod"
PLOF = "plof"
ROUTE = "route"
DEP = "sectionnement_departement"
SENS = "sens"
SURF_EVAL = "S_evaluee"
ABD = "abs_debut"
ABF = "abs_fin"
LONGUEUR_TRONCON= "longueur_troncon"

#constantes pour l'extraction des PR
PRD = "PRD"
PRF = "PRF"
PR_REGEX = r"^(\d{2})PR(\d+)[A-Z]?$"

# Colonnes calculées
PRD_NUM = "prd_num"
PRF_NUM = "prf_num"
CURV_START = "curv_start"
CURV_END = "curv_end"


# Paramètres d'affichage
Y_SCALE = 100
Y_SCALE_W_PR = 120

# Sens
SENS_LIST = ["P", "M"]

FIELDS_SELECTION = [
    PRD,
    ABD,
    LONGUEUR_TRONCON,
    CURV_START,
    CURV_END
]
