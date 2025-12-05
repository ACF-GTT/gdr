"""
Analyse des états de surface des routes à partir de l'AIGLE3D
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


from helpers.consts_etat_surface import (
    COLORS,
    CURV_START, CURV_END,
    SENS_LIST
)

from helpers.iq3d import GraphStates

def main(
    route: str,
    dep: str,
    sens_list: list[str],
    **kwargs
) -> None:
    """main"""
    # 3 graphiques pour 3 niveaux d'états
    #sharex vaut true pour partager l'axe x
    for sens in sens_list:
        assert sens in SENS_LIST
    nbg_per_sens = 3
    nbrows = nbg_per_sens * len(sens_list)
    fig, axes = plt.subplots(
        nrows=nbrows,
        ncols=1,
        figsize=(15, 6),
        sharex=True,
        gridspec_kw={'hspace': 0.5}
    )
    plt.rcParams.update({'font.size': 6})

    grapher = GraphStates()
    grapher.set_route_dep(route=route, dep=dep)
    index = 0
    for sens in sens_list:
        sub_axes = axes[index : index + nbg_per_sens]
        index += nbg_per_sens
        df_filtered = grapher.graphe_sens(
            sens=sens,
            axes=sub_axes,
            **kwargs
        )

        # Axe X partagé
        axes[-1].set_xlim(
            df_filtered[CURV_START].min(),
            df_filtered[CURV_END].max()
        )

    # LÉGENDE DES NIVEAUX
    patches = [
        mpatches.Patch(color=color, label=f">={lvl}")
        for lvl, color in enumerate(COLORS)
    ]

    fig.legend(
        handles=patches,
        loc="upper right",
        ncol=5,)

    plt.tight_layout()
    assert grapher.analyzer.sheet_name is not None
    plt.suptitle(f"{grapher.analyzer.sheet_name} - {route} - dpt {dep}")
    plt.show()

if __name__ == "__main__":
    main(
        route="N0122",
        dep="15",
        sens_list=["M", "P"],
        prd_num=123,
        prf_num=126
    )
