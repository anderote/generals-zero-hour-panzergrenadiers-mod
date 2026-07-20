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
 (4) ETERNAL WAVES: the battle must never end.  Adds 3 reinforcement teams
     (PlyrGLA, 8 mixed units each, mirroring the swarm composition) + 7 map
     scripts on PlyrGLA's ScriptList (1 one-shot init, 3 repeating wave
     spawners, 3 rearm subroutines).  Loop per lane X in {A,B,C}:
       init:   SET_MILLISECOND_TIMER SW_EW_TimerX = 5/25/45 s   (staggered)
       wave:   TIMER_EXPIRED(SW_EW_TimerX) -> CREATE_REINFORCEMENT_TEAM at an
               ORIGINAL GLA entry waypoint + TEAM_HUNT + re-set timer to 240 s
               (failsafe only)
       rearm:  the team dict's teamOnDestroyedScript fires SW_EW_Rearm_X when
               the wave is 75% destroyed (teamDestroyedThreshold) -> timer 20 s
     Population is hard-capped: a lane cannot respawn until its newest team
     instance is >=75% dead (engine GCs empty team instances every frame --
     TeamPrototype::updateState -- so gating on TEAM_DESTROYED conditions would
     deadlock at zero instances; the onDestroyed hook fires while the instance
     still exists, which is why it is used instead).  Steady-state live GLA
     from waves <= 3 lanes x 8 units + <=2 stragglers each ~= 30 (< ~40 target).
     All action/condition enums+NameKeys and chunk versions (ScriptList v1,
     Script v2, OrCondition v1, Condition v4, ScriptAction v2) were harvested
     from this map's own existing chunks; one new map symbol is appended
     (teamOnDestroyedScript, engine key from WellKnownKeys.h DEFINE_KEY).

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

# --- (4) ETERNAL WAVES: endless respawning GLA attack lanes -------------------
GLA_SIDE   = "PlyrGLA"                   # side index owns the wave scripts
GLA_LIST_IDX = 2                         # ScriptList index of PlyrGLA (asserted)
WAVE_UNITS = [("GLAInfantryRebel", 4),   # mirrors the swarm mix: inf/veh/air
              ("GLAVehicleRocketBuggy", 1), ("GLAVehicleTechnical", 1),
              ("GLAVehicleQuadCannon", 1), ("Salv_GLAVehicleMI8Gunship", 1)]
# lane id, ORIGINAL GLA entry waypoint (must exist in ObjectsList), first-wave delay s
WAVES = [("A", "Spawn Team Cycles ", 5.0),    # east  approach (ang ~12, d~731)
         ("B", "Starthiplanding",    25.0),   # NW    approach (ang ~115, d~627)
         ("C", "Spawnsab",           45.0)]   # SW    approach (ang ~221, d~417)
WAVE_TEAM   = "teamSWEternalWave%s"
WAVE_TIMER  = "SW_EW_Timer%s"
WAVE_SCRIPT = "SW_EW_Wave_%s"
REARM_SCRIPT = "SW_EW_Rearm_%s"
INIT_SCRIPT  = "SW_EW_Init"
REARM_SECONDS    = 20.0     # next wave this long after previous is 75% dead
FAILSAFE_SECONDS = 240.0    # lane self-heals even if onDestroyed never fires
DESTROY_THRESH   = 0.75     # fraction destroyed that counts as wave death
NEW_TEAM_KEY = "teamOnDestroyedScript"   # appended to the map symbol table
# enums + parameter types harvested from THIS map's existing chunks
COND_TRUE, COND_TIMER_EXPIRED = 3, 4
ACT_CREATE_REINFORCEMENT_TEAM, ACT_TEAM_HUNT, ACT_SET_MSEC_TIMER = 34, 60, 20
P_INT, P_REAL, P_TEAM, P_COUNTER, P_WAYPOINT = 0, 1, 3, 4, 7

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

# ------------------------------------------------- (4) eternal-wave machinery
def enc_ascii(txt):
    b = txt.encode("latin-1")
    return struct.pack("<H", len(b)) + b

def rd_ascii(buf, p):
    (n,) = struct.unpack_from("<H", buf, p); p += 2
    return buf[p:p+n].decode("latin-1"), p + n

