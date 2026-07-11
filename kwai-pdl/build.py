#!/usr/bin/env python3
"""Build zzz-ZZZZZZZKwaiPDL.big - $500 per-vehicle POINT DEFENSE LASER pod for
Kwai (China Tank General) + Siege Soldier garrison rights.  ShockWave under
GeneralsX.

FEATURE 1 - POINT DEFENSE LASER POD (per-vehicle purchase, $500 / 10 s)
  Mechanism (engine: PointDefenseLaserUpdate.cpp - the module is NOT
  upgrade-gated natively, so the RIDER-POD pattern is used; ShockWave itself
  ships the exact idiom: the Leang BlackShark Helix ECM-jammer rider):
    Tank_Command_UpgradeKwaiPDL (OBJECT_UPGRADE button, slot 9)
      -> Tank_Upgrade_KwaiPDL (Type = OBJECT, $500 / 10 s)
      -> ObjectCreationUpgrade -> Tank_OCL_KwaiPDLPod
         (ContainInsideSourceObject = Yes)
      -> Tank_ChinaPDLPod: invisible PORTABLE_STRUCTURE rider
         (W3DModelDraw Model=NONE - the ChinaBlackSharkMissileJammerModule
         idiom, so NO container draw-module changes are needed anywhere)
         carrying PointDefenseLaserUpdate:
           WeaponTemplate = Tank_KwaiPDLLaserWeapon (clone of the USA
             Avenger's AvengerPointDefenseLaserOne minus LaserBoneName -
             the pod has no bones; the beam falls back to the drawable
             position, LaserUpdate.cpp:122-151)
           PrimaryTargetTypes = SMALL_MISSILE (Tomahawks, infantry rockets,
             AT missiles), ScanRange 160 (spec ~150-175; must exceed the
             weapon's 100 AttackRange, PointDefenseLaserUpdate.cpp:109-117)
           ScanRate 0 / PredictTargetVelocityFactor 1.0 (Avenger parity)
  The rider needs a contain: HelixContain's first PORTABLE_STRUCTURE goes to
  a dedicated rider slot regardless of AllowInsideKindOf
  (HelixContain.cpp:300-306), is position-synced every frame, never appears
  on exit buttons and consumes no seats.  Vehicles without a contain get a
  minimal BlackShark-style HelixContain bay (PORTABLE_STRUCTURE-only).
  OBJECT_UPGRADE purchases additionally REQUIRE a ProductionUpdate
  (ControlBarCommand.cpp:1250-1254) - added where missing.

  NO VeterancyBoost INI fields are emitted: the engine patch for that is not
  deployed yet (PointDefenseLaserUpdate parses only WeaponTemplate /
  Primary+SecondaryTargetTypes / ScanRate / ScanRange /
  PredictTargetVelocityFactor).  A follow-up flips it on later.

  Exclusivity (the proptower ConflictsWith + CommandSetUpgrade pattern;
  the engine does NOT grey a conflicting OBJECT_UPGRADE button - it charges
  and the module refuses - so buttons are swapped away instead;
  canProduceUpgrade() requires the button in the CURRENT set,
  Object.cpp:6244-6260):
    - Battlemaster: PDL is a THIRD mutually-exclusive rider next to the
      propaganda tower and the ERA plates.
    - Emperor: PDL contests the Gattling-cannon rider.

FEATURE 2 - SIEGE SOLDIER GARRISON RIGHTS
  Vanilla ChinaInfantrySiegeSoldier (the object Kwai's roster stub builds)
  loses NO_GARRISON *and* BOAT from KindOf.  NO_GARRISON alone only opens
  GarrisonContain buildings (GarrisonContain.cpp:567); every bunker/tank bay
  in this stack carries ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT, and the
  ShockWave soldier is flagged BOAT - it would still be refused.  Removing
  BOAT is benign: engine uses of KINDOF_BOAT are contain filters, bomb-truck
  disguise targets (vehicles only), hijack/carbomb crates (vehicles only)
  and GPS-scrambler immunity (ActionManager.cpp:1739-1743,
  ThingTemplate.cpp:437, ConvertTo*CrateCollide.cpp).

COVERAGE (button at slot 9 everywhere):
  Battlemaster, Emperor (bay 10 -> 8 seats, exit 9 freed for the button),
  Gattling Tank, Dragon (sets cloned to Tank_ names - the originals are
  shared with vanilla China), ECM Tank, Reaper (OverlordContain ->
  HelixContain: the armor-addon rider keeps the rider slot, the pod rides
  the single passenger seat - passengers are position-synced via
  containReactToTransformChange -> redeployOccupants and enclosed update
  modules still run: the BlackShark jammer scans while contained),
  WarMaster, JS-7, Command Tank, and the four SHARED artillery objects
  (ChinaVehicleNukeLauncher / ChinaVehicleInfernoCannon /
  Spec_ChinaVehicleNukeLauncher / Spec_ChinaVehicleInfernoCannon) - the
  stubs (kwai-artillery, kwai-roster) spawn these shared donors, so other
  generals' copies of the SAME objects also gain the purchase (documented
  spillover).  Skipped: Overlord (its OverlordContain rider slot IS the
  unit's three-way turret choice on a vanilla-shared object), Scout Car
  (recon, not a combat vehicle), transports/dozers/supply, aircraft.

PACKAGING: zzz-ZZZZZZZKwaiPDL.big - case-insensitively sorts AFTER
zzz-ZZZZZZKwaiUAV.big ('z' > 'k' at char 11) and BEFORE
zzz_ControlBarPro*.big ('-' 0x2D < '_' 0x5F) as well as any
zzz-ZZZZZZZR*.big ('k' < 'r'); verified against the real listings of both
mod dirs.  This becomes the LAST INI layer.
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
OUT_NAME = "zzz-ZZZZZZZKwaiPDL.big"
TAG = "zzz-ZZZZZZZKwaiPDL"

CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
UPG_PATH = "Data\\INI\\Upgrade.ini"
OCL_PATH = "Data\\INI\\ObjectCreationList.ini"
WPN_PATH = "Data\\INI\\Weapon.ini"
STR_PATH = "Data\\Generals.str"
POD_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\PDLPod.ini"

BM_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\BattleMaster.ini"
EMP_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini"
GAT_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\GattlingTank.ini"
DRG_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\DragonTank.ini"
ECM_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\ECMTank.ini"
RPR_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\Reaper.ini"
WMR_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\WarMaster.ini"
JS7_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\JS7.ini"
CMD_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\CommandTank.ini"
NUK_PATH = "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\NukeCannon.ini"
INF_PATH = "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\InfernoCannon.ini"
HAM_PATH = "Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\HammerCannon.ini"
BUR_PATH = "Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\Buratino.ini"
SGE_PATH = "Data\\INI\\Object\\China\\Vanilla\\Infantry\\SiegeSoldier.ini"

# read-only donors / precedents
AVG_PATH = "Data\\INI\\Object\\USA\\Vanilla\\Vehicles\\Avenger.ini"
SWM_PATH = "Data\\INI\\Object\\China\\SpecialWeapons\\SpecialWeaponsGeneralMisc.ini"
SHK_PATH = "Data\\INI\\Object\\China\\SpecialWeapons\\Aircraft\\HelixBlackShark.ini"
WOB_PATH = "Data\\INI\\Object\\WeaponObjects.ini"

OWNERS = {
    CS_PATH: "zzz-ZZZZZZKwaiUAV.big",
    CB_PATH: "zzz-ZZZZZZKwaiUAV.big",
    UPG_PATH: "zzz-ZZZZZZKwaiUAV.big",
    OCL_PATH: "zzz-ZZZZZZKwaiUAV.big",
    STR_PATH: "zzz-ZZZZZZKwaiUAV.big",
    WPN_PATH: "zzz-ZZZZChaosUnits.big",
    BM_PATH: "zzz-KwaiDoctrine.big",
    EMP_PATH: "zzz-ZZZZChaosUnits.big",
    GAT_PATH: "zzz-KwaiDoctrine.big",
    DRG_PATH: "zzz-KwaiDoctrine.big",
    ECM_PATH: "zzz-KwaiDoctrine.big",
    RPR_PATH: "zzz-KwaiDoctrine.big",
    WMR_PATH: "zzz-KwaiDoctrine.big",
    JS7_PATH: "zzz-ZZZZChaosUnits.big",
    CMD_PATH: "zzz-ZZZZChaosUnits.big",
    NUK_PATH: "zzz-KwaiDoctrine.big",
    INF_PATH: "zzz-KwaiDoctrine.big",
    HAM_PATH: "zz_SPE_Shw_ini.big",
    BUR_PATH: "zz_SPE_Shw_ini.big",
    SGE_PATH: "zz_SPE_Shw_ini.big",
    AVG_PATH: "zz_SPE_Shw_ini.big",     # read-only donor (weapon shape)
    SWM_PATH: "zz_SPE_Shw_ini.big",     # read-only donor (jammer rider pod)
    SHK_PATH: "zz_SPE_Shw_ini.big",     # read-only precedent (mount idiom)
    WOB_PATH: "zz_SPE_Shw_ini.big",     # read-only (laser beam object)
}
SHIPPED = [CS_PATH, CB_PATH, UPG_PATH, OCL_PATH, WPN_PATH, STR_PATH, POD_PATH,
           BM_PATH, EMP_PATH, GAT_PATH, DRG_PATH, ECM_PATH, RPR_PATH,
           WMR_PATH, JS7_PATH, CMD_PATH, NUK_PATH, INF_PATH, HAM_PATH,
           BUR_PATH, SGE_PATH]

UPG = "Tank_Upgrade_KwaiPDL"
BTN = "Tank_Command_UpgradeKwaiPDL"
OCL_NAME = "Tank_OCL_KwaiPDLPod"
POD = "Tank_ChinaPDLPod"
WPN = "Tank_KwaiPDLLaserWeapon"
SET_BM_TOWER = "Tank_ChinaVehicleBattleMasterCommandSetTower"
SET_BM_PDL = "Tank_ChinaVehicleBattleMasterCommandSetPDL"
SET_EMP_GAT = "Tank_ChinaTankEmperorGattlingCommandSet"
SET_EMP_PDL = "Tank_ChinaTankEmperorPDLCommandSet"
SET_DRG = "Tank_ChinaTankDragonCommandSet"
SET_DRG_UP = "Tank_ChinaTankDragonUpgradedCommandSet"
SET_RPR = "Tank_ChinaReaperCommandSet"
NEW_SETS = [SET_BM_TOWER, SET_BM_PDL, SET_EMP_GAT, SET_EMP_PDL,
            SET_DRG, SET_DRG_UP, SET_RPR]
NEW_NAMES = [UPG, BTN, OCL_NAME, POD, WPN,
             "ModuleTag_KPDL_Bay01", "ModuleTag_KPDL_Mount01",
             "ModuleTag_KPDL_Prod01", "ModuleTag_KPDL_CmdSet01",
             "ModuleTag_KPDL_CmdSet02", "ModuleTag_KPDL_Laser01",
             "OBJECT:KwaiPDLPod", "UPGRADE:KwaiPDL",
             "CONTROLBAR:UpgradeKwaiPDL",
             "CONTROLBAR:TooltipUpgradeKwaiPDL"] + NEW_SETS

HIJACK_ANCHOR = "  Behavior = EjectPilotDie ModuleTag_HijackerEmerge01\n"
GEOM_ANCHOR = "  Geometry = BOX\n"
BTN_LINE = "  9  = %s ; %s\n" % (BTN, TAG)


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
        "expected %d occurrences of %r, found %d" % (count, old[:90], s.count(old))
    return s.replace(old, new)


def insert_before(s, anchor, insertion):
    return replace_exact(s, anchor, insertion + anchor, 1)


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


def parse_sets(cs_lf):
    sets = {}
    for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End", cs_lf):
        slots = {}
        for line in m.group(2).splitlines():
            lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
            if lm:
                slots[int(lm.group(1))] = lm.group(2)
        sets[m.group(1)] = slots
    return sets


def get_set_block(cs_lf, name):
    m = re.search(r"(?ms)^CommandSet[ \t]+%s[ \t]*\n.*?^End[ \t]*\n"
                  % re.escape(name), cs_lf)
    assert m, "command set not found: " + name
    return m.group(0)


# ------------------------------------------------------- generated INI text
CB_APPENDIX = """
;;; %s: per-vehicle Point Defense Laser pod purchase ($500) - the
;;; BlackShark ECM-jammer purchase idiom (Command_UpgradeChinaBlackSharkReconUpgrade)
CommandButton Tank_Command_UpgradeKwaiPDL
  Command       = OBJECT_UPGRADE
  Upgrade       = Tank_Upgrade_KwaiPDL
  Options       = OK_FOR_MULTI_SELECT NOT_QUEUEABLE
  TextLabel     = CONTROLBAR:UpgradeKwaiPDL
  ButtonImage   = SNBlackSharkJammer
  ButtonBorderType        = UPGRADE ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:TooltipUpgradeKwaiPDL
  PurchasedLabel          = CONTROLBAR:TooltipUpgradeKwaiPDL
  UnitSpecificSound = MoneyWithdraw
