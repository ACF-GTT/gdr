"""Traitement des fichiers du griptester MK2.
sous la forme de schémas itinéraires SI
"""
import argparse
import csv
import os
from statistics import mean

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from const.main import DATE_REGEXP, TIME_REGEXP, SITitle
from const.grip import BALISE_RESULTS, BALISE_HEADER, correle
from const.grip import POOR, GOOD, EXCELLENT, COLORS
from helpers.shared import pick_files

TITLE = "CFT"
PR = "pr"
START = "start"
END = "end"
YMAX = 100
LEGENDS = {
    "poor": f"CFT<={POOR}",
    "fine": f"{POOR}<CFT<={GOOD}",
    "good": f"{GOOD}<CFT<={EXCELLENT}",
    "excellent": f"CFT>{EXCELLENT}"
}
BBOX_PR = {
    "boxstyle": "round",
    "edgecolor": "gray",
    "facecolor": "white"
}
BBOX_START = {
    "boxstyle": "round",
    "edgecolor": "none",
    "facecolor": "green"
}
BBOX_END = {
    "boxstyle": "round",
    "edgecolor": "none",
    "facecolor": "red"
}

# pas en mètres pour une analyse en zône homogène
MEAN_STEP = 200


def color_map(y_data: list[float]):
    """Crée le tableau des couleurs pour l'histogramme."""
    return list(
        map(
            lambda val:
                COLORS["poor"] if val <= POOR
                else COLORS["fine"] if POOR < val <= GOOD
                else COLORS["good"] if GOOD <= val <= EXCELLENT
                else COLORS["excellent"],
            y_data
        )
    )


def draw_object(
        label: str,
        x_pos: float,
        bbox: dict[str, str],
        fontcolor: str,
        linecolor: str
) -> None:
    """Ajoute un évènement ponctuel
    et une ligne verticale de repérage.
    """
    label_pos = (x_pos, YMAX - 10)
    plt.annotate(
        label,
        label_pos,
        bbox = bbox,
        color = fontcolor
    )
    plt.vlines(
        x_pos,
        0,
        1.5 * YMAX,
        color = linecolor
    )


def draw_objects(tops : dict[str, tuple]):
    """Ajoute des évènements topés par le mesureur à un SI.
    tops est un dictionnaire avec 
    - clé = chaine topée
    - valeur = tuple (x,y) de la position sur le SI
    """
    for key, value in tops.items():
        x , _ = value
        if key == START:
            draw_object("D", x, BBOX_START, "white", "green")
        elif key == END:
            draw_object("F", x, BBOX_END, "white", "red")
        else:
            draw_object(key, x, BBOX_PR, "red", "blue")


