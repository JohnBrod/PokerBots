import time
import unittest
import os
import sys
import logging
# these two lines do some freaky stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from Xmpp import XmppMessenger
from runningTheApp import PokerGameRunner
from runningTheApp import FakePlayer

class testPokerGame(unittest.TestCase):

# common causes of failing tests
# throwing an exception, need to implement some handling, they are just being swallowed without notification
# player being logged in through pidgin, it seems to intercept the message
# some failing tests print messages with e instead of the @ character
# message queue not being cleared out between tests. i.e. assert stops test but game keeps going and sends messages. These messages are pickedup when the next test starts
# exceptions get swallowed sometimes. Remove import of dealer in poker game to see
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
        self.swallowDealerMessages()

    def swallowDealerMessages(self):
        m = XmppMessenger('dealer@localhost', 'password')
        m.listen('localhost', 5222)
        time.sleep(2)
        m.finish()

    def testQuittingGameThatNoPlayersHaveJoined(self):

        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        self.theGame.shouldDisplay('No players joined so quitting\r\n')

    def testQuittingGameThatOnlyOnePlayerJoins(self):
        
        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        
        self.aPlayer.says('Player1@pokerchat')
        self.aPlayer.hears('Cash 1000')

        self.theGame.shouldDisplay('Player1@pokerchat has joined the game\r\n')
        self.theGame.shouldDisplay('Not enough players for a game so quitting\r\n')

    def testPlayerGoesAllIn(self):
        
        self.theGame.shouldDisplay('Game started, waiting for players\r\n')
        
        self.aPlayer.says('Player1@pokerchat')
        self.aPlayer.hears('Cash 1000')
        self.theGame.shouldDisplay('Player1@pokerchat has joined the game\r\n')

        self.anotherPlayer.says('Player2@pokerchat')
        self.anotherPlayer.hears('Cash 1000')
        self.theGame.shouldDisplay('Player2@pokerchat has joined the game\r\n')

        self.aPlayer.hears('Private Cards...')        
        self.aPlayer.says('Bet Max')        

        self.anotherPlayer.hears('Private Cards...')        
        self.anotherPlayer.says('Call')

        self.aPlayer.hears('Community Cards...')        
        self.anotherPlayer.hears('Community Cards...')        

        self.aPlayer.hears('Flop...')        
        self.anotherPlayer.hears('Flop...')        

        self.aPlayer.hears('Turn...')        
        self.anotherPlayer.hears('Turn...')        

        self.aPlayer.hears('River...')        
        self.anotherPlayer.hears('River...')        

        self.aPlayer.hears('Result...')        
        self.anotherPlayer.hears('Result...')        

if __name__=="__main__":
    unittest.main()