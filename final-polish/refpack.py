"""EA RefPack decompressor (canonical algorithm). Also handles the engine's
8-byte 'EAR\\0'+LE-size wrapper (COMPRESSION_REFPACK)."""
import struct

def strip_ear(data):
    if data[:4] == b'EAR\x00':
        (usize,) = struct.unpack_from('<I', data, 4)
        return data[8:], usize
    return data, None

def refpack_decompress(stream):
    i = 0
    sig = (stream[0] << 8) | stream[1]; i = 2
    if sig & 0x0100:      # optional compressed-size field present
        i += 3
    outsize = (stream[i] << 16) | (stream[i+1] << 8) | stream[i+2]; i += 3
    out = bytearray()
    n = len(stream)
    while i < n:
        b0 = stream[i]; i += 1
        if b0 < 0x80:
            b1 = stream[i]; i += 1
            numplain = b0 & 0x03
            out += stream[i:i+numplain]; i += numplain
            numcopy = ((b0 & 0x1c) >> 2) + 3
            offset = ((b0 & 0x60) << 3) + b1 + 1
        elif b0 < 0xc0:
            b1 = stream[i]; b2 = stream[i+1]; i += 2
            numplain = (b1 >> 6) & 0x03
            out += stream[i:i+numplain]; i += numplain
            numcopy = (b0 & 0x3f) + 4
            offset = ((b1 & 0x3f) << 8) + b2 + 1
        elif b0 < 0xe0:
            b1 = stream[i]; b2 = stream[i+1]; b3 = stream[i+2]; i += 3
            numplain = b0 & 0x03
            out += stream[i:i+numplain]; i += numplain
            numcopy = ((b0 & 0x0c) << 6) + b3 + 5
            offset = ((b0 & 0x10) << 12) + (b1 << 8) + b2 + 1
        elif b0 < 0xfc:
            numplain = ((b0 & 0x1f) << 2) + 4
            out += stream[i:i+numplain]; i += numplain
            numcopy = 0; offset = 0
        else:
            numplain = b0 & 0x03
            out += stream[i:i+numplain]; i += numplain
            break
        for _ in range(numcopy):
            out.append(out[-offset])
    return bytes(out), outsize

if __name__ == '__main__':
    import sys, hashlib
    raw = open(sys.argv[1], 'rb').read()
    stream, usize = strip_ear(raw)
    out, decl = refpack_decompress(stream)
    print('declared uncompressed size (EAR):', usize, ' (refpack hdr):', decl,
          ' actual:', len(out), ' magic:', out[:4])
    print('md5:', hashlib.md5(out).hexdigest())
