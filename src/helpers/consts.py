"""constants."""
from collections import defaultdict
import logging

FORMAT = "%(asctime)-15s %(levelname)-8s %(module)-15s %(funcName)s :%(lineno)-8s %(message)s"
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger("gdr")
LOGGER.setLevel("DEBUG")

BALISE_RESULTS = "<RESULTS>"
BALISE_HEADER = "<HEADER>"

############
# GRIPTESTER
############
CFT_POOR = 50
CFT_GOOD = 60
CFT_EXCELLENT = 70
CFT_COLORS = {
    "poor": "#ea1256",
    "fine": "#ee7a0e",
    "good": "#e7dc0c",
    "excellent": "#38e70c"
}

# droite de corrélation obtenue lors des essais croisés
CFT_PENTE = 0.9915
CFT_DECALAGE = -0.0044

###########
# RUGOLASER
###########
PMP_POOR = 0.4
PMP_GOOD = 0.8

PMP_COLORS = {
    "poor": "#30383a",
    "fine": "#a2b3a3",
    "good": "#409f48"
}

COLORS = {
    "CFT": CFT_COLORS,
    "PMP": PMP_COLORS
}

########
# LEVELS
########
UPPER = "upper"
LOWER = "lower"

LEVELS: dict[str, dict[str, dict[str, int | float]]] = {
    "CFT": {
        "poor": {UPPER: CFT_POOR},
        "fine": {LOWER: CFT_POOR, UPPER: CFT_GOOD},
        "good": {LOWER: CFT_GOOD, UPPER: CFT_EXCELLENT},
        "excellent": {LOWER: CFT_EXCELLENT}
    },
    "PMP": {
        "poor": {UPPER: PMP_POOR},
        "fine": {LOWER: PMP_POOR, UPPER: PMP_GOOD},
        "good": {LOWER: PMP_GOOD}
    }
}

#####################
# LEGENDS (AUTOMATIC)
#####################
LEGENDS: dict[str, dict[str, str]] = {}

for metric, levels_description in LEVELS.items():
    if metric not in LEGENDS:
        LEGENDS[metric] = {}
    for level, bounds in levels_description.items():
        lower = bounds.get(LOWER)
        upper = bounds.get(UPPER)
        if lower is None and upper is not None:
            LEGENDS[metric][level] = f"{metric}<={upper}"
            continue
        if lower is not None and upper is None:
            LEGENDS[metric][level] = f"{metric}>{lower}"
            continue
        LEGENDS[metric][level] = f"{lower}<{metric}<={upper}"

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

def correle(gt_value):
    """Applique la corrélation issue des essais croisés."""
    return 100*(CFT_PENTE * gt_value + CFT_DECALAGE)

def define_color(cft_value):
    """Retourne la couleur de la classe de la valeur de CFT"""
    if cft_value <= CFT_POOR:
        return CFT_COLORS["poor"]
    if CFT_POOR < cft_value <= CFT_GOOD:
        return CFT_COLORS["fine"]
    if CFT_GOOD <= cft_value <= CFT_EXCELLENT:
        return CFT_COLORS["good"]
    return CFT_COLORS["excellent"]
