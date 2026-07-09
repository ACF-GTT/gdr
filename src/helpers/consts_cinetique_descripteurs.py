"""Constantes pour la cinétique des descripteurs."""

import matplotlib.patches as mpatches

from helpers.consts_etat_descripteur import (
    DescTypes,
    DESCRIPTEURS,
    colors_for_levels,
)

def cinetique_legend(desc_key: DescTypes):
    """Légende des différentiels par niveau."""
    colors = colors_for_levels(
        DESCRIPTEURS[desc_key].nb_levels,
        desc_key,
    )

    return [
        mpatches.Patch(color=color, label=f"Niveau {level}")
        for level, color in enumerate(colors)
    ]
