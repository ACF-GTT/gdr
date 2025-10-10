"""exploitation des fichiers SBO de l'APL"""
import argparse
import os

import matplotlib.pyplot as plt

from helpers.apl import get_po_mo_go_datas, GAUCHE, DROITE
from helpers.shared import pick_files
from helpers.road_mesure import RoadMeasure
from helpers.tools_file import CheckConf

YAML_CONF = CheckConf()

parser = argparse.ArgumentParser(description='linear diagrams')
parser.add_argument(
    "--multi",
    action="store",
    help="nombre de fichiers à traiter",
    default=1
)
args = parser.parse_args()
questions = {}

NB_MES = int(args.multi)

for j in range(NB_MES):
    questions[f"measure_{j}"] = {
        "folder_path": f"{os.path.dirname(__file__)}/{YAML_CONF.get_datas_folder()}",
        "ext": ["SBO"],
        "message": f"fichier de mesure {j}"
    }

file_names = pick_files(
    **questions
)

measures: list[dict[str, dict[str, RoadMeasure]]] = []

NB_GRAPHES = 0
for name in file_names.values():
    datas = get_po_mo_go_datas(name)
    if datas is not None:
        measures.append(datas)
        NB_GRAPHES += 3

INDEX = 1
NB_MES_APL = 0
for j, mes in enumerate(measures):
    for onde, traces in mes.items():
        if NB_MES_APL == 0:
            ax = plt.subplot(NB_GRAPHES, 1, INDEX)
        else:
            plt.subplot(NB_GRAPHES, 1, INDEX, sharex=ax)
        plt.title(str(traces[GAUCHE].title))

        ABSCISSES = [i * traces[GAUCHE].step for i in range(len(traces[GAUCHE].datas))]

        plt.step(ABSCISSES, traces[GAUCHE].datas, label=GAUCHE, color="tab:blue")
        plt.step(ABSCISSES, traces[DROITE].datas, label=DROITE, color="tab:orange")
        plt.xlabel("Abscisse (m)")
        plt.ylabel(onde)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.ylim(-10, 10)
        INDEX += 1
        NB_MES_APL += 1

    plt.tight_layout() # Ajuste automatiquement les espacements

plt.show()
