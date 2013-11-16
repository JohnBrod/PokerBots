import time
import unittest
import os
import sys
import logging
# these two lines do some freaky stuff so I can import from the parent director
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from Xmpp import XmppMessenger
from runningTheApp import FakePlayer
from runningTheApp import FakeAudience
import subprocess
import sys


class testPokerGame(unittest.TestCase):

# common causes of failing tests
# player being logged in through pidgin, it seems to intercept the message
# some failing tests print messages with e instead of the @ character
# message queue not being cleared out between tests. i.e. assert stops test but
# game keeps going and sends messages. These messages are pickedup when the
# next test starts
# exceptions get swallowed sometimes. Remove import of dealer in poker game to
# see python.exe from previous test still running (caused by exception being
# thrown in the main app)
# wrong signature on an event will fail without exception. Events should always
# have the signature (self, sender, args), even if args is not used
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
        logging.disable(logging.ERROR)

    def setUp(self):
        self.aPlayer = FakePlayer('Player1@pokerchat', 'Player1@localhost', 'password', 10, self)
        self.anotherPlayer = FakePlayer('Player2@pokerchat', 'Player2@localhost', 'password', 10, self)
        self.audience = FakeAudience('audience@pokerchat', 'audience@localhost', 'password', 10, self)
        subprocess.Popen([sys.executable, "..\\PokerGame.py"])

    def tearDown(self):
        self.aPlayer.stop()
        self.anotherPlayer.stop()
        self.audience.stop()
        self.swallowDealerMessages()

    def swallowDealerMessages(self):
        m = XmppMessenger('dealer@localhost', 'password')
        m.listen('localhost', 5222)
        time.sleep(2)
        m.finish()

    def testQuittingGameThatNoPlayersHaveJoined(self):

        self.audience.hears('Game started, waiting for players')
        self.audience.hears('No players joined so quitting')

    def testQuittingGameThatOnlyOnePlayerJoins(self):

        self.audience.hears('Game started, waiting for players')

        self.aPlayer.says('player1@pokerchat')
        self.aPlayer.hears('Cash 1000')

        self.audience.hears('player1@pokerchat has joined the game')
        self.audience.hears('Not enough players for a game so quitting')

    def testTwoPlayersAllIn(self):

        self.audience.hears('Game started, waiting for players')

        self.aPlayer.says('player1@pokerchat')
        self.aPlayer.hears('Cash 1000')
        self.audience.hears('player1@pokerchat has joined the game')

        self.anotherPlayer.says('player2@pokerchat')
        self.anotherPlayer.hears('Cash 1000')
        self.audience.hears('player2@pokerchat has joined the game')

        self.aPlayer.hears('go')
        self.aPlayer.says('1000')
        self.anotherPlayer.hears('player1@pokerchat 1000')
        self.anotherPlayer.says('1000')

        self.audience.hears('Game Over')


if __name__ == "__main__":
    unittest.main()
