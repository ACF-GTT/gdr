"""
Analyse des descripteurs (GPKG) dans la même logique que etat_surface
"""
from itertools import accumulate
from pathlib import Path
from typing import cast

import geopandas as gpd  # type: ignore
import pandas as pd
from geopandas import GeoDataFrame
from matplotlib.axes import Axes
from pandas import DataFrame, Series

from helpers.consts_etat_descripteur import (
    FILE_DESCRIPTEURS, FILE_SURFACE, SHEET_SURFACE,
    DESCRIPTEURS, DescTypes,
    CLE_TRONCON, CLE_TRONCON_LEFT, GraviteValue,
    pct_name, colors_for_levels, cft_color,
)
from helpers.consts_commun_pr_curv import (
    ABD, ABF, LONGUEUR_TRONCON, PLOD, PLOF, ROUTE, DEP, SENS, SURF_EVAL, MESSAGE_NO_DF,
    CURV_START, CURV_END, Y_SCALE,
)
from helpers.consts_etat_surface import SI, CFT_MOYEN
from helpers.iq3d import SurfaceAnalyzer
from helpers.tools_file import CheckConf

# Colonne surfacique dans le GPKG (surface de chaque gravité sur le tronçon)
SHAPE_AREA = "Shape_Area"
SURF_EVAL_TRON = f"{SURF_EVAL}_troncon"


class DescripteurAnalyzer:
    """Classe pour analyser les descripteurs d'état de surface des routes."""

    def __init__(
        self,
        file_path: str | Path = FILE_DESCRIPTEURS,
        surface_xls: str | Path = FILE_SURFACE,
    ) -> None:
        self.file_path = Path(file_path)
        self.surface_xls = Path(surface_xls)

        self.df : GeoDataFrame | None = None
        self.df_troncons : GeoDataFrame | None = None

        # Charger la BONNE feuille Excel
        self.df_surface = pd.read_excel(
            self.surface_xls,
            sheet_name=SHEET_SURFACE
        )

        # On garde uniquement ce qui nous intéresse
        self.df_surface = self.df_surface[
            [CLE_TRONCON, ABD, ABF, LONGUEUR_TRONCON, PLOD, PLOF, ROUTE,
            DEP, SENS, SURF_EVAL,SI,CFT_MOYEN]
        ].copy()

    def load(self, desc_key: DescTypes) -> None:
        """Charge la couche et ajoute les colonnes"""
        if DESCRIPTEURS[desc_key].is_score:
            self.df = None
            return

        layer = DESCRIPTEURS[desc_key].layer
        self.df = gpd.read_file(self.file_path, layer=layer).merge(
            self.df_surface,
            how="left",
            left_on=CLE_TRONCON_LEFT,
            right_on=CLE_TRONCON,
        )

    def _gravite_series(self, desc_key: DescTypes) -> pd.Series:
        """Renvoie une série 'gravite' normalisée (bool -> 'Oui', sinon colonne)."""
        assert self.df is not None, MESSAGE_NO_DF
        spec = DESCRIPTEURS[desc_key]
        if spec.gravite_type == "bool":
            return pd.Series("Oui", index=self.df.index)
        return self.df[spec.column]

    def levels_pct_by_troncon(self, desc_key: DescTypes) -> DataFrame:
        """Retourne: cle_unique_plod + pct_desc_<key>_level_i."""
        assert self.df is not None, MESSAGE_NO_DF
        spec = DESCRIPTEURS[desc_key]

        if SHAPE_AREA not in self.df.columns:
            raise KeyError(
                f"Colonne '{SHAPE_AREA}' absente de la couche GPKG chargée. "
            )

        ordered : list[GraviteValue] = ["Oui"] if spec.gravite_type=="bool" else list(spec.gravites)
        rank_map = {v: i + 1 for i, v in enumerate(ordered)}

        # On gère les surfaces via Shape_Area.
        occ = self.df[[CLE_TRONCON_LEFT, CLE_TRONCON, SURF_EVAL, SHAPE_AREA]].copy()
        occ["rank"] = self._gravite_series(desc_key).map(rank_map)

        # Somme des surfaces par tronçon et par rank (A1, A2, A3... surfaces cumulées >= i)
        areas = (
            occ.groupby([CLE_TRONCON_LEFT, "rank"], dropna=False)[SHAPE_AREA]
            .sum(min_count=1)
            .rename("area_rank")
            .reset_index()
        )

        # Surface totale évaluée par tronçon (100% du tronçon)
        seval = (
            occ.groupby(CLE_TRONCON_LEFT, dropna=False)[SURF_EVAL]
            .first()
            .rename(SURF_EVAL_TRON)
            .reset_index()
        )

        # Pivot des surfaces par rank (une colonne par rank)
        piv = areas.pivot_table(
            index=CLE_TRONCON_LEFT,
            columns="rank",
            values="area_rank",
            aggfunc="sum",
            fill_value=0.0
        )

        n_grav = DESCRIPTEURS[desc_key].nb_levels - 1  # ranks 1..n_grav

        # les surfaces par gravité sont déjà imbriquées (gravité 1 comprend 2 ect...)
        # On calcule les niveaux non cumulés via les différences:
        # level0 = S_evaluee - A1 ainsi de suite
        # last  = A_n

        df_final = pd.DataFrame(index=piv.index)
        df_final = df_final.join(seval.set_index(CLE_TRONCON_LEFT), how="left")

        areas_by_rank = {i: piv[i] if i in piv.columns else 0.0 for i in range(1, n_grav + 1)}

        # Niveau 0
        area_rank_1 = areas_by_rank.get(1, 0.0)
        lvl0_area = df_final[SURF_EVAL_TRON] - area_rank_1
        df_final[pct_name(desc_key, 0)] = lvl0_area / df_final[SURF_EVAL_TRON] * 100

        # Niveaux 1..n
        for i in range(1, n_grav + 1):
            if i < n_grav:
                level_area = (areas_by_rank.get(i, 0.0) - areas_by_rank.get(i + 1, 0.0))
            else:
                level_area = areas_by_rank.get(i, 0.0)
            df_final[pct_name(desc_key, i)] = level_area / df_final[SURF_EVAL_TRON] * 100

        #  si S_evaluee est vide  on affiche en blanc comme les surfaces
        df_final = df_final.drop(columns=[SURF_EVAL_TRON], errors="ignore").reset_index()
        return df_final.rename(columns={CLE_TRONCON_LEFT: CLE_TRONCON})


    def troncons_df(
        self,
        desc_key: DescTypes,
        route: str | None,
        dep: str | None,
        sens: str,
        **kwargs
    ) -> tuple[DataFrame, dict]:
        """Retourne DF tronçons filtré + curviligne + dict PR."""

        tron = self.df_surface[self.df_surface[SENS] == sens].copy()

        if route:
            tron = tron[tron[ROUTE] == route]
        if dep:
            # Comparaison DEP : float d'abord, sinon texte
            try:
                dep_float = float(dep)
                tron = tron[tron[DEP].astype(float) == dep_float]
            except ValueError:
                tron = tron[tron[DEP].astype(str).str.strip() == str(dep).strip()]

        if DESCRIPTEURS[desc_key].is_score:
            # on garde juste la colonne cft_moyen déjà présente dans le troncon (Excel)
            sa = SurfaceAnalyzer(df=tron)
            sa.compute_pr()
            sa.filter(**kwargs)
            return sa.compute_curviligne(sens)

        tron = tron.merge(self.levels_pct_by_troncon(desc_key), on=CLE_TRONCON, how="left")

        nlv = DESCRIPTEURS[desc_key].nb_levels
        pct_cols = [pct_name(desc_key, lvl) for lvl in range(nlv)]

        # Cas 1: S_evaluee vide : on laisse les % à NaN (affichage blanc)
        mask_no_eval = tron[SURF_EVAL].isna()
        tron.loc[mask_no_eval, pct_cols] = float("nan")

        # Cas 2: tronçon évalué mais aucune donnée du descripteur -> 100% niveau 0, 0% le reste
        mask_eval = tron[SURF_EVAL].notna()
        mask_no_desc = tron[pct_name(desc_key, 0)].isna() & mask_eval
        tron.loc[mask_no_desc, pct_name(desc_key, 0)] = 100.0
        tron.loc[mask_no_desc, [pct_name(desc_key, lvl) for lvl in range(1, nlv)]] = 0.0

        # Cas 3: tronçon évalué -> les niveaux de gravités pas remplis = "0% à ce niveau"
        tron.loc[mask_eval, pct_cols] = tron.loc[mask_eval, pct_cols].fillna(0.0)

        sa = SurfaceAnalyzer(df=tron)
        sa.compute_pr()
        sa.filter(**kwargs)
        return sa.compute_curviligne(sens)


