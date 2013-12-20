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
    if bet < min:
        return 'OUT you bet %d, minimum bet was %d' % (bet, min)

    if bet > max:
        return "OUT you bet %d, you have only %d chips avaiable" % (bet, max)


class XmppMessageInterpreter(object):

    def __init__(self, messenger, audience):
        self.messenger = messenger
        self.messenger.evt_messageReceived += self.__on_messageReceived
        self.evt_playerResponse = Event()
        self.evt_playerJoin = Event()
        self.audience = audience
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
        self.messenger.sendMessage(self.audience, msg)
        for player in self.players:
            self.messenger.sendMessage(player.name, msg)


class HostsGame(object):
    def __init__(self, messenger):
        self.messenger = messenger
        self.playing = True

    def start(self, players):
        self.takesBets = TakesBets(self.messenger)
        self.players = players
        self.dealHand()

    def dealHand(self):
        names = ' '.join([p.name for p in self.players])
        self.messenger.broadcast('DEALING ' + names)

        self.dealsCards = DealsCards(Deck(), self.players, self.messenger)

        self.dealsCards.evt_cardsDealt += self._setupFinish
        self.takesBets.evt_betsTaken += self._nextRound

        self._nextRound(self)

    def _setupFinish(self, sender, args=None):
        self.dealsCards.evt_cardsDealt -= self._setupFinish
        self.takesBets.evt_betsTaken -= self._nextRound
        self.takesBets.evt_betsTaken += self._finishHand

    def _finishHand(self, sender, args=None):
        self.takesBets.evt_betsTaken -= self._finishHand
        self.takesBets.distributeWinnings()

        if self._gameOver():
            self.playing = False
            return

        self._rotateButton()
        self.dealHand()

    def _nextRound(self, sender, args=None):
        self.dealsCards.go()
        self.takesBets.fromPlayers(self.players)

    def _gameOver(self):
        playersWithChips = [p for p in self.players if p.chips > 0]
        return len(playersWithChips) == 1

    def _rotateButton(self):
        self.players = self.players[1:] + self.players[:1]


class DealsCards(object):
    def __init__(self, deck, players, messenger):
        self.messenger = messenger
        self.deck = deck
        self.players = players
        for player in players:
            player.dropCards()
        self.dealStages = deque([
            self._dealPrivateCards,
            self._dealThreeCards,
            self._dealOneCard,
            self._dealOneCard])
        self.evt_cardsDealt = Event()

        self.deck.shuffle()

    def go(self):

        if not self.dealStages:
            raise Exception("No more stages left to deal")

        if len([player for player in self.players if player.chips > 0]) <= 1:
            self._dealRemainingCards()
        else:
            self.dealStages.popleft()()

        if self._done():
            self.evt_cardsDealt.fire(self)

    def _done(self):
        return not self.dealStages

    def _dealThreeCards(self):
        cards = [self.deck.take(), self.deck.take(), self.deck.take()]
        message = 'CARD ' + ' '.join([str(card) for card in cards])
        self.messenger.broadcast(message)
        for player in self.players:
            player.cards(cards)

    def _dealOneCard(self):
        card = self.deck.take()
        self.messenger.broadcast('CARD ' + str(card))
        for player in self.players:
            player.cards([card])

    def _dealPrivateCards(self):
        for player in self.players:
            privateCards = [self.deck.take(), self.deck.take()]
            message = 'CARD ' + ' '.join([str(card) for card in privateCards])
            self.messenger.sendMessage(player.name, message)
            player.cards(privateCards)

    def _dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()


