import os

def absolutePath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))