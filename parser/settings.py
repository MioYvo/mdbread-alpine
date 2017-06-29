# coding=utf-8
# __author__ = 'Mio'
from os import path

from redis import Redis

# --------------------     redis    --------------------
r = Redis(host="redis")

# --------------------    tornado   --------------------
settings = {
    "debug": True,
    "autoreload": True,
    "tmp_path": path.abspath(path.join(path.dirname("__file__"), "tmp"))
}
