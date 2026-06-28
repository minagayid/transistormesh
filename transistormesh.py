# ponytail: minimal working prototype — just enough to validate spec

import os
import struct
from typing import Dict, Tuple

META_CODES = {
    0x1: "english",
    0x2: "arabic",
    0x3: "numbers",
    0x4: "symbols",
    0x5: "image",
    0x6: "audio",
}


class CellCube:
    """
    16x16x16 cube: Z0 metadata plane, Z1-Z15 data planes.
    Each cell stores 1 bit; bytes packed across linearized x,y,z cells.
    """

    def __init__(self, size: int = 16):
        self.size = size
        self.meta_plane = 0
        self.cells: Dict[Tuple[int, int, int], int] = {}

    def index(self, x: int, y: int, z: int) -> int:
        return (x + y * self.size + z * self.size * self.size)

    def write_byte(self, x: int, y: int, z: int, byte: int) -> None:
        if byte not in (0, 1):
            raise ValueError("cell stores 1 bit only")
        self.cells[(x, y, z)] = byte

    def read_byte(self, x: int, y: int, z: int) -> int:
        return self.cells.get((x, y, z), 0)

    def tag_metadata(self, x: int, y: int, code: int) -> None:
        if code not in META_CODES:
            raise ValueError(f"unknown metadata code {code:#x}")
        # 4-bit code across four neighboring metadata cells
        for bit in range(4):
            z = self.meta_plane
            self.write_byte(x + bit, y, z, (code >> bit) & 1)

    def metadata_at(self, x: int, y: int) -> int:
        code = 0
        for bit in range(4):
            code |= self.read_byte(x + bit, y, self.meta_plane) << bit
        return code

    def capacity_bytes(self) -> int:
        data_planes = self.size - 1
        return (self.size * self.size * data_planes) // 8

    def store(self, data: bytes, lang: int = 0x3) -> None:
        if len(data) > self.capacity_bytes() - 2:
            raise ValueError("payload leaves no room for length prefix")

        self._write_u16(len(data))
        for i, byte_val in enumerate(data):
            for bit in range(8):
                region = 16 + i * 8 + bit  # skip metadata layer
                x = region % self.size
                y = (region // self.size) % self.size
                z = 1 + (region // (self.size * self.size))
                self.write_byte(x, y, z, (byte_val >> bit) & 1)

        # stamp metadata into first x,y tile
        for i in range(self.size):
            if (i, 0, self.meta_plane) not in self.cells:
                self.tag_metadata(i, 0, lang)

    def _write_u16(self, value: int) -> None:
        for bit in range(16):
            x = self.size - 1 - bit // self.size
            y = bit % self.size
            self.write_byte(x, y, self.meta_plane, (value >> bit) & 1)

    def _read_u16(self) -> int:
        value = 0
        for bit in range(16):
            x = self.size - 1 - bit // self.size
            y = bit % self.size
            value |= self.read_byte(x, y, self.meta_plane) << bit
        return value

    def load(self) -> bytes:
        length = self._read_u16()
        regions = 16 + length * 8
        out = bytearray()
        byte_buf = 0
        bit_i = 0

        for region in range(16, regions):
            x = region % self.size
            y = (region // self.size) % self.size
            z = 1 + (region // (self.size * self.size))
            bit = self.read_byte(x, y, z)
            byte_buf |= bit << bit_i
            bit_i += 1
            if bit_i == 8:
                out.append(byte_buf)
                byte_buf = 0
                bit_i = 0

        return bytes(out)

    def __repr__(self) -> str:
        return f"<Cube {self.size}³ type={META_CODES.get(self.metadata_at(0,0), '??')} cells={len(self.cells)}>"


def demo():
    cube = CellCube()
    msg = b"Mesh"
    cube.store(msg, lang=0x5)
    print(cube)
    print("capacity:", cube.capacity_bytes(), "bytes")
    print("payload loaded:", cube.load())


if __name__ == "__main__":
    demo()
