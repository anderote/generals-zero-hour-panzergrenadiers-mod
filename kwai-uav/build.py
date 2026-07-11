#!/usr/bin/env python3
"""Build zzz-ZZZZZZKwaiUAV.big — researchable "UAV Surveillance Program" for
Kwai (China Tank General), ShockWave under GeneralsX.

WHAT IT ADDS
  1. UAV SURVEILLANCE PROGRAM (Tank_Upgrade_KwaiUAVProgram, $1000 / 30 s)
     — a plain one-shot Type = PLAYER upgrade researched at Kwai's
     INTERNET CENTER (see "why not the Propaganda Center" below).
  2. DEPLOY SURVEILLANCE UAV — an upgrade-gated, player-targeted special
     power on the Internet Center: click anywhere on the map and a
     surveillance drone spawns above the target and loiters there giving
     vision (350) + dynamic shroud clearing (400) + stealth detection,
     permanent until killed (donor semantics).

DONOR MECHANISM (vanilla/ShockWave USA Spy Drone, live in ShockWave)
  - SpecialPower SpecialPowerSpyDrone (Enum SPECIAL_SPY_DRONE, reload
    150 s, RequiredScience SCIENCE_SpyDrone) fired by an OCLSpecialPower
    module on every USA command center: OCL SUPERWEAPON_SpyDrone,
    CreateLocation = CREATE_ABOVE_LOCATION (spawns 300 above the click,
    OCLSpecialPower.cpp:213-217).
  - The OCL creates AmericaVehicleSpyDrone ("Global Hawk",
    USA\\Vanilla\\Aircraft\\SpyDrone.ini): unarmed, MaxHealth 200,
    InnateStealth, StealthDetectorUpdate, DynamicShroudClearingRange
    FinalVision 250, NO LifetimeUpdate => permanent until killed.

OUR CLONE: Tank_ChinaSurveillanceUAV (new file
  Object\\China\\Tank\\Aircraft\\SurveillanceUAV.ini), donor-identical
  except: name, Side = ChinaTankGeneral, DisplayName, VisionRange
  250 -> 350, FinalVision 250 -> 400, and the America drone-armor hooks
  (UpgradeCameo1 + MaxHealthUpgrade ModuleTag_10, TriggeredBy
  Upgrade_AmericaDroneArmor) DROPPED — Kwai can never research that
  upgrade, so they would be permanently dead weight (same reasoning as
  kwai-roster dropping the Hammer Cannon science gate).  All art/sounds/
  locomotor/armor/death-OCL are live donor references (asserted).

UPGRADE GATING (engine-source verified, GeneralsX GeneralsMD tree):
  the ShockWave GLA Radar Van Scan idiom, BOTH halves:
  - client side: the deploy CommandButton carries Options = NEED_UPGRADE
    + Upgrade = Tank_Upgrade_KwaiUAVProgram -> COMMAND_RESTRICTED
    (greyed) until the player upgrade completes
    (ControlBarCommand.cpp:1096-1113 checks
    player->hasUpgradeComplete for UPGRADE_TYPE_PLAYER).
  - logic side: the OCLSpecialPower has StartsPaused = Yes
    (SpecialPowerModule.cpp:122-125 pauseCountdown(TRUE); paused =>
    isReady() FALSE, SpecialPowerModule.cpp:310) and an
    UnpauseSpecialPowerUpgrade module TriggeredBy the upgrade calls
    pauseCountdown(FALSE) on the matching template
    (UnpauseSpecialPowerUpgrade.cpp:83-94).  The engine header says this
    module exists precisely "so you can have [special powers] dependent
    on upgrades on the logic side, like NEED_UPGRADE does on the client
    side" (UnpauseSpecialPowerUpgrade.h:27-29).
  ShockWave's GLA Radar Van (GLA\\Demo\\Vehicles\\RadarVan.ini
  ModuleTag_06/07 + Command_RadarVanScan) ships exactly this pairing —
  asserted at build time as the living precedent.
  => NO CommandSetUpgrade is added anywhere: kwai-doctrine's 50-set
  Propaganda Center state machine and the Internet Center's own
  4-set machine are untouched as STATE MACHINES.

WHY THE INTERNET CENTER (both buttons), NOT THE PROPAGANDA CENTER:
  the spec wanted the research button at the Propaganda Center slot 13
  if free — it is NOT: all 50 Kwai prop-center sets are full 14/14
  (1-3 vanilla research, 4-5 kwai-artillery, 6-9 kwai-doctrine,
  10-11 kwai-basetech, 12 kwai-garrisons Evacuate, 13 the per-building
  Mines/EMP-Mines state slot, 14 Sell) — asserted at build time.  The
  Internet Center is the thematic surveillance building (satellite hack,
  spy-satellite scan), it is Kwai-buildable (dozer page 1), and hosting
  research + deploy on the same building is cleaner UX anyway.

INTERNET CENTER SETS: Kwai's Tank_ChinaInternetCenter used the
  VANILLA-SHARED ChinaInternetCenterCommandSet{One,OneUpgrade,Two,
  TwoUpgrade} (SatelliteHack x Mines state machine, CommandSetUpgrade
  ModuleTag_31/32 with CommandSetAlt/TriggerAlt) — patching those would
  leak the buttons (and a purchasable upgrade!) to vanilla China and
  Leang.  So the 4 sets are CLONED verbatim to Tank_… names (appended to
  CommandSet.ini) and ONLY Kwai's IC object is repointed (5 references).
  In the clones, garrison-exit cameos 7-8 become 7 = research /
  8 = deploy (exit-cameo sacrifice precedent: kwai-roster Airfield
  7 -> 5 exits; the IC already showed 8 exit cameos for 30 hacker seats;
  Evacuate at 9 still empties everyone).  Slots 7-8 are the only
  consistently identical slots across all four state sets (10/11 differ
  between One/Two states), so the buttons never move as states change.

NEW SPECIAL POWER: Tank_SpecialPowerKwaiUAV — Enum SPECIAL_SPY_DRONE
  (enum sharing between templates is ubiquitous: 181 templates share
  SPECIAL_COMMUNICATIONS_DOWNLOAD), ReloadTime 120000 (spec ~2 min;
  donor 150000), no RequiredScience (upgrade-gated instead), no
  ShortcutPower (a shortcut button would need the shared China shortcut
  command set => leak; deliberately dropped from donor parity),
  RadiusCursorRadius 400 aligned with the drone's FinalVision (donor
  comment idiom).  First use is available immediately after research
  (unpausing shifts m_availableOnFrame forward by exactly the paused
  duration, SpecialPowerModule.cpp:768-792 — it was ready when paused
  at spawn).  SharedSyncedTimer = Yes (donor parity: all ICs share one
  reload clock).

AI: none (player-only).  Strings: append-only Data\\Generals.str.
Cameo: reuses ShockWave's mapped SASienceSpyDrone (spy-drone cameo) for
both buttons; the drone object keeps donor SAScout/SAScout_L.

PACKAGING: zzz-ZZZZZZKwaiUAV.big.  Case-insensitively
'zzz-zzzzzz…' sorts AFTER zzz-ZZZZZKwaiRoster.big ('z' > 'k' at char 9)
— whose CommandSet.ini / CommandButton.ini it layers on — and '-'
(0x2D) < '_' (0x5F) sorts it BEFORE zzz_ControlBarPro*.big; verified
against the real directory listings of both mod dirs at build time.
This becomes the LAST INI layer.

REBUILD ORDER: if any lower layer is rebuilt (kwai-roster, chaos-units,
kwai-garrisons, kwai-basetech, kwai-bunkers, kwai-doctrine, …), rebuild
this archive afterwards — it embeds full copies of their files.  Lower
layers' builds must not see this archive: delete zzz-ZZZZZZKwaiUAV.big
from both mod dirs first, rebuild the lower chain in its documented
order, then rerun this build.
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
OUT_NAME = "zzz-ZZZZZZKwaiUAV.big"
TAG = "zzz-ZZZZZZKwaiUAV"

CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
UPG_PATH = "Data\\INI\\Upgrade.ini"
SP_PATH = "Data\\INI\\SpecialPower.ini"
OCL_PATH = "Data\\INI\\ObjectCreationList.ini"
STR_PATH = "Data\\Generals.str"
IC_PATH = "Data\\INI\\Object\\China\\Tank\\Buildings\\InternetCenter.ini"
UAV_PATH = "Data\\INI\\Object\\China\\Tank\\Aircraft\\SurveillanceUAV.ini"
DONOR_PATH = "Data\\INI\\Object\\USA\\Vanilla\\Aircraft\\SpyDrone.ini"
RADARVAN_PATH = "Data\\INI\\Object\\GLA\\Demo\\Vehicles\\RadarVan.ini"
USACC_PATH = "Data\\INI\\Object\\USA\\Vanilla\\Buildings\\CommandCenter.ini"

OWNERS = {
    CS_PATH: "zzz-ZZZZZKwaiRoster.big",
    CB_PATH: "zzz-ZZZZZKwaiRoster.big",
    UPG_PATH: "zzz-ZZKwaiBaseTech.big",
    SP_PATH: "zzz-ZZZZChaosUnits.big",
    OCL_PATH: "zzz-ZZZZChaosUnits.big",
    STR_PATH: "zzz-ZZZZChaosUnits.big",
    IC_PATH: "zzz-ZZKwaiBaseTech.big",
    DONOR_PATH: "zz_SPE_Shw_ini.big",       # read-only donor
    RADARVAN_PATH: "zz_SPE_Shw_ini.big",    # read-only precedent
    USACC_PATH: "zz_SPE_Shw_ini.big",       # read-only donor-carrier
}
SHIPPED = [CS_PATH, CB_PATH, UPG_PATH, SP_PATH, OCL_PATH, STR_PATH,
           IC_PATH, UAV_PATH]

UPG = "Tank_Upgrade_KwaiUAVProgram"
BTN_RESEARCH = "Tank_Command_UpgradeKwaiUAVProgram"
BTN_DEPLOY = "Tank_Command_KwaiUAVDeploy"
POWER = "Tank_SpecialPowerKwaiUAV"
OCL_NAME = "Tank_SUPERWEAPON_KwaiUAV"
UAV_OBJ = "Tank_ChinaSurveillanceUAV"
IC_SET_BASE = "ChinaInternetCenterCommandSet"
IC_SET_VARIANTS = ("One", "OneUpgrade", "Two", "TwoUpgrade")
NEW_SETS = ["Tank_" + IC_SET_BASE + v for v in IC_SET_VARIANTS]
NEW_NAMES = [UPG, BTN_RESEARCH, BTN_DEPLOY, POWER, OCL_NAME, UAV_OBJ,
             "ModuleTag_KUAV_Power01", "ModuleTag_KUAV_Unpause01",
             "OBJECT:TankSurveillanceUAV", "UPGRADE:KwaiUAVProgram",
             "CONTROLBAR:UpgradeKwaiUAVProgram",
             "CONTROLBAR:TooltipUpgradeKwaiUAVProgram",
             "CONTROLBAR:KwaiUAVDeploy",
             "CONTROLBAR:TooltipKwaiUAVDeploy"] + NEW_SETS


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


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    """Top-level-ish block-balance proxy: count of pure End/END lines."""
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


def parse_sets(cs_lf):
    """CommandSet name -> {slot:int -> button}, comments/blank skipped."""
    sets = {}
    for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End", cs_lf):
        slots = {}
        for line in m.group(2).splitlines():
            lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
            if lm:
                slots[int(lm.group(1))] = lm.group(2)
        sets[m.group(1)] = slots
    return sets


# ------------------------------------------------------- generated INI text
CB_APPENDIX = """
;;; zzz-ZZZZZZKwaiUAV: UAV Surveillance Program - research (Internet Center
;;; slot 7) + upgrade-gated deploy special power (slot 8).  Gating idiom =
;;; ShockWave GLA Radar Van Scan: NEED_UPGRADE on the button (client side)
;;; + StartsPaused/UnpauseSpecialPowerUpgrade on the module (logic side).

