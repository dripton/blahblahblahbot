#!/usr/bin/env python3

"""An IRC quote bot."""

import sys

from twisted.internet import defer, endpoints, protocol, reactor, ssl, task
from twisted.python import log
from twisted.words.protocols import irc

import config
import database


class IRCProtocol(irc.IRCClient):

    nickname = config.nickname

    def __init__(self):
        self.deferred = defer.Deferred()

    def connectionLost(self, reason):
        self.deferred.errback(reason)

    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)

    def privmsg(self, user, channel, message):
        nick, _, host = user.partition("!")
        message = message.strip()
        if not message.startswith("!"):
            return
        command, sep, rest = message.lstrip("!").partition(" ")
        func = getattr(self, "command_" + command, None)
        if not func:
            return
        deferred = defer.maybeDeferred(func, nick, channel, rest)
        deferred.addErrback(self._showError)
        if channel == self.nickname:
            deferred.addCallback(self._sendMessage, nick)
        else:
            deferred.addCallback(self._sendMessage, channel, nick)

    def _sendMessage(self, msg, target, nick=None):
        if nick:
            msg = "%s, %s" % (nick, msg)
        self.msg(target, msg)

    def _showError(self, failure):
        return failure.getErrorMessage()

    def command_ping(self, nick, channel, rest):
        return "pong"

    def command_help(self, nick, channel, rest):
        return "!addquote (aq), !deletequote (dq), !quote (q), !findquote (fq)"

    def command_addquote(self, nick, channel, rest):
        return self.factory.db.add_quote(rest, channel, nick)

    command_aq = command_addquote

    def command_deletequote(self, nick, channel, rest):
        return self.factory.db.delete_quote(rest, channel, nick)

    command_dq = command_deletequote

    def command_quote(self, nick, channel, rest):
        return self.factory.db.quote(channel)

    command_q = command_quote

    def command_findquote(self, nick, channel, rest):
        return self.factory.db.find_quote(rest, channel)

    command_fq = command_findquote


class IRCFactory(protocol.ReconnectingClientFactory):
    protocol = IRCProtocol
    channels = config.channels
    db = database.Database(config.sqlite_path)


def run(reactor, host, port):
    options = ssl.optionsForClientTLS(host)
    endpoint = endpoints.SSL4ClientEndpoint(reactor, host, port, options)
    factory = IRCFactory()
    deferred = endpoint.connect(factory)
    deferred.addCallback(lambda protocol: protocol.deferred)
    return deferred


def main():
    log.startLogging(sys.stderr)
    task.react(run, (config.serverhost, config.serverport))


if __name__ == "__main__":
    main()
