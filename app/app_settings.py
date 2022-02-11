from configparser import ConfigParser

from app.utils import get_root_path

root_dir = get_root_path()
conf = ConfigParser()
conf.read(root_dir + "//app_settings.ini")


class AppSettings:
    _config: ConfigParser

    def __init__(self) -> None:
        self._config = conf

    def get_config(self) -> ConfigParser:
        return self._config
