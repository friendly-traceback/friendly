"""Syntax colouring based on the availability of pygments
"""
from pygments import styles

from . import friendly_rich
from . import patch_tb_lexer  # noqa will automatically Monkeypatch
from ..my_gettext import current_lang

friendly_light = styles.get_style_by_name("friendly_light")
friendly_dark = styles.get_style_by_name("friendly_dark")
CURRENT_THEME = "friendly_light"


def validate_color(color):
    _ = current_lang.translate
    if color is None:
        return None
    valid_characters = set("0123456789abcdefABCDEF")
    if (
        isinstance(color, str)
        and color.startswith("#")
        and len(color) == 7
        and set(color[1:]).issubset(valid_characters)
    ):
        return color
    print(
        _("Invalid color {color}.\nColors must be of the form #dddddd.").format(
            color=color
        )
    )


def init_rich_console(
    style="dark", color_system="auto", force_jupyter=None, background=None
):
    global CURRENT_THEME
    background = validate_color(background)
    if style == "light":
        theme = "friendly_light"
        if background is not None:
            friendly_light.background_color = background
    else:
        theme = "friendly_dark"
        if background is not None:
            friendly_dark.background_color = background
    CURRENT_THEME = theme

    return friendly_rich.init_console(
        style=style, theme=theme, color_system=color_system, force_jupyter=force_jupyter
    )
