from Xmpp import XmppMessenger
import time
import sys


class DumbPlayer(object):
    """docstring for DumbPlayer"""
    def __init__(self, jid, password):
        self.jid = jid
        self.password = password
        self.messenger = XmppMessenger(jid, password)
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.messenger.listen('localhost', 5222)
        self.messenger.sendMessage('dealer@pokerchat', 'JOIN')
        self.chips = 0
        self.cards = []
        self.action = {'GO': self.makeBet,
                       'BET': self.recordBet,
                       'CARD': self.acceptCard,
                       'WON': self.recordWinnings,
                       'DEALING': self.initialiseHand,
                       'CHIPS': self.acceptChips}

    def on_messageReceived(self, sender, msg):
        args = msg[1].split(' ')
        self.action[args[0]](args[1:])

    def acceptChips(self, args):
        self.chips = int(args[0])

    def initialiseHand(self, args):
        self.bets = dict(zip(args, [0 for player in args]))
        print 'Chips', self.chips

    def recordWinnings(self, args):
        winner = args[0]
        loser = args[1]
        amount = int(args[2])

        if self.jid == winner:
            self.chips += amount

        if self.jid == loser:
            self.chips[loser] -= amount

    def makeBet(self, args):
        self.messenger.sendMessage('dealer@pokerchat', self.minBet())

    def recordBet(self, args):
        player = args[0]
        amount = int(args[1])
        self.bets[player] += amount

    def acceptCard(self, args):
        cards = [(card[0:-1], card[-1]) for card in args]
        self.cards = self.cards + cards

    def minBet(self):

        highest = max([self.bets[k] for k in self.bets])
        myContribution = self.bets[self.jid]

        bet = min(max(highest - myContribution, 100), self.chips)

        self.chips -= bet

        return bet

player = DumbPlayer(sys.argv[1], sys.argv[2])

time.sleep(999999)