CommandButton Tank_Command_UpgradeKwaiUAVProgram
  Command       = PLAYER_UPGRADE
  Upgrade       = Tank_Upgrade_KwaiUAVProgram
  TextLabel     = CONTROLBAR:UpgradeKwaiUAVProgram
  ButtonImage   = SASienceSpyDrone
  ButtonBorderType        = UPGRADE ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:TooltipUpgradeKwaiUAVProgram
  PurchasedLabel          = CONTROLBAR:TooltipUpgradeKwaiUAVProgram
  UnitSpecificSound = MoneyWithdraw
End

CommandButton Tank_Command_KwaiUAVDeploy
  Command           = SPECIAL_POWER
  SpecialPower      = Tank_SpecialPowerKwaiUAV
  Options           = NEED_TARGET_POS CONTEXTMODE_COMMAND NEED_UPGRADE OK_FOR_MULTI_SELECT
  Upgrade           = Tank_Upgrade_KwaiUAVProgram
  TextLabel         = CONTROLBAR:KwaiUAVDeploy
  ButtonImage       = SASienceSpyDrone
  ButtonBorderType  = ACTION ; Identifier for the User as to what kind of button this is
  DescriptLabel     = CONTROLBAR:TooltipKwaiUAVDeploy
  RadiusCursorType  = SPYDRONE
  InvalidCursorName = GenericInvalid
