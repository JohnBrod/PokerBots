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

messenger = XmppMessenger('dealer@localhost', 'password')
messenger.listen('localhost', 5222)

try:
	frank = Doorman(5, messenger, 1000)
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
		players = map(lambda x: PlayerProxy(x, messenger), players)
		casino = Casino(texasHoldEm.Dealer(), players)
		casino.play()
	except Exception, e:
		write(e)

messenger.finish()
