#!/usr/bin/env python3
"""Extract exact structural facts for the showcase build:
 - ObjectsList top-level chunk header position, data start/end, object count
 - trailing top-level chunks after ObjectsList (for byte-identity assertion)
 - a donor VEHICLE object chunk and a donor INFANTRY object chunk (raw bytes)
 - teams of combat units near the armor centroid (1181,575)
"""
import os, sys, struct, math
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
    (npairs,) = struct.unpack_from("<H", b, p); p0=p; p += 2
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
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+2*sl]; p += 2*sl
        else: raise ValueError("bad dict type %d @%d" % (typ,p))
        d[keyid] = v
    return d, p

# top-level walk
p = DATA_START
toplevel = []
while p + 10 <= len(buf):
    cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
    nm = id2name.get(cid)
    if nm is None or dsize < 0 or p+10+dsize > len(buf): break
    toplevel.append((nm, ver, dsize, p, p+10, p+10+dsize))
    p = p+10+dsize
print("== TOP-LEVEL CHUNKS ==")
for (nm,ver,dsize,hp,ds,de) in toplevel:
    print("  %-16s v%d size=%-8d hdr@%-8d data[%d..%d]" % (nm,ver,dsize,hp,ds,de))
print("  buffer end =", len(buf), " last chunk de =", toplevel[-1][5])

# ObjectsList
ol = [t for t in toplevel if t[0]=="ObjectsList"][0]
ol_nm, ol_ver, ol_dsize, ol_hp, ol_ds, ol_de = ol
print("\nObjectsList hdr@%d data[%d..%d] size=%d ver=%d" % (ol_hp, ol_ds, ol_de, ol_dsize, ol_ver))

# walk objects inside ObjectsList; collect chunk byte-ranges + parsed dict
objects = []
p = ol_ds
while p + 10 <= ol_de:
    cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
    nm = id2name.get(cid)
    if nm != "Object":
        print("  non-Object chunk inside ObjectsList:", nm, "ver",ver,"size",dsize,"@",p)
        p = p+10+dsize; continue
    ds = p+10; de = ds+dsize
    x,y,z,ang = struct.unpack_from("<ffff", buf, ds)
    flags, = struct.unpack_from("<i", buf, ds+16)
    (slen,) = struct.unpack_from("<H", buf, ds+20)
    tn = buf[ds+22:ds+22+slen].decode("latin-1")
    dstart = ds+22+slen
    d, dend = read_dict(buf, dstart)
    assert dend == de, "dict end %d != chunk end %d for %s" % (dend,de,tn)
    objects.append(dict(hp=p, ds=ds, de=de, ver=ver, dsize=dsize, x=x,y=y,z=z,ang=ang,
                        flags=flags, tn=tn, dict=d, dstart=dstart, dend=dend))
    p = de
print("Object chunks inside ObjectsList:", len(objects))
assert p == ol_de, "walk didn't end exactly at ObjectsList data end (%d vs %d)" % (p, ol_de)
print("walk ended exactly at ObjectsList data end: OK")

# ver histogram
from collections import Counter
print("Object versions:", Counter(o["ver"] for o in objects))
print("flags histogram (top):", Counter(o["flags"] for o in objects).most_common(5))

# nearby armor cluster teams
cx,cy = 1181,575
print("\n== combat-ish units within r=260 of (1181,575) ==")
COMBAT=("BattleMaster","Gattling","TankHunter","Redguard","Inferno","TankECM",
        "TankDragon","Emperor","Nuke","Buratino","ShockTrooper","TroopCrawler")
near=[]
for o in objects:
    if any(c in o["tn"] for c in COMBAT):
        dd=math.hypot(o["x"]-cx,o["y"]-cy)
        if dd<=260: near.append((dd,o))
near.sort()
for dd,o in near:
    print("  d=%3d (%5d,%5d) ang=%5.2f %-32s owner=%s uid=%r name=%r ver=%d flags=%d" % (
        dd,o["x"],o["y"],o["ang"],o["tn"],o["dict"].get(126),o["dict"].get(127),
        o["dict"].get(129,""),o["ver"],o["flags"]))

# pick donors: a vehicle (BattleMaster) and an infantry (Redguard) with FULL dict (has 129)
def pick(pred):
    for o in objects:
        if pred(o): return o
    return None
veh = pick(lambda o: "Spec_ChinaTankBattleMaster"==o["tn"])
inf = pick(lambda o: "Spec_ChinaInfantryRedguard"==o["tn"] and 129 in o["dict"])
print("\n== DONOR vehicle:", veh["tn"], "ver",veh["ver"],"dsize",veh["dsize"],"dictkeys",sorted(veh["dict"].keys()))
print("   dict:", {k:(v if not isinstance(v,bytes) else '<b>') for k,v in veh["dict"].items()})
print("== DONOR infantry:", inf["tn"], "ver",inf["ver"],"dsize",inf["dsize"],"dictkeys",sorted(inf["dict"].keys()))
print("   dict:", {k:(v if not isinstance(v,bytes) else '<b>') for k,v in inf["dict"].items()})

# save raw donor chunk bytes + boundaries to a pickle for the builder
import pickle
save = dict(
    ol_hp=ol_hp, ol_ds=ol_ds, ol_de=ol_de, ol_dsize=ol_dsize, ol_ver=ol_ver,
    id2name=id2name, DATA_START=DATA_START, buflen=len(buf),
    veh_chunk=bytes(buf[veh["hp"]:veh["de"]]),
    inf_chunk=bytes(buf[inf["hp"]:inf["de"]]),
    veh_ver=veh["ver"], inf_ver=inf["ver"],
    nobjects=len(objects),
    toplevel=[(t[0],t[1],t[2],t[3],t[4],t[5]) for t in toplevel],
)
with open(os.path.join(HERE,"scene_facts.pkl"),"wb") as f:
    pickle.dump(save,f)
print("\nsaved scene_facts.pkl")
