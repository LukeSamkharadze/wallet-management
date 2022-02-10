import os


def get_root_path() -> str:
    root_dir = os.path.dirname(os.path.abspath("root_file.py"))
    return root_dir