End
"""

UPGRADE_APPENDIX = """
;;; zzz-ZZZZZZKwaiUAV: UAV Surveillance Program (researched at Kwai's Internet Center)
Upgrade Tank_Upgrade_KwaiUAVProgram
  DisplayName        = UPGRADE:KwaiUAVProgram
  Type               = PLAYER
  BuildTime          = 30.0
  BuildCost          = 1000
  ButtonImage        = SASienceSpyDrone
End
"""

SP_APPENDIX = """
;-----------------------------------------------------------------------------
;;; zzz-ZZZZZZKwaiUAV: Kwai's deployable Surveillance UAV - derivative of
;;; SpecialPowerSpyDrone (no RequiredScience: gated by Tank_Upgrade_KwaiUAVProgram
;;; via NEED_UPGRADE + StartsPaused/UnpauseSpecialPowerUpgrade; no ShortcutPower:
;;; the China shortcut command set is vanilla-shared and must not be patched)
SpecialPower Tank_SpecialPowerKwaiUAV
  Enum                    = SPECIAL_SPY_DRONE
  ReloadTime              = 120000   ; in milliseconds
  PublicTimer             = No
  InitiateAtLocationSound = SpyDroneCreate
  SharedSyncedTimer       = Yes
  RadiusCursorRadius      = 400   ; align with Tank_ChinaSurveillanceUAV's FinalVision
  AcademyClassify         = ACT_SUPERPOWER ;Considered a powerful special power that a player could fire. Not for simpler unit based powers.
End
"""

OCL_APPENDIX = """
; -----------------------------------------------------------------------------
;;; zzz-ZZZZZZKwaiUAV: derivative of SUPERWEAPON_SpyDrone
ObjectCreationList Tank_SUPERWEAPON_KwaiUAV
  CreateObject
    ObjectNames = Tank_ChinaSurveillanceUAV
    Disposition = LIKE_EXISTING
    Count = 1
  End
End
"""

STR_APPENDIX = (
    "\nOBJECT:TankSurveillanceUAV\n"
    "\"Surveillance UAV\"\nEND\n"
    "\nUPGRADE:KwaiUAVProgram\n"
    "\"UAV Surveillance Program\"\nEND\n"
    "\nCONTROLBAR:UpgradeKwaiUAVProgram\n"
    "\"UAV Surveillance Program\"\nEND\n"
    "\nCONTROLBAR:TooltipUpgradeKwaiUAVProgram\n"
    "\"Research the UAV Surveillance Program. \\n Unlocks the Internet"
    " Center's deployable Surveillance UAV - a stealthy reconnaissance"
    " drone that loiters over a target location, providing vision and"
    " detecting stealth units.\"\nEND\n"
    "\nCONTROLBAR:KwaiUAVDeploy\n"
    "\"Deploy Surveillance UAV\"\nEND\n"
    "\nCONTROLBAR:TooltipKwaiUAVDeploy\n"
    "\"Deploy a Surveillance UAV to the target location. \\n The drone"
    " loiters there, revealing the area and detecting stealthed enemies"
    " until it is destroyed. \\n Requires the UAV Surveillance"
    " Program.\"\nEND\n"
)

IC_ANCHOR = (
    "  Behavior           = OCLSpecialPower ModuleTag_17\n"
    "    SpecialPowerTemplate = ChineseHackedSpecialPowerSpySatellite\n"
    "    OCL                  = SUPERWEAPON_SpySatellite\n"
    "    CreateLocation       = CREATE_AT_LOCATION\n"
    "  End\n"
)

IC_NEW_MODULES = (
    "  Behavior           = OCLSpecialPower ModuleTag_KUAV_Power01 ; " + TAG + ": deployable Surveillance UAV\n"
    "    SpecialPowerTemplate = Tank_SpecialPowerKwaiUAV\n"
    "    OCL                  = Tank_SUPERWEAPON_KwaiUAV\n"
    "    CreateLocation       = CREATE_ABOVE_LOCATION ; donor: USA command centers' SpecialPowerSpyDrone module\n"
    "    StartsPaused         = Yes ; Unpaused by upgrade module (GLA Radar Van Scan idiom)\n"
    "  End\n"
    "  Behavior = UnpauseSpecialPowerUpgrade ModuleTag_KUAV_Unpause01 ; " + TAG + "\n"
    "    SpecialPowerTemplate = Tank_SpecialPowerKwaiUAV\n"
    "    TriggeredBy = Tank_Upgrade_KwaiUAVProgram\n"
    "  End\n"
)

UAV_HEADER = (
    ";;; " + TAG + ": Tank_ChinaSurveillanceUAV - Kwai's deployable Surveillance UAV.\n"
    ";;; Clone of vanilla/ShockWave AmericaVehicleSpyDrone (Global Hawk,\n"
    ";;; USA\\Vanilla\\Aircraft\\SpyDrone.ini) with China Tank General flavor:\n"
    ";;; Side/DisplayName renamed, VisionRange 250 -> 350, FinalVision 250 -> 400.\n"
    ";;; The donor's drone-armor hooks (UpgradeCameo1 + MaxHealthUpgrade on\n"
    ";;; Upgrade_AmericaDroneArmor) are dropped - Kwai can never research them.\n"
    ";;; No LifetimeUpdate (donor parity): the drone loiters until killed.\n"
    ";;; Created by Tank_SUPERWEAPON_KwaiUAV (Tank_SpecialPowerKwaiUAV, Internet Center).\n"
)


# ------------------------------------------------------------- file patches
def patch_commandset(src_lf):
    """Append 4 Tank_ clones of the vanilla IC sets, exits 7-8 -> buttons."""
    blocks = {}
    for m in re.finditer(r"(?ms)^(CommandSet (%s\w*)[ \t]*\n.*?^End[ \t]*\n)" % IC_SET_BASE,
                         src_lf):
        blocks[m.group(2)] = m.group(1)
    want = [IC_SET_BASE + v for v in IC_SET_VARIANTS]
    assert sorted(blocks) == sorted(want), sorted(blocks)

    appendix = ("\n;;; %s: Kwai Internet Center command sets - verbatim clones of the\n"
                ";;; vanilla-shared ChinaInternetCenter sets (which stay untouched for\n"
                ";;; vanilla China / Leang), with garrison-exit cameos 7-8 replaced by the\n"
                ";;; UAV Surveillance Program research + deploy buttons (Evacuate at 9\n"
                ";;; still ejects all occupants; exit-cameo sacrifice precedent:\n"
                ";;; kwai-roster Airfield).  Only Tank_ChinaInternetCenter references these.\n"
                % TAG)
    for v in IC_SET_VARIANTS:
        b = blocks[IC_SET_BASE + v]
        b = replace_exact(b, "CommandSet " + IC_SET_BASE + v,
                          "CommandSet Tank_" + IC_SET_BASE + v, 1)
        b = replace_exact(b, "  7 = Command_StructureExit\n",
                          "  7 = %s ; %s\n" % (BTN_RESEARCH, TAG), 1)
        b = replace_exact(b, "  8 = Command_StructureExit\n",
                          "  8 = %s ; %s\n" % (BTN_DEPLOY, TAG), 1)
        appendix += "\n" + b
    return src_lf + appendix


def patch_ic(src):
    eol = eol_of(src)
    lf = to_lf(src)
    assert re.search(r"(?m)^Object Tank_ChinaInternetCenter\b", lf)
    assert len(re.findall(r"(?m)^Object ", lf)) == 1
    # repoint the 5 command-set references (base CommandSet line +
    # ModuleTag_31/32 CommandSet/CommandSetAlt values) to the Tank_ clones
    lf = replace_exact(lf, IC_SET_BASE, "Tank_" + IC_SET_BASE, 5)
    # insert the power + unpause modules right after the satellite-scan
    # OCLSpecialPower (ModuleTag_17) block
    lf = replace_exact(lf, IC_ANCHOR, IC_ANCHOR + IC_NEW_MODULES, 1)
    return from_lf(lf, eol)


def build_uav(donor_raw):
    eol = eol_of(donor_raw)          # donor is CRLF
    lf = to_lf(donor_raw)
    lf = replace_exact(lf, "Object AmericaVehicleSpyDrone ;; Global Hawk",
                       "Object Tank_ChinaSurveillanceUAV ;; Global Hawk", 1)
    lf = replace_exact(lf, "\n  UpgradeCameo1 = Upgrade_AmericaDroneArmor\n", "\n", 1)
    lf = replace_exact(lf, "  DisplayName      = OBJECT:SpyDrone",
                       "  DisplayName      = OBJECT:TankSurveillanceUAV", 1)
    lf = replace_exact(lf, "  Side = America", "  Side = ChinaTankGeneral", 1)
    lf = replace_exact(lf, "  VisionRange     = 250",
                       "  VisionRange     = 350", 1)
    lf = replace_exact(lf, "FinalVision = 250.0", "FinalVision = 400.0", 1)
    m = list(re.finditer(
        r"(?ms)^  Behavior = MaxHealthUpgrade ModuleTag_10\n.*?^  End\n", lf))
    assert len(m) == 1, "MaxHealthUpgrade block not found exactly once"
    block = m[0].group(0)
    assert "Upgrade_AmericaDroneArmor" in block and block.count("\n") == 5, block
    lf = lf.replace(block, "", 1)
    lf = UAV_HEADER + lf
    return from_lf(lf, eol)


# -------------------------------------------------------------- verification
def verify_donors(sources):
    """Donor drift guards: abort loudly if the donors changed shape."""
    d = to_lf(sources[DONOR_PATH])
    assert re.search(r"(?m)^Object AmericaVehicleSpyDrone\b", d)
    assert "MaxHealth       = 200.0" in d
    assert "InnateStealth               = Yes" in d
    assert "Behavior = StealthDetectorUpdate ModuleTag_05" in d
    assert "Behavior = DynamicShroudClearingRangeUpdate ModuleTag_04" in d
    assert "LifetimeUpdate" not in d, "donor grew a lifetime - re-decide semantics"
    assert "CommandSet      = GlobalHawkCommandSet" in d
    assert "Locomotor = SET_NORMAL GlobalHawkLocomtor" in d
    assert "CreationList      = OCL_AmericaScoutDroneExplode" in d

    rv = to_lf(sources[RADARVAN_PATH])
    assert "StartsPaused         = Yes" in rv, "Radar Van precedent lost"
    assert "Behavior = UnpauseSpecialPowerUpgrade ModuleTag_07" in rv
    assert "TriggeredBy = Upgrade_GLARadarVanScan" in rv

    cc = to_lf(sources[USACC_PATH])
    m = re.search(r"(?ms)Behavior\s+= OCLSpecialPower ModuleTag_21\n.*?End", cc)
    assert m and "SpecialPowerTemplate = SpecialPowerSpyDrone" in m.group(0)
    assert "CreateLocation       = CREATE_ABOVE_LOCATION" in m.group(0)
    print("donor drift guards OK (SpyDrone object, Radar Van gating pair, "
          "USA CC CREATE_ABOVE_LOCATION)")


def verify_propcenter_full(cs_lf):
    """Document the forced deviation: every Kwai prop-center set is 14/14."""
    sets = parse_sets(cs_lf)
    pc = {n: s for n, s in sets.items()
          if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc) == 50, len(pc)
    for name, slots in pc.items():
        assert sorted(slots) == list(range(1, 15)), \
            "prop-center set %s NOT full: %s" % (name, sorted(slots))
        assert slots[13] in ("Command_UpgradeChinaMines", "Command_UpgradeEMPMines")
        assert slots[14] == "Command_Sell"
        assert slots[12] == "Command_Evacuate"
        assert slots[10] == "Tank_Command_UpgradeKwaiAutoRepair"
        assert slots[11] == "Tank_Command_UpgradeKwaiBaseArmaments"
        assert slots[4] == "Command_UpgradeChinaChainGuns"
        assert slots[5] == "Command_UpgradeChinaBlackNapalm"
    print("Propaganda Center: all 50 Kwai sets asserted FULL (14/14; 13 = Mines/"
          "EMP state slot, 14 = Sell) -> research button moved to the Internet "
          "Center (documented deviation)")


def verify_cs_survival(cs, installed=False):
    lf = to_lf(cs)
    sets = parse_sets(lf)

    # --- our 4 clones: exact expected layout
    for v in IC_SET_VARIANTS:
        name = "Tank_" + IC_SET_BASE + v
        s = sets[name]
        exp_exits = [1, 2, 3, 4, 5, 6]
        for i in exp_exits:
            assert s[i] == "Command_StructureExit", (name, i)
        assert s[7] == BTN_RESEARCH and s[8] == BTN_DEPLOY, (name, s)
        assert s[9] == "Command_Evacuate"
        assert s[12] == "Command_ChinaUpgradeSystemHack"
        assert s[13] == ("Command_UpgradeEMPMines" if v.endswith("Upgrade")
                         else "Command_UpgradeChinaMines")
        assert s[14] == "Command_Sell"
        if v.startswith("One"):
            assert s[10] == "Command_UpgradeChinaSatelliteHackOne" and 11 not in s
        else:
            assert s[11] == "Command_HackedSpySatelliteScan" and 10 not in s

    # --- vanilla IC sets untouched (no UAV buttons, exits intact)
    for v in IC_SET_VARIANTS:
        s = sets[IC_SET_BASE + v]
        for i in (7, 8):
            assert s[i] == "Command_StructureExit", ("vanilla leak!", v, i)

    # --- prop-center machine intact (incl. basetech/artillery/garrisons)
    verify_propcenter_full(lf)
    assert lf.count("CommandSet Tank_ChinaPropagandaCenterCS_M") == 48

    # --- roster survival: WF page 2 slots 4-7, 8-11 free; Barracks 5; Airfield 3-4
    wf = sets["Tank_ChinaWarFactoryCommandSet_Down"]
    assert wf[1] == "Tank_Command_ConstructChinaVehicleNukeLauncher"
    assert wf[2] == "Tank_Command_ConstructChinaTankJS7"
    assert wf[3] == "Tank_Command_ConstructChinaTankCommandTank"
    assert wf[4] == "Tank_Command_ConstructChinaTankOverlord"
    assert wf[5] == "Tank_Command_ConstructChinaVehicleBuratino"
    assert wf[6] == "Tank_Command_ConstructChinaVehicleHammerCannon"
    assert wf[7] == "Tank_Command_ConstructChinaVehicleScoutCar"
    for i in (8, 9, 10, 11):
        assert i not in wf, "WF page2 slot %d no longer free" % i
    assert wf[12] == "Command_ChinaButtonCommandSetOneUp"
    for n in ("Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade"):
        assert sets[n][5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier", n
    for n in ("Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
        s = sets[n]
        assert s[3] == "Tank_Command_ConstructChinaJetMIGFighter", n
        assert s[4] == "Tank_Command_ConstructChinaJetMIGBomber", n
        for i in (5, 6, 7, 8, 9):
            assert s[i] == "Command_StructureExit", (n, i)
        assert s[10] == "Command_Evacuate", n

    # --- chaos-units WF page 1 arrow
    assert any(b == "Command_ChinaButtonCommandSetOneDown"
               for b in sets["Tank_ChinaWarFactoryCommandSet"].values())
    # --- kwai-artillery Inferno at WF 11 (chaos-units moved Nuke Cannon to
    #     page 2 slot 1 and put the page-down arrow at 12; both variants)
    for n in ("Tank_ChinaWarFactoryCommandSet", "Tank_ChinaWarFactoryCommandSetUpgrade"):
        assert sets[n][11] == "Tank_Command_ConstructChinaVehicleInfernoCannon", n
        assert sets[n][12] == "Command_ChinaButtonCommandSetOneDown", n
    # --- emperor-bunker Emperor set
    emp = sets["Tank_ChinaTankEmperorDefaultCommandSet"]
    assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
    assert emp[12] == "Command_Evacuate"
    assert [emp[i] for i in range(2, 10)] == ["Command_TransportExit"] * 8
    # --- mammoth-bunker transport slots 4-8 (basetech's needle: the one
    #     variant WITHOUT the ambulance cleanup line / trailing space)
    stem = ("  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n")
    assert lf.count(stem + "  8  = Command_Evacuate\n") == 1, "mammoth-bunker slots lost"
    assert lf.count(stem + "  8  = Command_Evacuate \n") == 4  # ambulance variants
    # --- prop-tower Battlemaster sets
    bm = sets["Tank_ChinaVehicleBattleMasterCommandSet"]
    assert bm[10] == "Command_UpgradeChinaOverlordPropagandaTower"
    assert bm[5] == "Command_Evacuate"
    assert "Tank_ChinaVehicleBattleMasterCommandSetERA" in sets
    # --- kwai-bunkers dozer pages + hacker bunker
    dz = sets["Tank_ChinaDozerCommandSet"]
    assert dz[13] == "Command_ChinaButtonCommandSetOneDown"
    dz2 = sets["Tank_ChinaDozerCommandSet_Down"]
    assert dz2[7] == "Tank_Command_ConstructChinaBunker"
    assert dz2[8] == "Tank_Command_ConstructChinaHackerBunker"
    assert "Tank_ChinaHackerBunkerCommandSet" in sets
    # --- garrisons: plenty of Evacuates
    assert lf.count("Command_Evacuate") >= 60
    # --- vanilla China prop-center untouched
    vpc = sets["ChinaPropagandaCenterCommandSet"]
    assert vpc[1] == "Command_UpgradeChinaNationalism" and 10 not in vpc
    # --- our buttons appear exactly in our 4 sets, nowhere else
    assert lf.count(BTN_RESEARCH) == 4 and lf.count(BTN_DEPLOY) == 4
    # --- GlobalHawkCommandSet still defined (drone clone references it)
    assert "GlobalHawkCommandSet" in sets
    print("  commandset survival OK%s" % (" (installed)" if installed else ""))


def verify_ic(shipped):
    lf = to_lf(shipped)
    # repointed to the clones - old names must survive ONLY inside new names
    assert lf.count("Tank_" + IC_SET_BASE) == 5
    assert lf.count(IC_SET_BASE) == 5  # every occurrence carries the Tank_ prefix
    assert ("CommandSet        = Tank_ChinaInternetCenterCommandSetOne\n") in lf
    assert ("CommandSet = Tank_ChinaInternetCenterCommandSetOneUpgrade\n") in lf
    assert ("CommandSet = Tank_ChinaInternetCenterCommandSetTwo\n") in lf
    assert lf.count("CommandSetAlt = Tank_ChinaInternetCenterCommandSetTwoUpgrade\n") == 2
    # new modules present exactly once
    assert lf.count("ModuleTag_KUAV_Power01") == 1
    assert lf.count("ModuleTag_KUAV_Unpause01") == 1
    assert lf.count("StartsPaused         = Yes") == 1
    assert lf.count("TriggeredBy = Tank_Upgrade_KwaiUAVProgram\n") == 1
    assert lf.count("SpecialPowerTemplate = Tank_SpecialPowerKwaiUAV\n") == 2
    assert lf.count("OCL                  = Tank_SUPERWEAPON_KwaiUAV\n") == 1
    # sibling survival inside the IC file
    assert "ModuleTag_KBT_Heal01" in lf and "ModuleTag_KBT_Arm01" in lf \
        and "ModuleTag_KBT_AI01" in lf                       # kwai-basetech
    assert lf.count("  WeaponSet\n") == 2                    # kwai-basetech
    for i in (1, 2, 3, 4):
        assert ("ModuleTag_KD_Armor%d" % i) in lf            # kwai-doctrine
    assert re.search(r"(?m)^\s*MaxHealth\s*=\s*20000\b", lf)  # stat-tune
    assert re.search(r"(?m)^\s*Slots\s*=\s*30\b", lf)         # stat-tune
    assert "OCLSpecialPower ModuleTag_17" in lf              # satellite scan
    assert "CommandSetUpgrade ModuleTag_31" in lf
    assert "CommandSetUpgrade ModuleTag_32" in lf
    assert "GenerateMinefieldBehavior" in lf
    print("  internet-center content + sibling survival OK")


def verify_uav(shipped, donor_raw):
    lf = to_lf(shipped)
    assert re.search(r"(?m)^Object Tank_ChinaSurveillanceUAV\b", lf)
    residue = (lf.replace("AmericaVehicleSpyDrone", "")      # header comment
               .replace("Upgrade_AmericaDroneArmor", "")     # header comment
               .replace("OCL_AmericaScoutDroneExplode", ""))  # kept death FX
    assert "America" not in residue, "unexpected America residue"
    assert "  Side = ChinaTankGeneral" in lf
    assert "  VisionRange     = 350" in lf
    assert "FinalVision = 400.0" in lf
    assert "MaxHealth       = 200.0" in lf
    assert "InnateStealth               = Yes" in lf
    assert "StealthDetectorUpdate" in lf
    # permanent until killed: no LifetimeUpdate module (header comment aside)
    assert not re.search(r"(?m)^\s*Behavior\s*=\s*LifetimeUpdate\b", lf)
    assert lf.count("LifetimeUpdate") == 1     # only the header comment
    assert not re.search(r"(?m)^\s*Behavior\s*=\s*MaxHealthUpgrade\b", lf)
    assert lf.count("MaxHealthUpgrade") == 1   # only the header comment
    assert lf.count("UpgradeCameo1") == 1      # only the header comment
    assert "OBJECT:TankSurveillanceUAV" in lf

    # exact diff audit vs donor
    dl = to_lf(donor_raw)
    diff = unified(dl, lf)
    added = Counter(l[1:] for l in diff if l.startswith("+"))
    removed = Counter(l[1:] for l in diff if l.startswith("-"))
    exp_removed = Counter([
        "Object AmericaVehicleSpyDrone ;; Global Hawk",
        "  UpgradeCameo1 = Upgrade_AmericaDroneArmor",
        "  DisplayName      = OBJECT:SpyDrone",
        "  Side = America",
        "  VisionRange     = 250",
        "    FinalVision = 250.0 ",
        "  Behavior = MaxHealthUpgrade ModuleTag_10",
        "    TriggeredBy   = Upgrade_AmericaDroneArmor",
        "    AddMaxHealth  = 50.0",
        "    ChangeType    = ADD_CURRENT_HEALTH_TOO   ;Choices are PRESERVE_RATIO, ADD_CURRENT_HEALTH_TOO, and SAME_CURRENTHEALTH",
        "  End",
    ])
    exp_added = Counter(UAV_HEADER.rstrip("\n").split("\n") + [
        "Object Tank_ChinaSurveillanceUAV ;; Global Hawk",
        "  DisplayName      = OBJECT:TankSurveillanceUAV",
        "  Side = ChinaTankGeneral",
        "  VisionRange     = 350",
        "    FinalVision = 400.0 ",
    ])
    assert removed == exp_removed, (removed - exp_removed, exp_removed - removed)
    assert added == exp_added, (added - exp_added, exp_added - added)
    assert end_lines(dl) - end_lines(lf) == 1   # exactly the dropped module's End
    print("  drone clone diff audit OK (5 changed lines + header; armor-upgrade "
          "hooks dropped; block balance -1 End as expected)")


def verify_cross_refs(patched, sources):
    cb, up = patched[CB_PATH], to_lf(patched[UPG_PATH])
    sp, ocl = to_lf(patched[SP_PATH]), patched[OCL_PATH]
    s, ic = patched[STR_PATH], to_lf(patched[IC_PATH])
    uav = to_lf(patched[UAV_PATH])

    # research button <-> upgrade <-> strings
    m = re.search(r"(?ms)^CommandButton %s\s*$.*?^End" % BTN_RESEARCH, cb)
    assert m and ("Upgrade       = %s\n" % UPG) in m.group(0)
    assert "Command       = PLAYER_UPGRADE" in m.group(0)
    # deploy button <-> power + NEED_UPGRADE <-> upgrade
    m = re.search(r"(?ms)^CommandButton %s\s*$.*?^End" % BTN_DEPLOY, cb)
    assert m and ("SpecialPower      = %s\n" % POWER) in m.group(0)
    assert "NEED_TARGET_POS" in m.group(0) and "NEED_UPGRADE" in m.group(0)
    assert ("Upgrade           = %s\n" % UPG) in m.group(0)
    assert "NEED_SPECIAL_POWER_SCIENCE" not in m.group(0)
    # upgrade block
    m = re.search(r"(?ms)^Upgrade %s\s*$.*?^End" % UPG, up)
    assert m and "Type               = PLAYER" in m.group(0)
    assert "BuildCost          = 1000" in m.group(0)
    assert "BuildTime          = 30.0" in m.group(0)
    # special power block
    m = re.search(r"(?ms)^SpecialPower %s\s*$.*?^End" % POWER, sp)
    assert m and "Enum                    = SPECIAL_SPY_DRONE" in m.group(0)
    assert "ReloadTime              = 120000" in m.group(0)
    assert "RequiredScience" not in m.group(0)
    assert "ShortcutPower" not in m.group(0)
    # OCL block -> object
    m = re.search(r"(?ms)^ObjectCreationList %s\s*$.*?^End$" % OCL_NAME, ocl)
    assert m and ("ObjectNames = %s\n" % UAV_OBJ) in m.group(0)
    # IC module -> power -> OCL -> object closure
    assert ("SpecialPowerTemplate = %s\n" % POWER) in ic
    assert ("OCL                  = %s\n" % OCL_NAME) in ic
    assert re.search(r"(?m)^Object %s\b" % UAV_OBJ, uav)
    # strings for every new label
    for lbl in ("OBJECT:TankSurveillanceUAV", "UPGRADE:KwaiUAVProgram",
                "CONTROLBAR:UpgradeKwaiUAVProgram",
                "CONTROLBAR:TooltipUpgradeKwaiUAVProgram",
                "CONTROLBAR:KwaiUAVDeploy", "CONTROLBAR:TooltipKwaiUAVDeploy"):
        assert ("\n%s\n" % lbl) in s, "missing string: " + lbl
    # cameo + donor art/sound/locomotor/armor closure in effective data
    assert cb.count("SASienceSpyDrone") >= 5   # 3 pre-existing + our 2
    for path, needle in (
            ("Data\\INI\\Locomotor.ini", "Locomotor GlobalHawkLocomtor"),
            ("Data\\INI\\Armor.ini", "Armor Genpower_AirplaneArmor"),
            ("Data\\INI\\Voice.ini", "AudioEvent SentryDroneVoiceCreate"),
            ("Data\\INI\\SoundEffects.ini", "AudioEvent SentryDroneVoiceSelect"),
            ("Data\\INI\\SoundEffects.ini", "AudioEvent GattlingDroneMoveStart"),
            ("Data\\INI\\SoundEffects.ini", "AudioEvent SpyDroneCreate"),
            ("Data\\INI\\MappedImages\\TextureSize_512\\SAUserInterface512.INI",
             "MappedImage SAScout_L"),
            ("Data\\INI\\MappedImages\\TextureSize_512\\SWUserInterface512_5.INI",
             "MappedImage SASienceSpyDrone"),
    ):
        data = EFFECTIVE(path)
        assert data and needle in to_lf(data), (path, needle)
    assert "ObjectCreationList OCL_AmericaScoutDroneExplode" in ocl
    print("  cross-reference closure OK (buttons<->upgrade<->power<->OCL<->object"
          "<->strings<->cameos<->sounds<->locomotor<->armor<->death OCL)")


def verify_sibling_appendices(cb, s, up, sp, ocl):
    assert cb.count("CommandButton Tank_Command_UpgradeKwai") == 13  # 10 doctrine + 2 basetech + ours
    assert re.search(r"(?m)^CommandButton Tank_Command_ConstructChinaVehicleScoutCar\s*$", cb)
    assert s.count("\nUPGRADE:Kwai") == 13
    assert ("\nOBJECT:JS7\n") in s                       # chaos-units strings
    assert "Upgrade Tank_Upgrade_KwaiAutoRepair" in to_lf(up)     # basetech
    assert "Upgrade Tank_Upgrade_KwaiVehicleArmor4" in to_lf(up)  # doctrine
    assert "SpecialPower SpecialPowerSpyDrone" in to_lf(sp)       # donor intact
    assert "ObjectCreationList SUPERWEAPON_GrantVeterancy" in ocl  # chaos tail
    print("  sibling appendices OK (CommandButton / Generals.str / Upgrade / "
          "SpecialPower / OCL)")


# ---------------------------------------------------------------------- main
EFFECTIVE = None  # set in main


def main():
    global EFFECTIVE
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

    EFFECTIVE = lambda p: effective(p)[0]  # noqa: E731

    sources = {}
    for path, owner in OWNERS.items():
        data, got = effective(path)
        assert data is not None, "effective source not found: " + path
        assert got == owner, "ownership drift for %s: %s (expected %s)" % (
            path, got, owner)
        sources[path] = data
    print("effective-file ownership verified (%d files)" % len(sources))

    # the new object INI path must be unclaimed in every archive of both dirs
    for d in (SPE_DIR, SHW_DIR):
        for a in (f for f in os.listdir(d) if f.lower().endswith(".big")
                  and f.lower() != OUT_NAME.lower()):
            for e in read_big(os.path.join(d, a)):
                assert e.path.lower() != UAV_PATH.lower(), (d, a)
    print("new INI path unclaimed: " + UAV_PATH)

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
    verify_propcenter_full(to_lf(sources[CS_PATH]))

    # drone model closure: ShockWave ships the Global Hawk art
    w3d = read_big(os.path.join(SPE_DIR, "!ShwW3D.big"))
    w3d_names = {e.path.lower() for e in w3d}
    assert "art\\w3d\\avspydr.w3d" in w3d_names
    assert "art\\w3d\\avspydr_d.w3d" in w3d_names
    print("drone model closure OK (AVSpyDr / AVSpyDr_d in !ShwW3D.big)")

    # ---- build the shipped files
    patched = {
        CS_PATH: patch_commandset(sources[CS_PATH]),   # LF file
        CB_PATH: sources[CB_PATH] + from_lf(CB_APPENDIX, eol_of(sources[CB_PATH])),
        UPG_PATH: sources[UPG_PATH] + from_lf(UPGRADE_APPENDIX, eol_of(sources[UPG_PATH])),
        SP_PATH: sources[SP_PATH] + from_lf(SP_APPENDIX, eol_of(sources[SP_PATH])),
        OCL_PATH: sources[OCL_PATH] + from_lf(OCL_APPENDIX, eol_of(sources[OCL_PATH])),
        STR_PATH: sources[STR_PATH] + from_lf(STR_APPENDIX, eol_of(sources[STR_PATH])),
        IC_PATH: patch_ic(sources[IC_PATH]),
        UAV_PATH: build_uav(sources[DONOR_PATH]),
    }

    # ---- append-only files: base bytes identical
    for path in (CS_PATH, CB_PATH, UPG_PATH, SP_PATH, OCL_PATH, STR_PATH):
        assert patched[path].startswith(sources[path]), path
    print("append-only base-byte identity OK (CommandSet, CommandButton, "
          "Upgrade, SpecialPower, OCL, Generals.str)")

    # ---- block-balance deltas (End-line counts)
    for path, delta in ((CS_PATH, 4), (CB_PATH, 2), (UPG_PATH, 1),
                        (SP_PATH, 1), (OCL_PATH, 2), (IC_PATH, 2)):
        d = end_lines(to_lf(patched[path])) - end_lines(to_lf(sources[path]))
        assert d == delta, (path, d, delta)
    assert patched[STR_PATH].count("\nEND\n") - sources[STR_PATH].count("\nEND\n") == 6
    print("block-balance deltas OK (+4 sets, +2 buttons, +1 upgrade, +1 power, "
          "+2 OCL Ends, +2 IC modules, +6 STR entries)")

    # ---- IC diff audit: exactly 5 renamed lines + the 2 inserted modules
    diff = unified(to_lf(sources[IC_PATH]), to_lf(patched[IC_PATH]))
    removed = Counter(l[1:] for l in diff if l.startswith("-"))
    added = Counter(l[1:] for l in diff if l.startswith("+"))
    exp_removed = Counter([
        "  CommandSet        = ChinaInternetCenterCommandSetOne",
        "    CommandSet = ChinaInternetCenterCommandSetOneUpgrade",
        "    CommandSet = ChinaInternetCenterCommandSetTwo",
    ]) + Counter({"    CommandSetAlt = ChinaInternetCenterCommandSetTwoUpgrade": 2})
    exp_added = Counter([
        "  CommandSet        = Tank_ChinaInternetCenterCommandSetOne",
        "    CommandSet = Tank_ChinaInternetCenterCommandSetOneUpgrade",
        "    CommandSet = Tank_ChinaInternetCenterCommandSetTwo",
    ]) + Counter({"    CommandSetAlt = Tank_ChinaInternetCenterCommandSetTwoUpgrade": 2}) \
      + Counter(IC_NEW_MODULES.rstrip("\n").split("\n"))
    assert removed == exp_removed, (removed - exp_removed, exp_removed - removed)
    assert added == exp_added, (added - exp_added, exp_added - added)
    print("InternetCenter.ini diff audit OK (5 set references repointed, "
          "2 modules inserted, nothing else)")

    # ---- CommandSet.ini appended-region audit: only our 4 sets + comments
    tail = patched[CS_PATH][len(sources[CS_PATH]):]
    assert tail.count("\nCommandSet ") == 4
    for n in NEW_SETS:
        assert ("\nCommandSet %s\n" % n) in tail or ("\nCommandSet %s \n" % n) in tail \
            or re.search(r"(?m)^CommandSet %s[ \t]*$" % n, tail), n
    print("CommandSet.ini appended-region audit OK (exactly the 4 Tank_ IC clones)")

    # ---- content + survival verification on final text
    verify_cs_survival(patched[CS_PATH])
    verify_ic(patched[IC_PATH])
    verify_uav(patched[UAV_PATH], sources[DONOR_PATH])
    verify_cross_refs(patched, sources)
    verify_sibling_appendices(patched[CB_PATH], patched[STR_PATH],
                              patched[UPG_PATH], patched[SP_PATH],
                              patched[OCL_PATH])
    # every button referenced in the new sets resolves to a CommandButton
    cb_names = set(re.findall(r"(?m)^CommandButton\s+(\S+)", patched[CB_PATH]))
    for name, slots in parse_sets(to_lf(patched[CS_PATH])).items():
        if name in NEW_SETS:
            for b in slots.values():
                assert b in cb_names, (name, b)
    print("  every button in the 4 new sets resolves to a CommandButton")

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
        assert after.lower() == "zzz-zzzzzkwairoster.big", listing
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
        verify_cs_survival(find_entry(back, CS_PATH).data.decode("latin-1"),
                           installed=True)
        verify_ic(find_entry(back, IC_PATH).data.decode("latin-1"))
        verify_uav(find_entry(back, UAV_PATH).data.decode("latin-1"),
                   sources[DONOR_PATH])
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
