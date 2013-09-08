import unittest
from texasHoldEm import Pot

class testTheMinimumBetOfThePot(unittest.TestCase):

    def testZeroWhenThereIsNothingInThePot(self):

        p = Pot()
        p1 = Player('p1')

        self.assertEqual(0, p.getMinimumBet(p1))

    def testSecondPlayerMustBetAtLeastTheFirstBet(self):

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 5)

        self.assertEqual(5, p.getMinimumBet(p2))

    def testZeroBecauseAllAreEven(self):

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 5)
        p.add(p2, 5)

        self.assertEqual(0, p.getMinimumBet(p1))
        self.assertEqual(0, p.getMinimumBet(p2))

    def testShouldPayTheDifferenceWhenRaised(self):

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 5)
        p.add(p2, 10)

        self.assertEqual(5, p.getMinimumBet(p1))

    def testZeroOnceTheRoundIsComplete(self):

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 10)
        p.add(p2, 10)

        self.assertEqual(0, p.getMinimumBet(p1))

class testDetermingWhenTheRoundOfBettingIsOver(unittest.TestCase):
# over when all players have contributed the same amount
# not over when some players still owe cash
# not over when the big blind is due the option

# test the second round of betting, player should be able to check at the start

# test player folding

    # example of behaviour that is not needed. This behaviour is not needed because of how the pot is used by the dealer. 
    # This is one advantage of top down over bottom up, the danger but building a class that can do everything.
    # def testNotOverWhenThereAreNoContributions(self):
    #     p = Pot()

    #     self.assertFalse(p.roundOfBettingOver())

    def testOverWhenAllPlayersHaveAddedTheSameAmount(self):
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 10)
        p.add(p2, 10)

        self.assertTrue(p.roundOfBettingOver())

    def testNotOverWhenSomePlayersStillOweCash(self):
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 10)
        p.add(p2, 15)

        self.assertFalse(p.roundOfBettingOver())

    def testNotOverWhenTheBigBlindIsDueTheOption(self):
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 5)

        self.assertFalse(p.roundOfBettingOver())

    def testBigBlindDoesNotGetOptionTheSecondTime(self):
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        
        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 5)
        p.add(p2, 5)
        p.add(p1, 5)

        self.assertTrue(p.roundOfBettingOver())

class Player(object):
    """docstring for Player"""
    def __init__(self, name):
        self.name = name
        self.cash = 0
        
if __name__=="__main__":
    unittest.main()