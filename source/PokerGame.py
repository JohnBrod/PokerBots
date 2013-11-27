from threading import Thread
import logging
from theHouse import Doorman
import texasHoldEm
from Xmpp import XmppMessenger
import traceback
import time
import sys


def countdown(duration):
    for i in xrange(duration):
        time.sleep(1)
        print 'start in {0} seconds'.format(duration - i)

if len(sys.argv) != 2:
    raise Exception('Usage: PokerGame <wait duration in seconds>')
    
playerCash = 1000
waitForPlayers = int(sys.argv[1])

logging.basicConfig(filename='poker.log', level=logging.DEBUG)

dealerMessenger = XmppMessenger('dealer@localhost/real', 'password')
dealerMessenger.listen('localhost', 5222)
interpreter = texasHoldEm.XmppMessageInterpreter(dealerMessenger)

startMessage = 'Game started, waiting for players'
dealerMessenger.sendMessage('audience@pokerchat', startMessage)

try:
    frank = Doorman(waitForPlayers, interpreter, playerCash)
    Thread(target=countdown, args=(waitForPlayers,)).start()
    players = frank.greetPlayers()
except:
    print traceback.format_exc()

if not players:
    msg = 'No players joined so quitting'
    dealerMessenger.sendMessage('audience@pokerchat', msg)
    print msg
elif len(players) == 1:
    msg = 'Not enough players for a game so quitting'
    dealerMessenger.sendMessage('audience@pokerchat', msg)
    print msg
else:

    try:
        dealer = texasHoldEm.Dealer(interpreter)
        dealer.deal(players)
        while dealer.playing:
            time.sleep(1)

        dealerMessenger.sendMessage('audience@pokerchat', 'Game Over')
    except:
        print traceback.format_exc()

dealerMessenger.finish()
