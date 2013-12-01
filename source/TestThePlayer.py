import unittest
from theHouse import PlayerProxy
from collections import deque
from EventHandling import Event


def createPlayer(chips):
    player = PlayerProxy('name', chips)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


class testThePlayersCash(unittest.TestCase):

    def setUp(self):
        print 'The players chips,', self.shortDescription()

    def testA_shouldBeIncreasedWhenTheyWin(self):
        '''is increased when the player wins'''
        p = createPlayer(chips=100)

        p.deposit(50)

        self.assertEqual(p.chips, 150)


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
