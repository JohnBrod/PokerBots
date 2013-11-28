import unittest
from theHouse import PlayerProxy
from texasHoldEm import DealsCardsToThePlayers
from EventHandling import Event
from mock import MagicMock
from collections import deque
from mock import create_autospec
from Xmpp import XmppMessenger


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

        audience = create_autospec(XmppMessenger)
        DealsCardsToThePlayers(PredictableDeck(), [p1, p2], audience).next()

        p1.cards.assert_called_with([1, 2])
        p2.cards.assert_called_with([3, 4])

    def testB_shouldDealTheCommunityCardsPublicly(self):
        '''should deal the community cards to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        audience = create_autospec(XmppMessenger)
        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], audience)
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([5, 6, 7])
        p2.cards.assert_called_with([5, 6, 7])
        audience.broadcast.assert_called_with('5,6,7')

    def testC_shouldDealTheFlopCardPublicly(self):
        '''should deal the flop to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        audience = create_autospec(XmppMessenger)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], audience)
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([8])
        p2.cards.assert_called_with([8])
        audience.broadcast.assert_called_with('8')

    def testD_shouldDealTheRiverCardPublicly(self):
        '''should deal the river to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        audience = create_autospec(XmppMessenger)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], audience)
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([9])
        p2.cards.assert_called_with([9])
        audience.broadcast.assert_called_with('9')

    def testE_shouldDealTheTurnCardPublicly(self):
        '''should deal the turn to each player'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        audience = create_autospec(XmppMessenger)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], audience)
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()
        dealer.next()

        p1.cards.assert_called_with([10])
        p2.cards.assert_called_with([10])
        audience.broadcast.assert_called_with('10')

    def testF_notPossibleToDealNextWhenNotStagesAreLeft(self):
        '''not possible to deal next when there are not stages left'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        audience = create_autospec(XmppMessenger)

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = DealsCardsToThePlayers(PredictableDeck(), [p1, p2], audience)
        dealer.dealStages = deque([])

        self.assertRaises(Exception, dealer.next)


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
        self.evt_playerResponse = Event()
        self.replies = deque()
        self.sentMessages = []
        self.broadcastMessages = []

    def skipBlind(self):
        self.replies.append('skip')
        return self

    def bet(self, player, amount):
        self.replies.append((player, amount))
        return self

    def sendMessage(self, jid, msg):

        self.sentMessages.append((jid, msg))
        self.lastMessage = (jid, msg)

        if msg != 'GO' or len(self.replies) == 0:
            return

        response = self.replies.popleft()

        if response == 'skip':
            return

        self.evt_playerResponse.fire(self, response)

    def broadcast(self, msg):
        self.broadcastMessages.append(msg)


if __name__ == "__main__":
    unittest.main()
