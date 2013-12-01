from EventHandling import Event
from collections import deque


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
