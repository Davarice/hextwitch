"""Messaging interface module

Provides methods for sending IRC messages to Twitch through HexChat, and
    displaying IRC messages thus received.
"""

from hexchat_twitch.util import split_tags


class ServerMessage:
    """Class representing a message received from Twitch.

    Takes a Bytes object containing the pure IRCv3 string received. Breaks the
        string apart into a Dict of tags that can be accessed easily.
    """
    def __init__(self, msg: bytes):
        self.raw = msg
        self.data = split_tags(msg)


class HexMessage:
    def __init__(self, msg):
        pass
