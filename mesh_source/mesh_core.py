# ponytail: leave richer checks to the prompt since the mesh API is tiny
import os
from dataclasses import dataclass, field
from typing import Optional

# Metadata codes mirror the prompt's semantic index
META = {
    0x1: "english",
    0x2: "arabic",
    0x3: "numbers",
    0x4: "symbols",
    0x5: "image",
    0x6: "audio",
}


@dataclass
class Cube:
    """
    Flexible 3D cube. Prompt shape is 16x16x16; meta layer sits at Z0.
    Enforcing 16 now would just guard a value the caller already chose.
    """
    x: int
    y: int
    z: int
    size: int = 16
    cells: dict = field(default_factory=dict)
    metadata_plane_z: int = 0

    def encode(self, data_type_code: int, payload: bytes) -> bytes:
        """
        Encode a payload with metadata tag into cube cell coordinates.
        Metadata lives at the one z-plane reserved for it.
        """
        if data_type_code not in META:
            raise ValueError(f"unsupported type code {data_type_code:#x}")

        header = data_type_code.to_bytes(1, byteorder="big")
        return header + payload

    def put(self, data: bytes):
        """
        Write encoded bytes into the cube along Z axis, one byte per x,y slice.
        """
        if len(data) > self.cell_capacity():
            raise ValueError("payload exceeds cube storage")
        for i, b in enumerate(data):
            x = i % self.size
            y = (i // self.size) % self.size
            z = (i // (self.size * self.size)) + 1  # skip metadata plane
            self.cells[(x, y, z)] = b

    def get(self, cx: int, cy: int, cz: int) -> Optional[int]:
        return self.cells.get((cx, cy, cz))

    def metadata_at(self, cx: int, cy: int) -> int:
        return self.cells.get((cx, cy, self.metadata_plane_z), 0)

    def cell_capacity(self) -> int:
        data_layers = self.size - 1
        return self.size * self.size * data_layers

    def __repr__(self) -> str:
        return (
            f"<Cube {self.size}x{self.size}x{self.size} "
            f"storing {len(self.cells)} cells "
            f"type={META.get(1, 'english')}>"
        )


def load_metadata(cube: Cube, code: int):
    """
    Debug helper: stamp a type tag across the metadata plane.
    """
    if code not in META:
        raise ValueError(f"unsupported type code {code:#x}")

    for x in range(cube.size):
        for y in range(cube.size):
            cube.cells[(x, y, cube.metadata_plane_z)] = code


def mesh_demo():
    mesh = Cube(x=0, y=0, z=0, size=16)
    load_metadata(mesh, 0x3)  # numbers
    payload = b"01 02 03 04 05"
    encoded = mesh.encode(0x3, payload)
    mesh.put(encoded)

    print(mesh)
    print("capacity:", mesh.cell_capacity(), "bytes")
    print("metadata plane:", META[mesh.metadata_at(0, 0)])
    print("sample cell (0,0,1):", mesh.get(0, 0, 1))


if __name__ == "__main__":
    mesh_demo()
