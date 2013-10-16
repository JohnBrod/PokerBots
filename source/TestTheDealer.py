import unittest
from theHouse import PlayerProxy
from theHouse import Deck
from texasHoldEm import Dealer
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


def p1Wins(publicCards, players):
    return filter(lambda x: x.name == 'p1', players)[0]


class testTellingThePlayersToTakeTheirGo(unittest.TestCase):

    def setUp(self):
        print 'Telling the players to take their go,', self.shortDescription()

    def testA_tellTheFirstPlayerToTakeTheirGo(self):
        '''tell the first player to take their go'''
        p1 = createPlayer('p1', StubMessenger())
        p1.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1])

        p1.yourGo.assert_called_with([])

    def testB_tellTheNextPlayerThePreviousMoves(self):
        '''tell the next player the previous moves'''
        p1 = createPlayer('p1', StubMessenger().bet(1))
        p2 = createPlayer('p2', StubMessenger())

        p2.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p2.yourGo.assert_called_with([(p1, 1)])


class testIllegalBetting(unittest.TestCase):

    def setUp(self):
        print 'Illegal betting,', self.shortDescription()

    def testD_playerBetsLessThanMinimum(self):
        '''a player betting less than minimum'''
        p1 = createPlayer('p1', StubMessenger().bet(2))
        p2 = createPlayer('p2', StubMessenger().bet(1))

        p1.handResult = MagicMock()
        p2.outOfGame = MagicMock()

        dealer = Dealer(Deck(), p1Wins)
        dealer.deal([p1, p2])

        p2.outOfGame.assert_called_once_with('You bet 1, minimum bet was 2')
        p1.handResult.assert_called_once_with('p1 wins')
        self.assertTrue(dealer.playing)

    def testE_firstPlayerBetsLessThanMinimum(self):
        '''the first player gets kicked out for betting less than minimum'''
        p1 = createPlayer('p1', StubMessenger().bet(1).bet(4))
        p2 = createPlayer('p2', StubMessenger().bet(6))
        p3 = createPlayer('p3', StubMessenger().bet(6))
        p1.outOfGame = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3])

        p1.outOfGame.assert_called_once_with('You bet 4, minimum bet was 5')

    def testG_playerBetsMoreThanTheyHave(self):
        '''a player betting more than they have'''
        p1 = createPlayer('p1', StubMessenger().bet(1001))
        p2 = createPlayer('p2', StubMessenger())
        p3 = createPlayer('p3', StubMessenger())
        p1.outOfGame = MagicMock()
        p2.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3])

        p1.outOfGame.assert_called_once_with('You bet 1001, you have only 1000 cash avaiable')
        p2.yourGo.assert_called_with([(p1, 0)])

    def testH_playerBetsMoreThanTheyHaveInTwoParts(self):
        '''player betting more than they have in two parts'''
        p1 = createPlayer('p1', StubMessenger().bet(10).bet(991))
        p2 = createPlayer('p2', StubMessenger().bet(10))
        p1.outOfGame = MagicMock()
        p2.handResult = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p1.outOfGame.assert_called_once_with('You bet 991, you have only 990 cash avaiable')
        p2.handResult.assert_called_once_with('p2 wins')

    def testI_playerCanBetLessThanMinimumIfTheyGoAllIn(self):
        '''a player can bet less than minimum if they go all in'''
        p1 = createPlayer('p1', StubMessenger().bet(10))
        p2 = createPlayer('p2', StubMessenger().bet(5))
        p2.outOfGame = MagicMock()

        p1.cash = 10
        p2.cash = 5

        Dealer(Deck(), p1Wins).deal([p1, p2])

        self.assertFalse(p2.outOfGame.called)


class testBettingBetweenTheDealerAndPlayers(unittest.TestCase):

    def setUp(self):
        print 'Betting between dealers and players,', self.shortDescription()

    def testC_playerFoldsByBettingZero(self):
        '''a player folds by betting 0'''
        p1 = createPlayer('p1', StubMessenger().bet(1))
        p2 = createPlayer('p2', StubMessenger().bet(0))

        p1.handResult = MagicMock()
        p2.outOfGame = MagicMock()

        dealer = Dealer(Deck(), p1Wins)
        dealer.deal([p1, p2])

        p2.outOfGame.assert_called_once_with('You folded')
        p1.handResult.assert_called_once_with('p1 wins')
        self.assertTrue(dealer.playing)

    def testF_playerBetsTheMax(self):
        '''a player betting the max'''
        p1 = createPlayer('p1', StubMessenger().bet(1000))
        p2 = createPlayer('p2', StubMessenger())
        p2.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p2.yourGo.assert_called_with([(p1, 1000)])

    def testI_theWinnerGetsThePot(self):
        '''player that wins the hand receives the pot'''
        p1 = createPlayer('p1', StubMessenger().bet(10).bet(0))
        p2 = createPlayer('p2', StubMessenger().bet(20))

        p2.youWin = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p2.youWin.assert_called_once_with(30)


class testDealingTheCards(unittest.TestCase):

    def setUp(self):
        print 'Dealing the cards,', self.shortDescription()

    def testA_shouldDealCardsToPlayersAtTheStart(self):
        '''should deal cards to the players at the start'''
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 1)
        self.assertEqual(p2.cards.call_count, 1)

    def testB_shouldDealCardsAfterRoundOfBetting(self):
        '''should deal after round of betting'''
        p1 = createPlayer('p1', StubMessenger().bet(5))
        p2 = createPlayer('p2', StubMessenger().bet(0))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(Deck(), p1Wins).deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 2)
        self.assertEqual(p2.cards.call_count, 2)

    def testG_shouldNotDealAnotherHandAfterTheGameIsWon(self):
        '''should not deal another hand after the game is won'''
        p1 = createPlayer('p1', StubMessenger().bet(1000))
        p2 = createPlayer('p2', StubMessenger().bet(1000))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = Dealer(Deck(), p1Wins)
        dealer.deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 5)
        self.assertEqual(p2.cards.call_count, 5)
        self.assertFalse(dealer.playing)

    def testJ_movingButtonToNextPlayerAfterFirstHand(self):
        '''moving the button to the next player after a hand'''
        p1 = createPlayer('p1', StubMessenger().bet(10).bet(0))
        p2 = createPlayer('p2', StubMessenger().bet(20))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck(), p2Wins).deal([p1, p2])

        p2.cards.assert_called_with((1, 2))
        p1.cards.assert_called_with((3, 4))


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
        self.replies = deque()

    def skipBlind(self):
        self.replies.append('skip')
        return self

    def bet(self, amount):
        self.replies.append(amount)
        return self

    def sendMessage(self, jid, msg):

        self.lastMessage = msg

        if len(self.replies) == 0:
            return

        response = self.replies.popleft()

        if response == 'skip':
            return

        self.evt_messageReceived.fire(self, response)


if __name__ == "__main__":
    unittest.main()
