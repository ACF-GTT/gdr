"""Helpers pour l'analyse des états de surface IQRN 3D"""

from itertools import accumulate

import pandas as pd
from pandas import DataFrame
from pandas import Series
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from helpers.graph_tools import draw_object

from helpers.consts_etat_surface import (
    FILE,
    COLORS,
    ABD,
    PLOD, PLOF,
    ROUTE, DEP, SENS,
    LONGUEUR_TRONCON,
    SURF_EVAL,
    PR_REGEX,
    STATES,
    PRD_NUM, PRF_NUM, PRD, PRF,
    CURV_START, CURV_END,
    FIELDS_SELECTION,
    Y_SCALE, Y_SCALE_W_PR,
    D_SUP,NB_LEVELS,
    MESSAGE_NO_DF,
    level_name,
    pct_name
)

class SurfaceAnalyzer:
    """Classe pour analyser les états """
    def __init__(self, file_path: str) -> None:
        """Initialisation"""
        self.file_path = file_path
        self.df = None
        self.sheet_name : str | None = None


    def load_sheet(self):
        """Charge une feuille"""
        excel_file = pd.ExcelFile(self.file_path)
        print("Feuilles disponibles dans le fichier :")
        for i, sheet in enumerate(excel_file.sheet_names):
            print(f"{i}: {sheet}")

        while True:
            sheet_index = int(input("Entrez le numéro de la feuille à charger : "))
            if 0 <= sheet_index < len(excel_file.sheet_names):
                break
            print("Numéro invalide, réessayez.")

        sheet_name = excel_file.sheet_names[sheet_index]
        self.df = pd.read_excel(self.file_path, sheet_name=sheet_name)
        print(f"Feuille '{sheet_name}' chargée avec succès !")
        self.sheet_name = sheet_name


    def compute_pr(self):
        """Construit les colonnes PRD et PRF à partir de plod/plof """
        assert self.df is not None, MESSAGE_NO_DF

        # Extraction du numéro de PR
        # On est obligé de faire en 2 étapes car sinon PR100<PR11
        # Explication du pattern : n°dep+PR+n°PR+Sens
        self.df[PRD_NUM] = (
            self.df[PLOD]
            .str.extract(PR_REGEX)[1]  # groupe 2 = numéro PR
            .astype("Int64")
        )

        self.df[PRF_NUM] = (
            self.df[PLOF]
            .str.extract(PR_REGEX)[1]
            .astype("Int64")
        )

        # On reconstruit les PR en txt
        self.df[PRD] = self.df[PRD_NUM].apply(
            lambda x: f"PR{int(x)}" if pd.notna(x) else None
        )
        self.df[PRF] = self.df[PRF_NUM].apply(
            lambda x: f"PR{int(x)}" if pd.notna(x) else None
        )


    def compute_levels(self):
        """Calcul des surfaces non cumulées pour chaque état de niveau"""
        assert self.df is not None, MESSAGE_NO_DF

        for state, cols in D_SUP.items():
            for i in range(NB_LEVELS):
                try:
                    levels = self.df[cols[i]] - self.df[cols[i + 1]]
                except IndexError:
                    levels = self.df[cols[i]]
                self.df[level_name(state, i)] = levels



    def compute_percent(self):
        """Calcul des pourcentages par rapport à S_evaluee"""
        assert self.df is not None, MESSAGE_NO_DF

        for state in STATES:
            for level in range(NB_LEVELS):
                self.df[pct_name(state, level)] = (
                    self.df[level_name(state, level)] / self.df[SURF_EVAL] * 100
                )



