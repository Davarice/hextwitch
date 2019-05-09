"""Module for controlling channels and tabs."""

import hexchat

from hexchat_twitch.api import get_rooms
from hexchat_twitch.config import cfg
from hexchat_twitch.util import color_tab


channels = {}
to_private = {
    "Channel Message": "Private Message to Dialog",
    "Channel Msg Hilight": "Private Message to Dialog",
    "Your Message": "Private Message to Dialog",
    "Channel Action": "Private Action to Dialog",
    "Channel Action Hilight": "Private Action to Dialog",
    "Your Action": "Private Action to Dialog",
}


def channel_add(name, alias):
    server = hexchat.find_context("Twitch")
    if server:
        server.command("query " + name)
        ctx = hexchat.find_context("Twitch", name)
        if ctx and alias:
            ctx.command("settab " + alias)
        return ctx
    return None


def channel_get(name):
    name = name.lower()
    ctx = hexchat.find_context("Twitch", name)
    # Find the channel with the given name on the Twitch server.
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
            ctx.command("join " + room_true)
            # Find the newly opened tab.
            room_ = channel_get(room_true)
            if room_:
                # Then, give it an alias of the form `#channel.room`.
                room_.command("settab " + cfg.get("tabs/room", "#{_id}").format(**room))


def dm_post(author, channel, text, mtype):
    ctx = channel_get(channel)


def dm_receive(message):
    pass


def dm_send(message, channel):
    pass
