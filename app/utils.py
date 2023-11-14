import os


def get_repository_abspath() -> str | None:
    current_path = os.getcwd()
    while os.path.abspath(current_path) != "/":
        gut_repo_path = os.path.join(current_path, ".gut/")
        if os.path.exists(gut_repo_path):
            return gut_repo_path
        else:
            current_path = os.path.dirname(current_path)
