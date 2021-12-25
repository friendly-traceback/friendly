"""Configuration file exclusively for friendly -- not for friendly-traceback"""

import configparser
import os
import sys

from appdirs import user_config_dir

app_name = "Friendly"
app_author = "AndreRoberge"  # No accent on André in case it messes with local encoding
config_dir = user_config_dir(app_name, app_author)
FILENAME = os.path.join(config_dir, "friendly.ini")


def ensure_existence():
    """Ensures that a configuration file exists"""
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(FILENAME):
        config = configparser.ConfigParser()
        with open(FILENAME, "w") as config_file:
            config.write(config_file)


# Perhaps friendly will be used in environments where the user cannot
# create configuration directories and files
try:
    ensure_existence()
except Exception:
    FILENAME = None


def read(*, key=None, environment=None):
    """Returns the value of a key in the current environment"""
    if FILENAME is None:
        return
    if environment is None:
        section = "common"
    else:
        section = environment.lower()
    key = key.lower()
    config = configparser.ConfigParser()
    config.read(FILENAME)
    if section in config and key in config[section]:
        return config[section][key]
    return


def write(*, key=None, value=None, environment=None):
    """Updates the value of a key in the current environment.

    If the section does not already exist, it is created.
    """
    if FILENAME is None:
        return
    if environment is None:
        section = "common"
    else:
        section = environment.lower()
    key = key.lower()
    value = value.lower()

    config = configparser.ConfigParser()
    config.read(FILENAME)
    if not config.has_section(section):
        config.add_section(section)
    config[section][key] = value
    with open(FILENAME, "w") as config_file:
        config.write(config_file)


def view_saved():
    """View the contents of the file for the configuration"""
    config = configparser.ConfigParser()
    config.read(FILENAME)
    config.write(sys.stdout)
