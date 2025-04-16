"""Module de méthodes partagées."""
import os
import inquirer

class CheckForFiles:
    """Recherche fichiers suivant extension"""
    def __init__(self) -> None:
        """Initialize."""
        self.names: list[str] = []

    def get_names(self) -> list[str]:
        "Return list of files paths."
        return self.names

    def filter_extension(self, folder_path, ext="lite") -> None:
        """Filter files with extension ext."""
        folder_path = os.path.abspath(folder_path)
        for name in [name for name in os.listdir(folder_path) if name not in [".",".."]]:
            full_path = os.path.join(folder_path, name)
            if os.path.isfile(full_path) and name.split(".")[-1] == ext:
                self.names.append(full_path)
            if os.path.isdir(full_path):
                self.filter_extension(full_path, ext=ext)

def pick_file(folder_path="datas", ext="csv", **kwargs) -> str:
    """choix d'un fichier de données"""
    message = kwargs.get(
        "message",
        f"choix du fichier {ext}?"
    )
    data_files = CheckForFiles()
    data_files.filter_extension(
        folder_path=folder_path,
        ext=ext
    )
    question = [
        inquirer.List(
            "data_file",
            message=message,
            choices=data_files.get_names(),
        )
    ]
    return inquirer.prompt(question)["data_file"]

def pick_files(**kwargs) -> dict[str, str]:
    """choix de fichiers de données
    il faut passer en arguments des dictionnaires
    clés obligatoires : folder_path et ext
    clé facultative : message (de la question)
    """
    questions = []
    for question_key, question in kwargs.items():
        if not isinstance(question, dict):
            continue
        if "folder_path" not in question:
            continue
        if "ext" not in question:
            continue
        folder_path = question["folder_path"]
        ext = question["ext"]
        message = question.get(
            "message",
            f"choix du fichier {ext}?"
        )
        data_files = CheckForFiles()
        data_files.filter_extension(
            folder_path=folder_path,
            ext=ext
        )
        questions.append(
            inquirer.List(
                question_key,
                message=message,
                choices=data_files.get_names(),
            )
        )
    return inquirer.prompt(questions)
