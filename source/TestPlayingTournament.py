import unittest
from texasHoldEm import PlaysTournament
from texasHoldEm import InteractsWithPlayers
from FakeMessaging import StubMessenger
from EventHandling import Event


class testA_StartingTheTournament(unittest.TestCase):

    def setUp(self):
        print 'Starting the tournament,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        pt = PlaysTournament(inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        pt.start()

    def testA_thePlayersAreAnnounced(self):
        '''the players are announced'''
        self.assertEqual(self.msngr.dealingMessages, ['DEALING p1 p2'])

    def testB_cardsAreDealt(self):
        '''the cards are dealt'''
        privateCards = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(privateCards, self.msngr.cardMessages)

    def testC_betsAreBeingTaken(self):
        '''bets are being taken'''
        self.assertEqual(('p1', 'GO'), self.msngr.lastMessage)


class testB_AfterHandIsPlayed(unittest.TestCase):

    def setUp(self):
        print 'After a hand is played,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        pt = PlaysTournament(inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        self.msngr.bet('p1', 100)
        self.msngr.bet('p2', 0)

        pt.start()

    def testA_rotateTheButtonAndStartTheNextHand(self):
        '''rotate the button and start the next hand'''
        twoGames = ['DEALING p1 p2', 'DEALING p2 p1']
        self.assertEqual(self.msngr.dealingMessages, twoGames)

    def testB_cardsAreDealt(self):
        '''the cards are dealt'''
        privateCards = [('p2', 'CARD'), ('p1', 'CARD')]

        self.assertEndsWith(privateCards, self.msngr.cardMessages)

    def testC_betsAreBeingTaken(self):
        '''bets are being taken'''
        self.assertEqual(('p2', 'GO'), self.msngr.lastMessage)

    def assertEndsWith(self, lookFor, atEndOf):
        failMessage = 'Search items greater than search area'
        self.assertTrue(len(lookFor) <= len(atEndOf), failMessage)

        atEndOf = atEndOf[-len(lookFor):]

        self.assertEqual(lookFor, atEndOf)


class testC_FinishingTheTournament(unittest.TestCase):

    def setUp(self):
        description = 'Finishing the tournament,'
        print description, self.shortDescription()

        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        pt = PlaysTournament(inter)
        pt._playsHand = FinishAfterFirstHand(inter)
        pt._playsHand.evt_done += pt._onHandDone
        self._done = False

        self.msngr.join('p1')
        self.msngr.join('p2')

        pt.evt_done += self._onTournamentFinished
        pt.start()

    def _onTournamentFinished(self, sender=None, args=None):
        self._done = True

    def testA_theWinnerIsAnnounced(self):
        '''the winner is announced'''
        self.assertTrue('WINNER' in self.msngr.broadcastMessages)

    def testB_signalsThatItIsFinished(self):
        '''signals that it is finished'''
        self.assertTrue(self._done)

    def testC_doesNotDealAnyMoreHands(self):
        '''does not deal any more hands'''
        self.assertTrue(self._done)


class FinishAfterFirstHand(object):
    def __init__(self, interacts):
        '''finishes the tournament by giving one player all the chips'''
        self.interacts = interacts
        self.evt_done = Event()

    def start(self):
        self.interacts.players[1].chips = 0
        self.evt_done(self, None)


if __name__ == "__main__":
    unittest.main()
