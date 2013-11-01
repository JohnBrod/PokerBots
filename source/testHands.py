import unittest
from texasHoldEm import highestCard
from texasHoldEm import pair
from texasHoldEm import flush
from texasHoldEm import straight
from texasHoldEm import trips
from texasHoldEm import poker
from texasHoldEm import straightFlush
from texasHoldEm import house


class TestRecognizingHands(unittest.TestCase):

    def setUp(self):
        print 'Recognizing hands,', self.shortDescription()

    def testA_highestCard(self):
        '''the highest card'''
        hand = [(3, 'C'), (2, 'D')]
        self.assertEqual(highestCard(hand), (3, 'C'))

    def testB_Pair(self):
        '''a pairt'''
        hand = [(3, 'C'), (3, 'D')]
        self.assertEqual(pair(hand), hand)

    def testC_Trips(self):
        '''trips'''
        hand = [(3, 'H'), (3, 'C'), (3, 'D')]
        self.assertEqual(trips(hand), hand)

    def testD_Poker(self):
        '''four of a kind, aka poker'''
        hand = [(3, 'S'), (3, 'H'), (3, 'C'), (3, 'D')]
        self.assertEqual(poker(hand), hand)

    def testE_Flush(self):
        '''a flush'''
        hand = [(2, 'C'), (4, 'C'), (6, 'C'), (8, 'C'), (10, 'C')]
        self.assertEqual(flush(hand), [(10, 'C'), (8, 'C'), (6, 'C'), (4, 'C'), (2, 'C')])

    def testF_TakeHighestFlush(self):
        '''make sure to take the highest flush'''
        hand = [(1, 'C'), (2, 'C'), (4, 'C'), (5, 'C'), (7, 'C'), (9, 'C')]
        self.assertEqual(flush(hand), [(9, 'C'), (7, 'C'), (5, 'C'), (4, 'C'), (2, 'C')])

    def testG_Straight(self):
        '''a straight'''
        hand = [(1, 'H'), (2, 'C'), (3, 'H'), (4, 'S'), (5, 'D')]
        expected = [(5, 'D'), (4, 'S'), (3, 'H'), (2, 'C'), (1, 'H')]
        self.assertEqual(straight(hand), expected)

    def testH_UseTheHighestStraight(self):
        '''take the highest straight'''
        hand = [(1, 'D'), (2, 'D'), (3, 'C'), (4, 'C'), (5, 'H'), (6, 'H')]
        expected = [(6, 'H'), (5, 'H'), (4, 'C'), (3, 'C'), (2, 'D')]
        self.assertEqual(straight(hand), expected)

    def testI_NoGapsAllowed(self):
        '''no gaps in a straight'''

        hand = [(1, 'D'), (2, 'D'), (3, 'C'), (4, 'C'), (5, 'H'), (7, 'H')]
        expected = [(5, 'H'), (4, 'C'), (3, 'C'), (2, 'D'), (1, 'D')]
        self.assertEqual(straight(hand), expected)

    def testJ_NoDuplicatesInStraight(self):
        '''no duplicate faces in a straight'''
        hand = [(1, 'C'), (2, 'C'), (3, 'C'), (4, 'C'),
                (5, 'H'), (7, 'D'), (7, 'H')]
        expected = [(5, 'H'), (4, 'C'), (3, 'C'), (2, 'C'), (1, 'C')]
        self.assertEqual(straight(hand), expected)

    def testK_StraightFlush(self):
        '''a straight flush'''
        hand = [(1, 'H'), (2, 'H'), (3, 'H'), (4, 'H'), (5, 'H')]
        expected = [(5, 'H'), (4, 'H'), (3, 'H'), (2, 'H'), (1, 'H')]
        self.assertEqual(straightFlush(hand), expected)

    def testK_house(self):
        '''a house'''
        hand = [(1, 'H'), (1, 'C'), (1, 'D'), (4, 'H'), (4, 'C')]
        self.assertEqual(house(hand), hand)


if __name__ == "__main__":
    unittest.main()
