"""constants."""
from collections import defaultdict
import logging

from helpers.tools_file import CheckConf

FORMAT = "%(asctime)-15s %(levelname)-8s %(module)-15s %(funcName)s :%(lineno)-8s %(message)s"
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger("gdr")

LOGGER.setLevel(CheckConf().get_log_level("gdr"))

BALISE_RESULTS = "<RESULTS>"
BALISE_HEADER = "<HEADER>"

POOR = "poor"
FINE = "fine"
GOOD = "good"
EXCELLENT = "excellent"

START = "start"
END = "end"

PR = "pr"

############
# GRIPTESTER
############
CFT_POOR = 50
CFT_GOOD = 60
CFT_EXCELLENT = 70
CFL_POOR = 50
CFL_GOOD = 60
CFL_EXCELLENT = 70
CFT_COLORS = {
    POOR: "#ea1256",
    FINE: "#ee7a0e",
    GOOD: "#e7dc0c",
    EXCELLENT: "#38e70c"
}
CFL_COLORS = {
    POOR: "#ea1256",
    FINE: "#ee7a0e",
    GOOD: "#e7dc0c",
    EXCELLENT: "#38e70c"
}

###########
# RUGOLASER
###########
PMP_POOR = 0.4
PMP_GOOD = 0.8

PMP_COLORS = {
    POOR: "#30383a",
    FINE: "#a2b3a3",
    GOOD: "#409f48"
}

UNKNOWN_COLOR = "#cccccc"
COLORS = {
    "CFL": CFL_COLORS, #grip
    "PMP": PMP_COLORS, #rugolaser
    "CFT": CFT_COLORS  #scrim avec le même seuil que CFL car CFT ~ CFL
}

########
# LEVELS
########
UPPER = "upper"
LOWER = "lower"

LEVELS: dict[str, dict[str, dict[str, int | float]]] = {
    "CFL": {
        POOR: {UPPER: CFL_POOR},
        FINE: {LOWER: CFL_POOR, UPPER: CFL_GOOD},
        GOOD: {LOWER: CFL_GOOD, UPPER: CFL_EXCELLENT},
        EXCELLENT: {LOWER: CFL_EXCELLENT}
    },
    "PMP": {
        POOR: {UPPER: PMP_POOR},
        FINE: {LOWER: PMP_POOR, UPPER: PMP_GOOD},
        GOOD: {LOWER: PMP_GOOD}
    },
    "CFT": {
        POOR: {UPPER: CFT_POOR},
        FINE: {LOWER: CFT_POOR, UPPER: CFT_GOOD},
        GOOD: {LOWER: CFT_GOOD, UPPER: CFT_EXCELLENT},
        EXCELLENT: {LOWER: CFT_EXCELLENT}
    }
}

#####################
# LEGENDS (AUTOMATIC)
#####################
def produce_legend() -> dict[str, dict[str, str]]:
    """production des bases pour les légendes."""
    legends : dict[str, dict[str, str]] = {}
    for metric, levels_description in LEVELS.items():
        if metric not in legends:
            legends[metric] = {}
        for level, bounds in levels_description.items():
            lower = bounds.get(LOWER)
            upper = bounds.get(UPPER)
            if lower is None and upper is not None:
                legends[metric][level] = f"{metric}<={upper}"
                continue
            if lower is not None and upper is None:
                legends[metric][level] = f"{metric}>{lower}"
                continue
            legends[metric][level] = f"{lower}<{metric}<={upper}"
    return legends

LEGENDS = produce_legend()

#############
# MANUAL TOPS
#############
EVE_STD = {
    "font": "red",
    "line": "blue",
    "bbox": {
        "boxstyle": "round",
        "edgecolor": "gray",
        "facecolor": "white"
    }
}
EVE_COLORS: dict[str, dict] = defaultdict(lambda: EVE_STD)
EVE_COLORS["D"] = {
    "font": "white",
    "line": "green",
    "bbox": {
        "boxstyle": "round",
        "edgecolor": "none",
        "facecolor": "green"
    }
}
EVE_COLORS["F"] = {
    "font": "white",
    "line": "red",
    "bbox": {
        "boxstyle": "round",
        "edgecolor": "none",
        "facecolor": "red"
    }
}


def get_color(val: float, unit: str = "CFT") -> str:
    """Couleur du couple (valeur, type de mesure)."""
    for level, bounds in LEVELS[unit].items():
        lower = bounds.get(LOWER, float("-inf"))
        upper = bounds.get(UPPER, float("inf"))
        if lower < val <= upper:
            return COLORS[unit][level]
    return UNKNOWN_COLOR
