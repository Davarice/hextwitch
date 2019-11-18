"""
Module dedicated to interfacing with the Twitch API
"""

from typing import List

import hexchat
import requests

from .config import cfg


baseurl = "https://api.twitch.tv/helix/"
games_cache = {}
temps = []


def request(url, auth: bool = False, v5: bool = False) -> requests.Response:
    """
    Send a query to a specified URL. This function mainly exists to apply the
        philosophy of DRY to the Request Header, which is always the same.
    """
    headers = {"Client-ID": cfg.get("auth/client_id") or ""}
    if auth:
        headers["Authorization"] = f"OAuth {(cfg.get('auth/twitch_oauth') or '')}"
    if v5:
        headers["Accept"] = "application/vnd.twitchtv.v5+json"
    return requests.get(url, headers=headers)


def make_url(qtype: str, prefix: str, logins: List[str]) -> str:
    """
    Construct a Query URL based on a Query Type, a Prefix for each Query, and a
        List of Keys to query.
    :param qtype: Type of Query. "streams", "users", etc.
    :param prefix: String to be prepended to each Query String in the List.
    :param logins: A List of Queries to be made. Typically usernames.
    :return: A constructed Query URL that will return channel information.
    """
    print("info", f"Querying '{qtype}'...")
    names = "&".join(f"{prefix}{login}" for login in logins)
    return f"{baseurl}{qtype}?{names}"


def id_from_name(name) -> int:
    # req = request(make_url("users", "login=", [name]))
    # if req.status_code == requests.codes.ok:
    #     return req.json()["data"][0]["id"]
    # else:
        return 0


def get_rooms(channel) -> dict:
    return {}
    # uid = id_from_name(channel)
    # if uid:
    #     ret = request(f"https://api.twitch.tv/kraken/chat/{uid}/rooms", True, True)
    #     if ret.status_code == requests.codes.ok:
    #         out = ret.json()
    #         for room in out["rooms"]:
    #             room["parent"] = channel
    #     else:
    #         out = {}
    # else:
    #     out = {}
    # return out


def cb_join_channel(words: List[str], _: List[str], self):
    """The HexChat command `/join` has just been invoked. Find all Rooms of
        the channel being joined, and join them too.
    """
    self.echo(str(words))
    ctx = hexchat.get_context()
    if ctx.get_info("network").lower() != "twitch":
        return hexchat.EAT_NONE
    # TODO
