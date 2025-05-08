"""Traitement des fichiers APO"""
import csv
import os

from helpers.road_mesure import SITitle, RoadMeasure, PR

def get_apo_datas(file_name: str, unit="PMP") -> RoadMeasure:
    """ouvre un fichier de mesure de type APO"""
    title = SITitle(unit)
    y_datas = []
    tops = {}
    step = None
    folder = os.path.dirname(file_name)
    all_files = os.listdir(folder)
    eve_name = [el for el in all_files if el.endswith(".EV0")][0]
    with open(f"{folder}/{eve_name}", encoding="utf-8") as evefile:
        for i,row in enumerate(
            csv.reader(evefile, delimiter='\t')
        ):
            if row[0].lower() == PR:
                tops[row[2]] = (float(row[1]), 0)
    with open(file_name, encoding="utf-8") as datafile:
        data = csv.reader(datafile, delimiter='\t')
        unit_index = None
        for i,row in enumerate(data):
            if i == 0:
                unit_index = row.index(unit)
            if i != 0 and unit_index is not None:
                if step is None:
                    step = float(row[1]) - float(row[0])
                y_datas.append(float(row[unit_index]))
    return RoadMeasure(
        step=step,
        datas=y_datas,
        tops=tops,
        unit=unit,
        title=title.title,
    )
