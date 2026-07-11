#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZZ0ShellKwai.big -- recast the ShockWave main-menu
shellmap (Maps\\ShellMapSHW\\ShellMapSHW.map) so its CHINA contingent is Kwai's
(China Tank General) 'Tank_' roster instead of the stock 'Spec_'/'Nuke_' units.

MECHANISM (pure-data, non-corrupting):
  * The map is EA RefPack-compressed (EAR\\0 wrapper). We decompress it to the
    1,282,022-byte 'CkMp' DataChunk payload (refpack decoder verified
    byte-identical to a reference decode).
  * Placed objects store their spawn template as a length-prefixed AsciiString
    inside each 'Object' chunk (offset +20 past loc/angle/flags). Every China
    subfaction prefix is exactly 5 bytes (Spec_ / Nuke_ / Tank_), so swapping a
    unit to its Kwai equivalent is an EQUAL-LENGTH in-place byte overwrite --
    no length prefix or chunk dataSize changes, zero risk of reflow/corruption.
  * We only swap base names that have a verified 'Tank_<base>' Object in the
    effective roster (21 of 24 placed China types). The 3 Kwai-less types
    (HellStorm, RepairStation, SeismicTank) are left as-is (still valid).
  * The engine reads UNCOMPRESSED maps fine (DataChunk.cpp:64-82 raw path), so
    we store the edited CkMp buffer uncompressed -- no refpack ENCODER needed.
  * The override archive sorts after the map's sole owner (!Shw_maps.big) and,
    being 'zzz-...', below zzz_ControlBarPro*/zzzz_FXEnhance; 14 Z's puts it
    above the current top INI layer (13-Z TeslaFinish).

