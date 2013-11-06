from collections import defaultdict
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
        self.c = []
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
        self.c = self.c + cards

    def hand(self):
        return self.c

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

    def ranking(self):

        ranks = group(lambda x: rank(x.hand()), self.pot.players())
        ranks = map(lambda x: x[1], ranks)

        return ranks

    def distributeWinnings(self):

        chips = map(lambda x: self.pot.total(x), self.pot.players())
        chipsFor = dict(zip(self.pot.players(), chips))

        for rank in self.ranking():

            for player in rank:

                for opponent in self.pot.players():
                    winnerChips = chipsFor[player] / len(rank)
                    opponentChips = chipsFor[opponent] / len(rank)
                    chipsDue = min(winnerChips, opponentChips)
                    winnings = self.pot.takeFrom(opponent, chipsDue)
                    player.deposit(winnings)

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


def rank(hand):

    if pair(hand):
        return 0

    return 1


def highestCard(hand):

    return sorted(hand, key=lambda x: x[0])[-1]


def pair(hand):
    values = map(lambda x: x[0], hand)
    pairs = [card for card in hand if values.count(card[0]) == 2]

    if len(pairs) == 2:
        return pairs


def trips(hand):
    values = map(lambda x: x[0], hand)
    trips = [card for card in hand if values.count(card[0]) == 3]

    return trips


def poker(hand):
    values = map(lambda x: x[0], hand)
    poker = [card for card in hand if values.count(card[0]) == 4]

    return poker


def flush(hand):

    flush = flushCards(hand)

    if flush:
        return sorted(hand, key=lambda x: x[0], reverse=True)[0:5]


def flushCards(hand):
    suits = map(lambda x: x[1], hand)
    flush = [card for card in hand if suits.count(card[1]) >= 5]

    return flush


def distinctFace(cards):

    distinctFaces = defaultdict(list)

    for f, s in cards:
        distinctFaces[f].append((f, s))

    cards = [(distinctFaces[k][0]) for k in distinctFaces]

    return cards


def straight(cards):

    cards = distinctFace(cards)
    cards = sorted(cards, key=lambda x: x[0], reverse=True)

    while len(cards) >= 5:

        if cards[0][0] - cards[4][0] == 4:
            return cards[0:5]

        cards = cards[1:]


def straightFlush(cards):

    return straight(flushCards(cards))


def highestHand(cards):

    return straightFlush(cards)


def house(cards):

    if not trips(cards):
        return

    hand = trips(cards)

    cards = [card for card in cards if card not in hand]
    if not pair(cards):
        return

    return hand + pair(cards)


def group(by, sequence):
    keys = list(set(map(lambda x: by(x), sequence)))
    grouping = map(lambda x: (x, filter(lambda y: by(y) == x, sequence)), keys)

    return grouping
