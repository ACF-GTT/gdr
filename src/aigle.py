"""aigle3D gpkg to matplotlib"""
import re
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

FILE = "datas/AIGLE_3D/2024_IQRN_indicateurs_etat_DIRMC.gpkg"
YEAR = 2024
STATES = ["Superficiel", "Profond", "Tres_Profond"]
LAYERS = {
    state: f"Indicateur_Etat_{state}_{YEAR} — DIRMC"
    for state in STATES
}
COLORS = {
    0: "green",
    1: "#b8dfaf",
    2: "orange",
    3: "red",
    4: "purple"
}
PLOD = "cle_troncon_plod"
NB_LEVELS = 5

PRD = "prd"
PRF = "prf"

SECTIONS = [
    [0, 5],
    [8, 10],
    [58, 60]
]

class Indicateur:
    """Indicateur d'état IQRN"""
    def __init__(self, state: str) -> None:
        """initialisation"""
        self._state: str = state
        self._dep: str | None = None
        self._route: str | None = None
        self._sens: str | None = None
        self._level: int | None = None

    def _sql(self):
        """format sql filter"""
        exp = f"{self._route}"
        if self._sens is not None:
            exp = f"{exp}\\_%\\_{self._sens}"
        if self._dep is not None:
            exp = f"{exp}\\_%{self._dep}PR%"
        exp = f"{exp}\\_%"
        return f"""
            SELECT * FROM
            '{LAYERS[self._state]}'
            WHERE {PLOD} LIKE '{exp}' ESCAPE '\\'
            AND gravite == '>= {self._level}'
        """

    def fix_road(self, route: str) -> None:
        """fix route"""
        self._route = route

    def fix_dep(self, dep: str) -> None:
        """fix departement"""
        self._dep = dep

    def fix_sens(self, sens: str) -> None:
        """fix sens"""
        self._sens = sens

    def fix_level(self, level: int) -> None:
        """fix level"""
        self._level = level

    def get(self) -> GeoDataFrame:
        """get the geodata frame"""
        sql= self._sql()
        print(sql)
        return gpd.read_file(FILE, sql=sql)


def get_pr_bounds(
    gdf: GeoDataFrame
) -> tuple[int | None, int | None]:
    """retourne les pr min et max sur un itinéraire."""
    regex = re.compile(r"PR(\d+)", re.IGNORECASE)
    values = []
    for val in gdf[PLOD].dropna():
        matches = [int(m.group(1)) for m in regex.finditer(val)]
        values.extend(matches)
    # on ne conserve que les valeurs distinctes et on trie
    values = sorted(set(values))
    if not values:
        return None, None
    return min(values), max(values)


def filter_pr_range(gdf: GeoDataFrame, prd=None, prf=None):
    """filtre sur un intervalle de pr"""
    if prd is None or prf is None:
        return gdf
    regex = re.compile(r"PR(\d+)", re.IGNORECASE)
    mask = gdf[PLOD].apply(
        lambda val: any(
            prd <= int(m.group(1)) <= prf
            for m in regex.finditer(val)
        )
    )
    return gdf[mask]


def graphe(
    state: str,
    route: str,
    sens: str | None = None
) -> None:
    """affiche les indicateurs d'état"""
    nbsec = len(SECTIONS)
    _, ax = plt.subplots(1, nbsec, figsize=(6*nbsec, 6))
    indicateur = Indicateur(state)
    indicateur.fix_dep("43")
    indicateur.fix_road(route)
    if sens:
        indicateur.fix_sens(sens)
    layers = {}
    for level in range(NB_LEVELS):
        indicateur.fix_level(level)
        layers[level] = indicateur.get()
        bounds = get_pr_bounds(layers[level])
        print(bounds)
    for i, prs in enumerate(SECTIONS):
        prd = max(prs[0], bounds[0])
        prf = min(prs[1], bounds[1])
        for level in range(NB_LEVELS):
            zoom = filter_pr_range(layers[level], prd=prd, prf=prf)
            zoom.plot(
                ax=ax[i],
                color=COLORS[level],
                edgecolor=COLORS[level]
            )
            # affichage des centroides
            # pas d'intérêt car dès qu'on est sur des portions sinueuses
            # le centroide n'est plus sur le tracé
            # zoom["centroid"] = zoom.geometry.centroid
            # zoom.centroid.plot(ax=ax, color="red", markersize=20)
        ax[i].set_title(f"PR {prd} à {prf}")
        ax[i].set_aspect("equal")
    plt.tight_layout()
    plt.show()

graphe("Superficiel", "N0088", sens="P")
