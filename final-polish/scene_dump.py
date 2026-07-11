#!/usr/bin/env python3
"""Full recursive chunk-tree dump of ShellMapSHW.map: the whole scene, not just
ObjectsList names. Reveals players/sides, teams, scripts (attack waves), camera,
waypoints, and each Object's position + Dict, so we can design the showcase."""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, HERE)
from bigfile import read_big, find_entry
from refpack import strip_ear, refpack_decompress

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
MAP_PATH = "Maps\\ShellMapSHW\\ShellMapSHW.map"

src = read_big(os.path.join(SPE, "!Shw_maps.big"))
ent = find_entry(src, MAP_PATH)
stream, ear_size = strip_ear(ent.data)
buf, _ = refpack_decompress(stream)
assert buf[:4] == b"CkMp"

pos = 4
(count,) = struct.unpack_from("<i", buf, pos); pos += 4
id2name = {}
for _ in range(count):
    ln = buf[pos]; pos += 1
    id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
    pos += ln + 4
DATA_START = pos
print("symbol table (%d chunk types):" % count)
for cid, nm in sorted(id2name.items()):
    print("   %3d  %s" % (cid, nm))

# recursive walk: print tree with sizes; recurse into container-ish chunks
CONTAINERS = {"ObjectsList", "SidesList", "PolygonTriggers", "ScriptsPlayers",
              "PlayerScriptsList", "ScriptList", "ScriptGroup", "Teams",
              "WorldInfo", "LibraryMapLists"}
type_counts = {}
def walk(start, end, depth, path):
    p = start
    while p + 10 <= end:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        name = id2name.get(cid)
        if name is None or dsize < 0 or p + 10 + dsize > end:
            if depth == 0:
                print("  " * depth + "<stop: bad chunk at %d>" % p)
            return
        ds = p + 10; de = ds + dsize
        type_counts[name] = type_counts.get(name, 0) + 1
        if depth <= 2:
            print("  " * depth + "%s v%d size=%d @%d" % (name, ver, dsize, p))
        if name in CONTAINERS or depth < 2:
            walk(ds, de, depth + 1, path + "/" + name)
        p = de

print("\n== chunk tree (top 3 levels) ==")
walk(DATA_START, len(buf), 0, "")

print("\n== chunk type totals ==")
for n, k in sorted(type_counts.items(), key=lambda x: -x[1]):
    print("   %5d  %s" % (k, n))