def enc_chunk(name2id, nm, ver, payload):
    return struct.pack("<IHi", name2id[nm], ver, len(payload)) + payload

def enc_parm(ptype, i=0, r=0.0, s=""):
    return struct.pack("<i", ptype) + struct.pack("<i", i) + struct.pack("<f", r) + enc_ascii(s)

def enc_content(name2id, chunk_nm, ver, enum, type_name, parms):
    """Condition (v4) / ScriptAction (v2): i32 enum, u32 (nameId<<8)|3, i32 n, parms."""
    payload = (struct.pack("<i", enum) + struct.pack("<I", (name2id[type_name] << 8) | 3) +
               struct.pack("<i", len(parms)) + b"".join(parms))
    return enc_chunk(name2id, chunk_nm, ver, payload)

def enc_script(name2id, name, active, oneshot, subroutine, conditions, actions):
    """Script v2 chunk: 4 strings, 6 flag bytes (active,oneshot,e,n,h,sub), i32 delay,
    one OrCondition v1 wrapping `conditions`, then ScriptAction chunks."""
    orc = enc_chunk(name2id, "OrCondition", 1, b"".join(conditions))
    payload = (enc_ascii(name) + enc_ascii("") * 3 +
               bytes([active, oneshot, 1, 1, 1, subroutine]) + struct.pack("<i", 0) +
               orc + b"".join(actions))
    return enc_chunk(name2id, "Script", 2, payload)

def walk_sides(buf, sl, id2name):
    """Parse SidesList v3 data: sides (+empty buildlists), teams, PlayerScriptsList."""
    assert sl["ver"] == 3, "SidesList version %d" % sl["ver"]
    p = sl["ds"]
    (nsides,) = struct.unpack_from("<i", buf, p); p += 4
    sides = []
    for _ in range(nsides):
        pairs, p = read_dict(buf, p)
        (nb,) = struct.unpack_from("<i", buf, p); p += 4
        assert nb == 0, "non-empty buildlist unsupported"
        sides.append({id2name.get(k, k): v for (k, _, v) in pairs})
    teams_cnt_off = p
    (nteams,) = struct.unpack_from("<i", buf, p); p += 4
    teams = []
    for _ in range(nteams):
        t0 = p
        pairs, p = read_dict(buf, p)
        teams.append((t0, p, pairs))
    psl_hp = p
    cid, psl_ver, dsize = struct.unpack_from("<IHi", buf, p)
    assert id2name.get(cid) == "PlayerScriptsList", "expected PlayerScriptsList @%d" % p
    psl_ds, psl_de = p + 10, p + 10 + dsize
    assert psl_de == sl["de"], "PlayerScriptsList must end SidesList"
    lists = []
    q = psl_ds
    while q < psl_de:
        cid2, lver, ds2 = struct.unpack_from("<IHi", buf, q)
        assert id2name.get(cid2) == "ScriptList", "expected ScriptList @%d" % q
        lists.append(dict(hp=q, ver=lver, ds=q + 10, de=q + 10 + ds2))
        q = q + 10 + ds2
    assert q == psl_de, "ScriptList walk ended @%d != %d" % (q, psl_de)
    return sides, teams_cnt_off, teams, dict(hp=psl_hp, ver=psl_ver, ds=psl_ds, de=psl_de), lists

