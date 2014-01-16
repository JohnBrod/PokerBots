import unittest
from theHouse import Table


class testRotatingAroundTheTable(unittest.TestCase):

    def setUp(self):
        print 'Rotating around the table,', self.shortDescription()
        self.table = Table()

    def testA_DealingToFirstAtTable(self):
        '''deal to the first person at the table'''
        self.table.seat(['p1', 'p2', 'p3'])

        self.assertEqual('p1', self.table.dealingTo())

    def testB_MovingToTheNext(self):
        '''move to the next'''
        self.table.seat(['p1', 'p2', 'p3'])
        self.table.nextPlayer()

        self.assertEqual('p2', self.table.dealingTo())

    def testC_ThenTheLast(self):
        '''all the way to the last'''
        self.table.seat(['p1', 'p2', 'p3'])

        self.table.nextPlayer()
        self.table.nextPlayer()

        self.assertEqual('p3', self.table.dealingTo())

    def testD_BackToFirst(self):
        '''back to first after last'''
        self.table.seat(['p1', 'p2', 'p3'])

        self.table.nextPlayer()
        self.table.nextPlayer()
        self.table.nextPlayer()

        self.assertEqual('p1', self.table.dealingTo())


if __name__ == "__main__":
    unittest.main()
