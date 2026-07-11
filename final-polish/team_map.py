#!/usr/bin/env python3
"""Enumerate every originalOwner team on the shellmap: unit count, centroid,
sample templates, and whether the Object Dict carries key 139 (aggressiveness).
Used to pick the attacker team (hostile to teamPlyrGLAYellow) + donor attackers."""
import os, sys, struct, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon")); sys.path.insert(0, HERE)
import build_shellmap_showcase as B
from bigfile import read_big, find_entry
from refpack import strip_ear, refpack_decompress

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
src = read_big(os.path.join(SPE, "!Shw_maps.big"))
ent = find_entry(src, "Maps\\ShellMapSHW\\ShellMapSHW.map")
stream, _ = strip_ear(ent.data); buf, _ = refpack_decompress(stream)
id2name, name2id, ds, top = B.parse_map(buf)
ol = [t for t in top if t["nm"] == "ObjectsList"][0]
objs = B.parse_objects(buf, ol)

from collections import defaultdict, Counter
teams = defaultdict(list)
for o in objs:
    owner = B.s(o["dictmap"].get(126, b""))
    x, y, z, ang = struct.unpack_from("<ffff", buf, o["ds"])
    keys = [k for (k, _, _) in o["pairs"]]
    teams[owner].append((o["tn"], x, y, 139 in keys, keys))

def is_combat(tn):
    non = ("Waypoint","Tree","Bush","Rock","Fence","Wall","Road","Tent","Barrel",
           "Drum","Light","Crate","Cargo","Scorch","Banner","Vender","Trap","Ammo",
           "PowerPlant","Sandbag","Net","Prop","Pine","Palm","Willow","Bonsai","Picket")
    return not any(n in tn for n in non)

print("== teams by TOTAL objects (combat-ish count in parens) ==")
for owner, lst in sorted(teams.items(), key=lambda kv: -len(kv[1])):
    combat = [u for u in lst if is_combat(u[0])]
    if not combat and len(lst) < 5: continue
    xs = [u[1] for u in combat] or [u[1] for u in lst]
    ys = [u[2] for u in combat] or [u[2] for u in lst]
    has139 = any(u[3] for u in combat)
    top3 = Counter(u[0] for u in combat).most_common(3)
    print("  %-34s total=%3d combat=%3d centroid=(%5d,%5d) key139=%s  %s" % (
        owner or "<none>", len(lst), len(combat),
        sum(xs)/len(xs), sum(ys)/len(ys), has139,
        ", ".join("%s×%d" % (t.split("_")[-1], k) for t, k in top3)))

# enemy density near our core placement (1181,575): count combat units by team within r
print("\n== combat units within r=350 of (1181,575), grouped by team ==")
cx, cy = 1181, 575
near = defaultdict(int); neartmpl = defaultdict(Counter)
for o in objs:
    if not is_combat(o["tn"]): continue
    x, y, z, a = struct.unpack_from("<ffff", buf, o["ds"])
    if math.hypot(x-cx, y-cy) <= 350:
        owner = B.s(o["dictmap"].get(126, b""))
        near[owner] += 1; neartmpl[owner][o["tn"]] += 1
for owner, n in sorted(near.items(), key=lambda kv: -kv[1]):
    print("  %-34s %3d  %s" % (owner or "<none>", n,
        ", ".join("%s×%d" % (t.split("_")[-1], k) for t, k in neartmpl[owner].most_common(4))))

# GLA / USA attacker templates present anywhere + their owner teams + key139
print("\n== GLA/USA-flavored attacker templates present + owner teams ==")
attack_kw = ("GLA","Rebel","Technical","Buggy","Terrorist","Toxin","Rocket","Jarmen",
             "Ranger","America","Humvee","MI8","Comanche","Gunship","Marauder","Scorpion","RPG")
seen = Counter()
for o in objs:
    tn = o["tn"]
    if any(k in tn for k in attack_kw) and is_combat(tn):
        owner = B.s(o["dictmap"].get(126, b""))
        seen[(tn, owner, 139 in [k for (k,_,_) in o["pairs"]])] += 1
for (tn, owner, k139), n in seen.most_common(40):
    print("  %-34s owner=%-24s key139=%s  ×%d" % (tn, owner, k139, n))
