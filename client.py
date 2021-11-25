from common.parser import Arguments
from common.connection import Connection
from data.config_loader import CONFIG
from data.segment import Segment

SERVER_IP = CONFIG['SERVER_IP']
SERVER_PORT = CONFIG['SERVER_PORT']
SEND_METADATA = CONFIG['SEND_METADATA']

assert SERVER_IP != None
assert SERVER_PORT != None
assert type(SERVER_IP) is str
assert type(SERVER_PORT) is int
assert SERVER_PORT > 0

assert SEND_METADATA != None
assert type(SEND_METADATA) is bool
METADATA_SEPARATOR = 0x3


class Client:
    def __init__(self):
        self.args = Arguments(
            "Client Program (TCP Over UDP With Go-Back-N)").add("port", int, "Client Port.").add("path", str, "Path file will be saved.")

        self.clientAddress = ("127.0.0.1", self.args.port)
        self.serverAddress = (SERVER_IP, SERVER_PORT)
        self.connection = None
        self.path = self.args.path

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

    def getMetadata(self):
        _, response, ok = self.listen()

        if ok:
            packetData = response.data
            i = 0
            for byte in packetData:
                i += 1
                if byte == METADATA_SEPARATOR:
                    break
            fileName = str(packetData[0:(i-1)], 'ascii')
            fileExt = str(packetData[i:len(packetData)], 'ascii')

            print(f'[!] Filename: {fileName}')
            print(f'[!] File Extension: {fileExt}')
        else:
            print(f'[!] Checksum failed when fetching metadata of file...')

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
        if SEND_METADATA:
            self.getMetadata()

        fileData = dict()
        reqNumber = 0
        while True:
            address, response, ok = self.listen()
            if ok and address == self.serverAddress:
                if reqNumber == response.seqNum:
                    print(
                        f"[Segment SEQ={reqNumber + 1}] Received, Ack sent")
                    ackResponse = Segment()
                    ackResponse.setFlag(['ack'])
                    ackResponse.setAcknowledgeNumber(reqNumber)
                    self.connection.send(ackResponse.getBytes(), address)
                    fileData[reqNumber] = response.data
                    reqNumber += 1
                elif response.flag.isFin():
                    print(f"[!] Successfully received file")
                    with open(self.path, 'wb+') as file:
                        for key in fileData.keys():
                            file.write(fileData[key])
                        return self
                else:
                    print(
                        f'[Segment SEQ={reqNumber + 1}] Segment damaged. Ack prev sequence number.')
                    reqNumber = response.ackNum
            elif not ok:
                print(
                    f'[!] [{address}] Checksum failed, response ins {response}')
            else:
                print(ok, address)


c = Client().threeWayHandshake().receiveFile().close()
