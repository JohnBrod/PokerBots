import unittest
import time
import os
import sys
import logging
# these two lines do some freaky stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from runningTheApp import PokerGameRunner
from runningTheApp import FakePlayer

class testPokerGame(unittest.TestCase):

# common causes of failing tests
# throwing an exception, need to implement some handling, they are just being swallowed without notification
# player being logged in through pidgin, it seems to intercept the message
# some failing tests print messages with e instead of the @ character

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
        logging.disable(logging.ERROR)

    def setUp(self):
        self.theGame = PokerGameRunner(10, self)
        self.aPlayer = FakePlayer('Player1@pokerchat', 'Player1@localhost', 'password', 10, self)
        self.anotherPlayer = FakePlayer('Player2@pokerchat', 'Player2@localhost', 'password', 10, self)
        self.theGame.start()

    def tearDown(self):
        self.aPlayer.stop()
        self.anotherPlayer.stop()

    def testQuittingGameThatNoPlayersHaveJoined(self):

        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        self.theGame.shouldDisplay('No players joined so quitting\r\n')

    def testQuittingGameThatOnlyOnePlayerJoins(self):
        
        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        
        self.aPlayer.asksToJoinTheGame()

        self.aPlayer.shouldReceiveAcknowledgementFromGame()

        self.theGame.shouldDisplay('Player1@pokerchat has joined the game\r\n')
        self.theGame.shouldDisplay('Not enough players for a game so quitting\r\n')

if __name__=="__main__":
    unittest.main()