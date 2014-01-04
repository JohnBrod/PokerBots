from texasHoldEm import Card
from texasHoldEm import InteractsWithPlayers
from texasHoldEm import DistributesWinnings
import unittest
from FakeMessaging import StubMessenger


def cards(items):
    return map(lambda x: Card(int(x[0:-1]), x[-1]), items.split(','))


class testA_GivingWinnersTheirChips(unittest.TestCase):

    def setUp(self):
        print 'Giving winners their chips,', self.shortDescription()
        self.msngr = StubMessenger()
        self.interact = InteractsWithPlayers(self.msngr, chips=1000)
        self.distribute = DistributesWinnings(self.interact)

        self.msngr.join('winner')
        self.msngr.join('loser')

        self.winner = self.interact.players[0]
        self.loser = self.interact.players[1]

    def testA_withoutSidePotsTheTopRankedPlayerWinsAll(self):
        '''without side pots the top ranked player wins all'''
        self.winner.cards(cards('14C,14D,4S,3H,2C'))
        self.loser.cards(cards('13S,9D,5C,3D,2C'))

        self.winner.bet(5)
        self.loser.bet(5)

        self.distribute.toPlayers()

        self.assertEqual(self.winner.chips, 1005)
        self.assertEqual(self.loser.chips, 995)

    def testB_theTopRankedPlayerCannotWinMoreThanAllowed(self):
        '''if a player is only in a side pot, that is all they can win'''
        self.winner.cards(cards('14C,14D,4S,3H,2C'))
        self.loser.cards(cards('13S,9D,5C,3D,2C'))

        self.winner.bet(5)
        self.loser.bet(10)

        self.distribute.toPlayers()

        self.assertEqual(self.winner.chips, 1005)
        self.assertEqual(self.loser.chips, 995)

    def testC_splittingThePot(self):
        '''players will split the pot if they are ranked the same'''
        self.winner.cards(cards('14C,14D,4S,3H,2C'))
        self.loser.cards(cards('14C,14D,4S,3H,2C'))

        self.winner.bet(5)
        self.loser.bet(5)

        self.distribute.toPlayers()

        self.assertEqual(self.winner.chips, 1000)
        self.assertEqual(self.loser.chips, 1000)


class testB_AnnouncingTheWinners(unittest.TestCase):

    def setUp(self):
        print 'Announcing the winners,', self.shortDescription()
        self.msngr = StubMessenger()
        self.interact = InteractsWithPlayers(self.msngr, chips=1000)
        self.distribute = DistributesWinnings(self.interact)

        self.msngr.join('winner')
        self.msngr.join('loser')

        self.winner = self.interact.players[0]
        self.loser = self.interact.players[1]

    def testA_shouldAnnounceTheWinners(self):
        '''should announce the winners of the game'''

        self.winner.cards(cards('14C,14D,4S,3H,2C'))
        self.loser.cards(cards('13S,9D,5C,3D,2C'))

        self.winner.bet(5)
        self.loser.bet(5)

        self.distribute.toPlayers()

        self.assertEqual(self.msngr.wonMessages,
                         ['WON winner loser 5 14C,14D,4S,3H,2C pairHand',
                          'WON winner winner 5 14C,14D,4S,3H,2C pairHand',
                          'WON loser winner 0 13S,9D,5C,3D,2C highestCard',
                          'WON loser loser 0 13S,9D,5C,3D,2C highestCard'])

    def testB_shouldOnlyDistributeToPlayersInTheGame(self):
        '''should only distribute the winnings to players in the game'''
        self.winner.cards(cards('14C,14D,4S,3H,2C'))
        self.winner.cards([])  # only in game players have cards

        self.winner.bet(5)

        self.distribute.toPlayers()

        self.assertEqual(self.msngr.wonMessages,
                         ['WON winner loser 0 14C,14D,4S,3H,2C pairHand',
                          'WON winner winner 5 14C,14D,4S,3H,2C pairHand'])


if __name__ == "__main__":
    unittest.main()
