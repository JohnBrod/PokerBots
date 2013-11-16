import logging
from theHouse import Doorman
from theHouse import PlayerProxy
from theHouse import PublicAnnouncer
import texasHoldEm
from Xmpp import XmppMessenger
import traceback

playerCash = 1000

logging.basicConfig(filename='poker.log', level=logging.DEBUG)


def onPlayerJoined(sender, playerId):
    dealerMessenger.sendMessage('audience@pokerchat', playerId + ' has joined the game')

dealerMessenger = XmppMessenger('dealer@localhost', 'password')
dealerMessenger.listen('localhost', 5222)

dealerMessenger.sendMessage('audience@pokerchat', 'Game started, waiting for players')

try:
    frank = Doorman(5, dealerMessenger, playerCash)
    frank.evt_playerJoined += onPlayerJoined
    players = frank.greetPlayers()
except Exception, e:
    dealerMessenger.sendMessage(e)

if not players:
    dealerMessenger.sendMessage('audience@pokerchat', 'No players joined so quitting')
elif len(players) == 1:
    dealerMessenger.sendMessage('audience@pokerchat', 'Not enough players for a game so quitting')
else:

    try:
        players = map(lambda x: PlayerProxy(x, dealerMessenger, playerCash), players)
        dealer = texasHoldEm.Dealer(PublicAnnouncer())
        dealer.deal(players)
        while dealer.playing:
            pass
        dealerMessenger.sendMessage('audience@pokerchat', 'Game Over')
    except:
        print traceback.format_exc()

dealerMessenger.finish()
