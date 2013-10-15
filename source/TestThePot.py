import unittest
from texasHoldEm import Pot


class testTheTotalOfThePot(unittest.TestCase):

    def setUp(self):
        print 'The total of the pot,', self.shortDescription()

    def testA_ZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        p = Pot()

        self.assertEqual(0, p.total())

    def testB_IncrementsWhenChipsAreAdded(self):
        '''increments when chips are added'''

        p = Pot()
        p1 = Player('p1')

        p.add(p1, 5)

        self.assertEqual(5, p.total())

    def testB_IncrementsWhenMoreChipsAreAdded(self):
        '''increments when more chips are added'''

        p = Pot()
        p1 = Player('p1')

        p.add(p1, 5)
        p.add(p1, 10)

        self.assertEqual(15, p.total())


class testTheMinimumBetOfThePot(unittest.TestCase):

    def setUp(self):
        print 'The minimum bet of the pot,', self.shortDescription()

    def testZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        p = Pot()
        p1 = Player('p1')

        self.assertEqual(0, p.getMinimumBet(p1))

    def testSecondPlayerMustBetAtLeastTheFirstBet(self):
        '''second player should pay at least the first bet'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)

        self.assertEqual(5, p.getMinimumBet(p2))

    def testZeroBecauseAllAreEven(self):
        '''zero when all players are even'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 5)

        self.assertEqual(0, p.getMinimumBet(p1))
        self.assertEqual(0, p.getMinimumBet(p2))

    def testShouldPayTheDifferenceWhenRaised(self):
        '''player should pay the difference when raised'''

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 10)

        self.assertEqual(5, p.getMinimumBet(p1))

    def testZeroOnceTheRoundIsComplete(self):
        '''will be zero once the round is complete'''
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


if __name__ == "__main__":
    unittest.main()
