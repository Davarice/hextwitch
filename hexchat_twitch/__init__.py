"""Plugin Root Package

Copyright (C) 2019 @Davarice
Free Software under GPLv3
"""

VERSION = "0.0.4-dev0"

from collections import deque
from typing import List

from hexchat_twitch.config import cfg
from hexchat_twitch.messaging import ServerMessage, HexMessage
from hexchat_twitch import api, util


commands = {}
events_recv = {
    "Channel Message": 2,
    "Channel Action": 2,
    "Channel Msg Hilight": 3,
    "Channel Action Hilight": 3,
}
events_send = {"Your Message": 2, "Your Action": 2}


userstates = {}
inbox = deque([], 5)


cfg.load("config.yml", False)


class HexTwitch:
    def __init__(self, hexchat):
        self.hexchat = hexchat

    def echo(self, text: str, type_: str = "Server Error", ctx=None):
        (ctx or self.hexchat).emit_print(type_, text)

    # ===--
    # CALLBACKS: Called by HexChat when Something™ happens.
    # ===--

    def cb_focus(self, *_):
        """Reset the color of a newly focused tab."""
        try:
            ctx = self.hexchat.get_context()
        except:
            return self.hexchat.EAT_NONE
        util.color_tab(ctx, 0, True)
        return self.hexchat.EAT_NONE

    def cb_message_send(self, words: List[str], words_eol: List[str]):
        """The HexChat command `/say` has just been invoked. This means that the
            user has typed and sent a message. Intercept it, and check whether
            it has been typed into a Twitch Whisper channel. If it has, do not
            send it as a `/say text`; Instead, send it as a `/w username text`.
        """
        ctx = self.hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return self.hexchat.EAT_NONE

    def cb_message_server(self, words: List[str], words_eol: List[str], _, attrs):
        """A message is being received from Twitch. All we know initially is that
            `attrs` is an object with attributes `time` and `ircv3`.
            Deal with it.

        DEVELOPER NOTE: This method is the Callback hooked by way of this:
                `hexchat.hook_server_attrs("RAW LINE", *_)`.
        If HexChat changes what attributes are given, THIS IS THE `attrs` WHERE
            THAT MATTERS.
        """
        ctx = self.hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return self.hexchat.EAT_NONE
        message = ServerMessage(words, attrs.ircv3, ctx)
        if message.mtype == "ROOMSTATE":
            # Nothing notable.
            return self.hexchat.EAT_HEXCHAT
        elif message.mtype == "USERSTATE":
            # Receiving data about user.
            userstates[
                f'{ctx.get_info("network")}/{ctx.get_info("channel")}'
            ] = util.split_badges(message.tags["badges"])
            return self.hexchat.EAT_HEXCHAT
        elif message.mtype == "PRIVMSG":
            # Receiving a message. Save it for now and wait for it to come up.
            inbox.append(message)
            return hexchat.EAT_NONE
        elif message.mtype == "USERNOTICE":
            # Notable event; Subscription or Raid.
            return  # TODO
        elif message.mtype == "WHISPER":
            # Receiving a Twitch Whisper (DM). Put it in its own tab.
            return  # TODO
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

    def cb_message_hex(self, args: List[str], args_eol: List[str], mtype: str):
        """A message is being posted in HexChat. All we know initially is that
            `mtype` is a `str` also found in `events_recv`. Deal with it.
        """
        ctx = self.hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return self.hexchat.EAT_NONE

    def cb_message_user(self, args: List[str], args_eol: List[str], mtype: str):
        """A message is being posted in HexChat. All we know initially is that
            `mtype` is a `str` also found in `events_send`. Deal with it.
        """
        ctx = self.hexchat.get_context()
        if ctx.get_info("network").lower() != "twitch":
            return self.hexchat.EAT_NONE
