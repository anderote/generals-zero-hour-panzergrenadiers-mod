#!/usr/bin/env python3
"""Build zzz-ZKwaiBunkers.big — two dozer-buildable structures for Kwai
(China Tank General), ShockWave under GeneralsX.

A. DEFENSE (TANK) BUNKER construct button.
   Tank_ChinaBunker (Data\\INI\\Object\\China\\Tank\\Defences\\Bunker.ini,
   3000 HP with stat-tune's 2x, holds 1 vehicle that fires out) has existed
   in ShockWave's data all along, together with a finished construct button
   Tank_Command_ConstructChinaBunker (DOZER_CONSTRUCT, cameo SNTankBunker,
   strings all present in Generals.str) — but the button is referenced by
   NO command set, so Kwai could never build it.  Every other China general
   has his bunker on dozer slot 7; Kwai's slot 7 is the Sentry Tower and
   ALL 14 UI slots of Tank_ChinaDozerCommandSet are occupied (engine
   MAX_COMMANDS_PER_SET = 18 but "user interface max is 14",
   ControlBar.h:411; both !Shw_wnd.big and zzz_ControlBarProZH.big define
   ButtonCommand01..14 only — verified).  So this mod adds a SECOND PAGE
   to Kwai's dozer using the vanilla-China dozer page-flip idiom
   (ChinaDozerCommandSet slot 13 <-> ChinaDozerCommandSet_Down; two
   CommandSetUpgrade modules keyed on the free instant OBJECT upgrades
   Upgrade_GLAWorkerFakeCommandSet / Upgrade_GLAWorkerRealCommandSet with
   RemovesUpgrades cross-clearing, plus ProductionUpdate MaxQueueEntries=1
   so OBJECT_UPGRADE buttons can queue — copied field-for-field from
   Data\\INI\\Object\\China\\Vanilla\\Vehicles\\Dozer.ini):
     page 1: slots 1-12 and 14 unchanged; 13 Industrial Plant -> page-down
     page 2 (Tank_ChinaDozerCommandSet_Down):
       1 Industrial Plant (relocated) . 7 Tank Bunker (the generals-wide
       bunker slot) . 8 Hacker Bunker (new, below) . 13 page-up .
       14 disarm mines

B. HACKER BUNKER (new object Tank_ChinaHackerBunker, new file
   Data\\INI\\Object\\China\\Tank\\Defences\\HackerBunker.ini — the engine
   loads Data\\INI\\Object with subdirs=TRUE, GameEngine.cpp:673 +
   INI::loadFileDirectory, so new INI paths inside a .big are picked up).
   Derived textually from Kwai's Tank_ChinaBunker (keeps his 2x-health
   3000 HP body, FireBaseArmor, bunker art/sounds/geometry and the four
   zzz-KwaiDoctrine MaxHealthUpgrade tiers) with:
     - GarrisonContain replaced by InternetHackContain (engine: subclass of
       TransportContain whose only override is onContaining ->
       rider->getAI()->aiHackInternet(CMD_FROM_AI), i.e. hackers
       auto-resume hacking inside; InternetHackContain.cpp:80-86).
       Contained hackers use CashUpdateDelayFast — 1600 ms vs 2000 ms
       outside (HackInternetAIUpdate.cpp getCashUpdateDelay, hacker INI) —
       a ~25% cash-rate bonus, exactly like the Internet Center.
       Fields mirror Tank_ChinaInternetCenter's module but Slots = 4,
       AllowInsideKindOf = MONEY_HACKER, PassengersAllowedToFire = No
       (hackers are unarmed anyway).  NumberOfExitPaths = 1: the NBTnkBnk
       model has no ExitStart/ExitEnd bones, but the engine falls back to
       the object position (Object.cpp:6141-6155) and
       adjustToPossibleDestination walks the rider out — same degenerate
       path many boneless containers rely on.
     - CAN_ATTACK / SPAWNS_ARE_THE_WEAPONS / GARRISONABLE_UNTIL_DESTROYED
       etc. dropped from KindOf; HiveStructureBody -> StructureBody.
     - mines / EMP-mines / auto-heal / mines command-set-swap modules
       dropped (keeps the object orthogonal to the doctrine state machine).
     - BuildCost 1000, BuildTime 15 s, prerequisite Tank_ChinaBarracks
       (the building that trains his hackers).
     - own command set: 4 x Command_StructureExit, Command_Evacuate, Sell.
     - construct button reuses the Internet Center cameo (SNIntCnt);
       3 new strings appended to Generals.str (append-only, base bytes
       untouched — ShockWave's effective string source per kwai-doctrine).

Packaging: zzz-ZKwaiBunkers.big.  Case-insensitive sort: '-' (0x2D) < '_'
(0x5F) puts it BEFORE zzz_ControlBarPro*.big, and 'k' < 'z' within the
"zzz-" group puts it AFTER zzz-KwaiDoctrine.big — so this archive layers
on the doctrine copies of CommandSet.ini / CommandButton.ini /
Generals.str / Dozer.ini (all owner-asserted) and owns everything it
ships.  Installed to both mod dirs.

Rebuild order: kwai-doctrine must be rebuilt BEFORE this mod (this mod
embeds full patched copies of doctrine-owned files).  Conversely
kwai-doctrine's own build must not see this archive: its ownership asserts
would (correctly, loudly) fail — remove zzz-ZKwaiBunkers.big first, then
rebuild doctrine, then rebuild this.
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
OUT_NAME = "zzz-ZKwaiBunkers.big"
TAG = "zzz-ZKwaiBunkers"

P = "Data\\INI\\Object\\China\\"
CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
STR_PATH = "Data\\Generals.str"
DOZER_PATH = P + "Tank\\Vehicles\\Dozer.ini"
BUNKER_PATH = P + "Tank\\Defences\\Bunker.ini"          # source only
IC_PATH = P + "Tank\\Buildings\\InternetCenter.ini"     # reference only
UPGRADE_PATH = "Data\\INI\\Upgrade.ini"                 # reference only
HACKERBUNKER_PATH = P + "Tank\\Defences\\HackerBunker.ini"  # NEW file

OWNER = "zzz-KwaiDoctrine.big"
OWNERS = {
    CS_PATH: OWNER,
    CB_PATH: OWNER,
    STR_PATH: OWNER,
    DOZER_PATH: OWNER,
    BUNKER_PATH: OWNER,
    IC_PATH: OWNER,
    UPGRADE_PATH: OWNER,
}
SHIPPED = [CS_PATH, CB_PATH, STR_PATH, DOZER_PATH, HACKERBUNKER_PATH]

NEW_OBJ = "Tank_ChinaHackerBunker"
NEW_BTN = "Tank_Command_ConstructChinaHackerBunker"
BUNKER_BTN = "Tank_Command_ConstructChinaBunker"
NEW_SET = "Tank_ChinaHackerBunkerCommandSet"
DOWN_SET = "Tank_ChinaDozerCommandSet_Down"
PAGE_DOWN_BTN = "Command_ChinaButtonCommandSetOneDown"
PAGE_UP_BTN = "Command_ChinaButtonCommandSetOneUp"
UPG_FAKE = "Upgrade_GLAWorkerFakeCommandSet"
UPG_REAL = "Upgrade_GLAWorkerRealCommandSet"


# ------------------------------------------------------------------ helpers
def replace_once(s, old, new):
    assert s.count(old) == 1, "expected exactly 1 occurrence of %r..." % old[:90]
    return s.replace(old, new)


def remove_block(s, first_line):
    """Remove an INI block starting with first_line (2-space indent) through
    its matching 2-space 'End' line, plus one trailing blank line if any."""
    assert s.count(first_line) == 1, first_line
    i = s.index(first_line)
    m = re.compile(r"(?m)^  End[ \t]*$").search(s, i)
    assert m, "unterminated block: " + first_line
    j = m.end()
    while j < len(s) and s[j] in "\r\n":
        j += 1
        if s[j - 1] == "\n":
            break
    # swallow at most one following blank line
    k = j
    while k < len(s) and s[k] in " \t":
        k += 1
    if k < len(s) and s[k] in "\r\n":
        j = k + (2 if s[k:k + 2] == "\r\n" else 1)
    return s[:i] + s[j:], s[i:j]


def eol_of(txt):
    return "\r\n" if "\r\n" in txt else "\n"


def with_eol(block_lf, eol):
    return block_lf.replace("\n", eol) if eol != "\n" else block_lf


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


# ------------------------------------------------------- generated INI text
CS_APPENDIX = """
; zzz-ZKwaiBunkers: Kwai dozer page 2 (vanilla-China page-flip idiom) and
; the Hacker Bunker structure set.  The dozer page sets are swapped by two
; CommandSetUpgrade modules on Tank_ChinaVehicleDozer keyed on the free
; instant OBJECT upgrades Upgrade_GLAWorkerFake/RealCommandSet.

