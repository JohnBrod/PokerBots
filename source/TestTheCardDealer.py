import unittest
from theHouse import PlayerProxy
from texasHoldEm import Deck
from texasHoldEm import DealsCards
from Hands import Hand
from mock import MagicMock
from FakeMessaging import StubMessenger
from FakeMessaging import PredictableDeck


def createPlayer(name, chips=0, cards=[]):
    player = PlayerProxy(name, chips)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    player.cards(cards)

    return player


class testDealingCardsToPlayers(unittest.TestCase):

    def setUp(self):
        print 'Dealing cards to players,', self.shortDescription()

    def testA_dealEachPlayerPrivateCardsFirst(self):
        '''should deal each player private cards first'''
        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        DealsCards(PredictableDeck(), [p1, p2], messenger).go()

        p1.cards.assert_called_with([1, 2])
        p2.cards.assert_called_with([3, 4])
        self.assertTrue(('p1', 'CARD') in messenger.sentMessages)
        self.assertTrue(('p2', 'CARD') in messenger.sentMessages)

    def testB_dealsTheFlopCards(self):
        '''deals the flop cards'''
        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCards(PredictableDeck(), [p1, p2], messenger)
        dealer.go()
        dealer.go()

        p1.cards.assert_called_with([5, 6, 7])
        p2.cards.assert_called_with([5, 6, 7])

        self.assertEqual(['CARD'], messenger.broadcastMessages)

    def testC_dealsTheRiverCard(self):
        '''deals the river card'''
        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCards(PredictableDeck(), [p1, p2], messenger)
        dealer.go()
        dealer.go()
        dealer.go()

        p1.cards.assert_called_with([8])
        p2.cards.assert_called_with([8])

        self.assertEqual(['CARD', 'CARD'], messenger.broadcastMessages)

    def testD_dealsTheTurnCard(self):
        '''deals the turn card'''
        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        messenger = StubMessenger()
        dealer = DealsCards(PredictableDeck(), [p1, p2], messenger)
        dealer.go()
        dealer.go()
        dealer.go()
        dealer.go()

        p1.cards.assert_called_with([9])
        p2.cards.assert_called_with([9])

        self.assertEqual(['CARD', 'CARD', 'CARD'], messenger.broadcastMessages)

    def testF_notPossibleToDealNextWhenNoStagesAreLeft(self):
        '''not possible to deal next when there no stages are left'''
        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCards(PredictableDeck(), [p1, p2], StubMessenger())

        dealer.go()
        dealer.go()
        dealer.go()
        dealer.go()

        self.assertRaises(Exception, dealer.go)

    def testG_shouldTakeCardsFromPlayersBeforeDealing(self):
        '''should take any cards the player may have before dealing'''
        p1 = createPlayer('p1', 100, ['cards from last hand'])

        DealsCards(PredictableDeck(), [p1], StubMessenger())

        self.assertEqual(p1.hand(), Hand([]))


class testDealingTheRemainingCards(unittest.TestCase):

    def setUp(self):
        print 'Deals the remaining cards,', self.shortDescription()

    def testH_allPlayersAreOutOfChips(self):
        '''when all players are out of chips'''
        p1 = createPlayer('p1', 0)
        p2 = createPlayer('p2', 0)
        p3 = createPlayer('p3', 0)

        msngr = StubMessenger()
        dealer = DealsCards(Deck(), [p1, p2, p3], msngr)

        dealer.go()

        allDealt = ['CARD', 'CARD', 'CARD']
        self.assertEqual(allDealt, msngr.broadcastMessages)

    def testI_allBarOnePlayersAreOutOfChips(self):
        '''when all players bar one are out of chips'''
        p1 = createPlayer('p1', 10)
        p2 = createPlayer('p2', 0)
        p3 = createPlayer('p3', 0)

        msngr = StubMessenger()
        dealer = DealsCards(Deck(), [p1, p2, p3], msngr)

        dealer.go()

        allDealt = ['CARD', 'CARD', 'CARD']
        self.assertEqual(allDealt, msngr.broadcastMessages)

if __name__ == "__main__":
    unittest.main()
