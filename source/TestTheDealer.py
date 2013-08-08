import unittest
from theHouse import PlayerProxy
from texasHoldEm import Dealer
from EventHandling import Event
from mock import MagicMock

def createPlayer(name, messenger):
    player = PlayerProxy(name, messenger)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player

class testTheRotationOfTheDeal(unittest.TestCase):

    def testSmallBlindFirst(self):
        player = createPlayer('p1', NoReplyMessenger())
        player.yourGo = MagicMock()

        Dealer().deal([player])

        self.assertTrue(player.yourGo.called)

# # i think the badness in this test is firing the event...

    def testThenTheBigBlind(self):
        player = createPlayer('p1', NoReplyMessenger())
        nextPlayer = createPlayer('p2', NoReplyMessenger())
        nextPlayer.yourGo = MagicMock()

        Dealer().deal([player, nextPlayer])

        self.assertTrue(nextPlayer.yourGo.called)

    def testThenFirstToBet(self):
        p1 = createPlayer('p1', NoReplyMessenger())
        p2 = createPlayer('p2', NoReplyMessenger())
        p3 = createPlayer('p3', NoReplyMessenger())
        p3.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        self.assertTrue(p3.yourGo.called)

# this is really testing interaction between the dealer and the player proxy

    def testShouldMovetoNextPlayerAfterResponse(self):
        p1 = createPlayer('p1', NoReplyMessenger())
        p2 = createPlayer('p2', NoReplyMessenger())
        p3 = createPlayer('p3', SingleReplyMessenger(10))
        p4 = createPlayer('p4', NoReplyMessenger())
        p4.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3, p4])

        self.assertTrue(p4.yourGo.called)

#don't think this was testing correctly. trying to test the table class from the public interface of the dealer is difficult
#maybe this testing should be done against the table
    def testDealsToFirstPlayerWhenLastPlayerResponds(self):
        player = createPlayer('p1', NoReplyMessenger())
        player.yourGo = MagicMock()

        nextPlayer = createPlayer('p2', NoReplyMessenger())

    	Dealer().deal([player, nextPlayer])

    	self.assertEqual(2, len(player.yourGo.mock_calls))

# can't figure out how to implement this test

    def testTellsPlayerThatTheyAreOutIfTheyRespondOutOfTurn(self):
        pass

    # def testStopsDealingWhenThereIsaWInner(self):
    #     player = createPlayer('p1')
    #     nextPlayer = createPlayer('p2')
    #     player.yourGo = MagicMock()
    #     nextPlayer.yourGo = MagicMock()

    #     dealer = Dealer()
    #     handFinished = False
    #     def onHandFinished(sender, flag) : handFinished = True

    #     dealer.evt_handFinished += onHandFinished
    #     dealer.deal([player, nextPlayer])

    #     player.evt_response.fire(nextPlayer, 5)
    #     # nextPlayer.evt_response.fire(nextPlayer, 5)

    #     # player.evt_response.fire(nextPlayer, 5)
    #     # nextPlayer.evt_response.fire(nextPlayer, 5)

    #     # player.evt_response.fire(nextPlayer, 5)
    #     # nextPlayer.evt_response.fire(nextPlayer, 0)

    #     self.assertEqual(4, len(player.yourGo.mock_calls))
    #     self.assertEqual(4, len(nextPlayer.yourGo.mock_calls))
    #     self.assertTrue(handFinished)
               
class testRoundOfCalling(unittest.TestCase):
    
    def testBlindsAndThenBetting(self):
        p1 = createPlayer('p1', NoReplyMessenger())
        p2 = createPlayer('p2', NoReplyMessenger())
        p3 = createPlayer('p3', NoReplyMessenger())

        p1.yourGo = MagicMock()
        p2.yourGo = MagicMock()
        p3.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p1.yourGo.assert_called_once_with([('p1', 5)])
        p2.yourGo.assert_called_once_with([('p1', 5), ('p2', 10)])
        p3.yourGo.assert_called_once_with([('p1', 5), ('p2', 10)])
    
    def testFirstShouldBetTheDifference(self):
        p1 = createPlayer('p1', NoReplyMessenger())
        p2 = createPlayer('p2', NoReplyMessenger())
        p3 = createPlayer('p3', SingleReplyMessenger(10))
        p1.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p1.yourGo.assert_called_with([('p1', 5), ('p2', 10), ('p3', 10)])
    
    def testPlayerKickedOutForBettingLessThanMinimum(self):
        p1 = createPlayer('p1', NoReplyMessenger())
        p2 = createPlayer('p2', NoReplyMessenger())
        p3 = createPlayer('p3', SingleReplyMessenger(9))
        p3.outOfGame = MagicMock()

        Dealer().deal([p1, p2, p3])

        p3.outOfGame.assert_called_once_with()

class NoReplyMessenger():

    def __init__(self):
        self.evt_messageReceived = Event()

    def sendMessage(self, jid, msg):
        pass

class SingleReplyMessenger():

    def __init__(self, msg):
        self.evt_messageReceived = Event()
        self.msg = msg

    def sendMessage(self, jid, msg):
        self.evt_messageReceived.fire(self, self.msg)

if __name__=="__main__":
    unittest.main()