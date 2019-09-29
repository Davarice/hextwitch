"""Module to read Configuration files into memory and access data from them.

Config files may define a "shadow" value at the top level, which is the file
    path of another Config file. If this second file is found, it will be loaded
    over the main one, transparently. This allows one to define a global config
    that will overwrite itself with values from a local config, or vice versa.

Uses YAML by default, but can be easily modified to accept any file format which
    can be loaded into a Python datastructure.
"""

from pathlib import Path
from typing import Union

import oyaml


cfg_dirs = ["~/.config/hexchat", "~/"]


def read_file(path: Path):
    newfile = path.resolve()
    if newfile.is_file():
        with newfile.open("r") as file:
            dat = oyaml.load(file)
        return dat
    else:
        return {}


def ensure_key(data, key: str):
    """Given a data structure and a string key, ensure that the key is of an
        appropriate type to be used as a subscription of the data.
    """
    err = ValueError(
        f"{key!r} is not a valid subscript value for type {type(data).__name__!r}."
    )
    if type(data) == dict:
        true_key = key
    elif type(data) in (list, str, tuple):
        if key.lstrip("-").isdigit() and key.count("-") <= 1:
            true_key = int(key)
        else:
            raise err
    else:
        raise err
    return true_key


def set_value(data, key, value):
    """Given a data structure, a key, and a new value destined for `data[key]`,
        first ensure the key, and then ensure that the value can be assigned to
        `data[key]`.

    Returns True if the assignment was done successfully, otherwise False.
    """
    # Sanity check the Key type.
    key = ensure_key(data, key)
    if type(data) == dict:
        # Data is a Dict.
        if key in data:
            # Key is a key present in the Dict, so we convert value to the type
            #   of the current value.
            try:
                new = type(data[key])(value)
            except ValueError:
                return False
        else:
            # Key is not present in the Dict, so assume the value type does not
            #   matter.
            new = value
    elif type(data) == list:
        if not -1 <= key <= len(data):
            # Key must be no less than negative one and no more than one more
            #   than the highest present index. An index of -1 (or the highest
            #   plus one) will append the value rather than replacing one.
            return False
        if data:
            # The List is not empty. Try, if possible, to set the type of the
            #   value to match all the other elements in the List.
            first_type = type(data[0])
            if all([type(x) == first_type for x in data]):
                # Every item in the List is the same type. Make value conform.
                try:
                    new = first_type(value)
                except ValueError:
                    return False
            else:
                # The List is heterogenous. Value type does not matter.
                new = value
        else:
            # The List is empty. Value type does not matter.
            new = value
        if key == -1 or key == len(data):
            data.append(new)
            return True
    else:
        # Data is something else. It may still be Iterable, like a String or
        #   a Set, but it is not mutable in this way.
        return False
    data[key] = new
    return True


class ConfigReader:
    """Class that serves as an interface to Configuration Files."""

    def __init__(self, path: Union[Path, str] = ""):
        self.cfg_dict = {}
        self.cfg_path = ""
        self.root = (Path.cwd() / path).resolve()

    def clear(self):
        self.cfg_dict = {}

    def get(self, key, default=None):
        """Follow a slash-separated "path" to a value in the config file, and
            retrieve a value.
        """
        route = key.split("/")
        here = self.cfg_dict
        try:
            # Start at the top of the Dict, and take each component of the path
            #   as the next key to go to in sequence.
            for part in route:
                here = here[ensure_key(here, part)]
        except KeyError:
            # If this is ever raised, return the default value.
            return default
        else:
            # If we get through every value, return the final object.
            return here

    def set(self, key, value):
        """Follow a slash-separated "path" to a value in the config file, and
            insert a value.
        """
        route = key.split("/")
        here = self.cfg_dict
        try:
            # Start at the top of the Dict, and take each component of the path
            #   as the next key to go to in sequence.
            while len(route) > 1:
                here = here[ensure_key(here, route.pop(0))]
        except KeyError:
            # If this is ever raised, stop immediately.
            return
        else:
            # When we reach the final path segment, assign the value to the key
            #   under the current structure.
            set_value(here, route.pop(0), value)

    def load(self, filepath: str = "", follow=True):
        """Locate and read the specified file, then save it in memory as a dict.
            Config file may specify a "shadow", which will then be loaded in and
            overwrite it. This is useful for "transparent" configurations, as it
            allows them to chain.
        """
        fp = Path(filepath)
        if fp.is_absolute():
            dat = read_file(fp)
        else:
            dat = {}
            for directory in cfg_dirs:
                dat = read_file(Path(directory) / fp)
                if dat:
                    break

        if dat:
            self.cfg_dict.update(dat)

        if "shadow" in self.cfg_dict:
            nextload = self.cfg_dict.pop("shadow")
            if follow and nextload:
                self.load(nextload)

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return self.get(attr)


cfg = ConfigReader()
