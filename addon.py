"""Copyright @Davarice 2019, GPLv3

Formatting plugin for use with HexChat and Twitch.TV
Parses IRCv3 tags from Twitch, representing subscriptions, raids, etc, and
    displays them properly in chat. Also prepends badges to the usernames of
    broadcasters, moderators, etc.

NOTE: This plugin --MUST-- be used with a version of HexChat that exposes IRCv3
    to the Python interface. As of this writing, the main branch DOES NOT
    support this.
"""

from pathlib import Path
import sys

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

# Set up all necessary Callbacks.
hexchat.hook_server_attrs("RAW LINE", plugin.cb_message_server)
# hexchat.hook_command("say", plugin.cb_message_send)
hexchat.hook_print("Focus Tab", plugin.cb_focus, priority=hexchat.PRI_LOW)

for event in plugin.messaging.events_recv:
    hexchat.hook_print_attrs(event, plugin.cb_message_hex, userdata=event)

for event in plugin.messaging.events_send:
    hexchat.hook_print(event, plugin.cb_message_user, userdata=event)

for key, (func, ht) in plugin.commands.items():
    hexchat.hook_command(key, func, plugin, help=ht)


plugin.echo(f"{__module_name__} v{__module_version__} loaded.", "Motd")
