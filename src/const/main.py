"""main constants"""
import re

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

BPTOPO_GEOJSON = "src/BDTOPO_GEOJSON"
