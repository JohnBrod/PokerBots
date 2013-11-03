from theHouse import HandlesBettingBetweenThePlayers
from EventHandling import Event
from collections import deque
from collections import defaultdict


class Dealer(object):
    """deals a hand to players"""
    def __init__(self, deck, ranking, public):
        self.ranking = ranking
        self.public = public
        self.playing = True
        self.evt_handDone = Event()
        self.deck = deck

    def deal(self, players):
        self.players = players

        for player in self.players:
            player.evt_response += self.__on_PlayerResponse

        self.startHand()

    def startHand(self):
        self.cardDealer = DealsCardsToThePlayers(self.deck, self.players, self.public)
        self.bettingDealer = HandlesBettingBetweenThePlayers(self.players)
        self.bettingDealer.ranking = self.ranking
        self.cardDealer.dealNext()
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
                self.cardDealer.dealNext()

            self.bettingDealer.next()

    def gameOver(self):
        return len(filter(lambda x: x.cash > 0, self.players)) <= 1

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

    def dealNext(self):

        if not self.dealStages:
            raise Exception("No more stages left to deal")

        stage = self.dealStages.popleft()
        stage()

    def done(self):
        return not self.dealStages

    def dealCommunityCards(self):
        communityCards = (self.deck.take(), self.deck.take(), self.deck.take())
        self.public.say(communityCards)

    def dealTurnCard(self):
        card = self.deck.take()
        self.public.say(card)

    def dealPrivateCards(self):
        for player in self.players:
            privateCards = (self.deck.take(), self.deck.take())
            player.cards(privateCards)

    def dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()


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
