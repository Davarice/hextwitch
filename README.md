# HexTwitch
This is a significant extension to HexChat that allows tighter integration with
Twitch.tv. It allows rendering of user badges, and display of chat events, as
provided by Twitch via IRCv3 tags.

The plugin has two primary components:
1. A package which will be placed in the system Python path. This package will
provide all the function of the plugin.
2. A script which will be placed in the HexChat Addons directory. This script
will import the above package and link the callbacks to HexChat hooks.