def walk_script_tree(buf, id2name, start, end, sink):
    """Recursively validate every Script/OrCondition/Condition/ScriptAction chunk;
    collect script names/flags and condition/action contents into sink."""
    p = start
    while p < end:
        cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
        nm = id2name.get(cid)
        ds, de = p + 10, p + 10 + dsize
        assert de <= end and dsize >= 0, "chunk overrun @%d" % p
        q = ds
        if nm == "ScriptGroup":
            _gname, q = rd_ascii(buf, q)
            q += 1 + (1 if ver >= 2 else 0)     # active [, subroutine]
            walk_script_tree(buf, id2name, q, de, sink)
        elif nm == "Script":
            sname, q = rd_ascii(buf, q)
            for _ in range(3):
                _c, q = rd_ascii(buf, q)
            flags = bytes(buf[q:q+6]); q += 6
            assert ver >= 2, "Script chunk v%d" % ver
            (_delay,) = struct.unpack_from("<i", buf, q); q += 4
            sink["scripts"].append((sname, flags, ds, de))
            walk_script_tree(buf, id2name, q, de, sink)
        elif nm == "OrCondition":
            walk_script_tree(buf, id2name, q, de, sink)
        elif nm in ("Condition", "ScriptAction", "ScriptActionFalse"):
            (enum,) = struct.unpack_from("<i", buf, q); q += 4
            (keyraw,) = struct.unpack_from("<I", buf, q); q += 4
            assert keyraw & 0xFF == 3, "namekey low byte %d" % (keyraw & 0xFF)
            (nparms,) = struct.unpack_from("<i", buf, q); q += 4
            parms = []
            for _ in range(nparms):
                (ptype,) = struct.unpack_from("<i", buf, q); q += 4
                if ptype == 17:                  # COORD3D: 3 floats
                    q += 12
                    parms.append((ptype, None, None, None))
                else:
                    (pi,) = struct.unpack_from("<i", buf, q); q += 4
                    (pr,) = struct.unpack_from("<f", buf, q); q += 4
                    ps, q = rd_ascii(buf, q)
                    parms.append((ptype, pi, pr, ps))
            assert q == de, "%s payload end %d != chunk end %d" % (nm, q, de)
            sink["contents"].append((nm, enum, id2name.get(keyraw >> 8), parms))
        else:
            raise AssertionError("unexpected chunk %r in script tree @%d" % (nm, p))
        p = de
    assert p == end, "script tree walk ended @%d != %d" % (p, end)

def build_wave_team_dict(name2id, key_ondestroyed, lane):
    """Team Dict mirroring the map's own team encodings (see 'Team Cycles')."""
    n = name2id
    pairs = [(n["teamName"], 3, WAVE_TEAM % lane), (n["teamOwner"], 3, GLA_SIDE),
             (n["teamIsSingleton"], 0, 0), (n["teamProductionPriority"], 1, 0)]
    for i in range(7):
        cnt = WAVE_UNITS[i][1] if i < len(WAVE_UNITS) else 0
        pairs += [(n["teamUnitMaxCount%d" % (i + 1)], 1, cnt),
                  (n["teamUnitMinCount%d" % (i + 1)], 1, cnt)]
    pairs += [(n["teamDescription"], 3, "SW eternal wave lane %s" % lane),
              (n["teamMaxInstances"], 1, 5),
              (n["teamProductionPrioritySuccessIncrease"], 1, 0),
              (n["teamProductionPriorityFailureDecrease"], 1, 0),
              (n["teamInitialIdleFrames"], 1, 0),
              (n["teamExecutesActionsOnCreate"], 0, 0),
              (n["teamDestroyedThreshold"], 2, DESTROY_THRESH)]
    for i, (tmpl, _cnt) in enumerate(WAVE_UNITS):
        pairs.append((n["teamUnitType%d" % (i + 1)], 3, tmpl))
    pairs += [(n["teamHome"], 3, ""), (n["teamReinforcementOrigin"], 3, ""),
              (n["teamAggressiveness"], 1, 2), (n["teamIsAIRecruitable"], 0, 0),
              (key_ondestroyed, 3, REARM_SCRIPT % lane)]
    return enc_dict(pairs)

def build_wave_scripts(name2id):
    """The 7 Script chunks appended to PlyrGLA's ScriptList."""
    def msec(timer, seconds):
        return enc_content(name2id, "ScriptAction", 2, ACT_SET_MSEC_TIMER,
                           "SET_MILLISECOND_TIMER",
                           [enc_parm(P_COUNTER, s=timer), enc_parm(P_REAL, r=seconds)])
    out = []
    out.append(enc_script(name2id, INIT_SCRIPT, 1, 1, 0,
        [enc_content(name2id, "Condition", 4, COND_TRUE, "CONDITION_TRUE", [])],
        [msec(WAVE_TIMER % lane, delay) for (lane, _wp, delay) in WAVES]))
    for (lane, wp, _delay) in WAVES:
        team, timer = WAVE_TEAM % lane, WAVE_TIMER % lane
        out.append(enc_script(name2id, WAVE_SCRIPT % lane, 1, 0, 0,
            [enc_content(name2id, "Condition", 4, COND_TIMER_EXPIRED, "TIMER_EXPIRED",
                         [enc_parm(P_COUNTER, s=timer)])],
            [enc_content(name2id, "ScriptAction", 2, ACT_CREATE_REINFORCEMENT_TEAM,
                         "CREATE_REINFORCEMENT_TEAM",
                         [enc_parm(P_TEAM, s=team), enc_parm(P_WAYPOINT, s=wp)]),
             enc_content(name2id, "ScriptAction", 2, ACT_TEAM_HUNT, "TEAM_HUNT",
                         [enc_parm(P_TEAM, s=team)]),
             msec(timer, FAILSAFE_SECONDS)]))
    for (lane, _wp, _delay) in WAVES:
        out.append(enc_script(name2id, REARM_SCRIPT % lane, 1, 0, 1,
            [enc_content(name2id, "Condition", 4, COND_TRUE, "CONDITION_TRUE", [])],
            [msec(WAVE_TIMER % lane, REARM_SECONDS)]))
    return out

