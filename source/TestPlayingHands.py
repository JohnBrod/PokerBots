import unittest
from texasHoldEm import PlaysHand
from texasHoldEm import InteractsWithPlayers
from texasHoldEm import Card
from FakeMessaging import StubMessenger


class testA_DealingCardsAndTakingBets(unittest.TestCase):

    def onDone(self, sender, args=None):
        self._done = True

    def setUp(self):
        print 'Dealing cards and taking bets,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.p1 = inter.players[0]
        self.p2 = inter.players[1]

        self.ph = PlaysHand(inter)
        self._done = False
        self.ph.evt_done += self.onDone

    def testA_dealEachPlayerSomeCardsFirst(self):
        '''should deal each player some cards first'''
        self.ph.start()

        expected = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(expected, self.msngr.cardMessages)
        self.assertEqual(2, len(self.p1._cards))
        self.assertEqual(2, len(self.p2._cards))

    def testB_startsBettingWithFirstPlayerAtTheTable(self):
        '''starts betting with the first player at the table'''
        self.ph.start()

        self.assertEqual(('p1', 'GO'), self.msngr.lastMessage)

    def testC_dealsTheMoreCardsAfterSomeBets(self):
        '''deals more cards after some bets'''
        self.msngr.bet('p1', 10).bet('p2', 10)
        self.ph.start()

        expected = [('p1', 'CARD'), ('p2', 'CARD'), 'CARD']
        self.assertEqual(expected, self.msngr.cardMessages)
        self.assertEqual(5, len(self.p1._cards))
        self.assertEqual(5, len(self.p2._cards))

    def testD_continuesBettingWithTheLastToRaise(self):
        '''continues betting with the last to raise'''
        self.msngr.bet('p1', 0).bet('p2', 100).bet('p1', 100)
        self.ph.start()

        self.assertEqual(('p2', 'GO'), self.msngr.lastMessage)

    def testG_shouldTakeOldCardsFromPlayersBeforehand(self):
        '''should take old cards from players beforehand'''
        self.p1.cards([Card(1, 'H')])
        self.p2.cards([Card(2, 'H')])
        self.ph.start()

        self.assertEqual(2, len(self.p1._cards))
        self.assertEqual(2, len(self.p2._cards))
        expected = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(expected, self.msngr.cardMessages)

    def testH_announceThatItIsDone(self):
        '''announce that it is done'''
        self.msngr.bet('p1', 10).bet('p2', 0)
        self.ph.start()

        self.assertTrue(self._done)

    def assertEndsWith(self, lookFor, atEndOf):
        failMessage = 'Search items greater than search area'
        self.assertTrue(len(lookFor) <= len(atEndOf), failMessage)

        atEndOf = atEndOf[-len(lookFor):]

        self.assertEqual(lookFor, atEndOf)


class testB_WhenHandIsDone(unittest.TestCase):

    def onDone(self, sender, args=None):
        self._done = True

    def setUp(self):
        print 'Rounds of cards and betting,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.p1 = inter.players[0]
        self.p2 = inter.players[1]

        self.ph = PlaysHand(inter)
        self.ph.evt_done += self._onDone
        self._done = False

        self.msngr.bet('p1', 10).bet('p2', 10)
        self.msngr.bet('p1', 10).bet('p2', 10)
        self.msngr.bet('p1', 10).bet('p2', 10)
        self.msngr.bet('p1', 10).bet('p2', 10)

    def _onDone(self, sender, args):
        self._done = True

    def testA_announceThatItIsDone(self):
        '''announce that it is done'''
        self.ph.start()

        self.assertTrue(self._done)

    def testB_shouldDistributeTheWinnings(self):
        '''should say when all cards are dealt'''
        self.ph.start()

        self.assertTrue(len(self.msngr.wonMessages) > 0)


class testD_WhenDownToOnePlayer(unittest.TestCase):

    def onDone(self, sender, args=None):
        self._done = True

    def setUp(self):
        print 'When down to one player,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.ph = PlaysHand(inter)
        self._done = False
        self.ph.evt_done += self.onDone

    def testA_announceThatItIsDone(self):
        '''announce that it is done'''
        self.msngr.bet('p1', 10).bet('p2', 0)
        self.ph.start()

        self.assertTrue(self._done)

    def testB_noMoreCardsAreDealt(self):
        '''no more cards are dealt'''
        self.msngr.bet('p1', 10).bet('p2', 0)
        self.ph.start()

        privateCards = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(privateCards, self.msngr.cardMessages)


if __name__ == "__main__":
    unittest.main()
