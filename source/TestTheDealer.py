import unittest
from Queue import Queue
from theHouse import PlayerProxy
from texasHoldEm import Dealer
from EventHandling import Event
from mock import MagicMock

def createPlayer(name, messenger):
    player = PlayerProxy(name, messenger)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player
               
# class testBettingBetweenTheDealerAndPlayers(unittest.TestCase):
    
#     def testMoveLeftToRightAtTheTable(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind())
#         p2 = createPlayer('p2', StubMessenger().skipBlind())
#         p3 = createPlayer('p3', StubMessenger())

#         p1.yourGo = MagicMock()
#         p2.yourGo = MagicMock()
#         p3.yourGo = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2, p3])

#         p1.yourGo.assert_called_with([(p1, 5)])
#         p2.yourGo.assert_called_with([(p1, 5), (p2, 10)])
#         p3.yourGo.assert_called_with([(p1, 5), (p2, 10)])
    
#     def testBackToFirstPlayerAfterTheLast(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind())
#         p2 = createPlayer('p2', StubMessenger().skipBlind())
#         p3 = createPlayer('p3', StubMessenger().bet(10))
#         p1.yourGo = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2, p3])

#         p1.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 10)])
    
#     def testPlayerFolds(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind().bet(0))
#         p2 = createPlayer('p2', StubMessenger().skipBlind())

#         p2.handResult = MagicMock()
#         p1.outOfGame = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2])

#         p1.outOfGame.assert_called_once_with('You folded')
#         p2.handResult.assert_called_once_with('p2 wins')
    
#     def testPlayerBetsLessThanMinimum(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind())
#         p2 = createPlayer('p2', StubMessenger().skipBlind())
#         p3 = createPlayer('p3', StubMessenger().bet(9))
#         p4 = createPlayer('p4', StubMessenger())
#         p3.outOfGame = MagicMock()
#         p4.yourGo = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2, p3, p4])

#         p3.outOfGame.assert_called_once_with('You bet 9, minimum bet was 10')
#         p4.yourGo.assert_called_with([(p1, 5), (p2, 10)])
    
#     def testFirstPlayerBetsLessThanMinimum(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind().bet(4))
#         p2 = createPlayer('p2', StubMessenger().skipBlind())
#         p3 = createPlayer('p3', StubMessenger().bet(10))
#         p1.outOfGame = MagicMock()
#         p2.yourGo = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2, p3])

#         p1.outOfGame.assert_called_once_with('You bet 4, minimum bet was 5')
#         p2.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 10)])
        
#     def testPlayerBetsTheMax(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind().bet(995))
#         p2 = createPlayer('p2', StubMessenger().skipBlind())
#         p2.yourGo = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2])

#         p2.yourGo.assert_called_with([(p1, 5), (p2, 10), (p1, 995)])
        
#     def testPlayerBetsMoreThanTheyHave(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind())
#         p2 = createPlayer('p2', StubMessenger().skipBlind())
#         p3 = createPlayer('p3', StubMessenger().bet(1001))
#         p4 = createPlayer('p4', StubMessenger())
#         p3.outOfGame = MagicMock()
#         p4.yourGo = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2, p3, p4])

#         p3.outOfGame.assert_called_once_with('You bet 1001, you have only 1000 cash avaiable')
#         p4.yourGo.assert_called_with([(p1, 5), (p2, 10)])
        
#     def testPlayerBetsMoreThanTheyHaveInTwoParts(self):
#         p1 = createPlayer('p1', StubMessenger().skipBlind().bet(10).bet(986))
#         p2 = createPlayer('p2', StubMessenger().skipBlind().bet(10))
#         p1.outOfGame = MagicMock()
#         p2.handResult = MagicMock()

#         Dealer(AnyDeck()).deal([p1, p2])

#         p1.outOfGame.assert_called_once_with('You bet 986, you have only 985 cash avaiable')
#         p2.handResult.assert_called_once_with('p2 wins')

class testDealingTheCards(unittest.TestCase):
    
    def testTheDealerShouldGiveEachPlayerSeparatePrivateCards(self):
        p1 = createPlayer('p1', StubMessenger())
        p2 = createPlayer('p2', StubMessenger())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((1, 2))
        p2.cards.assert_called_with((3, 4))

    def testCommunityCardsShouldNotBeDealtUntilTheBigBlindGetsTheOption(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5))
        p2 = createPlayer('p2', StubMessenger().skipBlind())

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((1, 2))
        p2.cards.assert_called_with((3, 4))

    def testCommunityCardsDealtAfterTheBigBlindRefusesTheOption(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(0))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((5, 6, 7))
        p2.cards.assert_called_with((5, 6, 7))

    def testCommunityCardsDealtAfterTheBigBlindGetsTakesTheOption(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5).bet(10))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(10))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((5, 6, 7))
        p2.cards.assert_called_with((5, 6, 7))

    def testThenTheFlop(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5).bet(10))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(0).bet(10))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((8))
        p2.cards.assert_called_with((8))

    def testThenTheRiver(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5).bet(10).bet(10))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(0).bet(10).bet(10))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((9))
        p2.cards.assert_called_with((9))

    def testThenTheTurn(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5).bet(10).bet(10).bet(10))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(0).bet(10).bet(10).bet(10))

        p1.cards = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((10))
        p2.cards.assert_called_with((10))

    def testThenTheWinnerIsDeclared(self):
        p1 = createPlayer('p1', StubMessenger().skipBlind().bet(5).bet(10).bet(10).bet(10).bet(10))
        p2 = createPlayer('p2', StubMessenger().skipBlind().bet(0).bet(10).bet(10).bet(10).bet(10))

        p1.cards = MagicMock()
        p1.handResult = MagicMock()
        p2.cards = MagicMock()

        Dealer(PredictableDeck()).deal([p1, p2])

        p1.cards.assert_called_with((10))
        p2.cards.assert_called_with((10))
        p1.handResult.assert_called_once_with('someone wins')

# should not send out any more messages after the winner

class PredictableDeck():

    def __init__(self):
        self.card = 0

    def take(self):
        self.card += 1
        return self.card
    
class AnyDeck():
    def take(self):
        pass

class StubMessenger(object):
    def __init__(self):
        self.evt_messageReceived = Event()
        self.replies = Queue()

    def skipBlind(self):
        self.replies.put('skip')
        return self

    def bet(self, amount):
        self.replies.put(amount)
        return self

    def sendMessage(self, jid, msg):

        self.lastMessage = msg

        if self.replies.empty(): return

        response = self.replies.get()

        if response == 'skip': return

        self.evt_messageReceived.fire(self, response)

if __name__=="__main__":
    unittest.main()