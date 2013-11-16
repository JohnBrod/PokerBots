import Queue
import time
import os
import sys
# these two lines do some freaky stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from Xmpp import XmppMessenger


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

    def on_messageReceived(self, sender, earg):
        self.q.put(earg)

    def stop(self):
        self.messenger.finish()


class FakeAudience():
    def __init__(self, jid, name, password, pollPeriod, testCase):
        self.testCase = testCase
        self.q = Queue.Queue()
        self.pollPeriod = pollPeriod
        self.jid = jid
        self.messenger = XmppMessenger(name, password)
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.messenger.listen('localhost', 5222)

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
            self.testCase.assertTrue(message.startswith(shouldHear[:-3]), self.jid + " expected '" + shouldHear + "' but heard '" + message + "'")
        else:
            self.testCase.assertEqual(message, shouldHear, self.jid + " expected '" + shouldHear + "' but heard '" + message + "'")

    def on_messageReceived(self, sender, msg):
        self.q.put(msg['body'])

    def stop(self):
        self.messenger.finish()
