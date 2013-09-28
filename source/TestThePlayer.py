import unittest
from theHouse import PlayerProxy
from collections import deque
from EventHandling import Event


def createPlayer(cash, amountToBet = 0):
    player = PlayerProxy('name', StubMessenger().bet(amountToBet))
    player.cash = cash
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


class testThePlayersCash(unittest.TestCase):

    def setUp(self):
        print 'The players cash,', self.shortDescription()

    def testA_shouldBetReduceWhenBetting(self):
        '''is reduced when the player bets'''
        p = createPlayer(cash=100, amountToBet=60)

        p.yourGo([])

        self.assertEqual(p.cash, 40)

    def testA_shouldBeIncreasedWhenTheyWin(self):
        '''is increased when the player wins'''
        p = createPlayer(cash=100)

        p.youWin(50)

        self.assertEqual(p.cash, 150)


class StubMessenger(object):

    def __init__(self):
        self.evt_messageReceived = Event()
        self.replies = deque()

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
