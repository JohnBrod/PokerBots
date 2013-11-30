import unittest
from theHouse import PlayerProxy
from texasHoldEm import Dealer
from EventHandling import Event
from mock import MagicMock
from collections import deque


def createPlayer(name, cash=1000):
    player = PlayerProxy(name, cash)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


class testTellingThePlayersToTakeTheirGo(unittest.TestCase):

    def setUp(self):
        print 'Telling the players to take their go,', self.shortDescription()

    def testA_tellTheFirstPlayerToTakeTheirGo(self):
        '''tell the first player to take their go'''
        p1 = createPlayer('p1')

        msngr = StubMessenger()
        Dealer(msngr).deal([p1])

        self.assertEqual(msngr.lastMessage, ('p1', 'GO'))


class testIllegalBetting(unittest.TestCase):

    def setUp(self):
        print 'Illegal betting,', self.shortDescription()

    def testD_playerBetsLessThanMinimum(self):
        '''a player betting less than minimum'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        msngr = StubMessenger().bet(p1, 2).bet(p2, 1)

        dealer = Dealer(msngr)
        dealer.deal([p1, p2])

        self.assertTrue(('p2', 'You are out, you bet 1, minimum bet was 2') in msngr.sentMessages)
        self.assertTrue(dealer.playing)

    def testE_firstPlayerBetsLessThanMinimum(self):
        '''the first player gets kicked out for betting less than minimum'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p3 = createPlayer('p3')

        msngr = StubMessenger().bet(p1, 1).bet(p2, 6).bet(p3, 6).bet(p1, 4)

        Dealer(msngr).deal([p1, p2, p3])

        self.assertTrue(('p1', 'You are out, you bet 4, minimum bet was 5') in msngr.sentMessages)

    def testG_playerBetsMoreThanTheyHave(self):
        '''a player betting more than they have'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p3 = createPlayer('p3')
        p2.yourGo = MagicMock()

        msngr = StubMessenger().bet(p1, 1001)

        Dealer(msngr).deal([p1, p2, p3])

        self.assertTrue(('p1', 'You are out, you bet 1001, you have only 1000 cash avaiable') in msngr.sentMessages)

    def testH_playerBetsMoreThanTheyHaveInTwoParts(self):
        '''player betting more than they have in two parts'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p2.handResult = MagicMock()

        msngr = StubMessenger().bet(p1, 10).bet(p2, 10).bet(p1, 991)

        Dealer(msngr).deal([p1, p2])

        self.assertTrue(('p1', 'You are out, you bet 991, you have only 990 cash avaiable') in msngr.sentMessages)


class testBettingBetweenTheDealerAndPlayers(unittest.TestCase):

    def setUp(self):
        print 'Betting between dealers and players,', self.shortDescription()

    def testC_playerFoldsByBettingZero(self):
        '''a player folds by betting 0'''

        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.handResult = MagicMock()

        msngr = StubMessenger().bet(p1, 1).bet(p2, 0)

        dealer = Dealer(msngr)
        dealer.deal([p1, p2])

        self.assertTrue(('p2', 'You are out, you folded') in msngr.sentMessages)

        self.assertTrue(dealer.playing)

    def testF_playerBetsTheMax(self):
        '''a player betting the max'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        msngr = StubMessenger().bet(p1, 1000)

        Dealer(msngr).deal([p1, p2])

        self.assertEqual(msngr.lastMessage, ('p2', 'GO'))

    def testI_playerCanBetLessThanMinimumIfTheyGoAllIn(self):
        '''a player can bet less than minimum if they go all in'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cash = 10
        p2.cash = 5

        msngr = StubMessenger().bet(p1, 10).bet(p2, 5)

        Dealer(msngr).deal([p1, p2])

        for msg in msngr.sentMessages:
            self.assertFalse(msg[0] == 'p2' and msg[1].startswith('You are out'))


class testDealingTheCards(unittest.TestCase):

    def setUp(self):
        print 'Dealing the cards,', self.shortDescription()

    def testA_shouldDealCardsToPlayersAtTheStart(self):
        '''should deal cards to the players at the start'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(StubMessenger()).deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 1)
        self.assertEqual(p2.cards.call_count, 1)

    def testB_shouldDealCardsAfterRoundOfBetting(self):
        '''should deal after round of betting'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        msngr = StubMessenger().bet(p1, 5).bet(p2, 0)

        Dealer(msngr).deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 2)
        self.assertEqual(p2.cards.call_count, 2)

    def testG_shouldNotDealAnotherHandAfterTheGameIsWon(self):
        '''should not deal another hand after the game is won'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        msngr = StubMessenger().bet(p1, 1000).bet(p2, 1000)

        dealer = Dealer(msngr)
        dealer.deal([p1, p2])

        self.assertFalse('DEALING p2 p1' in msngr.broadcastMessages)

    def testJ_movingButtonToNextPlayerAfterFirstHand(self):
        '''moving the button to the next player after a hand'''
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        msngr = StubMessenger().bet(p1, 10).bet(p2, 20).bet(p1, 0)

        Dealer(msngr).deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 2)
        self.assertEqual(p2.cards.call_count, 2)


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
