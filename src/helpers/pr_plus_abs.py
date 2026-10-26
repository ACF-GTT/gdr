"""helper pour travail en PR+abscisse"""
from enum import StrEnum
import csv
from matplotlib.axes import Axes
import matplotlib.patches as mpatches

from helpers.tools_file import CheckConf
from helpers.consts import LOGGER

PR_ABS_DB = CheckConf().pr_abs_csv()

ROUTE = "route"
SENS = "sens"
PRD = "prd"
PRF = "prf"
ABD = "abd"
ABF = "abf"
TXT = "txt"
TXT_TYPE = "type"

class Fields(StrEnum):
    """les champs de la bdd en PR+ABS"""
    TECH = "technique"
    GEOM = "geometrie"

class PlotText:
    """Add textual lines to SI"""
    def __init__(
        self,
        route: str | None = None
    ) -> None:
        """init"""
        self.filtered: dict[str, dict]= {
            "P": {},
            "M": {}
        }
        self.abds: dict[str, dict[str, list[float]]] = {}
        self.abfs: dict[str, dict[str, list[float]]] = {}
        csv_name = None
        if isinstance(PR_ABS_DB, str):
            csv_name = PR_ABS_DB
        if route is not None and isinstance(PR_ABS_DB, dict):
            csv_name = PR_ABS_DB.get(route)
        if csv_name is None:
            message = f"pas de datas PR+ABS pour {route} ou pas de bdd PR+ABS"
            LOGGER.warning(message)
            return
        try:
            with open(csv_name, encoding="utf-8") as csvfile:
                csv_data = list(csv.DictReader(csvfile, delimiter=','))
                for sens in self.filtered:
                    self.filtered[sens] = {
                        txt_type: items
                        for txt_type in Fields
                        if (items := [
                            el for el in csv_data
                            if el.get(TXT_TYPE) == txt_type
                            and el.get(ROUTE) == route
                            and el.get(SENS) == sens
                        ])
                    }
            message = f"nombre d'infos text : {self.len()}"
            LOGGER.info(message)
        except FileNotFoundError:
            message = f"CSV introuvable : {csv_name}"
            LOGGER.warning(message)

    def len(self, sens: str | None = None) -> int:
        """nombre de champs réellement dispo"""
        if sens is None:
            return sum(len(datas) for datas in self.filtered.values())
        return len(self.filtered[sens])

    def compute_abs(
        self,
        curv_prs : dict[str, float],
        sens: str
    ):
        """compute les abscisses curvilignes des datas PR+ABS"""
        datas = self.filtered[sens]
        self.abds[sens] = {
            txt_type: [
                curv_prs[str(row[PRD])] + int(row[ABD])
                for row in datas[txt_type]
            ]
            for txt_type in datas
        }
        self.abfs[sens] = {
            txt_type: [
                curv_prs[str(row[PRF])] + int(row[ABF])
                for row in datas[txt_type]
            ]
            for txt_type in datas
        }

    def plot_text_line(
        self,
        txt_type: Fields,
        ax: Axes,
        sens: str
    ) -> None:
        """plot a line of textual datas"""
        datas = self.filtered[sens]
        ax.yaxis.set_tick_params(labelcolor='none')
        ax.grid(visible=True, axis="x", linestyle="--")
        ax.grid(visible=True, axis="y")
        for i, row in enumerate(datas[txt_type]):
            txt_data = row[TXT]
            abd = self.abds[sens][txt_type][i]
            abf = self.abfs[sens][txt_type][i]
            ax.text(abd, 0.5, txt_data.replace("\\n", "\n"))
            rectangle = mpatches.Rectangle(
                (abd, 0),
                abf - abd,
                1,
                facecolor='none',
                edgecolor='blue'
            )
            ax.add_artist(rectangle)

    def adjust(
        self,
        ax: Axes,
    ):
        """adjust the window"""
        abds_min = min(
            min(values)
            for abds in self.abds.values()
            for values in abds.values()
        )
        abfs_max = max(
            max(values)
            for abfs in self.abfs.values()
            for values in abfs.values()
        )
        ax.set_xlim(abds_min, abfs_max)
