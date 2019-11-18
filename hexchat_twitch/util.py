"""Util module"""

from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import hexchat

from .config import cfg
import ircrust


ctxid = lambda ctx: f"{ctx.get_info('network')}/{ctx.get_info('channel')}"
# Test whether the passed context is focused.
is_focused = lambda ctxn: ctxn == ctxid(hexchat.find_context())
tab_colors: Dict[str, int] = defaultdict(int)


def color_tab(ctx, n: int = 0, force: bool = False) -> None:
    """Color a tab (0-3), but only if the current color is lower."""
    tab_name = ctxid(ctx)

    if 0 <= n <= 3 and (
        force or (n > tab_colors[tab_name] and not is_focused(tab_name))
    ):
        # If the new color is "more important", or the function is called with
        #   Force, change it.
        tab_colors[tab_name] = n
        ctx.command(f"gui color {n}")


def echo(
    text: str, type_: str = "Server Error", ctx: hexchat.Context = None, hl: int = 0
):
    (ctx or hexchat).emit_print(type_, text)
    if ctx and hl:
        color_tab(ctx, hl)


def highest_below(seq: Sequence[int], limit: int) -> int:
    """Find the highest number in a sequence that is not higher than the limit."""
    try:
        return max(item for item in seq if item <= limit)
    except ValueError:
        return limit


def plural(
    num: int, root: str = "", end_plural: str = "s", end_single: str = ""
) -> str:
    """Given grammar and a number, return the appropriate singular or plural form."""
    return f"{root}{end_single if num == 1 else end_plural}"


def render_badges(bstring: str) -> str:
    if not bstring:
        return ""
    prefix = ""

    for badge in bstring.split(","):
        btype, rank = badge.split("/")
        # "Rank" here is the "level" of the badge, for example "12" for the
        #   1-year subscription badge. The entry in badge_chars can be a dict,
        #   and if it is, the keys should be integers. The highest key which is
        #   <= the rank is the key whose value is displayed.
        try:
            rank = int(rank)
            icon = cfg["badges/chars"][btype]
            prefix += icon[highest_below(icon, rank)]
        except:
            pass

    return (
        prefix[: cfg.get("badges/maxlen", 3)] + cfg.get("badges/separate", " ")
        if prefix
        else ""
    )


def split_tags(ircv3: bytes) -> Tuple[str, str, List[str], str, defaultdict]:
    """Split a raw IRCv3 bytestring into a default dict and return it."""
    prefix, command, args, trail, tags = ircrust.decode(ircv3)
    tags_dict = defaultdict(str, tags)
    return prefix, command, args, trail, tags_dict
