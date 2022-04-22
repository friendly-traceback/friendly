"""Mu's repl uses an IPython QtConsole.
Mu has three themes designated (in English) as 'day', 'night',
and 'high contrast'."""

import json
import os

import appdirs
import colorama  # noqa
from friendly_traceback import set_stream
from friendly_traceback import set_formatter as ft_set_formatter
from friendly_traceback.config import session, did_exception_occur_before  # noqa
from friendly_traceback.functions_help import add_help_attribute, short_description

from ..my_gettext import current_lang  # noqa
from friendly.ipython_common import excepthook
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import Friendly, helpers
from friendly import print_repl_header
from friendly import settings
from friendly import theme
from friendly import rich_formatters

colorama.deinit()  # reset needed on Windows
colorama.init(convert=False, strip=False)
_ = current_lang.translate

settings.ENVIRONMENT = "mu"
mu_data_dir = appdirs.user_data_dir(appname="mu", appauthor="python")


def set_formatter(formatter=None, background=None):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    settings.write(option="formatter", value=formatter)
    if background is not None:
        settings.write(option="background", value=background)
    if formatter in ["colourful", "day", "night"]:
        style = "light" if formatter == "day" else "dark"
        session.console = theme.init_rich_console(
            style=style,
            color_system="truecolor",
            force_jupyter=False,
            background=background,
        )
        session.use_rich = True
        session.rich_add_vspace = True
        formatter = rich_formatters.rich_markdown
        set_stream(redirect=rich_formatters.rich_writer)
    else:
        session.use_rich = False
        session.rich_add_vspace = False
        set_stream()
    ft_set_formatter(formatter=formatter)


def set_width(width=80):
    """Sets the width in a iPython/Jupyter session using 'light' or 'dark' mode"""
    if session.use_rich:
        session.console._width = width
    else:
        print(
            _("set_width() is only available using 'day', 'night' or 'colourful' mode.")
        )


add_help_attribute({"set_formatter": set_formatter, "set_width": set_width})
Friendly.add_helper(set_formatter)
Friendly.add_helper(set_width)
helpers["set_formatter"] = set_formatter
helpers["set_width"] = set_width


# ========= Replacing theme-based formatters
del helpers["dark"]
del helpers["light"]
del helpers["plain"]
Friendly.remove_helper("dark")
Friendly.remove_helper("light")
Friendly.remove_helper("plain")


def day():
    """Day theme for Mu's REPL"""
    set_formatter("day", background="#FEFEF7")


def night():
    """Night theme for Mu's REPL"""
    set_formatter("night", background="#373737")


def colourful():
    """Colourful theme with black background."""
    set_formatter("colourful", background="#000000")


def contrast():
    """White text on black background."""
    set_formatter("repl", background="#000000")


short_description["day"] = lambda: _("Colour scheme designed for Mu's day theme.")
short_description["night"] = lambda: _("Colour scheme designed for Mu's night theme.")
short_description["colourful"] = lambda: _(
    "Colourful scheme with black background suitable for Mu's high contrast theme."
)
short_description["contrast"] = lambda: _(
    "White text on black background; suitable for Mu's high contrast theme."
)
local_helpers = {
    "day": day,
    "night": night,
    "colourful": colourful,
    "contrast": contrast,
}
add_help_attribute(local_helpers)

for helper in local_helpers:
    Friendly.add_helper(local_helpers[helper])
helpers.update(local_helpers)
__all__ = list(helpers.keys())


excepthook.enable()

try:
    with open(os.path.join(mu_data_dir, "session.json")) as fp:
        mu_settings = json.load(fp)
except FileNotFoundError:
    mu_settings = {}

if "theme" in mu_settings:
    mu_theme = mu_settings["theme"]
    if mu_theme == "day":
        day()
    elif mu_theme == "night":
        night()
    elif settings.has_environment("mu"):
        formatter = settings.read(option="formatter")
        background = settings.read(option="background")
        if formatter == "dark" and background == "#000000":
            colourful()
        else:
            contrast()
    else:
        contrast()
else:
    day()
if "locale" in mu_settings:
    set_lang(mu_settings["locale"])  # noqa
elif settings.has_environment("common"):
    lang = settings.read(option="lang")
    if lang is not None:
        set_lang(lang)  # noqa

print_repl_header()
if did_exception_occur_before():
    friendly_tb()  # noqa
