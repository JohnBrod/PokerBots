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

class Player(object):
    """docstring for Player"""
    def __init__(self, name):
        self.name = name
        self.cash = 0
        
if __name__=="__main__":
    unittest.main()