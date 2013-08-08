import time
from EventHandling import Event

def getName(x):
    return str(x)[:str(x).find('/')]

class Doorman(object):
    """greets players and passes their details onto the its boss"""
    def __init__(self, waitFor, messenger, cash):
        self.players = []
        self.cash = cash
        self.waitFor = waitFor
        self.messenger = messenger
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.evt_playerJoined = Event()

    def greetPlayers(self):
        time.sleep(self.waitFor)
        return self.players

    def on_messageReceived(self, sender, msg):
        
        if msg['type'] in ('normal', 'chat') and msg['body'].startswith('player'):
            self.players.append(getName(msg['from']))
            self.evt_playerJoined.fire(self, msg['body'])
            self.messenger.sendMessage(msg['body'], 'Cash ' + str(self.cash))

class Casino(object):
    """Controls the flow of a game of poker"""
    def __init__(self, dealer, players):
        self.dealer = dealer
        self.players = players
        self.playing = False

    def play(self):

        self.playing = True
        self.dealer.evt_handFinished += self.on_handFinished

        table = list(self.players)

        self.dealer.deal(table)

    def on_handFinished(self, sender, args):
        table = self.playersWithCash()

        if len(table) > 1:
            self.dealer.deal(table)
        else:
            for player in self.players:
                if player.cash == 0:
                    player.gameResult('You lost')
                else:
                    player.gameResult('You won')
            self.playing = False

    def playersWithCash(self):
        return filter(lambda x: x.cash > 0, self.players)

class PlayerProxy(object):
    """allows the game to interact with the player messages as if they were from an object"""
    def __init__(self, name, dealer):
        self.cash = 0
        self.name = name
        self.evt_response = Event()
        self.dealer = dealer
        self.dealer.evt_messageReceived += self.on_messageReceived

    def yourGo(self, transactions):
        self.dealer.sendMessage(self.name, ','.join(map(lambda x: '%s %s' % (x[0], x[1]), transactions)))

    def outOfGame(self):
        pass

    def gameResult(self, result):
        self.dealer.sendMessage(self.name, 'Game Result')

    def on_messageReceived(self, sender, msg):
        if self.fromMe(msg):
            self.evt_response.fire(self, self.parse(msg))

    def parse(self, msg):
        return msg['body']

    def fromMe(self, msg):
        return msg['type'] in ('normal', 'chat') and getName(msg['from']) == self.name