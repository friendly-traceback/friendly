def get_highlighting_ranges(lines):
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
        if set(line.strip().replace(" ", "")).issubset(caret_set) and "^" in line:
            # Ensure the line contains only ^ and spaces
            line = line.replace("-", " ").replace(">", " ").rstrip("\n")
            # Then, add the amount of spaces corresponding to the number of
            # characters in the line to be highlighted
            line = line + " " * (len(lines[index - 1].rstrip("\n")) - len(line))
            error_lines[index] = get_single_line_highlighting_ranges(line)
            # includes the remaining range for the line to be highlighted
    return error_lines


def get_single_line_highlighting_ranges(line):
    """Given a single line containing alternating sequences of consecutive
    spaces and carets (^), this function will compute the position of the
    beginning and end of each sequence of consecutive characters,
    recording them as tuples

    It returns a list corresponding containing these tuples alternating between
    regions where carets are not found and where carets are found.
    """
    caret_line = []
    scanning_carets = False
    char_index = begin = 0  # in case line is empty
    for char_index, char in enumerate(line):
        if not scanning_carets and char == "^":
            caret_line.append((begin, char_index))
            begin = char_index
            scanning_carets = True
        if scanning_carets and char == " ":
            caret_line.append((begin, char_index))
            begin = char_index
            scanning_carets = False
    # include the last subrange
    if begin != char_index:
        caret_line.append((begin, char_index + 1))
    return caret_line
