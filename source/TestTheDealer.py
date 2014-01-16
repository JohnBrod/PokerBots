import unittest
from texasHoldEm import HostsGame
from texasHoldEm import InteractsWithPlayers
from FakeMessaging import StubMessenger
from mock import MagicMock


class testA_StartingTheTournament(unittest.TestCase):

    def setUp(self):
        print 'Starting the tournament,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.dealer = HostsGame(self.inter)
        self.msngr.join('p1')
        self.msngr.join('p2')
        self.dealer.start()

    def testA_gameIsBeingPlayed(self):
        '''a game is being played'''
        self.assertTrue(self.dealer.playing)

    def testB_thePlayersAreAnnounced(self):
        '''the players are announced'''
        self.assertEqual(self.msngr.dealingMessages, ['DEALING p1 p2'])

    def testC_cardsAreDealt(self):
        '''cards are dealt'''
        expected = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(self.msngr.cardMessages, expected)

    def testD_betsAreBeingTaken(self):
        '''bets are being taken'''
        self.assertEqual(self.msngr.goMessages, [('p1', 'GO')])


class testC_FinishingTheHand(unittest.TestCase):

    def setUp(self):
        print 'Finishing the hand,', self.shortDescription()

        self.msngr = StubMessenger()
        self.msngr.bet('p1', 10).bet('p2', 10)  # private
        self.msngr.bet('p1', 10).bet('p2', 10)  # flop
        self.msngr.bet('p1', 10).bet('p2', 10)  # turn
        self.msngr.bet('p1', 10).bet('p2', 10)  # river

        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        dealer = HostsGame(self.inter)

        for player in self.inter.players:
            player.deposit = MagicMock()

        dealer.start()

    def testA_distributeTheWinnings(self):
        for player in self.inter.players:
            self.assertTrue(player.deposit.called)

    def testB_announceTheWinner(self):
        '''announce the winner'''
        self.assertTrue(self.msngr.wonMessages)

    def testC_rotateTheButtonAndStartTheNextHand(self):
        '''rotate the button and start the next hand'''
        twoGames = ['DEALING p1 p2', 'DEALING p2 p1']
        self.assertEqual(self.msngr.dealingMessages, twoGames)


class testD_FinishingTheTournament(unittest.TestCase):

    def setUp(self):
        description = 'Finishing the tournament (tests will fail on draw),'
        print description, self.shortDescription()

        self.msngr = StubMessenger()
        self.msngr.bet('p1', 10).bet('p2', 10)  # private
        self.msngr.bet('p1', 10).bet('p2', 10)  # flop
        self.msngr.bet('p1', 10).bet('p2', 10)  # turn
        self.msngr.bet('p1', 10).bet('p2', 10)  # river

        self.inter = InteractsWithPlayers(self.msngr, chips=40)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.dealer = HostsGame(self.inter)
        self.dealer.start()

    def testA_theDealerIsNoLongerPlaying(self):
        '''finished if one player has all the chips'''
        self.assertEqual(False, self.dealer.playing)

    def testB_noMoreHandsAreDealt(self):
        '''no more hands are dealt'''
        self.assertEqual(self.msngr.dealingMessages, ['DEALING p1 p2'])

    def testC_theWinnerIsAnnounced(self):
        '''the winner is announced'''
        self.assertTrue('WINNER' in self.msngr.broadcastMessages)


if __name__ == "__main__":
    unittest.main()
