import unittest
from texasHoldEm import InteractsWithPlayers
from FakeMessaging import StubMessenger


class testA_PlayerJoining(unittest.TestCase):

    def setUp(self):
        print 'Player joining,', self.shortDescription()

        self.msngr = StubMessenger()
        self.interactsWithPlayers = InteractsWithPlayers(self.msngr)

        self.msngr.join('player')

        self.player = self.interactsWithPlayers.players[0]

    def testA_thePlayerReceivesChips(self):
        '''the player receives chips'''
        self.assertEquals(1000, self.player.chips)

    def testB_anAcknowledgementIsSent(self):
        '''an acknowledgement is sent to the player'''
        self.assertEquals(('player', 'CHIPS 1000'), self.msngr.lastMessage)


class testB_SamePlayerJoiningTwice(unittest.TestCase):

    def setUp(self):
        print 'Same player joining twice,', self.shortDescription()

        self.msngr = StubMessenger()
        self.interactsWithPlayers = InteractsWithPlayers(self.msngr)

        self.msngr.join('player')
        self.msngr.join('player')

    def testA_thePlayerIsOnlyRegisteredOnce(self):
        '''the player is only registered once'''
        self.assertEquals(1, len(self.interactsWithPlayers.players))


if __name__ == "__main__":
    unittest.main()
