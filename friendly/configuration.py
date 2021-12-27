"""Configuration file exclusively for friendly -- not for friendly-traceback"""

import configparser
import os
import sys

from friendly_traceback import debug_helper
from appdirs import user_config_dir

app_name = "Friendly"
app_author = "AndreRoberge"  # No accent on André in case it messes with local encoding
config_dir = user_config_dir(app_name, app_author)
FILENAME = os.path.join(config_dir, "friendly.ini")

# I tried to install psutil to determine the kind of terminal (if any)
# that friendly was running in, but the installation failed.
# So I resort to a simpler way of determining the terminal if possible.
# For terminals, the assumption is that a single background color will
# be used for a given terminal type.

if "TERM_PROGRAM" in os.environ:  # used by VS Code
    terminal_type = os.environ["TERM_PROGRAM"]
elif "TERMINAL_EMULATOR" in os.environ:  # used by PyCharm
    terminal_type = os.environ["TERMINAL_EMULATOR"]
elif "TERM" in os.environ:  # Unix?
    terminal_type = os.environ["TERM"]
elif sys.platform == "win32":
    # The following might not be reliable.
    _ps = len(os.getenv("PSModulePath", "").split(os.pathsep))
    if _ps == 3:
        terminal_type = "powershell"
    elif _ps == 2:
        terminal_type = "cmd"
    else:
        terminal_type = ""
else:
    terminal_type = ""

ENVIRONMENT = None
# ENVIRONMENT is determined by the "flavour" of friendly.
# If a terminal type is identified, then the ENVIRONMENT variable
# would usually be a combination of the terminal_type and the flavour.


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
except Exception:  # noqa
    FILENAME = None


def read(*, option="unknown", environment=None):
    """Returns the value of a key in the current environment"""
    if FILENAME is None:
        return
    if environment is not None:
        section = environment
    elif ENVIRONMENT is not None:
        section = ENVIRONMENT
    else:
        section = "unknown"
        debug_helper.log("Unknown section")
    config = configparser.ConfigParser()
    config.read(FILENAME)
    if section in config and option in config[section]:
        return config[section][option]
    return


def write(*, option="unknown", value="unknown", environment=None):
    """Updates the value of a key in the current environment.

    If the section does not already exist, it is created.
    """
    if FILENAME is None:
        return
    if environment is not None:
        section = environment
    elif ENVIRONMENT is not None:
        section = ENVIRONMENT
    else:
        section = "unknown"

    config = configparser.ConfigParser()
    config.read(FILENAME)
    if not config.has_section(section):
        config.add_section(section)
    config[section][option] = value
    with open(FILENAME, "w") as config_file:
        config.write(config_file)


def remove_option(option, environment=None):
    if FILENAME is None:
        return
    if environment is not None:
        section = environment
    elif ENVIRONMENT is not None:
        section = ENVIRONMENT
    else:
        section = "unknown"
    config = configparser.ConfigParser()
    config.read(FILENAME)
    if config.has_section(section):
        if config.has_option(section, option):
            config.remove_option(section, option)
    with open(FILENAME, "w") as config_file:
        config.write(config_file)


def has_environment(environment=None):
    """Returns True if a section in the configuration file has already been set
    for this environment.
    """
    if FILENAME is None:
        return False
    if environment is not None:
        section = environment
    else:
        section = ENVIRONMENT
    config = configparser.ConfigParser()
    config.read(FILENAME)
    return config.has_section(section)


def print_settings():
    """Prints the contents of the configuration file"""
    config = configparser.ConfigParser()
    config.read(FILENAME)
    config.write(sys.stdout)
