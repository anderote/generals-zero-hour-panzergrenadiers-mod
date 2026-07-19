#!/usr/bin/env python3
"""Assemble a CLEAN grass-field shellmap on Green Pastures terrain that BOOTS in
the ShockWave shell -- ship as Maps\\ShellMapSHW\\ShellMapSHW.map in the ShellKwai
layer.

Prior grass build crashed (SIGSEGV) because Green Pastures ships skirmish-slot
players (SkirmishChina/GLA) the main-menu shell never instantiates -> null deref.
FIX: transplant the EXACT player+team set from the proven-good ShockWave
ShellMapSHW (which boots), re-encoded into Green Pastures' own symbol table.

WHAT WE DO (all on the decoded CkMp buffer):
 1. TERRAIN untouched: HeightMapData/BlendTileData/WorldInfo/GlobalLighting/
    PolygonTriggers/WaypointsList chunk bytes are copied byte-for-byte.
 2. SYMBOL TABLE: keep every existing Green Pastures (id,name) stable; APPEND two
    nameKeys the shell content needs but GP lacks: 'playerColor', 'objectAggressiveness'.
 3. SIDESLIST: replace GP's 14 skirmish players with the 13 shell players from
    ShockWave ShellMapSHW (Neutral, PlyrCivilian, PlyrGLA, PlyrGLAYellow, ...),
    re-encoded to GP nameKey ids -- PlyrGLA<->PlyrGLAYellow mutual hostility comes
    baked in. Teams = the shell's SINGLETON teams (each player's home team, incl.
    teamPlyrGLA + teamPlyrGLAYellow); GP's own (empty) PlayerScriptsList kept
    verbatim (static camera, no scripts).
 4. OBJECTS: strip GP scenery, keep GP waypoints (WaypointsList links stay valid),
    add 3 Tank_ShellEmperorElite (owner teamPlyrGLAYellow, objectAggressiveness=1
    ALERT: fire+hold) tight at flat centre (~1250,1620), a ring of 17 GLA attackers
    (owner teamPlyrGLA, objectAggressiveness=2 AGGRESSIVE: charge), and one
    InitialCameraPosition waypoint at centre (shell lookAt frames the fight).
 5. MAP.INI: ship an empty Maps\\ShellMapSHW\\Map.ini to override the stale
    ShockWave one (21 old-scene object overrides) so nothing mismatched applies.

AttitudeType (engine AI.h): SLEEP=-2 PASSIVE=-1 NORMAL=0 ALERT=1 AGGRESSIVE=2;
objectAggressiveness read at Object.cpp:3610 (TheKey_objectAggressiveness).

Fail-closed: whole buffer re-parsed; terrain byte-identity, symbol-table validity,
sides/teams, objects+attitudes+templates all asserted. Store UNCOMPRESSED.
"""
import os, sys, struct, hashlib, re, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon")); sys.path.insert(0, HERE)
from bigfile import BigEntry, read_big, write_big, find_entry
from refpack import strip_ear, refpack_decompress
from _eff import ARCHIVES, _CACHE
import build_shellmap_showcase as SHOW   # reuse build_new_ini() for ShellEmperorElite.ini

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW = os.path.expanduser("~/GeneralsX/mods/ShockWave")
GAME = os.path.expanduser("~/GeneralsX/GeneralsZH")
SHIP_PATH = "Maps\\ShellMapSHW\\ShellMapSHW.map"
MAPINI_PATH = "Maps\\ShellMapSHW\\Map.ini"
OUT_NAME = "zzz-ZZZZZZZZZZZZZZ0ShellKwai.big"
NEW_INI_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\ShellEmperorElite.ini"
NEW_OBJ = "Tank_ShellEmperorElite"
WAYPOINT_TMPL = "*Waypoints/Waypoint"
SW_MAP_OWNER = "!Shw_maps.big"

