from EventHandling import Event
from theHouse import PlayerProxy
import unittest
from theHouse import HandlesBettingBetweenThePlayers
from theHouse import Pot
from collections import deque
from texasHoldEm import Table


def shouldMatch(test, a, b):
    a = map(lambda x: (x[0].name, x[1]), a)
    b = map(lambda x: (x[0].name, x[1]), b)

    test.assertEqual(a, b)


class testSplittiingUpThePotBetweenTheWinners(unittest.TestCase):

    def setUp(self):
        print 'Splitting up the pot between the winners,', self.shortDescription()

    def testA_playerWinsBackTheirChips(self):
        '''a player wins back their chips if no one else is in'''

        p1 = createPlayer('p1', StubMessenger())
        dealer = HandlesBettingBetweenThePlayers(Table([]))
        dealer.ranking = lambda x: [[p1]]

        p1.cash = 5
        dealer.add(p1, 5)

        dealer.distributeWinnings()

        self.assertEqual(p1.cash, 5)

    def testB_withoutSidePotsTheTopRankedPlayerWinsAll(self):
        '''without side pots the top ranked player wins all'''

        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        dealer = HandlesBettingBetweenThePlayers(Table([]))
        dealer.ranking = lambda x: [[p1], [p2]]

        p1.cash = 5
        p2.cash = 5

        dealer.add(p1, 5)
        dealer.add(p2, 5)

        dealer.distributeWinnings()

        self.assertEqual(p1.cash, 10)

    def testC_theTopRankedPlayerCannotWinMoreThanAllowed(self):
        '''if a player is only in a side pot, that is all they can win'''

        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        dealer = HandlesBettingBetweenThePlayers(Table([]))
        dealer.ranking = lambda x: [[p1], [p2]]

        p1.cash = 5
        p2.cash = 10

        dealer.add(p1, 5)
        dealer.add(p2, 10)

        dealer.distributeWinnings()

        self.assertEqual(p1.cash, 10)
        self.assertEqual(p2.cash, 5)

    def testD_splittingThePot(self):
        '''players will split the pot if they are ranked the same'''

        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())
        p3 = createPlayer('p3', StubMessenger())

        dealer = HandlesBettingBetweenThePlayers(Table([]))
        dealer.ranking = lambda x: [[p1, p2], [p3]]

        p1.cash = 10
        p2.cash = 10
        p3.cash = 10

        dealer.add(p1, 10)
        dealer.add(p2, 10)
        dealer.add(p3, 10)

        dealer.distributeWinnings()

        self.assertEqual(p1.cash, 15)
        self.assertEqual(p2.cash, 15)


class testTheTotalOfThePot(unittest.TestCase):

    def setUp(self):
        print 'The total of the pot,', self.shortDescription()

    def testA_ZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        p = Pot()

        self.assertEqual(0, p.total())

    def testB_IncrementsWhenChipsAreAdded(self):
        '''increments when chips are added'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())

        p.add(p1, 5)

        self.assertEqual(5, p.total())

    def testC_IncrementsWhenMoreChipsAreAdded(self):
        '''increments when more chips are added'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())

        p.add(p1, 5)
        p.add(p1, 10)

        self.assertEqual(15, p.total())


class testTheMinimumBetForPlayer(unittest.TestCase):

    def setUp(self):
        print 'The minimum bet for a player,', self.shortDescription()

    def testA_ZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        dealer = HandlesBettingBetweenThePlayers(Table([]))
        p1 = createPlayer('p1', StubMessenger())

        self.assertEqual(0, dealer.getMinimumBet(p1))

    def testB_SecondPlayerMustBetAtLeastTheFirstBet(self):
        '''second player should pay at least the first bet'''
        dealer = HandlesBettingBetweenThePlayers(Table([]))
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        dealer.add(p1, 5)

        self.assertEqual(5, dealer.getMinimumBet(p2))

    def testC_ZeroBecauseAllAreEven(self):
        '''zero when all players are even'''
        dealer = HandlesBettingBetweenThePlayers(Table([]))
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        dealer.add(p1, 5)
        dealer.add(p2, 5)

        self.assertEqual(0, dealer.getMinimumBet(p1))
        self.assertEqual(0, dealer.getMinimumBet(p2))

    def testD_ShouldPayTheDifferenceWhenRaised(self):
        '''player should pay the difference when raised'''

        dealer = HandlesBettingBetweenThePlayers(Table([]))
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        dealer.add(p1, 5)
        dealer.add(p2, 10)

        self.assertEqual(5, dealer.getMinimumBet(p1))


def createPlayer(name, messenger):
    player = PlayerProxy(name, messenger)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


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
