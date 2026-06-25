"""Constantes pour la cinétique des états de surface."""

import matplotlib.patches as mpatches

DELTA_PCT_COLORS = {
    0: "green",
    1: "#b8dfaf",
    2: "orange",
    3: "red",
    4: "purple",
}


def delta_pct_name(state: str, level: int) -> str:
    """Nom de colonne du différentiel."""
    return f"delta_pct_{state}_level_{level}"


def cinetique_legend():
    """Légende des différentiels par niveau."""
    return [
        mpatches.Patch(color=DELTA_PCT_COLORS[level], label=f"Niveau {level}")
        for level in range(len(DELTA_PCT_COLORS))
    ]
