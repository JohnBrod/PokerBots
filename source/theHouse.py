import time
from EventHandling import Event
from collections import deque
import random

def getName(x):
    return str(x)[:str(x).find('/')]


def chat(msg):
    return msg['type'] in ('normal', 'chat')


def playerMessage(transactions):
    return ','.join(map(lambda x: '%s %s' % (x[0].name, x[1]), transactions))


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

        if chat(msg) and msg['body'].startswith('player'):
            self.players.append(getName(msg['from']))
            self.evt_playerJoined.fire(self, msg['body'])
            self.messenger.sendMessage(msg['body'], 'Cash ' + str(self.cash))


class PlayerProxy(object):
    """allows the game to interact with the player messages """
    """as if they were from an object"""
    def __init__(self, name, dealer):
        self.cash = 1000
        self.name = name
        self.evt_response = Event()
        self.dealer = dealer
        self.dealer.evt_messageReceived += self.on_messageReceived

    def yourGo(self, transactions):
        self.dealer.sendMessage(self.name, playerMessage(transactions))

    def send(self, msg):
        self.dealer.sendMessage(self.name, msg)

    def cards(self, transactions):
        pass

    def outOfGame(self, msg):
        pass

    def youWin(self, amount):
        self.cash += amount

    def gameResult(self, result):
        self.dealer.sendMessage(self.name, 'Game Result')

    def handResult(self, result):
        self.dealer.sendMessage(self.name, 'Hand Result')

    def on_messageReceived(self, sender, msg):
        if self.fromMe(msg):
            bet = self.parse(msg)
            self.evt_response.fire(self, bet)

    def parse(self, msg):
        return int(msg['body'])

    def fromMe(self, msg):
        return chat(msg) and getName(msg['from']) == self.name


class Pot(object):

    def __init__(self):
        self.transactions = []

    def add(self, player, amount):
        player.cash -= amount
        self.transactions.append((player, amount))

    def total(self, player=None):

        txns = self.transactionsFor(player) if player else self.transactions

        return sum(map(lambda x: x[1], txns))

    def getMinimumBet(self, player):
        playerContribution = self.total(player)

        if not self.players():
            return 0

        if playerContribution == self.highestContribution():
            return 0

        return self.highestContribution() - playerContribution

    def roundOfBettingOver(self):

        if len(self.players()) == 1:
            return True

        if self.bigBlindDueOption():
            return False

        return len(self.leftToContribute()) == 0

    def leftToContribute(self):
        return filter(lambda x: self.getMinimumBet(x) > 0, self.players())

    def players(self):
        players = set(map(lambda x: x[0], self.transactions))

        return players.difference(set(filter(self.folded, players)))

    def folded(self, player):

        if player == self.bigBlind() and len(self.transactionsFor(player)) == 2:
            return False

        return self.transactionsFor(player)[-1][1] == 0

    def highestContribution(self):
        return max(map(lambda x: self.total(x), self.players()))

    def smallBlind(self):
        return self.transactions[0][0]

    def bigBlind(self):
        if len(self.transactions) > 1:
            return self.transactions[1][0]

    def smallBlindWasPrevious(self):
        return self.transactions[-1][0] == self.smallBlind()

    def transactionsFor(self, player):
        return filter(lambda x: x[0] == player, self.transactions)

    def hadOneGo(self, player):
        return len(self.transactionsFor(player)) == 1

    def bigBlindDueOption(self):
        return self.smallBlindWasPrevious() and self.hadOneGo(self.bigBlind())


class Deck(object):
    def __init__(self):
        self.cards = deque()
        for suit in ['C', 'D', 'H', 'S']:
            for num in xrange(2, 15):
                self.cards.append((num, suit))

    def take(self):
        return self.cards.popleft()

    def shuffle(self):
        random.shuffle(self.cards)
