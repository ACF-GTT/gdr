"""Classe de base commune aux cinétiques AIGLE3D."""

import matplotlib.pyplot as plt

from helpers.consts import Aigle
from helpers.consts_commun_pr_curv import CURV_START, CURV_END
from helpers.graph_tools import render


class CinetiqueBase:
    """Regroupe les traitements communs aux cinétiques."""

    def __init__(self):
        aigle = Aigle()
        self.route = aigle.route
        self.dep = aigle.dep
        self.sens_list = aigle.sens_list

    def adjust(self, ax, df):
        """Ajuste les limites de l'axe X à partir du DataFrame."""
        if df is not None and not df.empty:
            ax.set_xlim(
                df[CURV_START].min(),
                df[CURV_END].max(),
            )

    def render(self, title: str, file_name: str):
        """Finalise et exporte le graphique."""
        plt.suptitle(title, x=0.01, ha="left")
        plt.tight_layout()
        render(file_name)