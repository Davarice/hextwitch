"""Module for controlling channels and tabs."""

import hexchat

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
    pass


def dm_post(author, channel, text, mtype):
    ctx = channel_get(channel)


def dm_receive(message):
    pass


def dm_send(message, channel):
    pass
