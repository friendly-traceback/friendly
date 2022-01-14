from idlelib import rpc
from friendly.idle import *  # noqa
from friendly_traceback import exclude_file_from_traceback

exclude_file_from_traceback(__file__)
from friendly_traceback.path_info import EXCLUDED_FILE_PATH

install()  # noqa

n = -1
entries = {}


def getcode():
    global n

    rpchandler = rpc.objecttable["exec"].rpchandler
    while True:
        n += 1
        filename = f"<pyshell#{n}>"
        lines = rpchandler.remotecall("linecache", "getlines", (filename, None), {})
        if not lines:
            n -= 1
            break
        entries[filename] = "\n".join(lines)

    for i in range(n, -1, -1):
        filename = f"<pyshell#{i}>"
        if filename not in entries:
            continue
        if entries[filename].strip() == "getcode()":
            EXCLUDED_FILE_PATH.add(filename)
            print("excluding", filename)
            continue
        compile(entries[filename], filename, "exec")
