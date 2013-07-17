import unittest
from theHouse import PlayerProxy
from texasHoldEm import Dealer
from mock import create_autospec
from Xmpp import XmppMessenger
from mock import MagicMock

def createMessenger():
    mockMessenger = create_autospec(XmppMessenger)
    mockMessenger.evt_messageReceived = MagicMock()
    return mockMessenger

def createPlayer():
    return PlayerProxy(None, createMessenger())

class testTheRotationOfTheDeal(unittest.TestCase):

    def testDealsToPlayer(self):
        player = createPlayer()
        player.yourGo = MagicMock()

        Dealer().deal([player])

        self.assertTrue(player.yourGo.called)

    def testDealsToNextPlayerWhenPlayerResponds(self):
        player = createPlayer()
        nextPlayer = createPlayer()
        nextPlayer.yourGo = MagicMock()

        Dealer().deal([player, nextPlayer])

        player.response.fire(player, 'anything')

        self.assertTrue(nextPlayer.yourGo.called)

    def testDealsToFirstPlayerWhenLastPlayerResponds(self):
        player = createPlayer()
        player.yourGo = MagicMock()

    	nextPlayer = createPlayer()

    	Dealer().deal([player, nextPlayer])

        player.response.fire(player, 'anything')
        nextPlayer.response.fire(nextPlayer, 'something')

    	self.assertEqual(2, len(player.yourGo.mock_calls))

    def testTellsPlayerThatTheyAreOutIfTheyRespondOutOfTurn(self):
        player = createPlayer()
        nextPlayer = createPlayer()
        nextPlayer.outOfGame = MagicMock()

        Dealer().deal([player, nextPlayer])

        nextPlayer.response.fire(nextPlayer, 'anything')

        nextPlayer.outOfGame.assert_called_once_with()

    def testDoesNotDealToRemovedPlayer(self):
        player = createPlayer()
        nextPlayer = createPlayer()
        nextPlayer.yourGo = MagicMock()

        Dealer().deal([player, nextPlayer])

        nextPlayer.response.fire(nextPlayer, 'anything')

        self.assertEqual(0, len(nextPlayer.yourGo.mock_calls))
                
if __name__=="__main__":
    unittest.main()