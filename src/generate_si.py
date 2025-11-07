"""Traitement des fichiers du griptester MK2.
sous la forme de schémas itinéraires SI
"""
import argparse
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from helpers.consts import (
    UPPER, LOWER,
    LEVELS, LEGENDS,
    EVE_COLORS, COLORS, get_color
)
from helpers.shared import pick_files, which_measure
from helpers.apo import get_apo_datas
from helpers.grip import get_grip_datas
from helpers.generic_absdatatop_csv import get_generic_absdatatop_csv
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


def filtre_bornes(mes: RoadMeasure, bornes: list[str] | None):
    """Filtre les données de la mesure fonction des bornes fournies."""
    if not bornes or bornes is None:
        mes.clear_zoom()
    elif len(bornes) == 1:
        mes.apply_zoom_from_prs(bornes[0], None)
    elif len(bornes) >= 2:
        mes.apply_zoom_from_prs(bornes[0], bornes[-1])
    return mes.abs_zoomed(), mes.datas_zoomed


def get_measures(nb_mes) -> list[RoadMeasure]:
    """construit la liste des mesures."""
    questions = {}
    for j in range(nb_mes):
        questions[f"measure_{j}"] = {
            "folder_path": f"{os.path.dirname(__file__)}/{YAML_CONF.get_datas_folder()}",
            "ext": ["csv", "RE0"],
            "message": f"fichier de mesure {j}"
        }

    file_names = pick_files(
        **questions
    )
    measures: list[RoadMeasure] = []

    for name in file_names.values():
        mes_unit = which_measure(name)
        print(f"{name} > unité de mesure : {mes_unit}")
        force_sens = None
        if "droite" in name.lower():
            force_sens = "D"
        if "gauche" in name.lower():
            force_sens = "G"
        datas : RoadMeasure | None = None
        if mes_unit == "CFL":
            datas = get_grip_datas(name, force_sens=force_sens)
        if mes_unit == "PMP":
            datas = get_apo_datas(name, unit=mes_unit, force_sens=force_sens)
        if mes_unit == "CFT":
            datas = get_generic_absdatatop_csv(name, unit=mes_unit, force_sens=force_sens)
        if datas is not None:
            measures.append(datas)
    return measures


def format_legend(add_percent, unit, data):
    """Formate la légende, avec ou sans %"""
    family_counts: dict[str, float] = {}
    if add_percent :
        levels_description = LEVELS[unit]
        for level, bounds in levels_description.items():
            lower = bounds.get(LOWER, float("-inf"))
            upper = bounds.get(UPPER, float("inf"))
            family_counts[level] = sum(1 for v in data if lower < v <= upper)

    legend = []
    for level, color_label in LEGENDS[unit].items():
        if add_percent and level in family_counts:
            pct = 100 * family_counts[level] / len(data)
            legend_text = f"{color_label} ({pct:.1f}%)"
        else:
            legend_text = color_label  # affichage simple sans %
        patch = mpatches.Patch(
            color=COLORS[unit][level],
            label=legend_text
        )
        legend.append(patch)
    return legend


def draw_colored_horizons(unit: str, y_max: int):
    """Ajout de bandes colorées en arrière-plan"""
    if unit in ("CFT", "CFL"):
        for level, val in LEVELS[unit].items():
            lower = val.get(LOWER, 0)
            upper = val.get(UPPER, y_max)
            plt.axhspan(
                lower,
                upper,
                color=COLORS[unit][level],
                alpha=YAML_CONF.get_backgound_alpha(level)
            )


def draw_mean_histo(mes: RoadMeasure, y_max: int, rec_zh: str):
    """affiche l'historgramme des valeurs moyennes."""
    x_mean_values, mean_values = mes.produce_mean(
        MEAN_STEP,
        rec_zh=rec_zh
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
            round(mean_value, PRECISION[y_max]),
            (x_mean_values[jj], mean_value)
        )


def fix_abs_reference(measures: list[RoadMeasure], pr: str | None):
    """fixe l'abscisse de référence"""
    abs_reference = None
    if pr is None:
        print("Pas de pr de recalage fourni")
        return abs_reference
    try:
        abs_reference = measures[0].tops()[pr][0]
        print(f"abscisse du pr {pr} dans cette mesure : {abs_reference}")
    except KeyError:
        print(f"Attention le PR saisi '{pr}' est inexistant : pas de recalage")
    return abs_reference


def main(args):
    """main exe"""
    measures = get_measures(int(args.multi))
    plt.subplots_adjust(hspace=0.5)
    plt.rcParams.update({'font.size': 6})

    nb_graphes = len(measures) if MEAN_STEP == 0 else 2*len(measures)
    plt_index = 1
    abs_reference = fix_abs_reference(measures, args.pr)
    abscisses = None

    for j, mes in enumerate(measures):
        y_max = 100 if mes.unit in  ("CFT","CFL") else 1
        print(f"mesure {j}")
        if j == 0:
            ax = plt.subplot(nb_graphes, 1, plt_index)
        else:
            plt.subplot(nb_graphes, 1, plt_index, sharex=ax)
        if mes.title is not None:
            plt.title(mes.title)

        print(f"tops avant offset {mes.tops()}")
        if j != 0 and mes.sens != measures[0].sens:
            mes.reverse()
        if j != 0 and abs_reference is not None:
            mes.offset = abs_reference - mes.tops()[args.pr][0]
            print(f""""
                  on applique un offset {mes.offset}
                  tops après offset : {mes.tops()}
            """)

        abscisses, data = filtre_bornes(mes, args.bornes)
        if args.bornes and j == 0:
            plt.xlim(min(abscisses), max(abscisses))
        n = len(data)
        if n == 0:
            continue

        draw_colored_horizons(mes.unit, y_max)

        print(f"il y a {n} lignes")
        if mes.unit is None:
            continue
        if YAML_CONF.view_legend():
            plt.legend(
                handles=format_legend(
                    args.add_percent,
                    mes.unit,
                    data
                ),
                loc="upper right"
            )

        plt.ylim((0, y_max))
        plt.grid(visible=True, axis="x", linestyle="--")
        plt.grid(visible=True, axis="y")
        draw_objects(mes.tops(), y_max)
        plt.bar(
            abscisses,
            data,
            width = mes.step,
            color = color_map(data, unit=mes.unit),
            edgecolor = color_map(data, unit=mes.unit)
        )
        plt_index += 1

        if MEAN_STEP :
            plt.subplot(nb_graphes, 1, plt_index, sharex=ax)
            plt.ylim((0, y_max))
            draw_mean_histo(mes, y_max, args.rec_zh)
            draw_objects(mes.tops(), y_max)
            plt_index += 1
    plt.show()
    return measures


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


if __name__ == "__main__":
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
    summarize(main(parser.parse_args()))
