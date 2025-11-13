"""aigle3D gpkg to matplotlib"""
import os
import re
from typing import cast, TypeAlias
import geopandas as gpd
from geopandas import GeoDataFrame
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button

FILE = f"{os.path.dirname(__file__)}/datas/AIGLE_3D/2024_IQRN_indicateurs_etat_DIRMC.gpkg"
YEAR = 2024
GEST = "DIRMC"
DEP = "43"
STATES = ["Superficiel", "Profond", "Tres_Profond"]
LAYERS = {
    state: f"Indicateur_Etat_{state}_{YEAR} — {GEST}"
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

class Indicateur:
    """Indicateur d'état IQRN"""
    def __init__(self, dep: str, route: str, sens: str | None = None) -> None:
        """initialisation"""
        assert re.fullmatch(r"[A-Z0-9_]+", route)
        if dep: assert re.fullmatch(r"\d{2,3}", dep)
        if sens: assert sens in ("P", "M")
        self._dep = dep
        self._route: str = route
        self._sens: str | None = sens
        self._state: str | None = None
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

    def fix_state(self, state: str) -> None:
        """fix state"""
        self._state = state

    def fix_level(self, level: int) -> None:
        """fix level"""
        self._level = int(level)

    def get(self) -> GeoDataFrame:
        """get the geodata frame"""
        sql= self._sql()
        print(sql)
        return gpd.read_file(FILE, sql=sql)


def get_pr_bounds(
    gdf: GeoDataFrame
) -> tuple[int | None, int | None, str, str]:
    """retourne les pr min et max sur un itinéraire
    ainsi que des strings prêts à nourrir les textbox.
    """
    regex = re.compile(r"PR(\d+)", re.IGNORECASE)
    values = []
    for val in gdf[PLOD].dropna():
        matches = [int(m.group(1)) for m in regex.finditer(val)]
        values.extend(matches)
    # on ne conserve que les valeurs distinctes et on trie
    values = sorted(set(values))
    if not values:
        return None, None, "", ""
    prd = min(values)
    prf = max(values)
    if prd == prf:
        return prd, prf, str(prd), str(prd)
    return prd, prf, str(prd), str(prd + 1)


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


def get_state(
    indicateur: Indicateur,
    state: str
) -> dict[int, GeoDataFrame]:
    """return all frames for a state"""
    indicateur.fix_state(state)
    layers = {}
    for level in range(NB_LEVELS):
        indicateur.fix_level(level)
        layers[level] = indicateur.get()
    return layers


def graphe_state(
    state: str,
    layers: dict[int, GeoDataFrame],
    ax: Axes,
    prd: int | None = None,
    prf: int | None = None,
) -> None:
    """graphe a single state"""
    for level in range(NB_LEVELS):
        zoom = filter_pr_range(layers[level], prd=prd, prf=prf)
        zoom.plot(
            ax=ax,
            color=COLORS[level],
            edgecolor=COLORS[level]
        )
        ax.set_title(f"Etat {state} - PR {prd} à {prf}")
        ax.set_aspect("equal")


def widget_axes(pos: list[float]) -> Axes:
    """return the widget position"""
    AxesRect: TypeAlias = tuple[float, float, float, float]
    return plt.axes(cast(AxesRect, tuple(pos)))


def graphe(
    route: str,
    sens: str | None = None
) -> None:
    """affiche les indicateurs d'état"""
    indicateur = Indicateur(dep=DEP, route=route, sens=sens)
    _, axes = plt.subplots(
        1,
        len(STATES),
        figsize=(6 * len(STATES), 6),
        sharex=True,
        sharey=True
    )
    # on réserve 25% pour les widgets
    plt.subplots_adjust(right=0.75)

    layers = {}
    for state in LAYERS:
        state_layers = get_state(indicateur, state)
        layers[state] = state_layers
    pr_min, pr_max, text_prd_ini, text_prf_ini = get_pr_bounds(layers[STATES[0]][0])

    def update(_=None):
        """filtre sur bornes"""
        try:
            prd = int(text_prd.text)
            prf = int(text_prf.text)
        except TypeError:
            print("vérifiez les PR saisis")
            return
        for ax in axes:
            ax.clear()
        for i, state in enumerate(LAYERS):
            graphe_state(state, layers[state], axes[i], prd=prd, prf=prf)

    # coordonnées des widgets
    pos = [
        0.78, # left
        0.85, # bottom
        0.18, # width
        0.05 # height
    ]
    y_gap = 0.07

    # dynamic filter
    text_prd = TextBox(
        widget_axes(pos),
        'PRD:',
        initial=text_prd_ini
    )
    pos[1] -= y_gap
    text_prf = TextBox(
        widget_axes(pos),
        'PRF:',
        initial=text_prf_ini
    )
    pos[1] -= y_gap
    button = Button(
        widget_axes(pos),
        'Filter',
        hovercolor="#17b835"
    )
    title = f"{route} IQRN {YEAR}"
    if pr_min is not None and pr_max is not None:
        title = f"{title} - données de PR {pr_min} à {pr_max}"
    plt.suptitle(title)
    update()
    button.on_clicked(update)
    plt.show()

graphe("N0088")
