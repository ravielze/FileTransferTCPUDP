from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST


class Connection:
    def __init__(self, ip: str, port: int):
        assert ip != None
        assert port != None
        assert port > 0
        assert len(ip) > 8

        self.ip = ip
        self.port = port

        # AF_INET     : format IPv4
        # SOCK_DGRAM  : socket type datagram -> UDP,
        #               full TCP? change to SOCK_STREAM
        self.socket = socket(AF_INET, SOCK_DGRAM)

        self.socket.bind((ip, port))

        # Control Socket Behavior
        # SOL_SOCKET    : setting socket level
        # SO_BROADCAST  : allow broadcast nessage
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    def timeout(self, timeout: float):
        assert timeout != None
        assert timeout > 0

        self.socket.settimeout(timeout)
        return self

    def send(self, msg: bytes, dest: tuple[str, int]):
        assert msg != None
        assert dest != None
        assert len(dest) == 2
        assert len(dest[0]) > 8
        assert len(dest[1]) > 0

        self.socket.sendto(msg, dest)
        return self

    def listen(self):
        response, address = self.socket.recvfrom(2**16)
        return response, address

    def close(self):
        self.socket.close()


class BroadcastConnection(Connection):
    def __init__(self, port: int):
        Connection.__init__(self, '', port)
