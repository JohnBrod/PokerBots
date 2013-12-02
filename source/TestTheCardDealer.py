import unittest
from theHouse import PlayerProxy
from texasHoldEm import Card
from texasHoldEm import DealsCardsToThePlayers
from Hands import Hand
from mock import MagicMock
from collections import deque
from FakeMessaging import StubMessenger


def createPlayer(name):
    player = PlayerProxy(name, 0)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


class testDealingCardsToPlayers(unittest.TestCase):

    def setUp(self):
        print 'Dealing cards to players,', self.shortDescription()

    def testA_shouldDealEachPlayerPrivateCardsFirst(self):
        '''should deal each player private cards first'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        DealsCardsToThePlayers(PredictableDeck(), [p1, p2], messenger).next()

        p1.cards.assert_called_with([1, 2])
        p2.cards.assert_called_with([3, 4])
        self.assertTrue(('p1', 'CARD 1 2') in messenger.sentMessages)
        self.assertTrue(('p2', 'CARD 3 4') in messenger.sentMessages)

    def testB_shouldDealTheCommunityCardsPublicly(self):
        '''should deal the community cards to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], messenger)
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([5, 6, 7])
        p2.cards.assert_called_with([5, 6, 7])
        self.assertTrue('CARD 5 6 7' in messenger.broadcastMessages)

    def testC_shouldDealTheFlopCardPublicly(self):
        '''should deal the flop to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], messenger)
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([8])
        p2.cards.assert_called_with([8])
        self.assertTrue('CARD 8' in messenger.broadcastMessages)

    def testD_shouldDealTheRiverCardPublicly(self):
        '''should deal the river to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], messenger)
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([9])
        p2.cards.assert_called_with([9])
        self.assertTrue('CARD 9' in messenger.broadcastMessages)

    def testE_shouldDealTheTurnCardPublicly(self):
        '''should deal the turn to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], messenger)
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([10])
        p2.cards.assert_called_with([10])
        self.assertTrue('CARD 10' in messenger.broadcastMessages)

    def testF_notPossibleToDealNextWhenNotStagesAreLeft(self):
        '''not possible to deal next when there are not stages left'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], StubMessenger())
        dealer.dealStages = deque([])

        self.assertRaises(Exception, dealer.next)

    def testG_shouldTakeCardsFromPlayersBeforeDealing(self):
        '''should take any cards the player may have before dealing'''
        p1 = createPlayer('p1')

        p1.cards([Card(2, 'H')])

        DealsCardsToThePlayers(PredictableDeck(), [p1], StubMessenger())

        self.assertEqual(p1.hand(), Hand([]))


class PredictableDeck():

    def __init__(self):
        self.card = 0

    def take(self):
        self.card += 1
        return self.card

    def shuffle(self):
        self.card = 0


if __name__ == "__main__":
    unittest.main()
