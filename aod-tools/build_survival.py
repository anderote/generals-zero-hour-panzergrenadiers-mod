#!/usr/bin/env python3
"""Phase 3: build 'A River Divided SURVIVAL' -- an AOD-style 30-wave survival
variant of 'A River Divided (2x6) V5'.

Design (per PLAYBOOK.md):
  * Ownership: TTK pattern -- new map-defined side 'WaveMaster' (FactionGLA,
    side idx 14 == new ScriptList idx 14); AODW_Init makes it ENEMIES with
    every lobby slot player0..7 both directions.  No lobby AI needed.
  * Engine: Noobzillas clear-gated ladder (counter 'AODW_Cleared' fed by a
    per-team generic hook 'AODW_CountKill': TEAM_DESTROYED '<This Team>' ->
    INCREMENT_COUNTER) + shellmap-proven failsafe (shared 'AODW_FS' 300 s
    timer, gated by 'AODW_Spawned' == N so exactly the next wave arms).
  * Waves spawn at the 6 southern AI start waypoints (Player_3..8_Start),
    rotating lanes; teams hunt (teamOnCreateScript/EnemySighted/AllClear ->
    TEAM_HUNT '<This Team>'), so they cross the river and hit the two human
    bases wherever they are.
  * Escalation: 30 waves, infantry -> vehicles -> armor+air -> mixed elite;
    teamVeterancy ramps 0 -> 3; every 10th wave is a boss wave (+hard-only
    escort lanes via the e/n/h script-flag difficulty selector).
  * Bounty: wave-cleared grants (PLAYER_GIVE_MONEY to all 8 slots, scaling)
    + e/n/h starting-cash scripts (SWARM idiom).
  * Anti-lag: teamMaxInstances=1 everywhere; Pasha cleanup idiom -- wave N's
    spawn TEAM_DELETEs every team of wave N-2 (x2 calls per team).
  * Announcements: SHOW_MILITARY_CAPTION incoming/cleared +
    DISPLAY_COUNTDOWN_TIMER / HIDE_COUNTDOWN_TIMER on each inter-wave clock.
  * Victory: 'AODW_Cleared' >= total counted teams -> VICTORY.  Defeat is the
    normal skirmish loss.

Every action/condition encoding (enum int + parameter type sequence) is taken
from a SIGNATURE LIBRARY harvested from the decoded AOD maps -- nothing is
guessed.  Fail-closed everywhere; full re-parse verification at the end.
"""
import os, sys, struct, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mapscript
from mapscript import (rd_ascii, read_dict, P_INT, P_REAL, P_TEAM, P_COUNTER,
                       P_WAYPOINT, P_TEXT_STRING, P_SIDE)
import vet

SRC = os.path.join(HERE, "harvest", "river_divided_v5.map")
OUT_DIR = os.path.join(HERE, "staged", "A River Divided SURVIVAL")
OUT_MAP = os.path.join(OUT_DIR, "A River Divided SURVIVAL.map")

SIDE_NAME = "WaveMaster"
ZONES = ["Player_%d_Start" % i for i in range(3, 9)]     # the 6 AI start zones
GRACE_S, GAP_S, FAILSAFE_S = 90.0, 30.0, 300.0
BOUNTY_BASE, BOUNTY_STEP = 1000, 200
MONEY = {"E": 30000, "N": 20000, "H": 10000}
CMP_GE = 3            # Parameter comparison GREATER_EQUAL (Scripts.h)
REL_ENEMY = 0

# ------------------------------------------------------------------ wave table
def W(n, comp, vet=0, boss=None, escort=None):
    return dict(n=n, comp=comp, vet=vet, boss=boss, escort=escort)