CX, CY = 1250.0, 1620.0
FRIEND_TEAM, ENEMY_TEAM = "teamPlyrGLAYellow", "teamPlyrGLA"
ALERT, AGGRESSIVE = 1, 2
EMPERORS = [(1250, 1598), (1216, 1650), (1284, 1650)]
SWARM = [
    ("GLAInfantryRebel",           15, 115), ("GLAInfantryRebel",          65, 115),
    ("GLAInfantryRebel",          125, 115), ("GLAInfantryRebel",         195, 115),
    ("GLAInfantryRebel",          245, 115), ("GLAInfantryRebel",         315, 115),
    ("GLAVehicleRocketBuggy",      40, 158), ("GLAVehicleRocketBuggy",    130, 158),
    ("GLAVehicleRocketBuggy",     220, 158), ("GLAVehicleRocketBuggy",    310, 158),
    ("GLAVehicleTechnical",         0, 138), ("GLAVehicleTechnical",      120, 138),
    ("GLAVehicleTechnical",       240, 138),
    ("GLAVehicleQuadCannon",       90, 148), ("GLAVehicleQuadCannon",     270, 148),
    ("Salv_GLAVehicleMI8Gunship",  60, 160), ("Salv_GLAVehicleMI8Gunship",300, 160),
]

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

def s(v): return v.decode("latin-1") if isinstance(v, (bytes, bytearray)) else v

# ---------------------------------------------------------------- map helpers
def parse_symbols(buf):
    assert buf[:4] == b"CkMp"
    pos = 4; (count,) = struct.unpack_from("<i", buf, pos); pos += 4
    id2name = {}
    for _ in range(count):
        ln = buf[pos]; pos += 1
        id2name[struct.unpack_from("<I", buf, pos+ln)[0]] = buf[pos:pos+ln].decode("latin-1")
        pos += ln + 4
    return id2name, {v: k for k, v in id2name.items()}, pos

def top_chunks(buf, id2name, start):
    top = []; p = start
    while p + 10 <= len(buf):
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        nm = id2name.get(cid)
        if nm is None or dsize < 0 or p+10+dsize > len(buf): raise ValueError("bad chunk @%d" % p)
        top.append(dict(nm=nm, cid=cid, ver=ver, dsize=dsize, hp=p, ds=p+10, de=p+10+dsize))
        p = p+10+dsize
    if p != len(buf): raise ValueError("walk != EOF (%d/%d)" % (p, len(buf)))
    return top

def parse_objects(buf, ol):
    objs = []; p = ol["ds"]
    while p + 10 <= ol["de"]:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        ds = p+10; de = ds+dsize
        if de > ol["de"] or dsize < 0: raise ValueError("obj overrun @%d" % p)
        (slen,) = struct.unpack_from("<H", buf, ds+20)
        tn = buf[ds+22:ds+22+slen].decode("latin-1")
        pairs, dend = read_dict(buf, ds+22+slen)
        if dend != de: raise ValueError("dict end mismatch %s" % tn)
        objs.append(dict(hp=p, ds=ds, de=de, ver=ver, cid=cid, tn=tn,
                         pairs=pairs, d={k: v for k, _, v in pairs}))
        p = de
    if p != ol["de"]: raise ValueError("obj walk != end")
    return objs

def decode_mapbytes(raw):
    if raw[:4] == b"CkMp": return bytes(raw)
    stream, _ = strip_ear(raw); buf, _ = refpack_decompress(stream); return buf

def load_green_pastures():
    for b in glob.glob(os.path.join(GAME, "*.big")):
        try: ents = read_big(b)
        except: continue
        for e in ents:
            if e.path.lower() == "maps\\green pastures\\green pastures.map":
                return decode_mapbytes(e.data), os.path.basename(b)
    raise SystemExit("Green Pastures not found")

