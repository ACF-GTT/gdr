"""
Affichage des descripteurs comme les états de surface: barres empilées (niveaux par gravités).
"""
import matplotlib.pyplot as plt
from helpers.consts_etat_descripteur import (
    DESCRIPTEURS,
    legend_patches,
    cft_legend_patches,
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

from iq3d_descripteurs import DescripteurAnalyzer, get_configured_descriptors, graphe_desc_section


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
            # CFT_MOYEN: échelle de 0 à 100
            if DESCRIPTEURS[desc_key].is_score:
                habille(
                    ax=ax,
                    scale=Y_SCALE,
                    title=f"CFT_MOYEN – sens {sens}",
                    label="CFT moyen",
                )
            else:
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
                if DESCRIPTEURS[desc_key].is_score:
                    ax.legend(
                        handles=cft_legend_patches(),
                        loc="lower right",
                        bbox_to_anchor=(1.0, 1.02),
                        ncol=4,
                        fontsize="small",
                        frameon=True,
                    )
                else:
                    ax.legend(
                        handles=legend_patches(desc_key),
                        loc="lower right",
                        bbox_to_anchor=(1.0, 1.02),
                        ncol=min(6, DESCRIPTEURS[desc_key].nb_levels),
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
        route="A0711",
        dep="63",
        sens_list=["P"],
        prd=1,
        abd=None,
        prf=6,
        abf=None,
    )
