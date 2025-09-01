# pylint: disable=too-many-instance-attributes
"""Représentation de mesures routières."""
import re
from statistics import mean
from helpers.consts import LOGGER

START = "start"
END = "end"
PR = "pr"

DATE_REGEXP = re.compile(
    "[0-9]{2}/[0-9]{2}/[0-9]{4}"
)
TIME_REGEXP = re.compile(
    "[0-9]{2}:[0-9]{2}:[0-9]{2}"
)

class SITitle():
    """titre de schéma itinéraire."""
    def __init__(self, title) -> None:
        """initialise un titre de SI"""
        self.title = title

    def add(self, motif) -> None:
        """Ajoute un motif au titre."""
        self.title = f"{self.title} - {motif}"

    def search_n_add(self, reg_exp, liste) -> None:
        """explore une liste sur la base d'une expression régulière
        ajoute le pattern trouvé au titre."""
        pattern_found = re.search(
            reg_exp,
            "".join(liste)
        )
        if pattern_found:
            self.add(pattern_found[0])


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
        self.title : str | None = kwargs.get("title", None)
        self.unit : str | None = kwargs.get("unit", None)
        self.step = step
        self.datas = datas
        self.zoom: tuple[int | None, int | None] = (None, None)
        # tops est un dictionnaire avec :
        #  - comme clé la saisie de l'opérateur,
        #  - comme valeur un tuple de 2 float
        # le premier float est l'abscisse curviligne
        # le second float est :
        # - soit 0.0
        # - soit la valeur mesurée par l'appareil à cette abscisse
        # celà peut servir pour des vérifications lorsqu'on a un bug :-)
        self._tops = tops
        prs = self.prs()
        # offset/décalage à appliquer en mètres
        self.offset = kwargs.get("offset", 0)
        try:
            self.sens: str = "D" if prs[0] < prs[1] else "G"
        except IndexError:
            force_sens = kwargs.get("force_sens", None)
            self.sens = force_sens if force_sens is not None else "D"

    def prs(self) -> list[str]:
        """retourne la liste des pr topés."""
        return [key for key in self._tops.keys() if key not in [START, END]]

    def top_abs(self, top_string: str, offset=True) -> None | float:
        """retourne l'abscisse du top"""
        top_strings = list(self._tops.keys())
        if top_string not in top_strings:
            return None
        decalage = self.offset if offset else 0
        return self._tops[top_string][0] + decalage

    def tops(self, offset=True) -> dict[str, tuple[float, float]]:
        """retourne les tops."""
        result = {}
        decalage = self.offset if offset else 0
        for key, value in self._tops.items():
            result[key] = (
                decalage + value[0],
                value[1]
            )
        return result

    def abs(self, index_start: int = 0, offset: bool = True) -> list[float]:
        """Liste des abscisses (avec ou sans offset), zoomées si applicable."""
        # Pour chaque indice i dans self.datas, on calcule son abscisse sans décalage
        base = [(i + index_start) * self.step for i in range(len(self.datas))]
        base = [x + (self.offset if offset else 0) for x in base]
        if self.zoom == (None, None):
            return base
        # Si le zoom actif, on retourne la partie start/end
        start, end = self.zoom
        return base[start:end]

    @property # on transforme une méthode en attribut, pas besoin des ()
    def datas_zoomed(self) -> list[float]:
        """retourne les données en fonction du zoom"""
        if self.zoom == (None, None):
            return self.datas
        start, end = self.zoom
        return self.datas[start:end]

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

    def set_zoom_by_abs(self, start_abs: float | None, end_abs: float | None) -> None:
        """Définit le zoom à partir des abscisses (mètres)."""
        abs_list = self.abs(offset=False)
        start_idx, end_idx = 0, len(self.datas)

        if start_abs is not None:
            # On parcourt abs_list jusqu'à trouver le premier point dont l’abscisse >= start_abs
            for i, val in enumerate(abs_list):
                if val >= start_abs:
                    start_idx = i
                    break
        if end_abs is not None:
            # On cherche en partant de la fin le dernier point inférieur ou égal à end_abs
            for i in reversed(range(len(abs_list))):
                if abs_list[i] <= end_abs:
                    end_idx = i + 1
                    break
        self.zoom = (start_idx, end_idx)

    def apply_zoom_from_prs(self, start_pr: str | None, end_pr: str | None) -> None:
        """Applique un zoom en se basant sur deux PR (ou None)."""
        start_abs = self.top_abs(start_pr) if start_pr else None
        end_abs = self.top_abs(end_pr) if end_pr else None
        self.set_zoom_by_abs(start_abs, end_abs)

    def clear_zoom(self) -> None:
        """Supprime le zoom (affiche tout)."""
        self.zoom = (None, None)

    def produce_mean(
        self,
        mean_step: int,
        rec_zh = None
    ) -> tuple[list, list]:
        """retourne les valeurs moyennes"""
        # pas de mesure en mètres
        LOGGER.debug("pas de mesure de l'appareil : %s mètre(s)", self.step)
        nb_pts_mean_step = int(mean_step // self.step)
        LOGGER.debug("nombre de points dans une zone homogène : %s", nb_pts_mean_step)
        # récupération de l'indice de départ
        start_index = 0
        top_abs = self.top_abs(rec_zh, offset=False)
        if top_abs is not None:
            # les tops peuvent être enregistrés à une précision centrimétrique
            # on arrondit à la précision du relevé (step)
            top_abs = (top_abs // self.step) * self.step
            abscisses = self.abs(offset=False)
            start_index = abscisses.index(top_abs)
            LOGGER.debug("indice du top : %s", start_index)
            # combien de zônes homogènes "complètes"
            # y a t'il entre l'extrémité gauche de la mesure et le top?
            start_index -= (start_index // nb_pts_mean_step) * nb_pts_mean_step
            LOGGER.debug("indice de départ zh : %s", start_index)
        i = start_index
        pos_in_meter = mean_step / 2 + self.step * start_index
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
