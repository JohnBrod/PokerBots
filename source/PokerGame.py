from threading import Thread
import logging
from theHouse import Doorman
from texasHoldEm import MessageInterpreter
from texasHoldEm import HostsGame
from Xmpp import XmppMessenger
import traceback
import time
from optparse import OptionParser


def countdown(duration):
    for i in xrange(duration):
        time.sleep(1)
        print 'start in {0} seconds'.format(duration - i)


if __name__ == '__main__':

    optp = OptionParser()

    optp.add_option('-d', '--dealerjid',
                    help='jid of account that deals and handles betting',
                    action="store", type="string", dest="dealerjid",
                    default='dealer@pokerchat')

    optp.add_option('-p', '--dealerpassword',
                    help='password of account that deals and handles betting',
                    action="store", type="string", dest="dealerpassword",
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

    logging.basicConfig(filename='poker.log', level=logging.DEBUG)
    messenger = XmppMessenger(opts.dealerjid, opts.dealerpassword)

    try:
        messenger.listen(opts.domain, opts.port)
        interpreter = MessageInterpreter(messenger, opts.audiencejid)

        startMessage = 'Game started, waiting for players'
        messenger.sendMessage(opts.audiencejid, startMessage)
        frank = Doorman(opts.wait, interpreter, opts.chips)
        Thread(target=countdown, args=(opts.wait,)).start()
        players = frank.greetPlayers()
    except:
        print traceback.format_exc()

    if not players:
        msg = 'No players joined so quitting'
        messenger.sendMessage(opts.audiencejid, msg)
        print msg
    elif len(players) == 1:
        msg = 'Not enough players for a game so quitting'
        messenger.sendMessage(opts.audiencejid, msg)
        print msg
    else:

        try:
            game = HostsGame(interpreter)
            game.start(players)
            while game.playing:
                time.sleep(1)

            messenger.sendMessage(opts.audiencejid, 'Game Over')
        except:
            print traceback.format_exc()

    messenger.finish()
