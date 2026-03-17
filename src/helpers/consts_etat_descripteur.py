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
    "CLASSE_IQP",
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
    "CLASSE_IQP": DescSpec(
        layer=None,
        column=None,
        category="score",
        gravite_type="str",
    ),
}

DESC_COLORS = [
    "green",
    "#b8dfaf",
    "orange",
    "red",
    "#c77cff",
    "#9b4dca",
    "#6a0dad",
    "#4b0082",
    "#2B002B",
    "#0A000A",
]

DESC_BOOL_COLORS = [
    "green",
    "purple",
]
# Noms colonnes calculées
DESC = "desc"


def level_name(desc_key: str, level: int) -> str:
    """Nom de la colonne niveau i pour un descripteur donné."""
    return f"{DESC}_{desc_key}_{LEVEL}_{level}"

def pct_name(desc_key: str, level: int) -> str:
    """Nom de la colonne % niveau i pour un descripteur donné."""
    return f"{PCT}_{DESC}_{desc_key}_{LEVEL}_{level}"


def colors_for_levels(n_levels: int, desc_key: DescTypes) -> List[str]:
    """
    Retourne une liste de couleurs pour les niveaux.
    Si le descripteur est bool, le niveau 1 (présence) est forcé en purple.
    """
    spec = DESCRIPTEURS[desc_key]

    if spec.gravite_type == "bool":
        return DESC_BOOL_COLORS
    if desc_key == "ORNIERAGE_PETIT_RAYON":
        return ["white"] + DESC_COLORS[1:n_levels]

    return DESC_COLORS[:n_levels]

def legend_patches(desc_key: DescTypes) -> list[mpatches.Patch]:
    """
    Légende: level 0 = tronçon, level 1.. = gravités.
    """
    nlv = DESCRIPTEURS[desc_key].nb_levels
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

CLASSE_IQP_COLORS = {
    "A": "green", "B": "green", "C": "green",
    "D": "yellow", "E": "yellow", "F": "yellow",
    "G": "red", "H": "red", "I": "red",
}

def classe_iqp_color(v: str | None) -> str:
    """Retourne la couleur correspondant à la classe IQP."""
    if pd.isna(v):
        return UNKNOWN_COLOR
    return CLASSE_IQP_COLORS.get(v, UNKNOWN_COLOR)

def classe_iqp_legend_patches():
    """Patches de légende pour la classe IQP."""
    return [
        mpatches.Patch(color="green", label="Niveau 1 : A, B, C"),
        mpatches.Patch(color="yellow", label="Niveau 2 : D, E, F"),
        mpatches.Patch(color="red", label="Niveau 3 : G, H, I"),
    ]
