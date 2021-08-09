"""Mu's repl uses an IPython QtConsole.
Mu has three themes designated (in English) as 'day', 'night',
and 'high contrast'."""

import colorama  # noqa
from friendly_traceback import set_stream
from friendly_traceback import set_formatter as ft_set_formatter
from friendly_traceback.config import session  # noqa
from friendly_traceback.functions_help import add_help_attribute, short_description

from ..my_gettext import current_lang  # noqa
from friendly.ipython import *  # noqa  # Will automatically install
from friendly.rich_console_helpers import Friendly, helpers
from friendly import theme
from friendly import rich_formatters

colorama.deinit()  # reset needed on Windows
colorama.init(convert=False, strip=False)
_ = current_lang.translate


def set_formatter(formatter=None, background=None):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    if formatter in ["black", "day", "night"]:
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
        print(_("set_width() is only available using 'day', 'night' or 'black' mode."))


add_help_attribute({"set_formatter": set_formatter, "set_width": set_width})
Friendly.add_helper("set_formatter", set_formatter)
Friendly.add_helper("set_width", set_width)
helpers["set_formatter"] = set_formatter
helpers["set_width"] = set_width


# ========= Replacing theme-based formatters
del helpers["dark"]
del helpers["light"]
Friendly.remove_helper("dark")
Friendly.remove_helper("light")


def day():
    """Day theme for Mu's REPL"""
    set_formatter("day", background="#FEFEF7")


def night():
    """Night theme for Mu's REPL"""
    set_formatter("night", background="#373737")


def black():
    """Colourful theme with black background."""
    set_formatter("black", background="#000000")


def bw():
    """Black and white."""
    set_formatter("repl", background="#000000")


short_description["day"] = lambda: _("Colour scheme designed for Mu's day theme.")
short_description["night"] = lambda: _("Colour scheme designed for Mu's night theme.")
short_description["black"] = lambda: _(
    "Colourful scheme designed for Mu's high contrast theme."
)
short_description["bw"] = lambda: _(
    "Black and white scheme designed for Mu's high contrast theme."
)
local_helpers = {"day": day, "night": night, "black": black, "bw": bw}
add_help_attribute(local_helpers)

for helper in local_helpers:
    Friendly.add_helper(helper, local_helpers[helper])
helpers.update(local_helpers)
__all__ = list(helpers.keys())
day()
