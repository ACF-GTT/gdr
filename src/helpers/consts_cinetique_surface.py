"""Constantes pour la cinétique des états de surface."""

import matplotlib.patches as mpatches

DELTA_COLORS = {
    -4: "darkgreen",
    -3: "forestgreen",
    -2: "limegreen",
    -1: "lightgreen",
     0: "white",
     1: "yellow",
     2: "orange",
     3: "red",
     4: "purple",
}

# Construction automatique des noms de colonnes pour les états de surface
def dom_name(state: str) -> str:
    """Nom de colonne du niveau dominant."""
    return f"dom_{state}"

#Construction automatique des noms de colonnes contenant les écarts entre les années
def delta_name(state: str) -> str:
    """Nom de colonne du différentiel."""
    return f"delta_{state}"


def cinetique_legend():
    """Légende des différentiels de gravité."""
    return [
        mpatches.Patch(color=color, label=str(delta))
        for delta, color in DELTA_COLORS.items()
    ]