def add_eternal_waves(buf):
    """Splice teams + scripts into SidesList and append the one new symbol."""
    id2name, name2id, data_start, top = parse_map(buf)
    assert NEW_TEAM_KEY not in name2id, "symbol already present?"
    sides, teams_cnt_off, teams, psl, lists = walk_sides(
        buf, [t for t in top if t["nm"] == "SidesList"][0], id2name)
    assert s(sides[GLA_LIST_IDX].get("playerName", b"")) == GLA_SIDE, \
        "side[%d] is not %s" % (GLA_LIST_IDX, GLA_SIDE)
    assert len(lists) > GLA_LIST_IDX
    # new symbol id = max existing + 1
    new_id = max(id2name) + 1
    name2id2 = dict(name2id); name2id2[NEW_TEAM_KEY] = new_id
    sym_entry = bytes([len(NEW_TEAM_KEY)]) + NEW_TEAM_KEY.encode("latin-1") + struct.pack("<I", new_id)
    # payload pieces
    team_bytes = b"".join(build_wave_team_dict(name2id2, new_id, lane) for (lane, _w, _d) in WAVES)
    script_bytes = b"".join(build_wave_scripts(name2id2))
    sl = [t for t in top if t["nm"] == "SidesList"][0]
    gl = lists[GLA_LIST_IDX]
    (nteams,) = struct.unpack_from("<i", buf, teams_cnt_off)
    # rebuild PlayerScriptsList: lists before GLA verbatim, GLA list + our scripts, rest verbatim
    new_gl_data = bytes(buf[gl["ds"]:gl["de"]]) + script_bytes
    new_psl_data = (bytes(buf[psl["ds"]:gl["hp"]]) +
                    struct.pack("<IHi", name2id["ScriptList"], gl["ver"], len(new_gl_data)) +
                    new_gl_data + bytes(buf[gl["de"]:psl["de"]]))
    new_sl_data = (bytes(buf[sl["ds"]:teams_cnt_off]) + struct.pack("<i", nteams + len(WAVES)) +
                   bytes(buf[teams_cnt_off + 4:psl["hp"]]) + team_bytes +
                   struct.pack("<IHi", name2id["PlayerScriptsList"], psl["ver"], len(new_psl_data)) +
                   new_psl_data)
    (sym_count,) = struct.unpack_from("<i", buf, 4)
    out = (bytes(buf[:4]) + struct.pack("<i", sym_count + 1) + bytes(buf[8:data_start]) + sym_entry +
           bytes(buf[data_start:sl["hp"]]) +
           struct.pack("<IHi", name2id["SidesList"], sl["ver"], len(new_sl_data)) + new_sl_data +
           bytes(buf[sl["de"]:]))
    return out, new_id

