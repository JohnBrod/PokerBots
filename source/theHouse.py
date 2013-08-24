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
        self.dealer.evt_gameFinished += self.on_gameFinished

    def play(self):

        self.playing = True

        self.dealer.deal(list(self.players))

    def on_gameFinished(self, sender, args = None):

        for player in self.players: player.gameResult('xxx')

        self.playing = False

class PlayerProxy(object):
    """allows the game to interact with the player messages as if they were from an object"""
    def __init__(self, name, dealer):
        self.cash = 1000
        self.name = name
        self.evt_response = Event()
        self.dealer = dealer
        self.dealer.evt_messageReceived += self.on_messageReceived

    def yourGo(self, transactions):
        self.dealer.sendMessage(self.name, ','.join(map(lambda x: '%s %s' % (x[0].name, x[1]), transactions)))

    def send(self, msg):
        self.dealer.sendMessage(self.name, msg)

    def cards(self, transactions):
        pass

    def outOfGame(self, msg):
        pass

    def youWin(self):
        pass

    def gameResult(self, result):
        self.dealer.sendMessage(self.name, 'Game Result')

    def handResult(self, result):
        self.dealer.sendMessage(self.name, 'Hand Result')

    def on_messageReceived(self, sender, msg):
        if self.fromMe(msg):
            self.evt_response.fire(self, self.parse(msg))

    def parse(self, msg):
        return int(msg['body'])

    def fromMe(self, msg):
        return msg['type'] in ('normal', 'chat') and getName(msg['from']) == self.name

class Pot(object):

    def __init__(self):
        self.transactions = []

    def add(self, player, amount):
        player.cash -= amount
        self.transactions.append((player, amount))

    def getTotal(self, player = None):

        txns = filter(lambda x: x[0].name == player.name, self.transactions) if player else self.transactions

        return sum(map(lambda x: x[1], txns))

    def getMinimumBet(self, player):
        playerContribution = self.getTotal(player)
        contributors = set(map(lambda x: x[0], self.transactions))

        if not contributors: return 0

        highestContribution = max(map(lambda x: self.getTotal(x), contributors))

        if playerContribution == highestContribution:
            return 0

        return highestContribution - playerContribution

    def allIn(self):
        contributors = list(set(map(lambda x: x[0], self.transactions)))

        return len(filter(lambda x: self.getMinimumBet(x) > 0, contributors)) == 0
