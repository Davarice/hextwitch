"""Util module"""

from collections import defaultdict
from typing import List, Tuple

import hexchat


tab_colors = {}


# Test whether the passed context is focused.
focused = lambda ctx: ctx.get_info("channel") == hexchat.find_context().get_info(
    "channel"
)


def color_tab(ctx, n=0, reset=False):
    """Color a tab (0-3), but only if the current color is lower."""
    if focused(ctx) and not reset:
        # Do not color the current tab, unless resetting.
        return
    if not 0 <= n <= 3:
        return

    tab_name = ctx.get_info("network").lower() + "/" + ctx.get_info("channel")
    current = tab_colors.get(tab_name, 0)
    if reset or n >= current:
        # If the new color is "more important", or the function is called with
        #   the reset flag, change it
        tab_colors[tab_name] = n
        ctx.command("gui color {}".format(str(n)))


def highest_below(seq: List[int], limit: int):
    """Find the highest number in a sequence that is not higher than the limit."""
    seq2 = [item for item in seq if item <= limit]

    if seq2:
        return max(seq2)
    else:
        return limit


def plural(num: int, root="", end_plural="s", end_single=""):
    """Given grammar and a number, return the appropriate singular or plural form."""
    return root + (end_single if num == 1 else end_plural)


def split_tags(ircv3: bytes) -> Tuple[str, defaultdict]:
    """Split a raw IRCv3 bytestring into a default dict and return it."""
    string_full = ircv3.decode("utf-8")
    tags_dict = defaultdict(str)
    if string_full[0] == "@":
        # Starting with @ indicates that the first half is Tags. The two
        #   segments are separated by a space.
        tags, text = string_full.split(" ", 1)

        for pair in tags[1:].split(";"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                tags_dict[k] = v
    else:
        # Otherwise, the whole thing is pure message.
        text = string_full
    return text, tags_dict
