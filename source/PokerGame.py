import sys
import logging

from theHouse import Dealer
from Xmpp import XmppMessenger

def write(text):
    print text
    sys.stdout.flush()

logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
logging.disable(logging.ERROR)

def onPlayerJoined(sender, args):
    write('Player1 has joined the game')

def onFinished(sender, args):
    write(args)

write('Game started, waiting for players')

dealer = Dealer(2, XmppMessenger('dealer@localhost', 'password'))
dealer.evt_playerJoined += onPlayerJoined
dealer.evt_finished += onFinished
dealer.start()