from EventHandling import Event
from collections import deque


class StubMessenger(object):
    def __init__(self):
        self.evt_playerResponse = Event()
        self.evt_messageReceived = Event()
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
        self.replies.append((player, str(amount)))
        return self

    def join(self, jid):
        self.evt_messageReceived.fire(self, (jid, 'JOIN'))

    def addTarget(self, jid):
        pass

    def sendMessage(self, jid, msg):

        # print 'sending', jid, msg
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

        # print 'responding', response
        self.evt_messageReceived.fire(self, response)
        self.evt_playerResponse.fire(self, response)

    def broadcast(self, msg):
        # print 'broadcasting', msg

        if msg.startswith('CARD'):
            self.cardMessages.append('CARD')
            msg = 'CARD'

        if msg.startswith('WON'):
            self.wonMessages.append(msg)
            msg = 'WON'

        if msg.startswith('DEALING'):
            self.dealingMessages.append(msg)

        if msg.startswith('WINNER'):
            msg = 'WINNER'

        self.allMessages.append(msg)
        self.broadcastMessages.append(msg)
        self.lastMessage = msg


class RiggedDeck(object):
    def __init__(self, cards):
        self.cards = deque(cards)

    def take(self):
        return self.cards.popleft()

    def shuffle(self):
        pass
