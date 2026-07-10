#!/usr/bin/env python3
"""Build zzz-ZZZKwaiGarrisons.big — garrisonable main-base buildings for
Kwai (China Tank General), ShockWave under GeneralsX.

Eight of Kwai's structures gain a 10-man infantry GarrisonContain
(passengers fire out and receive the GARRISONED weapon bonus, which the
engine sets/clears itself in GarrisonContain.cpp:1627/1667):

    Command Center, War Factory, Supply Center, Power Plant,
    Propaganda Center, Airfield, Industrial Plant, Nuclear Silo.

Skipped (existing contain modules -- an object supports only ONE contain
module; Object::getContain returns a single interface):
  - Barracks: HealContain ModuleTag_06 (infantry enter to heal).
  - Internet Center: InternetHackContain ModuleTag_10 (30 hackers,
    stat-tune) -- explicitly excluded by design.

MECHANISM (engine-source verified, GeneralsX GeneralsMD tree):
  - One GarrisonContain block per building, mirrored field-for-field from
    the shipping faction precedents GLAPalace (ModuleTag_10) and
    ChinaBunker (ModuleTag_08): ContainMax=10, Garrison enter/exit
    sounds, ImmuneToClearBuildingAttacks=Yes.  GarrisonContainModuleData
    defaults AllowInsideKindOf to INFANTRY (GarrisonContain.cpp:70), so
    no kindof line is needed; MAX_GARRISON_POINTS=40 so all 10 riders
    get fire points.  ActionManager::canEnterObject rejects any
    non-owning player for faction structures ("faction structure...
    can't do it"), so enemies/allies can never garrison these.
  - COEXISTENCE precedent: TechWarFortress_Real ships with
    AIUpdateInterface + GarrisonContain + ProductionUpdate +
    SpawnBehavior + WeaponSet on one object -- a superset of every
    module combination this mod creates (the 5 basetech-armed buildings
    have AIUpdateInterface + WeaponSets; all 8 have ProductionUpdate;
    the Supply Center has SpawnBehavior).  GLAPalace = GarrisonContain +
    ProductionUpdate on a player-owned production building.
  - KindOf is untouched (no GARRISONABLE_UNTIL_DESTROYED): like civilian
    buildings, passengers auto-exit when the building turns REALLYDAMAGED
    and cannot re-enter until it is repaired (GarrisonContain.cpp:1750 /
    :564).  Deliberate: keeps every diff pure-insertion in the building
    files and gives attackers counterplay.

UI / EVACUATE (engine-source verified):
  - The dedicated garrison-inventory context (CB_CONTEXT_STRUCTURE_INVENTORY,
    10 physical exit buttons) is used ONLY for objects with an EMPTY
    command-set string (ControlBar.cpp:1904 "if we DO have a commandset,
    trust that the commandset will handle it") -- i.e. civilian buildings.
    Faction buildings therefore need Evacuate/exit COMMAND BUTTONS.
  - Command_Evacuate (EVACUATE) works on structures with or without an
    AIUpdateInterface: AIGroup::groupEvacuate falls back to
    contain->orderAllPassengersToExit for AI-less KINDOF_STRUCTUREs, and
    AIUpdateInterface::privateEvacuate calls the contain directly (no
    locomotion involved).  The button self-disables while empty
    (ControlBarCommand.cpp:1375 COMMAND_RESTRICTED on empty contain).
  - Command_StructureExit (EXIT_CONTAINER) buttons get passenger cameos
    via doTransportInventoryUI (GarrisonContain::isDisplayedOnControlBar
    == TRUE); they must be CONTIGUOUS in the set, and overflow
    passengers beyond the button count simply get no cameo (the
    DEBUG_CRASH is compiled out in this build -- emperor-bunker finding).
    Partial exit rosters are safe; Evacuate always unloads everyone.

COMMAND SETS (per building, both mines/EMP-mines variants unless noted):
  - Supply Center: exits 2-11 (all 10) + Evacuate 12   (slots were free)
  - Nuclear Silo:  exits 2-9 (8)      + Evacuate 10    (free)
  - Airfield:      exits 3-9 (7)      + Evacuate 10    (free)
  - Industrial Pl: exits 3-11 (9)     + Evacuate 12    (free)
  - Command Center: Evacuate at slot 4 (the commented-out ";4 =
    Command_NapalmStrike" hole; the set is otherwise FULL).  No exits.
    The Taunt sub-set is untouched (Evacuate momentarily unreachable
    while the taunt menu is open -- flip back to use it).
  - War Factory: FULL at 14 -- SACRIFICE (documented): slot 13
    Command_UpgradeChinaMines / Command_UpgradeEMPMines is replaced by
    Command_Evacuate.  Mines remain purchasable on every other Kwai
    structure; Sell, all 12 production buttons incl. kwai-artillery's
    slots 11-12 are preserved (emperor-bunker rule: Evacuate is the
    priority; never sacrifice Sell/production/sibling buttons).
  - Propaganda Center: Evacuate at slot 12 in ALL 50 sets (2 base +
    kwai-doctrine's 48 state sets; slot 12 verified free in every one,
    13/14 = mines/Sell).  No exits.
  - Power Plant: its sets (ChinaPowerPlantCommandSet/+Upgrade) are
    SHARED with vanilla China's power plant, so they must not change
    (doctrine's shared-file rule).  Instead two NEW Kwai-only sets
    Tank_ChinaPowerPlantCommandSet/+Upgrade are appended (Overcharge 1,
    exits 2-11, Evacuate 12, mines 13, Sell 14) and PowerPlant.ini's two
    set references are retargeted (2 single-occurrence exact line swaps,
    the kwai-bunkers Dozer idiom).

All buttons are existing ShockWave buttons -- no CommandButton.ini,
Generals.str, Upgrade.ini or Weapon.ini changes.  No AI wiring.

Packaging: zzz-ZZZKwaiGarrisons.big.  Case-insensitively
'zzz-zzk...' < 'zzz-zzz...' puts it AFTER zzz-ZZKwaiBaseTech.big (whose
CommandSet.ini and building files it layers on) and '-' (0x2D) < '_'
(0x5F) puts it BEFORE zzz_ControlBarPro*.big -- verified against the
real directory listings at build time.  Installed to both mod dirs.

Rebuild order: this is now the LAST INI layer.  If any lower layer
(kwai-basetech, kwai-bunkers, kwai-doctrine, stat-tune, ...) is rebuilt,
rebuild this archive afterwards.  Conversely kwai-basetech's own build
must not see this archive (its ownership asserts would fail): delete
zzz-ZZZKwaiGarrisons.big from both mod dirs first, rebuild kwai-basetech,
then rerun this build.
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
OUT_NAME = "zzz-ZZZKwaiGarrisons.big"
TAG = "zzz-ZZZKwaiGarrisons"

P = "Data\\INI\\Object\\China\\Tank\\Buildings\\"
CS_PATH = "Data\\INI\\CommandSet.ini"

OWNER = "zzz-ZZKwaiBaseTech.big"

# the 8 garrisoned buildings (path, object name)
BUILDINGS = [
    (P + "Airfield.ini",         "Tank_ChinaAirfield"),
    (P + "CommandCenter.ini",    "Tank_ChinaCommandCenter"),
    (P + "IndustrialPlant.ini",  "Tank_ChinaIndustrialPlant"),
    (P + "NuclearSilo.ini",      "Tank_ChinaNuclearMissileLauncher"),
    (P + "PowerPlant.ini",       "Tank_ChinaPowerPlant"),
    (P + "PropagandaCenter.ini", "Tank_ChinaPropagandaCenter"),
    (P + "SupplyCenter.ini",     "Tank_ChinaSupplyCenter"),
    (P + "WarFactory.ini",       "Tank_ChinaWarFactory"),
]
# skipped because they already carry a contain module (asserted below)
SKIPPED = [
    (P + "Barracks.ini",       "HealContain"),          # heal-up contain
    (P + "InternetCenter.ini", "InternetHackContain"),  # 30 hackers (stat-tune)
]

SHIPPED = [CS_PATH] + [p for p, _ in BUILDINGS]
OWNERS = {p: OWNER for p in SHIPPED}
for p, _ in SKIPPED:
    OWNERS[p] = OWNER  # read-only reference (skip validation), NOT shipped

NEW_SET_MAIN = "Tank_ChinaPowerPlantCommandSet"
NEW_SET_UPG = "Tank_ChinaPowerPlantCommandSetUpgrade"
NEW_NAMES = ("ModuleTag_KG_Garrison01", NEW_SET_MAIN, NEW_SET_UPG)

EXIT_BTN = "Command_StructureExit"
EVAC_BTN = "Command_Evacuate"


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


def replace_exact(s, old, new, count):
    assert s.count(old) == count, \
        "expected %d occurrences of %r, found %d" % (count, old[:80], s.count(old))
    return s.replace(old, new)


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def diff_multisets(src_lf, out_lf):
    d = unified(src_lf, out_lf)
    return (Counter(l[1:] for l in d if l.startswith("+")),
            Counter(l[1:] for l in d if l.startswith("-")))


def slot_fmt(n):
    """Match the neighbouring '  N = ' / ' NN = ' one-space slot style."""
    return ("  %d" if n < 10 else " %d") % n


def slot_fmt_wide(n):
    """Match the '  N  = ' / ' NN  = ' two-space slot style."""
    return ("  %d " % n) if n < 10 else (" %d " % n)


# ------------------------------------------------------- generated INI text
GARRISON_MODULE = (
    "  Behavior = GarrisonContain ModuleTag_KG_Garrison01 ; " + TAG +
    ": 10-man infantry garrison, fires out (GLAPalace/ChinaBunker idiom)\n"
    "    ContainMax                    = 10\n"
    "    EnterSound                    = GarrisonEnter\n"
    "    ExitSound                     = GarrisonExit\n"
    "    ImmuneToClearBuildingAttacks  = Yes\n"
    "  End\n"
)

# anchor: the basetech AutoHeal module tail, exactly once per building file
HEAL_TAIL = "    TriggeredBy   = Tank_Upgrade_KwaiAutoRepair\n  End\n"

PP_SET_OLD_MAIN = "  CommandSet          = ChinaPowerPlantCommandSet\n"
PP_SET_NEW_MAIN = "  CommandSet          = Tank_ChinaPowerPlantCommandSet ; " \
    + TAG + ": Kwai-only set (garrison exits); vanilla-shared set untouched\n"
PP_SET_OLD_UPG = "    CommandSet = ChinaPowerPlantCommandSetUpgrade\n"
PP_SET_NEW_UPG = "    CommandSet = Tank_ChinaPowerPlantCommandSetUpgrade ; " \
    + TAG + "\n"


def pp_set_text(mines_button):
    lines = ["  1 = Command_Overcharge"]
    for i in range(2, 12):
        lines.append("%s = %s" % (slot_fmt(i), EXIT_BTN))
    lines.append(" 12 = %s" % EVAC_BTN)
    lines.append(" 13 = %s" % mines_button)
    lines.append(" 14 = Command_Sell")
    return "\n".join(lines)


CS_APPENDIX = (
    "\n"
    ";;; " + TAG + ": Kwai-only Power Plant sets with garrison exit/evacuate\n"
    ";;; buttons.  The ChinaPowerPlantCommandSet pair is SHARED with vanilla\n"
    ";;; China's power plant and stays untouched.\n"
    "CommandSet " + NEW_SET_MAIN + "\n"
    + pp_set_text("Command_UpgradeChinaMines") + "\n"
    "End\n"
    "\n"
    "CommandSet " + NEW_SET_UPG + "\n"
    + pp_set_text("Command_UpgradeEMPMines") + "\n"
    "End\n"
)


# ------------------------------------------------- command-set patch engine
def exits_then_evac(first, last, evac, wide=False):
    """slot lines for contiguous StructureExit first..last + Evacuate."""
    fmt = slot_fmt_wide if wide else slot_fmt
    lines = ["%s = %s" % (fmt(i), EXIT_BTN) for i in range(first, last + 1)]
    lines.append("%s = %s" % (fmt(evac), EVAC_BTN))
    return lines


# (set name, op, anchor/old line, new lines)  -- ops are scoped to the set body
CS_SET_PATCHES = [
    ("Tank_ChinaCommandCenterCommandSet", "insert_after",
     "  ;4  = Command_NapalmStrike", ["  4  = " + EVAC_BTN]),
    ("Tank_ChinaCommandCenterCommandSetUpgrade", "insert_after",
     "  ;4  = Command_NapalmStrike", ["  4  = " + EVAC_BTN]),
    ("Tank_ChinaWarFactoryCommandSet", "replace_line",
     "  13 = Command_UpgradeChinaMines", ["  13 = " + EVAC_BTN]),
    ("Tank_ChinaWarFactoryCommandSetUpgrade", "replace_line",
     "  13 = Command_UpgradeEMPMines", ["  13 = " + EVAC_BTN]),
    ("Tank_ChinaSupplyCenterCommandSet", "insert_after",
     "  1 = Tank_Command_ConstructChinaVehicleSupplyTruck",
     exits_then_evac(2, 11, 12)),
    ("Tank_ChinaSupplyCenterCommandSetUpgrade", "insert_after",
     "  1 = Tank_Command_ConstructChinaVehicleSupplyTruck",
     exits_then_evac(2, 11, 12)),
    ("Tank_ChinaAirfieldCommandSet", "insert_after",
     "  2 = Tank_Command_ConstructChinaVehicleHelix",
     exits_then_evac(3, 9, 10)),
    ("Tank_ChinaAirfieldCommandSetUpgrade", "insert_after",
     "  2 = Tank_Command_ConstructChinaVehicleHelix",
     exits_then_evac(3, 9, 10)),
    ("Tank_ChinaIndustrialPlantCommandSet", "insert_after",
     "  2  = Tank_Command_UpgradeChinaAutoLoader",
     exits_then_evac(3, 11, 12, wide=True)),
    ("Tank_ChinaIndustrialPlantCommandSetUpgrade", "insert_after",
     "  2  = Tank_Command_UpgradeChinaAutoLoader",
     exits_then_evac(3, 11, 12, wide=True)),
    ("Tank_ChinaNuclearMissileCommandSet", "insert_after",
     "  1 = Command_NeutronMissile",
     exits_then_evac(2, 9, 10)),
    ("Tank_ChinaNuclearMissileCommandSetUpgrade", "insert_after",
     "  1 = Command_NeutronMissile",
     exits_then_evac(2, 9, 10)),
]

# global (multi-set) patch: Evacuate at slot 12 in all 50 prop-center sets
PC_SLOT11 = " 11  = Tank_Command_UpgradeKwaiBaseArmaments\n"
PC_NEW = " 12  = Command_Evacuate\n"


def patch_set_body(cs, set_name, op, target, new_lines):
    m = re.search(r"(?ms)^(CommandSet %s\n)(.*?)(^End)" % re.escape(set_name), cs)
    assert m, "command set not found: " + set_name
    body = m.group(2)
    assert body.count(target + "\n") == 1, (set_name, target)
    if op == "insert_after":
        new_body = body.replace(target + "\n",
                                target + "\n" + "".join(l + "\n" for l in new_lines))
    elif op == "replace_line":
        new_body = body.replace(target + "\n",
                                "".join(l + "\n" for l in new_lines))
    else:
        raise AssertionError(op)
    # the new buttons must not collide with occupied slots
    return cs[:m.start(2)] + new_body + cs[m.end(2):]


def patch_commandset(src):
    out = src
    for set_name, op, target, new_lines in CS_SET_PATCHES:
        out = patch_set_body(out, set_name, op, target, new_lines)
    out = replace_exact(out, PC_SLOT11, PC_SLOT11 + PC_NEW, 50)
    out = out + from_lf(CS_APPENDIX, eol_of(src))
    return out


def patch_building(raw, path, obj_name):
    eol = eol_of(raw)
    lf = to_lf(raw)
    assert re.search(r"(?m)^Object %s\b" % re.escape(obj_name), lf), \
        "%s: object %s not found" % (path, obj_name)
    assert len(re.findall(r"(?m)^Object ", lf)) == 1, path
    lf = replace_exact(lf, HEAL_TAIL, HEAL_TAIL + GARRISON_MODULE, 1)
    if path.endswith("PowerPlant.ini"):
        lf = replace_exact(lf, PP_SET_OLD_MAIN, PP_SET_NEW_MAIN, 1)
        lf = replace_exact(lf, PP_SET_OLD_UPG, PP_SET_NEW_UPG, 1)
    return from_lf(lf, eol)


# -------------------------------------------------------------- verification
def parse_sets(cs_lf, strict_names=()):
    """name -> {slot: button} for every CommandSet block; duplicate-slot
    asserts are limited to strict_names (sets this mod touches)."""
    sets = {}
    for m in re.finditer(r"(?ms)^CommandSet (\S+)\n(.*?)^End", cs_lf):
        slots = {}
        for sm in re.finditer(r"(?m)^\s*(\d+)\s*=\s*(\S+)", m.group(2)):
            n = int(sm.group(1))
            if m.group(1) in strict_names:
                assert n not in slots, "duplicate slot %d in %s" % (n, m.group(1))
            slots[n] = sm.group(2)
        sets[m.group(1)] = slots
    return sets


def verify_garrison_sets(cs):
    """Every garrisoned building's sets: Evacuate reachable, exits contiguous."""
    lf = to_lf(cs)
    expect = {
        # set name: (exit slots, evacuate slot)
        "Tank_ChinaCommandCenterCommandSet": ([], 4),
        "Tank_ChinaCommandCenterCommandSetUpgrade": ([], 4),
        "Tank_ChinaWarFactoryCommandSet": ([], 13),
        "Tank_ChinaWarFactoryCommandSetUpgrade": ([], 13),
        "Tank_ChinaSupplyCenterCommandSet": (list(range(2, 12)), 12),
        "Tank_ChinaSupplyCenterCommandSetUpgrade": (list(range(2, 12)), 12),
        "Tank_ChinaAirfieldCommandSet": (list(range(3, 10)), 10),
        "Tank_ChinaAirfieldCommandSetUpgrade": (list(range(3, 10)), 10),
        "Tank_ChinaIndustrialPlantCommandSet": (list(range(3, 12)), 12),
        "Tank_ChinaIndustrialPlantCommandSetUpgrade": (list(range(3, 12)), 12),
        "Tank_ChinaNuclearMissileCommandSet": (list(range(2, 10)), 10),
        "Tank_ChinaNuclearMissileCommandSetUpgrade": (list(range(2, 10)), 10),
        NEW_SET_MAIN: (list(range(2, 12)), 12),
        NEW_SET_UPG: (list(range(2, 12)), 12),
    }
    # all 50 prop-center sets: Evacuate at 12, no exits
    sets = parse_sets(lf)
    for name in sets:
        if name.startswith("Tank_ChinaPropagandaCenter"):
            expect[name] = ([], 12)
    sets = parse_sets(lf, strict_names=frozenset(expect))
    pc = [n for n in expect if n.startswith("Tank_ChinaPropagandaCenter")]
    assert len(pc) == 50, "prop-center set count %d" % len(pc)

    for name, (exits, evac) in expect.items():
        slots = sets[name]
        got_exits = sorted(n for n, b in slots.items() if b == EXIT_BTN)
        assert got_exits == exits, (name, got_exits, exits)
        if exits:  # contiguity (engine doTransportInventoryUI requirement)
            assert got_exits == list(range(got_exits[0], got_exits[-1] + 1)), name
            # Evacuate directly after the exit run, nothing interleaved
            assert evac == got_exits[-1] + 1, name
        assert slots.get(evac) == EVAC_BTN, (name, evac, slots.get(evac))
        assert max(slots) <= 14, (name, "slot beyond the 14 UI windows")
        # Sell survives wherever it existed (every building set has it)
        if not name.startswith("Tank_ChinaCommandCenterTaunt"):
            assert slots.get(14, "Command_Sell").startswith("Command_Sell"), name
    # the sacrificed WF mines buttons are gone from WF only
    assert sets["Tank_ChinaWarFactoryCommandSet"].get(13) == EVAC_BTN
    assert sets["Tank_ChinaWarFactoryCommandSetUpgrade"].get(13) == EVAC_BTN
    # vanilla-shared power plant sets byte-untouched is asserted separately
    print("  garrison sets OK (evacuate reachable everywhere, exits contiguous,"
          " %d prop-center sets at slot 12)" % len(pc))


