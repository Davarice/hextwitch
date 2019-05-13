"""Messaging interface module

Provides methods for sending IRC messages to Twitch through HexChat, and
    displaying IRC messages thus received.
"""

from typing import List

import hexchat

from hexchat_twitch.config import cfg
from hexchat_twitch.util import ctxid, render_badges, split_tags


userstates = {}


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

        self.prefix, self.mtype, self.args, self.message, self.tags = split_tags(raw)

        self.author = self.prefix.split("!", 1)[0]
        self.ident = "/".join([str(ts), self.author, self.message])


def message_emit(
    ctx: hexchat.Context, mtype: str, author: str, content: str, badges: str
):
    ctx.emit_print(mtype, author, content, badges)


def message_from_other(
    ctx: hexchat.Context, mtype: str, author: str, content: str, source: ServerMessage
):
    badges = render_badges(source.tags.get("badges", {}))
    message_emit(ctx, mtype, author, content, badges)


def message_from_self(ctx: hexchat.Context, mtype: str, content: str):
    author = ctx.get_info("nick")
    badges = userstates.get(ctxid(ctx), "")
    message_emit(ctx, mtype, author, content, badges)
