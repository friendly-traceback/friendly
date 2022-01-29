def get_highlighting_range(lines):
    """Given a block of code highlighted primarily with carets (^),
    this function will identify the lines containing carets and break up
    that line into sub-ranges, showing at which indices the carets
    begin and end.

    It returns a dict whose index is the line number where the carets
    were found, and the content is a list of sub-ranges.
    """
    caret_set = set("^->")  # Some lines include --> to indicate that the
    # error continues on the next line
    error_lines = {}
    for index, line in enumerate(lines):
        if set(line.replace(" ", "")).issubset(caret_set) and "^" in line:
            error_lines[index] = []
            highlighting = False
            char_index = begin = 0
            # Ensure the line contains only ^ and end on a ^
            line = line.replace("-", " ").replace(">", " ").rstrip()
            for char_index, char in enumerate(line):
                if not highlighting and char == "^":
                    error_lines[index].append((begin, char_index))
                    begin = char_index
                    highlighting = True
                if highlighting and char != "^":
                    error_lines[index].append((begin, char_index))
                    begin = char_index
                    highlighting = False
            # include the last caret range correctly
            error_lines[index].append((begin, char_index + 1))
            # includes the remaining range for the line to be highlighted
            error_lines[index].append((char_index + 1, len(lines[index - 1])))
    return error_lines
