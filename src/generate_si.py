"""Traitement des fichiers du griptester MK2.
sous la forme de schémas itinéraires SI
"""
import argparse
from collections import defaultdict
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from helpers.consts import (
    CFT_COLORS,
    CFT_POOR,
    CFT_GOOD,
    CFT_EXCELLENT,
    PMP_COLORS,
    PMP_POOR,
    PMP_GOOD
)
from helpers.shared import pick_files, which_measure
from helpers.apo import get_apo_datas
from helpers.grip import get_grip_datas
from helpers.road_mesure import RoadMeasure, START, END

COLORS = {
    "CFT": CFT_COLORS,
    "PMP": PMP_COLORS
}

LEGENDS = {
    "CFT": {
        "poor": f"CFT<={CFT_POOR}",
        "fine": f"{CFT_POOR}<CFT<={CFT_GOOD}",
        "good": f"{CFT_GOOD}<CFT<={CFT_EXCELLENT}",
        "excellent": f"CFT>{CFT_EXCELLENT}"
    },
    "PMP" : {
        "poor": f"PMP<={PMP_POOR}",
        "fine": f"{PMP_POOR}<PMP<={PMP_GOOD}",
        "good": f"PMP>{PMP_GOOD}"
    }
}

EVE_STD = {
    "font": "red",
    "line": "blue",
    "bbox": {
        "boxstyle": "round",
        "edgecolor": "gray",
        "facecolor": "white"
    }
}
EVE_COLORS: dict[str, dict] = defaultdict(lambda: EVE_STD)
EVE_COLORS["D"] = {
    "font": "white",
    "line": "green",
    "bbox": {
        "boxstyle": "round",
        "edgecolor": "none",
        "facecolor": "green"
    }
}
EVE_COLORS["F"] = {
    "font": "white",
    "line": "red",
    "bbox": {
        "boxstyle": "round",
        "edgecolor": "none",
        "facecolor": "red"
    }
}

PRECISION = {
    100: 0,
    1: 2
}

# pas en mètres pour une analyse en zône homogène
MEAN_STEP = 200


def color_map(y_data: list[float], unit="CFT"):
    """Crée le tableau des couleurs pour l'histogramme."""
    if unit=="PMP":
        return list(
            map(
                lambda val:
                    PMP_COLORS["poor"] if val <= PMP_POOR
                    else PMP_COLORS["fine"] if PMP_POOR < val <=PMP_GOOD
                    else PMP_COLORS["good"],
                y_data
            )
        )
    return list(
        map(
            lambda val:
                CFT_COLORS["poor"] if val <= CFT_POOR
                else CFT_COLORS["fine"] if CFT_POOR < val <= CFT_GOOD
                else CFT_COLORS["good"] if CFT_GOOD <= val <= CFT_EXCELLENT
                else CFT_COLORS["excellent"],
            y_data
        )
    )

def draw_object(
        label: str,
        x_pos: float,
        ymax: int
) -> None:
    """Ajoute un évènement ponctuel
    et une ligne verticale de repérage.
    """
    plt.annotate(
        label,
        (x_pos, 0.9 * ymax),
        bbox = EVE_COLORS[label]["bbox"],
        color = EVE_COLORS[label]["font"]
    )
    plt.vlines(
        x_pos,
        0,
        1.5 * ymax,
        color = EVE_COLORS[label]["line"]
    )


def draw_objects(tops : dict[str, tuple], ymax: int):
    """Ajoute des évènements topés par le mesureur à un SI.
    tops est un dictionnaire avec 
    - clé = chaine topée
    - valeur = tuple (x,y) de la position sur le SI
    """
    for key, value in tops.items():
        x , _ = value
        if key == START:
            draw_object("D", x, ymax)
        elif key == END:
            draw_object("F", x, ymax)
        else:
            draw_object(key, x, ymax)

