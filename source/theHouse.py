import time
from EventHandling import Event

class Doorman(object):
    """greets players and passes their details onto the its boss"""
    def __init__(self, waitFor, messenger, cash):
        self.players = []
        self.cash = cash
        self.waitFor = waitFor
        self.messenger = messenger
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.evt_playerJoined = Event()

    def greetPlayers(self):
        time.sleep(self.waitFor)

        return self.players

    def on_messageReceived(self, sender, msg):
        if msg['type'] in ('normal', 'chat') and msg['body'].startswith('Player'):
            self.players.append(Player(msg['body'], self.messenger))
            self.evt_playerJoined.fire(self, msg['body'])
            self.messenger.sendMessage(msg['body'], 'Cash ' + str(self.cash))

class Player(object):
    """acts as a proxy to the real player"""
    def __init__(self, jid, messenger):
        self.jid = jid
        self.messenger = messenger

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

    def playHand(self, table):
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

class Casino(object):
    """Controls the flow of a game of poker"""
    def __init__(self, dealer, players):
        self.dealer = dealer
        self.players = players

    def play(self):
        self.dealer.playHand(self.players)

        for player in self.players:
            player.gameResult('anything')
