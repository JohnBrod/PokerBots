import unittest
from texasHoldEm import DealsTexasHoldEm
from texasHoldEm import InteractsWithPlayers
from FakeMessaging import StubMessenger


class testA_DealingCardsForTexasHoldEm(unittest.TestCase):

    def onDone(self, sender, args=None):
        self._done = True

    def setUp(self):
        print 'Dealing cards for texas hold em,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.p1 = inter.players[0]
        self.p2 = inter.players[1]

        self.txh = DealsTexasHoldEm(inter)

    def testA_dealEachPlayerPrivateCardsFirst(self):
        '''should deal each player private cards first'''
        self.txh.start()

        self.assertEqual(2, len(self.p1._cards))
        self.assertEqual(2, len(self.p2._cards))
        expected = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(expected, self.msngr.cardMessages)

    def testB_dealsTheFlopCardsNext(self):
        '''deals the flop cards next'''
        self.txh.start()
        self.txh.next()

        self.assertEqual(5, len(self.p1._cards))
        self.assertEqual(5, len(self.p2._cards))
        expected = [('p1', 'CARD'), ('p2', 'CARD'), 'CARD']
        self.assertEqual(expected, self.msngr.cardMessages)

    def testC_dealsTheRiverCard(self):
        '''deals the river card'''
        self.txh.start()
        self.txh.next()
        self.txh.next()

        self.assertEqual(6, len(self.p1._cards))
        self.assertEqual(6, len(self.p2._cards))
        expected = [('p1', 'CARD'), ('p2', 'CARD'), 'CARD', 'CARD']
        self.assertEqual(expected, self.msngr.cardMessages)

    def testD_dealsTheTurnCard(self):
        '''deals the turn card'''
        self.txh.start()
        self.txh.next()
        self.txh.next()
        self.txh.next()

        self.assertEqual(7, len(self.p1._cards))
        self.assertEqual(7, len(self.p2._cards))
        expected = [('p1', 'CARD'), ('p2', 'CARD'), 'CARD', 'CARD', 'CARD']
        self.assertEqual(expected, self.msngr.cardMessages)

    def testE_noMoreCardsAfterThat(self):
        '''no more cards after that'''
        self.txh.start()
        self.txh.next()
        self.txh.next()
        self.txh.next()

        self.assertFalse(self.txh.more())


class testC_DealingTheRemainingCards(unittest.TestCase):

    def onDone(self, sender, args=None):
        self._done = True

    def setUp(self):
        print 'Dealing the remaining cards,', self.shortDescription()
        self.msngr = StubMessenger()
        inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')
        self.msngr.join('p3')

        self.p1 = inter.players[0]
        self.p2 = inter.players[1]
        self.p3 = inter.players[2]

        self.txh = DealsTexasHoldEm(inter)

    def testA_allPlayersAreOutOfChips(self):
        '''when all players are out of chips'''
        self.p1.chips = 0
        self.p2.chips = 0
        self.p3.chips = 0

        self.txh.start()

        allDealt = [('p1', 'CARD'), ('p2', 'CARD'),
                    ('p3', 'CARD'),
                    'CARD', 'CARD', 'CARD']
        self.assertEqual(allDealt, self.msngr.cardMessages)

    def testB_allBarOnePlayersAreOutOfChips(self):
        '''when all players bar one are out of chips'''
        self.p2.chips = 0
        self.p3.chips = 0

        self.txh.start()

        allDealt = [('p1', 'CARD'), ('p2', 'CARD'),
                    ('p3', 'CARD'),
                    'CARD', 'CARD', 'CARD']
        self.assertEqual(allDealt, self.msngr.cardMessages)


if __name__ == "__main__":
    unittest.main()
