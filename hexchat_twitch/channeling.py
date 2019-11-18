"""Module for controlling channels and tabs."""

from typing import Optional

import hexchat

from .api import get_rooms
from .config import cfg
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


def channel_add(name, alias) -> Optional["hexchat.Context"]:
    server = hexchat.find_context("Twitch")
    if server:
        server.command("query " + name)
        ctx = hexchat.find_context("Twitch", name)
        if ctx and alias:
            ctx.command("settab " + alias)
        return ctx
    return None


def channel_get(name) -> "hexchat.Context":
    """Find the channel with the given name on the Twitch server."""
    name = name.lower()
    ctx = hexchat.find_context("Twitch", name)
    return ctx


def channel_join(name):
    ctx = hexchat.get_context()
    if ctx.get_info("network").lower() != "twitch" or ":" in name:
        return hexchat.EAT_NONE
    rooms = get_rooms(name[1:])
    if rooms:
        for room in rooms.get("rooms", []):
            # Assemble the true channel name of each Room.
            room_true = ":".join(
                ["#chatrooms", str(room.get("owner_id", 0)), str(room.get("_id", 0))]
            )
            # Execute the JOIN command to connect to the Room.
            ctx.command(f"join {room_true}")
            # Find the newly opened tab.
            room_ = channel_get(room_true)
            if room_:
                # Then, give it an alias of the form `#channel.room`.
                room_.command("settab " + cfg.get("tabs/room", "#{_id}").format(**room))


def dm_post(author, channel, text, mtype):
    ctx = channel_get(channel)
    if not ctx:
        channel_add(channel, "=={}==".format(channel))
        ctx = channel_get(channel)
        if not ctx:
            print(f"Cannot make DM tab '{channel}'")
            return
    ntype = to_private.get(mtype, "Private Message to Dialog")
    ctx.emit_print(ntype, author, text)


def dm_receive(message: ServerMessage):
    dm_post(message.author, message.author, message.message, message.mtype)


def dm_send(author, channel, text, mtype):
    dm_post(author, channel, text, mtype)
    twitch = hexchat.find_context("Twitch")
    if twitch:
        twitch.command(f"say .w {channel} {text}")
    else:
        print(f"Cannot send DM to {channel}.")
