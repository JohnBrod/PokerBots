import unittest
from texasHoldEm import Table

class testRotatingAroundTheTable(unittest.TestCase):
    
    def testDealingToFirstAtTable(self):

        t = Table(['p1', 'p2', 'p3'])

        self.assertEqual('p1', t.dealingTo())

    def testMovingToTheNext(self):

        t = Table(['p1', 'p2', 'p3'])

        t.nextPlayer()

        self.assertEqual('p2', t.dealingTo())

    def testThenTheLast(self):

        t = Table(['p1', 'p2', 'p3'])

        t.nextPlayer()
        t.nextPlayer()

        self.assertEqual('p3', t.dealingTo())

    def testBackToFirst(self):

        t = Table(['p1', 'p2', 'p3'])

        t.nextPlayer()
        t.nextPlayer()
        t.nextPlayer()

        self.assertEqual('p1', t.dealingTo())

class testRemovingPlayersFromTheTable(unittest.TestCase):
    
    def testRemoveFirst(self):

        t = Table(['p1', 'p2', 'p3'])
        self.assertEqual('p1', t.dealingTo())     
        t.removeCurrent()

        self.assertEqual('p2', t.dealingTo())     
    
    def testRemoveMiddle(self):

        t = Table(['p1', 'p2', 'p3'])
        self.assertEqual('p1', t.dealingTo())     
        t.nextPlayer()
        t.removeCurrent()

        self.assertEqual('p3', t.dealingTo())     
    
    def testRemoveLast(self):

        t = Table(['p1', 'p2', 'p3'])
        self.assertEqual('p1', t.dealingTo())     
        t.nextPlayer()
        t.nextPlayer()
        t.removeCurrent()

        self.assertEqual('p1', t.dealingTo())     

if __name__=="__main__":
    unittest.main()