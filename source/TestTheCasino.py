import unittest
from mock import MagicMock

from texasHoldEm import Dealer
from theHouse import Casino
from theHouse import PlayerProxy
from Xmpp import XmppMessenger
from mock import create_autospec

def CreatePlayer(cash):
    mockMessenger = create_autospec(XmppMessenger)
    mockMessenger.evt_messageReceived = MagicMock()
    player = PlayerProxy(None, mockMessenger)
    player.cash = cash
    player.gameResult = MagicMock()
    return player

# hand finished and one player has all the money then game over
# hand finished and no winner then deal again

class testPlayingGamesInTheCasino(unittest.TestCase):
    pass

if __name__=="__main__":
    unittest.main()