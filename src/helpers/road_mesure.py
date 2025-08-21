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

    def prs(self, all=False) -> list[str]:
        """retourne la liste des PR topés, si all=True, retourne tous les évenements topés dont start,end """
        if not all:
            return [key for key in self._tops.keys() if key not in [START, END]]
        return list(self._tops.keys())

    def top_abs(self, top_string: str) -> None | float:
        """retourne l'absisse du top"""
        if top_string not in self.prs(all=True):
            return None
        return self._tops[top_string][0] + self.offset

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

    def abs(self, index_start=0, offset=True) -> list[float]:
        """retourne les abscisses curvilignes en mètres.
        avec ou sans offset
        on peut décider de commencer à step et non à 0 (cf griptester)
        """
        nb_pts = len(self.datas)
        decalage = self.offset if offset else 0
        return [(i + index_start) * self.step + decalage for i in range(nb_pts)]

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
        rec_zh = None
    ) -> tuple[list, list]:
        """retourne les valeurs moyennes"""
        # pas de mesure en mètres
        LOGGER.debug("pas de mesure de l'appareil : %s mètre(s)", self.step)
        nb_pts_mean_step = int(mean_step // self.step)
        LOGGER.debug("nombre de points dans une zone homogène : %s", nb_pts_mean_step)
        # récupération de l'indice de départ
        start_index = 0
        if rec_zh is not None:
            abs_top = self.tops(offset=False)[rec_zh][0]
            # les tops peuvent être enregistrés à une précision centrimétrique
            # on arrondit à la précision du relevé (step)
            abs_top = (abs_top // self.step) * self.step
            abscisses = self.abs(offset=False)
            start_index = abscisses.index(abs_top)
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
