#!/usr/bin/env python3
"""Build zzz-ZZZZZZZWEconomy.big - ECONOMY + UAV layer for the Panzergrenadiers
stack (ShockWave under GeneralsX).  Four features, shipped as pure top-layer
file overrides (no lower layer is rebuilt):

FEATURE 1 - ALL CHINA INFANTRY: 50% BuildCost + 50% BuildTime (2x speed).
  Scope = every BUILD-QUEUEABLE infantry object across ALL five China
  generals (vanilla / Tank / Infantry / Nuke / SpecialWeapons): 32 objects in
  32 files, enumerated mechanically (China-side Object with KindOf INFANTRY +
  BuildCost + a UNIT_BUILD CommandButton carried by some CommandSet) and
  re-enumerated post-install as a completeness guard.
  BuildVariations cost semantics (engine-verified, GeneralsX GeneralsMD tree):
  ProductionUpdate::queueCreateUnit withdraws the QUEUED template's cost
  (ProductionUpdate.cpp:424 'money->withdraw(unitType->calcCostToBuild)') and
  the BuildVariations redirect happens later, at ThingFactory::newObject
  (ThingFactory.cpp:315) - so the STUB's BuildCost/BuildTime is what is
  charged and no variation is ever charged.  Both the stubs AND the donor
  objects are therefore halved (each build path charges exactly one object's
  cost - no double-halving is possible).  The Sharpshooter is a plain
  single-object Pathfinder clone since kwai-infantry v2 (its v1 ZHE
  BuildVariations were removed with the port) - one BuildCost line, halved.
  Non-buildable infantry (CINE_*, SecretPolice, Agent, Officer, Squad_*
  members - spawned free by SpawnBehavior InitialBurst, MortarPit soldier)
  are deliberately untouched.
  Rounding: halves that land on .5 are rounded DOWN to the nearest $5
  (player-favourable): Spec Redguard 325 -> 160, Tank TankHunter 375 -> 185.

FEATURE 2 - KWAI SCOUT CAR (Tank_ChinaVehicleScoutCar, the kwai-roster clone,
  effective owner zzz-ZZZZZZZVehicleKit.big which added its infantry bay):
  VisionRange 450 -> 900, ShroudClearingRange 500 -> 1000.

FEATURE 3 - UAV FOR EVERYONE, NO REQUIREMENTS.  The kwai-uav feature is
  reworked via overrides:
  (a) research gate REMOVED: the deploy button loses NEED_UPGRADE + its
      Upgrade ref (client gate); the Internet Center's StartsPaused
      OCLSpecialPower + UnpauseSpecialPowerUpgrade modules are removed (logic
      gate); the now-useless research button (CommandButton
      Tank_Command_UpgradeKwaiUAVProgram) is deleted outright.  The Upgrade
      block itself (Tank_Upgrade_KwaiUAVProgram, Upgrade.ini) stays defined
      but unreachable - shipping Upgrade.ini just to delete an orphan was not
      worth the extra shared-file surface (documented).
  (b) the ungated deploy button goes on EVERY faction's COMMAND CENTER
      (15 command centers: USA x5, China x5, GLA x5), each CC object gains
      the OCLSpecialPower module (no StartsPaused -> ready as soon as a CC
      exists; SpecialPowerModule.cpp:66 m_startsPaused=FALSE default;
      SharedSyncedTimer keyed by TEMPLATE id, Player.cpp:3319
      newTimer.m_templateID = temp->getID(), so USA's own SpecialPowerSpyDrone
      - same SPECIAL_SPY_DRONE enum - never shares our clock; player-click
      firing resolves modules BY TEMPLATE, Object.cpp:5442
      getSpecialPowerModule/isModuleForPower, so two same-enum modules on the
      USA CCs cannot cross-fire).
      Slots (occupancy-checked): USA x5 -> slot 12 (free in all five);
      GLA x6 sets (5 generals + Demo's suicide-upgrade variant) -> slot 11
      (free in all six); Leang -> slot 10 (free, keeps her taunt menu);
      vanilla China / Kwai / Fai / Tao (sets FULL 14/14) -> slot 12,
      SACRIFICING the China taunt-menu button (Command_ChinaTauntMenu, a
      voice-line gimmick; the taunt CommandSetUpgrade machinery + taunt sets
      stay intact and Leang still uses the button - documented).
      KWAI: deploy MOVED from the Internet Center to his CC for consistency;
      IC clone slots 7-8 restored to garrison exit cameos (the pre-kwai-uav
      state).  The drone stays Kwai-branded (Tank_ChinaSurveillanceUAV) -
      every faction deploys the same Global Hawk clone (pre-approved).

FEATURE 4 - PRODUCTION QUEUE BUMP: MaxQueueEntries = 30 on Kwai's Barracks,
  War Factory and Airfield (engine default is 9, ProductionUpdate.cpp:104;
  none of the three set it explicitly - verified).

PACKAGING: zzz-ZZZZZZZWEconomy.big - case-insensitively sorts AFTER
zzz-ZZZZZZZVetInsignia.big ('w' > 'v' at char 12), BEFORE
zzz_ControlBarPro*.big ('-' 0x2D < '_' 0x5F); verified against the real
directory listings of both mod dirs + 'no later archive claims any shipped
path'.  Installed to both mod dirs.  This becomes the LAST INI layer.
"""

import os
import re
import sys
import difflib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzz-ZZZZZZZWEconomy.big"
TAG = "zzz-ZZZZZZZWEconomy"
# CHANGELOG (kwai-infantry v2 chain rebuild): kwai-infantry removed its ZHE
# Sharpshooter port (now a Pathfinder clone; still 1200/30 -> halved here to
# 600/15).  Upgrade.ini reverted to zzz-ZZZZZZZKwaiPDL.big, SpecialPower.ini
# to zzz-ZZZZZZKwaiUAV.big.  Sources are read only from archives sorting
# strictly below this one (fx-enhance sorts above and is owned elsewhere).
# CHANGELOG (rotr-infantry merge): zzz-ZZZZZZZRotrInfantry.big landed below
# us with two new buildable Kwai infantry (ROTR Shmel Trooper $350/8s +
# Shock Trooper $800/10s at Barracks slots 9/10).  Per the rotr-infantry
# README they ship donor-verbatim / coordinator-set prices (the Shock
# Trooper was already repriced $450->$800 for its tesla rework) and are
# deliberately NOT covered by the China-infantry 50/50 convention - they
# are excluded from the buildable-infantry completeness enumeration below.
ROTR_UNITS = {"Tank_ChinaInfantryShmelTrooper",
              "Tank_ChinaInfantryShockTrooper"}

CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
OBJ = "Data\\INI\\Object\\"
IC_PATH = OBJ + "China\\Tank\\Buildings\\InternetCenter.ini"
SC_PATH = OBJ + "China\\Tank\\Vehicles\\ScoutCar.ini"
BAR_PATH = OBJ + "China\\Tank\\Buildings\\Barracks.ini"
WF_PATH = OBJ + "China\\Tank\\Buildings\\WarFactory.ini"
AIR_PATH = OBJ + "China\\Tank\\Buildings\\Airfield.ini"

DEPLOY = "Tank_Command_KwaiUAVDeploy"
RESEARCH = "Tank_Command_UpgradeKwaiUAVProgram"
POWER = "Tank_SpecialPowerKwaiUAV"
UAV_OCL = "Tank_SUPERWEAPON_KwaiUAV"
DRONE = "Tank_ChinaSurveillanceUAV"
MODTAG = "ModuleTag_WEco_UAV01"

