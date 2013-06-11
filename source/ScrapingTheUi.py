import Queue
import threading
import sys
import subprocess
import time

class ConsoleQueue():

    def __init__(self):
        self.screen = Queue.Queue()

    def startFilling(self, pythonFilename):
        t = threading.Thread(target=self.readConsole, args=[self.screen, pythonFilename])
        t.start()

    def readConsole(self, q, pythonFilename):
        process = subprocess.Popen([sys.executable, pythonFilename], stdout=subprocess.PIPE)

        while True:

            out = process.stdout.readline(1)
            if out == '' and process.poll() != None:
                break

            q.put(out)

    def get_nowait(self):
        return self.screen.get_nowait()

class QueueScraper():
    """docstring for QueueScraper"""
    def __init__(self, q, pollPeriod=0):
        self.screen = q
        self.pollPeriod = pollPeriod
    
    ## returns as many of the expected letters if found in the given order
    def expect(self, text):

        found = ''
        textQ = Queue.Queue()

        for char in text: textQ.put(char)

        end = time.time() + self.pollPeriod

        while time.time() <= end and not found:
            try:

                while True:
                    char = self.screen.get_nowait()
                    if char == textQ.get_nowait():
                        found += char

            except Queue.Empty:
                pass

        return found