def load_working_shell_sides():
    """Return (player_prop_lists, singleton_team_prop_lists) as [(name,type,value)]
       decoded from the proven-good ShockWave ShellMapSHW SidesList."""
    src = read_big(os.path.join(SPE, SW_MAP_OWNER))
    ent = find_entry(src, "Maps\\ShellMapSHW\\ShellMapSHW.map")
    buf = decode_mapbytes(ent.data)
    id2name, n2i, DS = parse_symbols(buf)
    top = top_chunks(buf, id2name, DS)
    sl = next(t for t in top if t["nm"] == "SidesList")
    q = sl["ds"]; (nsides,) = struct.unpack_from("<i", buf, q); q += 4
    players = []
    for i in range(nsides):
        pairs, q = read_dict(buf, q); (nb,) = struct.unpack_from("<i", buf, q); q += 4
        assert nb == 0, "working shell has buildlists -- unexpected"
        players.append([(id2name[k], t, v) for (k, t, v) in pairs])
    (nteams,) = struct.unpack_from("<i", buf, q); q += 4
    singles = []
    tkeyid = n2i["teamIsSingleton"]
    for i in range(nteams):
        pairs, q = read_dict(buf, q)
        d = {k: v for (k, _, v) in pairs}
        if d.get(tkeyid) == 1:      # keep only singleton (home) teams
            singles.append([(id2name[k], t, v) for (k, t, v) in pairs])
    return players, singles

