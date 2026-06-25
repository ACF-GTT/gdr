"""Cinétique des descripteurs AIGLE3D : delta % entre deux GPKG."""
# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from helpers.consts_cinetique_commun import draw_delta, draw_prs, merge_old_new, setup_delta_axis
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
    PRD,
    PRD_NUM,
    PRF_NUM,
    ABD,
    ABF,
    PLOD,
    PLOF,
    CURV_START,
    CURV_END,
)
from helpers.graph_tools import habille, init_single_column_plt
from helpers.iq3d_descripteurs import DescripteurAnalyzer, get_configured_descriptors
from helpers.tools_file import CheckConf


Y_MAX = 100
KEYS = [SENS, PRD_NUM, ABD, PRF_NUM, ABF, PLOD, PLOF]


def choose_gpkgs() -> tuple[Path, Path]:
    """Choix des deux fichiers GPKG à comparer."""
    files = sorted(Path(DATAS).rglob("*.gpkg"))

    print("Fichiers GPKG disponibles :")
    for i, file in enumerate(files):
        print(f"{i}: {file}")

    return (
        files[int(input("Fichier année ancienne : "))],
        files[int(input("Fichier année récente : "))],
    )


def weight_descriptors() -> list[DescTypes]:
    """Descripteurs configurés, uniquement les weight."""
    return [
        desc
        for desc in get_configured_descriptors(CheckConf())
        if DESCRIPTEURS[desc].is_weight
    ]


def compare(
    old: DescripteurAnalyzer,
    new: DescripteurAnalyzer,
    desc: DescTypes,
    route: str,
    dep: str,
    sens: str,
    **kwargs,
) -> tuple[pd.DataFrame, dict]:
    """Compare ancien/nouveau pour un descripteur et un sens."""
    old.load(desc)
    new.load(desc)

    df_old, _ = old.troncons_df(desc, route, dep, sens, **kwargs)
    df_new, prs = new.troncons_df(desc, route, dep, sens, **kwargs)

    n_levels = DESCRIPTEURS[desc].nb_levels
    pct_cols = [pct_name(desc, lvl) for lvl in range(n_levels)]

    df = merge_old_new(df_old, df_new, pct_cols, KEYS)


    for lvl in range(n_levels):
        col = pct_name(desc, lvl)
        df[delta_pct_name(desc, lvl)] = df[f"{col}_new"] - df[f"{col}_old"]

    return df, prs


def main(route: str, dep: str, sens_list: list[str], **kwargs) -> None:
    """Main."""
    for sens in sens_list:
        assert sens in SENS_LIST

    descs = weight_descriptors()
    old_gpkg, new_gpkg = choose_gpkgs()

    old = DescripteurAnalyzer(file_path=old_gpkg)
    new = DescripteurAnalyzer(file_path=new_gpkg)

    fig, axes = init_single_column_plt(len(descs) * len(sens_list))
    fig.set_size_inches(16.5, 11.7)

    row_idx = 0
    last_df = None

    for desc in descs:
        n_levels = DESCRIPTEURS[desc].nb_levels
        colors = colors_for_levels(n_levels, desc)

        for sens in sens_list:
            ax = axes[row_idx]
            df, prs = compare(old, new, desc, route, dep, sens, **kwargs)
            last_df = df

            draw_prs(prs, ax)

            habille(
                ax=ax,
                scale=Y_MAX,
                title=f"{desc} – sens {sens}",
                label=f"Delta % {desc}",
                grid=True,
            )

            setup_delta_axis(ax)

            for _, row in df.iterrows():
                draw_delta(
                    row,
                    desc,
                    delta_pct_name,
                    colors,
                    n_levels,
                    ax,
                )

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
                df[
                    [PRD, ABD]
                    + [delta_pct_name(desc, lvl) for lvl in range(n_levels)]
                ].head(200)
            )

            row_idx += 1

    if last_df is not None and not last_df.empty:
        axes[-1].set_xlim(
            last_df[CURV_START].min(),
            last_df[CURV_END].max(),
        )

    plt.suptitle(
        f"Cinétique descripteurs : {new_gpkg.name} - {old_gpkg.name} - {route} - dpt {dep}"
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
