"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
import inspect
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
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    String,
)
from friendly_styles import friendly_light, friendly_dark
from friendly_traceback import token_utils

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


def is_builtin(string):
    try:
        return inspect.isbuiltin(eval(string))
    except:  # noqa
        return False


def is_exception(string):
    try:
        return issubclass(eval(string), BaseException)
    except:  # noqa
        return False


def simple_line_highlighting(line, line_parts, theme):
    error_style = theme.styles[Error]
    bg, fg = error_style.split(" ")
    bg = bg.split(":")[1]
    error_style = f"{fg} on {bg}"

    background = theme.background_color
    operator_style = f"{theme.styles[Operator]} on {background}"
    number_style = f"{theme.styles[Number]} on {background}"
    code_style = f"{theme.styles[Generic]} on {background}"

    has_line_number = re.match(r"^\s*\d+\s*:", line) or re.match(
        r"^\s*-->\s*\d+\s*:", line
    )
    colon_position = line.find(":")
    highlighting = False
    text = None
    if not line_parts:
        line_parts = [(0, len(line))]
    for begin, end in line_parts:
        if highlighting:
            part = Text(line[begin:end], style=error_style)

        elif has_line_number and begin < colon_position:
            begin_line = line[begin : colon_position + 1]
            arrow_position = begin_line.find("-->")
            if arrow_position != -1:
                part = Text(line[begin : arrow_position + 3], style=operator_style)
                part.append(
                    Text(line[arrow_position + 3 : colon_position], style=number_style)
                )
                part.append(
                    Text(
                        line[colon_position : colon_position + 1], style=operator_style
                    )
                )
                part.append(Text(line[colon_position + 1 : end], style=code_style))
            else:
                part = Text(line[begin:colon_position], style=number_style)
                part.append(
                    Text(
                        line[colon_position : colon_position + 1], style=operator_style
                    )
                )
                part.append(Text(line[colon_position + 1 : end], style=code_style))
        else:
            if line.strip() == "(...)":
                part = Text(line[begin:end], style=operator_style)
            else:
                part = Text(line[begin:end], style=code_style)
        if text is None:
            text = part
        else:
            text.append(part)
        highlighting = not highlighting
    return text


def highlighting_line_by_line(line, line_parts, theme):
    error_style = theme.styles[Error]
    background = theme.background_color
    operator_style = f"{theme.styles[Operator]} on {background}"
    number_style = f"{theme.styles[Number]} on {background}"
    code_style = f"{theme.styles[Name]} on {background}"
    keyword_style = f"{theme.styles[Keyword]} on {background}"
    constant_style = f"{theme.styles[Keyword.Constant]} on {background}"
    comment_style = f"{theme.styles[Comment]} on {background}"
    builtin_style = f"{theme.styles[Name.Builtin]} on {background}"
    exception_style = f"{theme.styles[Generic.Error]} on {background}"
    string_style = f"{theme.styles[String]} on {background}"

    bg, fg = error_style.split(" ")
    bg = bg.split(":")[1]
    error_style = f"{fg} on {bg}"
    highlighting = False
    text = None
    tokens = token_utils.tokenize(line)
    last_column = 0
    for begin, end in line_parts:
        if highlighting:
            part = Text(line[begin:end], style=error_style)
            last_column = end
        else:
            part = None
            for token in tokens:
                if token.start_col < begin:
                    continue
                if token.start_col >= end:
                    if part is None:
                        part = Text(
                            " " * (token.start_col - last_column), style=code_style
                        )
                    else:
                        part.append(
                            Text(
                                " " * (token.start_col - last_column), style=code_style
                            )
                        )
                    last_column = token.start_col
                    break
                if token.start_col > last_column:
                    if part is None:
                        part = Text(
                            " " * (token.start_col - last_column), style=code_style
                        )
                    else:
                        part.append(
                            Text(
                                " " * (token.start_col - last_column), style=code_style
                            )
                        )
                last_column = token.end_col
                if token.is_keyword():
                    if token.string in ["True", "False", "None"]:
                        sub_part = Text(token.string, style=constant_style)
                    else:
                        sub_part = Text(token.string, style=keyword_style)
                elif is_builtin(token.string):
                    sub_part = Text(token.string, style=builtin_style)
                elif is_exception(token.string):
                    sub_part = Text(token.string, style=exception_style)
                elif token.is_comment():
                    sub_part = Text(token.string, style=comment_style)
                elif token.is_number():
                    sub_part = Text(token.string, style=number_style)
                elif token.is_operator():
                    sub_part = Text(token.string, style=operator_style)
                elif token.is_string():
                    sub_part = Text(token.string, style=string_style)
                else:
                    sub_part = Text(token.string, style=code_style)
                if part is None:
                    part = sub_part
                else:
                    part.append(sub_part)
        if text is None:
            text = part
        else:
            text.append(part)
        highlighting = not highlighting
    return text


def init_console(theme=friendly_dark, color_system="auto", force_jupyter=None):
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
        if self.lexer_name == "default":
            self.lexer_name = "python"
        code = str(self.text).rstrip()

        lines = code.split("\n")
        error_lines = get_highlighting_range(lines)
        tokens = token_utils.tokenize(code)
        no_multiline_string = True
        for token in tokens:
            if token.start_row != token.end_row:
                no_multiline_string = False
                break
        if not USE_CARETS and self.lexer_name == "python" and error_lines:
            for index, line in enumerate(lines):
                if index in error_lines:
                    continue
                if index + 1 in error_lines:
                    if no_multiline_string:
                        yield highlighting_line_by_line(
                            line, error_lines[index + 1], theme
                        )
                    else:
                        yield simple_line_highlighting(
                            line, error_lines[index + 1], theme
                        )
                else:
                    if no_multiline_string:
                        yield Syntax(line, self.lexer_name, theme=theme, word_wrap=True)
                    else:
                        yield simple_line_highlighting(line, None, theme)
        else:
            yield Syntax(code, self.lexer_name, theme=theme, word_wrap=True)

    CodeBlock.__rich_console__ = _patch_code_block

    if theme == friendly_light:
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
