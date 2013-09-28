import unittest
from texasHoldEm import Pot


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


class testDetermingWhenTheRoundOfBettingIsOver(unittest.TestCase):

    def setUp(self):
        print 'Determing when the betting is over,', self.shortDescription()

    def testOverWhenAllPlayersHaveAddedTheSameAmount(self):
        '''over when all players have added the same amount'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 10)
        p.add(p2, 10)

        self.assertTrue(p.roundOfBettingOver())

    def testNotOverWhenSomePlayersStillOweCash(self):
        '''not over when some players still owe cash'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 10)
        p.add(p2, 15)

        self.assertFalse(p.roundOfBettingOver())

    def testNotOverWhenTheBigBlindIsDueTheOption(self):
        '''not over when the big blind owes the option'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 5)

        self.assertFalse(p.roundOfBettingOver())

    def testBigBlindDoesNotGetOptionTheSecondTime(self):
        '''big blind will not get the option the second time'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 5)
        p.add(p2, 5)
        p.add(p1, 5)

        self.assertTrue(p.roundOfBettingOver())

    def testPlayerFolding(self):
        '''over when a player folds'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 0)

        self.assertTrue(p.roundOfBettingOver())

    def testGameContinuesAfterPlayerFolding(self):
        '''continues after a player folds'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')
        p3 = Player('p3')

        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p3, 15)
        p.add(p1, 0)

        self.assertFalse(p.roundOfBettingOver())

    def testBigBlindIsNotOutWhenItChecksTheOption(self):
        '''big blind is not out when they check on the option'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 5)
        p.add(p2, 0)
        p.add(p1, 10)

        self.assertFalse(p.roundOfBettingOver())

    def testBigBlindFolding(self):
        '''over when the big blind folds'''
        p = Pot()
        p1 = Player('p1')
        p2 = Player('p2')

        p.add(p1, 5)
        p.add(p2, 10)
        p.add(p1, 5)
        p.add(p2, 0)
        p.add(p1, 10)
        p.add(p2, 0)

        self.assertTrue(p.roundOfBettingOver())


class Player(object):
    """docstring for Player"""
    def __init__(self, name):
        self.name = name
        self.cash = 0


if __name__ == "__main__":
    unittest.main()
