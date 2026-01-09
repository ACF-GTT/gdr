"""
Analyse des états de surface des routes à partir de l'AIGLE3D
"""
import matplotlib.pyplot as plt


from helpers.consts_etat_surface import (
    CURV_START, CURV_END,
    SENS_LIST,
    FIELDS_SELECTION_B,
    surface_state_legend
)

from helpers.iq3d import GraphStates
from helpers.graph_tools import init_single_column_plt

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
    fig, axes = init_single_column_plt(nbrows)

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
        print("\n=== PRD / PRF (200 premières lignes) ===")
        print(df_filtered[FIELDS_SELECTION_B].head(200))

        # Axe X partagé
        axes[-1].set_xlim(
            df_filtered[CURV_START].min(),
            df_filtered[CURV_END].max()
        )

    # LÉGENDE DES NIVEAUX
    patches = surface_state_legend()
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
        sens_list=["P", "M"],
        prd = 40,
        abd = None,
        prf = 50,
        abf = None
    )
