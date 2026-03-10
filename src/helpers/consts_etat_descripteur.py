"""Constantes décrivant les couches, colonnes, types et niveaux des descripteurs
extraits depuis le fichier GPKG ou XLSX.
"""
from dataclasses import dataclass, field
from typing import Literal, List
import pandas as pd
import matplotlib.patches as mpatches
from helpers.tools_file import parent_dir, CheckConf
from helpers.consts_commun_pr_curv import LEVEL, PCT
from helpers.consts import (
    COLORS as METRIC_COLORS,
    UNKNOWN_COLOR,
    get_color,
    LEGENDS,
)

DATAS = f"{parent_dir(__file__, 2)}/datas/"

# Nom du fichier source (GPKG)
conf = CheckConf()

FILE_DESCRIPTEURS = f"{DATAS}/{conf.get('aigle_gpkg')}"
FILE_SURFACE = f"{DATAS}/{conf.get('aigle_xls')}"
SHEET_SURFACE = conf.get("aigle_sheet")

# Colonnes de ref "surface"
CLE_TRONCON = "cle_unique_plod"
CLE_TRONCON_LEFT = "cle_troncon_plod"  # côté gpkg


# Définition des descripteurs et de leurs caractéristiques
DescWeights = Literal[
    "DELAMINATION",
    "DENSITE_FISSURATION",
    "MACROTEXTURE",
    "EPO", "EMO",
    "ESTEX",
    "RAVELING",
    "ORNIERAGE_GRAND_RAYON", "ORNIERAGE_PETIT_RAYON",
]
DescScores = Literal[
    "CFT_MOYEN",
]

DescTypes = DescWeights | DescScores
DescCategory = Literal["weight", "score"]
GraviteType = Literal["bool", "int", "str"]
GraviteValue = int | str


@dataclass
class DescSpec:
    """Spécification d'un descripteur."""
    layer: str | None
    column: str | None
    category: DescCategory
    gravite_type: GraviteType
    gravites: list[GraviteValue] = field(default_factory=list)

    @property
    def is_score(self) -> bool:
        """Retourne True si le descripteur est un score brut."""
        return self.category == "score"

    @property
    def is_weight(self) -> bool:
        """Retourne True si le descripteur est un poids / ratio."""
        return self.category == "weight"

    @property
    def nb_levels(self) -> int:
        """Niveaux au total = 1 (niveau 0) + nb gravités."""
        if self.gravite_type == "bool":
            return 2
        return 1 + len(self.gravites)


DESCRIPTEURS: dict[DescTypes, DescSpec] = {
    "DELAMINATION": DescSpec(
        layer="Descr_final_Delamination_2025 — DIRMC",
        column=None,                # Pas de gravité = présent/absent
        category="weight",
        gravite_type="bool",
    ),

    "DENSITE_FISSURATION": DescSpec(
        layer="Descr_gravite_Densite_Fissuration_2025 — DIRMC",
        column="niveau_gravite",
        category="weight",
        gravite_type="int",
        gravites=[
            1, 2, 3, 4
        ]
    ),

    "MACROTEXTURE": DescSpec(
        layer="Descr_final_Macrotexture_Fermee_2025 — DIRMC",
        column=None,
        category="weight",
        gravite_type="bool",
    ),

    "EPO": DescSpec(
        layer="Descr_gravite_EPO_2025 — DIRMC",
        column="niveau_gravite_str",
        category="weight",
        gravite_type="str",
        gravites=[
            "0,25 cm3", "0,50 cm3", "1,00 cm3", "4,00 cm3"
        ]
    ),

    "EMO": DescSpec(
        layer="Descr_gravite_EMO_2025 — DIRMC",
        column="niveau_gravite_str",
        category="weight",
        gravite_type="str",
        gravites=[
            "02,5 cm3", "05,0 cm3", "07,5 cm3", "10,0 cm3", "20,0 cm3", "25,0 cm3", "40,0 cm3"
        ]
    ),

    "ESTEX": DescSpec(
        layer="Descr_gravite_eSTex_2025 — DIRMC",
        column="niveau_gravite_str",
        category="weight",
        gravite_type="str",
        gravites=[
            "0,025 cm3", "0,050 cm3", "0,100 cm3", "0,250 cm3"
        ]
    ),
    "RAVELING": DescSpec(
        layer="Descr_gravite_Raveling_2025 — DIRMC",
        column="niveau_gravite_str",
        category="weight",
        gravite_type="str",
        gravites=[
            "080 cm3/m2", "120 cm3/m2", "150 cm3/cm", "250 cm3/m2", "500 cm3/m2", "750 cm3/m2"
        ]
    ),
    "ORNIERAGE_GRAND_RAYON": DescSpec(
        layer="Descr_gravite_Orniere_Grand_Rayon_2025 — DIRMC",
        column="niveau_gravite_str",
        category="weight",
        gravite_type="str",
        gravites=[
            "07 mm", "10 mm", "15 mm", "20 mm", "25 mm", "30 mm"
        ]
    ),
    "ORNIERAGE_PETIT_RAYON": DescSpec(
        layer="Descr_gravite_Orniere_Petit_Rayon_2025 — DIRMC",
        column="niveau_gravite_str",
        category="weight",
        gravite_type="str",
        gravites=[
            "07 mm", "10 mm", "15 mm", "20 mm"
        ]
    ),
    "CFT_MOYEN": DescSpec(
        layer=None,
        column=None,
        category="score",
        gravite_type="int",
    ),
}