def verify_cs_survival(cs, src_lf=None):
    """Every sibling layer's machinery must survive on the final bytes."""
    checks = {
        ("Kwai artillery factory slots 11-12 (both variants)", 2):
            "  11 = Tank_Command_ConstructChinaVehicleInfernoCannon\n"
            "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n",
        ("prop-center artillery slots 4-5 (50 sets)", 50):
            "  4  = Command_UpgradeChinaChainGuns\n"
            "  5  = Command_UpgradeChinaBlackNapalm\n",
        ("doctrine slots 8-9 + basetech 10-11 + garrison 12 (50 sets)", 50):
            "  8  = Tank_Command_UpgradeKwaiTungstenShells\n"
            "  9  = Tank_Command_UpgradeKwaiInfantryDoctrine\n"
            " 10  = Tank_Command_UpgradeKwaiAutoRepair\n"
            " 11  = Tank_Command_UpgradeKwaiBaseArmaments\n"
            " 12  = Command_Evacuate\n",
        ("doctrine 48 appended state sets", 48):
            "CommandSet Tank_ChinaPropagandaCenterCS_M",
        ("Mammoth slots 4-8", 1):
            "  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n"
            "  8  = Command_Evacuate\n",
        ("Tank Battlemaster exit/prop-tower", 1):
            "CommandSet Tank_ChinaVehicleBattleMasterCommandSet\n"
            "  1  = Command_TransportExit\n"
            "  2  = Command_TransportExit\n"
            "  3  = Command_TransportExit\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_Evacuate\n"
            "  10 = Command_UpgradeChinaOverlordPropagandaTower\n",
        ("Tank Battlemaster ERA set", 1):
            "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n",
        ("Emperor bunker set (exits 2-9, gattling 10, evacuate 12)", 1):
            "CommandSet Tank_ChinaTankEmperorDefaultCommandSet\n"
            "  1  = Command_OverlordTaunt\n"
            "  2  = Command_TransportExit\n"
            "  3  = Command_TransportExit\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n"
            "  8  = Command_TransportExit\n"
            "  9  = Command_TransportExit\n"
            "  10 = Tank_Command_UpgradeChinaOverlordGattlingCannon\n"
            "  11 = Command_AttackMove\n"
            "  12 = Command_Evacuate\n"
            "  13 = Command_Guard\n"
            "  14 = Command_Stop\n"
            "End\n",
        ("Kwai dozer page 1 (bunkers page-flip) intact", 1):
            "CommandSet Tank_ChinaDozerCommandSet\n"
            "  1  = Tank_Command_ConstructChinaPowerPlant\n"
            "  2  = Tank_Command_ConstructChinaInternetCenter\n"
            "  3  = Tank_Command_ConstructChinaBarracks\n"
            "  4  = Tank_Command_ConstructChinaAirfield\n"
            "  5  = Tank_Command_ConstructChinaSupplyCenter\n"
            "  6  = Tank_Command_ConstructChinaPropagandaCenter\n"
            "  7  = Tank_Command_ConstructChinaSentryTower\n"
            "  8  = Tank_Command_ConstructChinaSpeakerTower\n"
            "  9  = Tank_Command_ConstructChinaGattlingCannon\n"
            " 10  = Tank_Command_ConstructChinaNuclearMissileLauncher\n"
            " 11  = Tank_Command_ConstructChinaWarFactory\n"
            " 12  = Tank_Command_ConstructChinaCommandCenter\n"
            " 13  = Command_ChinaButtonCommandSetOneDown\n"
            " 14  = Command_DisarmMinesAtPosition\nEnd\n",
        ("Kwai dozer page 2 (bunkers)", 1):
            "CommandSet Tank_ChinaDozerCommandSet_Down\n"
            "  1  = Tank_Command_ConstructChinaIndustrialPlant\n"
            "  7  = Tank_Command_ConstructChinaBunker\n"
            "  8  = Tank_Command_ConstructChinaHackerBunker\n",
        ("Hacker Bunker set (bunkers)", 1):
            "CommandSet Tank_ChinaHackerBunkerCommandSet\n",
        ("vanilla China dozer pages untouched", 1):
            "CommandSet ChinaDozerCommandSet_Down\n",
        ("vanilla prop-center sets untouched (no slot 10)", 1):
            "CommandSet ChinaPropagandaCenterCommandSet\n"
            "  1  = Command_UpgradeChinaNationalism\n"
            "  2  = Command_UpgradeChinaAutoLoader\n",
        # vanilla-SHARED power plant sets stay byte-identical (leak guard)
        ("vanilla-shared power plant set untouched", 1):
            "CommandSet ChinaPowerPlantCommandSet\n"
            "  1 = Command_Overcharge\n"
            " 13 = Command_UpgradeChinaMines\n",
        ("vanilla-shared power plant upgrade set untouched", 1):
            "CommandSet ChinaPowerPlantCommandSetUpgrade\n"
            "  1 = Command_Overcharge\n"
            " 13 = Command_UpgradeEMPMines\n",
        ("new Kwai power plant sets present", 1):
            "CommandSet " + NEW_SET_MAIN + "\n",
        ("Barracks set untouched (skipped building)", 1):
            "CommandSet Tank_ChinaBarracksCommandSet\n"
            "  1 = Tank_Command_ConstructChinaInfantryRedguard\n",
    }
    for (label, count), needle in checks.items():
        assert cs.count(needle) == count, \
            "CS SURVIVAL FAILED: %s (found %d, want %d)" % (
                label, cs.count(needle), count)
        print("  commandset OK:", label)


