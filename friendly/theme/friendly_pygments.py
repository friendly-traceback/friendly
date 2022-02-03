import sys

from pygments import styles
from friendly_styles import friendly_light, friendly_dark

# When friendly is imported in environments that have previously
# imported Pygments, the styles defined in friendly_styles do not
# get automatically added to the list of available styles from pygments,
# and we must "patch" the existing list.
sys.modules["pygments.styles.friendly_light"] = friendly_light
styles.STYLE_MAP["friendly_light"] = "friendly_light::FriendlyLightStyle"
friendly_light = styles.get_style_by_name("friendly_light")

sys.modules["pygments.styles.friendly_dark"] = friendly_dark
styles.STYLE_MAP["friendly_dark"] = "friendly_dark::FriendlyDarkStyle"
friendly_dark = styles.get_style_by_name("friendly_dark")

# The following global variable can be changed from other modules.
# Yes, I know, global variables are not a good idea.
CURRENT_THEME = friendly_dark

default_dark_background_colour = friendly_dark.background_color
default_light_background_colour = friendly_light.background_color


def get_default_background_color():
    if CURRENT_THEME == friendly_dark:
        return default_dark_background_colour
    else:
        return default_light_background_colour


def set_pygments_background_color(color):
    if color is None:
        CURRENT_THEME.background_color = get_default_background_color()
        return get_default_background_color()

    CURRENT_THEME.background_color = color
    return color
