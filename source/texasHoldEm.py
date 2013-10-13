from theHouse import Pot
from EventHandling import Event
from collections import deque


def outMessage(bet, min, max):
    if bet == 0:
        return 'You folded'

    if bet < min:
        return 'You bet %d, minimum bet was %d' % (bet, min)

    if bet > max:
        return "You bet %d, you have only %d cash avaiable" % (bet, max)


class Dealer(object):
    """deals a hand to players"""
    def __init__(self, deck, handComparison):
        self.handComparison = handComparison
        self.playing = True
        self.bigBlind = 10
        self.smallBlind = 5
        self.evt_handFinished = Event()
        self.deck = deck

    def deal(self, players):
        self.players = players

        for player in self.players:
            player.evt_response += self.__on_PlayerResponse

        self.startHand()

    def startHand(self):
        self.table = Table(self.players)
        self.cardDealer = CardDealer(self.deck, self.table)
        self.pot = Pot()
        self.cardDealer.dealPrivateCards()

        self.pot.add(self.table.dealingTo(), self.smallBlind)
        self.table.dealingTo().yourGo(list(self.pot.transactions))

        self.table.nextPlayer()
        self.pot.add(self.table.dealingTo(), self.bigBlind)
        self.table.dealingTo().yourGo(list(self.pot.transactions))
        self.bbPlayer = self.table.dealingTo()

        self.table.nextPlayer()
        self.table.dealingTo().yourGo(list(self.pot.transactions))

    def __on_PlayerResponse(self, sender, bet):

        if not self.legal(bet, sender):
            self.kickOut(sender, bet)
            bet = 0
        else:
            self.table.nextPlayer()

        self.pot.add(sender, bet)

        if self.table.allIn():
            self.cardDealer.dealRemainingCards()

        if self.handFinished():
            self.declareWinner()

            if self.gameOver():
                self.playing = False
            else:
                self.rotateButton()
                self.startHand()
        else:
            if self.pot.roundOfBettingOver() and not self.cardDealer.finishedDealing():
                self.cardDealer.dealNext()

            self.table.dealingTo().yourGo(list(self.pot.transactions))

    def declareWinner(self):
        winner = self.handComparison(None, self.table.players)

        for player in self.players:
            player.handResult(winner.name + ' wins')

        winner.cash += self.pot.total()
        winner.youWin(self.pot.total())

    def gameOver(self):
        return len(filter(lambda x: x.cash > 0, self.players)) <= 1

    def legal(self, bet, sender):
        minimum = self.pot.getMinimumBet(sender)
        maximum = sender.cash + 1
        return bet in range(minimum, maximum)

    def handFinished(self):
        bettingDone = self.pot.roundOfBettingOver()
        dealingDone = self.cardDealer.finishedDealing()
        lastPlayer = self.table.lastPlayer() is not None

        return (bettingDone and dealingDone) or lastPlayer

    def rotateButton(self):
        self.players = self.players[1:] + self.players[:1]

    def kickOut(self, player, bet):
        msg = outMessage(bet, self.pot.getMinimumBet(player), player.cash)
        player.outOfGame(msg)
        self.table.removeCurrent()


class CardDealer(object):
    """deals a hand to players"""
    def __init__(self, deck, table):
        self.deck = deck
        self.table = table
        self.dealStages = deque([
            self.dealCommunityCards,
            self.dealTurnCard,
            self.dealTurnCard,
            self.dealTurnCard])

        self.deck.shuffle()

    def dealNext(self):
        self.dealStages.popleft()()

    def finishedDealing(self):
        return not self.dealStages

    def dealCommunityCards(self):
        communityCards = (self.deck.take(), self.deck.take(), self.deck.take())
        for player in self.table.players:
            player.cards(communityCards)

    def dealTurnCard(self):
        card = self.deck.take()
        for player in self.table.players:
            player.cards(card)

    def dealPrivateCards(self):
        for player in self.table.players:
            privateCards = (self.deck.take(), self.deck.take())
            player.cards(privateCards)

    def dealRemainingCards(self):
        while len(self.dealStages) > 0:
            self.dealStages.popleft()()


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
