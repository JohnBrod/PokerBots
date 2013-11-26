import time
from EventHandling import Event
from Hands import Hand


class Doorman(object):
    """greets players and passes their details onto the its boss"""
    def __init__(self, waitFor, messenger, cash):
        self.players = []
        self.cash = cash
        self.waitFor = waitFor
        self.messenger = messenger
        self.messenger.evt_playerJoin += self.on_playerJoin

    def greetPlayers(self):
        time.sleep(self.waitFor)
        return self.players

    def on_playerJoin(self, sender, player):

        self.players.append(player)
        player.cash = self.cash
        self.messenger.sendMessage(player.name, 'CHIPS ' + str(self.cash))


class PlayerProxy(object):
    """allows the game to interact with the player messages """
    """as if they were from an object"""
    def __init__(self, name, cash=0):
        self._cards = []
        self.cash = cash
        self.name = name
        self.evt_response = Event()

    def withdraw(self, amount):
        self.cash -= amount
        if self.cash < 0:
            raise Exception('Overdrawn cash')

    def deposit(self, amount):
        self.cash += amount

    def cards(self, cards):
        self._cards = self._cards + cards

    def hand(self):
        return Hand(self._cards)


class Pot(object):

    def __init__(self):
        self.transactions = {}

    def add(self, player, amount):

        if player not in self.transactions:
            self.transactions[player] = 0

        self.transactions[player] += amount

    def total(self, player=None):

        if player and player not in self.transactions:
            return 0

        if player:
            return self.transactions[player]

        return sum(self.transactions.values())

    def players(self):
        return self.transactions.keys()

    def takeFrom(self, player, chips):
        availableChips = min(self.total(), chips)
        self.add(player, -availableChips)
        return availableChips


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

    def removeCurrent(self):
        self.players = filter(lambda x: x != self.dealingTo(), self.players)

        if self.dealingToPosition >= len(self.players):
            self.dealingToPosition = 0

    def lastPlayer(self):
        if len(self.players) == 1:
            return self.players[0]

    def allIn(self):
        return all(x.cash == 0 for x in self.players)
