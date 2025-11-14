"""
Script d'analyse des états de surface.
Charge un fichier Excel, extrait les PR et calcule les pourcentages de surface par niveau.
"""

#import re, on n'en a pas besoin pour l'instant(pylint beg sinon)
import pandas as pd
#import matplotlib.pyplot as plt , on n'en a pas besoin pour l'instant
from helpers.constante_etat_surface import (
    PLOD, PLOF,
    ROUTE, DEP, SENS,
    SURF_EVAL,
    PRD, PRF, PR_REGEX,
    LONGUEUR_TRONCON,
    ABD,
    #ABF, on n'en a pas besoin pour l'instant
    FILE,
    STATES,
    #COLORS, on n'en a pas besoin pour l'instant
)

class SurfaceAnalyzer:
    """Classe pour analyser les états """
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_sheet(self):
        """    1. Sélection de la feuille"""

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


    def extract_pr(self):
        """ 2. Extraire le numéro de PR à partir de plod/plof """

        self.df.insert(
            loc=0,
            column=PRD,
            value=self.df[PLOD].str.extract(PR_REGEX)
        )

        self.df.insert(
            loc=1,
            column=PRF,
            value=self.df[PLOF].str.extract(PR_REGEX)
        )

    def compute_levels(self):
        """ 3. Calcul des surfaces non cumulées pour chaque état et niveau """

        for state in STATES:
            for i in range(5):
                colonne = f"S_{state}_sup_{i}"
                next_colonne = f"S_{state}_sup_{i+1}" if i < 4 else None
                if next_colonne in self.df.columns:
                    self.df[f"S_{state}_level_{i}"] = self.df[colonne] - self.df[next_colonne]
                else:
                    self.df[f"S_{state}_level_{i}"] = self.df[colonne]

    def compute_percent(self):
        """    4. Calcul des pourcentages par rapport à S_evaluee """

        for state in STATES:
            for i in range(5):
                self.df[f"pct_{state}_level_{i}"] = (
                    self.df[f"S_{state}_level_{i}"] / self.df[SURF_EVAL]
                ) * 100

    def filter(self, route=None, dep=None, sens=None):
        """     5. Filtre Route/SENS/DEP """

        df = self.df
        if route:
            df = df[df[ROUTE] == route]
        if dep:
            df= df[df[DEP].astype(str).str.strip() == str(dep).strip()]
        if sens:
            df = df[df[SENS] == sens]
        return df.sort_values(by=[PRD, ABD], ascending=True)

    def compute_curviligne(self, df):
        """Calcule l'abscisse curviligne après filtre."""
        df = df.copy()
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
    df_filtered = analyzer.filter(route="N0088", dep="43", sens="M")
    df_filtered = analyzer.compute_curviligne(df_filtered)
    print(f"Nombre de lignes après filtrage : {len(df_filtered)}")
    print(df_filtered.loc[:, [PRD, ABD, LONGUEUR_TRONCON, "curv_start", "curv_end"]].head(10))
