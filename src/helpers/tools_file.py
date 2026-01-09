
"""File utilities."""
import os
import yaml

def parent_dir(path, levels=1) -> str:
    """Retourne le path du répertoire parent 
    jusqu'au niveau fourni en argument
    """
    for _ in range(levels):
        path = os.path.dirname(path)
    return path

class CheckConf():
    """Manage configuration.yaml."""
    def __init__(self) -> None:
        """Load configuration.yaml."""
        self.yaml: dict = {}
        self.src_path = parent_dir(__file__, 2)
        yaml_path = f"{self.src_path}/configuration.yml"
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                self.yaml = dict(yaml.safe_load(f))

    def get_keys(self) -> list:
        """Retourne toutes les clés présentes dans le yaml."""
        return list(self.yaml.keys())

    def get_mean_step(self) -> int:
        """retourne mean_step"""
        mean_step = self.yaml.get("mean_step")
        if mean_step is not None:
            return mean_step
        return 200

    def get_log_level(self, name: str) -> str:
        """Retourne le niveau de logging pour le module."""
        log_conf = dict(self.yaml.get("logging", {}))
        return str(log_conf.get(name, "INFO")).upper()

    def get_backgound_alpha(self, level: str) -> float:
        """Retourne la transparence d'un niveau"""
        conf = dict(self.yaml.get("background_alpha", {}))
        return float(conf.get(level, 0))

    def get_datas_folder(self) -> str:
        """retourne le path vers les datas"""
        sub_folder = self.yaml.get("datas")
        if sub_folder is not None:
            return f"{self.src_path}/datas/{sub_folder}"
        return f"{self.src_path}/datas"

    def view_legend(self) -> bool:
        """Affiche les légendes ou non."""
        show = self.yaml.get("legend")
        if show is not None:
            return bool(show)
        return True

    def aigle3d_xls(self) -> str:
        """Retourne le path vers le fichier excel Aigle3D contenant les états"""
        aigle_xls = self.yaml.get("aigle_xls")
        if aigle_xls is not None:
            return f"{self.src_path}/datas/{aigle_xls}"
        return f"{self.src_path}/datas/Aigle3D/Table_Indicateurs_Etat_surface_DIRMC.xlsx"

    def pr_abs_csv(self) -> str | None:
        """Retourne le path vers le csv contenant les données pr+abs"""
        pr_abs_csv = self.yaml.get("pr_abs_csv")
        if pr_abs_csv is not None:
            return f"{self.src_path}/datas/{pr_abs_csv}"
        return None
