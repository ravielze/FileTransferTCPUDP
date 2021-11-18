import struct


class SegmentFlag:

    def __init__(self):
        self.ACK = 0b00010000
        self.SYN = 0b00000010
        self.FIN = 0b00000001
        self.bytesValue = 0b00000000
        self.flag = [False, False, False]

    def getBytes(self):
        return self.bytesValue

    def setBytes(self, data: int):
        assert data != None
        assert type(data) is int
        assert data > 0

        self.bytesValue = data
        self.flag[0] = bool(data & self.ACK)
        self.flag[1] = bool(data & self.SYN)
        self.flag[2] = bool(data & self.FIN)
        return self

    def reset(self):
        self.bytesValue = 0b00000000
        self.flag = [False, False, False]
        return self

    def ack(self):
        self.bytesValue |= self.ACK
        self.flag[0] = True
        return self

    def syn(self):
        self.bytesValue |= self.SYN
        self.flag[1] = True
        return self

    def fin(self):
        self.bytesValue |= self.FIN
        self.flag[2] = True
        return self

    def isSyn(self):
        return bool(self.bytesValue & self.SYN)

    def isAck(self):
        return bool(self.bytesValue & self.ACK)

    def isFin(self):
        return bool(self.bytesValue & self.FIN)

    def __str__(self):
        return ''.join(["1" if self.flag[i] else "0" for i in range(3)])


class Segment:
    def __init__(self):
        self.seqNum = 0
        self.ackNum = 0
        self.flag = SegmentFlag()
        self.checksum = 0
        self.data = b''

    def __str__(self):
        return f"SeqNum: {self.seqNum}  | AckNum: {self.ackNum}\nFlags: {self.flag} | Checksum: {self.checksum}\nData: {len(self.data)} bytes"

    def calculateChecksum(self):
        assert self.flag != None

        result = 0x0000
        result = (result + self.seqNum) & 0xFFFF
        result = (result + self.ackNum) & 0xFFFF
        result = (result + self.flag.getBytes()) & 0xFFFF
        result = (result + self.checksum) & 0xFFFF
        for i in range(0, len(self.data), 2):
            piece = self.data[i:i+2]
            if len(piece) == 1:
                piece += struct.pack("x")
            chunk = struct.unpack("H", piece)[0]
            result = (result + chunk) & 0xFFFF
        result = 0xFFFF - result
        return result

    def setSequenceNumber(self, seqNum: int):
        self.seqNum = seqNum
        self.checksum = self.calculateChecksum()
        return self

    def setAcknowledgeNumber(self, ackNum: int):
        self.ackNum = ackNum
        self.checksum = self.calculateChecksum()
        return self

    def setFlag(self, flag: list[str]):
        assert flag != None
        assert type(flag) is list
        assert len(flag) > 0

        newFlag = SegmentFlag()
        for i in flag:
            ilowered = i.lower()
            assert (ilowered == 'ack' or ilowered ==
                    'syn' or ilowered == 'fin')

            if (ilowered == 'ack'):
                newFlag = newFlag.ack()
            elif (ilowered == 'syn'):
                newFlag = newFlag.syn()
            elif (ilowered == 'fin'):
                newFlag = newFlag.fin()

        self.flag = newFlag
        self.checksum = self.calculateChecksum()
        return self

    def setPayload(self, data: bytes):
        self.data = data
        self.checksum = self.calculateChecksum()
        return self

    def fromBytes(self, data: bytes):

        # IIBxH : 4(seqnum) 4(acknum) 1(flag) 1(padding) 2(checksum)
        unpacked = struct.unpack("IIBxH", data[0:12])
        self.seqNum = unpacked[0]
        self.acknowledgeNumber = unpacked[1]
        self.flag.setBytes(unpacked[2])
        self.checksum = unpacked[3]

        self.data = data[12:]

        self.checksum = self.calculateChecksum()
        return self

    def getBytes(self):
        result = b''

        # 4
        result += struct.pack("I", self.seqNum)
        result += struct.pack("I", self.ackNum)

        # 1
        result += struct.pack("B", self.flag.getBytes())

        # padding
        result += struct.pack("x")

        # 2
        result += struct.pack("H", self.checksum)

        # 0-32768
        result += self.data
        return result

    def isValid(self):
        return self.checksum == 0x0000
