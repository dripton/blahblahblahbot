"""Sample Configuration

The bot doesn't actually read sample-config.py; it reads config.py instead.
So you need to copy this file to config.py then make your local changes there.
(The reason for this extra step is to make it harder for me to accidentally
check in private information like server names or passwords.)
"""

# The bot's IRC nick
nickname = "blahblahblahbot"

# Hostname of the IRC server.  For now, only one.
serverhost = "irc.example.com"

# Port of the IRC server.  For now, only one.
serverport = 6667

# List of IRC channels to watch
channels = ["#bottest"]

# List of bot admins.  For now, admins are global not per-channel.
admins = ["dripton"]

# SQLite 3 database path.
sqlite_path = "/var/tmp/blahblahblahbot.db"
