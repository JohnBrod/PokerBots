import unittest
from theHouse import PlayerProxy
from texasHoldEm import Card
from texasHoldEm import DealsCardsToThePlayers
from texasHoldEm import XmppMessageInterpreter
from Hands import Hand
from mock import MagicMock
from collections import deque
from mock import create_autospec


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

        interpreter = create_autospec(XmppMessageInterpreter)
        DealsCardsToThePlayers(PredictableDeck(), [p1, p2], interpreter).next()

        p1.cards.assert_called_with([1, 2])
        p2.cards.assert_called_with([3, 4])

    def testB_shouldDealTheCommunityCardsPublicly(self):
        '''should deal the community cards to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        interpreter = create_autospec(XmppMessageInterpreter)
        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], interpreter)
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([5, 6, 7])
        p2.cards.assert_called_with([5, 6, 7])
        interpreter.broadcast.assert_called_with('5,6,7')

    def testC_shouldDealTheFlopCardPublicly(self):
        '''should deal the flop to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        interpreter = create_autospec(XmppMessageInterpreter)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], interpreter)
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([8])
        p2.cards.assert_called_with([8])
        interpreter.broadcast.assert_called_with('8')

    def testD_shouldDealTheRiverCardPublicly(self):
        '''should deal the river to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        interpreter = create_autospec(XmppMessageInterpreter)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], interpreter)
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([9])
        p2.cards.assert_called_with([9])
        interpreter.broadcast.assert_called_with('9')

    def testE_shouldDealTheTurnCardPublicly(self):
        '''should deal the turn to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        interpreter = create_autospec(XmppMessageInterpreter)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], interpreter)
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([10])
        p2.cards.assert_called_with([10])
        interpreter.broadcast.assert_called_with('10')

    def testF_notPossibleToDealNextWhenNotStagesAreLeft(self):
        '''not possible to deal next when there are not stages left'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        interpreter = create_autospec(XmppMessageInterpreter)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], interpreter)
        dealer.dealStages = deque([])

        self.assertRaises(Exception, dealer.next)

    def testG_shouldTakeCardsFromPlayersBeforeDealing(self):
        '''should take any cards the player may have before dealing'''
        p1 = createPlayer('p1')

        p1.cards([Card(2, 'H')])

        interpreter = create_autospec(XmppMessageInterpreter)
        DealsCardsToThePlayers(PredictableDeck(), [p1], interpreter)

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