WAVES = [
 W(1,  [("GLAInfantryRebel", 6)]),
 W(2,  [("GLAInfantryRebel", 5), ("GLAInfantryTunnelDefender", 2)]),
 W(3,  [("GLAInfantryRebel", 4), ("GLAInfantryTunnelDefender", 3), ("GLAInfantryTerrorist", 1)]),
 W(4,  [("GLAVehicleTechnical", 3), ("GLAInfantryRebel", 2)]),
 W(5,  [("GLAVehicleRocketBuggy", 3), ("GLAInfantryTunnelDefender", 2)]),
 W(6,  [("GLATankScorpion", 2), ("GLAVehicleQuadCannon", 2)]),
 W(7,  [("AmericaVehicleHumvee", 3), ("AmericaInfantryRanger", 3)]),
 W(8,  [("ChinaTankBattleMaster", 3), ("ChinaInfantryTankHunter", 2)]),
 W(9,  [("GLATankMarauder", 2), ("GLAVehicleCombatBike", 2), ("GLAVehicleBattleBus", 1)]),
 W(10, [("ChinaTankGattling", 3)], vet=1,
   boss=([("ChinaTankOverlord", 2)], 1), escort=(2, [("ChinaTankGattling", 2)], 1)),
 W(11, [("AmericaTankCrusader", 3), ("AmericaInfantryMissileDefender", 2)]),
 W(12, [("ChinaJetMIG", 2)]),
 W(13, [("ChinaTankDragon", 3), ("ChinaInfantryRedguard", 2)]),
 W(14, [("AmericaVehicleComanche", 2), ("AmericaVehicleHumvee", 2)]),
 W(15, [("ChinaVehicleHelix", 2), ("ChinaTankGattling", 2)], vet=1),
 W(16, [("GLATankMarauder", 3), ("GLAVehicleToxinTruck", 1)], vet=1),
 W(17, [("AmericaTankPaladin", 3), ("AmericaVehicleTomahawk", 1)], vet=1),
 W(18, [("ChinaVehicleInfernoCannon", 2), ("ChinaTankBattleMaster", 3)], vet=1),
 W(19, [("AmericaJetRaptor", 3)], vet=1),
 W(20, [("AmericaTankCrusader", 3)], vet=2,
   boss=([("AmericaTankAvenger", 2), ("AmericaJetSpectreGunship", 2)], 2),
   escort=(2, [("AmericaJetAurora", 2)], 2)),
 W(21, [("ChinaTankOverlord", 3)], vet=1),
 W(22, [("AmericaJetA10Thunderbolt", 2), ("AmericaJetRaptor", 2)], vet=2),
 W(23, [("Salv_GLATankT28", 3), ("GLATankScorpion", 2)], vet=2),
 W(24, [("GLAVehicleScudLauncher", 2), ("GLAVehicleQuadCannon", 3)], vet=2),
 W(25, [("AmericaTankPaladin", 3), ("AmericaTankAvenger", 2)], vet=2),
 W(26, [("ChinaVehicleHelix", 2), ("ChinaJetMIG", 2), ("ChinaTankDragon", 2)], vet=2),
 W(27, [("Demo_GLATankMarauder", 4), ("Slth_GLAInfantryRebel", 2)], vet=2),
 W(28, [("AmericaJetAurora", 3), ("AmericaJetSpectreGunship", 2)], vet=3),
 W(29, [("ChinaTankOverlord", 4), ("ChinaVehicleInfernoCannon", 2)], vet=3),
 W(30, [("ChinaTankOverlord", 3)], vet=3,
   boss=([("ChinaTankOverlord", 2), ("AmericaTankAvenger", 2),
          ("AmericaInfantryColonelBurton", 1), ("ChinaInfantryBlackLotus", 1),
          ("GLAInfantryJarmenKell", 1)], 3),
   escort=(3, [("AmericaJetSpectreGunship", 2)], 3)),
]
def lanes(n): return 2 if n <= 10 else 3
def lane_zones(n): return [ZONES[(n - 1 + 2*j) % 6] for j in range(lanes(n))]
def boss_zone(n): return ZONES[(n + 2) % 6]
def team_name(n, j): return "AODW_W%02d_L%d" % (n, j)
def boss_name(n): return "AODW_W%02d_BOSS" % n
def esc_name(n, j): return "AODW_W%02d_ESC%d" % (n, j)
def wave_teams(n, with_escorts=True):
    """(counted, uncounted) team names of wave n."""
    w = WAVES[n - 1]
    counted = [team_name(n, j) for j in range(lanes(n))]
    if w["boss"]: counted.append(boss_name(n))
    unc = [esc_name(n, j) for j in range(w["escort"][0])] if (w["escort"] and with_escorts) else []
    return counted, unc
