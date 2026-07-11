#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZZ0ShellKwai.big -- the FULL "awesome" showcase.

Two operations on the ShockWave main-menu shellmap
(Maps\\ShellMapSHW\\ShellMapSHW.map), both pure-data / non-corrupting:

 (A) RECAST  -- the safe equal-length Spec_/Nuke_ -> Tank_ (Kwai) name swaps on
     the existing China contingent (unchanged from build_shellmap_recast.py).

 (B) SHOWCASE -- ADD a coherent Kwai "panzer company" of ~22 units clustered in
     the armor centroid (~1181,575), owned by teamPlyrGLAYellow (the team that is
     mutually hostile to PlyrGLA -- the GLA attackers -- and that already owns the
     neighbouring China_Ravager BattleMasters / China_Hammer Nuke launchers /
     China_Gattling, so the company fights in the same defending line). New Object
     chunks are appended at the END of ObjectsList's data region; ObjectsList's
     header dataSize is grown; every trailing top-level chunk stays byte-identical
     (only shifted). Objects reference nothing by byte-offset, so this is safe.

Fail-closed: the output buffer is re-parsed from scratch and every structural
invariant is asserted before anything is written. If any assert trips, nothing
ships. Map is stored UNCOMPRESSED (engine reads raw maps fine).
"""
import os, sys, struct, hashlib, re, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, HERE)
from bigfile import BigEntry, read_big, write_big, find_entry
from refpack import strip_ear, refpack_decompress
from _eff import ARCHIVES, _CACHE

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW = os.path.expanduser("~/GeneralsX/mods/ShockWave")
MAP_PATH = "Maps\\ShellMapSHW\\ShellMapSHW.map"
MAP_OWNER = "!Shw_maps.big"
OUT_NAME = "zzz-ZZZZZZZZZZZZZZ0ShellKwai.big"

# ---- (A) recast swap sets (identical to build_shellmap_recast.py) ----
SWAP_BASES = {
 "ChinaBunker","ChinaGattlingCannon","ChinaInfantryFlameThrower",
 "ChinaInfantryRedguard","ChinaInfantryTankHunter","ChinaInternetCenter",
 "ChinaNuclearMissileLauncher","ChinaPowerPlant","ChinaPropagandaCenter",
 "ChinaSupplyCenter","ChinaTankBattleMaster","ChinaTankDragon","ChinaTankECM",
 "ChinaTankGattling","ChinaVehicleDozer","ChinaVehicleHelix",
 "ChinaVehicleInfernoCannon","ChinaVehicleListeningOutpost",
 "ChinaVehicleNukeLauncher","ChinaVehicleTroopCrawler","ChinaWarFactory",
}
NO_KWAI = {"ChinaHellStorm","ChinaRepairStation","ChinaVehicleSeismicTank"}
PREFIXES = ("Spec_", "Nuke_")

# ---- (B) showcase: a SMALL absurdly-OP elite core + a large enemy swarm. ----
# Design: 6 near-invincible HEROIC Kwai panzers in a tight ~110x120 knot at the
# armor centroid; ~17 basic GLA attackers ringed just outside, charging in and
# dying. Contrast (few unkillable heroes vs many dying attackers) is the point.
CX, CY = 1181.0, 575.0

# CORE -- owner teamPlyrGLAYellow (mutually hostile to PlyrGLA, the swarm). Every
# unit spawns at max rank with NO script by using the drop-ladder Heroic variants.
#   (template, x, y).  Cluster X[1128..1238] Y[520..640] = 110x120 tight knot.
CORE_TEAM = "teamPlyrGLAYellow"
CORE = [
    ("Tank_DropEmperorT3",      1150, 560),  # HEROIC + crewed (drop variant)
    ("Tank_DropEmperorT3",      1215, 560),  # HEROIC + crewed (drop variant)
    ("Tank_ChinaTankEmperor",   1183, 520),  # VETERAN + innate always-on PDL + Shtora
    ("Tank_DropBattleMasterT3", 1128, 612),  # HEROIC (drop variant)
    ("Tank_DropBattleMasterT3", 1238, 612),  # HEROIC (drop variant)
    ("Tank_DropGattlingT3",     1183, 640),  # ELITE (highest gattling drop; no Heroic drop exists)
]

# SWARM -- owner teamPlyrGLA. PlyrGLA.enemies = "PlyrAmericaAirForceGeneral
# PlyrGLAYellow" => hostile to our core; set aggressiveness (key139) = 2
# (AGGRESSIVE) so they charge in. These are meant to die. (template, angle_deg, radius)
SWARM_TEAM = "teamPlyrGLA"
AGGRESSIVE = 2  # AttitudeType: -2 SLEEP, -1 PASSIVE, 0 NORMAL, 1 ALERT, 2 AGGRESSIVE
SWARM = [
    ("GLAInfantryRebel",           20, 150), ("GLAInfantryRebel",          70, 150),
    ("GLAInfantryRebel",          130, 150), ("GLAInfantryRebel",         200, 150),
    ("GLAInfantryRebel",          250, 150), ("GLAInfantryRebel",         320, 150),
    ("GLAVehicleRocketBuggy",      45, 200), ("GLAVehicleRocketBuggy",    135, 200),
    ("GLAVehicleRocketBuggy",     225, 200), ("GLAVehicleRocketBuggy",    315, 200),
    ("GLAVehicleTechnical",         0, 178), ("GLAVehicleTechnical",      120, 178),
    ("GLAVehicleTechnical",       240, 178),
    ("GLAVehicleQuadCannon",       90, 188), ("GLAVehicleQuadCannon",     270, 188),
    ("Salv_GLAVehicleMI8Gunship",  60, 215), ("Salv_GLAVehicleMI8Gunship",300, 215),
]
INFANTRY_TEMPLATES = {"GLAInfantryRebel"}  # (only matters for donor pick; dict layout is generic)

# ---------------------------------------------------------------- roster
def roster_objects():
    objs, seen = set(), set()
    for a in ARCHIVES:
        for e in _CACHE[a]:
            lp = e.path.lower()
            if not lp.endswith(".ini") or lp in seen: continue
            seen.add(lp)
            for m in re.finditer(r"(?mi)^\s*Object\s+(\S+)", e.data.decode("latin-1", "replace")):
                objs.add(m.group(1))
    return objs

# ---------------------------------------------------------------- dict codec
def read_dict(b, p):
    (npairs,) = struct.unpack_from("<H", b, p); p += 2
    pairs = []
    for _ in range(npairs):
        (packed,) = struct.unpack_from("<I", b, p); p += 4
        keyid = packed >> 8; typ = packed & 0xFF
        if typ == 0:   v = b[p]; p += 1
        elif typ == 1: v = struct.unpack_from("<i", b, p)[0]; p += 4
        elif typ == 2: v = struct.unpack_from("<f", b, p)[0]; p += 4
        elif typ == 3:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+sl]; p += sl
        elif typ == 4:
            (sl,) = struct.unpack_from("<H", b, p); p += 2; v = b[p:p+2*sl]; p += 2*sl
        else: raise ValueError("bad dict type %d" % typ)
        pairs.append((keyid, typ, v))
    return pairs, p

def enc_dict(pairs):
    out = bytearray(struct.pack("<H", len(pairs)))
    for keyid, typ, v in pairs:
        out += struct.pack("<I", (keyid << 8) | typ)
        if typ == 0:   out += struct.pack("<B", 1 if v else 0)
        elif typ == 1: out += struct.pack("<i", v)
        elif typ == 2: out += struct.pack("<f", v)
        elif typ == 3:
            b = v if isinstance(v, (bytes, bytearray)) else v.encode("latin-1")
            out += struct.pack("<H", len(b)) + b
        elif typ == 4:
            out += struct.pack("<H", len(v)//2) + v
        else: raise ValueError("bad dict type %d" % typ)
    return bytes(out)

# ---------------------------------------------------------------- map parse
def parse_map(buf):
    assert buf[:4] == b"CkMp", "not a CkMp map"
    pos = 4
    (count,) = struct.unpack_from("<i", buf, pos); pos += 4
    id2name = {}
    for _ in range(count):
        ln = buf[pos]; pos += 1
        id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
        pos += ln + 4
    data_start = pos
    name2id = {v: k for k, v in id2name.items()}
    # top-level chunks
    top = []
    p = data_start
    while p + 10 <= len(buf):
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        nm = id2name.get(cid)
        if nm is None or dsize < 0 or p+10+dsize > len(buf):
            raise ValueError("bad top-level chunk @%d nm=%r dsize=%r" % (p, nm, dsize))
        top.append(dict(nm=nm, ver=ver, dsize=dsize, hp=p, ds=p+10, de=p+10+dsize))
        p = p+10+dsize
    if p != len(buf):
        raise ValueError("top-level walk ended @%d != buflen %d" % (p, len(buf)))
    return id2name, name2id, data_start, top

def parse_objects(buf, ol):
    """Walk Object chunks inside an ObjectsList top-level chunk dict `ol`.
       Returns list of dicts with hp/ds/de/tn/template offset/parsed dict."""
    objs = []
    p = ol["ds"]
    # need id2name for the Object type id: re-derive locally
    while p + 10 <= ol["de"]:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        ds = p+10; de = ds+dsize
        if de > ol["de"] or dsize < 0:
            raise ValueError("object chunk overruns ObjectsList @%d" % p)
        x,y,z,ang = struct.unpack_from("<ffff", buf, ds)
        (flags,) = struct.unpack_from("<i", buf, ds+16)
        (slen,) = struct.unpack_from("<H", buf, ds+20)
        toff = ds+22
        tn = buf[toff:toff+slen].decode("latin-1")
        dstart = toff+slen
        pairs, dend = read_dict(buf, dstart)
        if dend != de:
            raise ValueError("dict end %d != chunk end %d (%s)" % (dend, de, tn))
        d = {k: v for (k, _, v) in pairs}
        objs.append(dict(hp=p, ds=ds, de=de, ver=ver, tn=tn, toff=toff, slen=slen,
                         pairs=pairs, dictmap=d))
        p = de
    if p != ol["de"]:
        raise ValueError("Object walk ended @%d != ObjectsList data end %d" % (p, ol["de"]))
    return objs

def s(v):  # decode AsciiString dict value bytes
    return v.decode("latin-1") if isinstance(v, (bytes, bytearray)) else v

# ---------------------------------------------------------------- build one object
def build_object(name2id, donor_pairs, template, x, y, ang, uid, team, force139=None):
    """Clone donor dict pair-layout, override 119/126/127/128 (+ blank 129 if
    present). If force139 is not None, overwrite key 139 (aggressiveness) -- or
    append it (as int) if the donor lacks it."""
    new_pairs = []
    saw139 = False
    for (keyid, typ, val) in donor_pairs:
        if   keyid == 119 and typ == 1: val = 100
        elif keyid == 126 and typ == 3: val = team.encode("latin-1")
        elif keyid == 127 and typ == 3: val = uid.encode("latin-1")
        elif keyid == 128 and typ == 3: val = b""
        elif keyid == 129 and typ == 3: val = b""   # blank objectName: no script targets it
        elif keyid == 139 and force139 is not None: val = force139; saw139 = True
        new_pairs.append((keyid, typ, val))
    if force139 is not None and not saw139:
        new_pairs.append((139, 1, force139))
    dict_bytes = enc_dict(new_pairs)
    tb = template.encode("latin-1")
    body = (struct.pack("<ffff", x, y, 0.0, ang) + struct.pack("<i", 0) +
            struct.pack("<H", len(tb)) + tb + dict_bytes)
    hdr = struct.pack("<IHi", name2id["Object"], 3, len(body))
    return hdr + body

# ---------------------------------------------------------------- main
def main():
    src = read_big(os.path.join(SPE, MAP_OWNER))
    ent = find_entry(src, MAP_PATH)
    stream, ear_size = strip_ear(ent.data)
    buf, rp_size = refpack_decompress(stream)
    assert buf[:4] == b"CkMp" and len(buf) == ear_size == rp_size, "decompress mismatch"
    print("decompressed shellmap: %d bytes, CkMp OK" % len(buf))

    id2name, name2id, data_start, top = parse_map(buf)
    top_seq = [t["nm"] for t in top]
    print("top-level:", top_seq)
    ol = [t for t in top if t["nm"] == "ObjectsList"][0]
    objs = parse_objects(buf, ol)
    n_orig = len(objs)
    print("ObjectsList hdr@%d data[%d..%d] size=%d ; %d Object chunks" %
          (ol["hp"], ol["ds"], ol["de"], ol["dsize"], n_orig))

    roster = roster_objects()

    # ---- (A) plan + apply recast swaps (equal length, in place) ----
    work = bytearray(buf)
    n_swap = 0
    for o in objs:
        tn = o["tn"]; pfx = tn[:5]
        if pfx in PREFIXES and "China" in tn and tn[5:] in SWAP_BASES:
            new = "Tank_" + tn[5:]
            assert len(new) == len(tn), "swap length mismatch %r->%r" % (tn, new)
            assert new in roster, "swap target missing: " + new
            assert bytes(work[o["toff"]:o["toff"]+len(tn)]) == tn.encode("latin-1")
            work[o["toff"]:o["toff"]+len(new)] = new.encode("latin-1")
            n_swap += 1
    print("(A) recast swaps applied in place: %d" % n_swap)

    # ---- pick donors (from the swapped buffer so we clone a valid live dict) ----
    objs_sw = parse_objects(work, ol)  # offsets identical (equal-length swaps)
    veh_donor = next(o for o in objs_sw if o["tn"] == "Tank_ChinaTankBattleMaster")
    inf_donor = next(o for o in objs_sw if o["tn"] == "Tank_ChinaInfantryRedguard" and
                     any(k == 129 for (k, _, _) in o["pairs"]))
    # swarm donor: a real combat unit whose Dict already carries key 139 (aggressiveness)
    agg_donor = next(o for o in objs_sw if any(k == 139 for (k, _, _) in o["pairs"]))
    print("donor vehicle dict keys:", [k for (k, _, _) in veh_donor["pairs"]])
    print("donor infantry dict keys:", [k for (k, _, _) in inf_donor["pairs"]])
    print("donor aggressive dict keys:", [k for (k, _, _) in agg_donor["pairs"]],
          "(", agg_donor["tn"], ")")

    all_new = [t[0] for t in CORE] + [t[0] for t in SWARM]
    for tmpl in all_new:
        assert tmpl in roster, "showcase template missing from roster: " + tmpl

    new_chunks = bytearray()
    added_core, added_swarm = [], []
    idx = 0

    # ---- (B1) build the OP core (owner CORE_TEAM), facing outward at the swarm ----
    for (tmpl, x, y) in CORE:
        dx, dy = x - CX, y - CY
        ang = 2.44 if (dx*dx+dy*dy) < 30*30 else math.atan2(dy, dx)   # face outward toward the ring
        uid = "SHOWCASE_CORE_%02d_%s" % (idx, tmpl); idx += 1
        chunk = build_object(name2id, veh_donor["pairs"], tmpl, float(x), float(y),
                             ang, uid, CORE_TEAM)          # no forced aggressiveness: hold the knot
        new_chunks += chunk
        added_core.append((tmpl, x, y, round(ang, 3), uid))

    # ---- (B2) build the enemy swarm (owner SWARM_TEAM, AGGRESSIVE), facing inward ----
    for (tmpl, adeg, radius) in SWARM:
        a = math.radians(adeg)
        x = CX + radius * math.cos(a); y = CY + radius * math.sin(a)
        ang = math.atan2(CY - y, CX - x)                   # face inward toward the core
        uid = "SHOWCASE_SWARM_%02d_%s" % (idx, tmpl); idx += 1
        donor = inf_donor if tmpl in INFANTRY_TEMPLATES else agg_donor
        chunk = build_object(name2id, donor["pairs"], tmpl, float(x), float(y),
                             ang, uid, SWARM_TEAM, force139=AGGRESSIVE)
        new_chunks += chunk
        added_swarm.append((tmpl, round(x), round(y), round(ang, 3), uid))
    N_NEW = len(CORE) + len(SWARM)
    print("(B) built %d core + %d swarm = %d object chunks, %d bytes" %
          (len(CORE), len(SWARM), N_NEW, len(new_chunks)))

    # ---- splice: insert at end of ObjectsList data; grow ObjectsList dataSize ----
    out = bytearray(work)
    out[ol["de"]:ol["de"]] = new_chunks
    new_ol_dsize = ol["dsize"] + len(new_chunks)
    struct.pack_into("<i", out, ol["hp"]+6, new_ol_dsize)  # dsize field is at hdr+6
    out = bytes(out)
    print("spliced; ObjectsList dataSize %d -> %d ; buffer %d -> %d" %
          (ol["dsize"], new_ol_dsize, len(buf), len(out)))

    # ================= HARD VERIFY (fail-closed) =================
    id2b, name2b, ds2, top2 = parse_map(out)             # full top-level walk, ends exactly at len(out)
    seq2 = [t["nm"] for t in top2]
    assert seq2 == top_seq, "top-level sequence changed: %s" % seq2
    for a, b in zip(top, top2):
        if a["nm"] == "ObjectsList":
            assert b["dsize"] == new_ol_dsize, "ObjectsList dsize wrong"
        else:
            assert a["dsize"] == b["dsize"], "sibling %s dsize changed" % a["nm"]
    print("VERIFY top-level: sequence & every dataSize consistent; walk ends exactly at EOF")

    ol2 = [t for t in top2 if t["nm"] == "ObjectsList"][0]
    objs2 = parse_objects(out, ol2)                       # every Object + dict parses cleanly
    assert len(objs2) == n_orig + N_NEW, \
        "object count %d != %d+%d" % (len(objs2), n_orig, N_NEW)
    print("VERIFY ObjectsList: %d -> %d Object chunks (all dicts parse cleanly)" %
          (n_orig, len(objs2)))

    # every NEW template resolves; every Tank_China*/Tank_Drop* placement resolves
    for o in objs2:
        if o["tn"].startswith("Tank_China") or o["tn"].startswith("Tank_Drop"):
            assert o["tn"] in roster, "unresolved template: " + o["tn"]
    for tmpl in all_new:
        assert tmpl in roster, "new template unresolved: " + tmpl
    # confirm the swarm units really carry aggressiveness=2
    n_agg = sum(1 for o in objs2 if s(o["dictmap"].get(127, b"")).startswith("SHOWCASE_SWARM_")
                and o["dictmap"].get(139) == AGGRESSIVE)
    assert n_agg == len(SWARM), "not all swarm units aggressive: %d/%d" % (n_agg, len(SWARM))
    print("VERIFY roster: all %d new templates resolve (core Tank_Drop*/Tank_China* + swarm GLA*); "
          "%d/%d swarm units carry aggressiveness=%d" % (len(set(all_new)), n_agg, len(SWARM), AGGRESSIVE))

    # I must introduce NO NEW uniqueID collision. (The stock map already reuses
    # some "Waypoint N" uids -- harmless & pre-existing; I only guarantee my adds
    # collide with nothing and that the duplicate-set is otherwise unchanged.)
    from collections import Counter
    uids_before = [s(o["dictmap"].get(127, b"")) for o in objs]
    uids_after  = [s(o["dictmap"].get(127, b"")) for o in objs2]
    orig_uidset = set(u for u in uids_before if u)
    my_uids = [u for u in uids_after if u.startswith("SHOWCASE_")]
    assert len(my_uids) == N_NEW and len(set(my_uids)) == N_NEW, "SHOWCASE uid not unique"
    assert not (set(my_uids) & orig_uidset), "SHOWCASE uid collides with an existing uid!"
    dup_before = {k for k, v in Counter(u for u in uids_before if u).items() if v > 1}
    dup_after  = {k for k, v in Counter(u for u in uids_after  if u).items() if v > 1}
    assert dup_after == dup_before, "introduced a NEW duplicate uniqueID: %s" % (dup_after - dup_before)
    names_before = sorted(x for x in (s(o["dictmap"].get(129, b"")) for o in objs) if x)
    names_after  = sorted(x for x in (s(o["dictmap"].get(129, b"")) for o in objs2) if x)
    assert names_before == names_after, "objectName set changed (new dup name introduced?)"
    print("VERIFY ids: %d SHOWCASE uids unique & disjoint from %d originals; "
          "duplicate-uid set unchanged (%d pre-existing Waypoint dups); objectName set unchanged (%d named)" %
          (len(my_uids), len(orig_uidset), len(dup_before), len(names_after)))

    # trailing top-level chunks byte-identical to originals (just shifted)
    orig_tail = bytes(buf[ol["de"]:])            # PolygonTriggers+GlobalLighting+WaypointsList (unswapped region)
    new_tail  = out[ol["de"] + len(new_chunks):]
    assert new_tail == orig_tail, "trailing chunks NOT byte-identical!"
    print("VERIFY tail: PolygonTriggers+GlobalLighting+WaypointsList byte-identical (%d bytes, shifted +%d)" %
          (len(orig_tail), len(new_chunks)))

    # the recast region before ObjectsList is byte-identical to the swapped work
    # buffer, EXCEPT the 4-byte ObjectsList dataSize field (hdr+6..hdr+10) which we
    # legitimately grew. Everything before it, and all original object data, match.
    assert out[:ol["hp"]+6] == bytes(work[:ol["hp"]+6]), "region before ObjectsList dsize altered"
    assert out[ol["hp"]+10:ol["de"]] == bytes(work[ol["hp"]+10:ol["de"]]), "original object data altered"
    print("VERIFY head: all bytes up to ObjectsList data-end identical to swapped buffer "
          "(only the 4-byte ObjectsList dataSize field grew, %d->%d)" % (ol["dsize"], new_ol_dsize))

    # ================= package (UNCOMPRESSED) + install =================
    out_entry = BigEntry(MAP_PATH, out)
    big_bytes = write_big([out_entry])
    rt = read_big(big_bytes)
    assert len(rt) == 1 and find_entry(rt, MAP_PATH).data == out, "BIG round-trip failed"
    print("BIG round-trip byte-identical (1 entry, uncompressed map)")

    # sort-position guard
    for d in (SPE, SHW):
        for f in os.listdir(d):
            if not f.lower().endswith(".big"): continue
            if f.lower() > OUT_NAME.lower():
                for e in read_big(os.path.join(d, f)):
                    assert e.path.lower() != MAP_PATH.lower(), \
                        "archive %s sorts above us and owns the map!" % f
    print("sort-position OK: no higher archive claims the shellmap path")

    with open(os.path.join(HERE, OUT_NAME), "wb") as fh:
        fh.write(big_bytes)
    md5s = {}
    for d in (SPE, SHW):
        p = os.path.join(d, OUT_NAME)
        with open(p, "wb") as fh:
            fh.write(big_bytes)
        md5s[d] = hashlib.md5(open(p, "rb").read()).hexdigest()
        inst = read_big(p)
        assert find_entry(inst, MAP_PATH).data == out
    assert len(set(md5s.values())) == 1, "installed archives differ!"
    print("installed to both mod dirs; md5 match: %s" % list(md5s.values())[0])
    print("OUT: %s (%d bytes)" % (OUT_NAME, len(big_bytes)))

    print("\n=== OP CORE (owner=%s) -- small elite Heroic knot ===" % CORE_TEAM)
    for (tmpl, x, y, ang, uid) in added_core:
        print("   %-26s (%4d,%4d) ang=%6.3f  %s" % (tmpl, x, y, ang, uid))
    print("=== ENEMY SWARM (owner=%s, aggressiveness=%d) -- ringed, charging inward ===" %
          (SWARM_TEAM, AGGRESSIVE))
    for (tmpl, x, y, ang, uid) in added_swarm:
        print("   %-26s (%4d,%4d) ang=%6.3f  %s" % (tmpl, x, y, ang, uid))

if __name__ == "__main__":
    main()
