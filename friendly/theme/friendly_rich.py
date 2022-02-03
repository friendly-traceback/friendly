"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
import inspect
import re

from .friendly_pygments import friendly_dark, friendly_light
from . import colours
from ..utils import get_highlighting_range

import rich
from rich import pretty
from rich.markdown import Heading, CodeBlock
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

from pygments.token import Comment, Generic, Keyword, Name, Number, Operator, String

from friendly_traceback import token_utils

dark_background_theme = Theme(friendly_dark.friendly_style)
light_background_theme = Theme(friendly_light.friendly_style)


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
    error_style = colours.get_highlight()

    background = theme.background_color
    operator_style = f"{theme.styles[Operator]} on {background}"
    number_style = f"{theme.styles[Number]} on {background}"
    code_style = f"{theme.styles[Name]} on {background}"

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
            else:
                part = Text(line[begin:colon_position], style=number_style)
            part.append(
                Text(line[colon_position : colon_position + 1], style=operator_style)
            )
            part.append(Text(line[colon_position + 1 : end], style=code_style))
        elif line.strip() == "(...)":
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

    error_style = colours.get_highlight()
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
        elif part is not None:  # None can happen for EOF
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

        # As we might process line by line, the tokenization will not work
        # when multiline docstrings appear; we thus exclude them from our
        # token by token highlighting.
        problem_lines = []
        for index, line in enumerate(lines):
            if token_utils.untokenize(token_utils.tokenize(line)) != line:
                problem_lines.append(index)
        if problem_lines:
            problem_lines = list(range(problem_lines[0], problem_lines[-1] + 1))
        error_lines = get_highlighting_range(lines)

        if (
            colours.get_highlight() is not None  # use carets
            and self.lexer_name == "python"  # do not process pytb
            and error_lines
        ):
            for index, line in enumerate(lines):
                if index in error_lines:
                    continue
                if index + 1 in error_lines:
                    if index in problem_lines:
                        yield simple_line_highlighting(
                            line, error_lines[index + 1], theme
                        )
                    else:
                        yield highlighting_line_by_line(
                            line, error_lines[index + 1], theme
                        )
                else:
                    if index in problem_lines:
                        yield simple_line_highlighting(line, [], theme)
                    else:
                        yield Syntax(line, self.lexer_name, theme=theme, word_wrap=True)
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
