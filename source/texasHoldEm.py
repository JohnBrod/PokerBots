
from collections import deque
from theHouse import Pot
from theHouse import Table
from theHouse import PlayerProxy
from EventHandling import Event
import random


def chat(msg):
    return msg['type'] in ('normal', 'chat')


def getName(x):
    return str(x)[:str(x).find('/')]


def outMessage(bet, min, max):
    if bet == 0:
        return 'You are out, you folded'

    if bet < min:
        return 'You are out, you bet %d, minimum bet was %d' % (bet, min)

    if bet > max:
        return "You are out, you bet %d, you have only %d cash avaiable" % (bet, max)


class XmppMessageInterpreter(object):

    def __init__(self, messenger):
        self.messenger = messenger
        self.messenger.evt_messageReceived += self.__on_messageReceived
        self.evt_playerResponse = Event()
        self.evt_playerJoin = Event()
        self.players = []

    def __on_messageReceived(self, sender, msg):

        if chat(msg) and msg['body'].startswith('player'):
            name = msg['body']
            player = PlayerProxy(name, self.messenger)
            self.players.append(player)
            self.evt_playerJoin(self, player)
        else:
            name = getName(msg['from'])
            player = [p for p in self.players if p.name == name][0]
            bet = int(msg['body'])
            self.evt_playerResponse(self, (player, bet))

    def sendMessage(self, jid, msg):
        self.messenger.sendMessage(jid, msg)

    def broadcast(self, msg):
        self.messenger.sendMessage('audience@pokerchat', msg)
        for player in self.players:
            self.messenger.sendMessage(player.name, msg)


class Dealer(object):
    """deals a hand to players"""
    def __init__(self, messenger):
        self.messenger = messenger
        self.playing = True

    def deal(self, players):
        self.players = players
        self.messenger.evt_playerResponse += self.__on_PlayerResponse
        self.startHand()

    def startHand(self):
        self.messenger.broadcast('DEALING ' + ' '.join([p.name for p in self.players]))
        self.cardDealer = DealsCardsToThePlayers(Deck(), self.players, self.messenger)
        self.bettingDealer = HandlesBettingBetweenThePlayers(self.players, self.messenger)
        self.cardDealer.next()
        self.bettingDealer.next()

    def __on_PlayerResponse(self, sender, response):

        self.bettingDealer.add(player=response[0], amount=response[1])

        if self.bettingDealer.allIn():
            self.cardDealer.dealRemainingCards()

        if self.handDone():
            self.bettingDealer.distributeWinnings()

            if not self.gameOver():
                self.rotateButton()
                self.startHand()
            else:
                self.playing = False
        else:
            if self.bettingDealer.done():
                self.cardDealer.next()

            self.bettingDealer.next()

    def gameOver(self):
        return len(filter(lambda x: x.cash > 0, self.players)) == 1

    def handDone(self):
        bettingDone = self.bettingDealer.done()
        dealingDone = self.cardDealer.done()
        lastPlayer = self.bettingDealer.lastPlayer() is not None

        return (bettingDone and dealingDone) or lastPlayer

    def rotateButton(self):
        self.players = self.players[1:] + self.players[:1]


class DealsCardsToThePlayers(object):
    """deals a hand to players"""
    def __init__(self, deck, players, messenger):
        self.messenger = messenger
        self.deck = deck
        self.players = players
        self.dealStages = deque([
            self.dealPrivateCards,
            self.dealCommunityCards,
            self.dealTurnCard,
            self.dealTurnCard,
            self.dealTurnCard])

        self.deck.shuffle()

    def next(self):

        if not self.dealStages:
            raise Exception("No more stages left to deal")

        stage = self.dealStages.popleft()
        stage()

    def done(self):
        return not self.dealStages

    def dealCommunityCards(self):
        communityCards = [self.deck.take(), self.deck.take(), self.deck.take()]
        message = ','.join([str(card) for card in communityCards])
        self.messenger.broadcast(message)
        for player in self.players:
            player.cards(communityCards)

    def dealTurnCard(self):
        card = self.deck.take()
        self.messenger.broadcast(str(card))
        for player in self.players:
            player.cards([card])

    def dealPrivateCards(self):
        for player in self.players:
            privateCards = [self.deck.take(), self.deck.take()]
            message = ','.join([str(card) for card in privateCards])
            self.messenger.sendMessage(player.name, message)
            player.cards(privateCards)

    def dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()


class HandlesBettingBetweenThePlayers(object):

    def __init__(self, players, messenger):
        self.messenger = messenger
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

        ranks = sorted(self.table.players, key=lambda x: x.hand(), reverse=True)
        ranks = reduce(ranks, lambda x: x.hand())

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

                    message = '{0} won {1} with {2}'.format(player.name, winnings, player.hand().rank())

                    self.messenger.broadcast(message)

                    player.deposit(winnings)

    def add(self, player, amount):

        if not self.legal(amount, player):
            self.kickOut(player, amount)
            amount = 0
        else:
            self.table.nextPlayer()

        self.messenger.broadcast('BET ' + player.name + ' ' + str(amount))
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
        self.messenger.sendMessage(player.name, msg)
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
        self.messenger.sendMessage(self.table.dealingTo().name, 'GO')


class Deck(object):
    def __init__(self):
        self.cards = deque()
        for suit in ['C', 'D', 'H', 'S']:
            for num in xrange(2, 15):
                self.cards.append(Card(num, suit))

    def take(self):
        return self.cards.popleft()

    def shuffle(self):
        random.shuffle(self.cards)


class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return self.value != other.value

    def __str__(self):
        return str(self.value) + str(self.suit)


def reduce(sequence, by):

    reduced = []
    lastItem = None
    for item in sequence:

        if lastItem and item.hand() == lastItem.hand():
            reduced[-1].append(item)
            lastItem = item
            continue

        reduced.append([item])
        lastItem = item

    return reduced