DESC_COLORS = [
    "green",
    "#b8dfaf",
    "orange",
    "red",
]

DESC_BOOL_COLOR = "purple"

DESC_EXTRA_COLORS = [
    "#c77cff",
    "#9b4dca",
    "#6a0dad",
    "#4b0082",
    "#2B002B",
    "#0A000A",
]


# Noms colonnes calculées
DESC = "desc"
def is_score(desc_key: DescTypes) -> bool:
    """Retourne True si le descripteur est un score brut."""
    return DESCRIPTEURS[desc_key].is_score

def is_weight(desc_key: DescTypes) -> bool:
    """Retourne True si le descripteur est un poids / ratio."""
    return DESCRIPTEURS[desc_key].is_weight


def level_name(desc_key: str, level: int) -> str:
    """Nom de la colonne niveau i pour un descripteur donné."""
    return f"{DESC}_{desc_key}_{LEVEL}_{level}"

def pct_name(desc_key: str, level: int) -> str:
    """Nom de la colonne % niveau i pour un descripteur donné."""
    return f"{PCT}_{DESC}_{desc_key}_{LEVEL}_{level}"

# spec pour le type DescTypes
def nb_levels(desc_key: DescTypes) -> int:
    """Niveaux au total = 1 (niveau 0) + nb gravités."""
    return DESCRIPTEURS[desc_key].nb_levels

def colors_for_levels(n_levels: int, desc_key: DescTypes | None = None) -> List[str]:
    """
    Retourne une liste de couleurs pour les niveaux.
    Si le descripteur est bool, le niveau 1 (présence) est forcé en purple.
    """
    if n_levels <= len(DESC_COLORS):
        cols = DESC_COLORS[:n_levels]
    else:
        cols = DESC_COLORS[:4]

        # On ajoute des nuances de purple si besoin
        needed = n_levels - 4
        cols.extend(DESC_EXTRA_COLORS[:needed])

    # couleur purple pour bool
    if desc_key is not None:
        spec = DESCRIPTEURS.get(desc_key)
        if spec and spec.gravite_type == "bool" and len(cols) > 1:
            cols[1] = DESC_BOOL_COLOR

    return cols

def legend_patches(desc_key: DescTypes) -> list[mpatches.Patch]:
    """
    Légende: level 0 = tronçon, level 1.. = gravités.
    """
    nlv = nb_levels(desc_key)
    cols = colors_for_levels(nlv, desc_key=desc_key)
    spec = DESCRIPTEURS[desc_key]

    labels: list[str] = ["Niveau 0 (tronçon)"]
    if spec.gravite_type == "bool":
        labels.append(">=1 (présence)")
    else:
        labels.extend([
            f">={g}" if not str(g).startswith(">=") else str(g)
            for g in spec.gravites
        ])

    return [mpatches.Patch(color=cols[i], label=labels[i]) for i in range(nlv)]

# CFT MOYEN (Excel)



def cft_color(v: float) -> str:
    """Retourne la couleur correspondant au CFT moyen."""
    if pd.isna(v):
        return UNKNOWN_COLOR
    return get_color(float(v), unit="CFT")


def cft_legend_patches():
    """Patches de légende pour le CFT."""
    return [
        mpatches.Patch(color=METRIC_COLORS["CFT"][level], label=label)
        for level, label in LEGENDS["CFT"].items()
    ]