def verify_eternal_waves(before, after, roster):
    """Fail-closed structural + semantic verification of the wave splice."""
    id1, n1, dstart1, top1 = parse_map(before)
    id2, n2, dstart2, top2 = parse_map(after)
    # symbols: exactly one appended, everything else identical
    assert len(id2) == len(id1) + 1 and id2[max(id2)] == NEW_TEAM_KEY
    assert all(id2[k] == v for k, v in id1.items())
    assert bytes(after[8:dstart1]) == bytes(before[8:dstart1])  # original entries prefix-identical
    # top-level: same sequence; only SidesList changed, all other chunk DATA identical
    assert [t["nm"] for t in top2] == [t["nm"] for t in top1]
    for a, b in zip(top1, top2):
        if a["nm"] != "SidesList":
            assert bytes(before[a["ds"]:a["de"]]) == bytes(after[b["ds"]:b["de"]]), \
                "%s data changed" % a["nm"]
    sl1 = [t for t in top1 if t["nm"] == "SidesList"][0]
    sl2 = [t for t in top2 if t["nm"] == "SidesList"][0]
    sides1, tco1, teams1, psl1, lists1 = walk_sides(before, sl1, id1)
    sides2, tco2, teams2, psl2, lists2 = walk_sides(after, sl2, id2)
    # sides identical; teams: +3 appended, originals byte-identical
    assert sides1 == sides2 and len(lists1) == len(lists2)
    assert bytes(before[sl1["ds"]:tco1]) == bytes(after[sl2["ds"]:tco2])
    assert len(teams2) == len(teams1) + len(WAVES)
    for (a0, a1, _), (b0, b1, _) in zip(teams1, teams2):
        assert bytes(before[a0:a1]) == bytes(after[b0:b1]), "original team dict changed"
    new_teams = teams2[len(teams1):]
    team_names, ondestroyed = [], []
    for (_t0, _t1, pairs), (lane, _wp, _d) in zip(new_teams, WAVES):
        d = {id2.get(k, k): v for (k, _typ, v) in pairs}
        assert s(d["teamName"]) == WAVE_TEAM % lane and s(d["teamOwner"]) == GLA_SIDE
        assert d["teamIsSingleton"] == 0 and d["teamAggressiveness"] == 2
        assert abs(d["teamDestroyedThreshold"] - DESTROY_THRESH) < 1e-6
        assert s(d[NEW_TEAM_KEY]) == REARM_SCRIPT % lane
        for i, (tmpl, cnt) in enumerate(WAVE_UNITS):
            assert s(d["teamUnitType%d" % (i + 1)]) == tmpl and tmpl in roster
            assert d["teamUnitMaxCount%d" % (i + 1)] == cnt == d["teamUnitMinCount%d" % (i + 1)]
        team_names.append(s(d["teamName"])); ondestroyed.append(s(d[NEW_TEAM_KEY]))
    # script lists: all except GLA byte-identical; GLA = old bytes + our chunks
    for i, (a, b) in enumerate(zip(lists1, lists2)):
        if i != GLA_LIST_IDX:
            assert bytes(before[a["ds"]:a["de"]]) == bytes(after[b["ds"]:b["de"]]), \
                "ScriptList[%d] changed" % i
    ga, gb = lists1[GLA_LIST_IDX], lists2[GLA_LIST_IDX]
    old_len = ga["de"] - ga["ds"]
    assert bytes(after[gb["ds"]:gb["ds"] + old_len]) == bytes(before[ga["ds"]:ga["de"]])
    # full recursive walk of BOTH trees (validates every chunk boundary + payload);
    # NOTE: our scripts sit at the END of ScriptList[GLA_LIST_IDX], which is in the
    # MIDDLE of the whole-tree walk -- so compare per-list, not flat.
    sink1 = dict(scripts=[], contents=[])
    sink2 = dict(scripts=[], contents=[])
    for L, snk, bb, idm in ((lists1, sink1, before, id1), (lists2, sink2, after, id2)):
        for l in L:
            walk_script_tree(bb, idm, l["ds"], l["de"], snk)
    g1 = dict(scripts=[], contents=[])
    g2 = dict(scripts=[], contents=[])
    walk_script_tree(before, id1, ga["ds"], ga["de"], g1)
    walk_script_tree(after, id2, gb["ds"], gb["de"], g2)
    names1 = [x[0] for x in g1["scripts"]]
    names2 = [x[0] for x in g2["scripts"]]
    mine = [INIT_SCRIPT] + [WAVE_SCRIPT % l for (l, _w, _d) in WAVES] + \
           [REARM_SCRIPT % l for (l, _w, _d) in WAVES]
    assert names2 == names1 + mine, "GLA script roster mismatch"
    assert not set(mine) & {x[0] for x in sink1["scripts"]}, "wave script name collision"
    assert len(sink2["scripts"]) == len(sink1["scripts"]) + len(mine)
    # our scripts' flags: init one-shot, waves repeating, rearms subroutine (runScript needs it)
    flags = {nm: fl for (nm, fl, _a, _b) in g2["scripts"]}
    assert flags[INIT_SCRIPT][:2] == b"\x01\x01" and flags[INIT_SCRIPT][5] == 0
    for (lane, _w, _d) in WAVES:
        assert flags[WAVE_SCRIPT % lane][:2] == b"\x01\x00" and flags[WAVE_SCRIPT % lane][5] == 0
        assert flags[REARM_SCRIPT % lane][:2] == b"\x01\x00" and flags[REARM_SCRIPT % lane][5] == 1
    assert ondestroyed == [REARM_SCRIPT % l for (l, _w, _d) in WAVES]
    # semantic checks on the NEW condition/action contents (tail of the GLA list walk)
    new_contents = g2["contents"][len(g1["contents"]):]
    waypoint_names = set()
    ol2 = [t for t in top2 if t["nm"] == "ObjectsList"][0]
    for o in parse_objects(after, ol2):
        wp = o["dictmap"].get(131)
        if wp: waypoint_names.add(s(wp))
    old_counters = {p[3] for (_n, _e, _k, parms) in sink1["contents"]
                    for p in parms if p[0] == P_COUNTER}
    n_create = n_hunt = 0
    for (nm, enum, keyname, parms) in new_contents:
        if keyname == "CREATE_REINFORCEMENT_TEAM":
            n_create += 1
            assert enum == ACT_CREATE_REINFORCEMENT_TEAM
            assert parms[0][0] == P_TEAM and parms[0][3] in team_names
            assert parms[1][0] == P_WAYPOINT and parms[1][3] in waypoint_names, \
                "spawn waypoint %r not on map" % parms[1][3]
        elif keyname == "TEAM_HUNT":
            n_hunt += 1
            assert enum == ACT_TEAM_HUNT and parms[0][3] in team_names
        elif keyname == "SET_MILLISECOND_TIMER":
            assert enum == ACT_SET_MSEC_TIMER and parms[0][0] == P_COUNTER
            assert parms[0][3].startswith("SW_EW_") and parms[0][3] not in old_counters
            assert parms[1][0] == P_REAL and parms[1][2] > 0
        elif keyname == "TIMER_EXPIRED":
            assert enum == COND_TIMER_EXPIRED and parms[0][3].startswith("SW_EW_")
        else:
            assert keyname == "CONDITION_TRUE" and enum == COND_TRUE and not parms
    assert n_create == len(WAVES) and n_hunt == len(WAVES)
    print("VERIFY waves: symbol +1 (%s); teams %d->%d (3 lanes x %d units, thresh %.2f, "
          "onDestroyed hooks wired); scripts %d->%d (+init/3 wave/3 rearm-sub); all other "
          "chunks + ScriptLists byte-identical; every chunk in both script trees re-parses "
          "to exact boundaries; spawn waypoints + team refs + fresh SW_EW_ counters verified"
          % (NEW_TEAM_KEY, len(teams1), len(teams2), sum(c for _t, c in WAVE_UNITS),
             DESTROY_THRESH, len(names1), len(names2)))

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

    # ================= (4) ETERNAL WAVES: teams + scripts into SidesList ==========
    out2, wave_sym_id = add_eternal_waves(out)
    print("(4) eternal waves spliced: +%d teams, +%d scripts, +1 symbol (%s=id %d); "
          "buffer %d -> %d" % (len(WAVES), 1 + 2 * len(WAVES), NEW_TEAM_KEY,
                               wave_sym_id, len(out), len(out2)))
    verify_eternal_waves(out, out2, roster)
    out = out2

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
    print("=== ETERNAL WAVES (%d lanes, %d units each, owner=%s) ===" %
          (len(WAVES), sum(c for _t, c in WAVE_UNITS), GLA_SIDE))
    for (lane, wp, delay) in WAVES:
        print("   lane %s: first wave t=%2.0fs @ %-22r team=%s rearm=%.0fs after %.0f%% destroyed"
              % (lane, delay, wp, WAVE_TEAM % lane, REARM_SECONDS, DESTROY_THRESH * 100))
    print("   mix: %s" % ", ".join("%dx %s" % (c, t) for (t, c) in WAVE_UNITS))

if __name__ == "__main__":
    main()
