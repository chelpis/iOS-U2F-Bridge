from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.internet import reactor

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        global mainChannel
        mainChannel.register(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {} bytes".format(len(payload)))
        else:
            print("Text message received: {}".format(payload.decode('utf8')))

        mainChannel.onMessage(payload, isBinary)        

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

class Channel():
    session = None
    observer = None

    def isOnline(self):
        return (self.observer)

    def register(self, session):    
        self.session = session

    def sendMessage(self, message):    
        if self.session != None:
            self.session.sendMessage(message, True)

    def onMessage(self, payload, isBinary):
        if not self.observer:
            print("no observer to handle")
            return
        self.observer(payload, isBinary)

    def setObserver(self, observer):
        self.observer = observer
        

mainChannel = Channel()