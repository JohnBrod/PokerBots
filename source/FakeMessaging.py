from EventHandling import Event
from collections import deque


class StubMessenger(object):
    def __init__(self):
        self.evt_playerResponse = Event()
        self.replies = deque()
        self.sentMessages = []
        self.broadcastMessages = []
        self.goMessages = []
        self.lastMessage = None
        self.cardMessages = []
        self.allMessages = []
        self.dealingMessages = []
        self.wonMessages = []

    def skipBlind(self):
        self.replies.append('skip')
        return self

    def bet(self, player, amount):
        self.replies.append((player, amount))
        return self

    def sendMessage(self, jid, msg):

        if msg.startswith('CARD'):
            msg = 'CARD'

        self.allMessages.append((jid, msg))
        self.sentMessages.append((jid, msg))
        self.lastMessage = (jid, msg)
        if msg.startswith('GO'):
            self.goMessages.append((jid, msg))

        if msg.startswith('CARD'):
            self.cardMessages.append((jid, 'CARD'))

        if msg != 'GO' or len(self.replies) == 0:
            return

        response = self.replies.popleft()

        if response == 'skip':
            return

        self.evt_playerResponse.fire(self, response)

    def broadcast(self, msg):
        if msg.startswith('CARD'):
            self.cardMessages.append('CARD')
            msg = 'CARD'

        if msg.startswith('WON'):
            self.wonMessages.append(msg)
            msg = 'WON'

        if msg.startswith('DEALING'):
            self.dealingMessages.append(msg)

        self.allMessages.append(msg)
        self.broadcastMessages.append(msg)
        self.lastMessage = msg


class PredictableDeck():

    def __init__(self):
        self.card = 0

    def take(self):
        self.card += 1
        return self.card

    def shuffle(self):
        self.card = 0
