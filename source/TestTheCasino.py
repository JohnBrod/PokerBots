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

        dealer = Dealer()
        dealer.deal = MagicMock()
        c = Casino(dealer, [player1, player2])

        c.play()
        
        dealer.deal.assert_called_once_with([player1, player2])
    
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
        
class FakePlayer(object):
    """docstring for FakePlayer"""
    def __init__(self):
        pass


if __name__=="__main__":
    unittest.main()