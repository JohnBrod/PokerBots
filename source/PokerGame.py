from threading import Thread
import logging
from texasHoldEm import InteractsWithPlayers
from texasHoldEm import PlaysTournament
from Xmpp import XmppMessenger
import traceback
import time
from optparse import OptionParser


class RunsPokerGame(object):
    def __init__(self, opts):
        self.opts = opts
        self.done = False
        self.msngr = XmppMessenger(self.opts.dealerjid, self.opts.dealerpwd)

    def onDone(self, sender=None, args=None):
        self.msngr.sendMessage(self.opts.audiencejid, 'Game Over')
        self.msngr.finish()
        self.done = True

    def start(self):
        try:
            self.msngr.listen(self.opts.domain, self.opts.port)
            self.msngr.addTarget(self.opts.audiencejid)
            interacts = InteractsWithPlayers(self.msngr, self.opts.chips)
            startMessage = 'Game started, waiting for players'
            self.msngr.sendMessage(self.opts.audiencejid, startMessage)
            Thread(target=countdown, args=(self.opts.wait,)).start()
            time.sleep(self.opts.wait)
        except:
            print traceback.format_exc()

        if not interacts.players:
            msg = 'No players joined so quitting'
            self.msngr.sendMessage(self.opts.audiencejid, msg)
            print msg
        elif len(interacts.players) == 1:
            msg = 'Not enough players for a game so quitting'
            self.msngr.sendMessage(self.opts.audiencejid, msg)
            print msg
        else:

            try:
                game = PlaysTournament(interacts)
                game.evt_done += self.onDone
                game.start()
                while not self.done:
                    time.sleep(1)
            except:
                print traceback.format_exc()


def countdown(duration):
    for i in xrange(duration):
        time.sleep(1)
        print 'start in {0} seconds'.format(duration - i)


def getOptions():

    optp = OptionParser()

    optp.add_option('-d', '--dealerjid',
                    help='jid of account that deals and handles betting',
                    action="store", type="string", dest="dealerjid",
                    default='dealer@pokerchat')

    optp.add_option('-p', '--dealerpwd',
                    help='password of account that deals and handles betting',
                    action="store", type="string", dest="dealerpwd",
                    default='password')

    optp.add_option('-a', '--audiencejid',
                    help='jid of account that receives all public broadcasts',
                    action="store", type="string", dest="audiencejid",
                    default='audience@pokerchat')

    optp.add_option('-c', '--chips',
                    help='number of chips to give each player',
                    action="store", type="int", dest="chips", default=1000)

    optp.add_option('-w', '--wait',
                    help='time (in seconds) to wait for players',
                    action="store", type="int", dest="wait", default=5)

    optp.add_option('-o', '--domain',
                    help='domian to connect',
                    action="store", type="string", dest="domain",
                    default='localhost')

    optp.add_option('-r', '--port',
                    help='port number to connect',
                    action="store", type="int", dest="port", default=5222)

    opts, args = optp.parse_args()

    return opts


if __name__ == '__main__':

    logging.basicConfig(filename='poker.log', level=logging.DEBUG)

    game = RunsPokerGame(getOptions())
    game.start()