class RoadMeasure():
    """représentation d'une mesure routière"""
    def __init__(
        self,
        step: float,
        datas: list[float],
        tops: dict[str, tuple[float, float]],
        **kwargs
    ) -> None:
        """initialisation"""
        self.title = kwargs.get("title", None)
        self.step = step
        self.datas = datas
        self._tops = tops
        prs = self.prs()
        self.pr: int = min(prs)
        # offset/décalage à appliquer en mètres
        self.offset = kwargs.get("offset", 0)
        self.sens: str = "D" if prs[0] < prs[1] else "G"

    def prs(self) -> list[str]:
        """retourne la liste des pr topés."""
        return [key for key in self._tops.keys() if key not in [START, END]]

    def tops(self) -> dict[str, tuple[float, float]]:
        """retourne les tops."""
        result = {}
        for key, value in self._tops.items():
            result[key] = (
                self.offset + value[0],
                value[1]
            )
        return result

    def index(self, top: str|int) -> int:
        """retourne la position d'un top."""
        return int(self._tops[str(top)][0] // self.step - 1)

    def abs(self) -> list[float]:
        """retourne les abscisses curvilignes en mètres."""
        nb_pts = len(self.datas)
        return [(i + 1) * self.step + self.offset for i in range(nb_pts)]

    def longueur(self) -> float:
        """longueur de mesure en mètres"""
        return len(self.datas) * self.step

    def reverse(self) -> None:
        """retourne les données."""
        self.datas.reverse()
        for key, value in self._tops.items():
            self._tops[key] = (
                self.longueur() - value[0],
                value[1]
            )

    def produce_mean(
        self,
        mean_step: int,
    ) -> tuple[list, list]:
        """retourne les valeurs moyennes"""
        i = 0
        # pas de mesure en mètres
        print(f"pas de mesure de l'appareil : {self.step} mètre(s)")
        nb_pts_mean_step = int(mean_step // self.step)
        print(f"nombre de points dans une zone homogène : {nb_pts_mean_step}")
        pos_in_meter = mean_step / 2
        x_means = []
        y_means = []
        while i < len(self.datas) - nb_pts_mean_step:
            x_means.append(self.offset + pos_in_meter)
            y_means.append(
                mean(self.datas[i: i + nb_pts_mean_step])
            )
            i += nb_pts_mean_step
            pos_in_meter += mean_step
        return x_means, y_means


def get_grip_datas(file_name: str, root: str=TITLE) -> RoadMeasure:
    """ouvre un fichier de mesure du griptester mk2
    en extrait les mesures et les tops
    """
    y_datas = []
    tops = {}
    step = None
    with open(file_name, encoding="utf-8") as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',')
        index_start = None
        index_header = None
        for i,row in enumerate(csv_data):
            if row[0].strip() == BALISE_HEADER:
                index_header = i
            if index_header is not None:
                if i == index_header + 2:
                    title = SITitle(root)
                    # le nom de la section est le dernier champ....
                    # on pourrait utiliser la colonne 21...
                    title.add(row[-1])
                    title.search_n_add(DATE_REGEXP, row)
                    title.search_n_add(TIME_REGEXP, row)
            if row[0].strip() == BALISE_RESULTS:
                index_start = i
            if index_start and i == index_start + 2:
                step = float(row[0])
            if index_start and i > index_start + 1:
                x_val = float(row[0])
                y_val = correle(float(row[1]))
                if PR in row[14].lower():
                    pr_nb = row[14].split("@")[0].lower()
                    pr_nb = pr_nb.replace(PR,"").replace(" ","")
                    tops[pr_nb] = (x_val, y_val)
                if START in row[14].lower():
                    tops[START] = (x_val, y_val)
                if END in row[14].lower():
                    tops[END] = (x_val, y_val)
                y_datas.append(y_val)
    return RoadMeasure(
        step=step,
        datas=y_datas,
        tops=tops,
        title=title.title
    )


parser = argparse.ArgumentParser(description='GRIPTESTER MK2')
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
args = parser.parse_args()
questions = {}
NB_MES = int(args.multi)
PR_RECALAGE = args.pr
if PR_RECALAGE is None:
    print("Pas de pr de recalage fourni")
for j in range(NB_MES):
    questions[f"measure_{j}"] = {
        "folder_path": f"{os.path.dirname(__file__)}/datas",
        "ext": "csv",
        "message": f"fichier de mesure {j}"
    }

file_names = pick_files(
    **questions
)

INDEX = 2 * NB_MES * 100 + 11

plt.subplots_adjust(hspace=0.5)
plt.rcParams.update({'font.size': 6})

measures: list[RoadMeasure] = []

for name in file_names.values():
    measures.append(get_grip_datas(name))

XRANGE = None
ABS_REFERENCE = None

for j, mes in enumerate(measures):
    ax = plt.subplot(INDEX)
    plt.title(mes.title)
    if j == 0:
        legend = []
        for color_key,color_label in LEGENDS.items():
            legend.append(
                mpatches.Patch(
                    color=COLORS[color_key],
                    label=color_label
                )
            )
        plt.legend(handles=legend)
        if PR_RECALAGE is not None:
            ABS_REFERENCE = mes.tops()[PR_RECALAGE][0]
            print(f"abscisse du pr {PR_RECALAGE} dans cette mesure : {ABS_REFERENCE}")

    plt.ylim((0, YMAX))
    plt.grid(visible=True, axis="x", linestyle="--")
    plt.grid(visible=True, axis="y")
    if j != 0 and mes.sens == "G":
        mes.reverse()
    if j != 0 and ABS_REFERENCE is not None:
        mes.offset = ABS_REFERENCE - mes.tops()[PR_RECALAGE][0]
        print(f"********offset {mes.offset}")
    print(mes.tops())
    draw_objects(mes.tops())

    plt.bar(
        mes.abs(),
        mes.datas,
        color = color_map(mes.datas),
        edgecolor = color_map(mes.datas)
    )

    INDEX += 1
    plt.subplot(INDEX, sharex=ax)
    plt.ylim((0, YMAX))
    x_mean_values, mean_values = mes.produce_mean(MEAN_STEP)

    plt.bar(
        x_mean_values,
        mean_values,
        width=MEAN_STEP,
        color=color_map(mean_values),
        edgecolor="white"
    )
    for jj, mean_value in enumerate(mean_values):
        plt.annotate(
            round(mean_value),
            (x_mean_values[jj], mean_value)
        )
    draw_objects(mes.tops())
    INDEX += 1

    if XRANGE is not None:
        ax.set_xlim(XRANGE)
    if j == 0:
        XRANGE = ax.get_xlim()

plt.show()