def filtre_bornes(mesure : RoadMeasure, bornes: list[str] | None):
    """Filtre les données de la mesure en fonction des bornes fournies."""
    xs, ys= mesure.abs(), mesure.datas
    if bornes is None:
        # Pas de bornes, on retourne tout
        return xs, ys
    if not bornes : # Aucun argument donc bornes start/end
        start = mesure.top_abs(START) or 0
        end = mesure.top_abs(END) or max(mesure.abs())
        if start is None :
            start = 0
        if end is None :
            end = max(xs)
        filtered_1 = [(x,y) for x, y in zip(xs, ys) if start <= x <= end]
        if filtered_1:
            xs_filtre, ys_filtre = zip(*filtered_1)
            return list(xs_filtre), list(ys_filtre)
        return [], []
    # bornes fournies
    prs_abs = [mesure.top_abs(pr) for pr in bornes]
    prs_abs = [p for p in prs_abs if p is not None]
    assert all(p is not None for p in prs_abs)
    if len(prs_abs) >= 2:
        start, end = min(prs_abs), max(prs_abs)
        filtered_2 = [(x,y) for x, y in zip(xs, ys) if start <= x <= end]
        if filtered_2:
            xs_filtre, ys_filtre = zip(*filtered_2)
            return list(xs_filtre), list(ys_filtre)
        return [], []
    return xs, ys

parser = argparse.ArgumentParser(description='linear diagrams')
parser.add_argument(
    "--multi",
    action="store",
    help="nombre de csv à traiter",
    default=1
)
parser.add_argument(
    "--pr",
    action="store",
    help="pr de recalage",
    default=None
)
parser.add_argument(
    "--show_legend",
    action="store_true",
    help="Afficher la légende avec les pourcentages"
)
parser.add_argument(
    "--bornes",
    nargs= "*",
    default=None,
    help="Fixer manuellement les bornes d'affichage"
)
parser.add_argument(
    "--rec_zh",
    default=None,
    help="événement pour le recalage des zones homogènes"
)

args = parser.parse_args()
questions = {}
NB_MES = int(args.multi)
PR_RECALAGE = args.pr
if PR_RECALAGE is None:
    print("Pas de pr de recalage fourni")
for j in range(NB_MES):
    questions[f"measure_{j}"] = {
        "folder_path": f"{os.path.dirname(__file__)}/datas",
        "ext": ["csv", "RE0"],
        "message": f"fichier de mesure {j}"
    }

file_names = pick_files(
    **questions
)

# index du graphe
INDEX = 2 * NB_MES * 100 + 11

plt.subplots_adjust(hspace=0.5)
plt.rcParams.update({'font.size': 6})

measures: list[RoadMeasure] = []

for name in file_names.values():
    mes_unit = which_measure(name)
    print(f"{name} > unité de mesure : {mes_unit}")
    FORCE_SENS = None
    if "droite" in name.lower():
        FORCE_SENS = "D"
    if "gauche" in name.lower():
        FORCE_SENS = "G"
    datas : RoadMeasure | None = None
    if mes_unit == "CFT":
        datas = get_grip_datas(name, force_sens=FORCE_SENS)
    if mes_unit == "PMP":
        datas = get_apo_datas(name, unit="PMP", force_sens=FORCE_SENS)
    if datas is not None:
        measures.append(datas)

ABS_REFERENCE = None
LEGENDED = []

