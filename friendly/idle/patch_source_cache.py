import linecache
from idlelib import rpc

from friendly_traceback import source_cache


def _get_lines(filename, linenumber=None):
    rpchandler = rpc.objecttable["exec"].rpchandler
    lines = rpchandler.remotecall("linecache", "getlines", (filename, None), {})
    new_lines = []
    for line in lines:
        if not line.endswith("\n"):
            line += "\n"
        if filename.startswith("<pyshell#") and line.startswith("\t"):
            # Remove extra indentation added in the shell (\t == 8 spaces)
            line = "    " + line[1:]
        new_lines.append(line)
    if linenumber is None:
        return new_lines
    return new_lines[linenumber - 1 : linenumber]


old_get_lines = source_cache.cache.get_source_lines


def new_get_lines(filename, module_globals=None):
    """Intended to replace the undocumented linecache.getlines, with the
       same signature.
    """
    lines = _get_lines(filename)
    if not lines:
        lines = old_get_lines(filename=filename, module_globals=module_globals)
    return lines


source_cache.cache.get_source_lines = new_get_lines
linecache.getlines = new_get_lines
