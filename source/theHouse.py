import time
from EventHandling import Event
from Hands import Hand


class Doorman(object):
    """greets players and passes their details onto the its boss"""
    def __init__(self, waitFor, messenger, chips):
        self.players = []
        self.chips = chips
        self.waitFor = waitFor
        self.messenger = messenger
        self.messenger.evt_playerJoin += self.on_playerJoin

    def greetPlayers(self):
        time.sleep(self.waitFor)
        return self.players

    def on_playerJoin(self, sender, player):

        self.players.append(player)
        player.chips = self.chips
        self.messenger.sendMessage(player.name, 'CHIPS ' + str(self.chips))


class PlayerProxy(object):
    """allows the game to interact with the player messages """
    """as if they were from an object"""
    def __init__(self, name, chips=0):
        self._cards = []
        self.chips = chips
        self.pot = 0
        self.name = name
        self.evt_response = Event()

    def withdraw(self, amount):
        self.chips -= amount
        if self.chips < 0:
            raise Exception('Overdrawn chips')
        self.pot += amount

    def transferTo(self, player, amount):
        self.pot -= amount
        player.deposit(amount)

    def deposit(self, amount):
        self.chips += amount

    def cards(self, cards):
        self._cards = self._cards + cards

    def hand(self):
        return Hand(self._cards)

    def dropCards(self):
        self._cards = []


class Table(object):
    """players sit around this and get dealt to in order"""
    def __init__(self, players):
        self.players = players
        self.dealingToPosition = 0

    def nextPlayer(self):
        self.dealingToPosition += 1
        if self.dealingToPosition >= len(self.players):
            self.dealingToPosition = 0

    def dealingTo(self):
        return self.players[self.dealingToPosition]

    def lastPlayer(self):
        if len(self.players) == 1:
            return self.players[0]

    def allIn(self):
        return len([x for x in self.players if x.chips > 0]) <= 1

    def playing(self):
        playing = [p for p in self.players if p._cards]
        return playing
