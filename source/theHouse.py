import time
from EventHandling import Event

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
        if msg['type'] in ('normal', 'chat') and msg['body'].startswith('Player'):
            self.players.append(msg['body'])
            self.evt_playerJoined.fire(self, msg['body'])
            self.messenger.sendMessage(msg['body'], 'Cash ' + str(self.cash))

class Casino(object):
    """Controls the flow of a game of poker"""
    def __init__(self, dealer, players):
        self.dealer = dealer
        self.players = players

    def play(self):

        table = list(self.players)

        while len(table) > 1:
            self.dealer.deal(table)
            table = self.playersWithCash()

        for player in self.players:
            if player.cash == 0:
                player.gameResult('You lost')
            else:
                player.gameResult('You won')

    def playersWithCash(self):
        return filter(lambda x: x.cash > 0, self.players)

class PlayerProxy(object):
    """allows the game to interact with the player messages as if they were from an object"""
    def __init__(self, name, messenger):
        self.cash = 0
        self.name = name
        self.response = Event()
        self.messenger = messenger

    def yourGo(self):
        pass

    def outOfGame(self):
        pass

    def gameResult(self, result):
        self.messenger.sendMessage(self.name, 'Game Result')
