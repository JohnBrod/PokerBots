import unittest
from mock import MagicMock

from theHouse import Casino
from texasHoldEm import PlayerProxy
from texasHoldEm import Dealer

def CreatePlayer(cash):
    player = PlayerProxy(None, None)
    player.cash = cash
    player.gameResult = MagicMock()
    return player

class testPlayingGamesInTheCasino(unittest.TestCase):

    def testShouldTellTheDealerToDealToPlayers(self):
        player1 = CreatePlayer(cash = 1)
        player2 = CreatePlayer(cash = 1)

        dealer = RiggedDealer()
        c = Casino(dealer, [player1, player2])

        c.play()
        
        self.assertEqual(1, dealer.handsPlayed)
    
    def testTheWinnerIsThePlayerWithAllTheCash(self):
        player1 = CreatePlayer(cash = 1)
        player2 = CreatePlayer(cash = 0)
        player3 = CreatePlayer(cash = 0)
        dealer = Dealer()
        dealer.deal = MagicMock()
        c = Casino(dealer, [player1, player2, player3])

        c.play()
        
        player1.gameResult.assert_called_once_with('You won')
        player2.gameResult.assert_called_once_with('You lost')
        player3.gameResult.assert_called_once_with('You lost')

    def testTellsTheDealerToDealUntilOnePlayerHasAllTheCash(self):
        player1 = CreatePlayer(cash = 1)
        player2 = CreatePlayer(cash = 1)
        player3 = CreatePlayer(cash = 1)
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