for j, mes in enumerate(measures):
    Y_MAX = 100 if mes.unit == "CFT" else 1
    print(f"mesure {j}")
    if j == 0:
        ax = plt.subplot(INDEX)
        if PR_RECALAGE is not None:
            ABS_REFERENCE = mes.tops()[PR_RECALAGE][0]
            print(f"abscisse du pr {PR_RECALAGE} dans cette mesure : {ABS_REFERENCE}")
    else:
        plt.subplot(INDEX, sharex=ax)
    if mes.title is not None:
        plt.title(mes.title)

    # Ajout des bandes colorées en arrière-plan avec la fonction axhspan
    if mes.unit == "CFT":
        plt.axhspan(0, CFT_POOR, color=CFT_COLORS["poor"], alpha=0.1)
        plt.axhspan(CFT_POOR, CFT_GOOD, color=CFT_COLORS["fine"], alpha=0.1)
        plt.axhspan(CFT_GOOD, CFT_EXCELLENT, color=CFT_COLORS["good"], alpha=0.1)
        plt.axhspan(CFT_EXCELLENT, Y_MAX, color=CFT_COLORS["excellent"], alpha=0.1)

    if (n :=  len(mes.datas)) == 0:
        continue
    print(f"il y a {n} lignes")
    #  Ajout des % dans l'hystogramme en légende
    legend = []
    if args.show_legend :
        _, data = filtre_bornes(mes, args.bornes)
        n = len(data)
        if n > 0 : # pas de division par 0
            percentage: dict[str, float] = {}
            if mes.unit == "CFT" :
                percentage["poor"] = sum(1 for v in data if v <= CFT_POOR)
                percentage["fine"] = sum(1 for v in data if CFT_POOR < v <= CFT_GOOD)
                percentage["good"] = sum(1 for v in data if CFT_GOOD < v <= CFT_EXCELLENT)
                percentage["excellent"] = sum(1 for v in data if v > CFT_EXCELLENT)
                for level in ["poor", "fine", "good", "excellent"]:
                    pct = 100 * percentage[level] / n
                    patch = mpatches.Patch(
                        color=COLORS["CFT"][level],
                        label=f"{LEGENDS['CFT'][level]} ({pct:.1f}%)"
                    )
                    legend.append(patch)
            elif mes.unit == "PMP":
                percentage["poor"] = sum(1 for v in data if v <= PMP_POOR)
                percentage["fine"] = sum(1 for v in data if PMP_POOR < v <= PMP_GOOD)
                percentage["good"] = sum(1 for v in data if v > PMP_GOOD)
                for level in ["poor", "fine", "good"]:
                    pct = 100 * percentage[level] / n
                    patch = mpatches.Patch(
                        color=COLORS["PMP"][level],
                        label=f"{LEGENDS['PMP'][level]} ({pct:.1f}%)"
                    )
                    legend.append(patch)
            plt.legend(handles=legend, loc='upper right')
            LEGENDED.append(mes.unit)

    if mes.unit not in LEGENDED and mes.unit is not None:
        for color_key,color_label in LEGENDS[mes.unit].items():
            legend.append(
                mpatches.Patch(
                    color=COLORS[mes.unit][color_key],
                    label=color_label
                )
            )
        plt.legend(handles=legend, loc='upper right')
        LEGENDED.append(mes.unit)

    plt.ylim((0, Y_MAX))
    plt.grid(visible=True, axis="x", linestyle="--")
    plt.grid(visible=True, axis="y")
    print(f"tops avant offset {mes.tops()}")
    if j != 0 and mes.sens != measures[0].sens:
        mes.reverse()
    if j != 0 and ABS_REFERENCE is not None:
        mes.offset = ABS_REFERENCE - mes.tops()[PR_RECALAGE][0]
        print(f"on applique un offset {mes.offset}")
        print(f"tops après offset : {mes.tops()}")
    draw_objects(mes.tops(), Y_MAX)
    plt.bar(
        mes.abs(),
        mes.datas,
        color = color_map(mes.datas, unit=mes.unit),
        edgecolor = color_map(mes.datas, unit=mes.unit)
    )
    INDEX += 1


    plt.subplot(INDEX, sharex=ax)
    plt.ylim((0, Y_MAX))
    x_mean_values, mean_values = mes.produce_mean(
        MEAN_STEP,
        rec_zh=args.rec_zh
    )
    plt.bar(
        x_mean_values,
        mean_values,
        width=MEAN_STEP,
        color=color_map(mean_values, unit=mes.unit),
        edgecolor="white"
    )
    for jj, mean_value in enumerate(mean_values):
        plt.annotate(
            round(mean_value, PRECISION[Y_MAX]),
            (x_mean_values[jj], mean_value)
        )
    draw_objects(mes.tops(), Y_MAX)
    INDEX += 1

def summarize(list_of_measures):
    """affiche des éléments synthétiques sur les mesures."""
    for index, measure in enumerate(list_of_measures):
        msg = f"""
        SUMMARY mesure {index}
        sens {measure.sens}
        offset {measure.offset}
        abscisse départ {measure.abs()[0]}
        abscisse fin {measure.abs()[-1]}
        """
        print(msg)

summarize(measures)

if measures :
    # si des mesures existent, on applique le zoom
    xs_zoom, _ = filtre_bornes(measures[0], args.bornes)
    if xs_zoom:
        plt.xlim((min(xs_zoom), max(xs_zoom)))
plt.show()
