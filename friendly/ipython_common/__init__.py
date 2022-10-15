from friendly_traceback import add_ignored_warnings


def _do_not_show_warning(warning_instance, warning_type, filename, lineno) -> bool:
    return filename == "<>"


add_ignored_warnings(_do_not_show_warning)
del add_ignored_warnings
