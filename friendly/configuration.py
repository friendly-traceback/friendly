"""Configuration file exclusively for friendly -- not for friendly-traceback"""

import configparser
import os

from appdirs import user_config_dir
from friendly_traceback import debug_helper

app_name = "Friendly"
app_author = "AndreRoberge"  # No accent on André in case it messes with local encoding
config_dir = user_config_dir(app_name, app_author)
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

FILENAME = os.path.join(config_dir, "friendly.ini")
# The following can be changed elsewhere to take other values such as mu, jupyter, idle, ipython, etc.
ENVIRONMENT = "friendly"


def ensure_existence():
    """Ensures that a configuration file exists"""
    if not os.path.exists(FILENAME):
        config = configparser.ConfigParser()
        with open(FILENAME, "w") as config_file:
            config.write(config_file)


ensure_existence()


def read(key=None):
    """Returns the value of a key in the current environment"""
    if key is None:
        debug_helper.log("Attempting to read None in configuration.py")
        return

    section = ENVIRONMENT.lower()
    key = key.lower()
    config = configparser.ConfigParser()
    config.read(FILENAME)
    if section in config and key in config[section]:
        return config[section][key]
    return None


def write(key=None, value=None):
    """Updates the value of a key in the current environment.

    If the section does not already exist, it is created.
    """
    if key is None or value is None:
        debug_helper.log("Attempting to write None in configuration.py")
        return
    section = ENVIRONMENT.lower()
    key = key.lower()
    value = value.lower()

    config = configparser.ConfigParser()
    config.read(FILENAME)
    if not config.has_section(section):
        config.add_section(section)
    config[section][key] = value
    with open(FILENAME, "w") as config_file:
        config.write(config_file)
