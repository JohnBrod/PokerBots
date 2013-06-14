import time
from EventHandling import Event

class Doorman(object):
    """greets players and passes their details onto the its boss"""
    def __init__(self, waitFor, messenger):
        self.players = []
        self.waitFor = waitFor
        self.messenger = messenger
        self.messenger.evt_messageReceived += self.on_messageReceived
        self.evt_playerJoined = Event()

    def greetPlayers(self):
        self.messenger.listen('localhost', 5222)
        time.sleep(self.waitFor)

        self.messenger.finish()

        return self.players

    def on_messageReceived(self, sender, msg):
        self.players.append(msg)
        self.evt_playerJoined.fire(self, msg)
        if msg['type'] in ('normal', 'chat'):
            msg.reply("hi").send()
