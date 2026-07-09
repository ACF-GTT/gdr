"""
Cinétique des états de surface AIGLE3D.
Compare deux années et affiche les écarts en % par niveaux.
"""

import matplotlib.pyplot as plt
import pandas as pd

from helpers.consts_cinetique_commun import (
    draw_delta,
    draw_prs,
    merge_old_new,
    setup_delta_axis,
)
from helpers.consts_cinetique_surface import (
    DELTA_PCT_COLORS,
    cinetique_legend,
    delta_pct_name,
)
from helpers.consts_etat_surface import (
    FILE,
    STATES,
    IES,
    IEP,
    IETP,
    SENS_LIST,
    NB_LEVELS,
    pct_name,
)
from helpers.consts_commun_pr_curv import (
    SENS,
    PRD_NUM,
    ABD,
    PRF_NUM,
    ABF,
    PLOD,
    PLOF,
    CURV_START,
    CURV_END,
)
from helpers.graph_tools import habille, init_single_column_plt
from helpers.iq3d import SurfaceAnalyzer


Y_MAX = 100
NB_GRAPHS_PER_SENS = 3
KEYS = [SENS, PRD_NUM, ABD, PRF_NUM, ABF, PLOD, PLOF]

def load_analyzer(sheet_name, route=None, dep=None, **kwargs):
    """Charge une année et applique les traitements de base."""
    df = pd.read_excel(FILE, sheet_name=sheet_name)

    analyzer = SurfaceAnalyzer(df=df)
    analyzer.sheet_name = sheet_name
    analyzer.compute_pr()
    analyzer.compute_levels()
    analyzer.compute_percent()

    if route is not None and dep is not None:
        analyzer.set(route, dep)
        analyzer.filter(**kwargs)

    return analyzer


class CinetiqueSurface:
    """Cinétique des états de surface AIGLE3D : delta % entre deux années."""
    def __init__(self):
        excel_file = pd.ExcelFile(FILE)

        print("Feuilles disponibles dans le fichier :")
        for i, sheet in enumerate(excel_file.sheet_names):
            print(f"{i}: {sheet}")

        old_idx = int(input("Feuille année ancienne : "))
        new_idx = int(input("Feuille année récente : "))

        self.old_sheet = excel_file.sheet_names[old_idx]
        self.new_sheet = excel_file.sheet_names[new_idx]

        self.old = load_analyzer(self.old_sheet)
        self.new = load_analyzer(self.new_sheet)

    def compare(self, sens):
        """Compare deux années sur un même sens."""
        df_old, _ = self.old.compute_curviligne(sens)
        df_new, prs = self.new.compute_curviligne(sens)

        pct_cols = [
            pct_name(state, level)
            for state in STATES
            for level in range(NB_LEVELS)
        ]

        df = merge_old_new(df_old, df_new, pct_cols, KEYS)

        for state in STATES:
            for level in range(NB_LEVELS):
                col = pct_name(state, level)
                df[delta_pct_name(state, level)] = (
                    df[f"{col}_new"] - df[f"{col}_old"]
                )

        return df, prs

    def main(self, route, dep, sens_list, **kwargs):
        """Main."""
        for sens in sens_list:
            assert sens in SENS_LIST

        self.old = load_analyzer(self.old_sheet, route, dep, **kwargs)
        self.new = load_analyzer(self.new_sheet, route, dep, **kwargs)

        fig, axes = init_single_column_plt(NB_GRAPHS_PER_SENS * len(sens_list))

        index = 0
        last_df = None

        for sens in sens_list:
            sub_axes = axes[index:index + NB_GRAPHS_PER_SENS]
            index += NB_GRAPHS_PER_SENS

            df, prs = self.compare(sens)
            last_df = df

            draw_prs(prs, sub_axes[0])

            habille(sub_axes[0], Y_MAX, f"sens {sens}", STATES[IES], grid=True)
            habille(sub_axes[1], Y_MAX, f"sens {sens}", STATES[IEP], grid=True)
            habille(sub_axes[2], Y_MAX, f"sens {sens}", STATES[IETP], grid=True)

            colors = list(DELTA_PCT_COLORS.values())

            for ax in sub_axes:
                setup_delta_axis(ax)

            for _, row in df.iterrows():
                draw_delta(row, IES, delta_pct_name, colors, sub_axes[0])
                draw_delta(row, IEP, delta_pct_name, colors, sub_axes[1])
                draw_delta(row, IETP, delta_pct_name, colors, sub_axes[2])

            print(f"\n=== Delta sens {sens} ===")
            print(
                df[[PRD_NUM, ABD]+[delta_pct_name(IES,lvl) for lvl in range(NB_LEVELS)]]
                .head(200)
            )

        if last_df is not None and not last_df.empty:
            axes[-1].set_xlim(last_df[CURV_START].min(), last_df[CURV_END].max())

        fig.legend(handles=cinetique_legend(), loc="upper right", ncol=9)

        plt.suptitle(
            f"Cinétique surface : {self.new_sheet} - {self.old_sheet} - {route} - dpt {dep}"
        )
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    CinetiqueSurface().main(
        route="N0122",
        dep="15",
        sens_list=["P"],
        prd=78,
        abd=None,
        prf=83,
        abf=None,
    )
