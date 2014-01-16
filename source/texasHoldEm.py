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


class PlaysTournament(object):
    def __init__(self, interacts):
        self._interacts = interacts
        self.evt_done = Event()
        self._playsHand = PlaysHand(self._interacts)
        self._playsHand.evt_done += self._onHandDone

    def start(self):
        names = ' '.join([p.name for p in self._interacts.players])
        self._interacts.broadcast('DEALING ' + names)
        self._playsHand.start()

    def _onHandDone(self, sender, args=None):
        if self._done():
            self._finish()
        else:
            self._rotateButton()
            self.start()

    def _finish(self):
        winner = [p for p in self._interacts.players if p.chips > 0][0]
        message = 'WINNER {0} {1}'.format(winner.name, winner.chips)
        self._interacts.broadcast(message)
        self.evt_done(self, None)

    def _done(self):
        hasChips = [p for p in self._interacts.players if p.chips > 0]
        return len(hasChips) == 1

    def _rotateButton(self):
        players = self._interacts.players
        self._interacts.players = players[1:] + players[:1]


class DealsTexasHoldEm(object):
    def __init__(self, interacts):
        self._interacts = interacts
        self.deck = Deck()

    def start(self):
        self._stages = deque([
            self._dealPrivateCards,
            self._dealThreeCards,
            self._dealOneCard,
            self._dealOneCard])

        self.deck.shuffle()

        self.next()

    def next(self):
        self._stages.popleft()()

        if self._allInGame():
            self.dealRemaining()

    def more(self):
        return len(self._stages) > 0

    def _dealThreeCards(self):
        cards = [self.deck.take(), self.deck.take(), self.deck.take()]
        message = 'CARD ' + ' '.join([str(card) for card in cards])
        self._interacts.broadcast(message)
        for player in self._interacts.players:
            player.cards(cards)

    def _dealOneCard(self):
        card = self.deck.take()
        self._interacts.broadcast('CARD ' + str(card))
        for player in self._interacts.players:
            player.cards([card])

    def _dealPrivateCards(self):
        for player in self._interacts.players:
            privateCards = [self.deck.take(), self.deck.take()]
            message = 'CARD ' + ' '.join([str(card) for card in privateCards])
            self._interacts.sendMessage(player, message)
            player.cards(privateCards)

    def dealRemaining(self):
        while len(self._stages) > 0:
            self._stages.popleft()()

    def _allInGame(self):
        hasChips = [p for p in self._interacts.players if p.chips > 0]
        return len(hasChips) <= 1


class PlaysHand(object):
    def __init__(self, interacts):
        self._interacts = interacts
        self.evt_done = Event()
        self._deck = DealsTexasHoldEm(self._interacts)
        self._takeBets = TakesBets(self._interacts)
        self._takeBets.evt_done += self._onRoundDone

    def start(self):
        for player in self._interacts.players:
            player.dropCards()

        self._deck.start()
        self._takeBets.start()

    def _onRoundDone(self, sender=None, args=None):
        if not self._deck.more() or self._onePlayerLeft():
            self._finish()
        else:
            self._deck.next()
            self._takeBets.next()

    def _finish(self):
        dw = DistributesWinnings(self._interacts)
        dw.toPlayers()
        self.evt_done.fire(self)

    def _onePlayerLeft(self):
        hasCards = len([p for p in self._interacts.players if p.isPlaying()])
        return hasCards == 1


class TakesBets(object):

    def __init__(self, interacts):
        self._interacts = interacts
        self.evt_done = Event()
        self._interacts.evt_playerResponse += self._on_PlayerResponse
        self.lastToRaise = None
        self.table = Table()

    def start(self):
        self.table.seat(self._interacts.players)
        self.lastToRaise = self.table.dealingTo()
        self.next()

    def next(self):
        if self._notEnoughWithChips():
            self._finish()
        elif self._onePlayerLeft():
            self._finish()
        elif self.table.dealingTo().isPlaying():
            dealTo = self.table.dealingTo()
            self._interacts.sendMessage(dealTo, 'GO')
        else:
            self.table.nextPlayer()
            self.next()

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
            self.next()

    def getMinimumBet(self, player):
        highestContribution = max([p.pot for p in self.table.playing()])
        minBet = highestContribution - player.pot
        return minBet

    def _notEnoughWithChips(self):
        hasChips = len([p for p in self.table.playing() if p.chips > 0])
        return hasChips <= 1

    def _finish(self):
        self.evt_done(self)

    def _done(self):
        if self._notEnoughWithChips():
            return True

        return self.lastToRaise == self.table.dealingTo()

    def _onePlayerLeft(self):
        hasCards = len([p for p in self._interacts.players if p.isPlaying()])
        return hasCards == 1

    def _add(self, player, amount):
        if self._folding(player, amount):
            self._fold(player)
        elif amount > player.chips:
            self._kickOutOfGame(player, 'OVERDRAWN')
            amount = 0

        self._interacts.broadcast('BET ' + player.name + ' ' + str(amount))
        if amount > self.getMinimumBet(player):
            self.lastToRaise = player

        player.bet(amount)

    def _folding(self, player, amount):
        return amount < self.getMinimumBet(player) and player.chips - amount > 0

    def _fold(self, player):
        player.dropCards()
        self._interacts.sendMessage(player, 'OUT FOLD')

    def _kickOutOfGame(self, player, reason):
        self._interacts.sendMessage(player, "OUT " + reason)
        player.chips = 0
        player.dropCards()


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
