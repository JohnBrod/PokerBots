import time
from EventHandling import Event
from collections import deque
import random


def getName(x):
    return str(x)[:str(x).find('/')]


def chat(msg):
    return msg['type'] in ('normal', 'chat')


def playerMessage(transactions):
    msg = ','.join(map(lambda x: '%s %s' % (x[0].name, x[1]), transactions))

    if msg == '':
        return 'go'

    return msg


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

    def withdraw(self, amount):
        self.cash -= amount
        if self.cash < 0:
            raise Exception('Overdrawn cash')

    def deposit(self, amount):
        self.cash += amount

    def yourGo(self, transactions):
        self.dealer.sendMessage(self.name, playerMessage(transactions))

    def send(self, msg):
        self.dealer.sendMessage(self.name, msg)

    def cards(self, cards):
        pass

    def outOfGame(self, msg):
        pass

    def youWin(self, amount):
        pass

    def gameResult(self, result):
        self.dealer.sendMessage(self.name, 'Game Result')

    def handResult(self, result):
        print self.name, result
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


class HandlesBettingBetweenThePlayers(object):

    def __init__(self, handComparison):
        self.handComparison = handComparison
        self.pot = Pot()

    def add(self, player, amount):

        player.withdraw(amount)
        self.pot.add(player, amount)

    def distributeWinnings(self):

        ranking = self.handComparison(self.pot.players())

        chips = map(lambda x: self.pot.total(x), self.pot.players())
        chipsFor = dict(zip(self.pot.players(), chips))

        for rank in ranking:

            for player in rank:

                for opponent in self.pot.players():
                    winnerChips = chipsFor[player] / len(rank)
                    opponentChips = chipsFor[opponent] / len(rank)
                    chipsDue = min(winnerChips, opponentChips)
                    winnings = self.pot.takeFrom(opponent, chipsDue)
                    player.deposit(winnings)

    def getMinimumBet(self, player):
        playerContribution = self.pot.total(player)

        if not self.pot.players():
            return 0

        if playerContribution == self.highestContribution():
            return 0

        return self.highestContribution() - playerContribution

    def highestContribution(self):
        return max(map(lambda x: self.pot.total(x), self.pot.players()))


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
