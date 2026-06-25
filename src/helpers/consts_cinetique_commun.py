"""Fonctions communes aux cinétiques."""

import pandas as pd

from helpers.consts_commun_pr_curv import CURV_START, CURV_END, PRD, Y_SCALE_W_PR
from helpers.graph_tools import draw_object


def draw_prs(prs: dict, ax) -> None:
    """Affiche les PR."""
    for pr, curv in prs.items():
        draw_object(pr, curv, Y_SCALE_W_PR, ax)


def draw_delta(row, key, delta_name, colors, n_levels, ax) -> None:
    """Trace les deltas positifs/négatifs empilés."""
    width = row[CURV_END] - row[CURV_START]
    x = row[CURV_START] + width / 2

    bottom_pos = 0
    bottom_neg = 0

    for level in range(n_levels):
        delta = row[delta_name(key, level)]

        if pd.isna(delta) or delta == 0:
            continue

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
            color=colors[level],
            edgecolor=None,
            linewidth=0.2,
        )

def merge_old_new(df_old, df_new, pct_cols, keys):
    """Fusionne les deux années sur les clés communes."""
    return df_new[
        keys + [PRD, CURV_START, CURV_END] + pct_cols
    ].merge(
        df_old[keys + pct_cols],
        on=keys,
        suffixes=("_new", "_old"),
    )

def setup_delta_axis(ax) -> None:
    """Ajoute la ligne 0 et fixe l'échelle des deltas."""
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylim(-100, 120)
