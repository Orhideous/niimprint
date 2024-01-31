from dataclasses import dataclass


@dataclass
class NiimbotPacket:
    kind: int
    data: bytes

    @classmethod
    def from_bytes(cls, pkt):
        assert pkt[:2] == b"\x55\x55"
        assert pkt[-2:] == b"\xaa\xaa"
        kind = pkt[2]
        length = pkt[3]
        data = pkt[4 : 4 + length]

        checksum = kind ^ length
        for i in data:
            checksum ^= i
        assert checksum == pkt[-3]

        return cls(kind, data)

    def to_bytes(self):
        checksum = self.kind ^ len(self.data)
        for i in self.data:
            checksum ^= i
        return bytes(
            (0x55, 0x55, self.kind, len(self.data), *self.data, checksum, 0xAA, 0xAA)
        )
