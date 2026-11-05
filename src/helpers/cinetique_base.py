"""Classe de base commune aux cinétiques AIGLE3D."""
import re

import matplotlib.pyplot as plt

from helpers.tools_file import CheckConf
from helpers.consts_commun_pr_curv import CURV_START, CURV_END
from helpers.graph_tools import render


class CinetiqueBase:
    """Regroupe les traitements communs aux cinétiques."""

    def __init__(self) -> None:
        self.route: str = CheckConf().yaml.get("aigle_route", "N0088")
        self.dep: str = CheckConf().yaml.get("aigle_dep", 43)
        self.sens_list: str = CheckConf().yaml.get("aigle_sens", ["P"])
        self.section: dict = CheckConf().yaml.get("section", {})

    @staticmethod
    def adjust_range(ax, df, text_helper):
        """Ajuste l'axe X."""
        if df is None:
            return
        if df.empty:
            return
        if CheckConf().yaml.get("force_range") == "pr_abs":
            text_helper.adjust(ax)
        else:
            ax.set_xlim(
                df[CURV_START].min(),
                df[CURV_END].max(),
            )

    def render(self, suffix: str, name1: str, name2: str):
        """render to screen or save to disk"""
        years = []
        for name in [name1, name2]:
            match = re.search(r"\d+", name)
            if match:
                years.append(match.group())
        title = f"{suffix}_{'_'.join(years)}_{self.route}_dpt_{self.dep}"
        plt.suptitle(
            title,
            x=0.01,
            ha="left"
        )
        plt.tight_layout()
        # si l'enregistrement est activé dans le yml
        # on repart de title pour former le nom de fichier d'enregistrement
        file_name = f"{title}_PR_{self.section.get('prd')}_A_{self.section.get('prf')}"
        render(file_name)
