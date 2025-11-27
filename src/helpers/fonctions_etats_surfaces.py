"""
Fonctions utilitaires pour l'analyse des états de surface.
"""

def compute_levels(df, states):
    """
    Calcule les surfaces par niveau :
    S_level_n = S_sup_n - S_sup_{n+1}
    """
    for st in states:
        for level_index in range(5):
            col = f"S_{st}_sup_{level_index}"
            next_col = f"S_{st}_sup_{level_index+1}" if level_index < 4 else None

            df[f"S_{st}_level_{level_index}"] = (
                df[col] - df[next_col] if next_col in df.columns else df[col]
            )
    return df


def compute_percent(df, states, surf_col="S_evaluee"):
    """
    Calcule les pourcentages par rapport à la surface évaluée.
    """
    for st in states:
        for level_index in range(5):
            df[f"pct_{st}_level_{level_index}"] = (
                df[f"S_{st}_level_{level_index}"] / df[surf_col]
            ) * 100
    return df


def compute_curviligne(df, length_col="longueur_troncon"):
    """
    Ajoute les colonnes CURV_START / CURV_END au dataframe filtré.
    """
    df["curv_start"] = df[length_col].cumsum() - df[length_col]
    df["curv_end"] = df[length_col].cumsum()
    return df
