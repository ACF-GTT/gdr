"""
Script d'analyse des états de surface.
Charge un fichier Excel, extrait les PR et calcule les pourcentages de surface par niveau.
"""
from itertools import accumulate

import pandas as pd
from pandas import DataFrame
from pandas import Series
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import matplotlib.patches as mpatches

from generate_si import draw_object
from helpers.constante_etat_surface import (
    PLOD, PLOF,
    ROUTE, DEP, SENS,
    SURF_EVAL,
    PRD, PRF, PR_REGEX,
    LONGUEUR_TRONCON,
    ABD,
    FILE,
    STATES,
    COLORS
)

STATES = {
    "ies": "SURFACE",
    "iep": "PROFOND",
    "ietp": "TRES PROFOND"
}
Y_SCALE = 100
Y_SCALE_W_PR = 120
CURV_START = "curv_start"
CURV_END = "curv_end"

FIELDS_SELECTION = [
    PRD,
    ABD,
    LONGUEUR_TRONCON,
    CURV_START,
    CURV_END
]
PRD_NUM = "prd_num"
PRF_NUM = "prf_num"
SENS_LIST = ["P", "M"]


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


    def extract_pr(self):
        """Construit les colonnes PRD et PRF à partir de plod/plof """
        assert self.df is not None, "La feuille doit être chargée."

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
        """ 3. Calcul des surfaces non cumulées pour chaque état et niveau """
        assert self.df is not None, "La feuille doit être chargée avant de calculer les niveaux."

        for st in STATES:
            for level_index in range(5):
                colonne = f"S_{st}_sup_{level_index}"
                next_colonne = f"S_{st}_sup_{level_index+1}" if level_index < 4 else None
                if next_colonne in self.df.columns:
                    self.df[f"S_{st}_level_{level_index}"] = self.df[colonne]-self.df[next_colonne]
                else:
                    self.df[f"S_{st}_level_{level_index}"] = self.df[colonne]


    def compute_percent(self):
        """ 4. Calcul des pourcentages par rapport à S_evaluee """
        assert self.df is not None, "La feuille doit être chargée avant de calculer les %"

        for st in STATES:
            for level_index in range(5):
                self.df[f"pct_{st}_level_{level_index}"] = (
                    self.df[f"S_{st}_level_{level_index}"] / self.df[SURF_EVAL]
                ) * 100


    def filter(self, route=None, dep=None, sens=None, prd_num=None) -> DataFrame:
        """ 5. Filtre Route/SENS/DEP """
        assert self.df is not None, "La feuille doit être chargée avant de filtrer les données."

        df = self.df
        if route:
            df = df[df[ROUTE] == route]
        if dep:
            df= df[df[DEP].astype(str).str.strip() == str(dep).strip()]
        if sens:
            df = df[df[SENS] == sens]
        if prd_num:
            df = df[df[PRD_NUM] == prd_num]
        return df.sort_values(by=[PRD_NUM, ABD], ascending=True)


    def compute_curviligne(self, df: DataFrame) -> DataFrame:
        """Calcule l'abscisse curviligne après filtre."""
        assert df is not None, "Le DataFrame doit être fourni pour calculer l'abscisse curviligne."
        df[CURV_START] = df[LONGUEUR_TRONCON].cumsum() - df[LONGUEUR_TRONCON]
        df[CURV_END] = df[LONGUEUR_TRONCON].cumsum()
        return df


def graphe_state_section(
    state: str,
    row : Series,
    ax: Axes
) -> None:
    """for a given state, lets graph a single section"""
    curv_start = row[CURV_START]
    curv_end = row[CURV_END]
    # width représente la longueur totale du tronçon.
    width = curv_end - curv_start

    percents = [
        Y_SCALE * row[f"pct_{state}_level_{lvl}"] / 100
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
    """grapher helper for IQRN states"""
    def __init__(self):
        """initialisation"""
        self.analyzer = SurfaceAnalyzer(FILE)
        self.analyzer.load_sheet()
        self.analyzer.extract_pr()
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
        df_filtered = self.analyzer.filter(
            route=self.route,
            dep=self.dep,
            sens=sens,
            prd_num=prd_num
        )
        df_filtered = self.analyzer.compute_curviligne(df_filtered)
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


def main(
    route: str,
    dep: str,
    sens_list: list[str],
    prd_num: int | None = None
) -> None:
    """main"""
    # 3 graphiques pour 3 niveaux d'états
    #sharex vaut true pour partager l'axe x
    for sens in sens_list:
        assert sens in SENS_LIST
    nbg_per_sens = 3
    nbrows = nbg_per_sens * len(sens_list)
    fig, axes = plt.subplots(
        nrows=nbrows,
        ncols=1,
        figsize=(15, 6),
        sharex=True,
        gridspec_kw={'hspace': 0.5}
    )
    plt.rcParams.update({'font.size': 6})

    grapher = GraphStates()
    grapher.set_route_dep(route=route, dep=dep)
    index = 0
    for sens in sens_list:
        sub_axes = axes[index : index + nbg_per_sens]
        index += nbg_per_sens
        df_filtered = grapher.graphe_sens(
            sens=sens,
            prd_num=prd_num,
            axes=sub_axes
        )

        # Axe X partagé
        axes[-1].set_xlim(
            df_filtered[CURV_START].min(),
            df_filtered[CURV_END].max()
        )

    # LÉGENDE DES NIVEAUX
    patches = [
        mpatches.Patch(color=color, label=f">={lvl}")
        for lvl, color in enumerate(COLORS)
    ]

    fig.legend(
        handles=patches,
        loc="upper right",
        ncol=5,)

    plt.tight_layout()
    assert grapher.analyzer.sheet_name is not None
    plt.suptitle(f"{grapher.analyzer.sheet_name} - {route} - dpt {dep}")
    plt.show()

if __name__ == "__main__":
    main(
        route="N0088",
        dep="43",
        sens_list=["M", "P"],
        prd_num=None
    )
