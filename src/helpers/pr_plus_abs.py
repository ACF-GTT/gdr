"""helper pour travail en PR+abscisse"""
import csv
from matplotlib.axes import Axes
import matplotlib.patches as mpatches

from helpers.tools_file import CheckConf

FILE = CheckConf().pr_abs_csv()

PRD = "prd"
PRF = "prf"
ABD = "abd"
ABF = "abf"
TXT = "txt"
TXT_TYPE = "type"
TECH = "technique"
GEOM = "geometrie"

class PlotText:
    """Add textual lines to SI"""
    def __init__(
        self,
        curv_prs : dict[str, float]
    ) -> None:
        """init"""
        self.curv_prs = curv_prs
        assert FILE is not None
        with open(FILE, encoding="utf-8") as csvfile:
            csv_data = list(csv.DictReader(csvfile, delimiter=','))
            self.filtered = {
                txt_type: [el for el in csv_data if el[TXT_TYPE]==txt_type]
                for txt_type in [TECH, GEOM]
            }
        self.abds = {
            txt_type: [
                curv_prs[str(row[PRD])] + int(row[ABD])
                for row in self.filtered[txt_type]
            ]
            for txt_type in [TECH, GEOM]
        }
        self.abfs = {
            txt_type: [
                curv_prs[str(row[PRF])] + int(row[ABF])
                for row in self.filtered[txt_type]
            ]
            for txt_type in [TECH, GEOM]
        }

    def plot_text_line(
        self,
        txt_type: str,
        ax: Axes
    ) -> None:
        """plot a line of textual datas"""
        ax.yaxis.set_tick_params(labelcolor='none')
        ax.grid(visible=True, axis="x", linestyle="--")
        ax.grid(visible=True, axis="y")
        for i, row in enumerate(self.filtered[txt_type]):
            txt_data = row[TXT]
            abd = self.abds[txt_type][i]
            abf = self.abfs[txt_type][i]
            ax.text(abd, 0.5, txt_data)
            rectangle = mpatches.Rectangle(
                (abd, 0),
                abf - abd,
                1,
                facecolor='none',
                edgecolor='blue'
            )
            ax.add_artist(rectangle)

    def plot_text(
        self,
        axes,
        adjust=True
    ):
        """plot a text line for each types"""
        for i, txt_type in enumerate(self.filtered):
            self.plot_text_line(txt_type, axes[i])
        if adjust:
            abds_min = min(min(values) for values in self.abds.values())
            abfs_max = max(max(values) for values in self.abfs.values())
            axes[-1].set_xlim(abds_min, abfs_max)
