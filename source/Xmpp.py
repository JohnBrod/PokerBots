import sys
import logging
import sleekxmpp
from EventHandling import Event

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


def chat(msg):
    return msg['type'] in ('normal', 'chat')


def getName(x):
    return str(x)[:str(x).find('/')]


class XmppMessenger(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.evt_messageReceived = Event()

    def on_start(self, event):

        self.send_presence()
        self.get_roster()

    def on_message(self, msg):
        if not chat(msg):
            return

        msg = (getName(msg['from']), msg['body'])
        self.evt_messageReceived.fire(self, msg)

    def listen(self, domain, port):

        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.on_message)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping

        if self.connect((domain, port)):
            self.process(block=False)
        else:
            logging.error('failed to connect to ' + domain + port)

    def sendMessage(self, jid, message):
        self.send_message(mto=jid, mbody=str(message), mtype='chat')

    def finish(self):
        self.disconnect(wait=True)

# if __name__ == '__main__':

#     # logging.DEBUG
#     # logging.INFO
#     # logging.ERROR
#     logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(messag
    #e)s')
#     logging.disable(logging.ERROR)

#     # Setup the EchoBot and register plugins. Note that while plugins may
#     # have interdependencies, the order in which you register them does
#     # not matter.
#     player = XmppMessenger('player1@pokerchat', 'password')
#     dealer = XmppMessenger('dealer@pokerchat', 'password')

#     # ... here I add my own handlers
#     # f = open("/tmp/debug","w")          # example handler
#     # lh = logging.StreamHandler(f)
#     # logger.addHandler(lh)

#     print "**************** Game Start"

#     player.listen('localhost', 5222)
#     dealer.listen('localhost', 5222)

#     time.sleep(5)

#     dealer.sendMessage('player1@pokerchat', 'hello player 1')

#     time.sleep(5)

#     dealer.finish()
#     player.finish()

#     print "*************** Game Over"