def filter_order(df: DataFrame|None,ascending: bool = True,**kwargs) -> DataFrame:
    """ Filtre route/dep/sens et ré-ordonne"""
    assert df is not None, MESSAGE_NO_DF
    route = kwargs.get("route", None)
    dep = kwargs.get("dep", None)
    sens = kwargs.get("sens", None)
    prd_num= kwargs.get("prd_num", None)
    if route:
        df = df[df[ROUTE] == route]
    if dep:
        df= df[df[DEP].astype(str).str.strip() == str(dep).strip()]
    if sens:
        df = df[df[SENS] == sens]
    if prd_num:
        df = df[df[PRD_NUM] == prd_num]
    return df.sort_values(by=[PRD_NUM, ABD], ascending=ascending)


def compute_curviligne(df: DataFrame) -> DataFrame:
    """Calcule l'abscisse curviligne total après filtre."""
    assert df is not None, MESSAGE_NO_DF
    df[CURV_END] = df[LONGUEUR_TRONCON].cumsum()
    df[CURV_START] = df[CURV_END] - df[LONGUEUR_TRONCON]
    return df


def graphe_state_section(
    state: str,
    row : Series,
    ax: Axes
) -> None:
    """Trace un état de surface pour un tronçon donné."""
    curv_start = row[CURV_START]
    curv_end = row[CURV_END]
    # width représente la longueur totale du tronçon.
    width = curv_end - curv_start

    percents = [
        Y_SCALE * row[pct_name(state,lvl)] / 100
        for lvl in range(len(COLORS))
    ]
    bottoms  = [0, *accumulate(percents[:-1])]
    ax.bar(
        x=curv_start+width/2,
        width=width,
        bottom=bottoms,
        height=percents,
        color=COLORS
    )

class GraphStates:
    """Classe pour grapher les états de surface IQRN 3D"""
    def __init__(self):
        """initialisation"""
        self.analyzer = SurfaceAnalyzer(FILE)
        self.analyzer.load_sheet()
        self.analyzer.compute_pr()
        self.analyzer.compute_levels()
        self.analyzer.compute_percent()
        self.route = None
        self.dep = None

    def set_route_dep(
        self,
        route: str | None,
        dep: str | None
    ) -> None:
        """fixe route & département"""
        self.route = route
        self.dep = dep

    def graphe_sens(
        self,
        sens: str,
        prd_num: int | None,
        axes: list[Axes]
    ) -> DataFrame:
        """graphes de tous les états pour un sens donné"""
        assert self.route is not None
        assert self.dep is not None
        # Calcul des abscisses curvilignes et filtre
        df_filtered = filter_order(
            df=self.analyzer.df,
            route=self.route,
            dep=self.dep,
            sens=sens,
            prd_num=prd_num
        )
        df_filtered = compute_curviligne(df_filtered)
        print(f"Nombre de lignes après filtrage : {len(df_filtered)}")
        print(df_filtered.loc[:, FIELDS_SELECTION].head(40))

        # Boucle sur chaque état à tracer
        for ax, state in zip(axes, list(STATES.keys())):
            # On parcourt chaque tronçon décrit dans le dataframe filtré.
            ax.tick_params(labelsize=6)
            ax.set_ylabel(STATES[state], fontsize=8)
            for _, row in df_filtered.iterrows():
                # On affiche les PR et les abs_curv
                if row[ABD] == 0:
                    # PR sur l'axe X : n'afficher la barre verticale (draw_object) que
                    # sur le premier sous-graph (axes[0])
                    if ax is axes[0] and row[PRD] is not None:
                        prev_ax = plt.gca() # sauvegarde de l'axe actuel
                        plt.sca(ax)
                        draw_object(
                            label=str(row[PRD]),
                            x_pos=row[CURV_START],
                            ymax=Y_SCALE_W_PR
                        )
                         # on restaure l'axe précédent pour ps planter ls autres graphes
                        plt.sca(prev_ax)
                graphe_state_section(state, row, ax)

            #configuration des 3 ss-graphs
            ax.set_ylim(
                0,
                Y_SCALE_W_PR if ax == axes[0] else Y_SCALE
            )
            ax.grid(visible=True, axis="x", linestyle="--")
            ax.grid(visible=True, axis="y")
            ax.set_title(f"sens {sens}")
        return df_filtered
