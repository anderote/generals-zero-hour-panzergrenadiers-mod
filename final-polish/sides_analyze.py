#!/usr/bin/env python3
"""Parse SidesList: players (name/faction/allies/enemies) + teams (name/owner),
so we can pick a China team that is hostile to the attackers near (1181,575)."""
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

def read_dict(b, p):
    (npairs,) = struct.unpack_from("<H", b, p); p += 2
    d = {}
    for _ in range(npairs):
        (packed,) = struct.unpack_from("<I", b, p); p += 4
        keyid = packed >> 8; typ = packed & 0xFF
        if typ == 0: v = b[p]; p += 1
        elif typ == 1: v = struct.unpack_from("<i", b, p)[0]; p += 4
        elif typ == 2: v = struct.unpack_from("<f", b, p)[0]; p += 4
        elif typ == 3:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+sl].decode("latin-1"); p += sl
        elif typ == 4:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+2*sl].decode("latin-1", "replace"); p += 2*sl
        else: raise ValueError("bad type %d" % typ)
        d[keyid] = v
    return d, p

# find SidesList top-level chunk
p = DATA_START
sides_ds = sides_de = None
while p + 10 <= len(buf):
    cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
    nm = id2name.get(cid)
    if nm is None or dsize < 0 or p+10+dsize > len(buf): break
    ds = p+10; de = ds+dsize
    if nm == "SidesList":
        sides_ds, sides_de, sides_ver = ds, de, ver
        print("SidesList v%d @%d size=%d" % (ver, p, dsize))
    p = de

# SidesList format (ZH): int32 numSides, then per side: Dict; then int32 numTeams, then per team: Dict.
# But actually in ZH the SidesList also has BuildLists. Let's parse defensively.
p = sides_ds
(numSides,) = struct.unpack_from("<i", buf, p); p += 4
print("numSides =", numSides)
for i in range(numSides):
    d, p = read_dict(buf, p)
    # then build list: int32 numBuildings, each = name string + ... ; skip via count
    (numBuild,) = struct.unpack_from("<i", buf, p); p += 4
    # each buildlist entry (ZH): AsciiString name, AsciiString templateName, then a bunch of fields.
    # Format is complex; parse one field at a time. Building list entry:
    #  AsciiString buildingName; AsciiString templateName; Coord3D loc(3 float); float angle;
    #  Bool initiallyBuilt; UnsignedInt numRebuilds; AsciiString script; Int health;
    #  Bool whiner; Bool unsellable; Bool repairable; ... version-dependent. Risky.
    name = d.get(1) or d.get(2)
    pn = None
    # print key dict fields
    print("  side[%d] dict keyids=%s" % (i, sorted(d.keys())))
    for k,v in d.items():
        if isinstance(v,str) and v:
            print("       key %d = %r" % (k, v))
    if numBuild != 0:
        print("       (numBuildings=%d -- stopping detailed parse, structure version-specific)" % numBuild)
        break
print("\n-- attempting team parse only if buildlists empty --")
