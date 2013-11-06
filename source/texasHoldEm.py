from theHouse import HandlesBettingBetweenThePlayers
from EventHandling import Event
from collections import deque


class Dealer(object):
    """deals a hand to players"""
    def __init__(self, deck, public):
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
        communityCards = (self.deck.take(), self.deck.take(), self.deck.take())
        self.public.say([communityCards])
        for player in self.players:
            player.cards([communityCards])

    def dealTurnCard(self):
        card = self.deck.take()
        self.public.say([card])
        for player in self.players:
            player.cards([card])

    def dealPrivateCards(self):
        for player in self.players:
            privateCards = (self.deck.take(), self.deck.take())
            player.cards([privateCards])

    def dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()
