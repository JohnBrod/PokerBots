import unittest
from EventHandling import Event

from theHouse import Dealer

class testDealerCommunicationWithPlayer(unittest.TestCase):

    def onPlayerJoined(self, sender, msg): 
        self.playerJoined = True

    def testPlayerAsksToJoin(self):
     
        self.playerJoined = False
        xmppServer = FakeXmppServer()
        dealer = Dealer(0, xmppServer) 
        dealer.evt_playerJoined += self.onPlayerJoined 
        xmppServer.announceMessageReceived(FakeMessage())

        self.assertEqual(self.playerJoined, True)

class FakeXmppServer(object):
    """docstring for FakeXmppServer"""
    def __init__(self):
        self.evt_messageReceived = Event()
        self.evt_askedToSendMessage = Event()

    def announceMessageReceived(self, msg):
        self.evt_messageReceived.fire(self, msg)

    def sendMessage(self, msg):
        self.evt_askedToSendMessage.fire(self, msg)

    def listen(self, a, b):
        pass

    def finish(self):
        pass

class FakeMessage():

    def __init__(self):
        self.data = { 'type' : 'normal' }

    def __getitem__(self, key): 
        return self.data[key]

    def reply(self, msg):
        return self

    def send(self):
        pass

if __name__ == '__main__':
    unittest.main()