import sys
import logging

from theHouse import Doorman
from Xmpp import XmppMessenger

def write(text):
    print text
    sys.stdout.flush()

logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
logging.disable(logging.ERROR)

def onPlayerJoined(sender, args):
    write('Player1 has joined the game')

write('Game started, waiting for players')

jeeves = Doorman(2, XmppMessenger('dealer@localhost', 'password'))
jeeves.evt_playerJoined += onPlayerJoined
players = jeeves.greetPlayers()

if players:
	write('Not enough players for a game so quitting')
else:
	write('No players joined so quitting')