"""Plugin Root Package"""

VERSION = "0.0.1"

from .config import cfg


class HexTwitch:
    def __init__(self, hexchat):
        self.hexchat = hexchat

    def echo(self, text: str, type_: str = "Server Error", ctx=None):
        (ctx or self.hexchat).emit_print(type_, text)
