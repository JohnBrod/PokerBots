import time
from EventHandling import Event
from collections import deque
import random


def outMessage(bet, min, max):
    if bet == 0:
        return 'You folded'

    if bet < min:
        return 'You bet %d, minimum bet was %d' % (bet, min)

    if bet > max:
        return "You bet %d, you have only %d cash avaiable" % (bet, max)


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

    def __init__(self, players):
        self.table = Table(players)
        self.pot = Pot()
        self.transactions = []
        self.lastToRaise = self.table.dealingTo()

    def lastPlayer(self):

        return self.table.lastPlayer()

    def allIn(self):

        return self.table.allIn()

    def done(self):
        return self.lastToRaise == self.table.dealingTo()

    def ranking(self, players):

        return map(lambda x: [x], self.pot.players())

    def add(self, player, amount):

        if not self.legal(amount, player):
            self.kickOut(player, amount)
            amount = 0
        else:
            self.table.nextPlayer()

        if amount > self.getMinimumBet(player):
            self.lastToRaise = player

        self.transactions.append((player, amount))

        player.withdraw(amount)
        self.pot.add(player, amount)

    def legal(self, bet, sender):
        minimum = self.getMinimumBet(sender)
        maximum = sender.cash + 1
        allIn = sender.cash - bet == 0

        return bet in range(minimum, maximum) or allIn

    def kickOut(self, player, bet):
        msg = outMessage(bet, self.getMinimumBet(player), player.cash)
        player.outOfGame(msg)
        self.table.removeCurrent()

    def distributeWinnings(self):

        ranking = self.ranking(self.pot.players())

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

    def next(self):

        self.table.dealingTo().yourGo(self.transactions)


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


class PublicAnnouncer(object):
    def __init__(self):
        pass

    def say(self, msg):
        pass


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