def graphe_desc_section(desc_key: DescTypes, row: Series, ax: Axes) -> None:
    """Trace la barre empilée pour un tronçon (niveaux 0..N)."""
    curv_start = row[CURV_START]
    curv_end = row[CURV_END]
    width = curv_end - curv_start

    # Cas spécial CFT_MOYEN (Excel)
    # une seule barre, hauteur = valeur cft_moyen
    if DESCRIPTEURS[desc_key].is_score :
        v = row.get(CFT_MOYEN, float("nan"))
        ax.bar(
            x=curv_start + width / 2,
            width=width,
            bottom=0,
            height=float(v) if pd.notna(v) else 0.0,
            color=cft_color(v),
        )
        return

    nlv = DESCRIPTEURS[desc_key].nb_levels
    cols = colors_for_levels(nlv, desc_key=desc_key)

    heights = [
        Y_SCALE * row[pct_name(desc_key, lvl)] / 100
        for lvl in range(nlv)
    ]
    bottoms = [0, *accumulate(heights[:-1])]

    ax.bar(
        x=curv_start + width / 2,
        width=width,
        bottom=bottoms,
        height=heights,
        color=cols,
    )



def get_configured_descriptors(conf: CheckConf) -> list[DescTypes]:
    """Retourne la liste des descripteurs à afficher, selon la config."""
    raw = conf.get_descripteurs_raw()

    if raw is None:
        return list(DESCRIPTEURS.keys())

    return [cast(DescTypes, d) for d in raw if d in DESCRIPTEURS]
