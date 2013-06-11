import time
from EventHandling import Event

class Dealer():
    """docstring for Dealer"""
    def __init__(self, waitFor, messenger):
        self.players = []
        self.waitFor = waitFor
        self.messenger = messenger
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.evt_playerJoined = Event()
        self.evt_finished = Event()

    def start(self):
        self.messenger.listen('localhost', 5222)
        time.sleep(self.waitFor)

        if self.players:
            self.evt_finished.fire(self, 'Not enough players for a game so quitting')
        else:
            self.evt_finished.fire(self, 'No players joined so quitting')
        
        self.stop()

    def on_messageReceived(self, sender, msg):
        self.players.append(msg)
        self.evt_playerJoined.fire(self, msg)
        if msg['type'] in ('normal', 'chat'):
            msg.reply("hi").send()

    def stop(self):
        self.messenger.finish()

    def sendMessage(self, to, msg):
        self.messenger.sendMessage(to, msg)

