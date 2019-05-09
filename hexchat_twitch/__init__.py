"""Plugin Root Package

Copyright (C) 2019 @Davarice
Free Software under GPLv3
"""

VERSION = "0.0.4-dev0"

from collections import deque
from typing import List

import hexchat

from hexchat_twitch import api, util
from hexchat_twitch.config import cfg
from hexchat_twitch.channeling import dm_receive, dm_send
from hexchat_twitch.messaging import HexMessage, ServerMessage, userstates
from hexchat_twitch.util import ctxid


commands = {}
events_recv = {
    "Channel Message": 2,
    "Channel Action": 2,
    "Channel Msg Hilight": 3,
    "Channel Action Hilight": 3,
}
events_send = {"Your Message": 2, "Your Action": 2}


inbox = deque([], 5)


cfg.load("config.yml", False)


class HexTwitch:
    def echo(self, text: str, type_: str = "Server Error", ctx=None):
        (ctx or hexchat).emit_print(type_, text)

    # ===--
    # CALLBACKS: Called by HexChat when Something™ happens.
    # ===--

    def cb_focus(self, *_):
        """Reset the color of a newly focused tab."""
        try:
            ctx = hexchat.get_context()
        except:
            return hexchat.EAT_NONE
        util.color_tab(ctx, 0, True)
        return hexchat.EAT_NONE

    def cb_message_send(self, words: List[str], _: List[str]):
        """The HexChat command `/say` has just been invoked. This means that the
            user has typed and sent a message. Intercept it, and check whether
            it has been typed into a Twitch Whisper channel. If it has, do not
            send it as a `/say text`; Instead, send it as a `/w username text`.
        """
        ctx = hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return hexchat.EAT_NONE

    def cb_message_server(self, words: List[str], _: List[str], __, attrs):
        """A message is being received from Twitch. All we know initially is that
            `attrs` is an object with attributes `time` and `ircv3`.
            Deal with it.

        DEVELOPER NOTE: This method is the Callback hooked by way of this:
                `hexchat.hook_server_attrs("RAW LINE", *_)`.
        If HexChat changes what attributes are given, THIS IS THE `attrs` WHERE
            THAT MATTERS.
        """
        ctx = hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return hexchat.EAT_NONE
        message = ServerMessage(words, attrs.ircv3, attrs.time, ctx)
        if message.mtype == "ROOMSTATE":
            # Nothing notable.
            return hexchat.EAT_HEXCHAT
        elif message.mtype == "USERSTATE":
            # Receiving data about ourself.
            userstates[ctxid(ctx)] = util.split_badges(message.tags["badges"])
            return hexchat.EAT_HEXCHAT
        elif message.mtype == "PRIVMSG":
            # Receiving a message. Save it for now and wait for it to come up.
            inbox.append(message)
            return hexchat.EAT_NONE
        elif message.mtype == "USERNOTICE":
            # Notable event; Subscription or Raid.
            return  # TODO
        elif message.mtype == "WHISPER":
            # Receiving a Twitch Whisper (DM). Put it in its own tab.
            dm_receive(message)
            return hexchat.EAT_ALL
        elif message.mtype == "HOSTTARGET":
            # This channel has started hosting. Print a direct link.
            return  # TODO
        elif message.mtype == "CLEARCHAT":
            # A user has been purged. Either a timeout or a ban.
            return  # TODO
        elif message.mtype == "CLEARMSG":
            # A message has been selectively deleted. Repost it.
            return  # TODO
        else:
            # Unknown event type. Make a note of it.
            self.echo(
                "Unknown event of type '{}' in {}: {}".format(
                    message.mtype, ctx.get_info("channel"), message.msg
                )
            )
            return hexchat.EAT_NONE

    def cb_message_hex(self, args: List[str], _: List[str], mtype: str, attr):
        """A message is being posted in HexChat. All we know initially is that
            `mtype` is a `str` also found in `events_recv`. Deal with it.

        "Channel Message"
        "Channel Action"
        "Channel Msg Hilight"
        "Channel Action Hilight"
        """
        ctx = hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return hexchat.EAT_NONE
        name, text, pre = args
        ts = attr.time
        ident = "/".join([str(ts), name, text])

        source_message = None
        # Try to find the identifier in the inbox.
        for m in inbox:
            if m.ident == ident:
                # Found one. Remove it from the inbox, and process it.
                source_message = m
                inbox.remove(m)
                break

        if source_message:
            # This message has a ServerMessage twin. Apply tags.
            message = HexMessage(mtype, name, text, pre, source_message)
            message.emit()
            return hexchat.EAT_ALL

    def cb_message_user(self, args: List[str], _: List[str], mtype: str):
        """A message is being posted in HexChat. All we know initially is that
            `mtype` is a `str` also found in `events_send`. Deal with it.

        "Your Message"
        "Your Action"
        """
        ctx = hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return hexchat.EAT_NONE

        channel = ctx.get_info("channel")
        if not channel.startswith("#") or args[1].lower().startswith(".w "):
            # Channel does NOT start with #, OR the message DOES start with .w
            # This message is intended to be a Whisper/DM
            return hexchat.EAT_ALL
