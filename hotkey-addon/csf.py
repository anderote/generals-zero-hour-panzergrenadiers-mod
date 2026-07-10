"""CSF (compiled string file) reader/writer for C&C Generals Zero Hour.

Format (verified against the GeneralsX engine source,
Core/GameEngine/Source/GameClient/GameText.cpp — CSFHeader struct at
lines 110-119, getCSFInfo() and parseCSF() at lines 917-1120):

    Header, 6 x i32 little-endian (24 bytes):
        id          on-disk bytes b" FSC" (the source defines
                    CSF_ID = ('C'<<24)|('S'<<16)|('F'<<8)|' ' and reads it
                    as a native little-endian int)
        version     3
        num_labels  count of label records
        num_strings total count of string records (may be < num_labels if
                    some labels have zero strings)
        skip        extra bytes to skip after the header before the first
                    label record (0 in the shipped file)
        langid      language id

    Then num_labels label records:
        i32  id           on-disk b" LBL"
        i32  num_strings  string records under this label
        i32  label_len
        label_len bytes   ASCII label, e.g. "CONTROLBAR:ConstructGLAWorker"

        then num_strings string records:
            i32  id       on-disk b" RTS" (plain) or b"WRTS" (with wave)
            i32  char_count
            char_count*2 bytes: UTF-16LE text where every byte is
                    bitwise-NOTed (engine: *ptr = ~*ptr per 16-bit unit,
                    which equals XOR 0xFF on each byte)
            [b"WRTS" only] i32 wave_len + wave_len ASCII bytes (speech name)

Round-trip safety: parse() followed by serialize() reproduces the input
byte-identically (verified for the unmodified shipped generals.csf).
"""

import struct
from typing import List, Optional

CSF_MAGIC = b" FSC"
LBL_MAGIC = b" LBL"
STR_MAGIC = b" RTS"
STRW_MAGIC = b"WRTS"


def _mask(data: bytes) -> bytes:
    """Apply/remove the bitwise-NOT obfuscation (self-inverse)."""
    return bytes(b ^ 0xFF for b in data)


class CsfString:
    __slots__ = ("text", "wave")

    def __init__(self, text: str, wave: Optional[bytes] = None):
        self.text = text          # decoded, de-obfuscated text
        self.wave = wave          # raw ASCII bytes of speech name, or None


class CsfLabel:
    __slots__ = ("name", "strings")

    def __init__(self, name: bytes, strings: List[CsfString]):
        self.name = name          # raw ASCII label bytes
        self.strings = strings


class CsfFile:
    def __init__(self, version: int, langid: int, skip_bytes: bytes,
                 labels: List[CsfLabel]):
        self.version = version
        self.langid = langid
        self.skip_bytes = skip_bytes   # bytes covered by header.skip
        self.labels = labels

    @property
    def num_strings(self) -> int:
        return sum(len(l.strings) for l in self.labels)


def parse(data: bytes) -> CsfFile:
    if data[:4] != CSF_MAGIC:
        raise ValueError(f"Not a CSF file (magic={data[:4]!r})")
    _, version, num_labels, num_strings, skip, langid = \
        struct.unpack_from("<6i", data, 0)
    pos = 24
    skip_bytes = data[pos:pos + skip]
    pos += skip

    labels: List[CsfLabel] = []
    for _ in range(num_labels):
        if data[pos:pos + 4] != LBL_MAGIC:
            raise ValueError(f"Expected label record at offset {pos}")
        n_str, label_len = struct.unpack_from("<ii", data, pos + 4)
        pos += 12
        name = data[pos:pos + label_len]
        pos += label_len

        strings: List[CsfString] = []
        for _ in range(n_str):
            sid = data[pos:pos + 4]
            if sid not in (STR_MAGIC, STRW_MAGIC):
                raise ValueError(f"Expected string record at offset {pos}")
            (char_count,) = struct.unpack_from("<i", data, pos + 4)
            pos += 8
            text = _mask(data[pos:pos + char_count * 2]).decode("utf-16-le")
            pos += char_count * 2
            wave = None
            if sid == STRW_MAGIC:
                (wave_len,) = struct.unpack_from("<i", data, pos)
                pos += 4
                wave = data[pos:pos + wave_len]
                pos += wave_len
            strings.append(CsfString(text, wave))
        labels.append(CsfLabel(name, strings))

    if pos != len(data):
        raise ValueError(f"{len(data) - pos} trailing bytes after last label")
    if num_strings != sum(len(l.strings) for l in labels):
        raise ValueError("header num_strings mismatch")
    return CsfFile(version, langid, skip_bytes, labels)


def serialize(csf: CsfFile) -> bytes:
    out = bytearray()
    out += CSF_MAGIC
    out += struct.pack("<5i", csf.version, len(csf.labels), csf.num_strings,
                       len(csf.skip_bytes), csf.langid)
    out += csf.skip_bytes
    for label in csf.labels:
        out += LBL_MAGIC
        out += struct.pack("<ii", len(label.strings), len(label.name))
        out += label.name
        for s in label.strings:
            encoded = s.text.encode("utf-16-le")
            out += STRW_MAGIC if s.wave is not None else STR_MAGIC
            out += struct.pack("<i", len(encoded) // 2)
            out += _mask(encoded)
            if s.wave is not None:
                out += struct.pack("<i", len(s.wave))
                out += s.wave
    return bytes(out)


if __name__ == "__main__":
    import sys
    raw = open(sys.argv[1], "rb").read()
    csf = parse(raw)
    ok = serialize(csf) == raw
    print(f"{len(csf.labels)} labels, {csf.num_strings} strings, "
          f"round-trip byte-identical: {ok}")
