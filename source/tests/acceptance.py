import time
import unittest
import os
import sys
import logging
# these two lines do some freaky stuff so I can import from the parent director
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from Xmpp import XmppMessenger
from runningTheApp import FakeParticipant
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
        logMessageFormat = '%(levelname)-8s %(message)s'
        logging.basicConfig(level=logging.ERROR, format=logMessageFormat)
        logging.disable(logging.ERROR)

    def setUp(self):
        pollDuration = 20
        self.aPlayer = FakeParticipant('Player1@pokerchat', 'password',
                                       pollDuration, 'dealer@pokerchat', self)
        self.anotherPlayer = FakeParticipant('Player2@pokerchat', 'password',
                                             pollDuration, 'dealer@pokerchat',
                                             self)
        self.audience = FakeParticipant('audience@pokerchat', 'password',
                                        pollDuration, 'dealer@pokerchat', self)
        self.handle = subprocess.Popen([sys.executable, "..\\PokerGame.py",
                                        "-ddealer@pokerchat", "-ppassword",
                                        "-aaudience@pokerchat",
                                        "-c1000",
                                        "-w5"])

    def tearDown(self):
        self.aPlayer.stop()
        self.anotherPlayer.stop()
        self.audience.stop()
        self.swallowMessages()

        subprocess.Popen("taskkill /F /T /PID %i" % self.handle.pid)

    def swallowMessages(self):
        m = XmppMessenger('dealer@pokerchat', 'password')
        m.listen('localhost', 5222)
        time.sleep(2)
        m.finish()

        m = XmppMessenger('audience@pokerchat', 'password')
        m.listen('localhost', 5222)
        time.sleep(2)
        m.finish()

    def testQuittingGameThatNoPlayersHaveJoined(self):

        self.audience.hears('Game started, waiting for players')
        self.audience.hears('No players joined so quitting')

    def testQuittingGameThatOnlyOnePlayerJoins(self):

        self.audience.hears('Game started, waiting for players')
        self.aPlayer.says('JOIN')
        self.aPlayer.hears('CHIPS 1000')
        self.audience.hears('Not enough players for a game so quitting')

    def testTwoPlayersAllIn(self):

        self.audience.hears('Game started, waiting for players')

        self.aPlayer.says('JOIN')
        self.aPlayer.hears('CHIPS 1000')

        self.anotherPlayer.says('JOIN')
        self.anotherPlayer.hears('CHIPS 1000')

        self.audience.hears('DEALING player1@pokerchat player2@pokerchat')
        self.aPlayer.hears('DEALING player1@pokerchat player2@pokerchat')
        self.anotherPlayer.hears('DEALING player1@pokerchat player2@pokerchat')

        self.aPlayer.hears('CARD...')
        self.anotherPlayer.hears('CARD...')

        self.aPlayer.hears('GO')
        self.aPlayer.says('1000')

        self.audience.hears('BET player1@pokerchat 1000')
        self.aPlayer.hears('BET player1@pokerchat 1000')
        self.anotherPlayer.hears('BET player1@pokerchat 1000')

        self.anotherPlayer.hears('GO')
        self.anotherPlayer.says('1000')

        self.audience.hears('BET player2@pokerchat 1000')
        self.aPlayer.hears('BET player2@pokerchat 1000')
        self.anotherPlayer.hears('BET player2@pokerchat 1000')

        self.audience.hears('CARD...')
        self.aPlayer.hears('CARD...')
        self.anotherPlayer.hears('CARD...')

        self.audience.hears('CARD...')
        self.aPlayer.hears('CARD...')
        self.anotherPlayer.hears('CARD...')

        self.audience.hears('CARD...')
        self.aPlayer.hears('CARD...')
        self.anotherPlayer.hears('CARD...')

        self.audience.hears('WON...')
        self.aPlayer.hears('WON...')
        self.anotherPlayer.hears('WON...')

        self.audience.eventuallyHears('WINNER...')
        self.aPlayer.eventuallyHears('WINNER...')
        self.anotherPlayer.eventuallyHears('WINNER...')

        self.audience.eventuallyHears('Game Over')


if __name__ == "__main__":
    unittest.main()
