"""
Module dedicated to interfacing with the Twitch API
"""

import requests

from hexchat_twitch.config import cfg


baseurl = "https://api.twitch.tv/helix/"
games_cache = {}
temps = []


def request(url, auth=False, v5=False):
    """
    Send a query to a specified URL. This function mainly exists to apply the
        philosophy of DRY to the Request Header, which is always the same.
    """
    headers = {"Client-ID": cfg.get("client_id", "")}
    if auth:
        headers["Authorization"] = "OAuth " + (cfg.twitch_oauth or "")
    if v5:
        headers["Accept"] = "application/vnd.twitchtv.v5+json"
    return requests.get(url, headers=headers)


def make_url(qtype: str, prefix: str, logins: list) -> str:
    """
    Construct a Query URL based on a Query Type, a Prefix for each Query, and a
        List of Keys to query.
    :param qtype: Type of Query. "streams", "users", etc.
    :param prefix: String to be prepended to each Query String in the List.
    :param logins: A List of Queries to be made. Typically usernames.
    :return: A constructed Query URL that will return channel information.
    """
    print("info", "Querying '" + qtype + "'...")
    names = "&".join([prefix + login for login in logins])
    return baseurl + qtype + "?" + names


def id_from_name(name):
    req = request(make_url("users", "login=", [name]))
    if req.status_code == requests.codes.ok:
        return req.json()["data"][0]["id"]
    else:
        return 0


def rooms(channel):
    uid = id_from_name(channel)
    if uid:
        ret = request(
            "https://api.twitch.tv/kraken/chat/{}/rooms".format(uid), True, True
        )
        return ret.json() if ret.status_code == requests.codes.ok else {}
    else:
        return {}
