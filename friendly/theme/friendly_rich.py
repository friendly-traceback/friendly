"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
import re
import sys

from ..utils import get_highlighting_range

import rich
from rich import pretty
from rich.markdown import Heading, CodeBlock
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

from pygments import styles
from pygments.token import Error
from friendly_styles import friendly_light, friendly_dark
from friendly_traceback import debug_helper

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

USE_CARETS = False


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

        lines = [line for line in code.split("\n")]
        error_lines = get_highlighting_range(lines)

        if (
            debug_helper.DEBUG
            and not USE_CARETS
            and self.lexer_name == "python"
            and error_lines
        ):
            if theme == "dark":
                error_style = friendly_dark.styles[Error]
            else:
                error_style = friendly_light.styles[Error]
            bg, fg = error_style.split(" ")
            bg = bg.split(":")[1]
            error_style = f"{fg} on {bg}"

            for index, line in enumerate(lines):
                if index in error_lines:
                    continue
                has_line_number = re.match(r"^\s*\d+\s*:", line) or re.match(
                    r"^\s*-->\s*\d+\s*:", line
                )
                colon_position = line.find(":")
                if index + 1 in error_lines:
                    highlighting = False
                    text = None
                    for begin, end in error_lines[index + 1]:
                        if highlighting:
                            part = Text(line[begin:end], style=error_style)
                        else:
                            if has_line_number and begin < colon_position:
                                begin_line = line[begin : colon_position + 1]
                                arrow_position = begin_line.find("-->")
                                if arrow_position != -1:
                                    part = Text(
                                        line[begin : arrow_position + 3],
                                        style="operators",
                                    )
                                    part.append(
                                        Text(
                                            line[arrow_position + 3 : colon_position],
                                            style="repr.number",
                                        )
                                    )
                                else:
                                    part = Text(
                                        line[begin:colon_position], style="repr.number"
                                    )
                                part.append(
                                    Text(
                                        line[colon_position : colon_position + 1],
                                        style="operators",
                                    )
                                )
                                part.append(
                                    Text(
                                        line[colon_position + 1 : end],
                                        style="markdown.code",
                                    )
                                )
                            else:
                                part = Text(line[begin:end], style="markdown.code")
                        if text is None:
                            text = part
                        else:
                            text.append(part)
                        highlighting = not highlighting
                    yield text
                else:
                    yield Syntax(line, self.lexer_name, theme=theme, word_wrap=True)
        else:
            yield Syntax(code, self.lexer_name, theme=theme, word_wrap=True)

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
