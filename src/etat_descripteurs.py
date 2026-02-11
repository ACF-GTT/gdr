"""
Affichage des descripteurs comme les états de surface: barres empilées (niveaux par gravités).
"""

from itertools import accumulate

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pandas import Series

from helpers.consts_etat_descripteur import (
    DescTypes,
    DESCRIPTEURS,
    colors_for_levels,
    legend_patches,
    nb_levels,
    pct_name,
)
from helpers.consts_commun_pr_curv import (
    CURV_START,
    CURV_END,
    Y_SCALE_W_PR,
    Y_SCALE,
)
from helpers.graph_tools import (
    draw_object,
    init_single_column_plt,
    habille,
)
from helpers.tools_file import CheckConf

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
        color=cols,
    )


# pylint: disable=too-many-locals
def get_configured_descriptors(conf: CheckConf) -> list[DescTypes]:
    """Retourne la liste des descripteurs à afficher, selon la config."""
    raw = conf.get_descripteurs_raw()

    if raw is None:
        # Par défaut : tous les descripteurs
        return list(DESCRIPTEURS.keys())

    descs: list[DescTypes] = []
    for d in raw:
        if d not in DESCRIPTEURS:
            raise ValueError(f"Descripteur inconnu dans la config: {d}")
        descs.append(d)  # type: ignore[arg-type]

    return descs


def main(
    route: str,
    dep: str,
    sens_list: list[str],
    **kwargs
) -> None:
    """
    Affiche, pour un descripteur, des barres empilées par tronçon le long d'une route.
    """
    conf = CheckConf()
    descripteurs = get_configured_descriptors(conf)

    # 1) Création de la figure :
    # 1 ligne = 1 (descripteur, sens)
    n_rows = len(descripteurs) * len(sens_list)
    fig, axes = init_single_column_plt(n_rows)
    fig.set_size_inches(16.5, 11.7)

    analyzer = DescripteurAnalyzer()
    row_idx = 0
    last_df = None  # Pour caler l'axe X à la fin

    # 2) Boucle descripteur × sens
    for desc_key in descripteurs:
        analyzer.load(desc_key)

        for sens in sens_list:
            ax = axes[row_idx]

            # DF tronçons (1 ligne = 1 tronçon)
            df_tron, curv_prs = analyzer.troncons_df(
                desc_key=desc_key,
                route=route,
                dep=dep,
                sens=sens,
                **kwargs,
            )
            last_df = df_tron

            # 2a) Affiche les PR
            for pr_label, curv in curv_prs.items():
                draw_object(
                    label=pr_label,
                    x_pos=curv,
                    ymax=Y_SCALE_W_PR,
                    ax=ax,
                )

            # 2b) Habillage du graphe
            habille(
                ax=ax,
                scale=Y_SCALE_W_PR,
                title=f"{desc_key} – sens {sens}",
                label=str(desc_key),
            )

            # 2c) Barres empilées par tronçon
            for _, row in df_tron.iterrows():
                graphe_desc_section(desc_key, row, ax)

            row_idx += 1

            # 2d) Légende (une seule fois, sur le premier graphe)
            if sens == sens_list[0]:
                ax.legend(
                handles=legend_patches(desc_key),
                loc="lower right",
                bbox_to_anchor=(1.0, 1.02),
                ncol=min(6, nb_levels(desc_key)),
                fontsize="small",
                frameon=True,
            )

    # 3) Axe X commun
    if last_df is not None and not last_df.empty:
        axes[-1].set_xlim(last_df[CURV_START].min(), last_df[CURV_END].max())

    # 4) Affichage final
    plt.tight_layout()
    plt.suptitle(f"Descripteurs – {route} – dpt {dep}")
    plt.show()


if __name__ == "__main__":
    main(
        route="N0088",
        dep="43",
        sens_list=["P", "M"],
        prd=40,
        abd=None,
        prf=45,
        abf=None,
    )
