import Queue
import time
import os
import sys
# these two lines do some stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from Xmpp import XmppMessenger


class FakeParticipant():
    def __init__(self, jid, password, pollPeriod, dealerjid, testCase):
        self.dealerjid = dealerjid
        self.testCase = testCase
        self.jid = jid
        self.q = Queue.Queue()
        self.pollPeriod = pollPeriod
        self.messenger = XmppMessenger(jid, password)
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.messenger.listen('localhost', 5222)

    def says(self, said):
        self.messenger.sendMessage(self.dealerjid, said)

    def _getMessage(self):
        end = time.time() + self.pollPeriod

        message = None
        while time.time() <= end and not message:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass

        return message

    def hears(self, shouldHear):

        message = self._getMessage()

        self.assertMessage(message, shouldHear)

    def eventuallyHears(self, shouldHear):
        end = time.time() + self.pollPeriod

        message = None
        while time.time() <= end and message != shouldHear:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass

        self.assertMessage(message, shouldHear)

    def assertMessage(self, message, shouldHear):
        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear '" + shouldHear + "'")
        elif shouldHear.endswith('...'):
            failMessage = self.jid + " expected '" + shouldHear + "' but heard '" + message + "'"
            self.testCase.assertTrue(message.startswith(shouldHear[:-3]), )
        else:
            failMessage = self.jid + " expected '" + shouldHear + "' but heard '" + message + "'"
            self.testCase.assertEqual(message, shouldHear, failMessage)

        print self.jid + ' ' + message

    def on_messageReceived(self, sender, msg):
        self.q.put(msg['body'])

    def stop(self):
        self.messenger.finish()
