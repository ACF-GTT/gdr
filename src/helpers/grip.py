"""Traitement des fichiers griptester MK2"""
import csv

from helpers.consts import BALISE_RESULTS, BALISE_HEADER, correle
from helpers.road_mesure import (
    START, END, PR,
    DATE_REGEXP, TIME_REGEXP,
    SITitle,
    RoadMeasure
)

def get_grip_datas(
    file_name: str,
    force_sens: str | None = None
) -> RoadMeasure | None:
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
                    title = SITitle("CFT")
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
    if step is not None:
        # pylint: disable=duplicate-code
        return RoadMeasure(
            step=step,
            datas=y_datas,
            tops=tops,
            unit="CFT",
            title=title.title,
            force_sens=force_sens
        )
        # pylint: enable=duplicate-code
    return None
