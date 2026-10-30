"""helper pour travail en PR+abscisse"""
import csv
from matplotlib.axes import Axes
import matplotlib.patches as mpatches

from helpers.tools_file import CheckConf
from helpers.consts import LOGGER

PR_ABS_DB = CheckConf().pr_abs_csv()

FIELDS = CheckConf().yaml.get("pr_abs_rubriques", [])

ROUTE = "route"
SENS = "sens"
PRD = "prd"
PRF = "prf"
ABD = "abd"
ABF = "abf"
TXT = "txt"
TXT_TYPE = "type"


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
        self.abds: dict[str, dict[str, dict[str, float]]] = {}
        self.abfs: dict[str, dict[str, dict[str, float]]] = {}
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
                        for txt_type in FIELDS
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
            txt_type: {
                f"{row[TXT]}_{i}": curv_prs[str(row[PRD])] + int(row[ABD])
                for i, row in enumerate(datas[txt_type])
                if str(row[PRD]) in curv_prs
            }
            for txt_type in datas
        }
        self.abfs[sens] = {
            txt_type: {
                f"{row[TXT]}_{i}": curv_prs[str(row[PRF])] + int(row[ABF])
                for i, row in enumerate(datas[txt_type])
                if str(row[PRF]) in curv_prs
            }
            for txt_type in datas
        }

    def plot_text_line(
        self,
        txt_type: str,
        ax: Axes,
        sens: str
    ) -> None:
        """plot a line of textual datas"""
        ax.yaxis.set_tick_params(labelcolor='none')
        ax.grid(visible=True, axis="x", linestyle="--")
        ax.grid(visible=True, axis="y")
        for txt_data, abd in self.abds[sens][txt_type].items():
            if txt_data not in self.abfs[sens][txt_type]:
                continue
            abf = self.abfs[sens][txt_type][txt_data]
            ax.text(abd, 0.5, txt_data.replace("\\n", "\n").rsplit("_", 1)[0])
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
            min(values.values())
            for abds in self.abds.values()
            for values in abds.values()
            if values
        )
        abfs_max = max(
            max(values.values())
            for abfs in self.abfs.values()
            for values in abfs.values()
            if values
        )
        ax.set_xlim(abds_min, abfs_max)