CommandSet Tank_ChinaDozerCommandSet_Down
  1  = Tank_Command_ConstructChinaIndustrialPlant
  7  = Tank_Command_ConstructChinaBunker
  8  = Tank_Command_ConstructChinaHackerBunker
 13  = Command_ChinaButtonCommandSetOneUp
 14  = Command_DisarmMinesAtPosition
End

CommandSet Tank_ChinaHackerBunkerCommandSet
  1  = Command_StructureExit
  2  = Command_StructureExit
  3  = Command_StructureExit
  4  = Command_StructureExit
  5  = Command_Evacuate
 14  = Command_Sell
End
"""

CB_APPENDIX = """
;;; zzz-ZKwaiBunkers: Kwai Hacker Bunker construct button
;;; (the Tank Bunker button Tank_Command_ConstructChinaBunker already
;;;  exists above - ShockWave shipped it wired to no command set)

CommandButton Tank_Command_ConstructChinaHackerBunker
  Command       = DOZER_CONSTRUCT
  UnitSpecificSound = MoneyWithdraw
  Object        = Tank_ChinaHackerBunker
  TextLabel     = CONTROLBAR:ConstructChinaTankHackerBunker
  ButtonImage   = SNIntCnt
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildTankHackerBunker
End
"""

STR_APPENDIX = (
    "\n\nOBJECT:TankHackerBunker\n"
    "\"Hacker Bunker\"\nEND"
    "\n\nCONTROLBAR:ConstructChinaTankHackerBunker\n"
    "\"&Hacker Bunker\"\nEND"
    "\n\nCONTROLBAR:ToolTipChinaBuildTankHackerBunker\n"
    "\"Fortified post for up to 4 Hackers, who keep hacking the Internet"
    " inside at increased speed. \\n Cannot be entered by other units.\"\nEND"
)

DOZER_MODULES = (
    "  Behavior = CommandSetUpgrade ModuleTag_KB_Page01 ; zzz-ZKwaiBunkers: flip to dozer page 2\n"
    "    TriggeredBy = Upgrade_GLAWorkerFakeCommandSet\n"
    "    RemovesUpgrades = Upgrade_GLAWorkerRealCommandSet\n"
    "    CommandSet = Tank_ChinaDozerCommandSet_Down\n"
    "  End\n"
    "  Behavior = CommandSetUpgrade ModuleTag_KB_Page02 ; zzz-ZKwaiBunkers: flip back to dozer page 1\n"
    "    TriggeredBy = Upgrade_GLAWorkerRealCommandSet\n"
    "    RemovesUpgrades = Upgrade_GLAWorkerFakeCommandSet Upgrade_GLAWorkerRealCommandSet\n"
    "    CommandSet = Tank_ChinaDozerCommandSet\n"
    "  End\n"
    "  Behavior = ProductionUpdate ModuleTag_KB_Page03 ; zzz-ZKwaiBunkers: lets the OBJECT_UPGRADE page buttons queue\n"
    "    MaxQueueEntries = 1; For the command set switching upgrade\n"
    "  End\n"
)

HACK_CONTAIN = (
    "  Behavior = InternetHackContain ModuleTag_KB_Hack01 ; zzz-ZKwaiBunkers: passengers auto-hack for cash (fast contained rate)\n"
    "    PassengersAllowedToFire = No\n"
    "    Slots                 = 4\n"
    "    ScatterNearbyOnExit   = No\n"
    "    HealthRegen%PerSec    = 10\n"
    "    DamagePercentToUnits  = 50%\n"
    "    AllowInsideKindOf     = MONEY_HACKER\n"
    "    EnterSound            = GarrisonEnter\n"
    "    ExitSound             = GarrisonExit\n"
    "    ExitDelay             = 500\n"
    "    NumberOfExitPaths     = 1 ; no ExitStart/ExitEnd bones in NBTnkBnk; engine falls back to object position\n"
    "    GoAggressiveOnExit    = No\n"
    "  End\n"
)


# ------------------------------------------------------------- file patches
def patch_commandset(txt):
    txt = replace_once(
        txt,
        " 12  = Tank_Command_ConstructChinaCommandCenter\n"
        " 13  = Tank_Command_ConstructChinaIndustrialPlant\n"
        " 14  = Command_DisarmMinesAtPosition\n",
        " 12  = Tank_Command_ConstructChinaCommandCenter\n"
        " 13  = Command_ChinaButtonCommandSetOneDown\n"
        " 14  = Command_DisarmMinesAtPosition\n")
    return txt + CS_APPENDIX


def patch_dozer(txt):
    eol = eol_of(txt)
    anchor = "  Behavior = DozerAIUpdate ModuleTag_03" + eol
    ins = with_eol(DOZER_MODULES, eol)
    return replace_once(txt, anchor, ins + anchor)


def make_hacker_bunker(bunker_txt):
    """Derive the Tank_ChinaHackerBunker INI from the effective (doctrine)
    Tank_ChinaBunker text.  All edits are exact-match, single-occurrence."""
    eol = eol_of(bunker_txt)
    t = bunker_txt.replace("\r\n", "\n")

    t = replace_once(t, "Object Tank_ChinaBunker\n",
                     "; %s: Kwai Hacker Bunker - derived from Tank_ChinaBunker\n"
                     "; (keeps the 2x-health body, armor, art and the doctrine armor tiers;\n"
                     ";  garrison contain replaced by InternetHackContain)\n"
                     "Object %s\n" % (TAG, NEW_OBJ))
    t = replace_once(t, "  ButtonImage            = SNTankBunker\n",
                     "  ButtonImage            = SNIntCnt ; %s: internet-center cameo\n" % TAG)
    t = replace_once(t, "  DisplayName       = OBJECT:TankBunker\n",
                     "  DisplayName       = OBJECT:TankHackerBunker\n")
    t = replace_once(t, "    Object = Tank_ChinaWarFactory\n",
                     "    Object = Tank_ChinaBarracks ; %s: hackers come from the Barracks\n" % TAG)
    t = replace_once(t, "  BuildCost        = 200\n",
                     "  BuildCost        = 1000\n")
    t = replace_once(t, "  BuildTime        = 8.0           ; in seconds\n",
                     "  BuildTime        = 15.0          ; in seconds\n")
    t = replace_once(t, "  CommandSet        = ChinaTankBunkerCommandSet\n",
                     "  CommandSet        = %s\n" % NEW_SET)
    t = replace_once(
        t,
        "  KindOf          = PRELOAD STRUCTURE SELECTABLE CAN_ATTACK "
        "ATTACK_NEEDS_LINE_OF_SIGHT IMMOBILE SPAWNS_ARE_THE_WEAPONS SCORE "
        "FS_TECHNOLOGY FS_BASE_DEFENSE IMMUNE_TO_CAPTURE GARRISONABLE_UNTIL_DESTROYED\n",
        "  KindOf          = PRELOAD STRUCTURE SELECTABLE IMMOBILE SCORE "
        "FS_TECHNOLOGY FS_BASE_DEFENSE IMMUNE_TO_CAPTURE ; %s: non-combat contain structure\n" % TAG)
    t = replace_once(t, "  Body                 = HiveStructureBody ModuleTag_05;\n",
                     "  Body                 = StructureBody ModuleTag_05; %s: no slaved weapons\n" % TAG)
    # doctrine armor-tier comments now describe the derived object
    assert t.count(" for Tank_ChinaBunker\n") == 4
    t = t.replace(" for Tank_ChinaBunker\n", " for Tank_ChinaBunker (inherited)\n")

    # swap the garrison contain for the internet-hack contain
    garrison = (
        "  Behavior = GarrisonContain ModuleTag_07\n"
        "    ContainMax                    = 1\n"
        "    EnterSound                    = GarrisonEnter\n"
        "    ExitSound                     = GarrisonExit\n"
        "    ImmuneToClearBuildingAttacks  = Yes\n"
        "    DamagePercentToUnits          = 0%\n"
        "    IsEnclosingContainer          = No\n"
        "    AllowInsideKindOf             = VEHICLE CAN_ATTACK\n"
        "    ForbidInsideKindOf            = DOZER TRANSPORT AIRCRAFT HUGE_VEHICLE INFANTRY\n"
        "  End\n")
    t = replace_once(t, garrison, HACK_CONTAIN)

    # drop the mines family, the mines command-set swap, EMP armor and the
    # vehicle-repair aura — all bunker-specific
    removed = []
    for first in ("  Behavior = GenerateMinefieldBehavior     ModuleTag_09",
                  "  Behavior = CommandSetUpgrade ModuleTag_25",
                  "  Behavior = ArmorUpgrade ModuleTag_26",
                  "  Behavior = AutoHealBehavior ModuleTag_Repair01"):
        t, blk = remove_block(t, first)
        removed.append(blk)

    return with_eol(t, eol), removed


# -------------------------------------------------------------- verification
def verify_doctrine_survival(cs):
    """The kwai-doctrine 50-set state machine and every sibling needle it
    protects must be byte-identical in the shipped CommandSet.ini."""
    checks = {
        ("Kwai artillery factory slots 11-12 (both variants)", 2):
            "  11 = Tank_Command_ConstructChinaVehicleInfernoCannon\n"
            "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n",
        ("prop-center slots 4-5 (2 base + 48 state sets)", 50):
            "  4  = Command_UpgradeChinaChainGuns\n"
            "  5  = Command_UpgradeChinaBlackNapalm\n",
        ("doctrine slots 8-9 (2 base + 48 state sets)", 50):
            "  8  = Tank_Command_UpgradeKwaiTungstenShells\n"
            "  9  = Tank_Command_UpgradeKwaiInfantryDoctrine\n",
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
        ("Kwai dozer page 1 slots 1-12 intact", 1):
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
        ("vanilla China dozer pages untouched", 1):
            "CommandSet ChinaDozerCommandSet_Down\n",
    }
    for (label, count), needle in checks.items():
        assert cs.count(needle) == count, \
            "CS SURVIVAL FAILED: %s (found %d, want %d)" % (
                label, cs.count(needle), count)
        print("  commandset OK:", label)


def verify_hacker_bunker(hb):
    lf = hb.replace("\r\n", "\n")
    must = [
        "Object Tank_ChinaHackerBunker\n",
        "  Behavior = InternetHackContain ModuleTag_KB_Hack01",
        "    Slots                 = 4\n",
        "    AllowInsideKindOf     = MONEY_HACKER\n",
        "    PassengersAllowedToFire = No\n",
        "  BuildCost        = 1000\n",
        "  BuildTime        = 15.0",
        "    MaxHealth          = 3000\n",
        "    InitialHealth      = 3000\n",
        "    Armor           = FireBaseArmor\n",
        "  CommandSet        = Tank_ChinaHackerBunkerCommandSet\n",
        "    Object = Tank_ChinaBarracks",
        "  Body                 = StructureBody ModuleTag_05;",
        "  Behavior = ProductionUpdate ModuleTag_10\n",
        "  DisplayName       = OBJECT:TankHackerBunker\n",
    ]
    for n in must:
        assert n in lf, "HACKER BUNKER MISSING: " + n.strip()
    # the four doctrine armor tiers survived, with their triggers
    for i in (1, 2, 3, 4):
        assert ("ModuleTag_KD_Armor%d" % i) in lf
        assert ("Tank_Upgrade_KwaiVehicleArmor%d" % i) in lf
    forbidden = ["GarrisonContain", "GenerateMinefieldBehavior",
                 "ArmorUpgrade", "AutoHealBehavior", "CommandSetUpgrade",
                 "HiveStructureBody", "SPAWNS_ARE_THE_WEAPONS", "CAN_ATTACK",
                 "GARRISONABLE_UNTIL_DESTROYED", "ChinaTankBunkerCommandSet"]
    for n in forbidden:
        assert n not in lf, "HACKER BUNKER LEFTOVER: " + n
    assert not re.search(r"(?m)^Object Tank_ChinaBunker\s*$", lf)
    n_beh = sum(1 for l in lf.splitlines()
                if re.match(r"Behavior\s*=", l.strip()))
    assert n_beh == 11, "behavior count %d != 11" % n_beh
    print("  hacker bunker OK: contain/body/cost/prereq/tiers, %d behaviors" % n_beh)


def verify_cross_refs(cs, cb, s, hb, upgrade_src, dozer):
    # every command referenced by the two new sets exists in CommandButton.ini
    for b in ("Tank_Command_ConstructChinaIndustrialPlant", BUNKER_BTN,
              NEW_BTN, PAGE_UP_BTN, PAGE_DOWN_BTN,
              "Command_DisarmMinesAtPosition", "Command_StructureExit",
              "Command_Evacuate", "Command_Sell"):
        assert re.search(r"(?m)^CommandButton %s\s*$" % b, cb), \
            "button missing: " + b
    # the construct buttons point at objects that exist
    assert "Object        = Tank_ChinaHackerBunker\n" in cb
    assert "Object Tank_ChinaHackerBunker" in hb.replace("\r\n", "\n")
    # bunker button really is DOZER_CONSTRUCT at Tank_ChinaBunker
    m = re.search(r"(?ms)^CommandButton %s\s*$.*?^End" % BUNKER_BTN, cb)
    assert m and "DOZER_CONSTRUCT" in m.group(0) \
        and "Object        = Tank_ChinaBunker" in m.group(0)
    # page upgrades exist, are OBJECT type, free and instant
    for u in (UPG_FAKE, UPG_REAL):
        um = re.search(r"(?ms)^Upgrade %s\s*$.*?^End" % u,
                       upgrade_src.replace("\r\n", "\n"))
        assert um, "upgrade missing: " + u
        assert "Type               = OBJECT" in um.group(0)
        assert "BuildCost          = 0" in um.group(0)
        assert "BuildTime          = 0.0" in um.group(0)
    # dozer references both page sets and has the production update
    dlf = dozer.replace("\r\n", "\n")
    assert "    CommandSet = Tank_ChinaDozerCommandSet_Down\n" in dlf
    assert "    CommandSet = Tank_ChinaDozerCommandSet\n" in dlf
    assert "  Behavior = ProductionUpdate ModuleTag_KB_Page03" in dlf
    # both new sets defined exactly once; dozer page-2 wired
    assert cs.count("CommandSet %s\n" % DOWN_SET) == 1
    assert cs.count("CommandSet %s\n" % NEW_SET) == 1
    assert ("  7  = %s\n" % BUNKER_BTN) in cs
    assert ("  8  = %s\n" % NEW_BTN) in cs
    # strings for every new label; existing bunker-button labels present
    for lbl in ("OBJECT:TankHackerBunker",
                "CONTROLBAR:ConstructChinaTankHackerBunker",
                "CONTROLBAR:ToolTipChinaBuildTankHackerBunker",
                "CONTROLBAR:ConstructChinaTankBunker",
                "CONTROLBAR:ToolTipChinaBuildTankBunker",
                "OBJECT:TankBunker",
                "CONTROLBAR:OneUp", "CONTROLBAR:OneDown"):
        assert ("\n%s\n" % lbl) in s, "missing string: " + lbl
    print("  cross-reference closure OK (buttons<->objects<->sets<->upgrades<->strings)")


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

    # the new object file path must be new in the whole chain
    d, a = effective(HACKERBUNKER_PATH)
    assert d is None, "HackerBunker.ini already exists in " + str(a)
    print("new-file path is unclaimed:", HACKERBUNKER_PATH)

    # the new names must be unused anywhere relevant
    for name in (NEW_OBJ, NEW_BTN, NEW_SET, DOWN_SET,
                 "ModuleTag_KB_Page01", "ModuleTag_KB_Page02",
                 "ModuleTag_KB_Page03", "ModuleTag_KB_Hack01"):
        for path in (CS_PATH, CB_PATH, DOZER_PATH, BUNKER_PATH, UPGRADE_PATH):
            assert name not in sources[path], (name, path)
    print("new identifiers are collision-free")

    # ---- build the five shipped files
    patched = {
        CS_PATH: patch_commandset(sources[CS_PATH]),
        CB_PATH: sources[CB_PATH] + with_eol(CB_APPENDIX, eol_of(sources[CB_PATH])),
        STR_PATH: sources[STR_PATH] + with_eol(STR_APPENDIX, eol_of(sources[STR_PATH])),
        DOZER_PATH: patch_dozer(sources[DOZER_PATH]),
    }
    hb, removed_blocks = make_hacker_bunker(sources[BUNKER_PATH])
    patched[HACKERBUNKER_PATH] = hb

    # ---- append-only files: base bytes identical
    for path in (CB_PATH, STR_PATH):
        assert patched[path].startswith(sources[path]), path
    print("append-only base-byte identity OK (CommandButton.ini, Generals.str)")

    # ---- CommandSet.ini diff audit: one line swapped + appendix, no other loss
    cdiff = unified(sources[CS_PATH], patched[CS_PATH])
    crem = [l[1:] for l in cdiff if l.startswith("-")]
    cadd = [l[1:] for l in cdiff if l.startswith("+")]
    exp_rem = Counter([" 13  = Tank_Command_ConstructChinaIndustrialPlant"])
    exp_add = Counter(l for l in CS_APPENDIX.rstrip("\n").split("\n")) \
        + Counter([" 13  = Command_ChinaButtonCommandSetOneDown"])
    assert Counter(crem) - Counter(cadd) == exp_rem - exp_add, cdiff
    assert Counter(cadd) - Counter(crem) == exp_add - exp_rem, cdiff
    print("CommandSet.ini diff audit OK (1 slot swapped, 2 sets appended)")

    # ---- Dozer.ini diff audit: insertions only
    ddiff = unified(sources[DOZER_PATH].replace("\r\n", "\n"),
                    patched[DOZER_PATH].replace("\r\n", "\n"))
    drem = [l for l in ddiff if l.startswith("-")]
    dadd = [l[1:] for l in ddiff if l.startswith("+")]
    assert not drem, drem
    assert Counter(dadd) == Counter(DOZER_MODULES.rstrip("\n").split("\n")), ddiff
    print("Dozer.ini diff audit OK (3 modules inserted, nothing removed)")

    # ---- hacker bunker audits
    verify_hacker_bunker(patched[HACKERBUNKER_PATH])
    # every removed block was really one of the four expected ones
    assert len(removed_blocks) == 4
    for blk, opener in zip(removed_blocks,
                           ("GenerateMinefieldBehavior", "CommandSetUpgrade",
                            "ArmorUpgrade", "AutoHealBehavior")):
        assert opener in blk.splitlines()[0]

    # ---- survivals + closure on final text
    verify_doctrine_survival(patched[CS_PATH])
    verify_cross_refs(patched[CS_PATH], patched[CB_PATH], patched[STR_PATH],
                      patched[HACKERBUNKER_PATH], sources[UPGRADE_PATH],
                      patched[DOZER_PATH])
    # doctrine hunks survive in the other shipped doctrine-owned files
    assert patched[CB_PATH].count("CommandButton Tank_Command_UpgradeKwai") == 10
    assert patched[STR_PATH].count("\nCONTROLBAR:TooltipUpgradeKwai") == 10
    assert patched[STR_PATH].count("\nCONTROLBAR:UpgradeKwai") == 10
    assert patched[STR_PATH].count("\nUPGRADE:Kwai") == 10
    for i in (1, 2, 3, 4):
        assert ("ModuleTag_KD_Armor%d" % i) in patched[DOZER_PATH]
    print("doctrine survival OK in CommandButton.ini / Generals.str / Dozer.ini")

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
        assert after.lower() == "zzz-kwaidoctrine.big", listing
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
        verify_doctrine_survival(
            find_entry(back, CS_PATH).data.decode("latin-1"))
        verify_hacker_bunker(
            find_entry(back, HACKERBUNKER_PATH).data.decode("latin-1"))
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
