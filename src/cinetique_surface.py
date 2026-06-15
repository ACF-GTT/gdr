"""
Cinétique des états de surface AIGLE3D.
Compare deux années et affiche les écarts en % par niveaux.
"""

import matplotlib.pyplot as plt
import pandas as pd

from helpers.consts_etat_surface import (
    FILE, STATES, IES, IEP, IETP, SENS_LIST, NB_LEVELS, pct_name
)
from helpers.consts_cinetique_surface import (
    DELTA_PCT_COLORS, delta_pct_name, cinetique_legend
)
from helpers.iq3d import SurfaceAnalyzer
from helpers.graph_tools import draw_object, habille, init_single_column_plt
from helpers.consts_commun_pr_curv import (
    SENS, PRD, PRD_NUM, PRF_NUM,
    ABD, ABF, PLOD, PLOF,
    CURV_START, CURV_END,
    Y_SCALE_W_PR,
)


Y_MAX = 100


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


def compare(analyzer_old, analyzer_new, sens):
    """Compare deux années sur un même sens."""
    df_old, _ = analyzer_old.compute_curviligne(sens)
    df_new, prs = analyzer_new.compute_curviligne(sens)

    keys = [SENS, PRD_NUM, ABD, PRF_NUM, ABF, PLOD, PLOF]
    pct_cols = [
        pct_name(state, level)
        for state in STATES
        for level in range(NB_LEVELS)
    ]

    df = df_new[
        keys + [PRD, CURV_START, CURV_END] + pct_cols
    ].merge(
        df_old[keys + pct_cols],
        on=keys,
        suffixes=("_new", "_old")
    )

    for state in STATES:
        for level in range(NB_LEVELS):
            col = pct_name(state, level)
            df[delta_pct_name(state, level)] = (
                df[f"{col}_new"] - df[f"{col}_old"]
            )

    return df, prs


def draw_delta(row, state, ax):
    """Trace le différentiel d'un tronçon."""
    width = row[CURV_END] - row[CURV_START]
    x = row[CURV_START] + width / 2

    bottom_pos = 0
    bottom_neg = 0

    for level in range(NB_LEVELS):
        delta = row[delta_pct_name(state, level)]

        if pd.isna(delta) or delta == 0:
            continue

        # On empile les barres positives et négatives séparément
        if delta > 0:
            bottom = bottom_pos
            bottom_pos += delta
        else:
            bottom = bottom_neg
            bottom_neg += delta

        ax.bar(
            x=x,
            width=width,
            bottom=bottom,
            height=delta,
            color=DELTA_PCT_COLORS[level],
            edgecolor=None,
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

        habille(sub_axes[0], Y_MAX, f"sens {sens}", STATES[IES], grid=True)
        habille(sub_axes[1], Y_MAX, f"sens {sens}", STATES[IEP], grid=True)
        habille(sub_axes[2], Y_MAX, f"sens {sens}", STATES[IETP], grid=True)

        for ax in sub_axes:
            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_ylim(-100, 120)

        for _, row in df.iterrows():
            draw_delta(row, IES, sub_axes[0])
            draw_delta(row, IEP, sub_axes[1])
            draw_delta(row, IETP, sub_axes[2])

        axes[-1].set_xlim(df[CURV_START].min(), df[CURV_END].max())

        print(f"\n=== Delta sens {sens} ===")
        print(
            df[
                [
                    PRD, ABD,
                    delta_pct_name(IES, 0),
                    delta_pct_name(IES, 1),
                    delta_pct_name(IES, 2),
                    delta_pct_name(IES, 3),
                    delta_pct_name(IES, 4),
                ]
            ].head(200)
        )

    fig.legend(
        handles=cinetique_legend(),
        loc="upper right",
        ncol=9,
    )

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
