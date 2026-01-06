"""
Module pour analyser les descripteurs d'état de gravité des routes.
Logique identique à iq3d : self.df est l'état central.
"""
from pathlib import Path
import geopandas as gpd  # type: ignore
import pandas as pd

from helpers.consts_etat_descripteur import (
    FILE_DESCRIPTEURS,
    FILE_SURFACE,
    DESCRIPTEURS,
    DescTypes
)
from helpers.iq3d import SurfaceAnalyzer


class DescripteurAnalyzer:
    """Classe pour analyser les descripteurs d'état de surface des routes."""

    def __init__(
        self,
        file_path: str | Path = FILE_DESCRIPTEURS,
        surface_xls: str | Path = FILE_SURFACE,
        df: pd.DataFrame | None = None
    ) -> None:
        """Initialisation (même logique que SurfaceAnalyzer)"""
        self.file_path = Path(file_path)
        self.surface_xls = Path(surface_xls)
        self.df: pd.DataFrame | None = df
        self.df_counts: pd.DataFrame | None = None

        # Table de référence tronçons
        self.df_surface = pd.read_excel(self.surface_xls)

        # On garde uniquement ce qui nous intéresse
        self.df_surface = self.df_surface[
            [
                "cle_unique_plod",
                "abs_debut",
                "abs_fin",
                "longueur_troncon",
                "plod",
                "plof",
                "route",
                "sectionnement_departement",
                "sens",
            ]
        ]

    # 1. Lecture des couches
    def load_layer(self, descripteur_key: DescTypes) -> None:
        """
        Charge une couche GPKG et l'affecte à self.df
        """
        layer_name = DESCRIPTEURS[descripteur_key]["layer"]
        self.df = gpd.read_file(self.file_path, layer=layer_name)

    # 2. Enrichissement des données
    def enrich_with_surface_infos(self) -> None:
        """
        Ajoute abs_debut, abs_fin, longueur_troncon, plod, plof, etc.
        depuis la table Excel état de surface
        """
        assert self.df is not None, "Pas de DataFrame, impossible de continuer"

        self.df = self.df.merge(
            self.df_surface,
            how="left",
            left_on="cle_troncon_plod",
            right_on="cle_unique_plod"
        )

    # 3. Normalisation de la gravité
    def compute_gravite(self, descripteur_key: DescTypes) -> None:
        """
        Crée la colonne 'gravite' selon le type du descripteur
        """
        assert self.df is not None, "Pas de DataFrame, impossible de continuer"

        descripteur = DESCRIPTEURS[descripteur_key]

        if descripteur["gravite_type"] == "bool":
            # Présence simple (Delamination, Macrotexture)
            self.df["gravite"] = "Oui"
        else:
            self.df["gravite"] = self.df[descripteur["column"]]

    # 4. Comptage des occurrences par gravité et tronçon
    def count_gravite_par_troncon(self) -> None:
        """
        Compte le nombre d'occurrences de chaque gravité par tronçon.
        Résultat stocké dans self.df
        """
        assert self.df is not None, "Pas de DataFrame, impossible de continuer"

        self.df_counts = (
            self.df
            .groupby(["cle_troncon_plod", "gravite"])
            .size()
            .reset_index(name="count")
        )

        self.df_counts["total"] = (
            self.df_counts.groupby("cle_troncon_plod")["count"]
            .transform("sum")
        )
        self.df_counts["pct"] = (
            self.df_counts["count"] / self.df_counts["total"] * 100
        )


    # 5. Calcul PR et curviligne (réutilisation iq3d)
    def compute_pr_curviligne(
        self,
        sens: str
    ) -> dict[str, float]:
        """
        Réutilise compute_pr et compute_curviligne depuis SurfaceAnalyzer de iq3d
        """
        assert self.df is not None, "Pas de DataFrame, impossible de continuer"

        sa = SurfaceAnalyzer(df=self.df)
        sa.compute_pr()
        self.df, curv_prs_values = sa.compute_curviligne(sens)
        return curv_prs_values


if __name__ == "__main__":

    analyzer = DescripteurAnalyzer()

    analyzer.load_layer("ORNIERAGE_GRAND_RAYON")
    analyzer.enrich_with_surface_infos()
    analyzer.compute_gravite("ORNIERAGE_GRAND_RAYON")
    analyzer.count_gravite_par_troncon()

    # PR + curviligne
    curv_prs = analyzer.compute_pr_curviligne(sens="P")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    assert analyzer.df is not None
    print(analyzer.df.head())
    print(analyzer.df_counts)