def need(n):  # counted teams in waves 1..n
    return sum(len(wave_teams(k)[0]) for k in range(1, n + 1))

# ------------------------------------------------------- signature library
SIG_MAPS = ["AOD - Noobzillas Gambit v12.map", "ttk_neomaurice.map",
            "AOD SWARM by wWw (CNC LABS).map",
            "AOD Pasha Challanges You (4P) v_00 [pashacnc com].map"]
def build_signatures():
    """name -> (kind, enum, parm-type tuple) harvested from real chunks."""
    sig = {}
    for m in SIG_MAPS:
        info = mapscript.analyze(os.path.join(HERE, "harvest", m))
        for rec in info["sink"]["scripts"]:
            for kind, lst in (("Condition", rec["conds"]), ("ScriptAction", rec["actions"]),
                              ("ScriptAction", rec["false_actions"])):
                for (name, parms) in lst:
                    key = (kind, name)
                    val = tuple(p[0] for p in parms)
                    if key not in sig:
                        sig[key] = val
                    else:
                        assert sig[key] == val, "signature mismatch %s: %s vs %s" % (key, sig[key], val)
    # enum ints: rebuild from raw contents (mapscript resolves names already);
    # we need enum values too -- reparse one map keeping enums
    enums = {}
    for m in SIG_MAPS:
        info = mapscript.analyze(os.path.join(HERE, "harvest", m))
        for l in info["lists"]:
            p = None  # enums come from parse_content below
    return sig

def harvest_enums():
    """(kind, name) -> enum int, from raw chunk walk of the signature maps."""
    out = {}
    for m in SIG_MAPS:
        info = mapscript.analyze(os.path.join(HERE, "harvest", m))
        buf, id2name = info["buf"], info["id2name"]
        def walk(start, end):
            p = start
            while p < end:
                cid, ver, dsize = struct.unpack_from("<IHi", buf, p)
                nm = id2name.get(cid); ds, de = p+10, p+10+dsize
                if nm in ("ScriptGroup", "Script", "OrCondition"):
                    q = ds
                    if nm == "ScriptGroup":
                        _g, q = rd_ascii(buf, q); q += 1 + (1 if ver >= 2 else 0)
                    elif nm == "Script":
                        for _ in range(4): _s, q = rd_ascii(buf, q)
                        q += 6 + (4 if ver >= 2 else 0)
                    walk(q, de)
                elif nm in ("Condition", "ScriptAction", "ScriptActionFalse"):
                    enum, name, _parms = mapscript.parse_content(buf, id2name, nm, ver, ds, de)
                    kind = "Condition" if nm == "Condition" else "ScriptAction"
                    prev = out.get((kind, name))
                    assert prev in (None, enum), "enum clash %s" % name
                    out[(kind, name)] = enum
                p = de
        for l in info["lists"]:
            walk(l["ds"], l["de"])
    return out

# ------------------------------------------------------------- encoders
def enc_ascii(txt):
    b = txt.encode("latin-1"); return struct.pack("<H", len(b)) + b
