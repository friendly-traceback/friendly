"""In this module, we modify the basic console helpers for friendly-traceback
so as to add custom ones for Rich-based formatters."""

from friendly_traceback.console_helpers import *  # noqa

old_set_formatter = set_formatter  # noqa
old_history = history  # noqa
old_set_lang = set_lang  # noqa

from friendly_traceback.console_helpers import FriendlyHelpers, helpers
from friendly_traceback.utils import add_rich_repr
from friendly_traceback.config import session

from friendly.my_gettext import current_lang
from friendly import set_formatter

_ = current_lang.translate

# =============================================
# Modifying existing console helpers
# =============================================

set_formatter.help = old_set_formatter.help  # noqa
set_formatter.__rich_repr__ = old_set_formatter.__rich_repr__  # noqa
FriendlyHelpers.set_formatter = set_formatter
helpers["set_formatter"] = set_formatter


def history():
    session.rich_add_vspace = False
    old_history()
    session.rich_add_vspace = True


history.help = old_history.help  # noqa
history.__rich_repr__ = old_history.__rich_repr__  # noqa
history.__doc__ = old_history.__doc__
helpers["history"] = history


def set_lang(lang):
    old_set_lang(lang)
    current_lang.install(lang)


set_lang.help = old_set_lang.help  # noqa
set_lang.__rich_repr__ = old_set_lang.__rich_repr__  # noqa
set_lang.__doc__ = old_set_lang.__doc__
helpers["set_lang"] = set_lang


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


def set_width(width=80):
    """Sets the width in a iPython/Jupyter session using 'light' or 'dark' mode"""
    try:
        session.console.width = width
    except Exception:
        print(_("set_width() is only available using 'light' or 'dark' mode."))


dark.help = lambda: _("Sets a colour scheme designed for a black background.")
light.help = lambda: _("Sets a colour scheme designed for a white background.")
set_width.help = lambda: _("Sets the output width in some modes.")

local_helpers = {"dark": dark, "light": light, "set_width": set_width}
add_rich_repr(local_helpers)

for helper in local_helpers:
    setattr(FriendlyHelpers, helper, staticmethod(local_helpers[helper]))
Friendly = FriendlyHelpers(local_helpers=local_helpers)
setattr(Friendly, "history", history)

helpers["Friendly"] = Friendly
helpers.update(local_helpers)
__all__ = list(helpers.keys())
