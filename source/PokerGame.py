import sys
import logging

from theHouse import Doorman
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

jeeves = Doorman(5, messenger)
jeeves.evt_playerJoined += onPlayerJoined
players = jeeves.greetPlayers()

if not players:
    write('No players joined so quitting')
elif len(players) == 1:
	write('Not enough players for a game so quitting')
# else:
    # messenger.sendMessage('Player1@pokerchat', 'Private Cards')

messenger.finish()
    