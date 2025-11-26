"""Module pour analyser les descripteurs d'état de gravité des routes."""
from pathlib import Path
import geopandas as gpd #type: ignore
import fiona #type: ignore
import pandas as pd
from helpers.constante_descripteur import generate_palette
from helpers.constante_descripteur import FILE_DESCRIPTEURS
from helpers.constante_descripteur import (
    DESCRIPTEURS,
    CLE_TRONCON_REGEX,
    ROUTE, DEP, SENS,
    PRD, ABD,
    CLE_TRONCON_PLOD,
)


class DescripteurAnalyzer:
    """Classe pour analyser les descripteurs """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    #  1. Lecture générique des couches
    def load_layer(self, layer_name: str) -> gpd.GeoDataFrame:
        """Charge une couche GPKG """
        return gpd.read_file(self.file_path, layer=layer_name)

    # 2. Extraction de ROUTE / SENS / DEP / PRD / ABD depuis la clef tronçon
    def extract_troncon_infos(self, df: gpd.GeoDataFrame) -> pd.DataFrame :
        "Extrait les infos tronçon depuis la colonne cle_troncon_plod"
        # Utilisation de str.extract avec le regex
        extracted = df[CLE_TRONCON_PLOD].str.extract(CLE_TRONCON_REGEX)

        # Création des colonnes finales
        df_infos = pd.DataFrame({
            ROUTE: extracted["route"],
            DEP: extracted["dep"],
            PRD: extracted["pr"],
            SENS: extracted["sens"],
            ABD: extracted["abd"]
        })

        return pd.concat([df, df_infos], axis=1)


    #3. comptage des occurrences par gravité

    def count_gravite_par_troncon(self, descripteur_key: str) -> pd.DataFrame:
        """
        Compte le nombre d'occurrences de chaque gravité par tronçon.
        Retourne un DataFrame avec colonnes :
        cle_troncon_plod | gravite | count
        """
        descripteur = DESCRIPTEURS[descripteur_key]

        #  Charger la couche et extraire les infos tronçon
        gdf = self.load_layer(descripteur["layer"])
        df = self.extract_troncon_infos(gdf) #ajout des colonnes tronçon

        # Déterminer la colonne gravité
        if descripteur["gravite_type"] == "bool":
            df["gravite"] = "Oui" # présence de MacroTexture ou Delamination
        else:
            df["gravite"] = df[descripteur["column"]]

        # Comptage par tronçon et gravité
        df_count = df.groupby(["cle_troncon_plod", "gravite"]).size().reset_index(name="count")

        return df_count

    def get_gravity_colors(self, descripteur_key):
        """
        Associe chaque niveau de gravité à une couleur.
        """

        levels = DESCRIPTEURS[descripteur_key]["gravites"]

        # Cas bool → uniquement "Oui"
        if len(levels) == 0:
            return {"Oui": "purple"}

        palette = generate_palette(len(levels))
        return {level: palette[i] for i, level in enumerate(levels)}

if __name__ == "__main__":

    print("Démarrage de l'analyse des descripteurs...\n")
    analyzer = DescripteurAnalyzer(FILE_DESCRIPTEURS)

    # Test : lister les couches
    print("Couches disponibles dans le GPKG :")
    for layer in fiona.listlayers(FILE_DESCRIPTEURS):
        print(" -", layer)

    # Chargement de la couche
    df_test = analyzer.load_layer(DESCRIPTEURS["ORNIERAGE_GRAND_RAYON"]["layer"])
    print("\nAperçu du descripteur brut :")

    # Affichage de toutes les colonnes
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    print(df_test.head())

    # --- Extraction des infos tronçon ---
    print("\nExtraction des infos ROUTE / DEP / PRD / SENS / ABD :")
    df_test_infos = analyzer.extract_troncon_infos(df_test)

    print("\nAperçu du descripteur avec les colonnes tronçon :")
    print(df_test_infos.head(20))

    # --- Comptage des occurrences par gravité ---
    print("\nComptage des niveaux de gravité par tronçon :")
    df_counts = analyzer.count_gravite_par_troncon("ORNIERAGE_GRAND_RAYON")
    print(df_counts.head(20))
