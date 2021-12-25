"""In this module, we modify the basic console helpers for friendly-traceback
to add custom ones for Rich-based formatters."""

from friendly_traceback.console_helpers import *  # noqa; include Friendly below
from friendly_traceback.console_helpers import Friendly, helpers
from friendly_traceback.functions_help import add_help_attribute, short_description
from friendly_traceback.config import session

old_set_lang = set_lang  # noqa

from friendly.my_gettext import current_lang
from friendly import set_lang, view_saved

# The following is different from the one imported via the import * above
from friendly import set_formatter

_ = current_lang.translate
old_history = history  # noqa


def history():
    session.rich_add_vspace = False
    old_history()
    session.rich_add_vspace = True


history.__doc__ = old_history.__doc__
set_lang.__doc__ = old_set_lang.__doc__
helpers["history"] = history
helpers["set_formatter"] = set_formatter
helpers["set_lang"] = set_lang
add_help_attribute(
    {"set_formatter": set_formatter, "history": history, "set_lang": set_lang}
)

Friendly.add_helper(history)
Friendly.add_helper(set_formatter)
Friendly.add_helper(set_lang)
# =================================
# Additional rich-specific helpers
# =================================


def dark():
    """Synonym of set_formatter('dark') designed to be used
    within iPython/Jupyter programming environments.
    """
    set_formatter("dark")


def light():
    """Synonym of set_formatter('light') designed to be used
    within iPython/Jupyter programming environments.
    """
    set_formatter("light")


def plain():
    """Synonym of set_formatter('plain').
    Monochrome output without using Rich.
    """
    set_formatter("plain")


def set_width(width=80):
    """Sets the width in a iPython/Jupyter session using 'light' or 'dark' mode"""
    try:
        session.console.width = width
    except Exception:  # noqa
        print(_("set_width() has no effect with this formatter."))
        return
    session.rich_width = width
    if session.is_jupyter:
        if (
            session.rich_tb_width is not None
            and session.rich_width > session.rich_tb_width
        ):
            session.rich_tb_width = width


short_description["dark"] = lambda: _(
    "Sets a colour scheme designed for a black background."
)
short_description["light"] = lambda: _(
    "Sets a colour scheme designed for a white background."
)
short_description["plain"] = lambda: _("Plain formatting, with no colours added.")
short_description["set_width"] = lambda: _("Sets the output width in some modes.")
short_description["view_saved"] = lambda : _("Prints the saved configuration.")
local_helpers = {"dark": dark, "light": light, "plain": plain, "set_width": set_width, "view_saved": view_saved}
add_help_attribute(local_helpers)
for helper in local_helpers:
    Friendly.add_helper(local_helpers[helper])

helpers.update(local_helpers)
__all__ = list(helpers.keys())
