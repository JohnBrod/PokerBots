import Queue
import time
import os
import sys
# these two lines do some freaky stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

from Xmpp import XmppMessenger


class FakeParticipant():
    def __init__(self, jid, password, pollPeriod, testCase):
        self.testCase = testCase
        self.jid = jid
        self.q = Queue.Queue()
        self.pollPeriod = pollPeriod
        self.messenger = XmppMessenger(jid, password)
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.messenger.listen('localhost', 5222)

    def says(self, said):
        self.messenger.sendMessage('dealer@pokerchat', said)

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

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear '" + shouldHear + "'")
        elif shouldHear.endswith('...'):
            failMessage = self.jid + " expected '" + shouldHear + "' but heard '" + message + "'"
            self.testCase.assertTrue(message.startswith(shouldHear[:-3]), )
        else:
            failMessage = self.jid + " expected '" + shouldHear + "' but heard '" + message + "'"
            self.testCase.assertEqual(message, shouldHear, failMessage)

        print self.jid + ' ' + message

    def hearsPrivateCards(self):
        message = self._getMessage()

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear 'Private Cards'")
        else:
            failMessage = self.jid + " expected 'Private Cards' but heard '" + message + "'"
            self.testCase.assertTrue(message.count(',') == 1, failMessage)

        print self.jid + ' ' + message

    def hearsCommunityCards(self):
        message = self._getMessage()

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear 'Community Cards'")
        else:
            failMessage = self.jid + " expected 'Community Cards' but heard '" + message + "'"
            self.testCase.assertTrue(message.count(',') == 2, failMessage)

        print self.jid + ' ' + message

    def hearsTurnCard(self):
        message = self._getMessage()

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear 'Turn Card'")

        print self.jid + ' ' + message

    def hearsResult(self):
        message = self._getMessage()

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear the result")
        else:
            failMessage = self.jid + " expected the result but heard '" + message + "'"
            self.testCase.assertTrue(message.startswith('WON'), failMessage)

        print self.jid + ' ' + message

    def eventuallyHears(self, shouldHear):
        end = time.time() + self.pollPeriod

        message = None
        while time.time() <= end and message != shouldHear:
            try:
                message = self.q.get_nowait()
            except Queue.Empty:
                pass

        if not message:
            self.testCase.assertFalse(True, self.jid + " did not hear '" + shouldHear + "'")
        else:
            failMessage = self.jid + " expected '" + shouldHear + "' but heard '" + message + "'"
            self.testCase.assertEqual(message, shouldHear, failMessage)

        print self.jid + ' ' + message

    def on_messageReceived(self, sender, msg):
        self.q.put(msg['body'])

    def stop(self):
        self.messenger.finish()