End
""" % TAG

UPGRADE_APPENDIX = """
;;; %s: per-vehicle Point Defense Laser pod (Upgrade_BlackSharkJammer idiom)
Upgrade Tank_Upgrade_KwaiPDL
  DisplayName        = UPGRADE:KwaiPDL
  Type               = OBJECT
  BuildTime          = 10.0
  BuildCost          = 500
  ButtonImage        = SNBlackSharkJammer
  ResearchSound      = OverlordExpansion
End
""" % TAG

OCL_APPENDIX = """
; -----------------------------------------------------------------------------
;;; %s: mounts the PDL pod rider (OCL_BlackSharkECMJammer idiom)
ObjectCreationList Tank_OCL_KwaiPDLPod
  CreateObject
    ObjectNames       = Tank_ChinaPDLPod
    Count             = 1
    ContainInsideSourceObject = Yes
  End
End
""" % TAG

WPN_APPENDIX = """
;------------------------------------------------------------------------------
;;; %s: Point Defense Laser pod weapon - clone of AvengerPointDefenseLaserOne
;;; minus LaserBoneName (the invisible pod has no bones; the beam starts at the
;;; pod drawable = the host vehicle's hull, LaserUpdate.cpp:147-151)
Weapon Tank_KwaiPDLLaserWeapon
  PrimaryDamage       = 100.0
  PrimaryDamageRadius = 0.0
  AttackRange         = 100.0
  DamageType          = LASER
  DeathType           = LASERED
  WeaponSpeed         = 999999.0     ; dist/sec
  DelayBetweenShots   = 800         ; time between shots, msec
  ClipSize            = 0            ; how many shots in a Clip (0 == infinite)
  ClipReloadTime      = 0            ; how long to reload a Clip, msec
  AcceptableAimDelta  = 180          ; Don't need to turn at all.
  AntiSmallMissile    = Yes
  AntiProjectile      = Yes
  LaserName           = AvengerPointDefenseLaserBeam
  FireFX              = WeaponFX_AvengerPointDefenseLaser
End
""" % TAG

STR_APPENDIX = (
    "\nOBJECT:KwaiPDLPod\n"
    "\"Point Defense Laser\"\nEND\n"
    "\nUPGRADE:KwaiPDL\n"
    "\"Point Defense Laser\"\nEND\n"
    "\nCONTROLBAR:UpgradeKwaiPDL\n"
    "\"Point Defense Laser\"\nEND\n"
    "\nCONTROLBAR:TooltipUpgradeKwaiPDL\n"
    "\"Mount a Point Defense Laser pod on this vehicle. \\n The laser"
    " automatically shoots down incoming rockets and missiles near the"
    " vehicle - Tomahawks, infantry rockets and anti-tank missiles.\"\nEND\n"
)

POD_INI = (
    ";;; " + TAG + ": Tank_ChinaPDLPod - invisible Point Defense Laser rider pod.\n"
    ";;; Shape donor: ChinaBlackSharkMissileJammerModule (ShockWave's own\n"
    ";;; PORTABLE_STRUCTURE rider with a PointDefenseLaserUpdate and Model = NONE\n"
    ";;; - proof the module scans and fires while mounted/contained).\n"
    ";;; Weapon: Avenger point-defense laser clone (beam + pulse sound).\n"
    ";;; Deviations from the jammer donor (documented):\n"
    ";;;   - VisionRange 200 -> 0 (must not extend the host vehicle's vision)\n"
    ";;;   - no StealthDetectorUpdate (that is the jammer's ECM flavor; a mass\n"
    ";;;     $500 pod granting stealth detection would be a balance leak)\n"
    ";;;   - no FireWeaponUpdate radius-decal weapon (cosmetic ring dropped)\n"
    ";;;   - PrimaryTargetTypes = SMALL_MISSILE per spec (Avenger also lists\n"
    ";;;     BALLISTIC_MISSILE; SCUD-class interception is deliberately out)\n"
    ";;; NO VeterancyBoost fields: the engine patch for that is not deployed\n"
    ";;; yet - a follow-up layer flips it on once the engine supports it.\n"
    "Object Tank_ChinaPDLPod\n"
    "\n"
    "  ; *** ART Parameters ***\n"
    "  Draw = W3DModelDraw ModuleTag_01\n"
    "    ConditionState = NONE\n"
    "      Model = NONE\n"
    "    End\n"
    "  End\n"
    "\n"
    "  ; ***DESIGN parameters ***\n"
    "  DisplayName      = OBJECT:KwaiPDLPod\n"
    "  Side             = ChinaTankGeneral\n"
    "  EditorSorting    = SYSTEM\n"
    "  TransportSlotCount = 1\n"
    "\n"
    "  ArmorSet\n"
    "    Conditions     = None\n"
    "    Armor          = InvulnerableAllArmor ; We can't be hurt on the field.  We share damage from the host with his damage module\n"
    "  End\n"
    "  VisionRange     = 0\n"
    "\n"
    "  ; *** AUDIO Parameters ***\n"
    "  UnitSpecificSounds\n"
    "    TurretMoveStart = NoSound\n"
    "    TurretMoveLoop  = NoSound\n"
    "    VoiceRapidFire  = NoSound\n"
    "  End\n"
    "\n"
    "  ; *** ENGINEERING Parameters ***\n"
    "  KindOf            = PRELOAD PORTABLE_STRUCTURE CAN_ATTACK CLICK_THROUGH IGNORED_IN_GUI\n"
    "  Body            = StructureBody ModuleTag_02\n"
    "    MaxHealth       = 100.0\n"
    "    InitialHealth   = 100.0\n"
    "  End\n"
    "\n"
    "  Behavior = PointDefenseLaserUpdate ModuleTag_KPDL_Laser01\n"
    "    WeaponTemplate        = Tank_KwaiPDLLaserWeapon\n"
    "    PrimaryTargetTypes    = SMALL_MISSILE\n"
    "    ScanRate              = 0\n"
    "    ScanRange             = 160.0 ; must exceed the weapon's 100 AttackRange (engine assert)\n"
    "    PredictTargetVelocityFactor = 1.0\n"
    "  End\n"
    "\n"
    "  Behavior             = DestroyDie ModuleTag_04\n"
    "    ;nothing\n"
    "  End\n"
    "\n"
    "  Geometry            = BOX\n"
    "  GeometryMajorRadius = 8.0\n"
    "  GeometryMinorRadius = 8.0\n"
    "  GeometryHeight      = 9.0\n"
    "  GeometryIsSmall     = No\n"
    "  Shadow              = SHADOW_VOLUME\n"
    "  ShadowSizeX = 45  ; minimum elevation angle above horizon. Used to limit shadow length\n"
    "\n"
    "End\n"
)

BAY_BLOCK = (
    "  Behavior = HelixContain ModuleTag_KPDL_Bay01 ; " + TAG + ": rider seat for the PDL pod (BlackShark ECM-jammer idiom)\n"
    "    Slots                   = 1\n"
    "    DamagePercentToUnits    = 100%\n"
    "    AllowInsideKindOf       = PORTABLE_STRUCTURE\n"
    "    ForbidInsideKindOf      = AIRCRAFT BOAT\n"
    "    ExitDelay               = 100\n"
    "    NumberOfExitPaths       = 1\n"
    "    PassengersAllowedToFire = No\n"
    "  End\n"
)


def mount_block(conflicts=None, note=""):
    b = ("  Behavior = ObjectCreationUpgrade ModuleTag_KPDL_Mount01 ; "
         + TAG + ": mounts the PDL pod" + note + "\n"
         "    UpgradeObject = Tank_OCL_KwaiPDLPod\n"
         "    TriggeredBy   = Tank_Upgrade_KwaiPDL\n")
    if conflicts:
        b += "    ConflictsWith = %s\n" % conflicts
    b += "  End\n"
    return b


PROD_BLOCK = (
    "  Behavior = ProductionUpdate ModuleTag_KPDL_Prod01 ; " + TAG + ": OBJECT_UPGRADE purchases run through the unit's own queue\n"
    "    MaxQueueEntries = 1\n"
    "  End\n"
)


def csu_block(n, target, trigger, comment):
    return ("  Behavior = CommandSetUpgrade ModuleTag_KPDL_CmdSet0%d ; %s: %s\n"
            "    CommandSet  = %s\n"
            "    TriggeredBy = %s\n"
            "  End\n" % (n, TAG, comment, target, trigger))


# ------------------------------------------------------------- file patches
def patch_commandset(src_lf):
    """12 in-place slot-9 edits + 7 appended set clones."""
    out = src_lf

    def edit_block(cs, name, fn):
        old = get_set_block(cs, name)
        new = fn(old)
        return replace_exact(cs, old, new, 1), old, new

    # --- simple insertions of the button at slot 9
    before_11 = ["Tank_ChinaVehicleGattlingTankCommandSet",
                 "Tank_ChinaVehicleWarMasterCommandSet",
                 "RussianTankGolemCommandSet",
                 "ChinaVehicleNukeCannonCommandSet",
                 "ChinaVehicleInfernoCannonCommandSet",
                 "ChinaVehicleInfernoCannonUpgradedCommandSet",
                 "ChinaVehicleHammerCannonCommandSet",
                 "ChinaVehicleTOSCommandSet"]
    for name in before_11:
        out, _, _ = edit_block(
            out, name,
            lambda b: insert_before(b, "  11 = Command_AttackMove\n", BTN_LINE))
    # ECM has no slot 11
    out, _, _ = edit_block(
        out, "Tank_ChinaVehicleECMTankCommandSet",
        lambda b: insert_before(b, "  13 = Command_Guard\n", BTN_LINE))
    # Command Tank main page (its slot lines use odd indents; 10 is stable)
    out, _, _ = edit_block(
        out, "Tank_ChinaVehicleCommandTruckCommandSet",
        lambda b: insert_before(b, "  10 = Command_ChinaCommandTankGrantVeterancy\n",
                                BTN_LINE))

    # --- Battlemaster base: + slot 9 (tower keeps 10)
    out, bm_old, bm_new = edit_block(
        out, "Tank_ChinaVehicleBattleMasterCommandSet",
        lambda b: insert_before(
            b, "  10 = Command_UpgradeChinaOverlordPropagandaTower\n", BTN_LINE))

    # --- Emperor: exit cameo 9 -> PDL button (bay is reduced 10 -> 8 seats)
    out, emp_old, emp_new = edit_block(
        out, "Tank_ChinaTankEmperorDefaultCommandSet",
        lambda b: replace_exact(b, "  9  = Command_TransportExit\n", BTN_LINE, 1))

    # --- appended clones ------------------------------------------------
    appendix = ("\n;;; %s: exclusivity state sets (proptower idiom - a"
                " CommandSetUpgrade hides the\n"
                ";;; button whose rider can no longer mount) + Tank_ Dragon"
                " set clones (the vanilla\n"
                ";;; ChinaTankDragon sets are shared with vanilla China and"
                " stay untouched) + the\n"
                ";;; Reaper set clone (GenericCommandSet is shared by dozens"
                " of objects).\n" % TAG)

    def rename(block, old_name, new_name):
        return replace_exact(block, "CommandSet " + old_name,
                             "CommandSet " + new_name, 1)

    # BM after tower purchase: today's layout (tower @10, no PDL)
    appendix += "\n" + rename(bm_old, "Tank_ChinaVehicleBattleMasterCommandSet",
                              SET_BM_TOWER)
    # BM after PDL purchase: PDL @9, tower button gone
    b = rename(bm_new, "Tank_ChinaVehicleBattleMasterCommandSet", SET_BM_PDL)
    b = replace_exact(b, "  10 = Command_UpgradeChinaOverlordPropagandaTower\n",
                      "", 1)
    appendix += "\n" + b
    # Emperor after gattling purchase: gattling @10, no PDL (exit 9 stays freed)
    b = rename(emp_new, "Tank_ChinaTankEmperorDefaultCommandSet", SET_EMP_GAT)
    b = replace_exact(b, BTN_LINE, "", 1)
    appendix += "\n" + b
    # Emperor after PDL purchase: PDL @9, gattling button gone
    b = rename(emp_new, "Tank_ChinaTankEmperorDefaultCommandSet", SET_EMP_PDL)
    b = replace_exact(b, "  10 = Tank_Command_UpgradeChinaOverlordGattlingCannon\n",
                      "", 1)
    appendix += "\n" + b
    # Dragon clones (PDL in both black-napalm states)
    for old_name, new_name in (("ChinaTankDragonCommandSet", SET_DRG),
                               ("ChinaTankDragonUpgradedCommandSet", SET_DRG_UP)):
        b = get_set_block(out, old_name)
        b = rename(b, old_name, new_name)
        b = insert_before(b, "  11 = Command_AttackMove\n", BTN_LINE)
        appendix += "\n" + b
    # Reaper clone (GenericCommandSet + PDL)
    appendix += ("\nCommandSet %s\n" % SET_RPR
                 + BTN_LINE
                 + "  11 = Command_AttackMove\n"
                 "  13 = Command_Guard\n"
                 "  14 = Command_Stop\n"
                 "End\n")
    return out + appendix


def patch_battlemaster(src):
    eol = eol_of(src)
    lf = to_lf(src)
    assert len(re.findall(r"(?m)^Object ", lf)) == 1
    lf = replace_exact(
        lf,
        "    ConflictsWith = Upgrade_TankLightArmor ; ERA rider owns the HelixContain rider slot\n",
        "    ConflictsWith = Upgrade_TankLightArmor Tank_Upgrade_KwaiPDL ; ERA/PDL rider owns the HelixContain rider slot (" + TAG + ")\n",
        1)
    bundle = (mount_block(
        conflicts="Upgrade_TankLightArmor Upgrade_ChinaOverlordPropagandaTower",
        note=" (rider slot contested by ERA plates and the propaganda tower)")
        + csu_block(1, SET_BM_PDL, UPG,
                    "hide the tower button once the PDL pod is mounted")
        + csu_block(2, SET_BM_TOWER, "Upgrade_ChinaOverlordPropagandaTower",
                    "hide the PDL button once the tower is mounted"))
    lf = insert_before(lf, HIJACK_ANCHOR, bundle)
    return from_lf(lf, eol)


def patch_emperor(src):
    eol = eol_of(src)
    lf = to_lf(src)
    assert len(re.findall(r"(?m)^Object ", lf)) == 1
    lf = replace_exact(
        lf, "    Slots                   = 10\n",
        "    Slots                   = 8 ; " + TAG + ": was 10 - freed exit-cameo slot 9 for the PDL purchase button\n",
        1)
    lf = replace_exact(
        lf,
        "    UpgradeObject = OCL_Tank_OverlordGattlingCannon\n"
        "    TriggeredBy   = Upgrade_ChinaOverlordGattlingCannon\n",
        "    UpgradeObject = OCL_Tank_OverlordGattlingCannon\n"
        "    TriggeredBy   = Upgrade_ChinaOverlordGattlingCannon\n"
        "    ConflictsWith = Tank_Upgrade_KwaiPDL ; " + TAG + ": PDL pod owns the rider slot\n",
        1)
    bundle = (mount_block(
        conflicts="Upgrade_ChinaOverlordGattlingCannon",
        note=" (rider slot contested by the Gattling-cannon rider)")
        + csu_block(1, SET_EMP_PDL, UPG,
                    "hide the gattling button once the PDL pod is mounted")
        + csu_block(2, SET_EMP_GAT, "Upgrade_ChinaOverlordGattlingCannon",
                    "hide the PDL button once the gattling cannon is mounted"))
    lf = insert_before(lf, HIJACK_ANCHOR, bundle)
    return from_lf(lf, eol)


def patch_generic(src, anchor, bay=True, prod=True, n_objects=1):
    eol = eol_of(src)
    lf = to_lf(src)
    assert len(re.findall(r"(?m)^Object ", lf)) == n_objects
    bundle = (BAY_BLOCK if bay else "") + mount_block() + \
             (PROD_BLOCK if prod else "")
    lf = insert_before(lf, anchor, bundle)
    return from_lf(lf, eol)


def patch_dragon(src):
    eol = eol_of(src)
    lf = to_lf(src)
    lf = replace_exact(lf, "  CommandSet    = ChinaTankDragonCommandSet\n",
                       "  CommandSet    = %s ; %s: clone - the vanilla set is shared with vanilla China\n"
                       % (SET_DRG, TAG), 1)
    lf = replace_exact(lf, "    CommandSet = ChinaTankDragonUpgradedCommandSet\n",
                       "    CommandSet = %s ; %s\n" % (SET_DRG_UP, TAG), 1)
    bundle = BAY_BLOCK + mount_block() + PROD_BLOCK
    lf = insert_before(lf, HIJACK_ANCHOR, bundle)
    return from_lf(lf, eol)


def patch_reaper(src):
    eol = eol_of(src)
    lf = to_lf(src)
    assert len(re.findall(r"(?m)^Object ", lf)) == 2
    lf = replace_exact(
        lf,
        "  Behavior = OverlordContain ModuleTag_ArmorAddon01 ; Like Transport, but when full, passes transport queries along to first passenger (redirects like tunnel) \n",
        "  Behavior = HelixContain ModuleTag_ArmorAddon01 ; " + TAG + ": was OverlordContain - the armor-addon rider keeps the dedicated rider slot, the PDL pod rides the single passenger seat\n",
        1)
    lf = replace_exact(lf, "  CommandSet      = GenericCommandSet\n",
                       "  CommandSet      = %s ; %s: clone - GenericCommandSet is shared by dozens of objects\n"
                       % (SET_RPR, TAG), 1)
    bundle = mount_block() + PROD_BLOCK
    lf = insert_before(lf, HIJACK_ANCHOR, bundle)
    return from_lf(lf, eol)


def patch_siege(src):
    eol = eol_of(src)
    lf = to_lf(src)
    assert len(re.findall(r"(?m)^Object ", lf)) == 1
    lf = replace_exact(
        lf,
        "  KindOf        = PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE NO_GARRISON BOAT\n",
        "  KindOf        = PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE ; " + TAG + ": NO_GARRISON + BOAT removed - garrisons check NO_GARRISON, the bunker/tank bays forbid BOAT\n",
        1)
    return from_lf(lf, eol)


# -------------------------------------------------------------- verification
def verify_donors(sources):
    """Donor drift guards: abort loudly if the donors changed shape."""
    avg = to_lf(sources[AVG_PATH])
    m = re.search(r"(?ms)^Weapon AvengerPointDefenseLaserOne\n.*?^End",
                  to_lf(sources[WPN_PATH]))
    assert m, "Avenger PDL weapon lost from Weapon.ini"
    w = m.group(0)
    for needle in ("PrimaryDamage       = 100.0", "AttackRange         = 100.0",
                   "DelayBetweenShots   = 800", "AntiSmallMissile    = Yes",
                   "AntiProjectile      = Yes",
                   "LaserName           = AvengerPointDefenseLaserBeam",
                   "LaserBoneName       = LazerSpot01",
                   "FireFX              = WeaponFX_AvengerPointDefenseLaser"):
        assert needle in w, "Avenger weapon drift: " + needle
    assert "Behavior = PointDefenseLaserUpdate ModuleTag_Laser_One" in avg
    assert "PrimaryTargetTypes    = BALLISTIC_MISSILE SMALL_MISSILE" in avg
    assert "ScanRange             = 200.0" in avg

    swm = to_lf(sources[SWM_PATH])
    m = re.search(r"(?ms)^Object ChinaBlackSharkMissileJammerModule\n.*?^End$",
                  swm)
    assert m, "jammer rider donor lost"
    j = m.group(0)
    assert "KindOf            = PRELOAD PORTABLE_STRUCTURE CAN_ATTACK CLICK_THROUGH IGNORED_IN_GUI" in j
    assert "Model = NONE" in j
    assert "Behavior = PointDefenseLaserUpdate ModuleTag_Jammer01" in j
    assert "PrimaryTargetTypes    = SMALL_MISSILE" in j

    shk = to_lf(sources[SHK_PATH])
    assert "UpgradeObject = OCL_BlackSharkECMJammer" in shk
    assert "Behavior = HelixContain ModuleTag_29" in shk
    ocl = to_lf(sources[OCL_PATH])
    m = re.search(r"(?ms)^ObjectCreationList OCL_BlackSharkECMJammer\n.*?^End$",
                  ocl)
    assert m and "ContainInsideSourceObject = Yes" in m.group(0)
    upg = to_lf(sources[UPG_PATH])
    m = re.search(r"(?ms)^Upgrade Upgrade_BlackSharkJammer\n.*?^End$", upg)
    assert m and "BuildCost          = 500" in m.group(0) \
        and "Type               = OBJECT" in m.group(0)

    wob = to_lf(sources[WOB_PATH])
    m = re.search(r"(?ms)^Object AvengerPointDefenseLaserBeam\n.*?^End\n$",
                  wob[wob.index("Object AvengerPointDefenseLaserBeam") - 200:
                      wob.index("Object AvengerPointDefenseLaserBeam") + 3000])
    assert "Object AvengerPointDefenseLaserBeam" in wob
    assert "MuzzleParticleSystem = PaladinPointDefenseLaserFlare" in wob
    assert "TargetParticleSystem = AvengerDestroySmoke" in wob
    print("donor drift guards OK (Avenger PDL weapon+module, BlackShark jammer "
          "rider pod, jammer mount chain, laser beam object)")


EXPECT_SETS = {
    # name: exact slot layout after our patch
    "Tank_ChinaVehicleBattleMasterCommandSet": {
        1: "Command_TransportExit", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_Evacuate", 9: BTN,
        10: "Command_UpgradeChinaOverlordPropagandaTower",
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    SET_BM_TOWER: {
        1: "Command_TransportExit", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_Evacuate",
        10: "Command_UpgradeChinaOverlordPropagandaTower",
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    SET_BM_PDL: {
        1: "Command_TransportExit", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_Evacuate", 9: BTN,
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "Tank_ChinaVehicleBattleMasterCommandSetERA": {
        1: "Command_TransportExit", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_Evacuate",
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "Tank_ChinaTankEmperorDefaultCommandSet": {
        1: "Command_OverlordTaunt", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_TransportExit", 6: "Command_TransportExit",
        7: "Command_TransportExit", 8: "Command_TransportExit", 9: BTN,
        10: "Tank_Command_UpgradeChinaOverlordGattlingCannon",
        11: "Command_AttackMove", 12: "Command_Evacuate",
        13: "Command_Guard", 14: "Command_Stop"},
    SET_EMP_GAT: {
        1: "Command_OverlordTaunt", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_TransportExit", 6: "Command_TransportExit",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        10: "Tank_Command_UpgradeChinaOverlordGattlingCannon",
        11: "Command_AttackMove", 12: "Command_Evacuate",
        13: "Command_Guard", 14: "Command_Stop"},
    SET_EMP_PDL: {
        1: "Command_OverlordTaunt", 2: "Command_TransportExit",
        3: "Command_TransportExit", 4: "Command_TransportExit",
        5: "Command_TransportExit", 6: "Command_TransportExit",
        7: "Command_TransportExit", 8: "Command_TransportExit", 9: BTN,
        11: "Command_AttackMove", 12: "Command_Evacuate",
        13: "Command_Guard", 14: "Command_Stop"},
    "Tank_ChinaVehicleGattlingTankCommandSet": {
        9: BTN, 11: "Command_AttackMove", 12: "Command_GuardFlyingUnitsOnly",
        13: "Command_Guard", 14: "Command_Stop"},
    SET_DRG: {
        1: "Command_ChinaDragonTankFireWall",
        3: "Command_ChinaDragonTankUnignitedNapalmSpray", 9: BTN,
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    SET_DRG_UP: {
        1: "Command_ChinaDragonTankBlackNapalmFireWall",
        3: "Command_ChinaDragonTankUnignitedNapalmSpray", 9: BTN,
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "ChinaTankDragonCommandSet": {          # untouched vanilla-shared
        1: "Command_ChinaDragonTankFireWall",
        3: "Command_ChinaDragonTankUnignitedNapalmSpray",
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "ChinaTankDragonUpgradedCommandSet": {  # untouched vanilla-shared
        1: "Command_ChinaDragonTankBlackNapalmFireWall",
        3: "Command_ChinaDragonTankUnignitedNapalmSpray",
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "Tank_ChinaVehicleECMTankCommandSet": {
        1: "Command_ChinaTankECMDisableVehicle",
        2: "Command_SetECMTankToFreeFireMode",
        4: "Command_SetECMTankToHoldFireMode", 9: BTN,
        13: "Command_Guard", 14: "Command_Stop"},
    SET_RPR: {9: BTN, 11: "Command_AttackMove", 13: "Command_Guard",
              14: "Command_Stop"},
    "GenericCommandSet": {11: "Command_AttackMove", 13: "Command_Guard",
                          14: "Command_Stop"},   # untouched shared
    "Tank_ChinaVehicleWarMasterCommandSet": {
        1: "Command_ChinaWarMasterFireRockets", 9: BTN,
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "RussianTankGolemCommandSet": {
        1: "Command_RussiaGolemTankActivatedShtora", 9: BTN,
        11: "Command_AttackMove", 13: "Command_Guard", 14: "Command_Stop"},
    "Tank_ChinaVehicleCommandTruckCommandSet": {
        1: "Command_CommandTankAPFSDSShells", 3: "Command_CommandTankHESHShells",
        9: BTN, 10: "Command_ChinaCommandTankGrantVeterancy",
        11: "Command_AttackMove", 12: "Command_ChinaCommandTruckSwitchToPowers",
        13: "Command_Guard", 14: "Command_Stop"},
    "ChinaVehicleNukeCannonCommandSet": {
        1: "Command_FireNukeCannon", 2: "Command_ChinaNukeWarhead",
        4: "Command_ChinaNeutronWarhead", 6: "Command_NukeCannonHoldFireMode",
        9: BTN, 11: "Command_AttackMove", 13: "Command_Guard",
        14: "Command_Stop"},
    "ChinaVehicleInfernoCannonCommandSet": {
        1: "Command_ChinaInfernoCannonGroundAttack",
        2: "Command_ChinaIfernoNapalmWarhead", 4: "Command_ChinaIfernoHEWarhead",
        9: BTN, 11: "Command_AttackMove", 13: "Command_Guard",
        14: "Command_Stop"},
    "ChinaVehicleInfernoCannonUpgradedCommandSet": {
        1: "Command_ChinaInfernoCannonGroundAttack",
        2: "Command_ChinaIfernoBlackNapalmWarhead",
        4: "Command_ChinaIfernoHEWarhead",
        9: BTN, 11: "Command_AttackMove", 13: "Command_Guard",
        14: "Command_Stop"},
    "ChinaVehicleHammerCannonCommandSet": {
        1: "Command_HammerCannonGroundAttack",
        2: "Command_ChinaHammerCannonHEShells",
        4: "Command_ChinaHammerCannonSeismicShells",
        6: "Command_NukeCannonHoldFireMode",
        9: BTN, 11: "Command_AttackMove", 13: "Command_Guard",
        14: "Command_Stop"},
    "ChinaVehicleTOSCommandSet": {
        1: "Command_ChinaTOSGroundAttack",
        2: "Command_GenericArtilleryFreeFireMode",
        4: "Command_GenericArtilleryFreeHoldMode",
        9: BTN, 11: "Command_AttackMove", 13: "Command_Guard",
        14: "Command_Stop"},
}


def verify_cs_survival(cs, installed=False):
    lf = to_lf(cs)
    sets = parse_sets(lf)

    # --- our layouts (patched, cloned, and deliberately untouched sets)
    for name, exp in EXPECT_SETS.items():
        assert sets.get(name) == exp, (name, sets.get(name), exp)

    # --- the button appears exactly where planned (12 in-place edits + 5
    #     clones that carry it; BM Tower / Emperor Gattling clones do not)
    assert lf.count(BTN + " ;") == 17, lf.count(BTN + " ;")

    # --- kwai-uav IC clones + vanilla IC sets untouched
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):
        s = sets["Tank_ChinaInternetCenterCommandSet" + v]
        assert s[7] == "Tank_Command_UpgradeKwaiUAVProgram" \
            and s[8] == "Tank_Command_KwaiUAVDeploy" \
            and s[9] == "Command_Evacuate", (v, s)
        vs = sets["ChinaInternetCenterCommandSet" + v]
        assert vs[7] == "Command_StructureExit" and vs[8] == "Command_StructureExit"

    # --- prop-center machine: all 50 sets full 14/14 (doctrine/basetech/
    #     artillery/garrisons state fabric)
    pc = {n: s for n, s in sets.items()
          if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc) == 50, len(pc)
    for name, slots in pc.items():
        assert sorted(slots) == list(range(1, 15)), name
        assert slots[13] in ("Command_UpgradeChinaMines", "Command_UpgradeEMPMines")
        assert slots[14] == "Command_Sell"
    assert lf.count("CommandSet Tank_ChinaPropagandaCenterCS_M") == 48

    # --- roster: WF page 2 slots 4-7 / 8-11 free; Barracks 5; Airfield 3-4
    wf = sets["Tank_ChinaWarFactoryCommandSet_Down"]
    assert wf[4] == "Tank_Command_ConstructChinaTankOverlord"
    assert wf[7] == "Tank_Command_ConstructChinaVehicleScoutCar"
    for i in (8, 9, 10, 11):
        assert i not in wf
    assert wf[12] == "Command_ChinaButtonCommandSetOneUp"
    for n in ("Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade"):
        assert sets[n][5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier", n
    for n in ("Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
        s = sets[n]
        assert s[3] == "Tank_Command_ConstructChinaJetMIGFighter"
        assert s[4] == "Tank_Command_ConstructChinaJetMIGBomber"
        for i in (5, 6, 7, 8, 9):
            assert s[i] == "Command_StructureExit", (n, i)
        assert s[10] == "Command_Evacuate"

    # --- chaos-units / kwai-artillery WF page 1
    for n in ("Tank_ChinaWarFactoryCommandSet", "Tank_ChinaWarFactoryCommandSetUpgrade"):
        assert sets[n][11] == "Tank_Command_ConstructChinaVehicleInfernoCannon", n
        assert sets[n][12] == "Command_ChinaButtonCommandSetOneDown", n
    # --- mammoth-bunker transport slots (both needle variants)
    stem = ("  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n")
    assert lf.count(stem + "  8  = Command_Evacuate\n") == 1
    assert lf.count(stem + "  8  = Command_Evacuate \n") == 4
    # --- kwai-bunkers dozer pages + hacker bunker
    assert sets["Tank_ChinaDozerCommandSet"][13] == "Command_ChinaButtonCommandSetOneDown"
    dz2 = sets["Tank_ChinaDozerCommandSet_Down"]
    assert dz2[7] == "Tank_Command_ConstructChinaBunker"
    assert dz2[8] == "Tank_Command_ConstructChinaHackerBunker"
    assert "Tank_ChinaHackerBunkerCommandSet" in sets
    # --- garrisons + vanilla China prop center + drone set
    assert lf.count("Command_Evacuate") >= 60
    vpc = sets["ChinaPropagandaCenterCommandSet"]
    assert vpc[1] == "Command_UpgradeChinaNationalism" and 10 not in vpc
    assert "GlobalHawkCommandSet" in sets
    print("  commandset survival OK%s" % (" (installed)" if installed else ""))


def verify_vehicle_diffs(patched, sources):
    """Exact line-level diff audit per vehicle file - the strongest sibling-
    hunk survival guarantee: NOTHING but our known lines changed."""
    bay = Counter(BAY_BLOCK.rstrip("\n").split("\n"))
    prod = Counter(PROD_BLOCK.rstrip("\n").split("\n"))

    def mnt(conflicts=None, note=""):
        return Counter(mount_block(conflicts, note).rstrip("\n").split("\n"))

    def csu(n, target, trigger, comment):
        return Counter(csu_block(n, target, trigger, comment).rstrip("\n").split("\n"))

    cases = {
        BM_PATH: (
            Counter(["    ConflictsWith = Upgrade_TankLightArmor ; ERA rider owns the HelixContain rider slot"]),
            Counter(["    ConflictsWith = Upgrade_TankLightArmor Tank_Upgrade_KwaiPDL ; ERA/PDL rider owns the HelixContain rider slot (" + TAG + ")"])
            + mnt("Upgrade_TankLightArmor Upgrade_ChinaOverlordPropagandaTower",
                  " (rider slot contested by ERA plates and the propaganda tower)")
            + csu(1, SET_BM_PDL, UPG, "hide the tower button once the PDL pod is mounted")
            + csu(2, SET_BM_TOWER, "Upgrade_ChinaOverlordPropagandaTower",
                  "hide the PDL button once the tower is mounted")),
        EMP_PATH: (
            Counter(["    Slots                   = 10"]),
            Counter(["    Slots                   = 8 ; " + TAG + ": was 10 - freed exit-cameo slot 9 for the PDL purchase button",
                     "    ConflictsWith = Tank_Upgrade_KwaiPDL ; " + TAG + ": PDL pod owns the rider slot"])
            + mnt("Upgrade_ChinaOverlordGattlingCannon",
                  " (rider slot contested by the Gattling-cannon rider)")
            + csu(1, SET_EMP_PDL, UPG, "hide the gattling button once the PDL pod is mounted")
            + csu(2, SET_EMP_GAT, "Upgrade_ChinaOverlordGattlingCannon",
                  "hide the PDL button once the gattling cannon is mounted")),
        GAT_PATH: (Counter(), bay + mnt() + prod),
        DRG_PATH: (
            Counter(["  CommandSet    = ChinaTankDragonCommandSet",
                     "    CommandSet = ChinaTankDragonUpgradedCommandSet"]),
            Counter(["  CommandSet    = %s ; %s: clone - the vanilla set is shared with vanilla China" % (SET_DRG, TAG),
                     "    CommandSet = %s ; %s" % (SET_DRG_UP, TAG)])
            + bay + mnt() + prod),
        ECM_PATH: (Counter(), bay + mnt() + prod),
        RPR_PATH: (
            Counter(["  Behavior = OverlordContain ModuleTag_ArmorAddon01 ; Like Transport, but when full, passes transport queries along to first passenger (redirects like tunnel) ",
                     "  CommandSet      = GenericCommandSet"]),
            Counter(["  Behavior = HelixContain ModuleTag_ArmorAddon01 ; " + TAG + ": was OverlordContain - the armor-addon rider keeps the dedicated rider slot, the PDL pod rides the single passenger seat",
                     "  CommandSet      = %s ; %s: clone - GenericCommandSet is shared by dozens of objects" % (SET_RPR, TAG)])
            + mnt() + prod),
        WMR_PATH: (Counter(), bay + mnt()),
        JS7_PATH: (Counter(), bay + mnt() + prod),
        CMD_PATH: (Counter(), bay + mnt()),
        NUK_PATH: (Counter(), bay + mnt()),
        INF_PATH: (Counter(), bay + mnt() + prod),
        HAM_PATH: (Counter(), bay + mnt()),
        BUR_PATH: (Counter(), bay + mnt() + prod),
        SGE_PATH: (
            Counter(["  KindOf        = PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE NO_GARRISON BOAT"]),
            Counter(["  KindOf        = PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE ; " + TAG + ": NO_GARRISON + BOAT removed - garrisons check NO_GARRISON, the bunker/tank bays forbid BOAT"])),
    }
    for path, (exp_removed, exp_added) in cases.items():
        diff = unified(to_lf(sources[path]), to_lf(patched[path]))
        removed = Counter(l[1:] for l in diff if l.startswith("-"))
        added = Counter(l[1:] for l in diff if l.startswith("+"))
        assert removed == exp_removed, (path, removed - exp_removed,
                                        exp_removed - removed)
        assert added == exp_added, (path, added - exp_added, exp_added - added)
    print("vehicle-file diff audits OK (%d files: only the known lines "
          "changed; every sibling hunk byte-survives)" % len(cases))


def verify_vehicle_content(patched):
    """Spot-assert sibling hunks + our modules on the final text."""
    for path, kd_needles in (
            (BM_PATH, 4), (EMP_PATH, 4), (GAT_PATH, 4), (DRG_PATH, 4),
            (ECM_PATH, 4), (WMR_PATH, 4), (NUK_PATH, 4), (INF_PATH, 4),
            (RPR_PATH, 4)):
        lf = to_lf(patched[path])
        for i in range(1, kd_needles + 1):
            assert ("ModuleTag_KD_Armor%d" % i) in lf, (path, i)  # doctrine
    emp = to_lf(patched[EMP_PATH])
    assert "ModuleTag_ShtoraAuto01" in emp                # chaos-units Shtora
    assert "ModuleTag_Shtora01" in emp
    assert "HelixContain ModuleTag_06" in emp             # emperor-bunker bay
    assert "    Slots                   = 8 ;" in emp
    assert "ModulePropaganda_15" in emp                   # built-in prop tower
    assert emp.count("MaxHealth       = 1320.0") == 1     # china-tank-buff
    assert "ModuleTag_KPDL_Mount01" in emp and "ModuleTag_KPDL_CmdSet02" in emp
    assert "ModuleTag_KPDL_Bay01" not in emp              # bay reused, not added
    bm = to_lf(patched[BM_PATH])
    assert "HelixContain ModuleTag_ArmorAddon01" in bm    # china-bunkers bay
    assert "ModuleTag_PropTowerMount01" in bm             # proptower
    assert "ModuleTag_PropTowerCmdSet01" in bm
    assert "ModuleTag_KPDL_Bay01" not in bm
    assert bm.count("Tank_Upgrade_KwaiPDL") == 3          # tower-conflict line, OCU TriggeredBy, CSU TriggeredBy
    rpr = to_lf(patched[RPR_PATH])
    assert "HelixContain ModuleTag_ArmorAddon01" in rpr
    assert not re.search(r"(?m)^\s*Behavior\s*=\s*OverlordContain\b", rpr)
    assert rpr.count("OverlordContain") == 1              # only our comment
    assert "GrantUpgradeCreate ModuleTag_ArmorAddon03" in rpr
    assert "OCL_ReaperArmorAddons" in rpr
    assert "ModuleTag_KPDL_Bay01" not in rpr              # swap, not add
    for path in (GAT_PATH, DRG_PATH, ECM_PATH, WMR_PATH, JS7_PATH, CMD_PATH,
                 NUK_PATH, INF_PATH, HAM_PATH, BUR_PATH):
        lf = to_lf(patched[path])
        assert "ModuleTag_KPDL_Bay01" in lf and "ModuleTag_KPDL_Mount01" in lf, path
    # exactly one ProductionUpdate everywhere a button lives
    for path in (BM_PATH, EMP_PATH, GAT_PATH, DRG_PATH, ECM_PATH, RPR_PATH,
                 WMR_PATH, JS7_PATH, CMD_PATH, NUK_PATH, INF_PATH, HAM_PATH,
                 BUR_PATH):
        lf = to_lf(patched[path])
        n = len(re.findall(r"(?m)^\s*Behavior\s*=\s*ProductionUpdate\b", lf))
        assert n == 1, (path, n)
    sge = to_lf(patched[SGE_PATH])
    assert "NO_GARRISON + BOAT removed" in sge
    m = re.search(r"(?m)^  KindOf        = ([^;\n]*)", sge)
    assert m and "NO_GARRISON" not in m.group(1) and "BOAT" not in m.group(1)
    assert "INFANTRY SCORE" in m.group(1)
    assert re.search(r"(?m)^Object ChinaInfantrySiegeSoldier\b", sge)
    print("vehicle content OK (sibling hunks spot-asserted; one "
          "ProductionUpdate per host; pod bay/mount present per plan)")


def verify_cross_refs(patched):
    cb, up = to_lf(patched[CB_PATH]), to_lf(patched[UPG_PATH])
    ocl, wpn = to_lf(patched[OCL_PATH]), to_lf(patched[WPN_PATH])
    s, pod = patched[STR_PATH], to_lf(patched[POD_PATH])

    m = re.search(r"(?ms)^CommandButton %s\s*$.*?^End" % BTN, cb)
    assert m and ("Upgrade       = %s\n" % UPG) in m.group(0)
    assert "Command       = OBJECT_UPGRADE" in m.group(0)
    assert "ButtonImage   = SNBlackSharkJammer" in m.group(0)
    m = re.search(r"(?ms)^Upgrade %s\s*$.*?^End" % UPG, up)
    assert m and "Type               = OBJECT" in m.group(0)
    assert "BuildCost          = 500" in m.group(0)
    m = re.search(r"(?ms)^ObjectCreationList %s\s*$.*?^End$" % OCL_NAME, ocl)
    assert m and ("ObjectNames       = %s\n" % POD) in m.group(0)
    assert "ContainInsideSourceObject = Yes" in m.group(0)
    m = re.search(r"(?ms)^Object %s\s*$.*?^End$" % POD, pod)
    assert m
    p = m.group(0)
    assert ("WeaponTemplate        = %s\n" % WPN) in p
    assert "PrimaryTargetTypes    = SMALL_MISSILE" in p
    assert "ScanRange             = 160.0" in p
    assert "Model = NONE" in p
    assert "PORTABLE_STRUCTURE" in p
    assert "VeterancyBoost" not in p                    # engine patch not deployed
    m = re.search(r"(?ms)^Weapon %s\n.*?^End$" % WPN, wpn)
    assert m
    w = m.group(0)
    assert "LaserName           = AvengerPointDefenseLaserBeam" in w
    assert "LaserBoneName" not in w
    assert "AntiSmallMissile    = Yes" in w
    assert "AttackRange         = 100.0" in w           # < ScanRange 160
    for lbl in ("OBJECT:KwaiPDLPod", "UPGRADE:KwaiPDL",
                "CONTROLBAR:UpgradeKwaiPDL", "CONTROLBAR:TooltipUpgradeKwaiPDL"):
        assert ("\n%s\n" % lbl) in s, lbl
    # asset closure in effective data
    for path, needle in (
            ("Data\\INI\\MappedImages\\TextureSize_512\\SNUserInterface512.INI",
             "MappedImage SNBlackSharkJammer"),
            ("Data\\INI\\SoundEffects.ini", "AudioEvent AvengerPointDefenseLaserPulse"),
            ("Data\\INI\\SoundEffects.ini", "AudioEvent OverlordExpansion"),
            ("Data\\INI\\ParticleSystem.ini", "ParticleSystem PaladinPointDefenseLaserFlare"),
            ("Data\\INI\\ParticleSystem.ini", "ParticleSystem AvengerDestroySmoke"),
            ("Data\\INI\\Armor.ini", "Armor InvulnerableAllArmor"),
    ):
        data = EFFECTIVE(path)
        assert data and needle in to_lf(data), (path, needle)
    # FX + beam object live in effective space (owned by base ShockWave)
    assert "FXList WeaponFX_AvengerPointDefenseLaser" in to_lf(
        EFFECTIVE("Data\\INI\\FXList.ini"))
    assert "Object AvengerPointDefenseLaserBeam" in to_lf(EFFECTIVE(WOB_PATH))
    # every host file's mount chain points at the one OCL/upgrade
    print("  cross-reference closure OK (button<->upgrade<->OCL<->pod<->weapon"
          "<->beam<->FX<->sound<->particles<->cameo<->strings)")


def verify_sibling_appendices(patched):
    cb, up = to_lf(patched[CB_PATH]), to_lf(patched[UPG_PATH])
    ocl, wpn, s = to_lf(patched[OCL_PATH]), to_lf(patched[WPN_PATH]), patched[STR_PATH]
    assert "CommandButton Tank_Command_UpgradeKwaiUAVProgram" in cb   # kwai-uav
    assert "CommandButton Tank_Command_ConstructChinaVehicleScoutCar" in cb  # roster
    assert "Upgrade Tank_Upgrade_KwaiUAVProgram" in up                # kwai-uav
    assert "Upgrade Tank_Upgrade_KwaiVehicleArmor4" in up             # doctrine
    assert "Upgrade Upgrade_BlackSharkJammer" in up                   # donor intact
    assert "ObjectCreationList Tank_SUPERWEAPON_KwaiUAV" in ocl       # kwai-uav
    assert "ObjectCreationList SUPERWEAPON_GrantVeterancy" in ocl     # chaos
    assert "Weapon JS7TankGun" in wpn                                 # chaos appendix
    assert "Weapon BlackSharkJammerWeapon" in wpn                     # donor intact
    assert "Weapon AvengerPointDefenseLaserOne" in wpn                # donor intact
    assert "\nOBJECT:TankSurveillanceUAV\n" in s                      # kwai-uav strings
    assert "\nOBJECT:JS7\n" in s                                      # chaos strings
    print("  sibling appendices OK (CommandButton / Upgrade / OCL / Weapon / "
          "Generals.str)")


# ---------------------------------------------------------------------- main
EFFECTIVE = None


def main():
    global EFFECTIVE
    archives = sorted((f for f in os.listdir(SPE_DIR)
                       if f.lower().endswith(".big")
                       and f.lower() != OUT_NAME.lower()),
                      key=str.lower, reverse=True)
    cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}

    def effective(path):
        want = path.lower()
        for a in archives:
            for e in cache[a]:
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        return None, None

    EFFECTIVE = lambda p: effective(p)[0]  # noqa: E731

    sources = {}
    for path, owner in OWNERS.items():
        data, got = effective(path)
        assert data is not None, "effective source not found: " + path
        assert got == owner, "ownership drift for %s: %s (expected %s)" % (
            path, got, owner)
        sources[path] = data
    print("effective-file ownership verified (%d files)" % len(sources))

    # the new pod INI path must be unclaimed in every archive of both dirs
    for d in (SPE_DIR, SHW_DIR):
        for a in (f for f in os.listdir(d) if f.lower().endswith(".big")
                  and f.lower() != OUT_NAME.lower()):
            for e in read_big(os.path.join(d, a)):
                assert e.path.lower() != POD_PATH.lower(), (d, a)
    print("new INI path unclaimed: " + POD_PATH)

    # new identifiers must be unused across the whole effective INI space
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
    for name in NEW_NAMES:
        assert not re.search(r"(?<![\w:])%s(?![\w:])" % re.escape(name), blob), \
            "identifier collision: " + name
    print("new identifiers collision-free across the whole effective INI space "
          "(%d names, %d files)" % (len(NEW_NAMES), len(seen)))

    verify_donors(sources)

    # pre-state guards on sets we edit (documents current occupancy)
    pre = parse_sets(to_lf(sources[CS_PATH]))
    emp = pre["Tank_ChinaTankEmperorDefaultCommandSet"]
    assert [emp[i] for i in range(2, 10)] == ["Command_TransportExit"] * 8
    assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
    for n in ("Tank_ChinaVehicleGattlingTankCommandSet",
              "Tank_ChinaVehicleECMTankCommandSet",
              "Tank_ChinaVehicleWarMasterCommandSet", "RussianTankGolemCommandSet",
              "Tank_ChinaVehicleCommandTruckCommandSet",
              "ChinaVehicleNukeCannonCommandSet",
              "ChinaVehicleInfernoCannonCommandSet",
              "ChinaVehicleInfernoCannonUpgradedCommandSet",
              "ChinaVehicleHammerCannonCommandSet", "ChinaVehicleTOSCommandSet",
              "Tank_ChinaVehicleBattleMasterCommandSet",
              "ChinaTankDragonCommandSet", "ChinaTankDragonUpgradedCommandSet"):
        assert 9 not in pre[n], "slot 9 no longer free in " + n
    print("pre-state occupancy OK (slot 9 free in all 13 target sets; Emperor "
          "exits 2-9 as shipped by emperor-bunker)")

    # ---- build the shipped files
    patched = {
        CS_PATH: patch_commandset(sources[CS_PATH]),   # LF file
        CB_PATH: sources[CB_PATH] + from_lf(CB_APPENDIX, eol_of(sources[CB_PATH])),
        UPG_PATH: sources[UPG_PATH] + from_lf(UPGRADE_APPENDIX, eol_of(sources[UPG_PATH])),
        OCL_PATH: sources[OCL_PATH] + from_lf(OCL_APPENDIX, eol_of(sources[OCL_PATH])),
        WPN_PATH: sources[WPN_PATH] + from_lf(WPN_APPENDIX, eol_of(sources[WPN_PATH])),
        STR_PATH: sources[STR_PATH] + from_lf(STR_APPENDIX, eol_of(sources[STR_PATH])),
        POD_PATH: POD_INI,
        BM_PATH: patch_battlemaster(sources[BM_PATH]),
        EMP_PATH: patch_emperor(sources[EMP_PATH]),
        GAT_PATH: patch_generic(sources[GAT_PATH], HIJACK_ANCHOR),
        DRG_PATH: patch_dragon(sources[DRG_PATH]),
        ECM_PATH: patch_generic(sources[ECM_PATH], HIJACK_ANCHOR),
        RPR_PATH: patch_reaper(sources[RPR_PATH]),
        WMR_PATH: patch_generic(sources[WMR_PATH], HIJACK_ANCHOR, prod=False),
        JS7_PATH: patch_generic(sources[JS7_PATH], GEOM_ANCHOR),
        CMD_PATH: patch_generic(sources[CMD_PATH], GEOM_ANCHOR, prod=False),
        NUK_PATH: patch_generic(sources[NUK_PATH], HIJACK_ANCHOR, prod=False),
        INF_PATH: patch_generic(sources[INF_PATH], HIJACK_ANCHOR),
        HAM_PATH: patch_generic(sources[HAM_PATH], HIJACK_ANCHOR, prod=False),
        BUR_PATH: patch_generic(sources[BUR_PATH], HIJACK_ANCHOR),
        SGE_PATH: patch_siege(sources[SGE_PATH]),
    }

    # ---- append-only files: base bytes identical
    for path in (CB_PATH, UPG_PATH, OCL_PATH, WPN_PATH, STR_PATH):
        assert patched[path].startswith(sources[path]), path
    print("append-only base-byte identity OK (CommandButton, Upgrade, OCL, "
          "Weapon, Generals.str)")

    # ---- CommandSet.ini: in-place edits + appended clones only
    cs_tail_start = patched[CS_PATH].index(";;; %s: exclusivity state sets" % TAG)
    base_region = patched[CS_PATH][:cs_tail_start]
    tail = patched[CS_PATH][cs_tail_start:]
    diff = unified(to_lf(sources[CS_PATH]), base_region)
    added = Counter(l[1:] for l in diff if l.startswith("+"))
    removed = Counter(l[1:] for l in diff if l.startswith("-"))
    assert removed == Counter(["  9  = Command_TransportExit"]), removed
    # 12 in-place edits (8 slot-11 sets, ECM, Command Tank, Battlemaster,
    # Emperor) + the empty line the appendix split leaves at the seam
    exp_added = Counter({BTN_LINE.rstrip("\n"): 12, "": 1})
    assert added == exp_added, (added, exp_added)
    assert tail.count("\nCommandSet ") == 7
    for n in NEW_SETS:
        assert re.search(r"(?m)^CommandSet %s[ \t]*$" % n, tail), n
    print("CommandSet.ini diff audit OK (12 slot-9 button lines added in place, "
          "Emperor exit 9 replaced, 7 clones appended, nothing else)")

    # ---- block-balance deltas (End-line counts)
    for path, delta in ((CS_PATH, 7), (CB_PATH, 1), (UPG_PATH, 1),
                        (OCL_PATH, 2), (WPN_PATH, 1),
                        (BM_PATH, 3), (EMP_PATH, 3), (GAT_PATH, 3),
                        (DRG_PATH, 3), (ECM_PATH, 3), (RPR_PATH, 2),
                        (WMR_PATH, 2), (JS7_PATH, 3), (CMD_PATH, 2),
                        (NUK_PATH, 2), (INF_PATH, 3), (HAM_PATH, 2),
                        (BUR_PATH, 3), (SGE_PATH, 0)):
        d = end_lines(to_lf(patched[path])) - end_lines(to_lf(sources[path]))
        assert d == delta, (path, d, delta)
    assert patched[STR_PATH].count("\nEND\n") - sources[STR_PATH].count("\nEND\n") == 4
    print("block-balance deltas OK")

    # ---- content + survival verification on final text
    verify_vehicle_diffs(patched, sources)
    verify_vehicle_content(patched)
    verify_cs_survival(patched[CS_PATH])
    verify_cross_refs(patched)
    verify_sibling_appendices(patched)
    # every button referenced in new/modified sets resolves to a CommandButton
    cb_names = set(re.findall(r"(?m)^CommandButton\s+(\S+)",
                              to_lf(patched[CB_PATH])))
    for name, slots in parse_sets(to_lf(patched[CS_PATH])).items():
        if name in EXPECT_SETS or name in NEW_SETS:
            for b in slots.values():
                assert b in cb_names, (name, b)
    print("  every button in the touched sets resolves to a CommandButton")

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
        assert after.lower() == "zzz-zzzzzzkwaiuav.big", listing
        assert before and before.lower().startswith("zzz_controlbarpro"), listing
        # future-proof: a hypothetical zzz-ZZZZZZZRotrInfantry.big sorts after us
        probe = sorted(listing + ["zzz-ZZZZZZZRotrInfantry.big"], key=str.lower)
        assert probe.index(OUT_NAME) < probe.index("zzz-ZZZZZZZRotrInfantry.big")
        print("sort order OK in %s: %s < %s < %s" % (d, after, OUT_NAME, before))

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
        verify_cs_survival(find_entry(back, CS_PATH).data.decode("latin-1"),
                           installed=True)
        installed = {p: find_entry(back, p).data.decode("latin-1")
                     for p in SHIPPED}
        verify_vehicle_content(installed)
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
