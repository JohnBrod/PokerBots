from theHouse import Pot
from EventHandling import Event

class Dealer(object):
    """deals a hand to players"""
    def __init__(self):

        self.bigBlind = 10
        self.smallBlind = 5
        self.evt_handFinished = Event()

    def deal(self, players):

        self.table = Table(players)
        self.pot = Pot()

        for player in self.table.players:
            player.evt_response += self.__on_PlayerResponse

        self.pot.add(self.table.dealingTo(), self.smallBlind)
        self.table.dealingTo().yourGo(list(self.pot.transactions))

        self.table.nextPlayer()
        self.pot.add(self.table.dealingTo(), self.bigBlind)
        self.table.dealingTo().yourGo(list(self.pot.transactions))

        self.table.nextPlayer()
        self.table.dealingTo().yourGo(list(self.pot.transactions))

    def __on_PlayerResponse(self, sender, bet):

        if (bet < self.pot.getMinimumBet(sender)) or (bet > sender.cash):
            sender.outOfGame()
            self.table.removeCurrent()
            if self.table.lastPlayer():
                self.table.lastPlayer().handResult('You Win')
                self.evt_handFinished.fire(self)
            else:
                self.table.dealingTo().yourGo(list(self.pot.transactions))
            return

        self.pot.add(sender, bet)

        if self.table.allIn():
            for player in self.table.players: player.handResult('xxx')                
            self.evt_handFinished.fire(self)
            return
        
        self.table.nextPlayer()
        self.table.dealingTo().yourGo(list(self.pot.transactions))

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