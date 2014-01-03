import unittest
from theHouse import PlayerProxy


def createPlayer(chips):
    player = PlayerProxy('name', chips)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    return player


class testThePlayersCash(unittest.TestCase):

    def setUp(self):
        print 'The players chips,', self.shortDescription()

    def testA_shouldBeIncreasedWhenTheyWin(self):
        '''is increased when the player wins'''
        p = createPlayer(chips=100)

        p.deposit(50)

        self.assertEqual(p.chips, 150)


if __name__ == "__main__":
    unittest.main()
