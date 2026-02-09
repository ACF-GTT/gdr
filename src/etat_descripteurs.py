"""
Affichage des descripteurs comme les états de surface: barres empilées (niveaux par gravités).
"""

from itertools import accumulate

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pandas import Series

from helpers.consts_etat_descripteur import (
    DescTypes,
    colors_for_levels,
    legend_patches,
    nb_levels,
    pct_name,
)
from helpers.consts_commun_pr_curv import (
    CURV_START, CURV_END,
    Y_SCALE_W_PR, Y_SCALE
)
from helpers.graph_tools import draw_object, init_single_column_plt
from helpers.graph_tools import habille
from iq3d_descripteurs import DescripteurAnalyzer


def graphe_desc_section(desc_key: DescTypes, row: Series, ax: Axes) -> None:
    """Trace la barre empilée pour un tronçon (niveaux 0..N)."""
    curv_start = row[CURV_START]
    curv_end = row[CURV_END]
    width = curv_end - curv_start

    nlv = nb_levels(desc_key)
    cols = colors_for_levels(nlv, desc_key=desc_key)

    heights = [
        Y_SCALE * row[pct_name(desc_key, lvl)] / 100
        for lvl in range(nlv)
    ]
    bottoms = [0, *accumulate(heights[:-1])]

    ax.bar(
        x=curv_start + width / 2,
        width=width,
        bottom=bottoms,
        height=heights,
        color=cols
    )

# pylint: disable=too-many-locals

def main(
    desc_key: DescTypes,
    route: str,
    dep: str,
    sens_list: list[str],
    **kwargs
) -> None:
    """
    Affiche, pour un descripteur, des barres empilées par tronçon le long d'une route.
    """

    # 1) Création de la figure: 1 ligne = 1 sens
    fig, axes = init_single_column_plt(len(sens_list))

    # 2) On Charge les occurrences du descripteur + merge avec la table excel
    analyzer = DescripteurAnalyzer()
    analyzer.load(desc_key)
    last_df = None  # Pour caler l'axe X à la fin

    # 3) Pour chaque sens: on récupère les tronçons filtrés + les PR + on dessine
    for i, sens in enumerate(sens_list):
        ax = axes[i]

        # DF tronçons (1 ligne = 1 tronçon) avec % par niveau + curv_start/curv_end
        df_tron, curv_prs = analyzer.troncons_df(
            desc_key=desc_key,
            route=route,
            dep=dep,
            sens=sens,
            **kwargs
        )
        last_df = df_tron

        # 3a) Affiche les PR (lignes verticales / repères)
        for pr_label, curv in curv_prs.items():
            draw_object(label=pr_label, x_pos=curv, ymax=Y_SCALE_W_PR, ax=ax)

        # 3b) Habillage du graphe (titre, axes, limites Y)
        habille(ax=ax, scale=Y_SCALE_W_PR, title=f"sens {sens}", label=str(desc_key))

        # 3c) Dessine une barre empilée par tronçon
        for _, row in df_tron.iterrows():
            graphe_desc_section(desc_key, row, ax)

    # 4) Axe X commun : on prend min/max curv sur le dernier DF
    if last_df is not None and not last_df.empty:
        axes[-1].set_xlim(last_df[CURV_START].min(), last_df[CURV_END].max())

    # 5) Légende (couleurs = niveaux)
    fig.legend(
        handles=legend_patches(desc_key),
        loc="upper right",
        ncol=min(6, nb_levels(desc_key))
    )

    # 6) Affichage final
    plt.tight_layout()
    plt.suptitle(f"Descripteur {desc_key} - {route} - dpt {dep}")
    plt.show()


if __name__ == "__main__":
    main(
        desc_key="DENSITE_FISSURATION",
        route="N0122",
        dep="15",
        sens_list=["P", "M"],
        prd=None,
        abd=None,
        prf=None,
        abf=None,
    )
