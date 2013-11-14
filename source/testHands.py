import unittest
from theHouse import Hand
from theHouse import Card
from theHouse import highestCard
from theHouse import pairHand
from theHouse import twoPairHand
from theHouse import flush
from theHouse import straight
from theHouse import tripHand
from theHouse import pokerHand
from theHouse import straightFlush
from theHouse import house


class TestComparingAgainstHighCard(unittest.TestCase):

    def setUp(self):
        print 'Comparing against high card,', self.shortDescription()

    def testA_beatsLowerHighCard(self):
        '''beats a lower high card'''
        highCardA = cards('2D,4S,5C,6D,7H,9H,10H,13H')
        highCardB = cards('2D,4S,5C,6D,7H,9H,10H,12H')
        self.assertGreater(Hand(highCardA), Hand(highCardB))


class TestComparingAgainstPair(unittest.TestCase):

    def setUp(self):
        print 'Comparing against a pair,', self.shortDescription()

    def testA_beatsLowerPair(self):
        '''beats a lower pair'''
        pairA = cards('5D,5S,3C,4D,6H,8H,9H,10H')
        pairB = cards('4D,4S,3C,2D,6H,8H,9H,10H')
        self.assertGreater(Hand(pairA), Hand(pairB))

    def testB_beatsMatchingPairOnHighCard(self):
        '''beats a matching pair on the high card'''
        pairA = cards('5D,5S,3C,4D,6H,8H,9H,11H')
        pairB = cards('5D,5S,3C,4D,6H,8H,9H,10H')
        self.assertGreater(Hand(pairA), Hand(pairB))

    def testC_beatsHighCardHand(self):
        '''beats a high card hand'''
        aPair = cards('5D,5S,3C,4D,6H,8H,9H,11H')
        aHighCard = cards('2D,4S,5C,6D,7H,9H,10H,12H')
        self.assertGreater(Hand(aPair), Hand(aHighCard))

    def testD_equalWhenAllCardsAreSame(self):
        '''beats a matching pair on the high card'''
        pairA = cards('5D,5S,3C,4D,6H,8H,9H,11H')
        pairB = cards('5C,5H,3C,4D,6C,8H,9H,11H')
        self.assertEqual(Hand(pairA), Hand(pairB))


class TestComparingAgainstTwoPair(unittest.TestCase):

    def setUp(self):
        print 'Comparing against two pair,', self.shortDescription()

    def testA_beatsTwoPairOnHighPair(self):
        '''beats two pair with lower high pair'''
        twoPairA = cards('5D,5S,4C,4D,6H,8H,9H,10H')
        twoPairB = cards('4D,4S,2C,2D,6H,8H,9H,10H')
        self.assertGreater(Hand(twoPairA), Hand(twoPairB))

    def testB_beatsTwoPairOnLowPair(self):
        '''when high pairs are even, beats two pair with higheswt low pair'''
        twoPairA = cards('5D,5S,4C,4D,6H,8H,9H,10H')
        twoPairB = cards('5D,5S,2C,2D,6H,8H,9H,10H')
        self.assertGreater(Hand(twoPairA), Hand(twoPairB))

    def testC_highCardWinsWhenPairsAreEqual(self):
        '''the high card wins when the pairs are equal'''
        twoPairA = cards('5D,5S,4C,4D,6H,8H,9H,11H')
        twoPairB = cards('5D,5S,4C,4D,6H,8H,9H,10H')
        self.assertGreater(Hand(twoPairA), Hand(twoPairB))

    def testD_equalWhenTwoPairAndHighCArdAreEqual(self):
        '''equal when the two pairs and the high card are equal'''
        twoPairA = cards('5D,5S,4C,4D,6H,8H,9H,10H')
        twoPairB = cards('5D,5S,4C,4D,6H,8H,9H,10H')
        self.assertEqual(Hand(twoPairA), Hand(twoPairB))


class TestComparingAgainstTrips(unittest.TestCase):

    def setUp(self):
        print 'Comparing against trips,', self.shortDescription()

    def testA_beatsTripsWithOfLowerCard(self):
        '''beats trips with of lower card'''
        tripsA = cards('3D,3S,3D,5D,6H,8H,9H,10H')
        tripsB = cards('2D,2S,2C,5D,6H,8H,9H,10H')
        self.assertGreater(Hand(tripsA), Hand(tripsB))

    def testB_beatsEqualTripsOnHighCard(self):
        '''beats equal trips on high card'''
        tripsA = cards('3D,3S,3D,5D,6H,8H,9H,11H')
        tripsB = cards('3D,3S,3D,5D,6H,8H,9H,10H')
        self.assertGreater(Hand(tripsA), Hand(tripsB))

    def testC_beatsTwoPair(self):
        '''beats two pair'''
        aTrips = cards('3D,3S,3D,5D,6H,8H,9H,10H')
        aTwoPair = cards('2D,2S,4C,4D,6H,8H,9H,10H')
        self.assertGreater(Hand(aTrips), Hand(aTwoPair))

    def testB_equalToOtherTripsWhenAllCardsAreEqual(self):
        '''equal to other trips when other cards in the hand are equal'''
        tripsA = cards('3D,3S,3D,5D,6H,8H,9H,10H')
        tripsB = cards('3D,3S,3D,5D,6H,8H,9H,10H')
        self.assertEqual(Hand(tripsA), Hand(tripsB))


