import socket
from typing import Protocol

import serial


class BaseTransport(Protocol):
    def read(self, length: int) -> bytes:
        ...

    def write(self, data: bytes):
        ...


class BluetoothTransport(BaseTransport):
    def __init__(self, address: str):
        self._sock = socket.socket(
            socket.AF_BLUETOOTH,
            socket.SOCK_STREAM,
            socket.BTPROTO_RFCOMM,
        )
        self._sock.connect((address, 1))

    def read(self, length: int) -> bytes:
        return self._sock.recv(length)

    def write(self, data: bytes):
        self._sock.send(data)


class SerialTransport(BaseTransport):
    def __init__(self, port: str):
        self._serial = serial.Serial(port=port, baudrate=115200, timeout=0.5)

    def read(self, length: int) -> bytes:
        return self._serial.read(length)

    def write(self, data: bytes):
        self._serial.write(data)
