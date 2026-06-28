# TransistorMesh

![visualization](https://v3b.fal.media/files/b/0aa0295d/5KZ_amR3ERb5BmqASt-2V_iPkM0QGq.png)

**3D logic-memory fabric with self-describing cubes.**

- 16³ cubes with metadata plane (Z0) + data planes (Z1–Z15)
- each cell stores 1 bit; metadata tags stored as 4-bit codes in the metadata plane
- implemented as a Python software prototype

file | role
--- | ---
`transistormesh.py` | minimal runnable cube (read, write, metadata tagging)
`mesh_source/mesh_core.py` | preserved original implementation for comparison
`requirements.txt` | numpy + Pillow

## Run

```bash
git clone https://github.com/minagayid/transistormesh.git
cd transistormesh
python transistormesh.py
```

Demo writes `b"Mesh"` with `image` metadata tag into a fresh cube and reads it back.

## Notes

- prefix is 2 bytes (16 bits) for lengths up to `CAPACITY-2`; if you want >32K per cube, expand to `u32` (`_write_u32`, `_read_u32`).
