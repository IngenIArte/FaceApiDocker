import os
from configparser import ConfigParser


def is_windows():
    return os.name == "nt"


def load_config(configpath):
    config = ConfigParser()
    config.read(configpath)
    for sk, sv in config.items():
        for ik, iv in sv.items():
            key_name = f"{sk}_{ik}".upper()
            os.environ[key_name] = iv


def convert_to_boolean(value):
    return ConfigParser()._convert_to_boolean(value)
