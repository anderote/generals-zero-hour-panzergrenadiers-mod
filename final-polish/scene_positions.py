#!/usr/bin/env python3
"""Dump each Object's position + template, camera targets, and waypoints, so we
can design where to cluster the showcase army (in-battle, in-camera)."""
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
name2id = {v: k for k, v in id2name.items()}
DATA_START = pos

# Object data layout: 3 floats (x,y,z), 1 float angle, 1 int flags, then
# AsciiString template (u16 len + bytes), then Dict.
objs = []
def walk(start, end, ctx):
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
            objs.append((x, y, z, tn, p, dsize))
        if name in ("ObjectsList",):
            walk(ds, de, name)
        p = de
walk(DATA_START, len(buf), "")

# spatial extent
xs = [o[0] for o in objs]; ys = [o[1] for o in objs]
print("objects: %d   X:[%.0f..%.0f]  Y:[%.0f..%.0f]" % (len(objs), min(xs), max(xs), min(ys), max(ys)))

# cluster by coarse grid to find dense battle areas
from collections import defaultdict
cell = defaultdict(list)
for (x, y, z, tn, off, dsz) in objs:
    cell[(int(x)//400, int(y)//400)].append(tn)
print("\n== densest 400x400 cells (likely the battle) ==")
for (gx, gy), lst in sorted(cell.items(), key=lambda kv: -len(kv[1]))[:12]:
    from collections import Counter
    top = Counter(lst).most_common(4)
    print("  cell(%d,%d) center~(%d,%d): %d units  %s" %
          (gx, gy, gx*400+200, gy*400+200, len(lst),
           ", ".join("%s×%d" % (t.split("_")[-1], k) for t, k in top)))

# distinct templates present (Kwai-swapped names in the installed layer differ; this is stock)
from collections import Counter
print("\n== template histogram ==")
for tn, k in Counter(o[3] for o in objs).most_common():
    print("   %4d  %s" % (k, tn))