class TakesBets(object):

    def __init__(self, messenger):
        self.messenger = messenger
        self.pot = Pot()
        self.evt_betsTaken = Event()

    def fromPlayers(self, players):
        self.messenger.evt_playerResponse += self._on_PlayerResponse
        self.table = Table(players)
        self.lastToRaise = self.table.dealingTo()

        if self._noPlayerHasChips():
            self._finish()
        else:
            self._go()

    def distributeWinnings(self):

        chips = [self.pot.total(p) for p in self.pot.players()]
        chipsFor = dict(zip(self.pot.players(), chips))

        for rank in self._ranking():

            for player in rank:
                for opponent in self.pot.players():
                    winnerChips = chipsFor[player] / len(rank)
                    opponentChips = chipsFor[opponent] / len(rank)
                    chipsDue = min(winnerChips, opponentChips)
                    winnings = self.pot.takeFrom(opponent, chipsDue)

                    message = 'WON {0} {1} {2} {3}'.format(
                        player.name, opponent.name, winnings,
                        player.hand().rank())

                    self.messenger.broadcast(message)

                    player.deposit(winnings)

    def getMinimumBet(self, player):
        playerContribution = self.pot.total(player)

        if not self.pot.players():
            return 0

        if playerContribution == self._highestContribution():
            return 0

        return self._highestContribution() - playerContribution

    def _noPlayerHasChips(self):
        playersWithChips = len([p for p in self.table.players if p.chips > 0])
        return playersWithChips == 0

    def _on_PlayerResponse(self, sender, response):

        self._add(player=response[0], amount=response[1])

        if self._done():
            self._finish()
        else:
            self._go()

    def _finish(self):
        self.messenger.evt_playerResponse -= self._on_PlayerResponse
        self.evt_betsTaken.fire(self)

    def _done(self):

        playersWithCards = len([p for p in self.table.players if p._cards])
        if playersWithCards == 1:
            return True

        playersWithChips = len([p for p in self.table.players if p.chips > 0])
        if playersWithChips == 0:
            return True

        return self.lastToRaise == self.table.dealingTo()

    def _go(self):

        if len(self.table.dealingTo()._cards) > 0:
            dealTo = self.table.dealingTo()
            self.table.nextPlayer()
            self.messenger.sendMessage(dealTo.name, 'GO')
        else:
            self.table.nextPlayer()
            self._go()

    def _ranking(self):

        ranks = sorted(self.table.players, key=lambda x: x.hand(), reverse=True)
        ranks = reduce(ranks, lambda x: x.hand())

        return ranks

    def _add(self, player, amount):

        if amount == 0:
            player.dropCards()
            self.messenger.sendMessage(player.name, 'OUT you folded')
        elif not self._legal(amount, player):
            self._kickOut(player, amount)
            amount = 0

        self.messenger.broadcast('BET ' + player.name + ' ' + str(amount))
        if amount > self.getMinimumBet(player):
            self.lastToRaise = player

        player.withdraw(amount)
        self.pot.add(player, amount)

    def _legal(self, bet, sender):
        minimum = self.getMinimumBet(sender)
        maximum = sender.chips + 1
        allIn = sender.chips - bet == 0

        return bet in range(minimum, maximum) or allIn

    def _kickOut(self, player, bet):
        msg = outMessage(bet, self.getMinimumBet(player), player.chips)
        self.messenger.sendMessage(player.name, msg)
        player.chips = 0
        player.dropCards()

    def _highestContribution(self):
        playerTotals = [self.pot.total(p) for p in self.pot.players()]
        return max(playerTotals)


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


class RiggedDeck(object):
    def __init__(self):
        self.cards = deque([Card(11, 'H'), Card(10, 'D'),
                            Card(4, 'S'), Card(14, 'D'),
                            Card(8, 'D'), Card(6, 'H'), Card(10, 'H'),
                            Card(8, 'S'),
                            Card(9, 'C'),
                            Card(9, 'D'),
                            Card(11, 'H'), Card(10, 'D'),
                            Card(4, 'S'), Card(14, 'D'),
                            Card(8, 'D'), Card(6, 'H'), Card(10, 'H'),
                            Card(8, 'S'),
                            Card(9, 'C'),
                            Card(9, 'D')
                            ])

    def take(self):
        return self.cards.popleft()

    def shuffle(self):
        pass


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
