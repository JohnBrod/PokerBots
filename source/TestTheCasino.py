import unittest
from mock import MagicMock

from theHouse import Casino
from theHouse import PlayerProxy
from Xmpp import XmppMessenger
from mock import create_autospec
from EventHandling import Event

def CreatePlayer(cash):
    mockMessenger = create_autospec(XmppMessenger)
    mockMessenger.evt_messageReceived = MagicMock()
    player = PlayerProxy(None, mockMessenger)
    player.cash = cash
    player.gameResult = MagicMock()
    return player

class testPlayingGamesInTheCasino(unittest.TestCase):

    def testShouldTellTheDealerToDealToPlayers(self):
        player1 = CreatePlayer(cash = 1)
        player2 = CreatePlayer(cash = 1)

        dealer = RiggedDealer()
        dealer.handsToPlay = 1
        c = Casino(dealer, [player1, player2])

        c.play()
        
        self.assertEqual(1, dealer.handsPlayed)
    
    def testTheWinnerIsThePlayerWithAllTheCash(self):
        player1 = CreatePlayer(cash = 1)
        player2 = CreatePlayer(cash = 1)
        player3 = CreatePlayer(cash = 1)
        dealer = RiggedDealer()
        dealer.handsToPlay = 2

        c = Casino(dealer, [player1, player2, player3])

        c.play()
        
        player1.gameResult.assert_called_once_with('You lost')
        player2.gameResult.assert_called_once_with('You lost')
        player3.gameResult.assert_called_once_with('You won')

    def testTellsTheDealerToDealUntilOnePlayerHasAllTheCash(self):
        player1 = CreatePlayer(cash = 1)
        player2 = CreatePlayer(cash = 1)
        player3 = CreatePlayer(cash = 1)
        dealer = RiggedDealer()
        dealer.handsToPlay = 2
        c = Casino(dealer, [player1, player2, player3])

        c.play()
        
        self.assertEqual(2, dealer.handsPlayed)

class RiggedDealer(object):
    """dealer that will take all the cash from the first player at the table"""
    def __init__(self):
        self.handsPlayed = 0
        self.handsToPlay = 0
        self.evt_handFinished = Event()

    def deal(self, table):
        self.handsPlayed += 1
        table[0].cash = 0

        if self.handsPlayed <= self.handsToPlay:
            self.evt_handFinished.fire(self, None)

if __name__=="__main__":
    unittest.main()