
class Player(object):
    """acts as a proxy to the real player"""
    def __init__(self, jid, messenger):
        self.jid = jid
        self.messenger = messenger
        self.cash = 0

    def bet(self, amount):
        self.cash = 0

    def privateCards(self, cards):
        self.messenger.sendMessage(self.jid, 'Private Cards ' + cards)
        # wait for response - response is to a public group that contains the dealer and players

    def communityCards(self, cards):
        self.messenger.sendMessage(self.jid, 'Community Cards ' + cards)

    def flop(self, card):
        self.messenger.sendMessage(self.jid, 'Flop ' + card)
        
    def turn(self, card):
        self.messenger.sendMessage(self.jid, 'Turn ' + card)
        
    def river(self, card):
        self.messenger.sendMessage(self.jid, 'River ' + card)

    def handResult(self, result):
        self.messenger.sendMessage(self.jid, 'Hand Result ' + result)

    def gameResult(self, result):
        self.messenger.sendMessage(self.jid, 'Game Result ' + result)

class Dealer(object):
    """deals a hand to players"""
    def __init__(self):
        pass

    def deal(self, table):
        for player in table:
            player.privateCards('anything')

        for player in table:
            player.communityCards('anything')

        for player in table:
            player.flop('anything')

        for player in table:
            player.turn('anything')

        for player in table:
            player.river('anything')

        for player in table:
            player.handResult('anything')
