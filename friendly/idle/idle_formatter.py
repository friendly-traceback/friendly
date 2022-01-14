"""Custom formatter for IDLE.

The logic is quite convoluted, unless one is very familiar with
how the basic formatting is done.

All that matters is that, it is debugged and works appropriately! ;-)
"""
# TODO: add unit tests

import sys
from friendly_traceback.base_formatters import select_items, no_result, repl_indentation

if sys.version_info >= (3, 9, 5):
    repl_indentation["suggest"] = "single"  # more appropriate value


def format_source(text):
    """Formats the source code shown by where().

    Often, the location of an error is indicated by one or more ^ below
    the line with the error. IDLE uses highlighting with red background the
    normal single character location of an error.
    This function replaces the ^ used to highlight an error by the same
    highlighting scheme used by IDLE.
    """
    lines = text.split("\n")
    while not lines[-1].strip():
        lines.pop()
    caret_set = set(" ^->")
    error_lines = {}
    for index, line in enumerate(lines):
        if set(line).issubset(caret_set):
            error_lines[index] = line

    new_lines = []
    for index, line in enumerate(lines):
        if index in error_lines:
            continue
        colon_location = line.find(":") + 1

        new_lines.append((line[0:colon_location], "stdout"))
        if index + 1 in error_lines:
            line_with_carets = error_lines[index + 1]
            for char_index, char in enumerate(line):
                if char_index < colon_location:
                    continue
                if (
                    char_index < len(line_with_carets)
                    and line_with_carets[char_index] == "^"
                ):
                    new_lines.append((line[char_index], "ERROR"))
                else:
                    new_lines.append(((line[char_index], "default")))
        else:
            new_lines.append((line[colon_location:], "default"))
        new_lines.append(("\n", "default"))
    return new_lines


def format_text(info, item, indentation):
    """Format text with embedded code fragment surrounded by back-quote characters."""
    new_lines = []
    text = info[item].rstrip()
    for line in text.split("\n"):
        if not line.strip():
            continue
        if "`" in line and line.count("`") % 2 == 0:
            fragments = line.split("`")
            for index, fragment in enumerate(fragments):
                if index == 0:
                    new_lines.append((indentation + fragment, "stdout"))
                elif index % 2:
                    if "Error" in fragment:
                        new_lines.append((fragment, "stderr"))
                    else:
                        new_lines.append((fragment, "default"))
                else:
                    new_lines.append((fragment, "stdout"))
            new_lines.append(("\n", "stdout"))
        else:
            colour = "default" if line.startswith("    ") else "stdout"
            new_lines.append((indentation + line + "\n", colour))

    return new_lines


def format_traceback(text):
    """We format tracebacks using the default stderr color (usually red)
    except that lines with code are shown in the default color (usually black).
    """
    lines = text.split("\n")
    if lines[-2].startswith("SyntaxError:"):
        if lines[2].strip().startswith("File"):
            lines = lines[3:]  # Remove everything before syntax error
        else:
            lines = lines[1:]  # Remove file name
    new_lines = []
    for line in lines:
        if line.startswith("    "):
            new_lines.append((line, "default"))
        elif line:
            new_lines.append((line, "stderr"))
        new_lines.append(("\n", "default"))
    return new_lines


def idle_formatter(info, include="friendly_tb"):
    """Formatter that takes care of color definitions."""
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = ["\n"]
    for item in items_to_show:
        if item == "header":
            continue

        if item in info:
            if "traceback" in item:  # no additional indentation
                result.extend(format_traceback(info[item]))
            elif "source" in item:  # no additional indentation
                result.extend(format_source(info[item]))
            elif "header" in item:
                indentation = spacing[repl_indentation[item]]
                result.append((indentation + info[item], "stderr"))
            elif item == "message":  # Highlight error name
                parts = info[item].split(":")
                parts[0] = "`" + parts[0] + "`"
                _info = {item: ":".join(parts)}
                indentation = spacing[repl_indentation[item]]
                result.extend(format_text(_info, item, indentation))
            else:
                indentation = spacing[repl_indentation[item]]
                result.extend(format_text(info, item, indentation))
            if "traceback" not in item:
                result.extend("\n")

    if result == ["\n"]:
        return no_result(info, include)

    if result[-1] == "\n" and include != "friendly_tb":
        result.pop()

    return result
