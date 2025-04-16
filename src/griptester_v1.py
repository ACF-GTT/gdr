"""Traitement des fichiers du griptester MK2.
sous la forme de schémas itinéraires SI
"""
import csv
from statistics import mean
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from const.grip import BALISE_RESULTS, correle
from const.grip import POOR, GOOD, EXCELLENT, COLORS
from helpers.shared import pick_file

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
    - valuer = tuple (x,y) de la position sur le SI
    """
    for key, value in tops.items():
        x , _ = value
        if key == START:
            draw_object("D", x, BBOX_START, "white", "green")
        elif key == END:
            draw_object("F", x, BBOX_END, "white", "red")
        else:
            draw_object(key, x, BBOX_PR, "red", "blue")

grip_numbers = []
x_vals = []
field_tops = {}

file_name = pick_file()

ax = plt.subplot(211)

with open(file_name, encoding="utf-8") as csvfile:
    csv_data = csv.reader(csvfile, delimiter=',')
    INDEX_START = None
    for i,row in enumerate(csv_data):
        if i == 2:
            section_name = row[21].rstrip().replace("\\n","")
            TITLE = f"{TITLE} - {section_name} - {row[18]} - {row[19]}"
            plt.title(TITLE)
        if row[0].strip() == BALISE_RESULTS:
            INDEX_START = i
        if INDEX_START and i > INDEX_START + 1:
            x_val = float(row[0])
            y_val = correle(float(row[1]))
            if PR in row[-1].lower():
                pr_nb = row[-1].split("@")[0].lower()
                pr_nb = pr_nb.replace(PR,"").replace(" ","")
                field_tops[pr_nb] = (x_val, y_val)
            if START in row[14].lower():
                field_tops[START] = (x_val, y_val)
            if END in row[14].lower():
                field_tops[END] = (x_val, y_val)
            x_vals.append(x_val)
            grip_numbers.append(y_val)

# pas de mesure en mètres
STEP = x_vals[1] - x_vals[0]
print(f"pas de mesure de l'appareil : {STEP}")
NB_PTS_MEAN_STEP = int(MEAN_STEP // STEP)
print(f"nombre de points dans une zone homogène : {NB_PTS_MEAN_STEP}")

i=0
pos_in_meter = MEAN_STEP / 2
mean_values = []
x_mean_values = []
while i < len(grip_numbers) - NB_PTS_MEAN_STEP:
    x_mean_values.append(pos_in_meter)
    mean_values.append(
        mean(grip_numbers[i:i+NB_PTS_MEAN_STEP])
    )
    i += NB_PTS_MEAN_STEP
    pos_in_meter += MEAN_STEP
print(x_mean_values)
print(mean_values)

plt.ylim((0, YMAX))
plt.grid(visible=True, axis="x", linestyle="--")
plt.grid(visible=True, axis="y")
draw_objects(field_tops)

plt.bar(
    x_vals,
    grip_numbers,
    color = color_map(grip_numbers),
    edgecolor = color_map(grip_numbers)
)
legend = []
for color_key,color_label in LEGENDS.items():
    legend.append(
        mpatches.Patch(
            color=COLORS[color_key],
            label=color_label
        )
    )
plt.legend(handles=legend)
plt.subplot(212, sharex=ax)
plt.ylim((0, YMAX))

plt.bar(
    x_mean_values,
    mean_values,
    width=MEAN_STEP,
    color=color_map(mean_values),
    edgecolor="white"
)
for i, mean_value in enumerate(mean_values):
    plt.annotate(
        round(mean_value),
        (x_mean_values[i], mean_value)
    )
draw_objects(field_tops)
plt.show()
