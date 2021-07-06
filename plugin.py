###
# Copyright (c) 2021, Nicolas Coevoet
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from supybot import utils, plugins, ircutils, callbacks, ircmsgs, conf, ircdb
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('CheckInvite')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

invites = {}

class CheckInvite(callbacks.Plugin):
    """Join channel when on invite if bot has +o on ACL and provide some initial tips"""
    threaded = True

    def doInvite(self, irc, msg):
        channel = msg.args[1]
        if msg.nick == 'ChanServ':
            return
        self.log.info('%s invited me in %s' % (msg.prefix,channel))
        if not channel in invites and not channel in self.registryValue('ignores'):
            invites[channel] = msg.nick
            irc.queueMsg(ircmsgs.IrcMsg('CS STATUS %s' % channel))

    def doNotice(self, irc, msg):
        (targets, text) = msg.args
        text = ircutils.stripBold(text)
        if msg.nick == 'ChanServ' and targets == irc.nick:
#            self.log.info('CheckInvite --> %s' % text)
            ACCESS = 'You have access flags '
            if text.startswith(ACCESS):
               flag = text.split(ACCESS)[1].split(' ')[0]
               channel = text.split(ACCESS)[1].split(' ')[2].strip().split('.')[0]
               if 'o' in flag and channel in invites:
                   irc.queueMsg(ircmsgs.IrcMsg('JOIN %s' % channel))
                   try:
                       network = conf.supybot.networks.get(irc.network)
                       network.channels().add(channel)
                   except KeyError:
                       pass
                   irc.queueMsg(ircmsgs.notice(invites[channel],"Channel joined. Important: operator rights for %s are granted when i see someone identified to services adding or removing a ban or quiet, so please do that first!" % channel))
                   irc.queueMsg(ircmsgs.notice(invites[channel],"Available commands are: list chantracker, help <command name>, documentation: https://github.com/ncoevoet/ChanTracker#commands"))
                   irc.queueMsg(ircmsgs.notice(invites[channel],"Do you want new bans/quiets to be removed after a given period if no duration is given by the channel operator ? /msg %s help cautoexpire" % irc.nick))
                   irc.queueMsg(ircmsgs.notice(invites[channel],"Do you have a -ops channel or a channel where the bot should announces new bans/quiets ? contact staffers in #libera-bots"))
                   irc.queueMsg(ircmsgs.notice(invites[channel],"If you have a -ops channel would you like the bot to reply when addressed by nick or ! ? contact staffers in #libera-bots"))
                   irc.queueMsg(ircmsgs.notice(invites[channel],"i offers various channel protections against floods, repetitions, hilights, join/part flood, etc ... (https://github.com/ncoevoet/ChanTracker#channel-protection) and /msg %s help cflood or chl etc ..." % irc.nick))
                   if self.registryValue('logChannel') in irc.state.channels:
                       irc.queueMsg(ircmsgs.privmsg(self.registryValue('logChannel'),"[%s] joined due to %s's invitation" % (channel, invites[channel])))
                   del invites[channel]
            elif text.endswith(' is not registered.'):
               channel = text.split(' ')[0].strip()
               if channel in invites:
                   irc.queueMsg(ircmsgs.notice(invites[channel],"%s is not a registered channel: invite me once that's the case and once i have +o flag on the ACL" % channel))
                   del invites[channel]
            elif text.startswith('You have no special access to '):
               channel = text.split('You have no special access to ')[1].strip().split('.')[0]
               if channel in invites:
                   irc.queueMsg(ircmsgs.notice(invites[channel],"Error, i need operator access: /msg ChanServ flags %s %s +o . Invite me again once that's the case" % (channel,irc.nick)))
                   del invites[channel]

Class = CheckInvite


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
