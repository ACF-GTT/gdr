"""Schémas itinéraires SI
pour suivi de chantiers routiers d'innovation
"""
import argparse
from dataclasses import dataclass

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from helpers.consts import (
    UPPER, LOWER,
    LEVELS, LEGENDS,
    COLORS, get_color
)
from helpers.shared import pick_files, which_measure
from helpers.apo import get_apo_datas
from helpers.grip import get_grip_datas
from helpers.pr_plus_abs import PlotText
from helpers.generic_absdatatop_csv import get_generic_absdatatop_csv
from helpers.road_mesure import RoadMeasure
from helpers.tools_file import CheckConf
from helpers.graph_tools import draw_objects, init_single_column_plt, habille
from helpers.iq3d import GraphStates
from helpers.consts_etat_surface import surface_state_legend



YAML_CONF = CheckConf()

PRECISION = {
    100: 0,
    1: 2
}

# pas en mètres pour une analyse en zône homogène
MEAN_STEP = YAML_CONF.get_mean_step()

# Mapping entre sens des mesures Grip et sens Aigle
SENS_GRIP_TO_AIGLE = {
    "D": "P",  # Droite → P
    "G": "M",  # Gauche → M
}

@dataclass
class Aigle :
    """aigle3D dataclass"""
    active = YAML_CONF.yaml.get("aigle_3d")
    route = YAML_CONF.yaml.get("aigle_route")
    dep = YAML_CONF.yaml.get("aigle_dep")
    sens_list = YAML_CONF.yaml.get("aigle_sens", ["P"]) # par défaut "P" si rien
    recalage = YAML_CONF.yaml.get("aigle_recalage", {})
    df = None

aigle = Aigle()

def color_map(
    y_data: list[float],
    unit: str = "CFT"
)-> list[str]:
    """Crée le tableau des couleurs pour l'histogramme."""
    return [get_color(val, unit) for val in y_data]


def filtre_bornes(
    mes: RoadMeasure,
    args: argparse.Namespace
):
    """Filtre les données de la mesure fonction des bornes fournies."""

    if not args.bornes or args.bornes is None:
        return mes.abs_zoomed(), mes.datas_zoomed

    start_pr = args.bornes[0]
    end_pr = args.bornes[-1] if len(args.bornes) > 1 else None
    start_abs = mes.top_abs(start_pr)
    end_abs = mes.top_abs(end_pr)

    if not args.plus_abs:
        mes.set_zoom_by_abs(start_abs, end_abs)
        return mes.abs_zoomed(), mes.datas_zoomed

    # On applique les décalages
    if start_abs is not None :
        start_abs += args.plus_abs[0]
    if end_abs is not None and len(args.plus_abs) > 1:
        end_abs += args.plus_abs[-1]
    # Zoom final
    mes.set_zoom_by_abs(start_abs, end_abs)
    return mes.abs_zoomed(), mes.datas_zoomed


def get_measures(nb_mes) -> dict[str, list[RoadMeasure]]:
    """construit la liste des mesures."""
    questions = {}
    for j in range(nb_mes):
        questions[f"measure_{j}"] = {
            "folder_path" : YAML_CONF.get_datas_folder(),
            "ext": ["csv", "RE0"],
            "message": f"fichier de mesure {j}"
        }

    file_names = pick_files(
        **questions
    )
    measures: dict[str, list[RoadMeasure]] = {
        "D": [],
        "G": []
    }

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
        if datas is not None and datas.sens in measures:
            measures[datas.sens].append(datas)
    return measures


def format_legend(add_percent, unit, data):
    """Formate la légende, avec ou sans %"""
    family_counts = {}
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


def draw_colored_horizons(
    unit: str,
    y_max: int,
    ax: Axes
):
    """Ajout de bandes colorées en arrière-plan"""
    if unit in ("CFT", "CFL"):
        for level, val in LEVELS[unit].items():
            lower = val.get(LOWER, 0)
            upper = val.get(UPPER, y_max)
            ax.axhspan(
                lower,
                upper,
                color=COLORS[unit][level],
                alpha=YAML_CONF.get_backgound_alpha(level)
            )


def draw_mean_histo(
    mes: RoadMeasure,
    y_max: int,
    rec_zh: str,
    ax : Axes
):
    """affiche l'histogramme des valeurs moyennes."""
    if not mes.unit:
        return
    x_mean_values, mean_values = mes.produce_mean(
        MEAN_STEP,
        rec_zh=rec_zh
    )
    ax.bar(
        x_mean_values,
        mean_values,
        width=MEAN_STEP,
        color=color_map(mean_values, unit=mes.unit),
        edgecolor="white"
    )
    for jj, mean_value in enumerate(mean_values):
        ax.annotate(
            round(mean_value, PRECISION[y_max]),
            (x_mean_values[jj], mean_value)
        )


def get_abs_reference(
    measures: dict[str, list[RoadMeasure]],
    pr: str | None
):
    """fixe l'abscisse de référence"""
    if pr is None:
        print("Pas de pr de recalage fourni")
        return 0
    try:
        for mes_list in measures.values():
            if len(mes_list) > 0:
                mes = mes_list[0]
                break
        abs_reference = mes.tops()[pr][0]
        print(f"Grip sens {mes.sens} - abs pr {pr} = {abs_reference}")
        return abs_reference
    except KeyError:
        print(f"! pr {pr} inexistant : pas de recalage")
        return 0


