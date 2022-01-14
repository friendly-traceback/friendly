from idlelib import rpc
from friendly.idle import *  # noqa
from friendly_traceback import exclude_file_from_traceback

exclude_file_from_traceback(__file__)
from friendly_traceback.path_info import EXCLUDED_FILE_PATH

N = -1
entries = {}


def get_syntax_error():
    global N

    rpc_handler = rpc.objecttable["exec"].rpchandler
    while True:
        N += 1
        filename = f"<pyshell#{N}>"
        lines = rpc_handler.remotecall("linecache", "getlines", (filename, None), {})
        if not lines:
            N -= 1
            break
        entries[filename] = "\n".join(lines)

    for i in range(N, -1, -1):
        filename = f"<pyshell#{i}>"
        if filename not in entries:
            continue
        if entries[filename].replace(" ", "") == "get_syntax_error()":
            EXCLUDED_FILE_PATH.add(filename)
            continue
        compile(entries[filename], filename, "exec")
