"""graph_tools"""
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from helpers.consts import EVE_COLORS

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
