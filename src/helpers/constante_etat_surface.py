# === CONFIGURATION ===
FILE = r"C:/Users/hugo-h.perez/Desktop/Tables Indicateur Descripteur Localisation/Table_Indicateurs_Etat_surface_DIRMC.xlsx"

STATES = {
    "ies": "Superficiel",
    "iep": "Profond",
    "ietp": "Très profond"
}

# Couleurs du niveau 0 (meilleur) au niveau 4 (pire)
COLORS = [
    "#7CFC00",  # vert clair
    "#228B22",  # vert foncé
    "#FFFF00",  # jaune
    "#FFA500",  # orange
    "#FF0000"   # rouge
]

# Colonnes du DataFrame
PLOD = "plod"
PLOF = "plof"
ROUTE = "route"
DEP = "sectionnement_departement"  # tu gardes le vrai nom exact
SENS = "sens"
SURF_EVAL = "S_evaluee"
ABD = "abs_debut"
ABF = "abs_fin"

#constantes pour l'extraction des PR
PRD = "PRD"
PRF = "PRF"
