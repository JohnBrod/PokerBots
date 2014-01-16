import unittest
from texasHoldEm import DealsCards
from texasHoldEm import InteractsWithPlayers
from Hands import Hand
from FakeMessaging import StubMessenger
from FakeMessaging import PredictableDeck


class testA_DealingCardsToPlayers(unittest.TestCase):

    def setUp(self):
        print 'Dealing cards to players,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.p1 = self.inter.players[0]
        self.p2 = self.inter.players[1]

        self.dealer = DealsCards(PredictableDeck(), self.inter)
        self.dealer.evt_cardsDealt += self._onCardsDealt
        self._cardsDealt = False

    def _onCardsDealt(self, sender, args):
        self._cardsDealt = True

    def testA_dealEachPlayerPrivateCardsFirst(self):
        '''should deal each player private cards first'''
        self.dealer.go()

        self.assertSequenceEqual([1, 2], self.p1._cards)
        self.assertSequenceEqual([3, 4], self.p2._cards)
        self.assertTrue(('p1', 'CARD') in self.msngr.sentMessages)
        self.assertTrue(('p2', 'CARD') in self.msngr.sentMessages)

    def testB_dealsTheFlopCards(self):
        '''deals the flop cards'''
        self.dealer.go()
        self.dealer.go()

        self.assertSequenceEqual([1, 2, 5, 6, 7], self.p1._cards)
        self.assertSequenceEqual([3, 4, 5, 6, 7], self.p2._cards)
        self.assertEqual(['CARD'], self.msngr.broadcastMessages)

    def testC_dealsTheRiverCard(self):
        '''deals the river card'''
        self.dealer.go()
        self.dealer.go()
        self.dealer.go()

        self.assertSequenceEqual([1, 2, 5, 6, 7, 8], self.p1._cards)
        self.assertSequenceEqual([3, 4, 5, 6, 7, 8], self.p2._cards)

        self.assertEqual(['CARD', 'CARD'], self.msngr.broadcastMessages)

    def testD_dealsTheTurnCard(self):
        '''deals the turn card'''
        self.dealer.go()
        self.dealer.go()
        self.dealer.go()
        self.dealer.go()

        self.assertSequenceEqual([1, 2, 5, 6, 7, 8, 9], self.p1._cards)
        self.assertSequenceEqual([3, 4, 5, 6, 7, 8, 9], self.p2._cards)

        cardDeals = ['CARD', 'CARD', 'CARD']
        self.assertEqual(cardDeals, self.msngr.broadcastMessages)

    def testE_shouldSayWhenAllCardsAreDealt(self):
        '''should say when all cards are dealt'''
        self.dealer.go()
        self.dealer.go()
        self.dealer.go()
        self.dealer.go()

        self.assertTrue(self._cardsDealt)

    def testF_shouldTakeCardsFromPlayersBeforeDealing(self):
        '''should take any cards the player may have before dealing'''
        self.assertEqual(self.p1.hand(), Hand([]))


class testB_WhenToDealTheRemainingCards(unittest.TestCase):

    def setUp(self):
        print 'When to deal the the remaining cards,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')
        self.msngr.join('p3')

        self.p1 = self.inter.players[0]
        self.p2 = self.inter.players[1]
        self.p3 = self.inter.players[2]

        self.dealer = DealsCards(PredictableDeck(), self.inter)

    def testA_allPlayersAreOutOfChips(self):
        '''when all players are out of chips'''
        self.p1.chips = 0
        self.p2.chips = 0
        self.p3.chips = 0

        self.dealer.go()

        allDealt = ['CARD', 'CARD', 'CARD']
        self.assertEqual(allDealt, self.msngr.broadcastMessages)

    def testB_allBarOnePlayersAreOutOfChips(self):
        '''when all players bar one are out of chips'''
        self.p2.chips = 0
        self.p3.chips = 0

        self.dealer.go()

        allDealt = ['CARD', 'CARD', 'CARD']
        self.assertEqual(allDealt, self.msngr.broadcastMessages)


class testD_WhenDownToOnePlayer(unittest.TestCase):

    def onCardsDealt(self, sender, args=None):
        self.cardsDealt = True

    def setUp(self):
        print 'When down to one player,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')

        self.p2 = self.inter.players[1]

        self.dealer = DealsCards(PredictableDeck(), self.inter)
        self.cardsDealt = False
        self.dealer.evt_cardsDealt += self.onCardsDealt

    def testA_announceThatCardsAreDealt(self):
        '''announce that cards are dealt'''
        self.dealer.go()
        self.p2.dropCards()
        self.dealer.go()

        self.assertTrue(self.cardsDealt)

    def testB_noMoreCardsAreDealt(self):
        '''no more cards are dealt'''
        self.dealer.go()
        self.p2.dropCards()
        self.dealer.go()

        privateCards = [('p1', 'CARD'), ('p2', 'CARD')]
        self.assertEqual(privateCards, self.msngr.cardMessages)


if __name__ == "__main__":
    unittest.main()
