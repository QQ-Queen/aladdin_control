from abc import ABC, abstractmethod

__all__ = [
    "ApplicationConfig",
    ]

#
# Internals
#

class Config(ABC):
    @abstractmethod
    def config_as_dict(self):
        pass


class ApplicationConfig(Config):
    def __init__(self, path):
        self._path = path

    def __str__(self):
        """Return the string representation of the path of config file"""
        try:
            return self._str
        except AttributeError:
            self._str = self._path
            return self._str

    @property
    def config_as_dict(self):
        try:
            return self._config_as_dict
        except AttributeError:
            self._config_as_dict = self._load_config()

    def _load_config(self):
        pass
#
# Public API
#