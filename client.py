from common.parser import Arguments
from common.connection import Connection
from common.file import File
from data.config_loader import CONFIG
from data.segment import Segment

SERVER_IP = CONFIG['SERVER_IP']
SERVER_PORT = CONFIG['SERVER_PORT']

assert SERVER_IP != None
assert SERVER_PORT != None
assert type(SERVER_IP) is str
assert type(SERVER_PORT) is int
assert SERVER_PORT > 0


class Client:
    def __init__(self):
        self.args = Arguments(
            "Client Program (TCP Over UDP With Go-Back-N)").add("port", int, "Client Port.")

        self.clientAddress = ("127.0.0.1", self.args.port)
        self.serverAddress = (SERVER_IP, SERVER_PORT)
        self.connection = None
        self.file = File('./config.json')

    def listen(self):
        assert self.connection != None

        response, address = self.connection.listen()
        result = Segment().fromBytes(response)
        return address, result, result.isValid()

    def sendFlag(self, flags: list[str]):
        assert self.connection != None

        packet = Segment().setFlag(flags)
        self.connection.send(packet.getBytes(), self.serverAddress)

    def initConnection(self):
        assert self.connection == None

        self.connection = Connection(
            self.clientAddress[0], self.clientAddress[1])
        print(
            f"[!] Client started at {self.clientAddress[0]}:{self.clientAddress[1]}. Handshaking with server...")

    def broadcastSYN(self):
        assert self.connection != None

        print(f"[!] Broadcasting SYN...")
        self.sendFlag(['syn'])

    def waitSYNACK(self):
        assert self.connection != None

        print(f"[!] Waiting SYNACK...")
        _, response, ok = self.listen()
        if ok and response.flag.isAck() and response.flag.isSyn():
            self.sendFlag(['ack'])
            print(f"[!] Handshake OK. Sending ACK to server...")
        else:
            print(f"[!] Integrity Failed! Checksum or Flag error...")

    def close(self):
        assert self.connection != None

        self.connection.close()
        self.connection = None
        return self

    def threeWayHandshake(self):
        self.initConnection()
        self.broadcastSYN()
        self.waitSYNACK()
        return self

    def receiveFile(self):
        print("[!] Receiving File...")
        reqNumber = 0
        
        while True:
            address, response, ok = self.listen()
            if ok and address == self.serverAddress:
                if reqNumber == response.seqNum:
                    print(f"[Segment SEQ={reqNumber + 1}] Received, Ack sent")
                    ackResponse = Segment()
                    ackResponse.setFlag(['ack'])
                    self.connection.send(ackResponse.getBytes(), address)
                    reqNumber += 1
                elif response.flag.isFin():
                    print(f"[!] Successfully received file")
                    return self
                else:
                    print('error')
                    # print(
                        # f"[!] [{address}] Error ({response.seqNum} =/= {reqNumber}), Sequence number not equal, skipping...")
            elif not ok:
                print(
                    f'[!] [{address}] Checksum failed, response ins {response}')
            else:
                print(ok, address)

c = Client().threeWayHandshake().receiveFile().close()
