#!/usr/bin/env python3
"""Positions of the friendly China combat units (anchor for the showcase
cluster) + camera-target waypoints, decoding each Object's Dict enough to read
originalOwner / objectName / waypointName."""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon")); sys.path.insert(0, HERE)
from bigfile import read_big, find_entry
from refpack import strip_ear, refpack_decompress

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
src = read_big(os.path.join(SPE, "!Shw_maps.big"))
ent = find_entry(src, "Maps\\ShellMapSHW\\ShellMapSHW.map")
stream, _ = strip_ear(ent.data)
buf, _ = refpack_decompress(stream)

pos = 4
(count,) = struct.unpack_from("<i", buf, pos); pos += 4
id2name = {}
for _ in range(count):
    ln = buf[pos]; pos += 1
    id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
    pos += ln + 4
DATA_START = pos

# Dict format (ZH): u16 pairCount, then each pair:
#   u32 packed (keyId<<8 | type), value by type:
#   type 0=bool(1), 1=int(4), 2=real(4), 3=asciistring(u16 len+bytes), 4=unicode(u16 len+2*bytes)
def read_dict(b, p):
    (npairs,) = struct.unpack_from("<H", b, p); p += 2
    d = {}
    for _ in range(npairs):
        (packed,) = struct.unpack_from("<I", b, p); p += 4
        keyid = packed >> 8; typ = packed & 0xFF
        if typ == 0: v = b[p]; p += 1
        elif typ in (1, 2): v = struct.unpack_from("<I", b, p)[0]; p += 4
        elif typ == 3:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+sl].decode("latin-1"); p += sl
        elif typ == 4:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+2*sl]; p += 2*sl
        else: return d, p, False
        d[keyid] = v
    return d, p, True

combat = ("BattleMaster", "TroopCrawler", "GattlingCannon", "TankHunter",
          "Redguard", "InfernoCannon", "Helix", "TankECM", "TankDragon")
found = {c: [] for c in combat}
def walk(start, end):
    p = start
    while p + 10 <= end:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        name = id2name.get(cid)
        if name is None or dsize < 0 or p + 10 + dsize > end: return
        ds = p + 10; de = ds + dsize
        if name == "Object":
            x, y, z, ang = struct.unpack_from("<ffff", buf, ds)
            (slen,) = struct.unpack_from("<H", buf, ds + 20)
            tn = buf[ds+22:ds+22+slen].decode("latin-1")
            dstart = ds + 22 + slen
            d, dend, ok = read_dict(buf, dstart)
            owner = d.get(126)  # originalOwner keyid guess (varies) -- print raw
            for c in combat:
                if c in tn:
                    found[c].append((x, y, z, ang, tn, len(found[c])==0 and d or None))
        if name == "ObjectsList":
            walk(ds, de)
        p = de
walk(DATA_START, len(buf))

for c in combat:
    lst = found[c]
    if not lst: continue
    xs = [o[0] for o in lst]; ys = [o[1] for o in lst]
    print("%-16s n=%2d  centroid=(%d,%d)  X:[%d..%d] Y:[%d..%d]"
          % (c, len(lst), sum(xs)/len(xs), sum(ys)/len(ys),
             min(xs), max(xs), min(ys), max(ys)))
    for (x, y, z, ang, tn, d) in lst[:3]:
        print("     (%d,%d,%d) ang=%.2f %s" % (x, y, z, ang, tn))
        if d: print("       dict keyids:", sorted(d.keys()), {k:(v if not isinstance(v,(bytes,)) else '<bytes>') for k,v in list(d.items())[:12]})
