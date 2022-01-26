"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
import sys

import rich
from rich import pretty
from rich.markdown import Heading, CodeBlock
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

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

dark_background_theme = Theme(friendly_dark.friendly_style)
light_background_theme = Theme(friendly_light.friendly_style)


def init_console(style="dark", theme="dark", color_system="auto", force_jupyter=None):
    def _patch_heading(self, *_args):
        """By default, all headings are centered by Rich; I prefer to have
        them left-justified, except for <h3>
        """
        text = self.text
        text.justify = "left"
        if self.level == 3:
            yield Text("    ") + text
        else:
            yield text

    Heading.__rich_console__ = _patch_heading

    def _patch_code_block(self, *_args):
        code = str(self.text).rstrip()
        if self.lexer_name == "default":
            self.lexer_name = "python"
        syntax = Syntax(code, self.lexer_name, theme=theme, word_wrap=True)
        yield syntax

    CodeBlock.__rich_console__ = _patch_code_block

    if style == "light":
        rich.reconfigure(
            theme=light_background_theme,
            color_system=color_system,
            force_jupyter=force_jupyter,
        )
    else:
        rich.reconfigure(
            theme=dark_background_theme,
            color_system=color_system,
            force_jupyter=force_jupyter,
        )
    console = rich.get_console()
    pretty.install(console=console, indent_guides=True)
    return console
