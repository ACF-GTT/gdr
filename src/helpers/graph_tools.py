"""graph_tools"""
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator
from helpers.consts import EVE_COLORS
from helpers.road_mesure import START, END
from helpers.tools_file import CheckConf

FIG_PARAMS = CheckConf().yaml["figure"]

def init_single_column_plt(nb_graphes) :
    """Initialise un graphe a une seule colonne"""
    fig, axes = plt.subplots(
        nrows=nb_graphes,
        ncols=1,
        figsize=(
            FIG_PARAMS.get("width", 15),
            FIG_PARAMS.get("height", 6)
        ),
        sharex=True,
        gridspec_kw={'hspace': FIG_PARAMS.get("hspace", 0.8)}
    )
    fig.subplots_adjust(
        left=FIG_PARAMS.get("left", 0.125),
        right=FIG_PARAMS.get("right", 0.9),
        top=FIG_PARAMS.get("top", 0.88),
        bottom=FIG_PARAMS.get("bottom", 0.11)
    )
    plt.rcParams.update({'font.size':FIG_PARAMS.get("font", 5)})
    return fig, axes

def render(name):
    """render to screen or save to disk"""
    root = FIG_PARAMS.get("root")
    path = FIG_PARAMS.get("path")
    if root is not None:
        path = f"{root}{path}"
    if path is not None:
        plt.savefig(f"{path}/{name}.svg")
    else:
        plt.show()


def habille(
    ax: Axes,
    scale: int,
    title: str | None = None,
    label: str | None = None,
    grid: bool = False
):
    """Habillage d'un axe"""
    ax.tick_params(labelsize=6)
    ax.set_ylim(0, scale)

    # Réglage de l'espacement des ticks x depuis le YAML
    x_tick_step = FIG_PARAMS.get("x_tick_step")
    if x_tick_step:
        ax.xaxis.set_major_locator(MultipleLocator(x_tick_step))

    if title:
        ax.set_title(title)
    if label:
        ax.set_ylabel(label, fontsize=8)
    if grid:
        ax.grid(visible=True, axis="x", linestyle="--")
        ax.grid(visible=True, axis="y")


def draw_object(
    label: str,
    x_pos: float,
    ymax: float,
    ax : Axes | None = None
) -> None:
    """Ajoute un évènement ponctuel
    et une ligne verticale de repérage.
    """
    current = ax if ax else plt
    current.annotate(
        label,
        (x_pos, 0.9 * ymax),
        bbox = EVE_COLORS[label]["bbox"],
        color = EVE_COLORS[label]["font"]
    )
    current.vlines(
        x_pos,
        0,
        1.5 * ymax,
        color = EVE_COLORS[label]["line"]
    )


def draw_objects(
    tops : dict[str, tuple],
    ymax: int,
    ax : Axes | None = None
):

    """Ajoute des évènements topés par le mesureur à un SI.
    tops est un dictionnaire avec 
    - clé = chaine topée
    - valeur = tuple (x,y) de la position sur le SI
    """
    for key, value in tops.items():
        x , _ = value
        if key == START:
            draw_object("D", x, ymax, ax=ax)
        elif key == END:
            draw_object("F", x, ymax, ax=ax)
        else:
            draw_object(key, x, ymax, ax=ax)
