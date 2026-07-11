#!/usr/bin/env python3
"""Build zzz-ZZZZZKwaiRoster.big — SEVEN cross-general China units for Kwai
(China Tank General), ShockWave under GeneralsX.

Roster (all player-only; AI build lists untouched):

  War Factory PAGE 2 (chaos-units' reserved slots 4-7):
    4  Overlord      Tank_ChinaTankOverlord      -> ChinaTankOverlord (vanilla,
       $2000, WF+PropCenter).  Deliberately the VANILLA variant so the Battle
       Bunker turret option (slot 6 of its own command set) comes along; it
       also inherits china-tank-buff's 1320 HP automatically.
    5  Buratino      Tank_ChinaVehicleBuratino   -> Spec_ChinaVehicleInfernoCannon
       (SpecialWeapons/Leang TOS-1 thermobaric MLRS, $1400, WF+PropCenter).
    6  Hammer Cannon Tank_ChinaVehicleHammerCannon -> Spec_ChinaVehicleNukeLauncher
       ($1800, WF+PropCenter; donor's SCIENCE_HammerCannon gate DROPPED --
       Kwai's promotion tree cannot buy it; kwai-artillery Nuke Cannon precedent).
    7  Scout Car     Tank_ChinaVehicleScoutCar   -- NOT a stub: full CLONE of
       vanilla ChinaVehicleBullfrog with VisionRange 450 / ShroudClearingRange
       500 (donor 200/200 untouched, so vanilla-China's own scout is not buffed).

  Barracks slot 5 (set had 1-4 + 12-14 only; Barracks is NOT garrisoned --
  kwai-garrisons skipped it for its HealContain -- so no exit/evac buttons):
    5  Siege Soldier Tank_ChinaInfantrySiegeSoldier -> ChinaInfantrySiegeSoldier
       (vanilla mortar infantry, $600, Barracks).

  Airfield slots 3-4 (set was FULL: kwai-garrisons put 7 exit cameo buttons at
  3-9 + Evacuate at 10 for its 10-seat garrison.  Exit cameos are reduced
  7 -> 5 (now slots 5-9) -- garrisons' own precedent already gives several
  buildings FEWER exit buttons than seats (Command Center/War Factory/Prop
  Center have ZERO); Evacuate at 10 still dumps all 10 occupants):
    3  MiG           Tank_ChinaJetMIGFighter     -> ChinaJetMIG (vanilla napalm
       fighter, $1400, Airfield).  Vanilla variant chosen: it IS stock China,
       and its napalm missiles upgrade with Black Napalm, which Kwai can
       research (kwai-artillery moved it to his Propaganda Center).
    4  MiG Bomber    Tank_ChinaJetMIGBomber      -> ChinaJetMIGBomber (vanilla =
       ShockWave's EMP MiG Bomber, $1500, Airfield).  Vanilla variant chosen:
       stock China, EMP flavor matches Kwai's EMP mines / EMP Pulse; the Nuke
       general's $1600 nuclear variant needs his Nuclear Research Plant, which
       Kwai has no equivalent of.

Idiom: ShockWave's own cross-faction "build stub" objects (kwai-artillery
README) -- minimal Object with Side/Prerequisites/BuildCost/BuildTime and
BuildVariations = <real unit>; the factory queues the stub, the real unit
spawns.  Aircraft precedent: SupW_AmericaJetRaptor (KindOf AIRCRAFT on the
stub so the queue reserves a parking space).  Infantry precedent:
AirF_AmericaInfantryPathfinder.  All seven command buttons clone the donors'
existing construct buttons (same art + CSF labels; no new strings/textures).

Effective-file rule: CommandSet.ini and CommandButton.ini are based on the
zzz-ZZZZChaosUnits.big copies (current owners); everything else in the
archive is a new file.  This layer sorts case-insensitively AFTER
zzz-ZZZZChaosUnits.big and BEFORE zzz_ControlBarPro*.big -> it is now the
last INI layer.
"""
import difflib
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, os.path.join(HERE, "..", "chaos-units", "work"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402
from iniblocks import parse_blocks  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzz-ZZZZZKwaiRoster.big"
TAG = "zzz-ZZZZZKwaiRoster"

CS = "Data\\INI\\CommandSet.ini"
CB = "Data\\INI\\CommandButton.ini"
STR = "Data\\Generals.str"
VP = "Data\\INI\\Object\\China\\Tank\\Vehicles\\"
IP = "Data\\INI\\Object\\China\\Tank\\Infantry\\"
AP = "Data\\INI\\Object\\China\\Tank\\Aircraft\\"

EXPECT_OWNERS = {
    CS: "zzz-ZZZZChaosUnits.big",
    CB: "zzz-ZZZZChaosUnits.big",
    STR: "zzz-ZZZZChaosUnits.big",
    # donor object files (read-only here, listed to catch layer drift)
    "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\Overlord.ini": "zzx_ChinaTankBuff.big",
    "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\ScoutCar.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\Buratino.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\HammerCannon.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Vanilla\\Infantry\\SiegeSoldier.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Vanilla\\Aircraft\\MIG.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Vanilla\\Aircraft\\MIGBomber.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Tank\\Buildings\\Airfield.ini": "zzz-ZZZKwaiGarrisons.big",
    "Data\\INI\\Object\\China\\Tank\\Buildings\\Barracks.ini": "zzz-ZZKwaiBaseTech.big",
}
NEW_INI_PATHS = [
    VP + "Overlord.ini", VP + "Buratino.ini", VP + "HammerCannon.ini",
    VP + "ScoutCar.ini", IP + "SiegeSoldier.ini",
    AP + "MIG.ini", AP + "MIGBomber.ini",
]
NEW_OBJECTS = [
    "Tank_ChinaTankOverlord", "Tank_ChinaVehicleBuratino",
    "Tank_ChinaVehicleHammerCannon", "Tank_ChinaVehicleScoutCar",
    "Tank_ChinaInfantrySiegeSoldier", "Tank_ChinaJetMIGFighter",
    "Tank_ChinaJetMIGBomber",
]
NEW_BUTTONS = [
    "Tank_Command_ConstructChinaTankOverlord",
    "Tank_Command_ConstructChinaVehicleBuratino",
    "Tank_Command_ConstructChinaVehicleHammerCannon",
    "Tank_Command_ConstructChinaVehicleScoutCar",
    "Tank_Command_ConstructChinaInfantrySiegeSoldier",
    "Tank_Command_ConstructChinaJetMIGFighter",
    "Tank_Command_ConstructChinaJetMIGBomber",
]


# ---------------------------------------------------------------- helpers
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(s):
    return s.replace("\r\n", "\n")


def from_lf(s, eol):
    return s.replace("\n", eol) if eol != "\n" else s


def lf_text(b):
    return to_lf(b.decode("latin-1"))


def replace_exact(s, old, new, count, what=""):
    got = s.count(old)
    assert got == count, "%s: expected %d of %r..., found %d" % (
        what, count, old[:70], got)
    return s.replace(old, new)


def edit_set(lf, set_name, fn):
    """Apply fn to the body of `CommandSet <set_name> ... End` (exactly one)."""
    m = re.search(r"(?ms)^(CommandSet %s\n)(.*?)(^End)" % re.escape(set_name), lf)
    assert m, "set not found: " + set_name
    assert lf.count("CommandSet %s\n" % set_name) == 1, set_name
    body = fn(m.group(2))
    return lf[:m.start(2)] + body + lf[m.end(2):]


WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i, j = line.find(";"), line.find("//")
        if i >= 0 and (j < 0 or i < j):
            line = line[:i]
        elif j >= 0:
            line = line[:j]
        out.append(line)
    return "\n".join(out)


# ------------------------------------------------------------ load sources
print("== reading effective sources from", SPE_DIR)
bigs = sorted([f for f in os.listdir(SPE_DIR) if f.lower().endswith(".big")
               and f != OUT_NAME], key=str.lower)
eff_data, eff_owner = {}, {}
for b in bigs:
    for e in read_big(os.path.join(SPE_DIR, b)):
        eff_data[e.path] = e.data
        eff_owner[e.path] = b

for p, owner in EXPECT_OWNERS.items():
    assert eff_owner.get(p) == owner, \
        "ownership drift: %s owned by %s (expected %s)" % (p, eff_owner.get(p), owner)
for p in NEW_INI_PATHS:
    assert p not in eff_data, "new path already claimed: " + p

# whole effective INI text (for collision + resolution checks)
eff_ini_texts = {p: lf_text(d) for p, d in eff_data.items()
                 if p.lower().endswith(".ini") and p.startswith("Data\\INI")}
eff_all_text = "\n".join(eff_ini_texts.values())
eff_words = set(WORD.findall(eff_all_text))
for n in NEW_OBJECTS + NEW_BUTTONS:
    assert n not in eff_words, "identifier collision with effective space: " + n

eff_defined = {}
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _txt in parse_blocks(txt):
        eff_defined.setdefault(name, set()).add(t)


def eff_block(typ, name):
    for p, txt in eff_ini_texts.items():
        for t, n, _a, _b, btext in parse_blocks(txt):
            if (t, n) == (typ, name):
                return btext
    raise AssertionError("effective block missing: %s %s" % (typ, name))


# --------------------------------------------- donor-drift sanity asserts
print("== donor sanity")
DONOR_EXPECT = [
    # (object, cost, time, prereq objects, extra required text)
    ("ChinaTankOverlord", 2000, "20.0",
     ["ChinaWarFactory", "ChinaPropagandaCenter"],
     ["  KindOf = PRELOAD SELECTABLE CAN_ATTACK ATTACK_NEEDS_LINE_OF_SIGHT "
      "CAN_CAST_REFLECTIONS VEHICLE SCORE HUGE_VEHICLE\n",
      "MaxHealth       = 1320.0"]),          # china-tank-buff inherited
    ("Spec_ChinaVehicleInfernoCannon", 1400, "16.0",
     ["Spec_ChinaWarFactory", "Spec_ChinaPropagandaCenter"], []),
    ("Spec_ChinaVehicleNukeLauncher", 1800, "20.0",
     ["Spec_ChinaWarFactory", "Spec_ChinaPropagandaCenter"],
     ["Science = SCIENCE_HammerCannon"]),    # the gate we drop
    ("ChinaVehicleBullfrog", 100, "3.0", [], []),
    ("ChinaInfantrySiegeSoldier", 600, "8.0", ["ChinaBarracks"], []),
    ("ChinaJetMIG", 1400, "10", ["ChinaAirfield"], []),
    ("ChinaJetMIGBomber", 1500, "15", ["ChinaAirfield"], []),
]
for name, cost, btime, prereqs, extras in DONOR_EXPECT:
    blk = eff_block("Object", name)
    m = re.search(r"(?m)^\s*BuildCost\s*=\s*(\d+)", blk)
    assert m and int(m.group(1)) == cost, (name, "cost", m and m.group(1))
    m = re.search(r"(?m)^\s*BuildTime\s*=\s*(\S+)", blk)
    assert m and m.group(1) == btime, (name, "time", m and m.group(1))
    pm = re.search(r"(?ms)^\s*Prerequisites\s*\n(.*?)^\s*End", blk)
    donor_prereq_objs = re.findall(r"(?m)^\s*Object\s*=\s*(.+?)\s*$",
                                   pm.group(1)) if pm else []
    donor_prereq_objs = [t for line in donor_prereq_objs for t in line.split()]
    assert donor_prereq_objs == prereqs, (name, "prereqs", donor_prereq_objs)
    for x in extras:
        assert x in blk, (name, "missing donor text", x)
# Kwai's promotion tree cannot buy the Hammer Cannon science (gate drop is
# therefore mandatory, not optional):
for rank in ("Rank1", "Rank3", "Rank8"):
    assert "HammerCannon" not in eff_block(
        "CommandSet", "Tank_SCIENCE_CHINA_CommandSet" + rank), rank
# vanilla Overlord keeps its Battle Bunker option (reason we chose vanilla):
assert "Command_UpgradeChinaOverlordBattleBunker" in eff_block(
    "CommandSet", "ChinaTankOverlordDefaultCommandSet")
for n in ("ChinaTankOverlordBattleBunker", "Upgrade_ChinaOverlordBattleBunker",
          "OCL_OverlordBattleBunker"):
    assert n in eff_defined, "Overlord battle-bunker closure missing: " + n
# prereq targets we translate TO all exist:
for n in ("Tank_ChinaWarFactory", "Tank_ChinaPropagandaCenter",
          "Tank_ChinaBarracks", "Tank_ChinaAirfield"):
    assert "Object" in eff_defined.get(n, set()), "missing Kwai building: " + n


# =========================================================== CommandSet.ini
WF2_ANCHOR = "  3  = Tank_Command_ConstructChinaTankCommandTank\n"
WF2_ADD = (
    "  4  = Tank_Command_ConstructChinaTankOverlord ; " + TAG + "\n"
    "  5  = Tank_Command_ConstructChinaVehicleBuratino ; " + TAG + "\n"
    "  6  = Tank_Command_ConstructChinaVehicleHammerCannon ; " + TAG + "\n"
    "  7  = Tank_Command_ConstructChinaVehicleScoutCar ; " + TAG + "\n"
)
BAR_ANCHOR = "  4 = Tank_Command_ConstructChinaInfantryBlackLotus\n"
BAR_ADD = "  5 = Tank_Command_ConstructChinaInfantrySiegeSoldier ; " + TAG + "\n"
AIR_OLD = ("  3 = Command_StructureExit\n"
           "  4 = Command_StructureExit\n")
AIR_NEW = (
    "  3 = Tank_Command_ConstructChinaJetMIGFighter ; " + TAG +
    ": was a garrison exit cameo (7 -> 5; Evacuate at 10 still empties all seats)\n"
    "  4 = Tank_Command_ConstructChinaJetMIGBomber ; " + TAG +
    ": was a garrison exit cameo\n")


def patch_commandset(lf):
    lf = edit_set(lf, "Tank_ChinaWarFactoryCommandSet_Down",
                  lambda b: replace_exact(b, WF2_ANCHOR, WF2_ANCHOR + WF2_ADD,
                                          1, "WF page 2"))
    for s in ("Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade"):
        lf = edit_set(lf, s, lambda b: replace_exact(
            b, BAR_ANCHOR, BAR_ANCHOR + BAR_ADD, 1, s))
    for s in ("Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
        lf = edit_set(lf, s, lambda b: replace_exact(
            b, AIR_OLD, AIR_NEW, 1, s))
    return lf


# ========================================================= CommandButton.ini
# Clones of the donors' construct buttons: same art + CSF labels, new names,
# pointed at the stubs / the clone (kwai-artillery idiom).
BTN_APPENDIX = "".join("""\
CommandButton Tank_Command_Construct%s
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = %s
  TextLabel     = CONTROLBAR:%s
  ButtonImage   = %s
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:%s
End

""" % row for row in [
    ("ChinaTankOverlord", "Tank_ChinaTankOverlord",
     "ConstructChinaTankOverlord", "SNOverlord", "ToolTipChinaBuildOverlord"),
    ("ChinaVehicleBuratino", "Tank_ChinaVehicleBuratino",
     "ConstructChinaVehicleBuratino", "NVTOS-1", "ToolTipChinaBuildBuratino"),
    ("ChinaVehicleHammerCannon", "Tank_ChinaVehicleHammerCannon",
     "ConstructChinaVehicleHammerCannon", "SNHammerCannon",
     "ToolTipChinaBuildHammerCannon"),
    ("ChinaVehicleScoutCar", "Tank_ChinaVehicleScoutCar",
     "ConstructChinaVehicleBullfrog", "SNScoutCar", "ToolTipChinaBuildBullfrog"),
    ("ChinaInfantrySiegeSoldier", "Tank_ChinaInfantrySiegeSoldier",
     "ConstructChinaInfantrySiegeSoldier", "SNConscript",
     "ToolTipChinaBuildSiegeSoldier"),
    ("ChinaJetMIGFighter", "Tank_ChinaJetMIGFighter",
     "ConstructChinaJetMIG", "SNMig", "ToolTipChinaBuildMIG"),
    ("ChinaJetMIGBomber", "Tank_ChinaJetMIGBomber",
     "ConstructChinaJetMIGBomberEMP", "SNMiGBomber", "ToolTipChinaBuildMIGBomber"),
])


def patch_commandbutton(lf):
    if not lf.endswith("\n"):
        lf += "\n"
    return (lf + "\n;;; " + TAG + ": construct buttons for Kwai's cross-general "
            "China roster (donor art + labels reused)\n" + BTN_APPENDIX)


# ============================================================== object stubs
def stub(name, comment, portrait, image, draw, cost, btime, prereqs, sorting,
         variation, kindof):
    prereq_block = ""
    if prereqs:
        prereq_block = ("  Prerequisites\n" +
                        "".join("    Object = %s\n" % p for p in prereqs) +
                        "  End\n\n")
    return ("; %s: build stub letting China's Tank General (Kwai) produce\n"
            "; %s\n"
            "; Same BuildVariations idiom ShockWave uses for Tank_ChinaVehicleHackerVan,\n"
            "; SupW_AmericaJetRaptor (aircraft) and AirF_AmericaInfantryPathfinder (infantry).\n"
            "\n"
            "Object %s\n"
            "\n"
            "  ; *** ART Parameters ***\n"
            "  SelectPortrait         = %s\n"
            "  ButtonImage            = %s\n"
            "\n"
            "  Draw = W3DModelDraw ModuleTag_01\n"
            "    OkToChangeModelColor  = Yes\n"
            "    DefaultConditionState\n"
            "%s"
            "    End\n"
            "  End\n"
            "\n"
            "  ; set cost and time fields here or else they won't work\n"
            "  BuildCost       = %d\n"
            "  BuildTime       = %s          ;in seconds\n"
            "\n"
            "%s"
            "  Side = ChinaTankGeneral\n"
            "  EditorSorting = %s\n"
            "  BuildVariations = %s\n"
            "\n"
            "  KindOf = %s\n"
            "\nEnd\n" % (TAG, comment, name, portrait, image, draw, cost,
                         btime, prereq_block, sorting, variation, kindof))


STUBS = {
    VP + "Overlord.ini": stub(
        "Tank_ChinaTankOverlord",
        "the VANILLA China Overlord (bunker-capable variant; china-tank-buff 1320 HP\n"
        "; and the Battle Bunker / Gattling / Propaganda turret options come along).",
        "SNOverlord_L", "SNOverlord",
        "      Model               = NVOvrlrd\n",
        2000, "20.0",
        ["Tank_ChinaWarFactory", "Tank_ChinaPropagandaCenter"],
        "VEHICLE", "ChinaTankOverlord",
        "PRELOAD SELECTABLE CAN_ATTACK ATTACK_NEEDS_LINE_OF_SIGHT "
        "CAN_CAST_REFLECTIONS VEHICLE SCORE HUGE_VEHICLE"),
    VP + "Buratino.ini": stub(
        "Tank_ChinaVehicleBuratino",
        "Leang's TOS-1 Buratino thermobaric MLRS (Spec_ChinaVehicleInfernoCannon;\n"
        "; donor prereqs Spec_ WF+PropCenter translated to Tank_).",
        "NVTOS-1_L", "NVTOS-1",
        "      Model               = NVTOSM1\n",
        1400, "16.0",
        ["Tank_ChinaWarFactory", "Tank_ChinaPropagandaCenter"],
        "VEHICLE", "Spec_ChinaVehicleInfernoCannon",
        "PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS VEHICLE SCORE"),
    VP + "HammerCannon.ini": stub(
        "Tank_ChinaVehicleHammerCannon",
        "Leang's Hammer Cannon (Spec_ChinaVehicleNukeLauncher).  Donor gate\n"
        "; SCIENCE_HammerCannon DROPPED: Kwai's promotion tree cannot buy it\n"
        "; (Tank_SCIENCE_CHINA_CommandSetRank1/3/8) -- kwai-artillery Nuke Cannon precedent.",
        "SNHammerCannon_L", "SNHammerCannon",
        "      Model               = NVHammer\n",
        1800, "20.0",
        ["Tank_ChinaWarFactory", "Tank_ChinaPropagandaCenter"],
        "VEHICLE", "Spec_ChinaVehicleNukeLauncher",
        "PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS VEHICLE SCORE"),
    IP + "SiegeSoldier.ini": stub(
        "Tank_ChinaInfantrySiegeSoldier",
        "the vanilla China Siege Soldier (mortar infantry; donor prereq\n"
        "; ChinaBarracks translated to Tank_ChinaBarracks).",
        "SNSiegeSoldier_L", "SNConscript",
        "      Model               = AISTNG_SKN\n",
        600, "8.0",
        ["Tank_ChinaBarracks"],
        "INFANTRY", "ChinaInfantrySiegeSoldier",
        "PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE "
        "NO_GARRISON BOAT"),
    AP + "MIG.ini": stub(
        "Tank_ChinaJetMIGFighter",
        "the vanilla China MiG napalm fighter (ChinaJetMIG; Black Napalm upgrade\n"
        "; applies -- Kwai researches it at his Propaganda Center since kwai-artillery).\n"
        "; Name avoids Tank_ChinaJetMIG, which is Kwai's OWN Razor jet.",
        "SNMig_L", "SNMig",
        "      Model               = NVMIG\n",
        1400, "10",
        ["Tank_ChinaAirfield"],
        "VEHICLE", "ChinaJetMIG",
        "PRELOAD CAN_CAST_REFLECTIONS CAN_ATTACK SELECTABLE VEHICLE SCORE AIRCRAFT"),
    AP + "MIGBomber.ini": stub(
        "Tank_ChinaJetMIGBomber",
        "the vanilla China MiG Bomber (ChinaJetMIGBomber -- ShockWave's EMP MiG\n"
        "; Bomber; donor prereq ChinaAirfield translated to Tank_ChinaAirfield).",
        "SNMiGBomber_L", "SNMiGBomber",
        "      Model               = NVMig37\n",
        1500, "15",
        ["Tank_ChinaAirfield"],
        "VEHICLE", "ChinaJetMIGBomber",
        "PRELOAD CAN_CAST_REFLECTIONS CAN_ATTACK SELECTABLE VEHICLE SCORE AIRCRAFT"),
}
# stubs share the donor KindOf so the production queue treats them like the
# real unit (AIRCRAFT on the MiG stubs reserves an airfield parking space,
# exactly like the SupW_AmericaJetRaptor precedent).


# ------------------------------------------------------- Scout Car CLONE
SCOUT_DONOR_PATH = "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\ScoutCar.ini"
SCOUT_TRANSFORMS = [
    ("Object ChinaVehicleBullfrog\n", "Object Tank_ChinaVehicleScoutCar\n", 1),
    ("  VisionRange     = 200           ;Needs to see farther and match it's "
     "weapon range -- else troop crawlers will get slaughtered against tanks!\n",
     "  VisionRange     = 450           ; " + TAG + ": recon buff (donor 200); "
     "vanilla ChinaVehicleBullfrog untouched\n", 1),
    ("  ShroudClearingRange = 200\n",
     "  ShroudClearingRange = 500 ; " + TAG + ": recon buff (donor 200)\n", 1),
]
SCOUT_HEADER = (
    "; " + TAG + ": Kwai's Scout Car -- a full CLONE of vanilla China's\n"
    "; ChinaVehicleBullfrog (Vanilla\\Vehicles\\ScoutCar.ini) rather than a build\n"
    "; stub, so its VisionRange (200 -> 450) and ShroudClearingRange (200 -> 500)\n"
    "; could be buffed without touching vanilla-China's own scout.  Everything\n"
    "; else (including the donor's lack of a Prerequisites block -- gated only by\n"
    "; owning the War Factory the button sits on -- and Side = China, matching\n"
    "; what a BuildVariations-spawned vanilla unit would carry) is donor-identical.\n"
    "\n")


def build_scout_clone():
    raw = eff_data[SCOUT_DONOR_PATH].decode("latin-1")
    eol = eol_of(raw)
    lf = to_lf(raw)
    out = lf
    for old, new, count in SCOUT_TRANSFORMS:
        out = replace_exact(out, old, new, count, "ScoutCar clone")
    out = SCOUT_HEADER + out
    # diff audit: exactly the 3 intended line swaps + the header lines
    diff = [l for l in difflib.unified_diff(lf.split("\n"), out.split("\n"),
                                            lineterm="", n=0)
            if not l.startswith(("---", "+++", "@@"))]
    removed = Counter(l[1:] for l in diff if l.startswith("-"))
    added = Counter(l[1:] for l in diff if l.startswith("+"))
    exp_removed = Counter(t[0].rstrip("\n") for t in SCOUT_TRANSFORMS)
    exp_added = Counter(t[1].rstrip("\n") for t in SCOUT_TRANSFORMS)
    exp_added.update(SCOUT_HEADER.split("\n")[:-1])  # incl. the blank separator line
    assert removed == exp_removed, (removed - exp_removed, exp_removed - removed)
    assert added == exp_added, (added - exp_added, exp_added - added)
    return from_lf(out, eol).encode("latin-1"), out


# =========================================================== build the text
out_files = {}

cs_raw = eff_data[CS].decode("latin-1")
assert eol_of(cs_raw) == "\n"
cs_new = patch_commandset(cs_raw)
out_files[CS] = cs_new.encode("latin-1")

cb_raw = eff_data[CB].decode("latin-1")
cb_eol = eol_of(cb_raw)
cb_new = patch_commandbutton(to_lf(cb_raw))
out_files[CB] = from_lf(cb_new, cb_eol).encode("latin-1")

for p, text in STUBS.items():
    out_files[p] = text.encode("latin-1")

scout_bytes, scout_lf = build_scout_clone()
out_files[VP + "ScoutCar.ini"] = scout_bytes

# ========================================================== VERIFICATION
print("== verifying")

# ---- 1. diff audits -------------------------------------------------------
cs_diff = [l for l in difflib.unified_diff(
    to_lf(cs_raw).split("\n"), cs_new.split("\n"), lineterm="", n=0)
    if not l.startswith(("---", "+++", "@@"))]
removed = Counter(l[1:] for l in cs_diff if l.startswith("-"))
added = Counter(l[1:] for l in cs_diff if l.startswith("+"))
exp_removed = Counter([AIR_OLD.split("\n")[0], AIR_OLD.split("\n")[1]] * 2)
exp_added = Counter(WF2_ADD.rstrip("\n").split("\n"))
exp_added.update([BAR_ADD.rstrip("\n")] * 2)
exp_added.update(AIR_NEW.rstrip("\n").split("\n") * 2)
assert removed == exp_removed, (removed - exp_removed, exp_removed - removed)
assert added == exp_added, (added - exp_added, exp_added - added)
print("   CommandSet diff: +%d/-%d lines as intended" %
      (sum(added.values()), sum(removed.values())))

assert out_files[CB].startswith(cb_raw.encode("latin-1")), "CB not pure-append"

# ---- 2. block balance ------------------------------------------------------
assert len(parse_blocks(cs_new)) == len(parse_blocks(to_lf(cs_raw))), \
    "CommandSet block count changed"
assert len(parse_blocks(cb_new)) == len(parse_blocks(to_lf(cb_raw))) + 7, \
    "CommandButton must gain exactly 7 blocks"
for p in NEW_INI_PATHS:
    blocks = parse_blocks(lf_text(out_files[p]))
    assert len(blocks) == 1 and blocks[0][0] == "Object", p
    col0_end = sum(1 for l in lf_text(out_files[p]).split("\n")
                   if l.rstrip() == "End" and not l.startswith((" ", "\t")))
    assert col0_end == 1, p
new_names = {parse_blocks(lf_text(out_files[p]))[0][1] for p in NEW_INI_PATHS}
assert new_names == set(NEW_OBJECTS), new_names

# ---- 3. stub closure: BuildVariations / prereqs / art / labels ------------
print("   stub closure ...")
str_txt = to_lf(eff_data[STR].decode("latin-1"))
str_defined = set(re.findall(
    r"(?mi)^((?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+)\s*$", str_txt))
mapped_images = set()
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _t2 in parse_blocks(txt):
        if t == "MappedImage":
            mapped_images.add(name)

shipped_objects = {}
for p in NEW_INI_PATHS:
    t, name, _a, _b, btext = parse_blocks(lf_text(out_files[p]))[0]
    shipped_objects[name] = btext

for name, btext in shipped_objects.items():
    nc = strip_comments(btext)
    if name != "Tank_ChinaVehicleScoutCar":
        bv = re.search(r"(?m)^\s*BuildVariations\s*=\s*(\S+)", nc)
        assert bv, name
        target = bv.group(1)
        assert "Object" in eff_defined.get(target, set()), \
            "%s: BuildVariations target %s not in effective data" % (name, target)
    for pr in re.findall(r"(?m)^\s*Object\s*=\s*(\S+)\s*$", nc):
        assert "Object" in eff_defined.get(pr, set()), \
            "%s: prerequisite %s unresolved" % (name, pr)
    for key in ("SelectPortrait", "ButtonImage"):
        m = re.search(r"(?m)^\s*%s\s*=\s*(\S+)" % key, nc)
        assert m and m.group(1) in mapped_images, \
            "%s: %s %s not a MappedImage" % (name, key, m and m.group(1))

# buttons: object / art / strings all resolve; slot references all defined
cb_blocks = {n: t2 for t, n, _a, _b, t2 in parse_blocks(cb_new)
             if t == "CommandButton"}
for bn in NEW_BUTTONS:
    body = cb_blocks[bn]
    obj = re.search(r"(?m)^\s*Object\s*=\s*(\S+)", body).group(1)
    assert obj in shipped_objects, (bn, obj)
    img = re.search(r"(?m)^\s*ButtonImage\s*=\s*(\S+)", body).group(1)
    assert img in mapped_images, (bn, img)
    for lab in re.findall(r"\b(?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+", body):
        assert lab in str_defined, "%s: label %s missing from Generals.str" % (bn, lab)
# button<->stub cost sanity: stub costs equal spec
SPEC_COSTS = {"Tank_ChinaTankOverlord": 2000, "Tank_ChinaVehicleBuratino": 1400,
              "Tank_ChinaVehicleHammerCannon": 1800, "Tank_ChinaVehicleScoutCar": 100,
              "Tank_ChinaInfantrySiegeSoldier": 600, "Tank_ChinaJetMIGFighter": 1400,
              "Tank_ChinaJetMIGBomber": 1500}
for name, btext in shipped_objects.items():
    c = int(re.search(r"(?m)^\s*BuildCost\s*=\s*(\d+)", btext).group(1))
    assert c == SPEC_COSTS[name], (name, c)

# scout clone: vision buff present, donor untouched semantics
assert "  VisionRange     = 450" in scout_lf
assert "  ShroudClearingRange = 500" in scout_lf
assert "BuildVariations" not in strip_comments(scout_lf)  # a real clone, not a stub
donor_scout = lf_text(eff_data[SCOUT_DONOR_PATH])
assert "  VisionRange     = 200" in donor_scout  # vanilla stays 200 (we ship a copy, not a patch)
# every identifier the clone references resolves in the effective space
for tok in set(WORD.findall(strip_comments(scout_lf))):
    if tok in eff_defined or not tok.startswith(("OCL_", "FX_", "Upgrade_",
                                                 "SpecialAbility")):
        continue
    assert tok in eff_words, "ScoutCar clone unresolved reference: " + tok

# ---- 4. command-set audits -------------------------------------------------
def parse_sets(txt):
    sets = {}
    for t, name, _a, _b, btext in parse_blocks(txt):
        if t != "CommandSet":
            continue
        slots = {}
        for sm in re.finditer(r"(?m)^\s*(\d+)\s*=\s*(\S+)", btext):
            slots[int(sm.group(1))] = sm.group(2)
        sets[name] = slots
    return sets


sets = parse_sets(cs_new)
all_buttons = set(cb_blocks) | {n for n, t in eff_defined.items()
                                if "CommandButton" in t}

s = sets["Tank_ChinaWarFactoryCommandSet_Down"]
assert s == {1: "Tank_Command_ConstructChinaVehicleNukeLauncher",
             2: "Tank_Command_ConstructChinaTankJS7",
             3: "Tank_Command_ConstructChinaTankCommandTank",
             4: "Tank_Command_ConstructChinaTankOverlord",
             5: "Tank_Command_ConstructChinaVehicleBuratino",
             6: "Tank_Command_ConstructChinaVehicleHammerCannon",
             7: "Tank_Command_ConstructChinaVehicleScoutCar",
             12: "Command_ChinaButtonCommandSetOneUp",
             13: "Command_Evacuate", 14: "Command_Sell"}, s
for name in ("Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade"):
    s = sets[name]
    assert s[1] == "Tank_Command_ConstructChinaInfantryRedguard", name
    assert s[2] == "Tank_Command_ConstructChinaInfantryTankHunter", name
    assert s[3] == "Tank_Command_ConstructChinaInfantryHacker", name
    assert s[4] == "Tank_Command_ConstructChinaInfantryBlackLotus", name
    assert s[5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier", name
    assert s[12] == "Command_UpgradeChinaRedguardCaptureBuilding", name
    assert s[13] in ("Command_UpgradeChinaMines", "Command_UpgradeEMPMines"), name
    assert s[14] == "Command_Sell", name
    assert set(s) == {1, 2, 3, 4, 5, 12, 13, 14}, (name, sorted(s))
for name in ("Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
    s = sets[name]
    assert s[1] == "Tank_Command_ConstructChinaJetMIG", name          # Razor
    assert s[2] == "Tank_Command_ConstructChinaVehicleHelix", name
    assert s[3] == "Tank_Command_ConstructChinaJetMIGFighter", name
    assert s[4] == "Tank_Command_ConstructChinaJetMIGBomber", name
    for i in range(5, 10):
        assert s[i] == "Command_StructureExit", (name, i)             # 5 cameos
    assert s[10] == "Command_Evacuate", name                          # garrisons
    assert s[11] == "Command_UpgradeChinaAircraftArmor", name
    assert s[12] == "Command_UpgradeChinaHelixArmor", name
    assert s[13] in ("Command_UpgradeChinaMines", "Command_UpgradeEMPMines"), name
    assert s[14] == "Command_Sell", name
    assert set(s) == set(range(1, 15)), name
# every touched set: all slots 1-14, every referenced button defined
for name in ("Tank_ChinaWarFactoryCommandSet_Down",
             "Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade",
             "Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
    for slot, btn in sets[name].items():
        assert 1 <= slot <= 14, (name, slot)
        assert btn in all_buttons, "unknown button %s in %s" % (btn, name)

# ---- 5. sibling survival on shipped bytes ----------------------------------
print("   sibling survival ...")
# chaos-units WF page-1 (both variants): artillery 11, page-down 12, garrisons 13
for name in ("Tank_ChinaWarFactoryCommandSet", "Tank_ChinaWarFactoryCommandSetUpgrade"):
    s = sets[name]
    assert s[11] == "Tank_Command_ConstructChinaVehicleInfernoCannon", name
    assert s[12] == "Command_ChinaButtonCommandSetOneDown", name
    assert s[13] == "Command_Evacuate" and s[14] == "Command_Sell", name
    for i in range(1, 11):
        assert i in s, (name, i)
# chaos sets intact
assert "RussianTankGolemCommandSet" in sets
assert sets["Tank_ChinaVehicleCommandTruckCommandSet"][12] == \
    "Command_ChinaCommandTruckSwitchToPowers"
assert sets["Tank_ChinaVehicleCommandTruckPowersCommandSet"][12] == \
    "Command_ChinaCommandTruckSwitchToNormal"
# kwai-doctrine 50-set machine + garrisons evacuates
assert cs_new.count("CommandSet Tank_ChinaPropagandaCenter") == 50, \
    cs_new.count("CommandSet Tank_ChinaPropagandaCenter")
assert len(re.findall(r"(?m)^ 12  = Command_Evacuate", cs_new)) >= 50
# kwai-artillery relocated upgrades at prop center 4-5 (both base variants)
assert cs_new.count("  4  = Command_UpgradeChinaChainGuns\n") >= 2
assert cs_new.count("  5  = Command_UpgradeChinaBlackNapalm\n") >= 2
# emperor-bunker / doctrine / bunkers / garrisons sets exist
for name in ("Tank_ChinaDozerCommandSet", "Tank_ChinaDozerCommandSet_Down",
             "Tank_ChinaHackerBunkerCommandSet", "Tank_ChinaPowerPlantCommandSet",
             "Tank_ChinaPowerPlantCommandSetUpgrade",
             "Tank_ChinaTankEmperorDefaultCommandSet"):
    assert ("CommandSet %s\n" % name) in cs_new, "sibling set lost: " + name
emp = sets["Tank_ChinaTankEmperorDefaultCommandSet"]
assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
assert emp[12] == "Command_Evacuate"
# zzy_MammothBunker transport slots
assert ("  4  = Command_TransportExit\n"
        "  5  = Command_TransportExit\n"
        "  6  = Command_TransportExit\n"
        "  7  = Command_TransportExit\n"
        "  8  = Command_Evacuate\n") in cs_new, "Mammoth bunker slots lost"
# zzyzz_PropTowers battlemaster sets
assert "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n" in cs_new
assert " 10 = Command_UpgradeChinaOverlordPropagandaTower" in cs_new
# CommandButton.ini: chaos buttons survive (pure-append asserted); spot-check
for bn in ("Tank_Command_ConstructChinaTankJS7",
           "Tank_Command_ConstructChinaTankCommandTank",
           "Tank_Command_ConstructChinaVehicleInfernoCannon",
           "Tank_Command_ConstructChinaVehicleNukeLauncher"):
    assert ("CommandButton %s\n" % bn) in cb_new, bn

# ---- 6. no stray page-2 dupes: each new button appears in exactly one set --
for bn in NEW_BUTTONS:
    uses = [nm for nm, sl in sets.items() if bn in sl.values()]
    expect = 2 if bn in (NEW_BUTTONS[4], NEW_BUTTONS[5], NEW_BUTTONS[6]) else 1
    assert len(uses) == expect, (bn, uses)

# ---- 7. archive name sort position (both real dirs) ------------------------
for d in (SPE_DIR, SHW_DIR):
    listing = sorted(set(os.listdir(d)) | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    after = [f for f in listing[:i] if f.lower().endswith(".big")]
    before = [f for f in listing[i + 1:] if f.lower().endswith(".big")]
    assert "zzz-ZZZZChaosUnits.big" in after, d + ": must sort after chaos-units"
    assert any(f.startswith("zzz_ControlBarPro") for f in before), \
        d + ": must sort before ControlBarPro skins"
print("   sort order OK in both mod dirs")

# ============================================================ write + install
entries = [BigEntry(p, d) for p, d in sorted(out_files.items())]
out_path = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_path)
print("== wrote %s (%d files, %d bytes)" % (
    OUT_NAME, len(entries), os.path.getsize(out_path)))

with open(out_path, "rb") as f:
    blob = f.read()
for dest in (SPE_DIR, SHW_DIR):
    dst = os.path.join(dest, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob)
    back = read_big(dst)
    assert {e.path: e.data for e in back} == out_files, "install verify: " + dst
    print("== installed + re-verified:", dst)

print("\nOK.  7 units: WF page-2 slots 4-7, Barracks slot 5, Airfield slots 3-4.")
