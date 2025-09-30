"""Traitement des fichiers du griptester MK2.
sous la forme de schémas itinéraires SI
"""
import argparse
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from helpers.consts import (
    CFT_COLORS,
    UPPER, LOWER,
    LEVELS, LEGENDS,
    EVE_COLORS, COLORS, get_color
)
from helpers.shared import pick_files, which_measure
from helpers.apo import get_apo_datas
from helpers.grip import get_grip_datas
from helpers.scrim import get_scrim_datas
from helpers.road_mesure import RoadMeasure, START, END
from helpers.tools_file import CheckConf

YAML_CONF = CheckConf()

PRECISION = {
    100: 0,
    1: 2
}

# pas en mètres pour une analyse en zône homogène
MEAN_STEP = YAML_CONF.get_mean_step()

def color_map(y_data: list[float], unit: str = "CFT") -> list[str]:
    """Crée le tableau des couleurs pour l'histogramme."""
    return [get_color(val, unit) for val in y_data]

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
    if not bornes or bornes is None:
        mesure.clear_zoom()
    elif len(bornes) == 1:
        mesure.apply_zoom_from_prs(bornes[0], None)
    elif len(bornes) >= 2:
        mesure.apply_zoom_from_prs(bornes[0], bornes[-1])
    return mesure.abs_zoomed(), mesure.datas_zoomed


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
    "--add_percent",
    action="store_true",
    help="Afficher la légende avec les pourcentages"
)
parser.add_argument(
    "--bornes",
    nargs = "*",
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
        "folder_path": f"{os.path.dirname(__file__)}/{YAML_CONF.get_datas_folder()}",
        "ext": ["csv", "RE0"],
        "message": f"fichier de mesure {j}"
    }

file_names = pick_files(
    **questions
)

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
    if mes_unit == "SCRIM":
        datas = get_scrim_datas(name, force_sens=FORCE_SENS)
    if datas is not None:
        measures.append(datas)
NB_GRAPHES = len(measures) if MEAN_STEP == 0 else 2*len(measures)
INDEX= 1
ABS_REFERENCE = None
ABSCISSES = None

for j, mes in enumerate(measures):
    Y_MAX = 100 if mes.unit == "CFT" else 1
    print(f"mesure {j}")
    if j == 0:
        ax = plt.subplot(NB_GRAPHES,1,INDEX)
        if PR_RECALAGE is not None:
            try:
                ABS_REFERENCE = mes.tops()[PR_RECALAGE][0]
                print(f"abscisse du pr {PR_RECALAGE} dans cette mesure : {ABS_REFERENCE}")
            except KeyError:
                print(f"Attention le PR saisi '{PR_RECALAGE}' est inexistant : pas de recalage")
                ABS_REFERENCE = None
    else:
        plt.subplot(NB_GRAPHES,1,INDEX, sharex=ax)
    if mes.title is not None:
        plt.title(mes.title)

    print(f"tops avant offset {mes.tops()}")
    if j != 0 and mes.sens != measures[0].sens:
        mes.reverse()
    if j != 0 and ABS_REFERENCE is not None:
        mes.offset = ABS_REFERENCE - mes.tops()[PR_RECALAGE][0]
        print(f"on applique un offset {mes.offset}")
        print(f"tops après offset : {mes.tops()}")

    ABSCISSES, data = filtre_bornes(mes, args.bornes)
    if args.bornes and j==0:
        plt.xlim(min(ABSCISSES), max(ABSCISSES))
    n = len(data)
    if n == 0:
        continue

    # Ajout des bandes colorées en arrière-plan avec la fonction axhspan
    if mes.unit == "CFT":
        for level, val in LEVELS["CFT"].items():
            lower = val.get(LOWER, 0)
            upper = val.get(UPPER, Y_MAX)
            plt.axhspan(
                lower,
                upper,
                color=CFT_COLORS[level],
                alpha=YAML_CONF.get_backgound_alpha(level)
            )

    print(f"il y a {n} lignes")
    if mes.unit is None:
        continue
    #  Ajout des % dans l'hystogramme en légende
    legend = []
    family_counts: dict[str, float] = {}
    if args.add_percent :
        levels_description = LEVELS[mes.unit]
        for level, bounds in levels_description.items():
            lower = bounds.get(LOWER, float("-inf"))
            upper = bounds.get(UPPER, float("inf"))
            family_counts[level] = sum(1 for v in data if lower < v <= upper)

    if YAML_CONF.view_legend():
        # Création légende
        for level, color_label in LEGENDS[mes.unit].items():
            if args.add_percent and level in family_counts:
                pct = 100 * family_counts[level] / n
                legend_text = f"{color_label} ({pct:.1f}%)"
            else:
                legend_text = color_label  # affichage simple sans %
            patch = mpatches.Patch(
                color=COLORS[mes.unit][level],
                label=legend_text
            )
            legend.append(patch)
        plt.legend(handles=legend, loc="upper right")

    plt.ylim((0, Y_MAX))
    plt.grid(visible=True, axis="x", linestyle="--")
    plt.grid(visible=True, axis="y")
    draw_objects(mes.tops(), Y_MAX)
    plt.bar(
        ABSCISSES,
        data,
        width = mes.step,
        color = color_map(data, unit=mes.unit),
        edgecolor = color_map(data, unit=mes.unit)
    )
    INDEX += 1

    if MEAN_STEP :
        plt.subplot(NB_GRAPHES,1,INDEX, sharex=ax)
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

plt.show()
