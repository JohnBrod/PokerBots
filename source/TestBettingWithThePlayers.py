from theHouse import PlayerProxy
import unittest
from texasHoldEm import TakesBets
from FakeMessaging import StubMessenger


class testA_TellingThePlayersToBet(unittest.TestCase):

    def setUp(self):
        print 'Telling the players to bet,', self.shortDescription()

    def testA_tellTheFirstPlayerToTakeTheirGo(self):
        '''tell the first player to take their go'''
        p1 = createPlayer('p1', 100, ['any cards'])

        msngr = StubMessenger()
        tb = TakesBets(msngr)

        tb.fromPlayers([p1])

        self.assertEqual(('p1', 'GO'), msngr.lastMessage)

    def testB_tellTheSecondPlayerToTakeTheirGo(self):
        '''tell the second player to take their go'''
        p1 = createPlayer('p1', 100, ['any cards'])
        p2 = createPlayer('p2', 100, ['any cards'])

        msngr = StubMessenger().bet(p1, 10)
        tb = TakesBets(msngr)

        tb.fromPlayers([p1, p2])

        self.assertEqual(('p2', 'GO'), msngr.lastMessage)

    def testC_backToFirstPlayerAfterTheLast(self):
        '''moves back to the first player after the last'''
        p1 = createPlayer('p1', 100, ['any cards'])
        p2 = createPlayer('p2', 100, ['any cards'])

        msngr = StubMessenger().bet(p1, 10).bet(p2, 20)
        tb = TakesBets(msngr)

        tb.fromPlayers([p1, p2])

        self.assertEqual(('p1', 'GO'), msngr.lastMessage)

    def testD_skipsPlayerThatHasNoCards(self):
        '''skips player that does not have cards'''
        p1 = createPlayer('p1', 100, [])
        p2 = createPlayer('p2', 100, ['any cards'])

        msngr = StubMessenger()
        tb = TakesBets(msngr)

        tb.fromPlayers([p1, p2])

        self.assertEqual(('p2', 'GO'), msngr.lastMessage)


class testDecidingWhenAllBetsAreTaken(unittest.TestCase):

    def onBetsTaken(self, sender, args=None):
        self.betsTaken = True

    def setUp(self):
        print 'deciding when all bets are taken,', self.shortDescription()
        self.betsTaken = False

    def testA_takenIfBetIsCalledByAll(self):
        '''not if a player has raised'''
        p1 = createPlayer('p1', 20, ['any cards'])
        p2 = createPlayer('p2', 20, ['any cards'])

        msngr = StubMessenger().bet(p1, 10).bet(p2, 10)
        tb = TakesBets(msngr)
        tb.evt_betsTaken += self.onBetsTaken

        tb.fromPlayers([p1, p2])

        self.assertTrue(self.betsTaken)

    def testB_notIfPlayerHasRaised(self):
        '''not if a player has raised'''
        p1 = createPlayer('p1', 20, ['any cards'])
        p2 = createPlayer('p2', 20, ['any cards'])

        msngr = StubMessenger().bet(p1, 10).bet(p2, 20)
        tb = TakesBets(msngr)
        tb.evt_betsTaken += self.onBetsTaken

        tb.fromPlayers([p1, p2])

        self.assertFalse(self.betsTaken)

    def testC_doneIfRaiseIsCalled(self):
        '''done if raise is called by all others'''
        p1 = createPlayer('p1', 20, ['any cards'])
        p2 = createPlayer('p2', 20, ['any cards'])

        msngr = StubMessenger().bet(p1, 10).bet(p2, 20).bet(p1, 10)
        tb = TakesBets(msngr)
        tb.evt_betsTaken += self.onBetsTaken

        tb.fromPlayers([p1, p2])

        self.assertTrue(self.betsTaken)

    def testD_doneWhenOnlyOnePlayerLeftWithCards(self):
        '''done when only one player left with cards'''
        p1 = createPlayer('p1', 20, ['any cards'])
        p2 = createPlayer('p2', 20, [])

        msngr = StubMessenger().bet(p1, 10)
        tb = TakesBets(msngr)
        tb.evt_betsTaken += self.onBetsTaken

        tb.fromPlayers([p1, p2])

        self.assertTrue(self.betsTaken)

    def testE_doneWhenNoPlayerHasChipsLeft(self):
        '''done when only one player has chips left'''
        p1 = createPlayer('p1', 10, ['any cards'])
        p2 = createPlayer('p2', 20, ['any cards'])

        msngr = StubMessenger().bet(p1, 10).bet(p2, 20)
        tb = TakesBets(msngr)
        tb.evt_betsTaken += self.onBetsTaken

        tb.fromPlayers([p1, p2])

        self.assertTrue(self.betsTaken)

    def testF_doneImmediatelyIfNoneOfThePlayersHadChips(self):
        '''done immediately of none of the players had chips'''
        p1 = createPlayer('p1', 0, ['any cards'])
        p2 = createPlayer('p2', 0, ['any cards'])

        tb = TakesBets(StubMessenger())
        tb.evt_betsTaken += self.onBetsTaken

        tb.fromPlayers([p1, p2])

        self.assertTrue(self.betsTaken)


class testPlayerFolding(unittest.TestCase):

    def setUp(self):
        print 'A player folding,', self.shortDescription()

    def testA_playerFoldsByBettingLessThanMinimum(self):
        '''a player folds by betting less than minimum'''

        p1 = createPlayer('p1', 2, ['any cards'])
        p2 = createPlayer('p2', 2, ['any cards'])

        msngr = StubMessenger().bet(p1, 2).bet(p2, 0)
        tb = TakesBets(msngr)

        tb.fromPlayers([p1, p2])

        self.assertTrue(('p2', 'OUT you folded') in msngr.sentMessages)

    def testB_takePlayersCards(self):
        '''take the players cards'''

        p1 = createPlayer('p1', 2, ['any cards'])
        p2 = createPlayer('p2', 2, ['any cards'])

        msngr = StubMessenger().bet(p1, 2).bet(p2, 0)
        tb = TakesBets(msngr)

        tb.fromPlayers([p1, p2])

        self.assertEqual(p2._cards, [])


class testKickingOutPlayer(unittest.TestCase):

    def setUp(self):
        print 'Kick out a player,', self.shortDescription()

    def testA_playerBetsMoreThanTheyHave(self):
        '''when a player bets more than they have'''
        p1 = createPlayer('p1', 1, ['any cards'])
        p2 = createPlayer('p2', 1, ['any cards'])

        msngr = StubMessenger().bet(p1, 2)
        tb = TakesBets(msngr)

        tb.fromPlayers([p1, p2])

        outMessage = 'OUT you bet 2, you have only 1 chips avaiable'
        self.assertTrue(('p1', outMessage) in msngr.sentMessages)
        self.assertEqual(p1.chips, 0)
        self.assertEqual(p1._cards, [])


def createPlayer(name, chips=0, cards=[]):
    player = PlayerProxy(name, chips)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    player.cards(cards)

    return player


if __name__ == "__main__":
    unittest.main()