# ---- the 15 command centers: (file, object, commandset names to patch, mode)
#   mode: ("insert", slot) or ("replace_taunt", 12)
CC_PLAN = [
    (OBJ + "USA\\Vanilla\\Buildings\\CommandCenter.ini", "AmericaCommandCenter",
     ["AmericaCommandCenterCommandSet"], ("insert", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "USA\\Airforce\\Buildings\\CommandCenter.ini", "AirF_AmericaCommandCenter",
     ["AirF_AmericaCommandCenterCommandSet"], ("insert", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "USA\\Laser\\Buildings\\CommandCenter.ini", "Lazr_AmericaCommandCenter",
     ["Lazr_AmericaCommandCenterCommandSet"], ("insert", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "USA\\SuperWeapon\\Buildings\\CommandCenter.ini", "SupW_AmericaCommandCenter",
     ["SupW_AmericaCommandCenterCommandSet"], ("insert", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "USA\\Armor\\Buildings\\CommandCenter.ini", "Armor_AmericaCommandCenter",
     ["Armor_AmericaCommandCenterCommandSet"], ("insert", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "China\\Vanilla\\Buildings\\CommandCenter.ini", "ChinaCommandCenter",
     ["ChinaCommandCenterCommandSet", "ChinaCommandCenterCommandSetUpgrade"],
     ("replace_taunt", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "China\\Tank\\Buildings\\CommandCenter.ini", "Tank_ChinaCommandCenter",
     ["Tank_ChinaCommandCenterCommandSet", "Tank_ChinaCommandCenterCommandSetUpgrade"],
     ("replace_taunt", 12), "zzz-ZZZKwaiGarrisons.big"),
    (OBJ + "China\\Infantry\\Buildings\\CommandCenter.ini", "Infa_ChinaCommandCenter",
     ["Infa_ChinaCommandCenterCommandSet", "Infa_ChinaCommandCenterCommandSetUpgrade"],
     ("replace_taunt", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "China\\Nuke\\Buildings\\CommandCenter.ini", "Nuke_ChinaCommandCenter",
     ["Nuke_ChinaCommandCenterCommandSet", "Nuke_ChinaCommandCenterCommandSetUpgrade"],
     ("replace_taunt", 12), "zz_SPE_Shw_ini.big"),
    (OBJ + "China\\SpecialWeapons\\Buildings\\CommandCenter.ini", "Spec_ChinaCommandCenter",
     ["Spec_ChinaCommandCenterCommandSet", "Spec_ChinaCommandCenterCommandSetUpgrade"],
     ("insert", 10), "zz_SPE_Shw_ini.big"),
    (OBJ + "GLA\\Vanilla\\Buildings\\CommandCenter.ini", "GLACommandCenter",
     ["GLACommandCenterCommandSet"], ("insert", 11), "zz_SPE_Shw_ini.big"),
    (OBJ + "GLA\\Toxin\\Buildings\\CommandCenter.ini", "Chem_GLACommandCenter",
     ["Chem_GLACommandCenterCommandSet"], ("insert", 11), "zz_SPE_Shw_ini.big"),
    (OBJ + "GLA\\Demo\\Buildings\\CommandCenter.ini", "Demo_GLACommandCenter",
     ["Demo_GLACommandCenterCommandSet", "Demo_GLACommandCenterCommandSetUpgrade"],
     ("insert", 11), "zz_SPE_Shw_ini.big"),
    (OBJ + "GLA\\Stealth\\Buildings\\CommandCenter.ini", "Slth_GLACommandCenter",
     ["Slth_GLACommandCenterCommandSet"], ("insert", 11), "zz_SPE_Shw_ini.big"),
    (OBJ + "GLA\\Salvage\\Buildings\\CommandCenter.ini", "Salv_GLACommandCenter",
     ["Salv_GLACommandCenterCommandSet"], ("insert", 11), "zz_SPE_Shw_ini.big"),
]

# ---- feature 1: (relpath under Object\, owner, object, cost old->new,
#                  time old->new) - one buildable object per file
INF_PLAN = [
    ("China\\Vanilla\\Infantry\\Redguard.ini", "zzz-KwaiDoctrine.big",
     "ChinaInfantryRedguard", 300, 150, 10.0, 5.0),
    ("China\\Vanilla\\Infantry\\TankHunter.ini", "zzz-KwaiDoctrine.big",
     "ChinaInfantryTankHunter", 300, 150, 5.0, 2.5),
    ("China\\Vanilla\\Infantry\\SiegeSoldier.ini", "zzz-ZZZZZZZKwaiPDL.big",
     "ChinaInfantrySiegeSoldier", 600, 300, 8.0, 4.0),
    ("China\\Vanilla\\Infantry\\Hacker.ini", "zzz-KwaiDoctrine.big",
     "ChinaInfantryHacker", 600, 300, 13.0, 6.5),
    ("China\\Vanilla\\Infantry\\BlackLotus.ini", "zzz-KwaiDoctrine.big",
     "ChinaInfantryBlackLotus", 1500, 750, 20.0, 10.0),
    ("China\\Nuke\\Infantry\\RedGuard.ini", "zz_SPE_Shw_ini.big",
     "Nuke_ChinaInfantryRedguard", 300, 150, 12.0, 6.0),
    ("China\\Nuke\\Infantry\\TankHunter.ini", "zz_SPE_Shw_ini.big",
     "Nuke_ChinaInfantryTankHunter", 350, 175, 7.0, 3.5),
    ("China\\Nuke\\Infantry\\SiegeSoldier.ini", "zz_SPE_Shw_ini.big",
     "Nuke_ChinaInfantrySiegeSoldier", 600, 300, 8.0, 4.0),
    ("China\\Nuke\\Infantry\\Hacker.ini", "zz_SPE_Shw_ini.big",
     "Nuke_ChinaInfantryHacker", 600, 300, 13.0, 6.5),
    ("China\\Nuke\\Infantry\\BlackLotus.ini", "zz_SPE_Shw_ini.big",
     "Nuke_ChinaInfantryBlackLotus", 1500, 750, 20.0, 10.0),
    ("China\\Infantry\\Infantry\\RedGuard.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryRedguard", 450, 225, 14.0, 7.0),
    ("China\\Infantry\\Infantry\\TankHunter.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryTankHunter", 350, 175, 6.0, 3.0),
    ("China\\Infantry\\Infantry\\MiniGunner.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryMiniGunner", 550, 275, 14.0, 7.0),
    ("China\\Infantry\\Infantry\\SiegeSoldier.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantrySiegeSoldier", 600, 300, 8.0, 4.0),
    ("China\\Infantry\\Infantry\\Hacker.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryHacker", 700, 350, 13.0, 6.5),
    ("China\\Infantry\\Infantry\\BlackLotus.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryBlackLotus", 1500, 750, 20.0, 10.0),
    ("China\\Infantry\\Infantry\\RedGuardSquad.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryRedGuardSquadNexus", 2000, 1000, 25.0, 12.5),
    ("China\\Infantry\\Infantry\\MinigunnerSquad.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryMinigunnerSquadNexus", 2000, 1000, 25.0, 12.5),
    ("China\\Infantry\\Infantry\\TankHunterSquad.ini", "zz_SPE_Shw_ini.big",
     "Infa_ChinaInfantryTankHunterSquadNexus", 2000, 1000, 25.0, 12.5),
    ("China\\SpecialWeapons\\Infantry\\RedGuard.ini", "zz_SPE_Shw_ini.big",
     "Spec_ChinaInfantryRedguard", 325, 160, 10.0, 5.0),
    ("China\\SpecialWeapons\\Infantry\\TankHunter.ini", "zz_SPE_Shw_ini.big",
     "Spec_ChinaInfantryTankHunter", 300, 150, 5.0, 2.5),
    ("China\\SpecialWeapons\\Infantry\\FlameThrower.ini", "zz_SPE_Shw_ini.big",
     "Spec_ChinaInfantryFlameThrower", 350, 175, 8.0, 4.0),
    ("China\\SpecialWeapons\\Infantry\\Hacker.ini", "zz_SPE_Shw_ini.big",
     "Spec_ChinaInfantryHacker", 600, 300, 13.0, 6.5),
    ("China\\SpecialWeapons\\Infantry\\BlackLotus.ini", "zz_SPE_Shw_ini.big",
     "Spec_ChinaInfantryBlackLotus", 1500, 750, 20.0, 10.0),
    ("China\\Tank\\Infantry\\RedGuard.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaInfantryRedguard", 400, 200, 12.0, 6.0),
    ("China\\Tank\\Infantry\\TankHunter.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaInfantryTankHunter", 375, 185, 10.0, 5.0),
    ("China\\Tank\\Infantry\\Hacker.ini", "zzz-KwaiDoctrine.big",
     "Tank_ChinaInfantryHacker", 300, 150, 13.0, 6.5),
    ("China\\Tank\\Infantry\\BlackLotus.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaInfantryBlackLotus", 1500, 750, 20.0, 10.0),
    ("China\\Tank\\Infantry\\SiegeSoldier.ini", "zzz-ZZZZZKwaiRoster.big",
     "Tank_ChinaInfantrySiegeSoldier", 600, 300, 8.0, 4.0),
    ("China\\Tank\\Infantry\\FlameTrooper.ini", "zzz-ZZZZZZZLKwaiInfantry.big",
     "Tank_ChinaInfantryFlameThrower", 350, 175, 8.0, 4.0),
    ("China\\Tank\\Infantry\\MiniGunner.ini", "zzz-ZZZZZZZLKwaiInfantry.big",
     "Tank_ChinaInfantryMiniGunner", 550, 275, 14.0, 7.0),
    ("China\\Tank\\Infantry\\Sharpshooter.ini", "zzz-ZZZZZZZLKwaiInfantry.big",
     "Tank_ChinaInfantrySharpshooter", 1200, 600, 30.0, 15.0),
]

OWNERS = {
    CS_PATH: "zzz-ZZZZZZZVehicleKit.big",
    CB_PATH: "zzz-ZZZZZZZTTeslaCoil.big",
    IC_PATH: "zzz-ZZZZZZKwaiUAV.big",
    SC_PATH: "zzz-ZZZZZZZVehicleKit.big",
    BAR_PATH: "zzz-ZZKwaiBaseTech.big",
    WF_PATH: "zzz-ZZZZChaosUnits.big",
    AIR_PATH: "zzz-ZZZKwaiGarrisons.big",
}
for path, _objname, _sets, _mode, owner in CC_PLAN:
    OWNERS[path] = owner
for rel, owner, *_ in INF_PLAN:
    OWNERS[OBJ + rel] = owner
assert len(OWNERS) == 54, len(OWNERS)


# ------------------------------------------------------------------ helpers
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(raw):
    return raw.replace("\r\n", "\n")


def from_lf(lf_text, eol):
    return lf_text.replace("\n", eol) if eol != "\n" else lf_text


def replace_exact(s, old, new, count=1):
    assert s.count(old) == count, \
        "expected %d occurrences of %r..., found %d" % (count, old[:90],
                                                        s.count(old))
    return s.replace(old, new)


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


def parse_sets(cs_lf):
    sets = {}
    for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End",
                         cs_lf):
        slots = {}
        for line in m.group(2).splitlines():
            lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
            if lm:
                slots[int(lm.group(1))] = lm.group(2).split(";")[0]
        sets[m.group(1)] = slots
    return sets


def get_set_block(cs_lf, name):
    m = re.search(r"(?ms)^CommandSet[ \t]+%s[ \t]*\n.*?^End[ \t]*\n"
                  % re.escape(name), cs_lf)
    assert m, "command set not found: " + name
    return m.group(0)


def insert_slot(block, slot, command_text):
    """Insert '  <slot> = <command_text>' before the first numbered line with
    a higher slot (or before End).  Asserts the slot is free."""
    lines = block.split("\n")
    slots_here = {}
    for i, line in enumerate(lines):
        lm = re.match(r"\s*(\d+)\s*=", line)
        if lm:
            slots_here.setdefault(int(lm.group(1)), i)
    assert slot not in slots_here, "slot %d occupied in %r" % (slot, lines[0])
    at = None
    for s in sorted(slots_here):
        if s > slot:
            at = slots_here[s]
            break
    if at is None:
        at = len(lines) - 1
        while not re.match(r"End[ \t]*$", lines[at]):
            at -= 1
    lines.insert(at, "  %-2d = %s" % (slot, command_text))
    return "\n".join(lines)


def top_object_block(lf, name):
    m = re.search(r"(?m)^Object[ \t]+%s[ \t]*(;[^\n]*)?$" % re.escape(name),
                  lf)
    assert m, "object not found: " + name
    m2 = re.search(r"(?m)^End[ \t]*$", lf[m.start():])
    assert m2, "no top-level End after object " + name
    return lf[m.start():m.start() + m2.end()]


def fmt_time(v):
    return "%d.0" % v if v == int(v) else ("%.2f" % v).rstrip("0")


# ================================================== 1. effective sources
archives = sorted((f for f in os.listdir(SPE_DIR)
                   if f.lower().endswith(".big")
                   and f.lower() < OUT_NAME.lower()),
                  key=str.lower, reverse=True)
cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}


def effective(path):
    want = path.lower()
    for a in archives:
        for e in cache[a]:
            if e.path.lower() == want:
                return e.data.decode("latin-1"), a
    return None, None


def EFFECTIVE(path):
    return effective(path)[0]


sources = {}
for path, owner in OWNERS.items():
    data, got = effective(path)
    assert data is not None, "effective source not found: " + path
    assert got == owner, "ownership drift for %s: %s (expected %s)" % (
        path, got, owner)
    sources[path] = data
print("effective-file ownership verified (%d files)" % len(sources))

# the only new identifier is the module tag - must be unused everywhere
ini_space = []
seen = set()
for a in archives:
    for e in cache[a]:
        lp = e.path.lower()
        if lp in seen or not lp.endswith((".ini", ".str")):
            continue
        seen.add(lp)
        ini_space.append(e.data.decode("latin-1"))
blob = "\n".join(ini_space)
assert not re.search(r"(?<![\w:])%s(?![\w:])" % re.escape(MODTAG), blob), \
    "identifier collision: " + MODTAG
print("new identifier collision-free (%s, %d effective INI files)"
      % (MODTAG, len(seen)))

# ================================================== 2. scheme re-verification
# (drift guards: the decisions in this build are valid only while these hold)
cs_src = sources[CS_PATH]
cs_lf0 = to_lf(cs_src)
pre_sets = parse_sets(cs_lf0)
cb_src = sources[CB_PATH]
cb_lf0 = to_lf(cb_src)

# 2a. the UAV chain (kwai-uav shapes we degate/move)
sp_lf = to_lf(EFFECTIVE("Data\\INI\\SpecialPower.ini"))
m = re.search(r"(?ms)^SpecialPower %s\s*\n.*?^End" % POWER, sp_lf)
assert m, "UAV special power missing"
pow_block = m.group(0)
pow_code = "\n".join(l.split(";")[0] for l in pow_block.split("\n"))
for needle in ("Enum                    = SPECIAL_SPY_DRONE",
               "ReloadTime              = 120000",
               "SharedSyncedTimer       = Yes"):
    assert needle in pow_block, "UAV power drift: " + needle
assert "RequiredScience" not in pow_code, "UAV power grew a science gate"
assert "ShortcutPower" not in pow_code, "UAV power grew a shortcut"
ocl_lf = to_lf(EFFECTIVE("Data\\INI\\ObjectCreationList.ini"))
m = re.search(r"(?ms)^ObjectCreationList %s\s*\n.*?^End" % UAV_OCL, ocl_lf)
assert m and ("ObjectNames = " + DRONE) in m.group(0), "UAV OCL drift"
drone_text, drone_owner = effective(OBJ + "China\\Tank\\Aircraft\\SurveillanceUAV.ini")
assert drone_owner == "zzz-ZZZZZZKwaiUAV.big", drone_owner
drone_lf = to_lf(drone_text)
for needle in ("Object " + DRONE, "Behavior = StealthUpdate",
               "Behavior = StealthDetectorUpdate", "VisionRange     = 350"):
    assert needle in drone_lf, "drone drift: " + needle
print("UAV chain drift guards OK (power/OCL/drone shapes unchanged)")

# 2b. research button referenced ONLY by the 4 IC clones (safe to delete)
research_refs = [n for n, slots in pre_sets.items()
                 if RESEARCH in slots.values()]
assert sorted(research_refs) == [
    "Tank_ChinaInternetCenterCommandSetOne",
    "Tank_ChinaInternetCenterCommandSetOneUpgrade",
    "Tank_ChinaInternetCenterCommandSetTwo",
    "Tank_ChinaInternetCenterCommandSetTwoUpgrade"], research_refs
deploy_refs = [n for n, slots in pre_sets.items() if DEPLOY in slots.values()]
assert sorted(deploy_refs) == sorted(research_refs), deploy_refs

# 2c. CC occupancy (free slots free, taunt lines where expected)
for _path, _obj, set_names, (mode, slot), _o in CC_PLAN:
    for sn in set_names:
        slots = pre_sets[sn]
        if mode == "insert":
            assert slot not in slots, (sn, slot, "occupied")
        else:
            assert slots.get(slot) == "Command_ChinaTauntMenu", (sn, slot)
            assert not [s for s in range(1, 15) if s not in slots], \
                (sn, "set no longer full - use the free slot instead")
# Leang keeps her taunt menu (she has the free slot the others lack)
assert pre_sets["Spec_ChinaCommandCenterCommandSet"][12] == \
    "Command_ChinaTauntMenu"
print("CC occupancy verified (USA 12 free x5, GLA 11 free x6, Spec 10 free "
      "x2, China taunt at 12 in the 8 full sets)")

# 2d. queue defaults: none of the three buildings sets MaxQueueEntries
for path in (BAR_PATH, WF_PATH, AIR_PATH):
    lf = to_lf(sources[path])
    assert "MaxQueueEntries" not in lf, path
    assert len(re.findall(r"(?m)^\s*Behavior\s*=\s*ProductionUpdate\b", lf)) \
        == 1, path

# ================================================== 3. patches
patched = {}
edits = {p: [] for p in OWNERS}          # path -> [(old_lf, new_lf), ...]


def record(path, old, new):
    edits[path].append((old, new))


DEPLOY_LINE = (DEPLOY + " ; " + TAG + ": ungated Surveillance UAV deploy"
               " (kwai-uav power, research gate removed)")
DEPLOY_LINE_TAUNT = (DEPLOY + " ; " + TAG + ": ungated Surveillance UAV"
                     " deploy - replaces the China taunt-menu button"
                     " (set was full 14/14)")

# ---------------------------------------------------- 3a. CommandSet.ini
cs = cs_lf0

# IC clones: research+deploy at 7-8 -> restored garrison exit cameos
IC_OLD = ("  7 = Tank_Command_UpgradeKwaiUAVProgram ; zzz-ZZZZZZKwaiUAV\n"
          "  8 = Tank_Command_KwaiUAVDeploy ; zzz-ZZZZZZKwaiUAV\n")
IC_NEW = ("  7 = Command_StructureExit ; " + TAG + ": exit cameo restored"
          " (UAV research deleted, deploy moved to the Command Center)\n"
          "  8 = Command_StructureExit ; " + TAG + ": exit cameo restored\n")
cs = replace_exact(cs, IC_OLD, IC_NEW, count=4)
for _ in range(4):
    record(CS_PATH, IC_OLD, IC_NEW)

# CC sets
for _path, _obj, set_names, (mode, slot), _o in CC_PLAN:
    for sn in set_names:
        old_block = get_set_block(cs, sn)
        if mode == "insert":
            new_block = insert_slot(old_block, slot, DEPLOY_LINE)
        else:
            lm = re.search(r"(?m)^([ \t]*)%d[ \t]*=[ \t]*Command_ChinaTauntMenu[ \t]*$"
                           % slot, old_block)
            assert lm, (sn, "taunt line not found")
            new_block = old_block.replace(
                lm.group(0), "  %d = %s" % (slot, DEPLOY_LINE_TAUNT), 1)
        cs = replace_exact(cs, old_block, new_block)
        record(CS_PATH, old_block, new_block)
patched[CS_PATH] = from_lf(cs, eol_of(cs_src))

# ---------------------------------------------------- 3b. CommandButton.ini
cb = cb_lf0
CB_HDR_OLD = (
    ";;; zzz-ZZZZZZKwaiUAV: UAV Surveillance Program - research (Internet Center\n"
    ";;; slot 7) + upgrade-gated deploy special power (slot 8).  Gating idiom =\n"
    ";;; ShockWave GLA Radar Van Scan: NEED_UPGRADE on the button (client side)\n"
    ";;; + StartsPaused/UnpauseSpecialPowerUpgrade on the module (logic side).\n"
    "\n"
    "CommandButton Tank_Command_UpgradeKwaiUAVProgram\n"
    "  Command       = PLAYER_UPGRADE\n"
    "  Upgrade       = Tank_Upgrade_KwaiUAVProgram\n"
    "  TextLabel     = CONTROLBAR:UpgradeKwaiUAVProgram\n"
    "  ButtonImage   = SASienceSpyDrone\n"
    "  ButtonBorderType        = UPGRADE ; Identifier for the User as to what kind of button this is\n"
    "  DescriptLabel           = CONTROLBAR:TooltipUpgradeKwaiUAVProgram\n"
    "  PurchasedLabel          = CONTROLBAR:TooltipUpgradeKwaiUAVProgram\n"
    "  UnitSpecificSound = MoneyWithdraw\n"
    "End\n"
    "\n")
CB_HDR_NEW = (
    ";;; zzz-ZZZZZZKwaiUAV: deployable Surveillance UAV special power.\n"
    ";;; " + TAG + ": research gate REMOVED - the UAV Surveillance Program\n"
    ";;; research button was deleted, NEED_UPGRADE + the Upgrade ref came off the\n"
    ";;; deploy button, and the ungated deploy power now lives on EVERY faction's\n"
    ";;; Command Center (the kwai-uav Internet Center modules were removed; the\n"
    ";;; orphaned Upgrade block in Upgrade.ini stays defined but is unreachable).\n"
    "\n")
cb = replace_exact(cb, CB_HDR_OLD, CB_HDR_NEW)
record(CB_PATH, CB_HDR_OLD, CB_HDR_NEW)

CB_GATE_OLD = (
    "  Options           = NEED_TARGET_POS CONTEXTMODE_COMMAND NEED_UPGRADE OK_FOR_MULTI_SELECT\n"
    "  Upgrade           = Tank_Upgrade_KwaiUAVProgram\n")
CB_GATE_NEW = (
    "  Options           = NEED_TARGET_POS CONTEXTMODE_COMMAND OK_FOR_MULTI_SELECT ; "
    + TAG + ": research gate deleted (upgrade requirement + ref removed)\n")
cb = replace_exact(cb, CB_GATE_OLD, CB_GATE_NEW)
record(CB_PATH, CB_GATE_OLD, CB_GATE_NEW)
patched[CB_PATH] = from_lf(cb, eol_of(cb_src))

# ---------------------------------------------------- 3c. InternetCenter.ini
ic = to_lf(sources[IC_PATH])
IC_MODS_OLD = (
    "  Behavior           = OCLSpecialPower ModuleTag_KUAV_Power01 ; zzz-ZZZZZZKwaiUAV: deployable Surveillance UAV\n"
    "    SpecialPowerTemplate = Tank_SpecialPowerKwaiUAV\n"
    "    OCL                  = Tank_SUPERWEAPON_KwaiUAV\n"
    "    CreateLocation       = CREATE_ABOVE_LOCATION ; donor: USA command centers' SpecialPowerSpyDrone module\n"
    "    StartsPaused         = Yes ; Unpaused by upgrade module (GLA Radar Van Scan idiom)\n"
    "  End\n"
    "  Behavior = UnpauseSpecialPowerUpgrade ModuleTag_KUAV_Unpause01 ; zzz-ZZZZZZKwaiUAV\n"
    "    SpecialPowerTemplate = Tank_SpecialPowerKwaiUAV\n"
    "    TriggeredBy = Tank_Upgrade_KwaiUAVProgram\n"
    "  End\n")
IC_MODS_NEW = (
    "  ; " + TAG + ": kwai-uav's gated deploy modules (the paused OCLSpecialPower\n"
    "  ; power + its research-unpause companion) removed - the ungated deploy power\n"
    "  ; now lives on EVERY faction's Command Center (incl. Tank_ChinaCommandCenter);\n"
    "  ; the IC command-set clone slots 7-8 are garrison exit cameos again.\n")
ic = replace_exact(ic, IC_MODS_OLD, IC_MODS_NEW)
record(IC_PATH, IC_MODS_OLD, IC_MODS_NEW)
patched[IC_PATH] = from_lf(ic, eol_of(sources[IC_PATH]))

# ---------------------------------------------------- 3d. CC object modules
CC_MODULE = (
    "\n  Behavior           = OCLSpecialPower " + MODTAG + " ; " + TAG +
    ": ungated Surveillance UAV deploy (kwai-uav Global Hawk clone;"
    " every faction's Command Center carries this module)\n"
    "    SpecialPowerTemplate = Tank_SpecialPowerKwaiUAV\n"
    "    OCL                  = Tank_SUPERWEAPON_KwaiUAV\n"
    "    CreateLocation       = CREATE_ABOVE_LOCATION ; donor: USA command"
    " centers' SpecialPowerSpyDrone module\n"
    "  End\n")
for path, objname, _sets, _mode, _o in CC_PLAN:
    src = sources[path]
    lf = to_lf(src)
    m = re.search(r"(?m)^Object[ \t]+%s[ \t]*(;[^\n]*)?$" % objname, lf)
    assert m, (path, objname)
    m2 = re.search(r"(?m)^End[ \t]*$", lf[m.start():])
    assert m2, path
    end_abs = m.start() + m2.start()
    lf = lf[:end_abs] + CC_MODULE + lf[end_abs:]
    record(path, "", CC_MODULE)
    patched[path] = from_lf(lf, eol_of(src))

# ---------------------------------------------------- 3e. Scout Car vision
sc = to_lf(sources[SC_PATH])
SC_V_OLD = ("  VisionRange     = 450           ; zzz-ZZZZZKwaiRoster: recon"
            " buff (donor 200); vanilla ChinaVehicleBullfrog untouched\n")
SC_V_NEW = ("  VisionRange     = 900           ; zzz-ZZZZZKwaiRoster: recon"
            " buff (donor 200); vanilla ChinaVehicleBullfrog untouched ; "
            + TAG + ": 450 -> 900\n")
SC_S_OLD = ("  ShroudClearingRange = 500 ; zzz-ZZZZZKwaiRoster: recon buff"
            " (donor 200)\n")
SC_S_NEW = ("  ShroudClearingRange = 1000 ; zzz-ZZZZZKwaiRoster: recon buff"
            " (donor 200) ; " + TAG + ": 500 -> 1000\n")
sc = replace_exact(sc, SC_V_OLD, SC_V_NEW)
sc = replace_exact(sc, SC_S_OLD, SC_S_NEW)
record(SC_PATH, SC_V_OLD, SC_V_NEW)
record(SC_PATH, SC_S_OLD, SC_S_NEW)
patched[SC_PATH] = from_lf(sc, eol_of(sources[SC_PATH]))

# ---------------------------------------------------- 3f. queue bumps
QUEUE_LINE = "    MaxQueueEntries = 30 ; %s: was 9 (engine default)\n" % TAG
for path, modtag in ((BAR_PATH, "ModuleTag_10"), (WF_PATH, "ModuleTag_12"),
                     (AIR_PATH, "ModuleTag_11")):
    src = sources[path]
    lf = to_lf(src)
    anchor = "  Behavior = ProductionUpdate %s\n" % modtag
    lf = replace_exact(lf, anchor, anchor + QUEUE_LINE)
    record(path, anchor, anchor + QUEUE_LINE)
    patched[path] = from_lf(lf, eol_of(src))

# ---------------------------------------------------- 3g. infantry 50/50
for rel, _owner, objname, c_old, c_new, t_old, t_new in INF_PLAN:
    path = OBJ + rel
    src = sources[path]
    lf = to_lf(src)
    block = top_object_block(lf, objname)
    mc = re.findall(r"(?m)^([ \t]*BuildCost[ \t]*=[ \t]*)([\d.]+)([^\n]*)$",
                    block)
    mt = re.findall(r"(?m)^([ \t]*BuildTime[ \t]*=[ \t]*)([\d.]+)([^\n]*)$",
                    block)
    assert len(mc) == 1 and len(mt) == 1, (path, objname, mc, mt)
    assert int(float(mc[0][1])) == c_old, (path, mc[0][1], c_old)
    assert float(mt[0][1]) == t_old, (path, mt[0][1], t_old)
    old_c_line = "%s%s%s" % mc[0]
    new_c_line = "%s%d%s ; %s: was %d (50%%%s)" % (
        mc[0][0], c_new, mc[0][2], TAG, c_old,
        "" if c_old == 2 * c_new else ", rounded down to a multiple of $5")
    old_t_line = "%s%s%s" % mt[0]
    new_t_line = "%s%s%s ; %s: was %s (2x build speed)" % (
        mt[0][0], fmt_time(t_new), mt[0][2], TAG, mt[0][1])
    new_block = replace_exact(block, old_c_line + "\n", new_c_line + "\n")
    new_block = replace_exact(new_block, old_t_line + "\n", new_t_line + "\n")
    lf = replace_exact(lf, block, new_block)
    record(path, block, new_block)
    patched[path] = from_lf(lf, eol_of(src))

assert sorted(patched) == sorted(OWNERS)
print("patched %d files" % len(patched))

# ================================================== 4. verification
# ---- exact line-level diff audits on ALL 54 files (added/removed multisets
#      must equal the sum of the recorded edits - sibling hunks byte-survive)
for path in sorted(patched):
    exp_removed, exp_added = Counter(), Counter()
    for old, new in edits[path]:
        def lines_of(x):
            if not x:
                return Counter()
            return Counter(x.split("\n")[:-1] if x.endswith("\n")
                           else x.split("\n"))
        o, n = lines_of(old), lines_of(new)
        exp_removed += o - n
        exp_added += n - o
    d = unified(to_lf(sources[path]), to_lf(patched[path]))
    got_added = Counter(l[1:] for l in d if l.startswith("+"))
    got_removed = Counter(l[1:] for l in d if l.startswith("-"))
    assert got_removed == +exp_removed, (path, got_removed - exp_removed,
                                         exp_removed - got_removed)
    assert got_added == +exp_added, (path, got_added - exp_added,
                                     exp_added - got_added)
print("line-level diff audits OK on all %d files" % len(patched))

# ---- block-balance (End-count) deltas
for path in patched:
    want = {CB_PATH: -1, IC_PATH: -2}.get(path, 0)
    if path in [p for p, *_ in CC_PLAN]:
        want = 1
    d = end_lines(to_lf(patched[path])) - end_lines(to_lf(sources[path]))
    assert d == want, (path, d, want)
print("block-balance deltas OK (CB -1, IC -2, 15 CCs +1, rest 0)")

# ---- CommandButton.ini: research button gone, deploy degated, siblings kept
cb_new = to_lf(patched[CB_PATH])
assert RESEARCH not in cb_new
m = re.search(r"(?ms)^CommandButton %s\s*\n.*?^End" % DEPLOY, cb_new)
assert m, "deploy button lost"
dep = m.group(0)
dep_code = "\n".join(l.split(";")[0] for l in dep.split("\n"))
assert "NEED_UPGRADE" not in dep_code
assert not re.search(r"(?m)^\s*Upgrade\s*=", dep_code)
assert "SpecialPower      = " + POWER in dep
for sib in ("Tank_Command_ConstructChinaTeslaCoil",
            "Tank_Command_UpgradeKwaiPDL",
            "Tank_Command_ConstructChinaInfantrySharpshooter",
            "Tank_Command_ConstructChinaInfantryFlameThrower",
            "Tank_Command_ConstructChinaInfantryMiniGunner",
            "Tank_Command_ConstructChinaVehicleScoutCar",
            "Command_ChinaTauntMenu", "Command_SpyDrone"):
    assert re.search(r"(?m)^CommandButton\s+%s\b" % sib, cb_new), sib
print("CommandButton audit OK (research deleted, deploy ungated, siblings "
      "defined)")

# ---- InternetCenter: gating modules gone, everything else intact
ic_new = to_lf(patched[IC_PATH])
for gone in ("ModuleTag_KUAV_Power01", "ModuleTag_KUAV_Unpause01",
             "StartsPaused", "UnpauseSpecialPowerUpgrade",
             "Tank_Upgrade_KwaiUAVProgram"):
    assert gone not in ic_new, gone
for kept in ("CommandSet        = Tank_ChinaInternetCenterCommandSetOne",
             "ChineseHackedSpecialPowerSpySatellite",
             "Behavior = CommandSetUpgrade ModuleTag_31",
             "Behavior = CommandSetUpgrade ModuleTag_32"):
    assert kept in ic_new, kept

# ---- CC objects: module present once, inside the right object
for path, objname, _sets, _mode, _o in CC_PLAN:
    lf = to_lf(patched[path])
    assert lf.count(MODTAG) == 1, path
    block = top_object_block(lf, objname)
    assert MODTAG in block, (path, "module landed outside " + objname)
    assert block.count("SpecialPowerTemplate = " + POWER) == 1, path
    assert "StartsPaused" not in block.split(MODTAG)[1].split("End")[0], path
print("IC module removal + 15 CC module insertions OK")

# ---- command-set layouts: exact expectations for every touched set
cs_new_lf = to_lf(patched[CS_PATH])
new_sets = parse_sets(cs_new_lf)
for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):
    icset = new_sets["Tank_ChinaInternetCenterCommandSet" + v]
    for s in range(1, 9):
        assert icset[s] == "Command_StructureExit", (v, s)
    assert icset[9] == "Command_Evacuate"
    assert icset[12] == "Command_ChinaUpgradeSystemHack"
    assert icset[14] == "Command_Sell"
    assert RESEARCH not in icset.values() and DEPLOY not in icset.values()
for _path, _obj, set_names, (mode, slot), _o in CC_PLAN:
    for sn in set_names:
        was, now = pre_sets[sn], new_sets[sn]
        assert now[slot] == DEPLOY, (sn, slot)
        exp = dict(was)
        exp[slot] = DEPLOY
        assert now == exp, (sn, "unexpected drift", now, exp)
print("command-set layout audits OK (4 IC clones restored, 21 CC sets carry "
      "the deploy button at their planned slot)")

# ---- closure: every slot of every set resolves to a CommandButton, modulo
# any violations ShockWave itself already ships (baseline-aware)
def closure_violations(cs_lf, cb_lf):
    names = set(re.findall(r"(?m)^CommandButton[ \t]+(\S+)", cb_lf))
    bad = set()
    for sn, slots in parse_sets(cs_lf).items():
        for sl, btn in slots.items():
            if btn not in names:
                bad.add((sn, sl, btn))
    return bad


baseline_bad = closure_violations(cs_lf0, cb_lf0)
new_bad = closure_violations(cs_new_lf, cb_new)
assert new_bad <= baseline_bad, ("new dangling command-set refs",
                                 new_bad - baseline_bad)
touched_sets = set()
for _path, _obj, set_names, _mode, _o in CC_PLAN:
    touched_sets.update(set_names)
touched_sets.update("Tank_ChinaInternetCenterCommandSet" + v
                    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"))
for sn in touched_sets:
    for sl, btn in new_sets[sn].items():
        assert (sn, sl, btn) not in new_bad, (sn, sl, btn)
print("cross-reference closure OK (no new dangling refs; all %d touched sets "
      "fully resolve; baseline pre-existing violations: %d)"
      % (len(touched_sets), len(baseline_bad)))

# ---- infantry: exact new numbers + completeness re-enumeration
def field(block, name):
    m = re.search(r"(?mi)^\s*%s\s*=\s*([^;\n]+)" % name, block)
    return m.group(1).strip() if m else None


for rel, _owner, objname, c_old, c_new, t_old, t_new in INF_PLAN:
    lf = to_lf(patched[OBJ + rel])
    block = top_object_block(lf, objname)
    assert int(field(block, "BuildCost")) == c_new, objname
    assert float(field(block, "BuildTime")) == t_new, objname

# completeness: enumerate buildable China infantry from the patched space
CHINA_SIDES = {"China", "ChinaTankGeneral", "ChinaInfantryGeneral",
               "ChinaNukeGeneral", "ChinaSpecialWeaponsGeneral"}


def enumerate_buildable_china_infantry(get_text):
    objects = {}
    for lp in sorted(seen):
        if not lp.endswith(".ini"):
            continue
        t = get_text(lp)
        if t is None or "Object" not in t:
            continue
        t = to_lf(t)
        for m in re.finditer(r"(?m)^Object[ \t]+(\S+)", t):
            m2 = re.search(r"(?mi)^End[ \t]*(;[^\n]*)?$", t[m.start():])
            if not m2:
                continue
            block = t[m.start():m.start() + m2.end()]
            name = m.group(1)
            if name not in objects:
                objects[name] = block
    cb_txt = to_lf(get_text(CB_PATH.lower()))
    cs_txt = to_lf(get_text(CS_PATH.lower()))
    live_buttons = set()
    for slots in parse_sets(cs_txt).values():
        live_buttons.update(slots.values())
    btn_obj = {}
    for m in re.finditer(r"(?ms)^CommandButton[ \t]+(\S+)[ \t]*\n(.*?)^End",
                         cb_txt):
        if m.group(1) in live_buttons and \
                re.search(r"(?m)^\s*Command\s*=\s*UNIT_BUILD", m.group(2)):
            o = field(m.group(2), "Object")
            if o:
                btn_obj.setdefault(o, []).append(m.group(1))
    result = {}
    for name, block in objects.items():
        if name in ROTR_UNITS:      # rotr-infantry merge: donor pricing
            continue                # kept by design (see CHANGELOG above)
        if field(block, "Side") not in CHINA_SIDES:
            continue
        # object-level KindOf only (the FIRST KindOf line - module-nested
        # KindOf filters, e.g. HordeUpdate's, always come later)
        kind = field(block, "KindOf") or ""
        if "INFANTRY" not in kind.split():
            continue
        if field(block, "BuildCost") is None or name not in btn_obj:
            continue
        result[name] = (int(field(block, "BuildCost")),
                        float(field(block, "BuildTime")))
    return result


def patched_text(lp):
    for p in patched:
        if p.lower() == lp:
            return patched[p]
    for a in archives:
        for e in cache[a]:
            if e.path.lower() == lp:
                return e.data.decode("latin-1")
    return None


buildable = enumerate_buildable_china_infantry(patched_text)
expected = {objname: (c_new, t_new)
            for _rel, _own, objname, _co, c_new, _to, t_new in INF_PLAN}
assert buildable == expected, (
    "buildable-China-infantry enumeration mismatch",
    {k: v for k, v in buildable.items() if expected.get(k) != v},
    {k: v for k, v in expected.items() if buildable.get(k) != v})
print("infantry completeness re-enumeration OK (exactly the %d planned "
      "objects are buildable, all at half cost/time)" % len(expected))

# ---- scout car + vanilla scout untouched
sc_new = to_lf(patched[SC_PATH])
assert "VisionRange     = 900" in sc_new
assert "ShroudClearingRange = 1000" in sc_new
assert "ModuleTag_VKitBay01" in sc_new                       # vehicle-kit bay
assert "CommandSet = Tank_ChinaVehicleScoutCarCommandSet" in sc_new
van_sc = to_lf(EFFECTIVE(OBJ + "China\\Vanilla\\Vehicles\\ScoutCar.ini"))
assert re.search(r"(?m)^\s*VisionRange\s*=\s*200\b", van_sc)
assert re.search(r"(?m)^\s*ShroudClearingRange\s*=\s*200\b", van_sc)

# ---- queue bumps in place
for path in (BAR_PATH, WF_PATH, AIR_PATH):
    lf = to_lf(patched[path])
    m = re.search(r"(?ms)^  Behavior = ProductionUpdate.*?^  End", lf)
    assert m and "MaxQueueEntries = 30" in m.group(0), path
assert "QuantityModifier = Tank_ChinaInfantryRedguard   2" in \
    to_lf(patched[BAR_PATH])
print("scout car (900/1000, bay intact, vanilla scout 200/200) + queue "
      "bumps (3x MaxQueueEntries=30) OK")


# ---- sibling survival on the shipped CommandSet.ini (and installed later)
def verify_survival(cs_text, cb_text, label=""):
    lf = to_lf(cs_text)
    sets = parse_sets(lf)
    # kwai-bunkers / tesla-coil dozer pages
    dz1 = sets["Tank_ChinaDozerCommandSet"]
    assert dz1[9] == "Tank_Command_ConstructChinaGattlingCannon"
    assert dz1[13] == "Command_ChinaButtonCommandSetOneDown"
    dz2 = sets["Tank_ChinaDozerCommandSet_Down"]
    assert dz2 == {1: "Tank_Command_ConstructChinaIndustrialPlant",
                   7: "Tank_Command_ConstructChinaBunker",
                   8: "Tank_Command_ConstructChinaHackerBunker",
                   9: "Tank_Command_ConstructChinaTeslaCoil",
                   13: "Command_ChinaButtonCommandSetOneUp",
                   14: "Command_DisarmMinesAtPosition"}, dz2
    assert sets["Tank_ChinaTeslaCoilCommandSet"] == \
        {12: "Command_Stop", 14: "Command_Sell"}
    # kwai-infantry / roster barracks
    for n in ("Tank_ChinaBarracksCommandSet",
              "Tank_ChinaBarracksCommandSetUpgrade"):
        b = sets[n]
        assert b[5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier"
        assert b[6] == "Tank_Command_ConstructChinaInfantryFlameThrower"
        assert b[7] == "Tank_Command_ConstructChinaInfantryMiniGunner"
        assert b[8] == "Tank_Command_ConstructChinaInfantrySharpshooter"
    # chaos/roster WF page 2 + artillery page 1
    wf2 = sets["Tank_ChinaWarFactoryCommandSet_Down"]
    assert wf2[2] == "Tank_Command_ConstructChinaTankJS7"
    assert wf2[7] == "Tank_Command_ConstructChinaVehicleScoutCar"
    assert wf2[12] == "Command_ChinaButtonCommandSetOneUp"
    for n in ("Tank_ChinaWarFactoryCommandSet",
              "Tank_ChinaWarFactoryCommandSetUpgrade"):
        assert sets[n][11] == "Tank_Command_ConstructChinaVehicleInfernoCannon"
        assert sets[n][12] == "Command_ChinaButtonCommandSetOneDown"
    # kwai-pdl
    assert lf.count("Tank_Command_UpgradeKwaiPDL ;") == 17
    emp = sets["Tank_ChinaTankEmperorDefaultCommandSet"]
    assert emp[9] == "Tank_Command_UpgradeKwaiPDL"
    assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
    assert emp[12] == "Command_Evacuate"
    assert sets["Tank_ChinaTankEmperorPDLCommandSet"][11] == "Command_AttackMove"
    assert 10 not in sets["Tank_ChinaTankEmperorPDLCommandSet"]
    assert 9 not in sets["Tank_ChinaTankEmperorGattlingCommandSet"]
    for n in ("Tank_ChinaTankDragonCommandSet",
              "Tank_ChinaTankDragonUpgradedCommandSet"):
        assert sets[n][9] == "Tank_Command_UpgradeKwaiPDL"
        assert 7 not in sets[n] and 8 not in sets[n]
    ct = sets["Tank_ChinaVehicleCommandTruckCommandSet"]
    assert ct[1] == "Command_CommandTankAPFSDSShells"
    assert ct[9] == "Tank_Command_UpgradeKwaiPDL"
    # vehicle-kit bays
    for n, evac in (("Tank_ChinaVehicleGattlingTankCommandSet", 10),
                    ("ChinaVehicleNukeCannonCommandSet", 12),
                    ("ChinaVehicleInfernoCannonCommandSet", 12),
                    ("ChinaVehicleInfernoCannonUpgradedCommandSet", 12),
                    ("ChinaVehicleHammerCannonCommandSet", 12),
                    ("ChinaVehicleTOSCommandSet", 12)):
        assert sets[n][7] == "Command_TransportExit", n
        assert sets[n][8] == "Command_TransportExit", n
        assert sets[n][evac] == "Command_Evacuate", n
    assert sets["Tank_ChinaVehicleScoutCarCommandSet"] == {
        1: "Command_ChinaScoutCarAreaScan", 2: "Command_ScoutCarTaunt",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        12: "Command_Evacuate", 14: "Command_Stop"}
    # doctrine / basetech / garrisons / bunkers
    pc_sets = {n for n in sets if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc_sets) == 50, len(pc_sets)
    assert "Tank_ChinaHackerBunkerCommandSet" in sets
    gat_def = sets["Tank_ChinaGattlingCannonCommandSet"]
    assert gat_def == {12: "Command_Stop", 13: "Command_UpgradeChinaMines",
                       14: "Command_Sell"}, gat_def
    assert lf.count("= Command_Evacuate") >= 60
    # kwai-uav IC clones: OUR new state (7-8 exits, no research/deploy)
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):
        icset = sets["Tank_ChinaInternetCenterCommandSet" + v]
        for s in range(1, 9):
            assert icset[s] == "Command_StructureExit", (v, s)
        assert icset[9] == "Command_Evacuate"
        assert RESEARCH not in icset.values()
        assert DEPLOY not in icset.values()
    # vanilla IC sets byte-frozen (exits 1-8)
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):
        vic = sets["ChinaInternetCenterCommandSet" + v]
        for s in range(1, 9):
            assert vic[s] == "Command_StructureExit", (v, s)
        assert DEPLOY not in vic.values()
    # untouched vanilla-shared sets stay frozen
    assert sets["ChinaVehicleBullfrogCommandSet"] == \
        {1: "Command_ChinaScoutCarAreaScan", 2: "Command_ScoutCarTaunt",
         14: "Command_Stop"}
    for n in ("ChinaTankDragonCommandSet", "GenericCommandSet",
              "ChinaTankOverlordDefaultCommandSet",
              "Nuke_ChinaVehicleNukeCannonCommandSet"):
        assert n in sets, n
        assert "Command_TransportExit" not in sets[n].values(), n
    # CC sets: deploy present at the planned slots, everything else intact
    for _path, _obj, set_names, (mode, slot), _o in CC_PLAN:
        for sn in set_names:
            assert sets[sn][slot] == DEPLOY, (sn, slot)
            exp = dict(pre_sets[sn])
            exp[slot] = DEPLOY
            assert sets[sn] == exp, sn
    # Leang keeps her taunt menu; USA/GLA taunt menus untouched at 13
    assert sets["Spec_ChinaCommandCenterCommandSet"][12] == \
        "Command_ChinaTauntMenu"
    assert sets["AmericaCommandCenterCommandSet"][13] == \
        "Command_AmericaTauntMenu"
    assert sets["GLACommandCenterCommandSet"][13] == "Command_GLATauntMenu"
    # taunt machinery sets stay intact (Fai's shown as representative + count)
    assert len(sets["Infa_ChinaCommandCenterTauntCommandSet"]) == 14
    assert sets["Infa_ChinaCommandCenterTauntCommandSet"][13] == \
        "Command_ChinaExitTauntMenu"
    assert "FakeGLACommandCenterCommandSet" in sets
    # USA spy drone stays where it was
    for n in ("AmericaCommandCenterCommandSet",
              "AirF_AmericaCommandCenterCommandSet",
              "Lazr_AmericaCommandCenterCommandSet",
              "SupW_AmericaCommandCenterCommandSet",
              "Armor_AmericaCommandCenterCommandSet"):
        assert sets[n][7] == "Command_SpyDrone", n
    # CommandButton side
    cblf = to_lf(cb_text)
    assert RESEARCH not in cblf
    assert re.search(r"(?m)^CommandButton\s+%s\b" % DEPLOY, cblf)
    print("  sibling survival OK" + (" (%s)" % label if label else ""))


verify_survival(patched[CS_PATH], patched[CB_PATH], "shipped")

# ================================================== 5. package + install
SHIPPED = sorted(patched)
entries = [BigEntry(p, patched[p].encode("latin-1")) for p in SHIPPED]
out_local = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_local)
print("wrote %s (%d files, %d bytes)" % (out_local, len(entries),
                                         os.path.getsize(out_local)))

# ---- sort order against the real listings
shipped_lc = {p.lower() for p in SHIPPED}
for d in (SPE_DIR, SHW_DIR):
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    assert listing[i - 1].lower() == "zzz-zzzzzzzvetinsignia.big", listing
    assert listing[i + 1].lower().startswith("zzz_controlbarpro"), listing
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, (d, later, e.path)
    print("sort order OK in %s: %s < %s < %s (no later archive claims any "
          "shipped path)" % (d, listing[i - 1], OUT_NAME, listing[i + 1]))

# ---- install + re-read verification
blob_bytes = open(out_local, "rb").read()
for d in (SPE_DIR, SHW_DIR):
    dst = os.path.join(d, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob_bytes)
    back = read_big(dst)
    assert [e.path for e in back] == [e.path for e in entries]
    for x, y in zip(back, entries):
        assert x.data == y.data, x.path
    verify_survival(find_entry(back, CS_PATH).data.decode("latin-1"),
                    find_entry(back, CB_PATH).data.decode("latin-1"),
                    "installed " + d)
    print("installed + re-read OK:", dst)

# ---- post-install effective-space audit (both dirs)
for d in (SPE_DIR, SHW_DIR):
    arcs = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")),
                  key=str.lower, reverse=True)
    arc_cache = {a: read_big(os.path.join(d, a)) for a in arcs}

    def eff2(path, _arcs=arcs, _c=arc_cache):
        want = path.lower()
        for a in _arcs:
            for e in _c[a]:
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        return None, None

    for p in SHIPPED:
        data, got = eff2(p)
        assert got == OUT_NAME, (d, p, got)
        assert data == patched[p], (d, p, "content mismatch")
    # sibling-owned files we did NOT touch keep their owners + key content
    for p, owner_prefix in (
            ("Data\\INI\\Upgrade.ini", "zzz-ZZZZZZZKwaiPDL"),      # kwai-infantry v2
            ("Data\\INI\\SpecialPower.ini", "zzz-ZZZZZZKwaiUAV"),  # kwai-infantry v2
            ("Data\\INI\\ObjectCreationList.ini", "zzz-ZZZZZZZTTeslaCoil"),
            ("Data\\Generals.str", "zzz-ZZZZZZZTTeslaCoil"),
            (OBJ + "China\\Tank\\Aircraft\\SurveillanceUAV.ini",
             "zzz-ZZZZZZKwaiUAV"),
            (OBJ + "China\\Vanilla\\Vehicles\\ScoutCar.ini", None)):
        data, got = eff2(p)
        assert data is not None, (d, p)
        if owner_prefix:
            assert got.startswith(owner_prefix), (d, p, got)
        assert got != OUT_NAME, (d, p)
    # the orphaned upgrade is still defined (documented) but unreachable:
    # no button anywhere references it, no Unpause module remains
    up_eff = eff2("Data\\INI\\Upgrade.ini")[0]
    assert "Upgrade Tank_Upgrade_KwaiUAVProgram" in up_eff
    all_ini = []
    seen2 = set()
    for a in arcs:
        for e in arc_cache[a]:
            lp = e.path.lower()
            if lp in seen2 or not lp.endswith(".ini"):
                continue
            seen2.add(lp)
            all_ini.append(e.data.decode("latin-1"))
    blob2 = "\n".join(all_ini)
    assert RESEARCH not in blob2, (d, "research button still referenced")
    refs = re.findall(r"(?m)^.*Tank_Upgrade_KwaiUAVProgram.*$", blob2)
    for r in refs:
        assert re.match(r"\s*(Upgrade\s+Tank_Upgrade_KwaiUAVProgram|;)", r), \
            (d, "unexpected live ref to the orphaned upgrade", r)
    assert "UnpauseSpecialPowerUpgrade" not in \
        eff2(IC_PATH)[0], d
    # UAV chain closure in the installed effective space
    sp_eff = eff2("Data\\INI\\SpecialPower.ini")[0]
    assert "SpecialPower Tank_SpecialPowerKwaiUAV" in sp_eff
    ocl_eff = eff2("Data\\INI\\ObjectCreationList.ini")[0]
    assert "ObjectCreationList Tank_SUPERWEAPON_KwaiUAV" in ocl_eff
    assert ("Object " + DRONE) in eff2(
        OBJ + "China\\Tank\\Aircraft\\SurveillanceUAV.ini")[0]
    # completeness enumeration against the installed effective space
    def eff_text(lp, _arcs=arcs, _c=arc_cache):
        for a in _arcs:
            for e in _c[a]:
                if e.path.lower() == lp:
                    return e.data.decode("latin-1")
        return None
    buildable2 = enumerate_buildable_china_infantry(eff_text)
    assert buildable2 == expected, (d, "installed enumeration mismatch")
    print("post-install effective-space audit OK:", d)

print("DONE")
