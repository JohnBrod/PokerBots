import sys
import logging
from theHouse import Doorman
from theHouse import Casino
from theHouse import PlayerProxy
import texasHoldEm
from Xmpp import XmppMessenger
		

class AnyDeck():
    def take(self):
        pass

def write(text):
	print text
	sys.stdout.flush()

logging.basicConfig(filename='poker.log',level=logging.DEBUG)

def onPlayerJoined(sender, playerId):
	write(playerId + ' has joined the game')

write('Game started, waiting for players')

dealerMessenger = XmppMessenger('dealer@localhost', 'password')
dealerMessenger.listen('localhost', 5222)

try:
	frank = Doorman(5, dealerMessenger, 1000)
	frank.evt_playerJoined += onPlayerJoined
	players = frank.greetPlayers()
except Exception, e:
	write(e)

if not players:
	write('No players joined so quitting')
elif len(players) == 1:
	write('Not enough players for a game so quitting')
else:

	try:
		players = map(lambda x: PlayerProxy(x, dealerMessenger), players)
		dealer = texasHoldEm.Dealer(AnyDeck())
		dealer.deal(players)
		while dealer.playing: pass 
	except Exception, e:
		write(e)

dealerMessenger.finish()
