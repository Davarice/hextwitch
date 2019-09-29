"""Hexchat Plugin Stub.

Contains no functionality. Only Signatures.

(Incomplete)
"""

from typing import Any, Dict, List, Optional, Union


PRI_HIGHEST = 5
PRI_HIGH = 4
PRI_NORM = 3
PRI_LOW = 2
PRI_LOWEST = 1

EAT_PLUGIN = -3
EAT_HEXCHAT = -2
EAT_ALL = -1
EAT_NONE = 0


def prnt(string: str):
    ...


def emit_print(event_name: str, *args):
    ...


def command(string: str):
    ...


def nickcmp(s1: str, s2: str) -> int:
    ...


def strip(text: str, length: int = -1, flags: int = 3) -> str:
    ...


def get_info(type: str) -> Optional[str]:
    ...


def get_prefs(name: str) -> str:
    ...


def get_list(type: str) -> List:
    ...


def set_pluginpref(name: str, value) -> bool:
    ...


def get_pluginpref(name: str) -> Optional[Union[int, str]]:
    ...


def del_pluginpref(name: str) -> bool:
    ...


def list_pluginpref() -> List[str]:
    ...


class Attribute(object):
    ircv3: Dict[str, Any] = {}  # Only available by modding the Hexchat Source.
    time: int = 0


class context(object):
    def set(self):
        ...

    def prnt(self, string: str):
        ...


    def emit_print(self, event_name: str, *args):
        ...


    def command(self, string: str):
        ...


    def get_info(self, type: str) -> Optional[str]:
        ...


    def get_list(self, type: str) -> List:
        ...


def get_context() -> context:
    ...


def find_context(server: str = None, channel: str = None) -> context:
    ...
