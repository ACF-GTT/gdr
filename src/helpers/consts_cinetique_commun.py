"""Fonctions communes aux cinétiques."""

import pandas as pd
from matplotlib.axes import Axes

from helpers.consts_cinetique_surface import delta_pct_name
from helpers.consts_commun_pr_curv import CURV_START, CURV_END, PRD, Y_SCALE_W_PR
from helpers.graph_tools import draw_object

def draw_prs(prs: dict[str, float], ax: Axes) -> None:
    """Affiche les PR."""
    for pr, curv in prs.items():
        draw_object(pr, curv, Y_SCALE_W_PR, ax)


def draw_delta(
    row: pd.Series,
    key: str,
    colors: list[str],
    ax: Axes,
) -> None:
    """Trace les deltas positifs/négatifs empilés."""
    width = row[CURV_END] - row[CURV_START]
    x = row[CURV_START] + width / 2

    bottom = {"pos": 0, "neg": 0}

    for level, color in enumerate(colors):
        delta = row[delta_pct_name(key, level)]

        if pd.isna(delta) or delta == 0:
            continue

        field = "pos" if delta > 0 else "neg"

        ax.bar(
            x=x,
            width=width,
            bottom=bottom[field],
            height=delta,
            color=color,
            edgecolor=None,
            linewidth=0.2,
        )

        bottom[field] += delta

def merge_old_new(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    pct_cols: list[str],
    keys: list[str],
) -> pd.DataFrame:
    """Fusionne les deux années sur les clés communes."""
    return df_new[
        keys + [PRD, CURV_START, CURV_END] + pct_cols
    ].merge(
        df_old[keys + pct_cols],
        on=keys,
        suffixes=("_new", "_old"),
    )

def setup_delta_axis(ax: Axes) -> None:
    """Ajoute la ligne 0 et fixe l'échelle des deltas."""
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylim(-100, 120)
