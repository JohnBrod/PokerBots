import unittest
from texasHoldEm import Pot


class testFiguringOutTheWinnerOfaPot(unittest.TestCase):

    def setUp(self):
        print 'Figuring out the winner of a pot,', self.shortDescription()

    def testA_noPlayersMeansNoWinner(self):
        '''no players means no winner'''

        p = Pot()
        p1 = Player('p1')

        self.assertEqual([], p.getWinners([p1]))

    def testB_noRankingMeansNoWinner(self):
        '''no ranking means no winner'''

        p = Pot()
        p1 = Player('p1')
        p.add(p1, 5)

        self.assertEqual([], p.getWinners([]))

    def testC_onePlayerOneRankingMeansThatPlayerWinsThePot(self):
        '''one player one ranking means that player wins the pot'''

        p = Pot()
        p1 = Player('p1')
        p.add(p1, 5)

        self.assertEqual([(p1, 5)], p.getWinners([p1]))

    def testD_highestRankingPlayerWins(self):
        '''the highest ranking player wins'''

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        p.add(p1, 5)
        p.add(p2, 5)

        self.assertEqual([(p1, 10)], p.getWinners([p1, p2]))

    def testE_nextHighestWinsIfTheHighestIsNotInThePot(self):
        '''the next highest wins if the highest is not in the pot'''

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        p.add(p2, 5)

        self.assertEqual([(p2, 5)], p.getWinners([p1, p2]))


class testFiguringOutTheWinnerOfaSidePot(unittest.TestCase):

    def setUp(self):
        print 'Figuring out the winner of a side pot,', self.shortDescription()

    def testA_noPlayersMeansNoWinner(self):
        '''no players means no winner'''

        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 10)
        p.add(p2, 5)

        self.shouldMatch([(p1, 5), (p2, 10)], p.getWinners([p2, p1]))

    def shouldMatch(self, a, b):
        a = map(lambda x: (x[0].name, x[1]), a)
        b = map(lambda x: (x[0].name, x[1]), b)

        self.assertEqual(a, b)


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
