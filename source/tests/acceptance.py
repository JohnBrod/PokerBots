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

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')
        logging.disable(logging.ERROR)

    def setUp(self):
        self.player1Jid = 'Player1@pokerchat'
        self.player1Name = 'Player1@localhost'
        self.player1Password = 'password'
        self.theGame = PokerGameRunner(10, self)
        self.thePlayer = FakePlayer(self.player1Jid, self.player1Name, self.player1Password, 10, self)
        self.theGame.start()

    def tearDown(self):
        self.thePlayer.stop()

    def testQuittingGameThatNoPlayersHaveJoined(self):

        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        time.sleep(3)
        self.theGame.shouldDisplay('No players joined so quitting\r\n')

    def testQuittingGameThatOnlyOnePlayerJoins(self):
        
        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        
        self.thePlayer.asksToJoinTheGame()

        self.thePlayer.shouldReceiveAcknowledgementFromGame()

        self.theGame.shouldDisplay('Player1 has joined the game\r\n')
        time.sleep(3)
        self.theGame.shouldDisplay('Not enough players for a game so quitting\r\n')

if __name__=="__main__":
    unittest.main()