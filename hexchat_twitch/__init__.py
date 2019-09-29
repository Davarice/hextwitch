"""Plugin Root Package

Copyright (C) 2019 @Davarice
Free Software under GPLv3
"""

VERSION = "0.0.7-dev0"

from collections import deque
from typing import List

import hexchat

from hexchat_twitch.config import cfg
from hexchat_twitch.channeling import dm_post, dm_receive, dm_send
from hexchat_twitch.messaging import ServerMessage, message_from_other, userstates
from hexchat_twitch.util import ctxid, color_tab, render_badges


commands = {}
events_recv = {
    "Channel Message": 2,
    "Channel Action": 2,
    "Channel Msg Hilight": 3,
    "Channel Action Hilight": 3,
}
events_send = {"Your Message": 2, "Your Action": 2}
ignore_and_allow = ["CAP", "JOIN", "MODE", "NOTICE", "PART", "PING", "PONG"]
ignore_and_eat = ["ROOMSTATE"]


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
        color_tab(ctx, 0, True)
        return hexchat.EAT_NONE

    def cb_message_send(self, words: List[str], _: List[str], __=None):
        """The HexChat command `/say` has just been invoked. This means that the
            user has typed and sent a message. Intercept it, and check whether
            it has been typed into a Twitch Whisper channel. If it has, do not
            send it as a `/say text`; Instead, send it as a `/w username text`.
        """
        self.echo(str(words))
        ctx = hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return hexchat.EAT_NONE
        # TODO

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
        if message.mtype.isdigit() or message.mtype in ignore_and_allow:
            # Nothing notable. Let it pass.
            color_tab(ctx, 1)
            return hexchat.EAT_NONE
        elif message.mtype in ignore_and_eat:
            # Nothing notable. Kill it.
            return hexchat.EAT_HEXCHAT
        elif message.mtype == "USERSTATE":
            # Receiving data about ourself.
            userstates[ctxid(ctx)] = render_badges(message.tags["badges"])
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
                f"Unknown event of type {message.mtype!r}"
                f" in {ctx.get_info('channel')}: {message.message}"
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
        ts = attr.time
        args = [hexchat.strip(arg) for arg in args]
        ident = "/".join([str(ts), args[0], args[1]])

        # Try to find the identifier in the inbox.
        # self.echo(str(inbox))
        for m in inbox:
            if m.ident == ident:
                # Found one. Remove it from the inbox, and process it.
                # self.echo("`{}` == `{}`".format(repr(m.ident), repr(ident)))
                inbox.remove(m)
                message_from_other(ctx, mtype, args[0], args[1], m)
                return hexchat.EAT_ALL
            # else:
            #     self.echo("`{}` != `{}`".format(repr(m.ident), repr(ident)))

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
        if args[1].lower().startswith(".w "):
            comps = args[1].split(maxsplit=2)
            comps.pop(0)
            if comps:
                dest = comps.pop(0)
                if comps:
                    dm_post(args[0], dest, comps[0], mtype)
            return hexchat.EAT_NONE
        elif not channel.startswith("#"):
            # Channel does NOT start with #
            # This message is intended to be a Whisper/DM
            # TODO
            dm_send(args[0], channel, args[1], mtype)
            return hexchat.EAT_HEXCHAT
