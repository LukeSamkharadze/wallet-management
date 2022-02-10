# Added for root navigation
import os


def get_app_path() -> str:
    return os.path.dirname(os.path.realpath(__file__))
