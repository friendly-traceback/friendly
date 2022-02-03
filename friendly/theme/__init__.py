"""Syntax colouring based on the availability of pygments
"""
import sys

from . import friendly_pygments
from . import friendly_rich
from . import patch_tb_lexer  # noqa will automatically Monkeypatch
from .colours import validate_color


def init_rich_console(
    style="dark", color_system="auto", force_jupyter=None, background=None
):
    try:
        background = validate_color(background)
    except ValueError as e:
        print(e.args[0])
        background = None

    if style == "light":
        theme = friendly_pygments.friendly_light
        if background is not None:
            friendly_pygments.friendly_light.background_color = background
    else:
        theme = friendly_pygments.friendly_dark
        if background is not None:
            friendly_pygments.friendly_dark.background_color = background
    friendly_pygments.CURRENT_THEME = theme

    return friendly_rich.init_console(
        theme=theme, color_system=color_system, force_jupyter=force_jupyter
    )


def disable_rich():
    try:  # are we using IPython ?
        # get_ipython is an IPython builtin which returns the current instance.
        ip = get_ipython()  # noqa
        from IPython.core.formatters import PlainTextFormatter  # noqa

        ip.display_formatter.formatters["text/plain"] = PlainTextFormatter()
    except NameError:
        sys.displayhook = sys.__displayhook__
