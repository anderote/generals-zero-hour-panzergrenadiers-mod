"""BIG archive (BIGF) reader/writer for C&C Generals Zero Hour.

Format (verified against the GeneralsX engine source,
Core/GameEngineDevice/Source/StdDevice/Common/StdBIGFileSystem.cpp,
openArchiveFile(), lines 522-622):

    offset 0   : 4 bytes  magic "BIGF"
    offset 4   : u32 LE   total archive size in bytes
                 (the engine reads this raw with no byte swap; the shipped
                 EnglishZH.big stores its exact file size here little-endian)
    offset 8   : u32 BE   number of contained files (engine calls betoh())
    offset 12  : u32 BE   header size / offset of first file's data
                 (the engine seeks to 0x10 and ignores this field)
    offset 16  : index table, one entry per file:
                     u32 BE  file data offset (absolute)
                     u32 BE  file data size
                     NUL-terminated path string ('\\' separators, e.g.
                     "Data\\English\\generals.csf")
    then       : file data blobs at the recorded offsets.
"""

import struct
from typing import List, Tuple

MAGIC = b"BIGF"


class BigEntry:
    __slots__ = ("path", "data")

    def __init__(self, path: str, data: bytes):
        self.path = path
        self.data = data

    def __repr__(self):
        return f"BigEntry({self.path!r}, {len(self.data)} bytes)"


def read_big(path_or_bytes) -> List[BigEntry]:
    """Read a BIG archive. Accepts a filesystem path or raw bytes."""
    if isinstance(path_or_bytes, (bytes, bytearray)):
        data = bytes(path_or_bytes)
    else:
        with open(path_or_bytes, "rb") as f:
            data = f.read()

    if data[:4] != MAGIC:
        raise ValueError(f"Not a BIGF archive (magic={data[:4]!r})")

    # archive size (LE) is informational; file count and header size are BE
    (num_files,) = struct.unpack_from(">I", data, 8)

    entries = []
    pos = 16
    for _ in range(num_files):
        offset, size = struct.unpack_from(">II", data, pos)
        pos += 8
        end = data.index(b"\x00", pos)
        name = data[pos:end].decode("latin-1")
        pos = end + 1
        entries.append(BigEntry(name, data[offset:offset + size]))
    return entries


def write_big(entries: List[BigEntry]) -> bytes:
    """Serialize entries into a BIGF archive (returns bytes)."""
    table_size = sum(8 + len(e.path.encode("latin-1")) + 1 for e in entries)
    header_size = 16 + table_size  # first file data starts right after table

    # lay out file data
    offsets: List[Tuple[int, int]] = []
    pos = header_size
    for e in entries:
        offsets.append((pos, len(e.data)))
        pos += len(e.data)
    total_size = pos

    out = bytearray()
    out += MAGIC
    out += struct.pack("<I", total_size)   # LE, matches shipped archives
    out += struct.pack(">I", len(entries))
    out += struct.pack(">I", header_size)
    for e, (off, size) in zip(entries, offsets):
        out += struct.pack(">II", off, size)
        out += e.path.encode("latin-1") + b"\x00"
    for e in entries:
        out += e.data
    assert len(out) == total_size
    return bytes(out)


def write_big_file(entries: List[BigEntry], out_path: str) -> None:
    with open(out_path, "wb") as f:
        f.write(write_big(entries))


def find_entry(entries: List[BigEntry], internal_path: str) -> BigEntry:
    """Case-insensitive, separator-insensitive lookup (engine lowercases paths)."""
    want = internal_path.lower().replace("/", "\\")
    for e in entries:
        if e.path.lower().replace("/", "\\") == want:
            return e
    raise KeyError(internal_path)


if __name__ == "__main__":
    import sys
    for e in read_big(sys.argv[1]):
        print(f"{len(e.data):>10}  {e.path}")
