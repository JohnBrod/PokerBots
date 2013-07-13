import unittest
from mock import MagicMock

from theHouse import Casino
from theHouse import Player
from theHouse import Dealer

class testPlayingGamesInTheCasino(unittest.TestCase):

    def testShouldTellTheDealerToDealToPlayers(self):
        player1 = Player(None, None)
        player1.cash = 1
        player1.gameResult = MagicMock()
        player2 = Player(None, None)
        player2.cash = 1
        player2.gameResult = MagicMock()

        dealer = RiggedDealer()
        c = Casino(dealer, [player1, player2])

        c.play()
        
        self.assertEqual(1, dealer.handsPlayed)
    
    def testTheWinnerIsThePlayerWithAllTheCash(self):
        player1 = Player(None, None)
        player1.gameResult = MagicMock()
        player1.cash = 1
        player2 = Player(None, None)
        player2.gameResult = MagicMock()
        player3 = Player(None, None)
        player3.gameResult = MagicMock()
        dealer = Dealer()
        dealer.deal = MagicMock()
        c = Casino(dealer, [player1, player2, player3])

        c.play()
        
        player1.gameResult.assert_called_once_with('You won')
        player2.gameResult.assert_called_once_with('You lost')
        player3.gameResult.assert_called_once_with('You lost')

    def testTellsTheDealerToDealUntilOnePlayerHasAllTheCash(self):
        player1 = Player(None, None)
        player1.gameResult = MagicMock()
        player1.cash = 1
        player2 = Player(None, None)
        player2.gameResult = MagicMock()
        player2.cash = 1
        player3 = Player(None, None)
        player3.gameResult = MagicMock()
        player3.cash = 1
        dealer = RiggedDealer()
        c = Casino(dealer, [player1, player2, player3])

        c.play()
        
        self.assertEqual(2, dealer.handsPlayed)

class RiggedDealer(object):
    """dealer that will take all the cash from the first player at the table"""
    def __init__(self):
        self.handsPlayed = 0
    
    def deal(self, table):
        self.handsPlayed += 1
        table[0].cash = 0

if __name__=="__main__":
    unittest.main()