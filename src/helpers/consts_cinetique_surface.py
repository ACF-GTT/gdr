"""Constantes pour la cinétique des états de surface."""

import matplotlib.patches as mpatches

DELTA_PCT_COLORS = {
    0: "green",
    1: "#b8dfaf",
    2: "orange",
    3: "red",
    4: "purple",
}

#Construction automatique des noms de colonnes contenant les écarts entre les années
def delta_pct_name(state: str, level: int) -> str:
    """Nom de colonne du différentiel."""
    return f"delta_pct_{state}_level_{level}"


def cinetique_legend():
    """Légende des différentiels de gravité."""
    return [
        mpatches.Patch(color=color, label=f"Niveau {level}")
        for level, color in DELTA_PCT_COLORS.items()
    ]
