"""Copyright @Davarice 2019, GPLv3

Formatting plugin for use with HexChat and Twitch.TV
Parses IRCv3 tags from Twitch, representing subscriptions, raids, etc, and
displays them properly in chat. Also prepends badges to the usernames of
broadcasters, moderators, etc.

NOTE: This plugin --MUST-- be used with a version of HexChat that exposes IRCv3
to the Python interface. As of this writing, the main branch DOES NOT support
this.
"""

from pathlib import Path
import sys

# The "hexchat" module does not actually exist anywhere we can consistently find
#   it. However, its API is documented here:
# https://hexchat.readthedocs.io/en/latest/script_python.html
import hexchat

sys.path.append(str(Path.home() / "Development/git/hextwitch"))
import hexchat_twitch as plugin


# Set information that will be displayed in the HexChat Addons list.
__module_name__ = "HexTwitch"
__module_version__ = plugin.VERSION
__module_description__ = (
    "(irc.twitch.tv) "
    'Subscription notifications, name shortening, user "badges", and more.'
)

# Initialize the plugin.
Twitch = plugin.HexTwitch()

# Set up all necessary Callbacks.
hexchat.hook_server_attrs("RAW LINE", Twitch.cb_message_server)
# hexchat.hook_command("say", Twitch.cb_message_send)
hexchat.hook_print("Focus Tab", Twitch.cb_focus, priority=hexchat.PRI_LOW)

for event in plugin.events_recv:
    hexchat.hook_print_attrs(event, Twitch.cb_message_hex, userdata=event)

for event in plugin.events_send:
    hexchat.hook_print(event, Twitch.cb_message_user, userdata=event)

for key, (func, ht) in plugin.commands.items():
    hexchat.hook_command(key, func, Twitch, help=ht)


Twitch.echo("{} v{} loaded.".format(__module_name__, __module_version__), "Motd")
