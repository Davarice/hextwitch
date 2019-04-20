"""Util module"""

from typing import List


def plural(num, root="", end_plural="s", end_single=""):
    """Given grammar and a number, return the appropriate singular or plural form."""
    return root + {True: end_plural, False: end_single}[num != 1]


def split_tags(tagline: bytes) -> dict:
    """Split a raw IRCv3 bytestring into a dict and return it."""
    # TODO: REWRITE
    tagline = tagline.decode("utf-8").lstrip("@")
    tags = {}
    m = ""

    tagtable = tagline.split(";")

    for pair in tagtable:
        try:
            [k, v] = pair.split("=", 1)
            if " :" in v:
                vm = v.split(" :", 1)
                v = vm[0]
                m = vm[1]
            tags.update({k: v})
        except:
            pass
    tags.update({"_msg": m})
    return tags


def highest_below(seq: List[int], limit: int):
    """Find the highest number in a sequence that is not higher than the limit."""
    seq2 = [item for item in seq if item <= limit]

    if seq2:
        return max(seq2)
    else:
        return limit
