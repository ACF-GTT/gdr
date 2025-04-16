"""constants for griptester mk2."""

BALISE_RESULTS = "<RESULTS>"
BALISE_HEADER = "<HEADER>"
START_DATE = "StartDate"
START_TIME = "StartTime"

POOR = 50
GOOD = 60
EXCELLENT = 70
COLORS = {
    "poor": "#ea1256",
    "fine": "#ee7a0e",
    "good": "#e7dc0c",
    "excellent": "#38e70c"
}

# droite de corrélation obtenue lors des essais croisés
PENTE = 0.9915
DECALAGE = -0.0044

def correle(gt_value):
    """Applique la corrélation issue des essais croisés."""
    return 100*(PENTE * gt_value + DECALAGE)

def define_color(cft_value):
    """Retourne la couleur de la classe de la valeur de CFT"""
    if cft_value <= POOR:
        return COLORS["poor"]
    if POOR < cft_value <= GOOD:
        return COLORS["fine"]
    if GOOD <= cft_value <= EXCELLENT:
        return COLORS["good"]
    return COLORS["excellent"]
