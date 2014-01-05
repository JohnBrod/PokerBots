from collections import deque
from theHouse import Table
from theHouse import PlayerProxy
from EventHandling import Event
import random
import logging


class InteractsWithPlayers(object):
    def __init__(self, messenger, chips=1000):
        self.messenger = messenger
        self.messenger.evt_messageReceived += self._on_messageReceived
        self.evt_playerResponse = Event()
        self.evt_playerJoin = Event()
        self.players = []
        self.chips = chips

    def _on_messageReceived(self, sender, msg):

        name = msg[0]
        content = msg[1]
        playerNames = [p.name for p in self.players]

        if content.startswith('JOIN') and name not in playerNames:
            player = PlayerProxy(name, self.messenger)
            self.players.append(player)
            player.chips = self.chips
            self.messenger.sendMessage(player.name, 'CHIPS ' + str(self.chips))
            self.messenger.addTarget(name)
            self.evt_playerJoin(self, player)
        else:
            player = [p for p in self.players if p.name == name][0]
            self.evt_playerResponse(self, (player, content))

    def sendMessage(self, player, msg):
        self.messenger.sendMessage(player.name, msg)

    def broadcast(self, msg):
        self.messenger.broadcast(msg)


class HostsGame(object):
    def __init__(self, interacts):
        self.interacts = interacts
        self.playing = True

    def start(self):
        self.takeBets = TakesBets(self.interacts)
        self.dealHand()

    def dealHand(self):
        names = ' '.join([p.name for p in self.interacts.players])
        self.interacts.broadcast('DEALING ' + names)

        self.dealsCards = DealsCards(Deck(), self.interacts)

        self.dealsCards.evt_cardsDealt += self._setupFinish
        self.takeBets.evt_betsTaken += self._nextRound

        self._nextRound(self)

    def _setupFinish(self, sender, args=None):
        self.dealsCards.evt_cardsDealt -= self._setupFinish
        self.takeBets.evt_betsTaken -= self._nextRound
        self.takeBets.evt_betsTaken += self._finishHand

    def _finishHand(self, sender, args=None):
        self.takeBets.evt_betsTaken -= self._finishHand

        distributeWinnings = DistributesWinnings(self.interacts)
        distributeWinnings.toPlayers()

        if self._gameOver():
            self._finishTournament()
        else:
            self._rotateButton()
            self.dealHand()

    def _finishTournament(self):
        self.playing = False
        winner = [p for p in self.interacts.players if p.chips > 0][0]
        message = 'WINNER {0} {1}'.format(winner.name, winner.chips)
        self.interacts.broadcast(message)

    def _nextRound(self, sender, args=None):
        self.dealsCards.go()
        self.takeBets.fromPlayers()

    def _gameOver(self):
        hasChips = [p for p in self.interacts.players if p.chips > 0]
        return len(hasChips) == 1

    def _rotateButton(self):
        players = self.interacts.players
        self.interacts.players = players[1:] + players[:1]


class DealsCards(object):
    def __init__(self, deck, interacts):
        self.interacts = interacts
        self.deck = deck
        for player in self.interacts.players:
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
        hasChips = [p for p in self.interacts.players if p.chips > 0]
        return len(hasChips) <= 1

    def _onePlayerLeft(self):
        hasCards = len([p for p in self.interacts.players if p.isPlaying()])
        return hasCards == 1

    def _dealThreeCards(self):
        cards = [self.deck.take(), self.deck.take(), self.deck.take()]
        message = 'CARD ' + ' '.join([str(card) for card in cards])
        self.interacts.broadcast(message)
        for player in self.interacts.players:
            player.cards(cards)

    def _dealOneCard(self):
        card = self.deck.take()
        self.interacts.broadcast('CARD ' + str(card))
        for player in self.interacts.players:
            player.cards([card])

    def _dealPrivateCards(self):
        for player in self.interacts.players:
            privateCards = [self.deck.take(), self.deck.take()]
            message = 'CARD ' + ' '.join([str(card) for card in privateCards])
            self.interacts.sendMessage(player, message)
            player.cards(privateCards)

    def _dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()


class DistributesWinnings(object):

    def __init__(self, interact):
        self.interact = interact

    def toPlayers(self):

        self._logRanking()
        for rank in self._ranking():
            for player in rank:
                players = self.interact.players
                otherRanks = [p for p in players if p not in rank]
                for opponent in otherRanks:
                    winnings = min(player.pot, opponent.pot / len(rank))
                    self._transfer(opponent, player, winnings)

                self._transfer(player, player, player.pot)

    def _logRanking(self):
        for rank in self._ranking():
            info = ''
            for player in rank:
                cards = [str(c) for c in sorted(player._cards)]
                info += '{0} {1} {2}|'.format(player.name, cards,
                                              player.hand().rank())
            logging.debug(info)

    def _transfer(self, source, target, amount):
        message = 'WON {0} {1} {2} {3}'.format(
            target.name, source.name, amount,
            target.hand().rank())
        self.interact.broadcast(message)
        source.transferTo(target, amount)

    def _ranking(self):

        playing = [p for p in self.interact.players if p.isPlaying()]
        ranks = sorted(playing, key=lambda x: x.hand(), reverse=True)
        ranks = reduce(ranks, lambda x: x.hand())

        return ranks


class TakesBets(object):

    def __init__(self, interact):
        self.interact = interact
        self.evt_betsTaken = Event()

    def fromPlayers(self):
        self.interact.evt_playerResponse += self._on_PlayerResponse
        self.table = Table(self.interact.players)
        self.lastToRaise = self.table.dealingTo()

        if self._noPlayerHasChips():
            self._finish()
        else:
            self._go()

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
        self.interact.evt_playerResponse -= self._on_PlayerResponse
        self.evt_betsTaken.fire(self)

    def _done(self):

        if self._noPlayerHasChips():
            return True

        return self.lastToRaise == self.table.dealingTo()

    def _go(self):

        if self._onePlayerLeft():
            self._finish()
            return

        if self.table.dealingTo().isPlaying():
            dealTo = self.table.dealingTo()
            self.interact.sendMessage(dealTo, 'GO')
        else:
            self.table.nextPlayer()
            self._go()

    def _onePlayerLeft(self):
        hasCards = len([p for p in self.interact.players if p.isPlaying()])
        return hasCards == 1

    def _add(self, player, amount):

        if amount < self.getMinimumBet(player):
            self._fold(player)
        elif amount > player.chips:
            self._kickOutOfGame(player, 'OVERDRAWN')
            amount = 0

        self.interact.broadcast('BET ' + player.name + ' ' + str(amount))
        if amount > self.getMinimumBet(player):
            self.lastToRaise = player

        player.bet(amount)

    def _fold(self, player):
        player.dropCards()
        self.interact.sendMessage(player, 'OUT FOLD')

    def _kickOutOfGame(self, player, reason):
        self.interact.sendMessage(player, "OUT " + reason)
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
