import unittest
from theHouse import PlayerProxy
from texasHoldEm import CardDealer
from texasHoldEm import Table
from EventHandling import Event
from mock import MagicMock
from collections import deque


def createPlayer(name, messenger):
    player = PlayerProxy(name, messenger)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


def p2Wins(publicCards, players):
    return filter(lambda x: x.name == 'p2', players)[0]


class testDealingCardsToPlayers(unittest.TestCase):

    def setUp(self):
        print 'Dealing cards to players,', self.shortDescription()

    def testA_shouldDealEachPlayerPrivateCardsFirst(self):
        '''should deal each player private cards first'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        CardDealer(PredictableDeck(), Table([p1, p2])).dealNext()

        p1.cards.assert_called_with((1, 2))
        p2.cards.assert_called_with((3, 4))

    def testB_shouldDealTheCommunityCardsToEachPlayer(self):
        '''should deal the community cards to each player'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = CardDealer(PredictableDeck(), Table([p1, p2]))
        dealer.dealNext()
        dealer.dealNext()

        p1.cards.assert_called_with((5, 6, 7))
        p2.cards.assert_called_with((5, 6, 7))

    def testC_shouldDealTheFlopCardToEachPlayer(self):
        '''should deal the flop to each player'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = CardDealer(PredictableDeck(), Table([p1, p2]))
        dealer.dealNext()
        dealer.dealNext()
        dealer.dealNext()

        p1.cards.assert_called_with((8))
        p2.cards.assert_called_with((8))

    def testD_shouldDealTheRiverCardToEachPlayer(self):
        '''should deal the river to each player'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = CardDealer(PredictableDeck(), Table([p1, p2]))
        dealer.dealNext()
        dealer.dealNext()
        dealer.dealNext()
        dealer.dealNext()

        p1.cards.assert_called_with((9))
        p2.cards.assert_called_with((9))

    def testE_shouldDealTheTurnCardToEachPlayer(self):
        '''should deal the turn to each player'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = CardDealer(PredictableDeck(), Table([p1, p2]))
        dealer.dealNext()
        dealer.dealNext()
        dealer.dealNext()
        dealer.dealNext()
        dealer.dealNext()

        p1.cards.assert_called_with((10))
        p2.cards.assert_called_with((10))

    def testF_notPossibleToDealNextWhenNotStagesAreLeft(self):
        '''not possible to deal next when there are not stages left'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = CardDealer(PredictableDeck(), Table([p1, p2]))
        dealer.dealStages = deque([])

        self.assertRaises(Exception, dealer.dealNext)


class PredictableDeck():

    def __init__(self):
        self.card = 0

    def take(self):
        self.card += 1
        return self.card

    def shuffle(self):
        self.card = 0


class StubMessenger(object):
    def __init__(self):
        self.evt_messageReceived = Event()

    def sendMessage(self, jid, msg):
        pass


if __name__ == "__main__":
    unittest.main()