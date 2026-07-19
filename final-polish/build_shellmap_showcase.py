#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZZ0ShellKwai.big -- the "3 god-Emperors" shellmap.

The ShockWave main-menu shellmap (Maps\\ShellMapSHW\\ShellMapSHW.map) is
rebuilt so the ONLY Chinese presence is 3 maxed-out, fully-loaded elite Emperor
Overlords standing in a knot at the armor centroid, shrugging off a swarm of GLA
attackers. Pure-data binary surgery (World Builder unavailable); fail-closed.

OPERATIONS (all on the decompressed CkMp DataChunk buffer):
 (1) REMOVE every China-faction Object chunk (all military units + buildings,
     146 of them across 36 templates -- match /China|Chinee/). Deletion is safe:
     objects reference nothing by byte offset; scripts reference units by NAME and
     ZH tolerates a dangling NAMED reference (resolves NULL -> condition/action is
     skipped, never crashes). Scenery / props / waypoints / civilians / all GLA &
     USA enemy units are KEPT.
 (2) ADD a 17-unit GLA swarm (owner teamPlyrGLA, aggressiveness=2) ringed around
     the centroid, charging inward -- cannon fodder for the Emperors.
 (3) ADD exactly 3 Tank_ShellEmperorElite (owner teamPlyrGLAYellow -- mutually
     hostile to PlyrGLA) clustered tight at the centroid, facing the swarm.

Tank_ShellEmperorElite is defined in a NEW INI shipped inside this same .big
(Data\\INI\\Object\\China\\Tank\\Vehicles\\ShellEmperorElite.ini). It is a verbatim
clone of the CURRENT effective Tank_DropEmperorFullUpgrade (full loadout: granted
gattling, 3320-HP baked energy shield, ABM + reactive PDL + fleet aura + innate
PDL + Shtora, 8-man Waffen crew), with exactly TWO changes:
  * VeterancyGainCreate StartingLevel HEROIC -> HEROIC6. The patched engine
    binary (~/GeneralsX/GeneralsZH/GeneralsXZH) extends TheVeterancyNames with
    HEROIC2..HEROIC6, so LEVEL_HEROIC6 == LEVEL_LAST is the top spawnable rank
    (verified against the installed binary's string table; the stock binary
    stops at HEROIC, hence the binary guard below).
  * BOTH ArmorSet blocks (Conditions=None AND Conditions=PLAYER_UPGRADE) swap
    Armor TankArmor -> InvulnerableAllArmor (0% from everything except
    UNRESISTABLE/STATUS; defined in the effective Data\\INI\\Armor.ini). The
    menu scene can never lose the Emperors. DamageFX entries stay untouched.

KILLABILITY FIX: build_object() used to clone the donor Dict verbatim, and the
aggressiveness donor (an original scripted scene actor) carries
objectIndestructible=1 -- so every SHOWCASE swarm unit shipped invulnerable.
build_object now forces objectIndestructible (key 121) to 0 on everything it
creates, and the verifier asserts no SWARM_TEAM-owned object is indestructible.
(The map's scripts never set invulnerability: the map symbol table contains no
such ScriptAction name. Neutral GLATrap props / USA scene actors / civilian
scenery keep their original indestructible flags by design.)

The map is stored UNCOMPRESSED (engine reads raw maps fine). The whole output
buffer is re-parsed from scratch and every structural invariant asserted before
anything ships.

Usage:  build_shellmap_showcase.py          build + verify + install to both mod dirs
        build_shellmap_showcase.py --stage  build + verify + write ONLY the layer-dir
                                            .big (no install; for staging while the
                                            game is running)
