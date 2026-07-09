"""Cinétique des descripteurs AIGLE3D : delta % entre deux GPKG."""

from pathlib import Path

import matplotlib.pyplot as plt

from helpers.consts_cinetique_commun import (
    draw_delta,
    draw_prs,
    merge_old_new,
    setup_delta_axis,
)
from helpers.consts_cinetique_descripteurs import (
    cinetique_legend,
    delta_pct_name,
)
from helpers.consts_etat_descripteur import (
    DATAS,
    DESCRIPTEURS,
    DescTypes,
    colors_for_levels,
    pct_name,
)
from helpers.consts_etat_surface import SENS_LIST
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
from helpers.iq3d_descripteurs import DescripteurAnalyzer, get_configured_descriptors
from helpers.tools_file import CheckConf
from helpers.shared import pick_files


Y_MAX = 100
KEYS = [SENS, PRD_NUM, ABD, PRF_NUM, ABF, PLOD, PLOF]


def weight_descriptors() -> list[DescTypes]:
    """Descripteurs configurés, uniquement les weight."""
    return [
        desc
        for desc in get_configured_descriptors(CheckConf())
        if DESCRIPTEURS[desc].is_weight
    ]

class CinetiqueDescripteurs:
    """Cinétique des descripteurs AIGLE3D : delta % entre deux GPKG."""
    def __init__(self):
        files = pick_files(
            old={"folder_path": DATAS, "ext": ["gpkg"], "message": "Choisir ancien"},
            new={"folder_path": DATAS, "ext": ["gpkg"], "message": "Choisir récent"},
        )

        self.old_gpkg = Path(files["old"])
        self.new_gpkg = Path(files["new"])

        self.old = DescripteurAnalyzer(file_path=self.old_gpkg)
        self.new = DescripteurAnalyzer(file_path=self.new_gpkg)


    def compare(self, desc: DescTypes, *, route: str, dep: str, sens: str, **kwargs):
        """Compare ancien/nouveau pour un descripteur et un sens."""
        self.old.load(desc)
        self.new.load(desc)

        df_old, _ = self.old.troncons_df(desc, route, dep, sens, **kwargs)
        df_new, prs = self.new.troncons_df(desc, route, dep, sens, **kwargs)

        n_levels = DESCRIPTEURS[desc].nb_levels
        pct_cols = [pct_name(desc, lvl) for lvl in range(n_levels)]

        df = merge_old_new(df_old, df_new, pct_cols, KEYS)

        for lvl in range(n_levels):
            col = pct_name(desc, lvl)
            df[delta_pct_name(desc, lvl)] = df[f"{col}_new"] - df[f"{col}_old"]

        return df, prs

    def main(self, route: str, dep: str, sens_list: list[str], **kwargs):
        """Main."""
        for sens in sens_list:
            assert sens in SENS_LIST

        descs = weight_descriptors()

        fig, axes = init_single_column_plt(len(descs) * len(sens_list))
        fig.set_size_inches(16.5, 11.7)

        row_idx = 0
        last_df = None

        for desc in descs:
            n_levels = DESCRIPTEURS[desc].nb_levels
            colors = colors_for_levels(n_levels, desc)

            for sens in sens_list:
                ax = axes[row_idx]

                df, prs = self.compare(desc, route=route, dep=dep, sens=sens, **kwargs)
                last_df = df

                draw_prs(prs, ax)

                habille(
                    ax=ax,
                    scale=Y_MAX,
                    title=f"{desc} – sens {sens}",
                    label=f"Delta % {desc}",
                    grid=True
                )

                setup_delta_axis(ax)

                for _, row in df.iterrows():
                    draw_delta(row, desc, delta_pct_name, colors, ax)

                if sens == sens_list[0]:
                    ax.legend(
                        handles=cinetique_legend(desc),
                        loc="lower right",
                        bbox_to_anchor=(1.0, 1.02),
                        ncol=min(6, n_levels),
                        fontsize="small",
                        frameon=True,
                    )

                print(f"\n=== Delta {desc} sens {sens} ===")
                print(
                    df[[PRD_NUM, ABD] + [delta_pct_name(desc, lvl) for lvl in range(n_levels)]]
                    .head(200)
                )

                row_idx += 1

        if last_df is not None and not last_df.empty:
            axes[-1].set_xlim(last_df[CURV_START].min(), last_df[CURV_END].max())

        plt.suptitle(
            f"Cinétique descripteurs:{self.new_gpkg.name}-{self.old_gpkg.name}-{route}-dpt{dep}"
        )
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    CinetiqueDescripteurs().main(
        route="N0122",
        dep="15",
        sens_list=["P"],
        prd=89,
        abd=None,
        prf=92,
        abf=None,
    )
