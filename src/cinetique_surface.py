"""
Cinétique des états de surface AIGLE3D.
Compare deux années et affiche les écarts de niveaux dominants.
"""

import matplotlib.pyplot as plt
import pandas as pd

from helpers.consts_etat_surface import (
    FILE, STATES, IES, IEP, IETP, SENS_LIST
)

from helpers.consts_cinetique_surface import (
    DELTA_COLORS, dom_name, delta_name, cinetique_legend
)

from helpers.iq3d import SurfaceAnalyzer, dominant_level
from helpers.graph_tools import draw_object, habille, init_single_column_plt

from helpers.consts_commun_pr_curv import (
    SENS, PRD, PRD_NUM, PRF_NUM,
    ABD, ABF, PLOD, PLOF,
    CURV_START, CURV_END,
    Y_SCALE, Y_SCALE_W_PR,
)


def choose_sheets():
    """Choix des deux feuilles à comparer."""
    excel_file = pd.ExcelFile(FILE)

    print("Feuilles disponibles dans le fichier :")
    for i, sheet in enumerate(excel_file.sheet_names):
        print(f"{i}: {sheet}")

    old_idx = int(input("Feuille année ancienne : "))
    new_idx = int(input("Feuille année récente : "))

    return excel_file.sheet_names[old_idx], excel_file.sheet_names[new_idx]


def load_analyzer(sheet_name, route, dep, **kwargs):
    """Charge une année et applique les traitements de base."""
    df = pd.read_excel(FILE, sheet_name=sheet_name)

    analyzer = SurfaceAnalyzer(df=df)
    analyzer.sheet_name = sheet_name
    analyzer.compute_pr()
    analyzer.compute_levels()
    analyzer.compute_percent()
    analyzer.set(route, dep)
    analyzer.filter(**kwargs)

    return analyzer

#Pour chaque ligne du DataFrame, on calcule le niveau dominant
def add_dominants(df):
    """Ajoute les niveaux dominants pour chaque état."""
    for state in STATES:
        df[dom_name(state)] = df.apply(
            dominant_level,
            axis=1,
            state=state,
        )
    return df

# 1 : On compare un même tronçon
# 2 : On fusionne les deux DataFrames sur les clés de tronçon
# 3 : On calcule les différentiels pour chaque état de surface
def compare(analyzer_old, analyzer_new, sens):
    """Compare deux années sur un même sens."""
    df_old, _ = analyzer_old.compute_curviligne(sens)
    df_new, prs = analyzer_new.compute_curviligne(sens)

    df_old = add_dominants(df_old)
    df_new = add_dominants(df_new)

    keys = [SENS, PRD_NUM, ABD, PRF_NUM, ABF, PLOD, PLOF]
    dom_cols = [dom_name(state) for state in STATES]

    df = df_new[
        keys + [PRD, CURV_START, CURV_END] + dom_cols
    ].merge(
        df_old[keys + dom_cols],
        on=keys,
        suffixes=("_new", "_old")
    )

    for state in STATES:
        df = df.dropna(
            subset=[
                f"{dom_name(state)}_new",
                f"{dom_name(state)}_old"
            ]
        )

        df[delta_name(state)] = (
            df[f"{dom_name(state)}_new"]
            - df[f"{dom_name(state)}_old"]
        )

    return df, prs


def draw_delta(row, state, ax):
    """Trace le différentiel d'un tronçon."""
    delta = int(row[delta_name(state)])
    width = row[CURV_END] - row[CURV_START]

    ax.bar(
        x=row[CURV_START] + width / 2,
        width=width,
        height=Y_SCALE,
        color=DELTA_COLORS[delta],
        edgecolor="black",
        linewidth=0.2,
    )


def main(route, dep, sens_list, **kwargs):
    """Main."""
    for sens in sens_list:
        assert sens in SENS_LIST

    old_sheet, new_sheet = choose_sheets()

    analyzer_old = load_analyzer(old_sheet, route, dep, **kwargs)
    analyzer_new = load_analyzer(new_sheet, route, dep, **kwargs)

    fig, axes = init_single_column_plt(3 * len(sens_list))

    index = 0
    for sens in sens_list:
        sub_axes = axes[index:index + 3]
        index += 3

        df, prs = compare(analyzer_old, analyzer_new, sens)

        for pr, curv in prs.items():
            draw_object(pr, curv, Y_SCALE_W_PR, sub_axes[0])

        habille(sub_axes[0], Y_SCALE_W_PR, f"sens {sens}", STATES[IES], grid=True)
        habille(sub_axes[1], Y_SCALE, f"sens {sens}", STATES[IEP], grid=True)
        habille(sub_axes[2], Y_SCALE, f"sens {sens}", STATES[IETP], grid=True)

        for _, row in df.iterrows():
            draw_delta(row, IES, sub_axes[0])
            draw_delta(row, IEP, sub_axes[1])
            draw_delta(row, IETP, sub_axes[2])

        axes[-1].set_xlim(df[CURV_START].min(), df[CURV_END].max())

        print(f"\n=== Delta sens {sens} ===")
        print(df[[PRD, ABD, delta_name(IES), delta_name(IEP), delta_name(IETP)]].head(200))

    fig.legend(handles=cinetique_legend(), loc="upper right", ncol=9)

    plt.suptitle(
        f"Cinétique surface : {new_sheet} - {old_sheet} - {route} - dpt {dep}"
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main(
        route="N0102",
        dep="43",
        sens_list=["P"],
        prd=60,
        abd=None,
        prf=80,
        abf=None,
    )
