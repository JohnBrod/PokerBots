from EventHandling import Event
from theHouse import PlayerProxy
import unittest
from texasHoldEm import Pot
from collections import deque


def shouldMatch(test, a, b):
    a = map(lambda x: (x[0].name, x[1]), a)
    b = map(lambda x: (x[0].name, x[1]), b)

    test.assertEqual(a, b)


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

    def testB_IncrementsWhenMoreChipsAreAdded(self):
        '''increments when more chips are added'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())

        p.add(p1, 5)
        p.add(p1, 10)

        self.assertEqual(15, p.total())


class testTheMinimumBetOfThePot(unittest.TestCase):

    def setUp(self):
        print 'The minimum bet of the pot,', self.shortDescription()

    def testZeroWhenThereIsNothingInThePot(self):
        '''zero when there is nothing in the pot'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())

        self.assertEqual(0, p.getMinimumBet(p1))

    def testSecondPlayerMustBetAtLeastTheFirstBet(self):
        '''second player should pay at least the first bet'''
        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 5)

        self.assertEqual(5, p.getMinimumBet(p2))

    def testZeroBecauseAllAreEven(self):
        '''zero when all players are even'''
        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 5)
        p.add(p2, 5)

        self.assertEqual(0, p.getMinimumBet(p1))
        self.assertEqual(0, p.getMinimumBet(p2))

    def testShouldPayTheDifferenceWhenRaised(self):
        '''player should pay the difference when raised'''

        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 5)
        p.add(p2, 10)

        self.assertEqual(5, p.getMinimumBet(p1))

    def testZeroOnceTheRoundIsComplete(self):
        '''will be zero once the round is complete'''
        p = Pot()
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p.add(p1, 10)
        p.add(p2, 10)

        self.assertEqual(0, p.getMinimumBet(p1))


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