"""
import os, sys, struct, hashlib, re, math

STAGE = "--stage" in sys.argv
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

# --- new elite-Emperor object shipped inside this layer ---
DONOR_INI = "Data\\INI\\Object\\China\\Tank\\Vehicles\\EmperorFullDrop.ini"
DONOR_OBJ = "Tank_DropEmperorFullUpgrade"
NEW_OBJ   = "Tank_ShellEmperorElite"
NEW_INI_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\ShellEmperorElite.ini"
MAX_VET = "HEROIC6"   # LEVEL_HEROIC6 == LEVEL_LAST in the PATCHED engine binary
                      # (TheVeterancyNames extended HEROIC2..HEROIC6; guarded below)
INVULN_ARMOR = "InvulnerableAllArmor"   # 0% all damage except UNRESISTABLE/STATUS
ENGINE_BIN = os.path.expanduser("~/GeneralsX/GeneralsZH/GeneralsXZH")

# --- removal filter: any China-faction template (military units + buildings) ---
CHINA_RE = re.compile(r"China|Chinee")

# --- the 3 god-Emperors (owner CORE_TEAM), tight knot at the armor centroid ---
CX, CY = 1181.0, 575.0
CORE_TEAM = "teamPlyrGLAYellow"          # PlyrGLAYellow.enemies = PlyrGLA -> swarm attacks these
EMPERORS = [(1181, 528), (1128, 612), (1236, 612)]

# --- GLA swarm (owner SWARM_TEAM, AGGRESSIVE), ringed & charging inward ---
SWARM_TEAM = "teamPlyrGLA"               # PlyrGLA.enemies includes PlyrGLAYellow -> hostile to Emperors
AGGRESSIVE = 2   # AttitudeType: -2 SLEEP, -1 PASSIVE, 0 NORMAL, 1 ALERT, 2 AGGRESSIVE
ALERT = 1        # Emperors: acquire & fire on the charging swarm while holding position (no wander)
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

# ---------------------------------------------------------------- roster / INI
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

def effective_ini_text(path):
    want = path.lower().replace("/", "\\")
    for a in ARCHIVES:
        for e in _CACHE[a]:
            if e.path.lower().replace("/", "\\") == want:
                return e.data.decode("latin-1", "replace"), a
    return None, None

def build_new_ini():
    """Extract donor Object block verbatim, rename, bump StartingLevel to MAX_VET."""
    txt, owner = effective_ini_text(DONOR_INI)
    assert txt is not None, "donor INI not found: " + DONOR_INI
    m = re.search(r"(?mi)^\s*Object\s+" + re.escape(DONOR_OBJ) + r"\s*$", txt)
    assert m, "donor object not found: " + DONOR_OBJ
    mend = re.search(r"(?mi)^End\s*$", txt[m.end():])
    assert mend, "donor object End not found"
    block = txt[m.start(): m.end() + mend.end()]
    assert block.count(DONOR_OBJ) == 1, "donor name appears >1x; unsafe rename"
    block2, n1 = re.subn(r"(?m)^(\s*Object\s+)" + re.escape(DONOR_OBJ) + r"\s*$",
                         r"\g<1>" + NEW_OBJ, block)
    assert n1 == 1, "rename count %d" % n1
    block3, n2 = re.subn(r"(?mi)^(\s*StartingLevel\s*=\s*)HEROIC\s*$",
                         r"\g<1>" + MAX_VET, block2)
    assert n2 == 1, "StartingLevel replace count %d (expected 1)" % n2
    assert ("StartingLevel = " + MAX_VET) in block3
    assert not re.search(r"(?mi)^\s*StartingLevel\s*=\s*HEROIC\s*$", block3), "level-4 HEROIC still present"
    # MAX_VET must exist in the RUNNING engine or INI load throws INI_INVALID_DATA:
    # StartingLevel parses via INI::parseIndexList(TheVeterancyNames) (fail-closed guard).
    eng = open(ENGINE_BIN, "rb").read()
    assert (MAX_VET.encode() + b"\x00") in eng, \
        "installed engine binary lacks veterancy rank %s" % MAX_VET
    # invulnerability: swap the armor in BOTH ArmorSet blocks (Conditions=None and
    # Conditions=PLAYER_UPGRADE -- swapping only one would leave the upgrade-
    # condition set vulnerable). DamageFX lines untouched.
    block4, n3 = re.subn(r"(?m)^(\s*Armor\s*=\s*)TankArmor\s*$",
                         r"\g<1>" + INVULN_ARMOR, block3)
    assert n3 == 2, "ArmorSet Armor swap count %d (expected 2: Conditions=None + PLAYER_UPGRADE)" % n3
    assert not re.search(r"(?mi)^\s*Armor\s*=\s*TankArmor\s*$", block4), "TankArmor still present"
    assert len(re.findall(r"(?m)^\s*Armor\s*=\s*" + INVULN_ARMOR + r"\s*$", block4)) == 2
    assert len(re.findall(r"(?m)^\s*DamageFX\s*=", block4)) == \
           len(re.findall(r"(?m)^\s*DamageFX\s*=", block)), "DamageFX lines changed"
    # the armor template must resolve in the effective INI space
    armor_txt, armor_owner = effective_ini_text("Data\\INI\\Armor.ini")
    assert armor_txt and re.search(r"(?mi)^\s*Armor\s+" + INVULN_ARMOR + r"\b", armor_txt), \
        INVULN_ARMOR + " not defined in effective Armor.ini"
    header = ("; %s -- shipped by %s. Verbatim clone of %s (from %s, owner %s)\n"
              "; with StartingLevel raised HEROIC -> %s (top spawnable rank in the patched\n"
              "; engine) and both ArmorSet Armors swapped TankArmor -> %s\n"
              "; (menu-scene Emperors must never die; %s defined in %s).\n\n"
              % (NEW_OBJ, OUT_NAME, DONOR_OBJ, DONOR_INI, owner, MAX_VET,
                 INVULN_ARMOR, INVULN_ARMOR, armor_owner))
    return (header + block4 + "\n").encode("latin-1"), owner

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
    objs = []
    p = ol["ds"]
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
        objs.append(dict(hp=p, ds=ds, de=de, ver=ver, tn=tn, pairs=pairs, dictmap=d))
        p = de
    if p != ol["de"]:
        raise ValueError("Object walk ended @%d != ObjectsList data end %d" % (p, ol["de"]))
    return objs

def s(v):
    return v.decode("latin-1") if isinstance(v, (bytes, bytearray)) else v

# ---------------------------------------------------------------- build object
def build_object(name2id, donor_pairs, template, x, y, ang, uid, team, force139=None):
    new_pairs = []
    saw139 = False
    for (keyid, typ, val) in donor_pairs:
        if   keyid == 119 and typ == 1: val = 100
        elif keyid == 121 and typ == 0: val = 0   # objectIndestructible: NEVER inherit
                                                  # (the agg donor is an indestructible
                                                  # scene actor; all units must be killable)
        elif keyid == 126 and typ == 3: val = team.encode("latin-1")
        elif keyid == 127 and typ == 3: val = uid.encode("latin-1")
        elif keyid == 128 and typ == 3: val = b""
        elif keyid == 129 and typ == 3: val = b""   # blank objectName: nothing targets it
        elif keyid == 139 and force139 is not None: val = force139; saw139 = True
        new_pairs.append((keyid, typ, val))
    if force139 is not None and not saw139:
        new_pairs.append((139, 1, force139))
    dict_bytes = enc_dict(new_pairs)
    tb = template.encode("latin-1")
    body = (struct.pack("<ffff", x, y, 0.0, ang) + struct.pack("<i", 0) +
            struct.pack("<H", len(tb)) + tb + dict_bytes)
    return struct.pack("<IHi", name2id["Object"], 3, len(body)) + body

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

    # ---- new elite-Emperor INI (defines NEW_OBJ) ----
    ini_bytes, donor_owner = build_new_ini()
    print("new INI %s (%d bytes) cloned from %s @ %s ; StartingLevel=%s" %
          (NEW_INI_PATH, len(ini_bytes), DONOR_OBJ, donor_owner, MAX_VET))

    # ---- donors for cloned Dicts (read structure in-memory; source chunk may be removed) ----
    veh_donor = next(o for o in objs if o["tn"] == "Spec_ChinaTankBattleMaster")
    agg_donor = next(o for o in objs if any(k == 139 for (k, _, _) in o["pairs"]))
    print("veh donor keys:", [k for (k,_,_) in veh_donor["pairs"]],
          "| agg donor keys:", [k for (k,_,_) in agg_donor["pairs"]], "(", agg_donor["tn"], ")")

    # ---- (1) partition: remove China-faction, keep the rest ----
    kept, removed = [], []
    for o in objs:
        (removed if CHINA_RE.search(o["tn"]) else kept).append(o)
    n_removed = len(removed)
    named_removed = [(o["tn"], s(o["dictmap"].get(129, b"")))
                     for o in removed if s(o["dictmap"].get(129, b""))]
    from collections import Counter
    rem_tmpls = Counter(o["tn"] for o in removed)
    print("(1) removing %d China objects across %d templates (%d were NAMED, objectName!='' )" %
          (n_removed, len(rem_tmpls), len(named_removed)))
    kept_data = b"".join(bytes(buf[o["hp"]:o["de"]]) for o in kept)

    # ---- (2) GLA swarm chunks ----
    swarm_chunks = bytearray(); added_swarm = []; idx = 0
    for (tmpl, adeg, radius) in SWARM:
        assert tmpl in roster, "swarm template missing: " + tmpl
        a = math.radians(adeg)
        x = CX + radius*math.cos(a); y = CY + radius*math.sin(a)
        ang = math.atan2(CY - y, CX - x)          # face inward
        uid = "SHOWCASE_SWARM_%02d_%s" % (idx, tmpl); idx += 1
        swarm_chunks += build_object(name2id, agg_donor["pairs"], tmpl, float(x), float(y),
                                     ang, uid, SWARM_TEAM, force139=AGGRESSIVE)
        added_swarm.append((tmpl, round(x), round(y), round(ang, 3), uid))

    # ---- (3) three god-Emperors ----
    emp_chunks = bytearray(); added_emp = []
    for (x, y) in EMPERORS:
        dx, dy = x - CX, y - CY
        ang = math.atan2(dy, dx) if (dx*dx+dy*dy) >= 25*25 else -1.571   # face outward
        uid = "SHOWCASE_EMPEROR_%02d_%s" % (idx, NEW_OBJ); idx += 1
        emp_chunks += build_object(name2id, veh_donor["pairs"], NEW_OBJ, float(x), float(y),
                                   ang, uid, CORE_TEAM, force139=ALERT)   # ALERT: fire + hold
        added_emp.append((NEW_OBJ, x, y, round(ang, 3), uid))

    n_new = len(SWARM) + len(EMPERORS)
    new_ol_data = kept_data + bytes(swarm_chunks) + bytes(emp_chunks)
    print("(2)+(3) added %d swarm + %d Emperors = %d new chunks (%d bytes)" %
          (len(SWARM), len(EMPERORS), n_new, len(swarm_chunks)+len(emp_chunks)))

    # ---- splice: replace ObjectsList data; patch its dataSize; shift the tail ----
    out = bytearray()
    out += buf[:ol["ds"]]
    out += new_ol_data
    out += buf[ol["de"]:]
    new_ol_dsize = len(new_ol_data)
    struct.pack_into("<i", out, ol["hp"]+6, new_ol_dsize)
    out = bytes(out)
    print("spliced; ObjectsList dataSize %d -> %d ; buffer %d -> %d" %
          (ol["dsize"], new_ol_dsize, len(buf), len(out)))

    # ================= HARD VERIFY (fail-closed) =================
    _, _, _, top2 = parse_map(out)
    seq2 = [t["nm"] for t in top2]
    assert seq2 == top_seq, "top-level sequence changed: %s" % seq2
    for a, b in zip(top, top2):
        if a["nm"] == "ObjectsList":
            assert b["dsize"] == new_ol_dsize, "ObjectsList dsize wrong"
        else:
            assert a["dsize"] == b["dsize"], "sibling %s dsize changed" % a["nm"]
    print("VERIFY top-level: sequence & every dataSize consistent; walk ends exactly at EOF")

    ol2 = [t for t in top2 if t["nm"] == "ObjectsList"][0]
    objs2 = parse_objects(out, ol2)
    expect = n_orig - n_removed + n_new
    assert len(objs2) == expect, "object count %d != %d-%d+%d=%d" % (
        len(objs2), n_orig, n_removed, n_new, expect)
    print("VERIFY ObjectsList: %d -> %d Object chunks (removed %d, added %d; all Dicts parse cleanly)" %
          (n_orig, len(objs2), n_removed, n_new))

    # no China-faction template remains (except our NEW_OBJ, which is China-named by path only)
    leftover = sorted({o["tn"] for o in objs2 if CHINA_RE.search(o["tn"]) and o["tn"] != NEW_OBJ})
    assert not leftover, "China templates still present: %s" % leftover
    assert sum(1 for o in objs2 if o["tn"] == NEW_OBJ) == len(EMPERORS)
    print("VERIFY removal: zero China-faction units/buildings remain (only %d %s)" % (len(EMPERORS), NEW_OBJ))

    # templates resolve: swarm in effective roster; Emperor in the INI we ship
    ini_objs = set(re.findall(r"(?mi)^\s*Object\s+(\S+)", ini_bytes.decode("latin-1")))
    assert NEW_OBJ in ini_objs, "new INI does not define " + NEW_OBJ
    roster_plus = roster | ini_objs
    for o in objs2:
        if o["tn"].startswith("GLA") or o["tn"].startswith("Salv_") or o["tn"] == NEW_OBJ:
            assert o["tn"] in roster_plus, "unresolved new template: " + o["tn"]
    n_agg = sum(1 for o in objs2 if s(o["dictmap"].get(127, b"")).startswith("SHOWCASE_SWARM_")
                and o["dictmap"].get(139) == AGGRESSIVE)
    assert n_agg == len(SWARM), "swarm aggressiveness %d/%d" % (n_agg, len(SWARM))
    n_alert = sum(1 for o in objs2 if s(o["dictmap"].get(127, b"")).startswith("SHOWCASE_EMPEROR_")
                  and o["dictmap"].get(139) == ALERT)
    assert n_alert == len(EMPERORS), "emperor ALERT %d/%d" % (n_alert, len(EMPERORS))
    print("VERIFY roster: %d swarm GLA templates resolve; %s resolves in shipped INI; "
          "%d/%d swarm objectAggressiveness=%d (AGGRESSIVE); %d/%d Emperor objectAggressiveness=%d (ALERT)" %
          (len({t[0] for t in SWARM}), NEW_OBJ, n_agg, len(SWARM), AGGRESSIVE,
           n_alert, len(EMPERORS), ALERT))

    # uniqueIDs: my adds unique & disjoint from survivors; introduce no new duplicate
    uids_kept = [s(o["dictmap"].get(127, b"")) for o in objs2
                 if not s(o["dictmap"].get(127, b"")).startswith("SHOWCASE_")]
    my_uids = [s(o["dictmap"].get(127, b"")) for o in objs2
               if s(o["dictmap"].get(127, b"")).startswith("SHOWCASE_")]
    assert len(my_uids) == n_new and len(set(my_uids)) == n_new, "SHOWCASE uid not unique"
    assert not (set(my_uids) & set(u for u in uids_kept if u)), "SHOWCASE uid collides!"
    dup_now = {k for k, v in Counter(u for u in uids_kept if u).items() if v > 1}
    assert not any(u.startswith("SHOWCASE_") for u in dup_now)
    assert all(not s(o["dictmap"].get(129, b"")) for o in objs2
               if s(o["dictmap"].get(127, b"")).startswith("SHOWCASE_")), "a SHOWCASE unit has a non-empty objectName"
    print("VERIFY ids: %d SHOWCASE uids unique & disjoint from survivors; every new unit has blank objectName" % n_new)

    # (B) killability: nothing we add, and nothing the attacking side owns, may be
    # indestructible (key 121 = objectIndestructible; the agg donor carries =1)
    assert id2name.get(121) == "objectIndestructible", "key 121 is %r" % id2name.get(121)
    n_sc = n_swarmside = 0
    for o in objs2:
        uid = s(o["dictmap"].get(127, b"")); team = s(o["dictmap"].get(126, b""))
        if uid.startswith("SHOWCASE_"):
            n_sc += 1
            assert not o["dictmap"].get(121), "SHOWCASE unit indestructible: %s" % uid
        if team == SWARM_TEAM:
            n_swarmside += 1
            assert not o["dictmap"].get(121), \
                "%s-owned object indestructible: %s %s" % (SWARM_TEAM, o["tn"], uid)
    assert n_sc == n_new
    print("VERIFY killable: all %d SHOWCASE objects and all %d %s-owned objects have "
          "objectIndestructible=0 (GLA attackers are killable)" % (n_sc, n_swarmside, SWARM_TEAM))

    # (A) invulnerable-Emperor INI: re-assert on the exact bytes being shipped
    ini_txt = ini_bytes.decode("latin-1")
    assert len(re.findall(r"(?m)^\s*Armor\s*=\s*" + INVULN_ARMOR + r"\s*$", ini_txt)) == 2
    assert not re.search(r"(?mi)^\s*Armor\s*=\s*TankArmor\s*$", ini_txt)
    assert ("StartingLevel = " + MAX_VET) in ini_txt
    print("VERIFY invulnerable: shipped INI has 2/2 ArmorSet Armor=%s, zero TankArmor, "
          "StartingLevel=%s (rank present in engine binary)" % (INVULN_ARMOR, MAX_VET))

    # trailing chunks byte-identical (PolygonTriggers+GlobalLighting+WaypointsList), just shifted
    orig_tail = bytes(buf[ol["de"]:])
    new_tail  = out[ol["ds"] + len(new_ol_data):]
    assert new_tail == orig_tail, "trailing chunks NOT byte-identical!"
    print("VERIFY tail: PolygonTriggers+GlobalLighting+WaypointsList byte-identical (%d bytes, shifted)" %
          len(orig_tail))

    # head: everything up to ObjectsList data-start identical except the 4-byte dsize field
    assert out[:ol["hp"]+6] == bytes(buf[:ol["hp"]+6]), "pre-ObjectsList bytes altered"
    assert out[ol["hp"]+10:ol["ds"]] == bytes(buf[ol["hp"]+10:ol["ds"]]), "ObjectsList header tail altered"
    print("VERIFY head: all bytes before ObjectsList data identical (only the 4-byte dataSize changed, %d->%d)"
          % (ol["dsize"], new_ol_dsize))

    # ================= package (map UNCOMPRESSED + new INI) + install =================
    entries = [BigEntry(MAP_PATH, out), BigEntry(NEW_INI_PATH, ini_bytes)]
    big_bytes = write_big(entries)
    rt = read_big(big_bytes)
    assert len(rt) == 2, "expected 2 entries"
    assert find_entry(rt, MAP_PATH).data == out, "map round-trip failed"
    assert find_entry(rt, NEW_INI_PATH).data == ini_bytes, "INI round-trip failed"
    print("BIG round-trip OK (2 entries: uncompressed map + %s)" % NEW_INI_PATH)

    # sort-position guard: no higher-sorting archive may own the map path OR the INI path
    for d in (SPE, SHW):
        for f in os.listdir(d):
            if not f.lower().endswith(".big") or f.lower() <= OUT_NAME.lower(): continue
            for e in read_big(os.path.join(d, f)):
                assert e.path.lower() != MAP_PATH.lower(), "%s sorts above us and owns the map!" % f
                assert e.path.lower() != NEW_INI_PATH.lower(), "%s sorts above us and owns the new INI!" % f
    print("sort-position OK: no higher archive owns the map or the new INI path")

    staged = os.path.join(HERE, OUT_NAME)
    with open(staged, "wb") as fh:
        fh.write(big_bytes)
    stage_md5 = hashlib.md5(open(staged, "rb").read()).hexdigest()
    if STAGE:
        print("STAGED ONLY (no install; game may be running): %s" % staged)
        print("staged md5: %s" % stage_md5)
    else:
        md5s = {}
        for d in (SPE, SHW):
            p = os.path.join(d, OUT_NAME)
            with open(p, "wb") as fh:
                fh.write(big_bytes)
            md5s[d] = hashlib.md5(open(p, "rb").read()).hexdigest()
            inst = read_big(p)
            assert find_entry(inst, MAP_PATH).data == out
            assert find_entry(inst, NEW_INI_PATH).data == ini_bytes
        assert len(set(md5s.values())) == 1 and stage_md5 in md5s.values(), "installed archives differ!"
        print("installed to both mod dirs; md5 match: %s" % stage_md5)
    print("OUT: %s (%d bytes)" % (OUT_NAME, len(big_bytes)))

    # ---- report ----
    print("\n=== REMOVED China templates (all military/buildings) ===")
    for tn, k in rem_tmpls.most_common():
        print("   -%-40s x%d" % (tn, k))
    print("named units removed (objectName): %d  e.g. %s" %
          (len(named_removed), ", ".join(sorted({n for _, n in named_removed})[:8])))
    print("\n=== 3 GOD-EMPERORS (%s, StartingLevel=%s, owner=%s) ===" % (NEW_OBJ, MAX_VET, CORE_TEAM))
    for (tmpl, x, y, ang, uid) in added_emp:
        print("   %-24s (%4d,%4d) ang=%6.3f  %s" % (tmpl, x, y, ang, uid))
    print("=== GLA SWARM (owner=%s, aggressiveness=%d) ===" % (SWARM_TEAM, AGGRESSIVE))
    for (tmpl, x, y, ang, uid) in added_swarm:
        print("   %-24s (%4d,%4d) ang=%6.3f  %s" % (tmpl, x, y, ang, uid))

if __name__ == "__main__":
    main()
