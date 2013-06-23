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
        self.messenger.listen('localhost', 5222)

    def asksToJoinTheGame(self):
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

    def says(self, said):
        self.messenger.sendMessage('dealer@pokerchat', said)
        
    def hears(self, shouldHear):
        end = time.time() + self.pollPeriod

        message = None
        while time.time() <= end and not message:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear '" + shouldHear + "'")
        elif shouldHear.endswith('...'):
            self.testCase.assertTrue(message['body'].startswith(shouldHear[:-3]), self.jid + " expected '" + shouldHear + "' but heard '" + message['body'] + "'")
        else:
            self.testCase.assertEqual(message['body'], shouldHear, self.jid + " expected '" + shouldHear + "' but heard '" + message['body'] + "'")
        
    def discardMessages(self):
        end = time.time() + self.pollPeriod

        message = None
        while time.time() <= end and not message:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass
                
    def won(self):
        end = time.time() + self.pollPeriod

        message = None
        while time.time() <= end and not message:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass
        if message and message['body'] == 'You won':
            return True
        
        return False

    def on_messageReceived(self, sender, earg):
        self.q.put(earg)

    def stop(self):
        self.messenger.finish()
