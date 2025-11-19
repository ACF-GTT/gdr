"""
Script d'analyse des états de surface.
Charge un fichier Excel, extrait les PR et calcule les pourcentages de surface par niveau.
"""
from itertools import accumulate

import pandas as pd
import matplotlib.pyplot as plt
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

class SurfaceAnalyzer:
    """Classe pour analyser les états """
    def __init__(self, file_path: str) -> None:
        """Initialisation"""
        self.file_path = file_path
        self.df = None
        self.sheet_name : str | None = None


    def load_sheet(self):
        """charge une feuille"""
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
        """ 2. Extraire le numéro de PR à partir de plod/plof """
        assert self.df is not None, "La feuille doit être chargée."

        # Extraction du numéro de PR
        # On est onligé de faire en 2 étapes car sinon PR100<PR11
        # Explication du pattern : n°dep+PR+n°PR+Sens
        self.df["prd_num"] = (
            self.df[PLOD]
            .str.extract(PR_REGEX)[1]  # groupe 2 = numéro PR
            .astype("Int64")
        )

        self.df["prf_num"] = (
            self.df[PLOF]
            .str.extract(PR_REGEX)[1]
            .astype("Int64")
        )

        # On reconstruit les PR en txt
        self.df[PRD] = self.df["prd_num"].apply(lambda x: f"PR{int(x)}" if pd.notna(x) else None )
        self.df[PRF] = self.df["prf_num"].apply(lambda x: f"PR{int(x)}" if pd.notna(x) else None )


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


    def filter(self, route=None, dep=None, sens=None, prd_num=None):
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
            df = df[df["prd_num"] == prd_num]
        return df.sort_values(by=["prd_num", ABD], ascending=True)


    def compute_curviligne(self, df):
        """Calcule l'abscisse curviligne après filtre."""
        assert df is not None, "Le DataFrame doit être fourni pour calculer l'abscisse curviligne."
        df["curv_start"] = df[LONGUEUR_TRONCON].cumsum() - df[LONGUEUR_TRONCON]
        df["curv_end"] = df[LONGUEUR_TRONCON].cumsum()
        return df


if __name__ == "__main__":
    analyzer = SurfaceAnalyzer(FILE)

    # Charger la feuille
    analyzer.load_sheet()

    # Extraction PR
    analyzer.extract_pr()

    # Calcul des surfaces par niveau
    analyzer.compute_levels()

    # Calcul des pourcentages
    analyzer.compute_percent()

    # Calcul des abscisses curvilignes et filtre
    df_filtered = analyzer.filter(route="N0122", dep="15", sens="P", prd_num=123)
    df_filtered = analyzer.compute_curviligne(df_filtered)
    print(f"Nombre de lignes après filtrage : {len(df_filtered)}")
    print(df_filtered.loc[:, [PRD, ABD, LONGUEUR_TRONCON, "curv_start", "curv_end"]].head(40))

    # 3 graphiques pour 3 niveaux d'états
    #sharex vaut true pour partager l'axe x
    fig, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(15, 6),
        sharex=True,
        gridspec_kw={'hspace': 0.2}
    )

    # Boucle sur chaque état à tracer
    for ax, state in zip(axes, list(STATES.keys())):
        # On parcourt chaque tronçon décrit dans le dataframe filtré.
        for idx, row in df_filtered.iterrows():
            curv_start = row["curv_start"]
            curv_end = row["curv_end"]
            # width représente la longueur totale du tronçon.
            width = curv_end - curv_start

            # On affiche les PR et les abs_curv
            if row[ABD] == 0:
                # PR sur l'axe X : n'afficher la barre verticale (draw_object) que
                # sur le premier sous-graph (axes[0])
                if ax is axes[0] and row[PRD] is not None:
                    prev_ax = plt.gca() # sauvegarde de l'axe actuel
                    plt.sca(ax)
                    draw_object(str(row[PRD]), curv_start, 1)
                    plt.sca(prev_ax) # on restaure l'axe précédent pour ps planter ls autres graphes

            percents = [
                row[f"pct_{state}_level_{lvl}"] / 100
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

        #configuration des 3 ss-graphs
        ax.set_ylim(0, 1)
        ax.grid(visible=True, axis="x", linestyle="--")
        ax.grid(visible=True, axis="y")
        ax.set_title(STATES[state])

    # Axe X partagé
    axes[-1].set_xlim(df_filtered["curv_start"].min(), df_filtered["curv_end"].max())

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
    assert analyzer.sheet_name is not None
    plt.suptitle(analyzer.sheet_name)
    plt.show()
