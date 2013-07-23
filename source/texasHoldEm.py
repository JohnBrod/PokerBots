
class Dealer(object):
    """deals a hand to players"""
    def __init__(self):
        pass

    def deal(self, players):
        for player in players:
            player.response += self.onPlayerResponse

        self.table = Table(players)
        self.pot = Pot(5, 10)

        self.table.dealingTo.smallBlind(self.table.smallBlind)
        self.pot.add(self.table.dealingTo, self.table.smallBlind)

        self.table.nextPlayer()

        self.table.dealingTo.bigBlind(self.table.bigBlind)
        self.pot.add(self.table.dealingTo, self.table.bigBlind)

        self.table.nextPlayer()

        self.table.dealingTo.yourGo(self.pot.getMinimumBet(self.table.dealingTo))

    def onPlayerResponse(self, sender, bet):
        
        if self.__outOfTurn(sender):
            self.__kickOut(sender)
        
        if bet < self.pot.getMinimumBet(sender):
            self.__kickOut(sender)

        self.pot.add(sender, bet)
        self.table.nextPlayer()
        self.table.dealingTo.yourGo(self.pot.getMinimumBet(self.table.dealingTo))

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
        self.contributions = {}
        self.smallBlind = smallBlind 
        self.bigBlind = bigBlind 

    def add(self, player, amount):
        if player not in self.contributions:
            self.contributions[player.name] = []

        self.minimumBet = amount
        
        self.contributions[player.name].append(amount)

    def getTotal(self, player = None):

        if player:
            if player.name in self.contributions:
                return sum(self.contributions[player.name])
            else:
                return 0

        total = 0
        for v in self.contributions.iterkeys():
            total += sum(self.contributions[v])
                
        return total

    def getMinimumBet(self, player):
        return self.minimumBet - self.getTotal(player)