class TestComparingAgainstStraight(unittest.TestCase):

    def setUp(self):
        print 'Comparing against a straight,', self.shortDescription()

    def testA_sameAsStraightWithMatchingValues(self):
        '''is ranked the same as a straight with matching values'''
        straightA = cards('2C,3D,4H,5S,6S,8H,9H,10H')
        straightB = cards('2D,3S,4S,5D,6H,8H,9H,10H')
        self.assertEqual(Hand(straightA), Hand(straightB))

    def testB_beatsStraightWithLowerHighCard(self):
        '''beats a straight with a lower high card'''
        straightA = cards('3D,4H,5S,6S,7H,8H,9H,10H')
        straightB = cards('2D,3S,4S,5D,6H,8H,9H,10H')
        self.assertGreater(Hand(straightA), Hand(straightB))

    def testB_beatsTrips(self):
        '''beats trips'''
        aStraight = cards('2D,3S,4S,5D,6H,8H,9H,10H')
        aTrips = cards('2D,2S,2C,5D,6H,8H,9H,10H')
        self.assertGreater(Hand(aStraight), Hand(aTrips))


class TestComparingAgainstFlush(unittest.TestCase):

    def setUp(self):
        print 'Comparing against a flush,', self.shortDescription()

    def testA_sameAsFlushWithMatchingValues(self):
        '''is ranked the same as a flush with matching values'''
        flushA = cards('2D,4D,6D,8D,10D,8H,9H,10H')
        flushB = cards('2C,4C,6C,8C,10C,8H,9H,10H')
        self.assertEqual(Hand(flushA), Hand(flushB))

    def testB_beatsFlushWithLowerHighCard(self):
        '''beats a flush with a lower high card'''
        flushA = cards('2D,4D,6D,8D,10D,8H,9H,10H')
        flushB = cards('2C,4C,6C,8C,9C,8H,9H,10H')
        self.assertGreater(Hand(flushA), Hand(flushB))

    def testB_beatsStraight(self):
        '''beats a striaght'''
        aFlush = cards('3D,5D,8D,6D,10D,8H,9H,10H')
        aStraight = cards('2D,3S,4S,5D,6H,8H,9H,10H')
        self.assertGreater(Hand(aFlush), Hand(aStraight))


class TestComparingAgainstFullHouse(unittest.TestCase):

    def setUp(self):
        print 'Comparing against a full house,', self.shortDescription()

    def testA_beatsFullHouseWithLowerValue(self):
        '''beats a poker with a lower value'''
        fullHouseA = cards('3D,3C,3H,6S,6D,8H,9H,10H')
        fullHouseB = cards('2D,2C,2H,6S,6D,8H,9H,10H')
        self.assertGreater(Hand(fullHouseA), Hand(fullHouseB))

    def testB_beatsFlush(self):
        '''beats a flush'''
        aFullHouse = cards('2D,2C,4H,4S,4D,8H,9H,10H')
        aFlush = cards('3D,5D,8D,6D,10D,8H,9H,10H')
        self.assertGreater(Hand(aFullHouse), Hand(aFlush))

    def testC_cannotBeatPoker(self):
        '''cannot beat a poker'''
        aFullHouse = cards('2D,2C,4H,4S,4D,8H,9H,10H')
        aPoker = cards('3D,3C,3H,3S,6D,8H,9H,10H')
        self.assertLess(Hand(aFullHouse), Hand(aPoker))


class TestComparingAgainstPoker(unittest.TestCase):

    def setUp(self):
        print 'Comparing against a poker,', self.shortDescription()

    def testA_beatsPokerWithLowerValue(self):
        '''beats a poker with a lower value'''
        pokerA = cards('3D,3C,3H,3S,6D,8H,9H,10H')
        pokerB = cards('2D,2C,2H,2S,6D,8H,9H,10H')
        self.assertGreater(Hand(pokerA), Hand(pokerB))

    def testB_onlyEqualWhenAllValuesMatch(self):
        '''equal when all values including high card match'''
        pokerA = cards('3D,3C,3H,3S,6D,8H,9H,10H')
        pokerB = cards('3D,3C,3H,3S,6D,7H,6H,10H')
        self.assertEqual(Hand(pokerA), Hand(pokerB))

    def testC_beatsFullHouse(self):
        '''beats a full house'''
        aPoker = cards('3D,3C,3H,3S,6D,8H,9H,10H')
        aFullHouse = cards('2D,2C,4H,4S,4D,8H,9H,10H')
        self.assertGreater(Hand(aPoker), Hand(aFullHouse))

    def testE_beatsPokerOfSameValueWithHighCard(self):
        '''beats a poker with the same value on high card'''
        pokerA = cards('3D,3C,3H,3S,6D,8H,9H,11H')
        pokerB = cards('3D,3C,3H,3S,6D,8H,9H,10H')
        self.assertGreater(Hand(pokerA), Hand(pokerB))