# ---------------------------------------------------------------- main
def main():
    buf, gp_owner = load_green_pastures()
    print("base terrain: Green Pastures (%s), %d bytes" % (gp_owner, len(buf)))
    id2name, n2i, DATA_START = parse_symbols(buf)
    order = list(id2name.keys())                  # preserve original id order
    top = top_chunks(buf, id2name, DATA_START)
    print("top-level:", [t["nm"] for t in top])
    ol = next(t for t in top if t["nm"] == "ObjectsList")
    sl = next(t for t in top if t["nm"] == "SidesList")

    # ---- (2) grow symbol table: append playerColor + objectAggressiveness ----
    maxid = max(id2name)
    new_syms = []
    for nm in ("playerColor", "objectAggressiveness"):
        if nm not in n2i:
            maxid += 1; id2name[maxid] = nm; n2i[nm] = maxid; order.append(maxid); new_syms.append((maxid, nm))
    def build_symbol_table():
        out = bytearray(b"CkMp"); out += struct.pack("<i", len(order))
        for i in order:
            nb = id2name[i].encode("latin-1")
            out += struct.pack("<B", len(nb)) + nb + struct.pack("<I", i)
        return bytes(out)
    sym_bytes = build_symbol_table()
    print("(2) symbol table: %d -> %d (appended %s)" %
          (len(order)-len(new_syms), len(order), [nm for _, nm in new_syms]))

    # ---- (3) SidesList: transplant proven-good shell players + singleton teams ----
    players, singles = load_working_shell_sides()
    def enc_props(proplist):   # [(name,type,value)] -> dict bytes using GP ids
        return enc_dict([(n2i[nm], t, v) for (nm, t, v) in proplist])
    # extract GP's PlayerScriptsList sub-chunk (verbatim) = tail after GP teams
    q = sl["ds"]; (gp_ns,) = struct.unpack_from("<i", buf, q); q += 4
    for _ in range(gp_ns):
        _, q = read_dict(buf, q); (nb,) = struct.unpack_from("<i", buf, q); q += 4; assert nb == 0
    (gp_nt,) = struct.unpack_from("<i", buf, q); q += 4
    for _ in range(gp_nt):
        _, q = read_dict(buf, q)
    gp_scripts = bytes(buf[q:sl["de"]])           # PlayerScriptsList sub-chunk, verbatim
    new_sides = bytearray(struct.pack("<i", len(players)))
    for pl in players:
        for nm, _, _ in pl: assert nm in n2i, "player key missing from symtab: " + nm
        new_sides += enc_props(pl) + struct.pack("<i", 0)
    new_sides += struct.pack("<i", len(singles))
    for tm in singles:
        for nm, _, _ in tm: assert nm in n2i, "team key missing from symtab: " + nm
        new_sides += enc_props(tm)
    new_sides += gp_scripts
    new_sl_data = bytes(new_sides)
    pnames = [next(s(v) for nm, t, v in pl if nm == "playerName") for pl in players]
    tnames = [next(s(v) for nm, t, v in tm if nm == "teamName") for tm in singles]
    assert FRIEND_TEAM in tnames and ENEMY_TEAM in tnames, "required teams missing from transplant"
    print("(3) SidesList: %d shell players %s ; %d singleton teams (incl %s,%s); GP scripts kept verbatim" %
          (len(players), [p for p in pnames if p][:6], len(singles), FRIEND_TEAM, ENEMY_TEAM))

    # ---- (4) ObjectsList: keep GP waypoints, drop scenery, add scene ----
    objs = parse_objects(buf, ol)
    unit_donor = next(o["pairs"] for o in objs if "Waypoint" not in o["tn"])
    wp_donor   = next(o["pairs"] for o in objs if o["tn"] == WAYPOINT_TMPL)
    base_wpids = [o["d"].get(n2i["waypointID"]) for o in objs if o["tn"] == WAYPOINT_TMPL]
    kept = [o for o in objs if "Waypoint" in o["tn"]]
    kept_bytes = b"".join(bytes(buf[o["hp"]:o["de"]]) for o in kept)
    cid_obj, ver_obj = n2i["Object"], objs[0]["ver"]

    roster = SHOW.roster_objects()
    ini_bytes, ini_owner = SHOW.build_new_ini()
    ini_objs = set(re.findall(r"(?mi)^\s*Object\s+(\S+)", ini_bytes.decode("latin-1")))
    roster_plus = roster | ini_objs
    for tmpl in [NEW_OBJ] + [t[0] for t in SWARM]:
        assert tmpl in roster_plus, "template unresolved: " + tmpl

    def author(template, x, y, ang, uid, team, donor, aggr=None, extra=None):
        pairs = [[k, t, v] for (k, t, v) in donor]
        def setk(key, typ, val):
            for pr in pairs:
                if pr[0] == key: pr[1], pr[2] = typ, val; return
            pairs.append([key, typ, val])
        setk(n2i["objectInitialHealth"], 1, 100)
        setk(n2i["originalOwner"], 3, team.encode("latin-1"))
        setk(n2i["uniqueID"], 3, uid.encode("latin-1"))
        if aggr is not None: setk(n2i["objectAggressiveness"], 1, aggr)
        for (k, t, v) in (extra or []): setk(k, t, v)
        body = (struct.pack("<ffff", x, y, 0.0, ang) + struct.pack("<i", 0) +
                struct.pack("<H", len(template)) + template.encode("latin-1") +
                enc_dict([(k, t, v) for k, t, v in pairs]))
        return struct.pack("<IHi", cid_obj, ver_obj, len(body)) + body

    new_obj = bytearray(); added_emp = []; added_swarm = []; idx = 0
    for (x, y) in EMPERORS:
        dx, dy = x-CX, y-CY
        ang = math.atan2(dy, dx) if dx*dx+dy*dy >= 20*20 else -1.571
        uid = "SHOWCASE_EMPEROR_%02d" % idx; idx += 1
        new_obj += author(NEW_OBJ, float(x), float(y), ang, uid, FRIEND_TEAM, unit_donor, aggr=ALERT)
        added_emp.append((NEW_OBJ, x, y, round(ang, 3), uid))
    for (tmpl, adeg, r) in SWARM:
        a = math.radians(adeg); x = CX + r*math.cos(a); y = CY + r*math.sin(a)
        ang = math.atan2(CY-y, CX-x); uid = "SHOWCASE_SWARM_%02d" % idx; idx += 1
        new_obj += author(tmpl, float(x), float(y), ang, uid, ENEMY_TEAM, unit_donor, aggr=AGGRESSIVE)
        added_swarm.append((tmpl, round(x), round(y), round(ang, 3), uid))
    CAM_WPID = 9990; assert CAM_WPID not in base_wpids
    new_obj += author(WAYPOINT_TMPL, CX, CY, 0.0, "InitialCameraPosition", "team", wp_donor,
                      extra=[(n2i["waypointID"], 1, CAM_WPID),
                             (n2i["waypointName"], 3, b"InitialCameraPosition")])
    n_added = len(EMPERORS) + len(SWARM) + 1
    new_ol_data = kept_bytes + bytes(new_obj)
    print("(4) ObjectsList: kept %d waypoints, dropped %d scenery, added 3 Emperors(ALERT) + %d swarm(AGGRESSIVE) + 1 cam"
          % (len(kept), len(objs)-len(kept), len(SWARM)))

    # ---- reassemble ----
    out = bytearray(sym_bytes)
    for t in top:
        if t["nm"] == "SidesList":
            out += struct.pack("<IHi", t["cid"], t["ver"], len(new_sl_data)) + new_sl_data
        elif t["nm"] == "ObjectsList":
            out += struct.pack("<IHi", t["cid"], t["ver"], len(new_ol_data)) + new_ol_data
        else:
            out += buf[t["hp"]:t["de"]]
    out = bytes(out)
    print("reassembled: %d bytes" % len(out))

    # ================= HARD VERIFY (fail-closed) =================
    id2b, n2b, DS2 = parse_symbols(out)
    for i, nm in id2name.items(): assert id2b.get(i) == nm, "symbol id %d changed" % i
    assert len(id2b) == len(id2name) and n2b["playerColor"] and n2b["objectAggressiveness"]
    top2 = top_chunks(out, id2b, DS2)
    assert [t["nm"] for t in top2] == [t["nm"] for t in top], "chunk sequence changed"
    print("VERIFY symtab+tree: existing %d ids stable + 2 appended; 8 siblings; walk ends at EOF; sizes consistent" % (len(id2name)-len(new_syms)))

    for nm in ("HeightMapData","BlendTileData","WorldInfo","GlobalLighting","PolygonTriggers","WaypointsList"):
        a = next(t for t in top if t["nm"] == nm); b = next(t for t in top2 if t["nm"] == nm)
        assert out[b["hp"]:b["de"]] == buf[a["hp"]:a["de"]], nm + " changed!"
    print("VERIFY terrain: HeightMapData+BlendTileData+WorldInfo+GlobalLighting+PolygonTriggers+WaypointsList byte-identical")

    # SidesList decode
    sl2 = next(t for t in top2 if t["nm"] == "SidesList"); q = sl2["ds"]
    (ns,) = struct.unpack_from("<i", out, q); q += 4
    enemy_of = {}   # name -> UNION of enemies across duplicate player entries
    for i in range(ns):
        pairs, q = read_dict(out, q); (nb,) = struct.unpack_from("<i", out, q); q += 4
        d = {id2b[k]: v for (k, _, v) in pairs}
        nm = s(d.get("playerName")); en = (s(d.get("playerEnemies")) or "").split()
        if nm: enemy_of.setdefault(nm, set()).update(en)
    (nt,) = struct.unpack_from("<i", out, q); q += 4
    tset = set()
    for i in range(nt):
        pairs, q = read_dict(out, q); d = {id2b[k]: v for (k, _, v) in pairs}
        tset.add(s(d.get("teamName")))
    assert ns == len(players) and nt == len(singles)
    assert "PlyrGLA" in enemy_of.get("PlyrGLAYellow", set()) and "PlyrGLAYellow" in enemy_of.get("PlyrGLA", set()), \
        "PlyrGLA<->PlyrGLAYellow hostility missing"
    assert FRIEND_TEAM in tset and ENEMY_TEAM in tset
    print("VERIFY sides: %d shell players, %d teams; PlyrGLA<->PlyrGLAYellow mutual; %s+%s present" %
          (ns, nt, FRIEND_TEAM, ENEMY_TEAM))

    # ObjectsList
    ol2 = next(t for t in top2 if t["nm"] == "ObjectsList"); objs2 = parse_objects(out, ol2)
    assert len(objs2) == len(kept) + n_added
    emp = [o for o in objs2 if o["tn"] == NEW_OBJ]
    swm = [o for o in objs2 if s(o["d"].get(n2i["uniqueID"], b"")).startswith("SHOWCASE_SWARM_")]
    cam = [o for o in objs2 if s(o["d"].get(n2i["waypointName"], b"")) == "InitialCameraPosition"]
    assert len(emp) == 3 and len(swm) == len(SWARM) and len(cam) == 1
    aggid = n2i["objectAggressiveness"]
    assert all(o["d"].get(aggid) == ALERT and s(o["d"].get(n2i["originalOwner"]))==FRIEND_TEAM for o in emp), "emperor attitude/team"
    assert all(o["d"].get(aggid) == AGGRESSIVE and s(o["d"].get(n2i["originalOwner"]))==ENEMY_TEAM for o in swm), "swarm attitude/team"
    for o in objs2:
        if o["tn"] != WAYPOINT_TMPL: assert o["tn"] in roster_plus, "unresolved: " + o["tn"]
    my_uids = [s(o["d"].get(n2i["uniqueID"], b"")) for o in objs2
               if s(o["d"].get(n2i["uniqueID"], b"")).startswith("SHOWCASE_") or
                  s(o["d"].get(n2i["uniqueID"], b"")) == "InitialCameraPosition"]
    assert len(my_uids) == len(set(my_uids)) == n_added
    onk = n2i.get("objectName")
    assert all(not o["d"].get(onk) for o in objs2 if s(o["d"].get(n2i["uniqueID"], b"")).startswith("SHOWCASE_"))
    cx, cy = struct.unpack_from("<ff", out, cam[0]["ds"]); assert abs(cx-CX) < 1 and abs(cy-CY) < 1
    print("VERIFY objects: %d total (%d waypoints + 3 Emp[ALERT/%s] + %d swarm[AGGR/%s] + cam@(%.0f,%.0f)); "
          "templates resolve; uids unique; objectNames blank" %
          (len(objs2), len(kept), FRIEND_TEAM, len(SWARM), ENEMY_TEAM, cx, cy))

    # ================= package + install =================
    mapini = (b";GeneralsX Kwai shell (Green Pastures terrain). Intentionally EMPTY -- overrides the\n"
              b";stale ShockWave ShellMapSHW Map.ini (21 old-scene object tweaks) so nothing mismatched applies.\n")
    entries = [BigEntry(SHIP_PATH, out), BigEntry(NEW_INI_PATH, ini_bytes), BigEntry(MAPINI_PATH, mapini)]
    big_bytes = write_big(entries)
    rt = read_big(big_bytes)
    assert len(rt) == 3
    assert find_entry(rt, SHIP_PATH).data == out
    assert find_entry(rt, NEW_INI_PATH).data == ini_bytes
    assert find_entry(rt, MAPINI_PATH).data == mapini
    print("BIG round-trip OK (3 entries: map + ShellEmperorElite.ini + empty Map.ini)")

    for d in (SPE, SHW):
        for f in os.listdir(d):
            if not f.lower().endswith(".big") or f.lower() <= OUT_NAME.lower(): continue
            for e in read_big(os.path.join(d, f)):
                assert e.path.lower() not in (SHIP_PATH.lower(), NEW_INI_PATH.lower(), MAPINI_PATH.lower()), \
                    "%s sorts above us and owns %s" % (f, e.path)
    print("sort-position OK (nothing higher owns map/INI/Map.ini)")

    with open(os.path.join(HERE, OUT_NAME), "wb") as fh: fh.write(big_bytes)
    md5s = {}
    for d in (SPE, SHW):
        p = os.path.join(d, OUT_NAME)
        with open(p, "wb") as fh: fh.write(big_bytes)
        md5s[d] = hashlib.md5(open(p, "rb").read()).hexdigest()
        inst = read_big(p)
        assert find_entry(inst, SHIP_PATH).data == out
        assert find_entry(inst, MAPINI_PATH).data == mapini
    assert len(set(md5s.values())) == 1
    print("installed to both dirs; md5 match: %s ; OUT %s (%d bytes)" %
          (list(md5s.values())[0], OUT_NAME, len(big_bytes)))

    print("\n=== 3 EMPERORS (%s, owner=%s, ALERT) ===" % (NEW_OBJ, FRIEND_TEAM))
    for r in added_emp: print("   %-22s (%4d,%4d) ang=%6.3f %s" % r)
    print("=== SWARM (owner=%s, AGGRESSIVE) ===" % ENEMY_TEAM)
    for r in added_swarm: print("   %-22s (%4d,%4d) ang=%6.3f %s" % r)

if __name__ == "__main__":
    main()
