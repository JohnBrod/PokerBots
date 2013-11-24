import logging
from theHouse import Doorman
import texasHoldEm
from Xmpp import XmppMessenger
import traceback

playerCash = 1000
waitForPlayers = 5

logging.basicConfig(filename='poker.log', level=logging.DEBUG)

dealerMessenger = XmppMessenger('dealer@localhost/real', 'password')
dealerMessenger.listen('localhost', 5222)
interpreter = texasHoldEm.XmppMessageInterpreter(dealerMessenger)

dealerMessenger.sendMessage('audience@pokerchat', 'Game started, waiting for players')

try:
    frank = Doorman(waitForPlayers, interpreter, playerCash)
    players = frank.greetPlayers()
except:
    print traceback.format_exc()

if not players:
    dealerMessenger.sendMessage('audience@pokerchat', 'No players joined so quitting')
elif len(players) == 1:
    dealerMessenger.sendMessage('audience@pokerchat', 'Not enough players for a game so quitting')
else:

    try:
        dealer = texasHoldEm.Dealer(interpreter)
        dealer.deal(players)
        while dealer.playing:
            pass
        dealerMessenger.sendMessage('audience@pokerchat', 'Game Over')
    except:
        print traceback.format_exc()

dealerMessenger.finish()
