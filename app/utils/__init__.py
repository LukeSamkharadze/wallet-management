from app.root_file import get_app_path


def get_root_path() -> str:
    root_dir = get_app_path()
    return root_dir
