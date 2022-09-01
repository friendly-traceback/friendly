"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
import builtins
import inspect

from .friendly_pygments import friendly_dark, friendly_light
from . import colours
from friendly_traceback.utils import get_highlighting_ranges

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
    if string.strip() not in dir(builtins):
        return False
    try:
        return inspect.isbuiltin(eval(string.strip()))
    except:  # noqa
        return False


def is_exception(string):
    if string.strip() not in dir(builtins):
        return False
    try:
        return issubclass(eval(string.strip()), BaseException)
    except:  # noqa
        return False


class MultilineString:
    def __init__(self, begin_col=None, begin_line=None, end_col=None, end_line=None):
        self.begin_col = begin_col
        self.begin_line = begin_line - 1
        self.end_col = end_col
        self.end_line = end_line - 1


class ColourHighlighter:
    def __init__(self, theme):
        self.theme = theme
        background = theme.background_color
        self.operator_style = f"{theme.styles[Operator]} on {background}"
        self.number_style = f"{theme.styles[Number]} on {background}"
        self.code_style = f"{theme.styles[Name]} on {background}"
        self.keyword_style = f"{theme.styles[Keyword]} on {background}"
        self.constant_style = f"{theme.styles[Keyword.Constant]} on {background}"
        self.comment_style = f"{theme.styles[Comment]} on {background}"
        self.builtin_style = f"{theme.styles[Name.Builtin]} on {background}"
        self.exception_style = f"{theme.styles[Generic.Error]} on {background}"
        self.string_style = f"{theme.styles[String]} on {background}"
        self.error_style = colours.get_highlight()

    def split_lineno_from_code(self, lines):
        # Also remove lines of markers
        self.lineno_info = []
        self.code_lines = []
        for line in lines:
            if (
                line.find("|") == -1
                and set(line.strip()) != {"^"}
                and line.strip() != ":"
            ):
                self.end_lineno_marker = 0
                break
        else:
            self.end_lineno_marker = lines[0].find("|") + 1
        for line in lines:
            lineno_marker = line[0 : self.end_lineno_marker]
            if lineno_marker.strip():
                self.lineno_info.append(lineno_marker)
                self.code_lines.append((line[self.end_lineno_marker :]))
            elif set(line.strip()) != {"^"}:
                self.lineno_info.append("")
                self.code_lines.append(line)

    def shift_error_lines(self, error_lines):
        new_error_lines = {}
        line_numbers = sorted(list(error_lines.keys()))
        up_shift = 1
        for lineno in line_numbers:
            new_error_lines[lineno - up_shift] = []
            for (begin, end) in error_lines[lineno][1::2]:
                new_error_lines[lineno - up_shift].append(
                    (
                        max(0, begin - self.end_lineno_marker),
                        end - self.end_lineno_marker,
                    )
                )
            up_shift += 1
        return new_error_lines

    def find_multiline_strings(self):
        self.multiline_strings = []
        source = "\n".join(self.code_lines)
        tokens = token_utils.tokenize(source)
        multiline_string = None
        for index, token in enumerate(tokens):
            if multiline_string:
                if multiline_string.end_line == token.start_row:
                    multiline_string.end_col = token.start_col
                self.multiline_strings.append(multiline_string)
            if token.start_row != token.end_row:
                multiline_string = MultilineString(
                    begin_col=token.start_col,
                    begin_line=token.start_row,
                    end_col=token.end_col,
                    end_line=token.end_row,
                )
                if index != 0:
                    prev_token = tokens[index - 1]
                    if multiline_string.begin_line == prev_token.end_row:
                        multiline_string.begin_col = tokens[index - 1].end_col
            else:
                multiline_string = None

    def format_lineno_info(self, lineno_marker):
        if "-->" in lineno_marker:
            indent, number = lineno_marker.split("-->")
            text = Text(indent + " > ", style=self.operator_style)
            return text.append(Text(number, style=self.number_style))
        return Text(lineno_marker, style=self.comment_style)

    def format_code_line(self, new_line, code_line, error_line=None):
        if not error_line:
            error_line = []
        tokens = token_utils.tokenize(code_line)
        if error_line:
            return self.format_code_line_with_error(new_line, tokens, error_line)
        end_previous = 0
        for token in tokens:
            if not token.string:
                continue
            new_line.append(self.highlight_token(token, end_previous))
            end_previous = token.end_col
        return new_line

    def format_code_line_with_error(self, new_line, tokens, error_line):
        end_previous = 0
        for token in tokens:
            if not token.string.strip():
                # handle spaces explicitly below to get the alignment right
                continue
            for begin, end in error_line:
                if begin <= token.start_col < end:
                    if begin > end_previous:
                        spaces = " " * (begin - end_previous)
                        new_line.append(spaces)
                        end_previous = begin
                    nb_spaces = token.start_col - end_previous
                    text_string = " " * nb_spaces + token.string
                    new_line.append(Text(text_string, style=self.error_style))
                    break
                elif token.start_col <= begin and token.end_col >= end:
                    # Error is inside token.string;
                    # For example, highlighting \' in
                    #  'don\'t'
                    #      ^^
                    style = self.get_style(token)
                    if token.start_col > end_previous:
                        spaces = " " * (token.start_col - end_previous)
                        new_line.append(spaces)
                    tok_string = token.string
                    text_string = tok_string[: begin - token.start_col]
                    new_line.append(Text(text_string, style=style))
                    text_string = tok_string[
                        begin - token.start_col : end - token.start_col
                    ]
                    new_line.append(Text(text_string, style=self.error_style))
                    text_string = tok_string[end - token.start_col :]
                    new_line.append(Text(text_string, style=style))
                    break
            else:
                new_line.append(self.highlight_token(token, end_previous))
            end_previous = token.end_col
        return new_line

    def format_lines(self, lines, error_lines):
        self.split_lineno_from_code(lines)
        error_lines = self.shift_error_lines(error_lines)
        self.find_multiline_strings()
        lineno = -1
        new_lines = []
        for lineno_marker, code_line in zip(self.lineno_info, self.code_lines):
            lineno += 1
            error_line = error_lines[lineno] if lineno in error_lines else None
            new_line = self.format_lineno_info(lineno_marker)

            inside_multiline = False
            for line_ in self.multiline_strings:
                if line_.begin_line < lineno < line_.end_line:
                    inside_multiline = True
                    break
                elif lineno == line_.end_line:
                    new_line.append(
                        Text(code_line[0 : line_.end_col], style=self.string_style)
                    )
                    code_line = code_line[line_.end_col :]
                    if error_line:
                        new_error_line = []
                        for (begin, end) in error_line:
                            new_error_line.append(
                                (
                                    max(0, begin - line_.end_col),
                                    end - line_.end_col,
                                )
                            )
                        error_line = new_error_line

            if inside_multiline:
                new_line.append(Text(code_line, style=self.string_style))
            elif error_line:
                new_line = self.format_code_line(new_line, code_line, error_line)
            else:
                new_line = self.format_code_line(new_line, code_line)
            new_lines.append(new_line)
        return new_lines

    def highlight_token(self, token, end_previous=0):
        """Imitating pygment's styling of individual token."""
        nb_spaces = token.start_col - end_previous
        text_string = " " * nb_spaces + token.string
        style = self.get_style(token)
        return Text(text_string, style=style)

    def get_style(self, token):
        """Imitating pygment's styling of individual token."""
        text_string = token.string
        if token.is_keyword():
            if text_string in ["True", "False", "None"]:
                return self.constant_style
            else:
                return self.keyword_style
        elif is_builtin(text_string):
            return self.builtin_style
        elif is_exception(text_string):
            return self.exception_style
        elif token.is_comment():
            return self.comment_style
        elif token.is_number():
            return self.number_style
        elif token.is_operator():
            return self.operator_style
        elif token.is_string() or token.is_unclosed_string():
            return self.string_style
        else:
            return self.code_style


def format_with_highlight(lines, error_lines, theme):
    """Formats lines, replacing code underlined by ^^ (on the following line)
    into highlighted code, and removing the ^^ from the end result.
    """
    highlighter = ColourHighlighter(theme)
    return highlighter.format_lines(lines, error_lines)


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
        error_lines = get_highlighting_ranges(lines)
        # Sometimes, an entire line is the cause of an error and is not
        # highlighted with carets so that error_lines is an empty dict.
        if not error_lines:
            for line in lines:
                if line.strip().startswith("-->"):
                    error_lines = {0: tuple()}
                    break

        if (
            colours.get_highlight() is not None  # otherwise, use carets
            and self.lexer_name == "python"  # do not process pytb
            and error_lines
        ):
            yield from format_with_highlight(lines, error_lines, theme)
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
