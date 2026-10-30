
"""Génération d'une page de légende PDF/SVG pour les rapports."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from helpers.tools_file import CheckConf
from helpers.consts_etat_surface import surface_state_legend
from helpers.consts_etat_descripteur import (
    DESCRIPTEURS,
    legend_patches,
    cft_legend_patches,
    classe_iqp_legend_patches,
)
from helpers.iq3d_descripteurs import get_configured_descriptors
from helpers.consts import LEGENDS, COLORS


def get_cft_legend():
    """Retourne la légende GripTester sans pourcentages."""
    return [
        mpatches.Patch(
            color=COLORS["CFT"][level],
            label=label
        )
        for level, label in LEGENDS["CFT"].items()
    ]


def create_legend_page():
    """Génère les légendes choisies dans configuration.yml."""

    conf = CheckConf()

    # Vérifie si l'export est activé
    if not conf.export_legend_page():
        return

    # Choix des légendes depuis le YAML
    grip = bool(conf.yaml.get("legend_page_grip", 0))
    aigle = bool(conf.yaml.get("legend_page_etat_surface", 0))
    descripteurs = bool(conf.yaml.get("legend_page_etat_descripteurs", 0))

    groups = []

    # 1. Légende GripTester - CFT
    if grip:
        groups.append((
            "GripTester - CFT",
            get_cft_legend()
        ))

    # 2. Légende des états de surface Aigle3D
    if aigle:
        groups.append((
            "États de surface Aigle3D",
            surface_state_legend()
        ))

    # 3. Légendes des descripteurs sélectionnés dans le YAML
    if descripteurs:
        for desc in get_configured_descriptors(conf):

            if DESCRIPTEURS[desc].is_score:
                patches = cft_legend_patches()

            elif DESCRIPTEURS[desc].is_iqp:
                patches = classe_iqp_legend_patches()

            else:
                patches = legend_patches(desc)

            groups.append((str(desc), patches))

    # Si aucune légende n'est sélectionnée
    if not groups:
        print("Aucune légende sélectionnée pour l'export.")
        return

    # CRÉATION DE LA PAGE A4 PAYSAGE

    fig = plt.figure(figsize=(11.69, 8.27))

    fig.suptitle(
        "Légende des schémas itinéraires",
        fontsize=18,
        y=0.97
    )

    # Deux colonnes
    nb_rows = (len(groups) + 1) // 2

    for i, (title, patches) in enumerate(groups):

        ax = fig.add_subplot(nb_rows, 2, i + 1)
        ax.axis("off")

        ax.legend(
            handles=patches,
            title=title,
            loc="upper left",
            frameon=False,
            fontsize=9,
            title_fontsize=11
        )

    fig.subplots_adjust(
        top=0.88,
        bottom=0.05,
        left=0.06,
        right=0.96,
        hspace=0.25,
        wspace=0.25
    )

    # Export PDF et SVG
    fig.savefig("legende_generale.pdf", bbox_inches="tight")
    fig.savefig("legende_generale.svg", bbox_inches="tight")

    plt.close(fig)

    print("Page de légende générée : legende_generale.pdf / .svg")


if __name__ == "__main__":
    create_legend_page()
