"""Représentation de mesures routières."""
import re
from statistics import mean

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
        self.title = kwargs.get("title", None)
        self.unit = kwargs.get("unit", None)
        self.step = step
        self.datas = datas
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

    def tops(self) -> dict[str, tuple[float, float]]:
        """retourne les tops."""
        result = {}
        for key, value in self._tops.items():
            result[key] = (
                self.offset + value[0],
                value[1]
            )
        return result

    def abs(self, offset=1) -> list[float]:
        """retourne les abscisses curvilignes en mètres."""
        nb_pts = len(self.datas)
        return [(i + offset) * self.step + self.offset for i in range(nb_pts)]

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
        **kwargs
    ) -> tuple[list, list]:
        """retourne les valeurs moyennes"""
        # pas de mesure en mètres
        print(f"pas de mesure de l'appareil : {self.step} mètre(s)")
        nb_pts_mean_step = int(mean_step // self.step)
        print(f"nombre de points dans une zone homogène : {nb_pts_mean_step}")
        # récupération de l'indice de départ
        start_index = kwargs.get("start_index", 0)
        print(f"saisie_utilisateur : {start_index}")
        start_index-= (start_index// nb_pts_mean_step) * nb_pts_mean_step
        print(f"recalcul_code : {start_index}")
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
