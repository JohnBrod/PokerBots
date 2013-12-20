import unittest
from theHouse import PlayerProxy
from texasHoldEm import HostsGame
from FakeMessaging import StubMessenger
from mock import MagicMock


def createPlayer(name, chips, cards=[]):
    player = PlayerProxy(name, chips)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    player.cards(cards)
    return player


class testA_StartingTheTournament(unittest.TestCase):

    def setUp(self):
        print 'Starting the tournament,', self.shortDescription()

    def testA_gameIsBeingPlayer(self):
        '''a game is being played'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        dealer = HostsGame(msngr)
        dealer.start([p1, p2])

        self.assertTrue(dealer.playing)

    def testB_thePlayersAreAnnounced(self):
        '''the players are announced'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        HostsGame(msngr).start([p1, p2])

        self.assertEqual(msngr.dealingMessages, ['DEALING p1 p2'])

    def testC_cardsAreDealt(self):
        '''cards are dealt'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        HostsGame(msngr).start([p1, p2])

        self.assertEqual(msngr.cardMessages, [('p1', 'CARD'), ('p2', 'CARD')])

    def testD_betsAreBeingTaken(self):
        '''bets are being taken'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        HostsGame(msngr).start([p1, p2])

        self.assertEqual(msngr.goMessages, [('p1', 'GO')])


class testB_RoundOfBettingFinished(unittest.TestCase):

    def setUp(self):
        print 'When a round of betting is finished,', self.shortDescription()

    def testA_dealsTheNextRoundAndMoreBetsAreTaken(self):
        '''the next round is dealt and more bets are taken'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger().bet(p1, 10).bet(p2, 10)

        HostsGame(msngr).start([p1, p2])

        self.assertEqual(msngr.allMessages, ['DEALING p1 p2',
                                             ('p1', 'CARD'), ('p2', 'CARD'),
                                             ('p1', 'GO'), 'BET p1 10',
                                             ('p2', 'GO'), 'BET p2 10',
                                             'CARD',
                                             ('p1', 'GO')])


class testC_FinishingTheHand(unittest.TestCase):

    def setUp(self):
        print 'Finishing the hand,', self.shortDescription()

    def testA_distributeTheWinnings(self):
        '''distribute the winnings'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        p1.deposit = MagicMock()
        p2.deposit = MagicMock()

        msngr.bet(p1, 10).bet(p2, 10)  # private
        msngr.bet(p1, 10).bet(p2, 10)  # flop
        msngr.bet(p1, 10).bet(p2, 10)  # turn
        msngr.bet(p1, 10).bet(p2, 10)  # river

        HostsGame(msngr).start([p1, p2])

        self.assertTrue(p1.deposit.called)
        self.assertTrue(p2.deposit.called)

    def testB_announceTheWinner(self):
        '''announce the winner'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        msngr.bet(p1, 10).bet(p2, 10)  # private
        msngr.bet(p1, 10).bet(p2, 10)  # flop
        msngr.bet(p1, 10).bet(p2, 10)  # turn
        msngr.bet(p1, 10).bet(p2, 10)  # river

        HostsGame(msngr).start([p1, p2])

        self.assertTrue(msngr.wonMessages)

    def testC_rotateTheButtonAndStartTheNextHand(self):
        '''rotate the button and start the next hand'''

        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        msngr = StubMessenger()

        msngr.bet(p1, 10).bet(p2, 10)  # private
        msngr.bet(p1, 10).bet(p2, 10)  # flop
        msngr.bet(p1, 10).bet(p2, 10)  # turn
        msngr.bet(p1, 10).bet(p2, 10)  # river

        HostsGame(msngr).start([p1, p2])

        twoGames = ['DEALING p1 p2', 'DEALING p2 p1']
        self.assertEqual(msngr.dealingMessages, twoGames)


class testD_FinishingTheTournament(unittest.TestCase):

    def setUp(self):
        print 'Finishing the tournament,', self.shortDescription()

    def testA_dealerIsNoLongerPlaying(self):
        '''the dealer is no longer playing'''

        p1 = createPlayer('p1', 40)
        p2 = createPlayer('p2', 40)

        msngr = StubMessenger()
        msngr.bet(p1, 10).bet(p2, 10)  # private
        msngr.bet(p1, 10).bet(p2, 10)  # flop
        msngr.bet(p1, 10).bet(p2, 10)  # turn
        msngr.bet(p1, 10).bet(p2, 10)  # river

        dealer = HostsGame(msngr)
        dealer.start([p1, p2])

        self.assertEqual(False, dealer.playing, 'Will fail if a draw occurs')

    def testB_noMoreHandsAreDealt(self):
        '''no more hands are dealt'''

        p1 = createPlayer('p1', 40)
        p2 = createPlayer('p2', 40)

        msngr = StubMessenger()
        msngr.bet(p1, 10).bet(p2, 10)  # private
        msngr.bet(p1, 10).bet(p2, 10)  # flop
        msngr.bet(p1, 10).bet(p2, 10)  # turn
        msngr.bet(p1, 10).bet(p2, 10)  # river

        dealer = HostsGame(msngr)
        dealer.start([p1, p2])

        failMessage = 'Will fail if a draw occurs'
        self.assertEqual(msngr.dealingMessages, ['DEALING p1 p2'], failMessage)


if __name__ == "__main__":
    unittest.main()
