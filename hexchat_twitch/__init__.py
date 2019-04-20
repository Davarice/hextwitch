"""Plugin Root Package"""

VERSION = "0.0.1"

from .config import cfg


commands = {}


class HexTwitch:
    def __init__(self, hexchat):
        self.hexchat = hexchat

    def echo(self, text: str, type_: str = "Server Error", ctx=None):
        (ctx or self.hexchat).emit_print(type_, text)

    def cb_message_hex(self, word, word_eol, mtype):
        pass

    def cb_message_server(self, word, word_eol, userdata, attrs):
        pass

    def cb_message_user(self, word, word_eol, userdata):
        pass
