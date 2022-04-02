import yaml
from yaml import Loader

LINEAR = "#linear-supporters:matrix.org"
QUADRATIC = "#quadratic-supporters:matrix.org"
POLYNOMIAL = "#polynomial-supporters:matrix.org"
ELLIPTIC = "#elliptic-supporters:matrix.org"


class YamlGuestList:
    """YAML-backed guest list - keep the config out of code :) :) :)"""

    def __init__(self, filename):
        with open(filename) as guest_list_file:
            self._yaml_config = yaml.load(stream=guest_list_file, Loader=Loader)

    def guest_list(self):
        """Return a guest list generated from the YAML config file"""
        return {
            LINEAR: [(user, True) for user in self._yaml_config[LINEAR]]
            + [(user, False) for user in self._yaml_config[QUADRATIC]]
            + [(user, False) for user in self._yaml_config[POLYNOMIAL]]
            + [(user, False) for user in self._yaml_config[ELLIPTIC]],
            QUADRATIC: [(user, True) for user in self._yaml_config[QUADRATIC]]
            + [(user, False) for user in self._yaml_config[POLYNOMIAL]]
            + [(user, False) for user in self._yaml_config[ELLIPTIC]],
            POLYNOMIAL: [(user, True) for user in self._yaml_config[POLYNOMIAL]]
            + [(user, False) for user in self._yaml_config[ELLIPTIC]],
            ELLIPTIC: [(user, True) for user in self._yaml_config[ELLIPTIC]],
        }
