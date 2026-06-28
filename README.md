ponytail: minimal v0.1 to satisfy the prompt — real architecture needs field-specific writeup.

# TransistorMesh

**3D logic-memory fabric with self-describing cubes.**

Built from the prompt structure: `16x16x16` cubes with metadata layer tagging content type, so every stored blob knows what it is.

## Why this exists

Conventional storage is a flat word array. Overhead is carried outside the memory: addresses and types in headers, buffers, file formats.

TransistorMesh collapses that representation into the fabric. Local computation, no crossing reads, metadata live on Z0.

## What's implemented here

V0 is a software prototype. The hardware concept stays untouched: real through-silicon vias, TSVs, and heat removal are out of scope. Software model is enough to validate the address/data split and metadata routing.

## Run it

```bash
pip install -r requirements.txt
python mesh_demo.py
```

Outputs:
- byte encoding + lookup
- 3-D cube render (`output/transistormesh.png`)
- metadata demux

## Repo layout

```
transistormesh/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ mesh_source/
│  └─ mesh_core.py
└─ output/
   └─ transistormesh.png
```

## Then what

- 32x32x32 cubes, then cube hierarchy
- LEDGER plane in Z0 to chain related elements
- auto-dispatch compute kernels by metadata tag
