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
               
class testBettingBetweenTheDealerAndPlayers(unittest.TestCase):
    
    def testMoveLeftToRightAtTheTable(self):
        p1 = createPlayer('p1', ObedientMessenger().skip())
        p2 = createPlayer('p2', ObedientMessenger().skip())
        p3 = createPlayer('p3', ObedientMessenger())

        p1.yourGo = MagicMock()
        p2.yourGo = MagicMock()
        p3.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p1.yourGo.assert_called_with([(p1, 5)])
        p2.yourGo.assert_called_with([(p1, 5), (p2, 10)])
        p3.yourGo.assert_called_with([(p1, 5), (p2, 10)])
    
    def testBackToFirstPlayerAfterTheLast(self):
        p1 = createPlayer('p1', ObedientMessenger().skip())
        p2 = createPlayer('p2', ObedientMessenger().skip())
        p3 = createPlayer('p3', ObedientMessenger().bet(10))
        p1.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p1.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 10)])
    
    def testPlayerFolds(self):
        p1 = createPlayer('p1', ObedientMessenger().skip().bet(0))
        p2 = createPlayer('p2', ObedientMessenger().skip())

        p2.handResult = MagicMock()

        dealer = Dealer()
        dealer.evt_handFinished.fire = MagicMock()
        dealer.deal([p1, p2])

        dealer.evt_handFinished.fire.assert_called_with(dealer)
        p2.handResult.assert_called_once_with('You Win')
    
    def testPlayerBetsLessThanMinimum(self):
        p1 = createPlayer('p1', ObedientMessenger().skip())
        p2 = createPlayer('p2', ObedientMessenger().skip())
        p3 = createPlayer('p3', ObedientMessenger().bet(9))
        p4 = createPlayer('p4', ObedientMessenger())
        p3.outOfGame = MagicMock()
        p4.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3, p4])

        p3.outOfGame.assert_called_once_with()
        p4.yourGo.assert_called_with([(p1, 5), (p2, 10)])
    
    def testFirstPlayerBetsLessThanMinimum(self):
        p1 = createPlayer('p1', ObedientMessenger().skip().bet(4))
        p2 = createPlayer('p2', ObedientMessenger().skip())
        p3 = createPlayer('p3', ObedientMessenger().bet(10))
        p1.outOfGame = MagicMock()
        p2.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p1.outOfGame.assert_called_once_with()
        p2.yourGo.assert_called_with([(p1, 5), (p2, 10), (p3, 10)])
        
    def testPlayerBetsMoreThanTheyHave(self):
        p1 = createPlayer('p1', ObedientMessenger().skip())
        p2 = createPlayer('p2', ObedientMessenger().skip())
        p3 = createPlayer('p3', ObedientMessenger().bet(1001))
        p4 = createPlayer('p4', ObedientMessenger())
        p3.outOfGame = MagicMock()
        p4.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3, p4])

        p3.outOfGame.assert_called_once_with()
        p4.yourGo.assert_called_with([(p1, 5), (p2, 10)])
        
    def testPlayerBetsMoreThanTheyHaveInTwoParts(self):
        p1 = createPlayer('p1', ObedientMessenger().skip().bet(10).bet(986))
        p2 = createPlayer('p2', ObedientMessenger().skip().bet(10))
        p1.outOfGame = MagicMock()
        p2.handResult = MagicMock()

        Dealer().deal([p1, p2])

        p1.outOfGame.assert_called_once_with()
        p2.handResult.assert_called_once_with('You Win')
        
# class testDealingTheCards(unittest.TestCase):
    
#     def testTheDealerShouldGiveEachPlayerPrivateCards(self):
#         p1 = createPlayer('p1', ObedientMessenger())
#         p2 = createPlayer('p2', ObedientMessenger())

#         p1.cards = MagicMock()
#         p2.cards = MagicMock()

#         Dealer(PredictableDeck()).deal([p1, p2])

#         p1.cards.assert_called_once_with((1, 2))
#         p2.cards.assert_called_once_with((3, 4))

# a player that folds is excluded from the next round
# player folds, all players are in
# if only one player left then they win

    # def testPlayerFoldsAndTheRemainingPlayerIsTheWinner(self):
    #     p1 = createPlayer('p1', ObedientMessenger().skip().bet(0))
    #     p2 = createPlayer('p2', ObedientMessenger().skip())

    #     p1.cards = MagicMock()
    #     p2.cards = MagicMock()

    #     Dealer(PredictableDeck()).deal([p1, p2])

    #     p1.cards.assert_not_called_with((5, 6, 7))
    #     p1.cards.assert_not_called_with((5, 6, 7))

# player kicked out because they don't respond within the allowed time

# no community cards until all palyers are in

    # def testCommunityCardsAreDealtAfterTheFirstRoundOfBetting(self):
    #     p1 = createPlayer('p1', ObedientMessenger().skip().bet(5))
    #     p2 = createPlayer('p2', ObedientMessenger().skip().bet(0))

    #     p1.cards = MagicMock()
    #     p2.cards = MagicMock()

    #     Dealer(PredictableDeck()).deal([p1, p2])

    #     p1.cards.assert_called_with((5, 6, 7))
    #     p2.cards.assert_called_with((5, 6, 7))

class PredictableDeck():

    def __init__(self):
        self.card = 0

    def take(self):
        self.card += 1
        return self.card
    
class AnyDeck():
    def take(self):
        pass

class ObedientMessenger(object):
    """docstring for ObedientMessenger"""
    def __init__(self):
        self.evt_messageReceived = Event()
        self.replies = Queue()

    def skip(self):
        self.replies.put('skip')
        return self

    def bet(self, amount):
        self.replies.put(amount)
        return self

    def sendMessage(self, jid, msg):

        if self.replies.empty(): return

        response = self.replies.get()

        if response == 'skip': return

        self.evt_messageReceived.fire(self, response)
        
if __name__=="__main__":
    unittest.main()