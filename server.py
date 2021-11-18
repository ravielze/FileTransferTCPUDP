from common.parser import Arguments
from common.connection import BroadcastConnection, Connection
from data.config_loader import CONFIG
from data.segment import Segment
from socket import error as socketerror

SERVER_IP = CONFIG['SERVER_IP']
SERVER_PORT = CONFIG['SERVER_PORT']
WINDOW_SIZE = CONFIG['WINDOW_SIZE']

assert SERVER_IP != None
assert SERVER_PORT != None
assert type(SERVER_IP) is str
assert type(SERVER_PORT) is int
assert SERVER_PORT > 0

assert WINDOW_SIZE != None
assert type(WINDOW_SIZE) is int
assert WINDOW_SIZE > 0


class Server:
    def __init__(self):
        self.args = Arguments(
            "File Server Program (TCP Over UDP With Go-Back-N)")
        self.connection = None

    def listen(self):
        assert self.connection != None

        response, address = self.connection.listen()
        result = Segment().fromBytes(response)
        return address, result, result.isValid()

    def initBroadcastServer(self):
        assert self.connection == None

        self.connection = BroadcastConnection(SERVER_PORT)
        print(f"[!] Server started at {SERVER_IP}:{SERVER_PORT}...")

    def initConnection(self):
        assert self.connection == None

        self.connection = Connection(SERVER_IP, SERVER_PORT)

    def close(self):
        assert self.connection != None

        self.connection.close()
        self.connection = None

    def listenToClients(self):
        assert self.connection != None

        self.connectionList = []
        while True:
            address, response, ok = self.listen()
            if (ok and response.flag.isSyn() and not(address in self.connectionList)):
                self.connectionList.append(address)
                print(f"[!] Client ({address[0]}:{address[1]}) found")
                nextClient = input("[?] Listen more? (y/n) ")
                if nextClient.lower() != 'y':
                    break

    def infoClients(self, msg: str = "Clients found:"):
        print(f"\n[!] {len(self.connectionList)} {msg}")
        i = 1
        for each in self.connectionList:
            print(f"{i}. {each[0]}:{each[1]}")
            i += 1

    def checkClients(self):
        assert self.connection != None
        assert len(self.connectionList) > 0

        failedClients = []
        for client in self.connectionList:
            print(f"[!] Client ({client[0]}:{client[1]}): Handshaking...")
            if not self.checkClient(client):
                failedClients.append(client)

        self.connectionList = list(
            set(self.connectionList) - set(failedClients))

        self.infoClients("Clients successfully handshaked:")

    def checkClient(self, address: tuple[str, int]):
        assert address != None
        assert len(address) == 2

        packet = Segment().setFlag(['syn', 'ack'])
        self.connection.send(packet.getBytes(), address)

        self.connection.timeout(3)
        try:
            responseAddress, response, ok = self.listen()
            if responseAddress[0] == address[0] and responseAddress[1] == address[1] and response.flag.isAck() and ok:
                print(f"[!] Client ({address[0]}:{address[1]}): Handshake OK")
                self.connection.resetTimeout()
                return True
            else:
                print(
                    f"[!] Client ({address[0]}:{address[1]}): Handshake FAILED")
                self.connection.resetTimeout()
                return False
        except socketerror:
            print(f"[!] Client ({address[0]}:{address[1]}): Handshake TIMEOUT")
            self.connection.resetTimeout()
            return False

    def threeWayHandshake(self):
        # Client Registration
        self.initBroadcastServer()
        self.listenToClients()
        self.close()
        self.infoClients()

        # Three Way Handshake
        self.initConnection()
        self.checkClients()
        # TODO remove .close() after implementing sending file with gobackn
        self.close()


s = Server()
s.threeWayHandshake()
