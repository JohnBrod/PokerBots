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
        p1 = createPlayer('p1', 100)
        p2 = createPlayer('p2', 100)

        self.msngr = StubMessenger()

        self.dealer = HostsGame(self.msngr)
        self.dealer.start([p1, p2])

    def testA_gameIsBeingPlayer(self):
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
        self.p1 = createPlayer('p1', 100)
        self.p2 = createPlayer('p2', 100)

        self.p1.deposit = MagicMock()
        self.p2.deposit = MagicMock()

        self.msngr = StubMessenger()
        self.msngr.bet(self.p1, 10).bet(self.p2, 10)  # private
        self.msngr.bet(self.p1, 10).bet(self.p2, 10)  # flop
        self.msngr.bet(self.p1, 10).bet(self.p2, 10)  # turn
        self.msngr.bet(self.p1, 10).bet(self.p2, 10)  # river

        HostsGame(self.msngr).start([self.p1, self.p2])

    def testA_distributeTheWinnings(self):
        '''distribute the winnings'''
        self.assertTrue(self.p1.deposit.called)
        self.assertTrue(self.p2.deposit.called)

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
        p1 = createPlayer('p1', 40)
        p2 = createPlayer('p2', 40)

        self.msngr = StubMessenger()
        self.msngr.bet(p1, 10).bet(p2, 10)  # private
        self.msngr.bet(p1, 10).bet(p2, 10)  # flop
        self.msngr.bet(p1, 10).bet(p2, 10)  # turn
        self.msngr.bet(p1, 10).bet(p2, 10)  # river

        self.dealer = HostsGame(self.msngr)
        self.dealer.start([p1, p2])

    def testA_finishedIfOnePlayerHasAllChips(self):
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
