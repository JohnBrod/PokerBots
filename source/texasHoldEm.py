from collections import deque
from theHouse import Pot
from theHouse import Table
from EventHandling import Event
import random


def outMessage(bet, min, max):
    if bet == 0:
        return 'You folded'

    if bet < min:
        return 'You bet %d, minimum bet was %d' % (bet, min)

    if bet > max:
        return "You bet %d, you have only %d cash avaiable" % (bet, max)


class Dealer(object):
    """deals a hand to players"""
    def __init__(self, public):
        self.public = public
        self.playing = True
        self.evt_handDone = Event()

    def deal(self, players):
        self.players = players

        for player in self.players:
            player.evt_response += self.__on_PlayerResponse

        self.startHand()

    def startHand(self):
        self.cardDealer = DealsCardsToThePlayers(Deck(), self.players, self.public)
        self.bettingDealer = HandlesBettingBetweenThePlayers(self.players)
        self.cardDealer.next()
        self.bettingDealer.next()

    def __on_PlayerResponse(self, sender, bet):

        self.bettingDealer.add(sender, bet)

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
    def __init__(self, deck, players, public):
        self.public = public
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
        self.public.say(communityCards)
        for player in self.players:
            player.cards(communityCards)

    def dealTurnCard(self):
        card = self.deck.take()
        self.public.say([card])
        for player in self.players:
            player.cards([card])

    def dealPrivateCards(self):
        for player in self.players:
            privateCards = [self.deck.take(), self.deck.take()]
            player.cards(privateCards)

    def dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()


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

        ranks = sorted(self.pot.players(), key=lambda x: x.hand(), reverse=True)
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