def expected_cs_added():
    add = Counter()
    for _, op, target, new_lines in CS_SET_PATCHES:
        for l in new_lines:
            add[l] += 1
    add[PC_NEW.rstrip("\n")] += 50
    # the appendix's leading "\n" creates one blank line after the old EOF
    for l in CS_APPENDIX.rstrip("\n").split("\n"):
        add[l] += 1
    return add


def expected_cs_removed():
    rem = Counter()
    for _, op, target, _ in CS_SET_PATCHES:
        if op == "replace_line":
            rem[target] += 1
    return rem


def verify_building(shipped, path, obj_name):
    lf = to_lf(shipped)
    assert lf.count("ModuleTag_KG_Garrison01") == 1, path
    assert lf.count("    ContainMax                    = 10\n") == 1, path
    assert "ImmuneToClearBuildingAttacks  = Yes" in lf, path
    # exactly one contain module on the final object
    contains = re.findall(r"(?m)^\s*Behavior\s*=\s*(\w*Contain)\b", lf)
    assert contains == ["GarrisonContain"], (path, contains)
    # basetech machinery survives
    assert lf.count("ModuleTag_KBT_Heal01") == 1, path
    assert "TriggeredBy   = Tank_Upgrade_KwaiAutoRepair\n" in lf, path
    # doctrine armor tiers survive with their triggers
    for i in (1, 2, 3, 4):
        assert ("ModuleTag_KD_Armor%d" % i) in lf, (path, i)
        assert ("Tank_Upgrade_KwaiVehicleArmor%d" % i) in lf, (path, i)
    # basetech armed-building machinery (5 of the 8)
    armed = obj_name in ("Tank_ChinaCommandCenter", "Tank_ChinaPowerPlant",
                         "Tank_ChinaPropagandaCenter", "Tank_ChinaSupplyCenter",
                         "Tank_ChinaWarFactory")
    if armed:
        assert lf.count("ModuleTag_KBT_Arm01") == 1, path
        assert lf.count("ModuleTag_KBT_AI01") == 1, path
        assert lf.count("  WeaponSet\n") == 2, path
        assert "Weapon              = PRIMARY Tank_KwaiBaseArmamentsGun\n" in lf, path
    else:
        assert "ModuleTag_KBT_Arm01" not in lf and "ModuleTag_KBT_AI01" not in lf, path
    # production module survives (contain+production coexistence targets)
    assert re.search(r"(?m)^\s*Behavior\s*=\s*ProductionUpdate\b", lf), path
    if path.endswith("PowerPlant.ini"):
        assert "CommandSet          = Tank_ChinaPowerPlantCommandSet ;" in lf, path
        assert "CommandSet = Tank_ChinaPowerPlantCommandSetUpgrade ;" in lf, path
        assert "= ChinaPowerPlantCommandSet\n" not in lf, path
        assert "= ChinaPowerPlantCommandSetUpgrade\n" not in lf, path
    if path.endswith("Airfield.ini"):
        assert "ParkingPlaceBehavior" in lf, path  # aircraft parking intact
    if path.endswith("SupplyCenter.ini"):
        assert "SpawnBehavior" in lf, path  # supply trucks intact
    # block balance: every End matches (crude but effective: no drift vs source
    # is asserted through the diff audit; here assert Object block closes)
    assert lf.rstrip().endswith("End"), path