class TestComparingAgainstStraightFlush(unittest.TestCase):

    def setUp(self):
        print 'Comparing against a straight flush,', self.shortDescription()

    def testA_twoStraightFlushesAreEqual(self):
        '''two straight flushes are equal when they have the same value'''
        straightFlushA = cards('2C,3C,4C,5C,6C,8H,9H,10H')
        straightFlushB = cards('2D,3D,4D,5D,6D,8H,9H,10H')
        self.assertEqual(Hand(straightFlushA), Hand(straightFlushB))

    def testB_beatsStraightFlushWithLowerValue(self):
        '''beats a straight flush with a lower value'''
        straightFlushA = cards('3C,4C,5C,6C,7C,8H,9H,10H')
        straightFlushB = cards('2D,3D,4D,5D,6D,8H,9H,10H')
        self.assertGreater(Hand(straightFlushA), Hand(straightFlushB))

    def testA_beatsPoker(self):
        '''beats a poker'''
        aStraightFlush = cards('3C,4C,5C,6C,7C,8H,9H,10H')
        aPoker = cards('2D,2C,2H,2S,6D,8H,9H,10H')
        self.assertGreater(Hand(aStraightFlush), Hand(aPoker))


class TestRecognizingHandRank(unittest.TestCase):

    def setUp(self):
        print 'Recognizing hands,', self.shortDescription()

    def testA_highestCard(self):
        '''the highest card'''
        hand = cards('3C,2D,6H,7D,9H,10C,11C,13H')
        self.assertEqual(highestCard(hand), cards('13H,11C,10C,9H,7D'))

    def testB_Pair(self):
        '''a pair'''
        hand = cards('3C,3D,6H,7D,9H,10C,11C,13H')
        self.assertEqual(pairHand(hand), cards('3C,3D,13H,11C,10C'))

    def testC_Trips(self):
        '''trips'''
        hand = cards('3C,3C,3D,7D,9H,10C,11C,13H')
        self.assertEqual(tripHand(hand), cards('3C,3C,3D,13H,11C'))

    def testD_Poker(self):
        '''four of a kind, aka poker'''
        hand = cards('3S,3H,3C,3D,9H,10C,11C,13H')
        self.assertEqual(pokerHand(hand), cards('3S,3H,3C,3D,13H'))

    def testE_Flush(self):
        '''a flush'''
        hand = cards('2C,4C,6C,8C,10C,11D,12D,5H')
        self.assertEqual(flush(hand), cards('10C,8C,6C,4C,2C'))

    def testF_TakeHighestFlush(self):
        '''make sure to take the highest flush'''
        hand = cards('1C,2C,4C,5C,7C,9C')
        self.assertEqual(flush(hand), cards('9C,7C,5C,4C,2C'))

    def testG_Straight(self):
        '''a straight'''
        hand = cards('1H,2C,3H,4S,5D')
        self.assertEqual(straight(hand), cards('5D,4S,3H,2C,1H'))

    def testH_UseTheHighestStraight(self):
        '''take the highest straight'''
        hand = cards('1D,2D,3C,4C,5H,6H')
        self.assertEqual(straight(hand), cards('6H,5H,4C,3C,2D'))

    def testI_NoGapsAllowed(self):
        '''no gaps in a straight'''
        hand = cards('1D,2D,3C,4C,5H,7H')
        self.assertEqual(straight(hand), cards('5H,4C,3C,2D,1D'))

    def testJ_NoDuplicatesInStraight(self):
        '''no duplicate faces in a straight'''
        hand = cards('1C,2C,3C,4C,5H,7D,7H')
        self.assertEqual(straight(hand), cards('5H,4C,3C,2C,1C'))

    def testK_StraightFlush(self):
        '''a straight flush'''
        hand = cards('1H,2H,3H,4H,5H')
        self.assertEqual(straightFlush(hand), cards('5H,4H,3H,2H,1H'))

    def testK_house(self):
        '''a house'''
        hand = cards('1H,1C,1D,4H,4C')
        self.assertEqual(house(hand), hand)

    def testL_twoPair(self):
        '''two pair'''
        hand = cards('1H,1C,2D,2H,5H')
        self.assertEqual(twoPairHand(hand), hand)


def cards(items):
    return map(lambda x: Card(int(x[0:-1]), x[-1]), items.split(','))

if __name__ == "__main__":
    unittest.main()