def enc_dict(pairs):
    out = bytearray(struct.pack("<H", len(pairs)))
    for keyid, typ, v in pairs:
        out += struct.pack("<I", (keyid << 8) | typ)
        if typ == 0:   out += struct.pack("<B", 1 if v else 0)
        elif typ == 1: out += struct.pack("<i", v)
        elif typ == 2: out += struct.pack("<f", v)
        elif typ == 3: out += enc_ascii(v)
        elif typ == 4:
            b = v.encode("utf-16-le"); out += struct.pack("<H", len(b)//2) + b
        else: raise ValueError(typ)
    return bytes(out)

class Author:
    def __init__(self, name2id, sig, enums):
        self.n, self.sig, self.enums = name2id, sig, enums
    def chunk(self, nm, ver, payload):
        return struct.pack("<IHi", self.n[nm], ver, len(payload)) + payload
    def content(self, kind, name, *vals):
        types = self.sig[(kind, name)]
        assert len(types) == len(vals), "%s arity %d != %d" % (name, len(types), len(vals))
        enum = self.enums[(kind, name)]
        pay = struct.pack("<i", enum) + struct.pack("<I", (self.n[name] << 8) | 3) + \
              struct.pack("<i", len(vals))
        for t, v in zip(types, vals):
            pay += struct.pack("<i", t)
            if t == P_INT:    pay += struct.pack("<i", v) + struct.pack("<f", 0.0) + enc_ascii("")
            elif t == P_REAL: pay += struct.pack("<i", 0) + struct.pack("<f", v) + enc_ascii("")
            elif t == 6:      pay += struct.pack("<i", v) + struct.pack("<f", 0.0) + enc_ascii("")   # COMPARISON
            elif t == 19:     pay += struct.pack("<i", v) + struct.pack("<f", 0.0) + enc_ascii("")   # RELATION
            else:             pay += struct.pack("<i", 0) + struct.pack("<f", 0.0) + enc_ascii(v)    # string-ish
        return self.chunk("Condition" if kind == "Condition" else "ScriptAction",
                          4 if kind == "Condition" else 2, pay)
    def IF(self, name, *vals):  return self.content("Condition", name, *vals)
    def DO(self, name, *vals):  return self.content("ScriptAction", name, *vals)
    def script(self, name, conds, actions, active=1, oneshot=1, sub=0,
               easy=1, normal=1, hard=1):
        orc = self.chunk("OrCondition", 1, b"".join(c for c in conds if isinstance(c, bytes)))
        # conds may be a list of OrCondition byte strings already wrapped:
        body = orc if not (conds and conds[0][:1] == b"OR") else b""
        pay = (enc_ascii(name) + enc_ascii("") * 3 +
               bytes([active, oneshot, easy, normal, hard, sub]) + struct.pack("<i", 0) +
               orc + b"".join(actions))
        return self.chunk("Script", 2, pay)
    def script_or(self, name, orconds, actions, **kw):
        """orconds: list of lists of Condition bytes (each list = one OrCondition)."""
        active = kw.get("active", 1); oneshot = kw.get("oneshot", 1); sub = kw.get("sub", 0)
        e, nrm, h = kw.get("easy", 1), kw.get("normal", 1), kw.get("hard", 1)
        ors = b"".join(self.chunk("OrCondition", 1, b"".join(c)) for c in orconds)
        pay = (enc_ascii(name) + enc_ascii("") * 3 +
               bytes([active, oneshot, e, nrm, h, sub]) + struct.pack("<i", 0) +
               ors + b"".join(actions))
        return self.chunk("Script", 2, pay)

# ------------------------------------------------------------- team dicts
TEAM_KEYS = ["teamName", "teamOwner", "teamIsSingleton", "teamMaxInstances",
             "teamAggressiveness", "teamVeterancy", "teamOnCreateScript",
             "teamEnemySightedScript", "teamAllClearScript",
             "teamGenericScriptHook0", "teamDestroyedThreshold"] + \
            ["teamUnitType%d" % i for i in range(1, 8)] + \
            ["teamUnitMaxCount%d" % i for i in range(1, 8)] + \
            ["teamUnitMinCount%d" % i for i in range(1, 8)]

def build_team(n2, name, comp, vet, counted):
    pairs = [(n2["teamName"], 3, name), (n2["teamOwner"], 3, SIDE_NAME),
             (n2["teamIsSingleton"], 0, 0), (n2["teamMaxInstances"], 1, 1),
             (n2["teamAggressiveness"], 1, 2)]
    if vet: pairs.append((n2["teamVeterancy"], 1, vet))
    for i, (tmpl, cnt) in enumerate(comp):
        pairs += [(n2["teamUnitType%d" % (i+1)], 3, tmpl),
                  (n2["teamUnitMaxCount%d" % (i+1)], 1, cnt),
                  (n2["teamUnitMinCount%d" % (i+1)], 1, cnt)]
    pairs += [(n2["teamOnCreateScript"], 3, "AODW_Hunt"),
              (n2["teamEnemySightedScript"], 3, "AODW_Hunt"),
              (n2["teamAllClearScript"], 3, "AODW_Hunt")]
    if counted:
        pairs.append((n2["teamGenericScriptHook0"], 3, "AODW_CountKill"))
    return enc_dict(pairs)

# --------------------------------------------------------------------- main
def main():
    roster = vet.effective_roster()
    sig = build_signatures()
    enums = harvest_enums()
    info = mapscript.analyze(SRC)
    buf, id2name, name2id = info["buf"], info["id2name"], info["name2id"]
    sl, psl, lists = info["sl"], info["psl"], info["lists"]
    assert len(info["sides"]) == len(lists) == 14

    # ---- template vet (fail closed) ----
    used_templates = set()
    for w in WAVES:
        for (t, _c) in w["comp"]: used_templates.add(t)
        if w["boss"]:
            for (t, _c) in w["boss"][0]: used_templates.add(t)
        if w["escort"]:
            for (t, _c) in w["escort"][1]: used_templates.add(t)
    missing = sorted(t for t in used_templates if t not in roster)
    assert not missing, "wave templates missing from effective space: %s" % missing
    for z in ZONES:
        assert z in info["waypoints"], "zone waypoint missing: " + z

    # ---- symbols: append every missing name ----
    needed_syms = set()
    for (kind, name) in list(sig.keys()):
        pass
    used_contents = set()
    ACTIONS = ["CREATE_REINFORCEMENT_TEAM", "TEAM_HUNT", "TEAM_DELETE",
               "SET_MILLISECOND_TIMER", "INCREMENT_COUNTER", "SHOW_MILITARY_CAPTION",
               "DISPLAY_COUNTDOWN_TIMER", "HIDE_COUNTDOWN_TIMER", "PLAYER_GIVE_MONEY",
               "PLAYER_RELATES_PLAYER", "VICTORY"]
    CONDS = ["CONDITION_TRUE", "TIMER_EXPIRED", "COUNTER", "TEAM_DESTROYED"]
    for a in ACTIONS:
        assert ("ScriptAction", a) in sig and ("ScriptAction", a) in enums, "no signature for " + a
        needed_syms.add(a)
    for c in CONDS:
        assert ("Condition", c) in sig and ("Condition", c) in enums, "no signature for " + c
        needed_syms.add(c)
    needed_syms.update(TEAM_KEYS)
    needed_syms.update(["Script", "ScriptAction", "Condition", "OrCondition",
                        "ScriptList", "PlayerScriptsList"])
    new_syms = sorted(s for s in needed_syms if s not in name2id)
    n2 = dict(name2id)
    next_id = max(id2name) + 1
    sym_entries = b""
    for s_ in new_syms:
        n2[s_] = next_id
        sym_entries += bytes([len(s_)]) + s_.encode("latin-1") + struct.pack("<I", next_id)
        next_id += 1

    A = Author(n2, sig, enums)

    # ---- new side dict: clone SkirmishGLA side pairs, patch identity ----
    # find raw pairs of SkirmishGLA side (index 4)
    p = sl["ds"]
    (nsides,) = struct.unpack_from("<i", buf, p); p += 4
    side_pairs = None
    sides_end = None
    for i in range(nsides):
        pairs, p = read_dict(buf, p)
        (nb,) = struct.unpack_from("<i", buf, p); p += 4
        assert nb == 0
        d = {id2name.get(k): (k, t, v) for (k, t, v) in pairs}
        if d.get("playerName", (0, 0, ""))[2] == "SkirmishGLA":
            side_pairs = pairs
    sides_end = p
    assert side_pairs is not None
    new_side = []
    for (k, t, v) in side_pairs:
        nm = id2name.get(k)
        if nm == "playerName": v = SIDE_NAME
        elif nm == "playerDisplayName": v = SIDE_NAME
        # CRITICAL: FactionCivilian, not FactionGLA.  SidesList::
        # prepareForMP_or_Skirmish (engine) DELETES every non-civilian map side
        # at skirmish start (wave scripts would never run) and any non-civilian
        # side with scripts suppresses SkirmishScripts.scb loading entirely
        # (all lobby AI would idle).  Civilian-faction sides are kept as real
        # players WITH their embedded ScriptLists, and are skipped by the scb
        # shadow scan.  (TTK's 'Civ_Evil' uses the same trick.)
        elif nm == "playerFaction": v = "FactionCivilian"
        elif nm == "playerAllies": v = ""
        elif nm == "playerEnemies": v = ""
        new_side.append((k, t, v))
    side_bytes = enc_dict(new_side) + struct.pack("<i", 0)   # 0 buildlists

    # ---- teams ----
    team_bytes = b""
    team_names = ["teamWaveMaster"]
    team_bytes += enc_dict([(n2["teamName"], 3, "teamWaveMaster"),
                            (n2["teamOwner"], 3, SIDE_NAME),
                            (n2["teamIsSingleton"], 0, 1)])
    n_team_dicts = 1
    for w in WAVES:
        n = w["n"]
        for j in range(lanes(n)):
            team_bytes += build_team(n2, team_name(n, j), w["comp"], w["vet"], True)
            team_names.append(team_name(n, j)); n_team_dicts += 1
        if w["boss"]:
            comp, bvet = w["boss"]
            team_bytes += build_team(n2, boss_name(n), comp, bvet, True)
            team_names.append(boss_name(n)); n_team_dicts += 1
        if w["escort"]:
            cnt, comp, evet = w["escort"]
            for j in range(cnt):
                team_bytes += build_team(n2, esc_name(n, j), comp, evet, False)
                team_names.append(esc_name(n, j)); n_team_dicts += 1

    # ---- scripts ----
    scripts = []
    # subroutines
    scripts.append(A.script("AODW_Hunt", [A.IF("CONDITION_TRUE")],
                            [A.DO("TEAM_HUNT", "<This Team>")], oneshot=1, sub=1))
    scripts.append(A.script("AODW_CountKill", [A.IF("TEAM_DESTROYED", "<This Team>")],
                            [A.DO("INCREMENT_COUNTER", 1, "AODW_Cleared")], oneshot=1, sub=1))
    # init: relations + grace timer + welcome
    init_actions = []
    for pn in range(8):
        init_actions.append(A.DO("PLAYER_RELATES_PLAYER", SIDE_NAME, "player%d" % pn, REL_ENEMY))
        init_actions.append(A.DO("PLAYER_RELATES_PLAYER", "player%d" % pn, SIDE_NAME, REL_ENEMY))
    init_actions += [
        A.DO("SHOW_MILITARY_CAPTION",
             "SURVIVAL: 30 waves spawn from the 6 southern start zones. Defend the north bank! No enemy AI players needed.", 12000),
        A.DO("SET_MILLISECOND_TIMER", "AODW_T1", GRACE_S),
        A.DO("DISPLAY_COUNTDOWN_TIMER", "AODW_T1", "SCRIPT:CHI02xReinforcementTimer"),
    ]
    scripts.append(A.script("AODW_Init", [A.IF("CONDITION_TRUE")], init_actions))
    # difficulty starting cash
    for tag, flags in (("E", dict(easy=1, normal=0, hard=0)),
                       ("N", dict(easy=0, normal=1, hard=0)),
                       ("H", dict(easy=0, normal=0, hard=1))):
        acts = [A.DO("PLAYER_GIVE_MONEY", "player%d" % pn, MONEY[tag]) for pn in range(8)]
        scripts.append(A.script("AODW_Money_%s" % tag, [A.IF("CONDITION_TRUE")], acts, **flags))
    # waves
    for w in WAVES:
        n = w["n"]
        # arm script for wave n (n>=2): cleared-gate OR (failsafe AND spawned==n-1)
        if n >= 2:
            bounty = BOUNTY_BASE + BOUNTY_STEP * (n - 1)
            arm_actions = [
                A.DO("SHOW_MILITARY_CAPTION",
                     "Wave %d cleared! Bounty $%d. Wave %d in %d seconds." %
                     (n - 1, bounty, n, int(GAP_S)), 8000),
            ] + [A.DO("PLAYER_GIVE_MONEY", "player%d" % pn, bounty) for pn in range(8)] + [
                A.DO("SET_MILLISECOND_TIMER", "AODW_T%d" % n, GAP_S),
                A.DO("DISPLAY_COUNTDOWN_TIMER", "AODW_T%d" % n, "SCRIPT:CHI02xReinforcementTimer"),
            ]
            scripts.append(A.script_or("AODW_Arm_%02d" % n,
                [[A.IF("COUNTER", "AODW_Cleared", CMP_GE, need(n - 1))],
                 [A.IF("TIMER_EXPIRED", "AODW_FS"),
                  A.IF("COUNTER", "AODW_Spawned", CMP_GE, n - 1),
                  A.IF("COUNTER", "AODW_Cleared", CMP_GE, 0)]],
                arm_actions))
        # spawn script
        sp = [A.DO("HIDE_COUNTDOWN_TIMER", "AODW_T%d" % n)]
        label = "BOSS WAVE %d" % n if w["boss"] else "Wave %d" % n
        sp.append(A.DO("SHOW_MILITARY_CAPTION", "%s incoming!" % label, 8000))
        for j, z in enumerate(lane_zones(n)):
            sp.append(A.DO("CREATE_REINFORCEMENT_TEAM", team_name(n, j), z))
        if w["boss"]:
            sp.append(A.DO("CREATE_REINFORCEMENT_TEAM", boss_name(n), boss_zone(n)))
        sp.append(A.DO("INCREMENT_COUNTER", 1, "AODW_Spawned"))
        sp.append(A.DO("SET_MILLISECOND_TIMER", "AODW_FS", FAILSAFE_S))
        if n >= 3:
            old_counted, old_unc = wave_teams(n - 2)
            for t in old_counted + old_unc:
                sp += [A.DO("TEAM_DELETE", t), A.DO("TEAM_DELETE", t)]
        scripts.append(A.script("AODW_Spawn_%02d" % n,
                                [A.IF("TIMER_EXPIRED", "AODW_T%d" % n)], sp))
        # hard-only escorts on boss waves
        if w["escort"]:
            cnt, _comp, _v = w["escort"]
            acts = [A.DO("CREATE_REINFORCEMENT_TEAM", esc_name(n, j), ZONES[(n + 3 + j) % 6])
                    for j in range(cnt)]
            scripts.append(A.script("AODW_HardEscort_%02d" % n,
                                    [A.IF("TIMER_EXPIRED", "AODW_T%d" % n)], acts,
                                    easy=0, normal=0, hard=1))
    # victory
    scripts.append(A.script("AODW_Victory",
        [A.IF("COUNTER", "AODW_Cleared", CMP_GE, need(30))],
        [A.DO("SHOW_MILITARY_CAPTION", "ALL 30 WAVES DEFEATED - VICTORY!", 15000),
         A.DO("VICTORY")]))

    new_list_data = b"".join(scripts)
    new_list = struct.pack("<IHi", n2["ScriptList"], 1, len(new_list_data)) + new_list_data

    # ---- splice ----
    (nteams_,) = struct.unpack_from("<i", buf, info["teams_cnt_off"])
    teams_start = info["teams_cnt_off"] + 4
    new_psl_data = bytes(buf[psl["ds"]:psl["de"]]) + new_list
    new_sl_data = (
        struct.pack("<i", nsides + 1) + bytes(buf[sl["ds"] + 4:sides_end]) + side_bytes +
        struct.pack("<i", nteams_ + n_team_dicts) + bytes(buf[teams_start:psl["hp"]]) + team_bytes +
        struct.pack("<IHi", n2["PlayerScriptsList"], psl["ver"], len(new_psl_data)) + new_psl_data)
    (sym_count,) = struct.unpack_from("<i", buf, 4)
    out = (bytes(buf[:4]) + struct.pack("<i", sym_count + len(new_syms)) +
           bytes(buf[8:info["data_start"]]) + sym_entries +
           bytes(buf[info["data_start"]:sl["hp"]]) +
           struct.pack("<IHi", name2id["SidesList"], sl["ver"], len(new_sl_data)) +
           new_sl_data + bytes(buf[sl["de"]:]))

    # ================= VERIFY (fail-closed) =================
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_MAP, "wb") as fh:
        fh.write(out)
    info2 = mapscript.analyze(OUT_MAP)   # full re-parse: every chunk walked
    assert len(info2["sides"]) == 15 and len(info2["lists"]) == 15
    assert info2["sides"][14].get("playerName") == SIDE_NAME
    # symbols: originals identical, appended block correct
    assert all(info2["id2name"][k] == v for k, v in id2name.items())
    assert len(info2["id2name"]) == len(id2name) + len(new_syms)
    # untouched top-level chunks byte-identical
    for a, b in zip(info["top"], info2["top"]):
        assert a["nm"] == b["nm"]
        if a["nm"] != "SidesList":
            assert bytes(info["buf"][a["ds"]:a["de"]]) == bytes(info2["buf"][b["ds"]:b["de"]]), a["nm"]
    # original sides/teams/scriptlists preserved
    assert info2["sides"][:14] == info["sides"]
    t2 = info2["teams"]
    assert len(t2) == len(info["teams"]) + n_team_dicts
    for (a0, a1, da), (b0, b1, db) in zip(info["teams"], t2):
        assert da == db, "original team changed"
    for i in range(14):
        a, b = lists[i], info2["lists"][i]
        assert bytes(info["buf"][a["ds"]:a["de"]]) == bytes(info2["buf"][b["ds"]:b["de"]]), i
    # new teams: names, owner, composition resolves, hooks
    new_team_dicts = {d.get("teamName"): d for (_x, _y, d) in t2[len(info["teams"]):]}
    assert set(new_team_dicts) == set(team_names)
    n_counted = 0
    for nm_, d in new_team_dicts.items():
        if nm_ == "teamWaveMaster": continue
        assert d["teamOwner"] == SIDE_NAME and d["teamMaxInstances"] == 1
        for i in range(1, 8):
            t = d.get("teamUnitType%d" % i)
            if t: assert t in roster, "unresolved %s in %s" % (t, nm_)
        assert d["teamOnCreateScript"] == "AODW_Hunt"
        if d.get("teamGenericScriptHook0") == "AODW_CountKill": n_counted += 1
    assert n_counted == need(30), "counted teams %d != need(30) %d" % (n_counted, need(30))
    # new scripts: names/refs/structure
    g2 = dict(scripts=[], contents=[])
    nl = info2["lists"][14]
    mapscript.walk_tree(info2["buf"], info2["id2name"], nl["ds"], nl["de"], g2)
    names = [r["name"] for r in g2["scripts"]]
    assert len(names) == len(set(names)) == len(scripts)
    wp2 = set(info2["waypoints"])
    for rec in g2["scripts"]:
        for (nm_, parms) in rec["actions"]:
            if nm_ == "CREATE_REINFORCEMENT_TEAM":
                assert parms[0][3] in new_team_dicts, parms[0][3]
                assert parms[1][3] in wp2, parms[1][3]
            if nm_ == "TEAM_DELETE":
                assert parms[0][3] in new_team_dicts
    subs = {r["name"]: r["flags"] for r in g2["scripts"]}
    assert subs["AODW_Hunt"][5] == 1 and subs["AODW_CountKill"][5] == 1
    assert subs["AODW_Money_E"][2:5] == b"\x01\x00\x00"
    assert subs["AODW_Money_H"][2:5] == b"\x00\x00\x01"
    for w in WAVES:
        if w["escort"]:
            assert subs["AODW_HardEscort_%02d" % w["n"]][2:5] == b"\x00\x00\x01"
    # counter freshness vs original map
    old_counters = {p_[3] for (_k, _n, parms) in info["sink"]["contents"]
                    for p_ in parms if p_[0] == P_COUNTER}
    assert not any(c.startswith("AODW_") for c in old_counters)
    md5 = hashlib.md5(out).hexdigest()
    print("VERIFY OK: 15 sides/lists; +%d symbols; +%d teams (%d counted = need(30)); "
          "+%d scripts; all original regions byte-identical; every wave template resolves "
          "(%d templates); zones OK" %
          (len(new_syms), n_team_dicts, n_counted, len(scripts), len(used_templates)))
    print("OUT: %s (%d bytes) md5=%s" % (OUT_MAP, len(out), md5))
    # readable dump for eyeballing
    with open(os.path.join(HERE, "dumps", "SURVIVAL_out.txt"), "w") as fh:
        mapscript.dump(OUT_MAP, out=fh)
    return md5

if __name__ == "__main__":
    main()
