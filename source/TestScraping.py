import unittest
import Queue
import os
import sys
# these two lines do some freaky stuff so I can import from the parent directory
parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))
from ScrapingTheUi import QueueScraper

class testScrapeTheQueue(unittest.TestCase):

    def testLookForNothingAndGetsNothing(self):

        lookFor = ''
        screen = Queue.Queue()
        scraper = QueueScraper(screen)

        self.assertEqual(scraper.expect(lookFor), lookFor)

    def testLookForHAndGetsH(self):

        lookFor = 'H'
        screen = Queue.Queue()
        screen.put('H')
        scraper = QueueScraper(screen)

        self.assertEqual(scraper.expect(lookFor), lookFor)

    def testLookForHeAndGetsHe(self):

        lookFor = 'He'
        screen = Queue.Queue()
        screen.put('H')
        screen.put('e')
        scraper = QueueScraper(screen)

        self.assertEqual(scraper.expect(lookFor), lookFor)

    def testLookForHelloAndGetsHellX(self):

        lookFor = 'Hello'
        screen = Queue.Queue()
        screen.put('H')
        screen.put('e')
        screen.put('l')
        screen.put('l')
        screen.put('X')
        scraper = QueueScraper(screen)

        self.assertEqual(scraper.expect(lookFor), 'Hell')

    def testMoreTextAfterSearchText(self):

        lookFor = 'H'
        screen = Queue.Queue()
        screen.put('H')
        screen.put('e')
        scraper = QueueScraper(screen)

        self.assertEqual(scraper.expect(lookFor), 'H')



if __name__=="__main__":
    unittest.main()