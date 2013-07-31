import time
import sys
import logging
from theHouse import Doorman
from theHouse import Casino
from theHouse import PlayerProxy
import texasHoldEm
from Xmpp import XmppMessenger
		
def write(text):
	print text
	sys.stdout.flush()

logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
logging.disable(logging.ERROR)

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
		casino = Casino(texasHoldEm.Dealer(), players)
		# need to start this on a thread and wait for it to finish
		casino.play()
		while casino.playing: pass # could do screen updates here
	except Exception, e:
		write(e)

dealerMessenger.finish()