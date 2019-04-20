"""Copyright @Davarice 2019, GPLv3

Formatting plugin for use with HexChat and Twitch.TV
Parses IRCv3 tags from Twitch, representing subscriptions, raids, etc, and
displays them properly in chat. Also prepends badges to the usernames of
broadcasters, moderators, etc.

NOTE: This plugin --MUST-- be used with a version of HexChat that exposes IRCv3
to the Python interface. As of this writing, the main branch DOES NOT support
this.
"""

import hexchat

import hexchat_twitch as plugin


__module_name__ = "HexTwitch"
__module_version__ = plugin.VERSION
__module_description__ = (
    '(irc.twitch.tv) Subscription notifications, name shortening, user "badges", and more'
)
