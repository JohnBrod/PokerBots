from theHouse import Pot
from EventHandling import Event
from Queue import Queue

def outMessage(bet, min, max):
    if bet == 0:
        return 'You folded'

    if bet < min:
        return 'You bet %d, minimum bet was %d' % (bet, min)

    if bet > max:
        return "You bet %d, you have only %d cash avaiable" % (bet, max)

class Dealer(object):
    """deals a hand to players"""
    def __init__(self, deck):
        self.deck = deck
        self.bigBlind = 10
        self.smallBlind = 5
        self.evt_gameFinished = Event()
        self.dealStages = Queue()
        self.dealStages.put(self.dealPrivateCards)
        self.dealStages.put(self.dealCommunityCards)
        self.dealStages.put(self.dealTurnCard)
        self.dealStages.put(self.dealTurnCard)
        self.dealStages.put(self.dealTurnCard)

    def deal(self, players):

        self.table = Table(players)
        self.pot = Pot()

        for player in self.table.players:
            player.evt_response += self.__on_PlayerResponse

        self.dealStages.get()()

        self.pot.add(self.table.dealingTo(), self.smallBlind)        
        self.table.dealingTo().yourGo(list(self.pot.transactions))

        self.table.nextPlayer()
        self.pot.add(self.table.dealingTo(), self.bigBlind)
        self.table.dealingTo().yourGo(list(self.pot.transactions))

        self.table.nextPlayer()
        self.table.dealingTo().yourGo(list(self.pot.transactions))

    def __on_PlayerResponse(self, sender, bet):
# the next round of cards are dealt once all players (other than players that have folded) have put the same amount in the pot
# the exception is the community cards, the big blind has the option to bet again if everyone just calls the big blind. In this case the big blind can choose not
# to exercise the option by calling (bet of 0), or exercise the option (bet more than 0)

        if bet not in range(self.pot.getMinimumBet(sender), sender.cash + 1):

            sender.outOfGame(outMessage(bet, self.pot.getMinimumBet(sender), sender.cash))
            self.table.removeCurrent()

            if self.table.lastPlayer():
                self.table.lastPlayer().handResult('You win')
            else:
                self.table.dealingTo().yourGo(list(self.pot.transactions))
            return

        self.pot.add(sender, bet)

        if self.pot.allIn():

            if not self.dealStages.empty():
                self.dealStages.get()()
            else:
                for player in self.table.players: player.handResult('xxx')                

        if self.table.allIn():
            for player in self.table.players: player.handResult('xxx')                
            self.evt_gameFinished.fire(self)
            return
        
        self.table.nextPlayer()
        self.table.dealingTo().yourGo(list(self.pot.transactions))

    def dealCommunityCards(self):
        communityCards = (self.deck.take(), self.deck.take(), self.deck.take())
        for player in self.table.players:
            player.cards(communityCards)
        self.ccDealt = True

    def dealTurnCard(self):
        flop = (self.deck.take())
        for player in self.table.players:
            player.cards(flop)

    def dealPrivateCards(self):
        for player in self.table.players:            
            player.cards((self.deck.take(), self.deck.take()))

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
        if len(self.players) == 1: return self.players[0]

    def allIn(self):
        return len(filter(lambda x: x.cash == 0, self.players)) == len(self.players)