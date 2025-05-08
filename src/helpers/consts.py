"""constants."""

BALISE_RESULTS = "<RESULTS>"
BALISE_HEADER = "<HEADER>"

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

PMP_POOR = 0.4
PMP_GOOD = 0.8

PMP_COLORS = {
    "poor": "#30383a",
    "fine": "#a2b3a3",
    "good": "#409f48"
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
