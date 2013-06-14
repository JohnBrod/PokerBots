import Queue
import time
import os
import sys
# these two lines do some freaky stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from ScrapingTheUi import ConsoleQueue
from ScrapingTheUi import QueueScraper
from Xmpp import XmppMessenger

class PokerGameRunner():
    
    def __init__(self, pollPeriod, testCase):
        self.testCase = testCase
        self.pollPeriod = pollPeriod
        self.pokerGameScript = '..\\PokerGame.py'

    def start(self):
        q = ConsoleQueue()
        q.startFilling(self.pokerGameScript) 
        self.pokerConsole = QueueScraper(q, self.pollPeriod)
    
    def shouldDisplay(self, expectedScreen):
        onScreen = self.pokerConsole.expect(expectedScreen)
        self.testCase.assertEqual(onScreen, expectedScreen)

class FakePlayer():
    def __init__(self, jid, name, password, pollPeriod, testCase):
        self.testCase = testCase
        self.q = Queue.Queue()
        self.pollPeriod = pollPeriod
        self.jid = jid
        self.messenger = XmppMessenger(name, password)
        self.messenger.evt_messageReceived += self.on_messageReceived

    def asksToJoinTheGame(self):
        self.messenger.listen('localhost', 5222)
        self.messenger.sendMessage('dealer@pokerchat', self.jid)

    def shouldReceiveAcknowledgementFromGame(self):
        end = time.time() + self.pollPeriod

        message = ''
        while time.time() <= end and not message:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass

        self.testCase.assertTrue(message)

    def on_messageReceived(self, sender, earg):
        self.q.put(earg)

    def stop(self):
        self.messenger.finish()
