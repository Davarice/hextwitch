"""Messaging interface module

Provides methods for sending IRC messages to Twitch through HexChat, and
    displaying IRC messages thus received.
"""

from typing import List

from hexchat_twitch.util import split_tags


class HexMessage:
    """Class representing a message printed in HexChat.

    Takes a number of strings and allows modifying the message before sending.
    """

    def __init__(self, mtype: str, name: str, msg: str, badge: str = "", servmsg=None):
        self.mtype = mtype
        self.author = name
        self.msg = msg
        self.badge = badge
        self.servmsg = servmsg

    def emit(self):
        self.servmsg.context.emit_print(self.mtype, self.author, self.msg, self.badge)


class ServerMessage:
    """Class representing a message received from Twitch.

    Takes a Bytes object containing the pure IRCv3 string received. Breaks the
        string apart into a Dict of tags that can be accessed easily.
    """

    def __init__(self, words: List[str], raw: bytes, ts: int, ctx=None):
        self.words = words
        self.raw = raw
        self.ts = ts
        self.context = ctx
        self.msg, self.tags = split_tags(raw)

        comp = self.msg.split(" ", 3)
        if len(comp) == 4:
            self.hostname, self.mtype, self.channel, self.message = comp
        else:
            self.hostname, self.mtype, self.channel = comp
            self.message = ""

        self.author = self.hostname.split("!", 1)[0][1:]
        self.ident = "/".join([str(ts), self.author, self.message])
