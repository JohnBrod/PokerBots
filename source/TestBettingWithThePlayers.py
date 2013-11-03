from EventHandling import Event
from theHouse import PlayerProxy
import unittest
from theHouse import Pot
from theHouse import Transactions
from collections import deque


def shouldMatch(test, a, b):
    a = map(lambda x: (x[0].name, x[1]), a)
    b = map(lambda x: (x[0].name, x[1]), b)

    test.assertEqual(a, b)


class testTheWinningsOfaPlayer(unittest.TestCase):

    def setUp(self):
        print 'The winnings of a player,', self.shortDescription()

    def testA_playerWinsBackTheirChips(self):
        '''a player wins back their chips if no one else is in'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p1.cash = 5
        p.add(p1, 5)

        p.distributeWinnings([[p1]])

        self.assertEqual(p1.cash, 5)

    def testB_withoutSidePotsTheTopRankedPlayerWinsAll(self):
        '''without side pots the top ranked player wins all'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cash = 5
        p2.cash = 5

        p.add(p1, 5)
        p.add(p2, 5)

        p.distributeWinnings([[p1], [p2]])

        self.assertEqual(p1.cash, 10)

    def testC_theTopRankedPlayerCannotWinMoreThanAllowed(self):
        '''if a player is only in a side pot, that is all they can win'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cash = 5
        p2.cash = 10

        p.add(p1, 5)
        p.add(p2, 10)

        p.distributeWinnings([[p1], [p2]])

        self.assertEqual(p1.cash, 10)
        self.assertEqual(p2.cash, 5)

    def testD_splittingThePot(self):
        '''players will split the pot if they are ranked the same'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())
        p3 = createPlayer('p3', StubMessenger())

        p1.cash = 10
        p2.cash = 10
        p3.cash = 10

        p.add(p1, 10)
        p.add(p2, 10)
        p.add(p3, 10)

        p.distributeWinnings([[p1, p2], [p3]])

        self.assertEqual(p1.cash, 15)
        self.assertEqual(p2.cash, 15)


class testTheTotalOfTheTransactions(unittest.TestCase):

    def setUp(self):
        print 'The total of the transactions,', self.shortDescription()

    def testA_ZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        txns = Transactions()

        self.assertEqual(0, txns.total())

    def testB_IncrementsWhenChipsAreAdded(self):
        '''increments when chips are added'''

        txns = Transactions()
        p1 = createPlayer('p1', StubMessenger())

        txns.add(p1, 5)

        self.assertEqual(5, txns.total())

    def testC_IncrementsWhenMoreChipsAreAdded(self):
        '''increments when more chips are added'''

        txns = Transactions()
        p1 = createPlayer('p1', StubMessenger())

        txns.add(p1, 5)
        txns.add(p1, 10)

        self.assertEqual(15, txns.total())


class testTheMinimumBetOfThePot(unittest.TestCase):

    def setUp(self):
        print 'The minimum bet of the pot,', self.shortDescription()

    def testA_ZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())

        self.assertEqual(0, p.getMinimumBet(p1))

    def testB_SecondPlayerMustBetAtLeastTheFirstBet(self):
        '''second player should pay at least the first bet'''
        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 5)

        self.assertEqual(5, p.getMinimumBet(p2))

    def testC_ZeroBecauseAllAreEven(self):
        '''zero when all players are even'''
        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 5)
        p.add(p2, 5)

        self.assertEqual(0, p.getMinimumBet(p1))
        self.assertEqual(0, p.getMinimumBet(p2))

    def testD_ShouldPayTheDifferenceWhenRaised(self):
        '''player should pay the difference when raised'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 5)
        p.add(p2, 10)

        self.assertEqual(5, p.getMinimumBet(p1))


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
