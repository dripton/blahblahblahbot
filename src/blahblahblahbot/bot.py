#!/usr/bin/env python3

"""An IRC quote bot."""

import sys

import config

from twisted.internet import defer, endpoints, protocol, reactor, ssl, task
from twisted.python import log
from twisted.words.protocols import irc


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
        deferred = defer.maybeDeferred(func, rest)
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

    def command_ping(self, rest):
        return "pong"

    def command_help(self, rest):
        return "!addquote, !deletequote, !quote"

    def command_addquote(self, rest):
        # TODO
        return "fake added a quote"

    def command_deletequote(self, rest):
        # TODO
        return "fake deleted a quote"

    def command_quote(self, rest):
        # TODO
        return "Eat my shorts! -- The Raven"


class IRCFactory(protocol.ReconnectingClientFactory):
    protocol = IRCProtocol
    channels = config.channels


def main(reactor, host, port):
    options = ssl.optionsForClientTLS(host)
    endpoint = endpoints.SSL4ClientEndpoint(reactor, host, port, options)
    factory = IRCFactory()
    deferred = endpoint.connect(factory)
    deferred.addCallback(lambda protocol: protocol.deferred)
    return deferred


if __name__ == "__main__":
    log.startLogging(sys.stderr)
    task.react(main, (config.serverhost, config.serverport))
