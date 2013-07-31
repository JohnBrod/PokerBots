from EventHandling import Event

class Dealer(object):
    """deals a hand to players"""
    def __init__(self):
        self.evt_handFinished = Event()

    def deal(self, players):
        for player in players:
            player.evt_response += self.__on_PlayerResponse

        self.table = Table(players)
        self.pot = Pot(5, 10)

        self.pot.add(self.table.dealingTo, self.table.smallBlind)
        self.table.dealingTo.yourGo(list(self.pot.transactions))

        self.table.nextPlayer()

        self.pot.add(self.table.dealingTo, self.table.bigBlind)
        self.table.dealingTo.yourGo(list(self.pot.transactions))

        self.table.nextPlayer()

        self.table.dealingTo.yourGo(list(self.pot.transactions))

    def __on_PlayerResponse(self, sender, bet):
        
        if self.__outOfTurn(sender):
            self.__kickOut(sender)
        
        if bet < self.pot.getMinimumBet(sender):
            self.__kickOut(sender)

        self.pot.add(sender, bet)
        self.table.nextPlayer()
        self.table.dealingTo.yourGo(self.pot.transactions)

        self.evt_handFinished.fire(self, None)

    def __outOfTurn(self, sender):
        return sender != self.table.dealingTo

    def __kickOut(self, sender):
        sender.outOfGame()
        self.table.remove(sender)

class Table(object):
    """players sit around this and get dealt to in order"""
    def __init__(self, players):
        self.bigBlind = 10
        self.smallBlind = 5
        self.players = players
        self.dealingToPosition = 0
        self.dealingTo = self.players[self.dealingToPosition]

    def nextPlayer(self):
        self.dealingToPosition += 1

        if self.dealingToPosition >= len(self.players):
            self.dealingToPosition = 0

        self.dealingTo = self.players[self.dealingToPosition]

    def remove(self, player):
        self.players = filter(lambda x: x != player, self.players)

class Pot(object):

    def __init__(self, smallBlind, bigBlind):
        self.minimumBet = 0
        self.smallBlind = smallBlind 
        self.bigBlind = bigBlind 
        self.transactions = []

    def add(self, player, amount):
        self.minimumBet = amount
        
        self.transactions.append((player.name, amount))

    def getTotal(self, player = None):

        txns = filter(lambda x: x[0] == player.name, self.transactions) if player else self.transactions

        return sum(map(lambda x: x[1], txns))

    def getMinimumBet(self, player):
        return self.minimumBet - self.getTotal(player)