# ---------------------------------------------------------------------- main
def main():
    archives = sorted((f for f in os.listdir(SPE_DIR)
                       if f.lower().endswith(".big")
                       and f.lower() != OUT_NAME.lower()),  # never self-source
                      key=str.lower, reverse=True)
    cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}

    def effective(path):
        want = path.lower()
        for a in archives:
            for e in cache[a]:
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        return None, None

    sources = {}
    for path, owner in OWNERS.items():
        data, got = effective(path)
        assert data is not None, "effective source not found: " + path
        assert got == owner, "ownership drift for %s: %s (expected %s)" % (
            path, got, owner)
        sources[path] = data
    print("effective-file ownership verified (%d files, all %s)"
          % (len(sources), OWNER))

    # new identifiers must be unused across the WHOLE effective INI space
    seen_ini = {}
    for a in archives:
        for e in cache[a]:
            pl = e.path.lower()
            if pl.startswith("data\\ini\\") and pl.endswith(".ini") and pl not in seen_ini:
                seen_ini[pl] = e.data
    for name in NEW_NAMES:
        for pl, data in seen_ini.items():
            assert name.encode("latin-1") not in data, (name, pl)
    print("new identifiers are collision-free across the effective INI space "
          "(%d files)" % len(seen_ini))

    # target buildings must have NO existing contain module
    for path, obj in BUILDINGS:
        assert not re.search(r"(?m)^\s*Behavior\s*=\s*\w*Contain\b",
                             to_lf(sources[path])), path + ": already has a contain"
    # ... and the skip list must be skipped for the documented reason
    for path, contain in SKIPPED:
        assert re.search(r"(?m)^\s*Behavior\s*=\s*%s\b" % contain,
                         to_lf(sources[path])), \
            path + ": expected " + contain + " (skip reason drifted)"
    print("contain-module freedom verified on all 8 targets; "
          "Barracks=HealContain / InternetCenter=InternetHackContain skips confirmed")

    # required buttons all pre-exist in the effective CommandButton.ini
    cb, cb_owner = effective("Data\\INI\\CommandButton.ini")
    for btn in (EXIT_BTN, EVAC_BTN, "Command_Overcharge", "Command_Sell",
                "Command_UpgradeChinaMines", "Command_UpgradeEMPMines"):
        assert re.search(r"(?m)^CommandButton %s\s*$" % btn, to_lf(cb)), btn
    m = re.search(r"(?ms)^CommandButton %s\s*$.*?^End" % EXIT_BTN, to_lf(cb))
    assert "Command       = EXIT_CONTAINER" in m.group(0)
    m = re.search(r"(?ms)^CommandButton %s\s*?\n.*?^End" % EVAC_BTN, to_lf(cb))
    assert "Command                 = EVACUATE" in m.group(0)
    print("all referenced buttons pre-exist in CommandButton.ini (%s); "
          "no button/string/upgrade/weapon changes shipped" % cb_owner)

    # ---- build the shipped files
    patched = {CS_PATH: patch_commandset(sources[CS_PATH])}
    for path, obj in BUILDINGS:
        patched[path] = patch_building(sources[path], path, obj)
        print("  %-34s + GarrisonContain 10" % obj)

    # ---- CommandSet.ini diff audit
    add, rem = diff_multisets(to_lf(sources[CS_PATH]), to_lf(patched[CS_PATH]))
    assert rem == expected_cs_removed(), ("CS removals", rem - expected_cs_removed(),
                                          expected_cs_removed() - rem)
    assert add == expected_cs_added(), ("CS additions", add - expected_cs_added(),
                                        expected_cs_added() - add)
    n_add = sum(add.values())
    print("CommandSet.ini diff audit OK (%d lines added, exactly the 2 WF mines "
          "lines replaced, nothing else removed)" % n_add)

    # ---- building-file diff audits
    mod_lines = Counter(GARRISON_MODULE.rstrip("\n").split("\n"))
    for path, obj in BUILDINGS:
        add, rem = diff_multisets(to_lf(sources[path]), to_lf(patched[path]))
        exp_add, exp_rem = Counter(mod_lines), Counter()
        if path.endswith("PowerPlant.ini"):
            exp_add[PP_SET_NEW_MAIN.rstrip("\n")] += 1
            exp_add[PP_SET_NEW_UPG.rstrip("\n")] += 1
            exp_rem[PP_SET_OLD_MAIN.rstrip("\n")] += 1
            exp_rem[PP_SET_OLD_UPG.rstrip("\n")] += 1
        assert add == exp_add, (path, add - exp_add, exp_add - add)
        assert rem == exp_rem, (path, rem, exp_rem)
    print("building-file diff audits OK (8 files: garrison block insertion only; "
          "PowerPlant also the 2 command-set line retargets)")

    # ---- content + survival verification on final text
    verify_garrison_sets(patched[CS_PATH])
    verify_cs_survival(patched[CS_PATH])
    for path, obj in BUILDINGS:
        verify_building(patched[path], path, obj)
    print("  building content OK (single GarrisonContain each; basetech heal/arm/AI,"
          " doctrine tiers, production modules survive)")

    # ---- package
    entries = [BigEntry(path, patched[path].encode("latin-1"))
               for path in sorted(SHIPPED)]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_local)
    print("wrote %s (%d files, %d bytes)"
          % (out_local, len(entries), os.path.getsize(out_local)))

    # ---- sort-order verification against the real directory listings
    for d in (SPE_DIR, SHW_DIR):
        listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                         | {OUT_NAME}, key=str.lower)
        i = listing.index(OUT_NAME)
        after = listing[i - 1]
        before = listing[i + 1] if i + 1 < len(listing) else None
        assert after.lower() == "zzz-zzkwaibasetech.big", listing
        assert before and before.lower().startswith("zzz_controlbarpro"), listing
        print("sort order OK in %s: %s < %s < %s" % (d, after, OUT_NAME, before))

    # ---- install + re-read verification
    blob = open(out_local, "rb").read()
    for d in (SPE_DIR, SHW_DIR):
        dst = os.path.join(d, OUT_NAME)
        with open(dst, "wb") as f:
            f.write(blob)
        back = read_big(dst)
        assert [e.path for e in back] == [e.path for e in entries]
        for x, y in zip(back, entries):
            assert x.data == y.data, x.path
        cs_back = find_entry(back, CS_PATH).data.decode("latin-1")
        verify_garrison_sets(cs_back)
        verify_cs_survival(cs_back)
        for path, obj in BUILDINGS:
            verify_building(find_entry(back, path).data.decode("latin-1"), path, obj)
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
