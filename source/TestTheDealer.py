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


class testBettingBetweenTheDealerAndPlayers(unittest.TestCase):

    def setUp(self):
        print 'Betting between dealers and players,', self.shortDescription()

    def testA_moveLeftToRightAtTheTable(self):
        '''should move left to right at the table'''
        p1 = createPlayer('p1', StubMessenger().skipBlind())
        p2 = createPlayer('p2', StubMessenger().skipBlind())
        p3 = createPlayer('p3', StubMessenger())

        p1.yourGo = MagicMock()
        p2.yourGo = MagicMock()
        p3.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3])

        p1.yourGo.assert_called_with([(p1, 5)])
        p2.yourGo.assert_called_with([(p1, 5), (p2, 10)])
        p3.yourGo.assert_called_with([(p1, 5), (p2, 10)])

    def testB_backToFirstPlayerAfterTheLast(self):
        '''should move back to the first player after the last'''
        p1 = createPlayer('p1', StubMessenger().skipBlind())
        p2 = createPlayer('p2', StubMessenger().skipBlind())
        p3 = createPlayer('p3', StubMessenger().bet(10))
        p1.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3])

        p1.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 10)])

    def testC_playerFolds(self):
        '''a player folding'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(0))
        p2 = createPlayer('p2', StubMessenger().skipBlind())

        p2.handResult = MagicMock()
        p1.outOfGame = MagicMock()

        dealer = Dealer(Deck(), p2Wins)
        dealer.deal([p1, p2])

        p1.outOfGame.assert_called_once_with('You folded')
        p2.handResult.assert_called_once_with('p2 wins')
        self.assertTrue(dealer.playing)

    def testD_playerBetsLessThanMinimum(self):
        '''a player betting less than minimum'''
        p1 = createPlayer('p1', StubMessenger().skipBlind())
        p2 = createPlayer('p2', StubMessenger().skipBlind())
        p3 = createPlayer('p3', StubMessenger().bet(9))
        p4 = createPlayer('p4', StubMessenger())
        p3.outOfGame = MagicMock()
        p4.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3, p4])

        p3.outOfGame.assert_called_once_with('You bet 9, minimum bet was 10')
        p4.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 0)])

    def testE_firstPlayerBetsLessThanMinimum(self):
        '''the first player gets kicked out for betting less than minimum'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(4))
        p2 = createPlayer('p2', StubMessenger().skipBlind())
        p3 = createPlayer('p3', StubMessenger().bet(10))
        p1.outOfGame = MagicMock()
        p2.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3])

        p1.outOfGame.assert_called_once_with('You bet 4, minimum bet was 5')
        p2.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 10), (p1, 0)])

    def testF_playerBetsTheMax(self):
        '''a player betting the max'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(995))
        p2 = createPlayer('p2', StubMessenger().skipBlind())
        p2.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p2.yourGo.assert_called_with([(p1, 5), (p2, 10), (p1, 995)])

    def testG_playerBetsMoreThanTheyHave(self):
        '''a player betting more than they have'''
        p1 = createPlayer('p1', StubMessenger().skipBlind())
        p2 = createPlayer('p2', StubMessenger().skipBlind())
        p3 = createPlayer('p3', StubMessenger().bet(1001))
        p4 = createPlayer('p4', StubMessenger())
        p3.outOfGame = MagicMock()
        p4.yourGo = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2, p3, p4])

        p3.outOfGame.assert_called_once_with('You bet 1001, you have only 1000 cash avaiable')
        p4.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 0)])

    def testH_playerBetsMoreThanTheyHaveInTwoParts(self):
        '''player betting more than they have in two parts'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(10).bet(986))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(10))
        p1.outOfGame = MagicMock()
        p2.handResult = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p1.outOfGame.assert_called_once_with('You bet 986, you have only 985 cash avaiable')
        p2.handResult.assert_called_once_with('p2 wins')

    def testI_theWinnerGetsThePot(self):
        '''player that wins the hand receives the pot'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(0))
        p2 = createPlayer('p2', StubMessenger().skipBlind())

        p2.youWin = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        p2.youWin.assert_called_once_with(15)


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
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(0))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(Deck(), p2Wins).deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 2)
        self.assertEqual(p2.cards.call_count, 2)

    def testG_shouldNotDealAnotherHandAfterTheGameIsWon(self):
        '''should not deal another hand after the game is won'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(995))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(990))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        dealer = Dealer(Deck(), p2Wins)
        dealer.deal([p1, p2])

        self.assertEqual(p1.cards.call_count, 5)
        self.assertEqual(p2.cards.call_count, 5)
        self.assertFalse(dealer.playing)

    def testJ_movingButtonToNextPlayerAfterFirstHand(self):
        '''moving the button to the next player after a hand'''
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(0))
        p2 = createPlayer('p2', StubMessenger().skipBlind())

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
