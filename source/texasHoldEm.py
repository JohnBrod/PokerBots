from collections import deque
from theHouse import Table
from theHouse import PlayerProxy
from EventHandling import Event
import random
import logging


class MessageInterpreter(object):
    '''sends messages to and interprets messages from the players'''
    def __init__(self, messenger, audience):
        self.messenger = messenger
        self.messenger.evt_messageReceived += self._on_messageReceived
        self.evt_playerResponse = Event()
        self.evt_playerJoin = Event()
        self.audience = audience
        self.players = []

    def _on_messageReceived(self, sender, msg):

        name = msg[0]
        content = msg[1]

        if content.startswith('JOIN'):
            player = PlayerProxy(name, self.messenger)
            self.players.append(player)
            self.evt_playerJoin(self, player)
        else:
            player = [p for p in self.players if p.name == name][0]
            self.evt_playerResponse(self, (player, content))

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
            self._finishTournament()
        else:
            self._rotateButton()
            self.dealHand()

    def _finishTournament(self):
        self.playing = False
        winner = [p for p in self.players if p.chips > 0][0]
        message = 'WINNER {0} {1}'.format(winner.name, winner.chips)
        self.messenger.broadcast(message)

    def _nextRound(self, sender, args=None):
        self.dealsCards.go()
        self.takesBets.fromPlayers(self.players)

    def _gameOver(self):
        hasChips = [p for p in self.players if p.chips > 0]
        return len(hasChips) == 1

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

        if self._onePlayerLeft():
            self.evt_cardsDealt.fire(self)
        elif self._allInGame():
            self._dealRemainingCards()
        else:
            self.dealStages.popleft()()

        if not self.dealStages:
            self.evt_cardsDealt.fire(self)

    def _allInGame(self):
        hasChips = [player for player in self.players if player.chips > 0]
        return len(hasChips) <= 1

    def _onePlayerLeft(self):
        playersWithCards = len([p for p in self.players if p.isPlaying()])
        return playersWithCards == 1

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
        self.evt_betsTaken = Event()

    def fromPlayers(self, players):
        self.players = players
        self.messenger.evt_playerResponse += self._on_PlayerResponse
        self.table = Table(players)
        self.lastToRaise = self.table.dealingTo()

        if self._noPlayerHasChips():
            self._finish()
        else:
            self._go()

    def distributeWinnings(self):

        self._logRanking()
        for rank in self._ranking():
            for player in rank:
                otherRanks = [p for p in self.players if p not in rank]
                for opponent in otherRanks:
                    winnings = min(player.pot, opponent.pot / len(rank))
                    self.transfer(opponent, player, winnings)

                self.transfer(player, player, player.pot)

    def _logRanking(self):
        for rank in self._ranking():
            info = ''
            for player in rank:
                cards = [str(c) for c in sorted(player._cards)]
                info += '{0} {1} {2}|'.format(player.name, cards,
                                              player.hand().rank())
            logging.debug(info)

    def transfer(self, source, target, amount):
        message = 'WON {0} {1} {2} {3}'.format(
            target.name, source.name, amount,
            target.hand().rank())
        self.messenger.broadcast(message)
        source.transferTo(target, amount)

    def getMinimumBet(self, player):
        highestContribution = max([p.pot for p in self.table.playing()])
        return highestContribution - player.pot

    def _noPlayerHasChips(self):
        hasChips = len([p for p in self.table.playing() if p.chips > 0])
        return hasChips == 0

    def _on_PlayerResponse(self, sender, response):

        player = response[0]
        amount = response[1]

        if player != self.table.dealingTo():
            self._kickOutOfGame(player, 'OUT_OF_TURN')
            return

        if not amount.isdigit():
            self._kickOutOfGame(player, 'NOT_A_NUMBER')
            return

        self._add(player, int(amount))

        self.table.nextPlayer()

        if self._done():
            self._finish()
        else:
            self._go()

    def _finish(self):
        self.messenger.evt_playerResponse -= self._on_PlayerResponse
        self.evt_betsTaken.fire(self)

    def _done(self):

        if self._noPlayerHasChips():
            return True

        return self.lastToRaise == self.table.dealingTo()

    def _go(self):

        if self._onePlayerLeft():
            self._finish()

        if self.table.dealingTo().isPlaying():
            dealTo = self.table.dealingTo()
            self.messenger.sendMessage(dealTo.name, 'GO')
        else:
            self.table.nextPlayer()
            self._go()

    def _onePlayerLeft(self):
        playersWithCards = len([p for p in self.players if p.isPlaying()])
        return playersWithCards == 1

    def _ranking(self):

        playing = self.table.playing()
        ranks = sorted(playing, key=lambda x: x.hand(), reverse=True)
        ranks = reduce(ranks, lambda x: x.hand())

        return ranks

    def _add(self, player, amount):

        if amount < self.getMinimumBet(player):
            self._fold(player)
        elif amount > player.chips:
            self._kickOutOfGame(player, 'OVERDRAWN')
            amount = 0

        self.messenger.broadcast('BET ' + player.name + ' ' + str(amount))
        if amount > self.getMinimumBet(player):
            self.lastToRaise = player

        player.withdraw(amount)

    def _fold(self, player):
        player.dropCards()
        self.messenger.sendMessage(player.name, 'OUT FOLD')

    def _kickOutOfGame(self, player, reason):
        self.messenger.sendMessage(player.name, "OUT " + reason)
        player.chips = 0
        player.dropCards()


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