def extract_prd_prf(args):
    """bornes pour prd/prf """
    if args.bornes:
        prd = int(args.bornes[0])
        prf = int(args.bornes[-1]) if len(args.bornes) > 1 else None
        return prd, prf

    if args.pr:
        return int(args.pr), None

    return None, None

def init_context(args):
    """Initialise le contexte de graphes (Aigle + matplotlib)."""
    grapher = None
    nb_graphes = 0
    text_helper = PlotText(route=aigle.route)
    if aigle.active :
        grapher = GraphStates(user_pr=args.pr)

        grapher.set_route_dep(route=aigle.route, dep=aigle.dep)
        # 3 graphes par sens + 2 graphes pour le texte PR+abs
        nb_graphes += 3 * len(aigle.sens_list)
        for sens in aigle.sens_list:
            nb_graphes += text_helper.len(sens)

    measures = get_measures(int(args.multi))

    nb_mes = len(measures["D"]) + len(measures["G"])
    nb_graphes += nb_mes if MEAN_STEP == 0 else 2 * nb_mes
    _, axes = init_single_column_plt(nb_graphes)

    if grapher:
        fig = axes[0].figure
        if aigle.route and aigle.dep:
            fig.suptitle(
                f"Route : {aigle.route} - Département : {aigle.dep}",
                x=0.01, ha="left"
            )
        fig.legend(
            handles = surface_state_legend(),
            loc = "upper right",
            ncol = len(surface_state_legend()),
        )

    return grapher, text_helper, measures, axes


# pylint: disable=too-many-branches
def main(args):
    """main exe"""
    grapher, text_helper, measures, axes = init_context(args)
    plt_index, abs_reference, xlim_set = 0, None, False

    # Boucle par sens : Sens Aigle puis Sens mesures Grip
    for sens, mes_list in measures.items():

        # 1) Mesures Aigle
        aigle_sens = SENS_GRIP_TO_AIGLE[sens]
        if grapher and aigle_sens in aigle.sens_list:
            prd, prf = extract_prd_prf(args)
            aigle.df = grapher.graphe_sens(
                sens=aigle_sens,
                axes=axes[plt_index:plt_index+3],
                force_abs=abs_reference,
                prd=prd,
                prf=prf
            )
            plt_index += 3
            if abs_reference is None:
                abs_reference = grapher.abs_reference
        # 2) abscisse de référence
        if abs_reference is None:
            abs_reference = get_abs_reference(
                measures,
                pr=args.pr
            )
        # 3) Autres mesures
        for mes in mes_list:
            y_max = 100 if mes.unit in ("CFT", "CFL") else 1
            ax: Axes = axes[plt_index]
            habille(ax, y_max, title=mes.title, grid=True)

            # Reverse des sens moins
            if mes.sens == "G":
                mes.reverse()
            mes.offset = abs_reference - mes.tops().get(args.pr, [0])[0]

            abscisses_data = filtre_bornes(mes, args)
            if args.bornes and not xlim_set:
                ax.set_xlim(min(abscisses_data[0]), max(abscisses_data[0]))
                xlim_set = True

            if len(abscisses_data[1]) == 0 or mes.unit is None:
                plt_index += 1
                continue

            draw_colored_horizons(mes.unit, y_max, ax=ax)

            if YAML_CONF.view_legend():
                ax.legend(
                    handles=format_legend(args.add_percent, mes.unit, abscisses_data[1]),
                    loc="upper right"
                )

            draw_objects(mes.tops(), y_max, ax=ax)
            ax.bar(
                abscisses_data[0],
                abscisses_data[1],
                width=mes.step,
                color=color_map(abscisses_data[1], unit=mes.unit),
                edgecolor=color_map(abscisses_data[1], unit=mes.unit)
            )
            plt_index += 1

            if MEAN_STEP:
                ax = axes[plt_index]
                habille(ax, y_max)
                draw_mean_histo(mes, y_max, args.rec_zh, ax=ax)
                draw_objects(mes.tops(), y_max, ax=ax)
                plt_index += 1

        # Texte PR+abs
        if text_helper.len(aigle_sens) and aigle.active and aigle_sens in grapher.curv_prs:
            text_helper.compute_abs(grapher.curv_prs[aigle_sens], aigle_sens)
            for txt_type in text_helper.filtered[aigle_sens]:
                text_helper.plot_text_line(txt_type, axes[plt_index], aigle_sens)
                plt_index += 1
    if text_helper.len():
        text_helper.adjust(axes[-1])
    return measures


def summarize(measures):
    """affiche des éléments synthétiques sur les mesures."""
    index = 0
    for mes_list in measures.values():
        for measure in mes_list:
            msg = f"""
            SUMMARY mesure {index}
            sens {measure.sens}
            offset {measure.offset}
            abscisse départ {measure.abs()[0]}
            abscisse fin {measure.abs()[-1]}
            """
            print(msg)
            index += 1


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
    parser.add_argument(
        "--plus_abs",
        nargs="*",
        type=float,
        default=None,
        help= "zoom en pr+abs "
    )

    summarize(main(parser.parse_args()))
    root = YAML_CONF.yaml["figure"].get("root")
    path = YAML_CONF.yaml["figure"].get("path")
    if root is not None:
        path = f"{root}{path}"
    if path is not None:
        plt.savefig(f"{path}/fig.svg")
    else:
        plt.show()
