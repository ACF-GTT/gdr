"""Cinétique des descripteurs AIGLE3D : delta % entre deux GPKG."""

from pathlib import Path

import matplotlib.pyplot as plt

from helpers.consts_cinetique_commun import (
    Y_MAX,
    draw_delta,
    draw_prs,
    merge_old_new,
    setup_delta_axis,
    delta_pct_name,
)
from helpers.consts_cinetique_descripteurs import cinetique_legend
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
from helpers.graph_tools import habille, init_single_column_plt, render
from helpers.iq3d_descripteurs import DescripteurAnalyzer, get_configured_descriptors
from helpers.tools_file import CheckConf
from helpers.shared import pick_files
from helpers.pr_plus_abs import PlotText


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
        """initialisation"""
        self.route = CheckConf().yaml.get("aigle_route", "N0088")
        self.dep = CheckConf().yaml.get("aigle_dep", 43)
        self.sens_list = CheckConf().yaml.get("aigle_sens", ["P"])
        files = pick_files(
            old={"folder_path": DATAS, "ext": ["gpkg"], "message": "Choisir ancien"},
            new={"folder_path": DATAS, "ext": ["gpkg"], "message": "Choisir récent"},
        )

        self.old_gpkg = Path(files["old"])
        self.new_gpkg = Path(files["new"])

        self.old = DescripteurAnalyzer(file_path=self.old_gpkg)
        self.new = DescripteurAnalyzer(file_path=self.new_gpkg)

    def compare(self, desc: DescTypes, *, sens: str):
        """Compare ancien/nouveau pour un descripteur et un sens."""
        self.old.load(desc)
        self.new.load(desc)
        section = CheckConf().yaml.get("section", {})
        prd = section.get("prd")
        abd = section.get("abd")
        prf = section.get("prf")
        abf = section.get("abf")
        df_old, _ = self.old.troncons_df(desc, self.route, self.dep, sens,
            prd=prd, abd=abd, prf=prf, abf=abf)
        df_new, prs = self.new.troncons_df(desc, self.route, self.dep, sens,
            prd=prd, abd=abd, prf=prf, abf=abf)

        n_levels = DESCRIPTEURS[desc].nb_levels
        pct_cols = [pct_name(desc, lvl) for lvl in range(n_levels)]

        df = merge_old_new(df_old, df_new, pct_cols, KEYS)

        for lvl in range(n_levels):
            col = pct_name(desc, lvl)
            df[delta_pct_name(desc, lvl)] = df[f"{col}_new"] - df[f"{col}_old"]

        return df, prs

    def main(self):
        """Main."""
        for sens in self.sens_list:
            assert sens in SENS_LIST

        descs = weight_descriptors()
        text_helper = PlotText(route=self.route)

        _, axes = init_single_column_plt(
            len(descs) * len(self.sens_list) + text_helper.nb_infos
        )

        row_idx = 0
        df = None

        for sens in self.sens_list:
            for desc in descs:
                n_levels = DESCRIPTEURS[desc].nb_levels
                colors = colors_for_levels(n_levels, desc)
                ax = axes[row_idx]

                df, prs = self.compare(
                    desc, sens=sens
                )

                draw_prs(prs, ax)

                habille(
                    ax=ax,
                    scale=Y_MAX,
                    title=f"{desc} - sens {sens}",
                    label="Delta %",
                    grid=True,
                )

                setup_delta_axis(ax, y_scale=Y_MAX)

                for _, row in df.iterrows():
                    draw_delta(row, desc, colors, ax)

                if CheckConf().view_legend() and sens == self.sens_list[0]:
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
                    df[
                        [PRD_NUM, ABD]
                        + [delta_pct_name(desc, lvl) for lvl in range(n_levels)]
                    ].head(200)
                )

                row_idx += 1

            if text_helper.nb_infos:
                text_helper.compute_abs(prs, sens)

                for txt_type in text_helper.filtered[sens]:
                    row_idx += text_helper.plot_text_line(
                        txt_type, axes[row_idx], sens
                    )
        if df is not None and not df.empty:
            if CheckConf().yaml.get("force_range") == "pr_abs":
                text_helper.adjust(axes[-1])
            else:
                axes[-1].set_xlim(
                    df[CURV_START].min(),
                    df[CURV_END].max()
                )

        title = "Cinétique descripteurs :"
        title = f"{title} {self.new_gpkg.name} - {self.old_gpkg.name}"
        title = f"{title}- {self.route} - dpt {self.dep}"
        plt.suptitle(
            title,
            x=0.01, ha="left"
        )
        plt.tight_layout()
        render("cinetique_descripteurs")


if __name__ == "__main__":
    CinetiqueDescripteurs().main()
