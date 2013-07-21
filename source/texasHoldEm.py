
class Dealer(object):
    """deals a hand to players"""
    def __init__(self):
        pass

    def deal(self, players):
        for player in players:
            player.response += self.onPlayerResponse

        self.table = Table(players)
        self.pot = Pot()

        self.table.dealingTo.yourGo(self.pot.getTotal(), self.table.smallBlind)

    def onPlayerResponse(self, sender, bet):
        
        if sender != self.table.dealingTo:
            sender.outOfGame()
            self.table.players = filter(lambda player: player != sender, self.table.players)

        self.pot.add(sender, bet)
        self.table.nextPlayer()
        self.table.dealingTo.yourGo(self.pot.getTotal(), self.table.bigBlind - self.pot.getTotal(self.table.dealingTo))

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

        if self.dealingToPosition == len(self.players):
            self.dealingToPosition = 0

        self.dealingTo = self.players[self.dealingToPosition]

class Pot(object):

    def __init__(self):
        self.total = 0
        self.contributions = {}

    def add(self, player, amount):
        if player not in self.contributions:
            self.contributions[player.name] = []
        
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