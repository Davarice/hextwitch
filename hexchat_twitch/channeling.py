"""Module for controlling channels and tabs."""

from typing import Optional

import hexchat

from .messaging import ServerMessage
from .util import color_tab


channels = {}
to_private = {
    "Channel Message": "Private Message to Dialog",
    "Channel Msg Hilight": "Private Message to Dialog",
    "Your Message": "Private Message to Dialog",
    "Channel Action": "Private Action to Dialog",
    "Channel Action Hilight": "Private Action to Dialog",
    "Your Action": "Private Action to Dialog",
}


def channel_add(name: str, alias: str = None) -> Optional["hexchat.Context"]:
    server = hexchat.find_context("Twitch")
    if server:
        server.command(f"query {name}")
        ctx = hexchat.find_context("Twitch", name)

        if ctx and alias:
            ctx.command(f"settab {alias}")

        return ctx


def channel_get(name: str) -> "hexchat.Context":
    """Find the channel with the given name on the Twitch server."""
    return hexchat.find_context("Twitch", name)


def dm_post(author, channel, text, mtype):
    ctx = channel_get(channel)
    if not ctx:
        ctx = channel_add(channel, f"=={channel}==")
        if not ctx:
            print(f"Cannot make DM tab {channel!r}")
            return

    ntype = to_private.get(mtype, "Private Message to Dialog")
    ctx.emit_print(ntype, author, text)
    color_tab(ctx, 2)


def dm_receive(message: ServerMessage):
    dm_post(message.author, message.author, message.message, message.mtype)


def dm_send(author, channel, text, mtype):
    dm_post(author, channel, text, mtype)
    twitch = hexchat.find_context("Twitch")
    if twitch:
        twitch.command(f"say .w {channel} {text}")
    else:
        print(f"Cannot send DM to {channel}.")
