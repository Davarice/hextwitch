"""Plugin Root Package

Copyright (C) 2019 @Davarice
Free Software under GPLv3
"""
from string import Template


VERSION = "0.0.9-dev0"

from collections import deque
from typing import List

import hexchat

from .config import cfg
from .channeling import dm_post, dm_receive, dm_send
from .messaging import message_from_other, ServerMessage, userstates
from .util import ctxid, color_tab, echo, render_badges


commands = {}
ignore_and_allow = ["CAP", "JOIN", "MODE", "NOTICE", "PART", "PING", "PONG"]
ignore_and_eat = ["ROOMSTATE"]


inbox = deque([], 5)


cfg.load("config.yml", False)


# ===--
# CALLBACKS: Called by HexChat when Something™ happens.
# ===--


def cb_focus(_, __, ___):
    """Reset the color of a newly focused tab."""
    try:
        ctx = hexchat.get_context()
    except:
        return hexchat.EAT_NONE
    color_tab(ctx, 0, True)
    return hexchat.EAT_NONE


def cb_message_server(words: List[str], _: List[str], __, attrs):
    """A message is being received from Twitch. All we know initially is that
        `attrs` is an object with attributes `time` and `ircv3`.
        Deal with it.

    NOTE: This method is the Callback hooked by way of this:
            `hexchat.hook_server_attrs("RAW LINE", *_)`.
        If HexChat changes what attributes are given, THIS IS THE `attrs`
        WHERE THAT MATTERS.
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
        inbox.appendleft(message)
        return hexchat.EAT_NONE

    elif message.mtype == "USERNOTICE":
        # Notable event; Subscription or Raid.
        stype = message.tags.get("msg-id")
        if not stype:
            return

        elif stype == "raid":
            echo(
                "{msg-param-displayName} sends {msg-param-viewerCount}"
                " raiders to this channel".format(**message.tags),
                "Motd",
                ctx=ctx,
            )
            return hexchat.EAT_HEXCHAT

        elif stype == "ritual" or stype == "charity" or stype == "rewardgift":
            if "system-msg" in message.tags:
                echo(message.tags["system-msg"].replace("\s", " "), "Motd", ctx=ctx)
            else:
                echo(str(message.tags), ctx=ctx)

            return hexchat.EAT_ALL

        else:
            # Probably a Subscription.
            alert = cfg["sublines"].get(stype)

            if alert is None:
                echo(
                    "Unknown S-Type {!r}: {}".format(
                        stype,
                        message.tags.get("system-msg", "").replace("\s", " ")
                        or message.tags,
                    ),
                    ctx=ctx,
                )
            else:
                for types, keys, modifier in cfg["submods"]:
                    if stype in types and all(key in message.tags for key in keys):
                        alert += modifier

                echo(
                    Template(alert).safe_substitute(
                        MSG=message.message, **message.tags
                    ),
                    "Motd",
                    ctx=ctx,
                )

            return hexchat.EAT_ALL

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
        echo(
            f"Unknown M-Type {message.mtype!r}: "
            + (
                message.message
                or message.tags.get("system-msg", "").replace("\s", " ")
                or message.tags
            ),
            ctx=ctx,
        )
        color_tab(ctx, 1)
        return hexchat.EAT_NONE


def cb_message_hex(args: List[str], _: List[str], mtype: str, attr):
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
    ident = f"{ts}/{args[0]}"

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


def cb_message_user(args: List[str], _: List[str], mtype: str):
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