SCOPE / CEILING (documented, honest): this makes the menu scene's China army
Kwai's tank-general roster. It does NOT add Emperors, tesla units or crewed
paradrops or any PDL choreography -- those objects are NOT on the stock map, so
showcasing them requires ADDING Object chunks + scripting = World Builder, out
of pure-data scope. See SHELLMAP_RECAST.md.
"""
import os, sys, struct, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, HERE)
from bigfile import BigEntry, read_big, write_big, find_entry
from refpack import strip_ear, refpack_decompress
from _eff import ARCHIVES, _CACHE   # effective stack (reverse-sorted, first hit wins)

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW = os.path.expanduser("~/GeneralsX/mods/ShockWave")
MAP_PATH = "Maps\\ShellMapSHW\\ShellMapSHW.map"
MAP_OWNER = "!Shw_maps.big"
OUT_NAME = "zzz-ZZZZZZZZZZZZZZ0ShellKwai.big"

# China base names with a verified Tank_ (Kwai) equivalent -- swap these.
SWAP_BASES = {
 "ChinaBunker","ChinaGattlingCannon","ChinaInfantryFlameThrower",
 "ChinaInfantryRedguard","ChinaInfantryTankHunter","ChinaInternetCenter",
 "ChinaNuclearMissileLauncher","ChinaPowerPlant","ChinaPropagandaCenter",
 "ChinaSupplyCenter","ChinaTankBattleMaster","ChinaTankDragon","ChinaTankECM",
 "ChinaTankGattling","ChinaVehicleDozer","ChinaVehicleHelix",
 "ChinaVehicleInfernoCannon","ChinaVehicleListeningOutpost",
 "ChinaVehicleNukeLauncher","ChinaVehicleTroopCrawler","ChinaWarFactory",
}
# Kwai-less (documented, left untouched)
NO_KWAI = {"ChinaHellStorm","ChinaRepairStation","ChinaVehicleSeismicTank"}
PREFIXES = ("Spec_", "Nuke_")

def roster_objects():
    objs, seen = set(), set()
    for a in ARCHIVES:
        for e in _CACHE[a]:
            lp = e.path.lower()
            if not lp.endswith(".ini") or lp in seen: continue
            seen.add(lp)
            for m in re.finditer(r"(?mi)^Object\s+(\S+)", e.data.decode("latin-1")):
                objs.add(m.group(1))
    return objs

def parse_objects(buf):
    """Return (id2name, list of (name_off, slen, name)). Raises on malformed."""
    assert buf[:4] == b"CkMp", "not a CkMp map"
    pos = 4
    (count,) = struct.unpack_from("<i", buf, pos); pos += 4
    id2name = {}
    for _ in range(count):
        ln = buf[pos]; pos += 1
        id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
        pos += ln + 4
    first = pos
    objects = []
    def walk(start, end):
        p = start
        while p + 10 <= end:
            cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
            name = id2name.get(cid)
            if name is None or dsize < 0 or p + 10 + dsize > end:
                return
            ds = p + 10; de = ds + dsize
            if name == "Object":
                no = ds + 20
                (slen,) = struct.unpack_from("<H", buf, no)
                tn = buf[no+2:no+2+slen].decode("latin-1")
                objects.append((no+2, slen, tn))
            if name == "ObjectsList":
                walk(ds, de)
            p = de
    walk(first, len(buf))
    return id2name, objects

def main():
    # 1. decompress the shellmap from its sole owner
    src = read_big(os.path.join(SPE, MAP_OWNER))
    ent = find_entry(src, MAP_PATH)
    stream, ear_size = strip_ear(ent.data)
    buf, rp_size = refpack_decompress(stream)
    assert buf[:4] == b"CkMp" and len(buf) == ear_size == rp_size, "decompress mismatch"
    print("decompressed shellmap: %d bytes, CkMp OK" % len(buf))

    # 2. parse + plan swaps
    _, objects = parse_objects(buf)
    roster = roster_objects()
    edits = []           # (name_off, old, new)
    skipped_no_kwai = {}
    unknown = {}
    for (off, slen, name) in objects:
        pfx = name[:5]
        if pfx not in PREFIXES or "China" not in name:
            continue
        base = name[5:]
        if base in SWAP_BASES:
            new = "Tank_" + base
            assert len(new) == len(name), "length mismatch %r->%r" % (name, new)
            assert new in roster, "target missing from roster: " + new
            edits.append((off, name, new))
        elif base in NO_KWAI:
            skipped_no_kwai[base] = skipped_no_kwai.get(base, 0) + 1
        # else: prefix-China but base not in either set -> leave (shouldn't happen)
    print("planned swaps: %d object placements" % len(edits))
    print("left as-is (no Kwai equivalent): %s" % dict(skipped_no_kwai))

    # 3. apply in place (all equal length)
    out = bytearray(buf)
    for (off, old, new) in edits:
        assert bytes(out[off:off+len(old)]) == old.encode("latin-1")
        out[off:off+len(new)] = new.encode("latin-1")
    out = bytes(out)
    assert len(out) == len(buf), "length changed!"

    # 4. re-parse the edited buffer: structure identical, swaps applied, closure
    _, objs2 = parse_objects(out)
    assert len(objs2) == len(objects), "object count changed"
    for (o1, l1, n1), (o2, l2, n2) in zip(objects, objs2):
        assert o1 == o2 and l1 == l2, "offset/len drift"
    remaining = [n for (_, _, n) in objs2
                 if n[:5] in PREFIXES and "China" in n and n[5:] in SWAP_BASES]
    assert not remaining, "un-swapped leftovers: %s" % set(remaining)
    for (_, _, n) in objs2:
        if n.startswith("Tank_China"):
            assert n in roster, "post-swap unresolved: " + n
    print("edited buffer re-parses; %d objects; every Tank_China* placement resolves"
          % len(objs2))

    # 5. pack (map stored UNCOMPRESSED) + round-trip
    out_entry = BigEntry(MAP_PATH, out)
    big_bytes = write_big([out_entry])
    rt = read_big(big_bytes)
    assert len(rt) == 1 and find_entry(rt, MAP_PATH).data == out, "BIG round-trip failed"
    print("BIG round-trip byte-identical (1 entry, uncompressed map)")

    # 6. sort-position guard: no archive sorting >= ours (except ours) may own the map path
    for d in (SPE, SHW):
        for f in os.listdir(d):
            if not f.lower().endswith(".big"):
                continue
            if f.lower() >= OUT_NAME.lower() and f.lower() != OUT_NAME.lower():
                for e in read_big(os.path.join(d, f)):
                    assert e.path.lower() != MAP_PATH.lower(), \
                        "archive %s sorts above us and owns the map!" % f
    print("sort-position OK: no higher archive claims the shellmap path")

    # 7. keep a local copy in the layer dir, then install to both dirs + md5 match
    with open(os.path.join(HERE, OUT_NAME), "wb") as fh:
        fh.write(big_bytes)
    md5s = {}
    for d in (SPE, SHW):
        p = os.path.join(d, OUT_NAME)
        with open(p, "wb") as fh:
            fh.write(big_bytes)
        md5s[d] = hashlib.md5(open(p, "rb").read()).hexdigest()
        # post-install: re-read the installed archive, confirm the map entry
        inst = read_big(p)
        assert find_entry(inst, MAP_PATH).data == out
    assert len(set(md5s.values())) == 1, "installed archives differ!"
    print("installed to both mod dirs; md5 match: %s" % list(md5s.values())[0])
    print("OUT: %s (%d bytes)" % (OUT_NAME, len(big_bytes)))

if __name__ == "__main__":
    main()
