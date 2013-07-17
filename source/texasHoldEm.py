
class Dealer(object):
    """deals a hand to players"""
    def __init__(self):
        pass

    def deal(self, players):
        for player in players:
            player.response += self.onPlayerResponse

        self.table = Table(players)

        self.table.dealingTo.yourGo()

    def onPlayerResponse(self, sender, message):
        
        if sender != self.table.dealingTo:
            sender.outOfGame()
            self.table.players = filter(lambda player: player != sender, self.table.players)

        self.table.nextPlayer()
        self.table.dealingTo.yourGo()

class Table(object):
    """players sit around this and get dealt to in order"""
    def __init__(self, players):
        self.players = players
        self.dealingToPosition = 0
        self.dealingTo = self.players[self.dealingToPosition]

    def nextPlayer(self):
        self.dealingToPosition += 1

        if self.dealingToPosition == len(self.players):
            self.dealingToPosition = 0

        self.dealingTo = self.players[self.dealingToPosition]
