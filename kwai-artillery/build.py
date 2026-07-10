#!/usr/bin/env python3
"""Build zzyzzzzz_KwaiArtillery.big — lets China's Tank General (Kwai) build
vanilla China's Nuke Cannon and Inferno Cannon from his War Factory.

Idiom: ShockWave's own cross-faction "build stub" pattern — a minimal Object
with BuildCost/BuildTime/Prerequisites/Side and `BuildVariations = <vanilla
object>`; the factory queues the stub but spawns the vanilla unit (exactly
how Tank_ChinaVehicleHackerVan, Tank_ChinaVehicleListeningOutpost,
Infa_ChinaVehicleInfernoCannon etc. already work).

Sources (effective-file rule, highest-priority archive containing each file):
  - Data\\INI\\CommandSet.ini      <- zzyzz_PropTowers.big
  - Data\\INI\\CommandButton.ini   <- zz_SPE_Shw_ini.big
  - stubs are NEW files (no archive ships Tank\\Vehicles\\{NukeCannon,InfernoCannon}.ini)

Command-set slot decision: both Tank war-factory sets use slots 1-14 fully and
the UI (ShockWave's ControlBar.wnd AND ControlBarPro's) has exactly 14
ButtonCommand windows (engine MAX_COMMANDS_PER_SET=18 is "script only" above
14), so slots 15+ never display.  We free slots 11-12 by moving the two
PLAYER_UPGRADE buttons (Chain Guns, Black Napalm) to Kwai's Propaganda Center
(slots 4-5, currently empty; it already hosts research via ProductionUpdate).
Slot 13 (per-building mines OBJECT_UPGRADE) and 14 (Sell) stay put.
"""

import os
import sys
import difflib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzyzzzzz_KwaiArtillery.big"

CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
NUKE_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\NukeCannon.ini"
INFERNO_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\InfernoCannon.ini"


def edit_block(text: str, header: str, fn):
    """Apply fn to the block `CommandSet <header> ... End`; assert exactly one."""
    needle = "CommandSet " + header + "\n"
    start = text.index(needle)
    assert text.count(needle) == 1, header
    end = text.index("\nEnd", start) + len("\nEnd")
    block = text[start:end]
    new_block = fn(block)
    assert new_block != block, "no change made in " + header
    return text[:start] + new_block + text[end:]


def replace_once(s: str, old: str, new: str) -> str:
    assert s.count(old) == 1, "expected exactly one occurrence of %r" % old
    return s.replace(old, new)


# ---------------------------------------------------------------- CommandSet
def patch_commandset(text: str) -> str:
    # War factory (both variants): slots 11/12 upgrades -> artillery builds
    def factory(block):
        block = replace_once(
            block,
            "  11 = Command_UpgradeChinaChainGuns\n",
            "  11 = Tank_Command_ConstructChinaVehicleInfernoCannon\n")
        block = replace_once(
            block,
            "  12 = Command_UpgradeChinaBlackNapalm\n",
            "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n")
        return block

    # Propaganda Center (both variants): host the two relocated upgrades
    def propcenter(block):
        return replace_once(
            block,
            "  3  = Command_UpgradeChinaNeutronBomb\n",
            "  3  = Command_UpgradeChinaNeutronBomb\n"
            "  4  = Command_UpgradeChinaChainGuns\n"
            "  5  = Command_UpgradeChinaBlackNapalm\n")

    text = edit_block(text, "Tank_ChinaWarFactoryCommandSet", factory)
    text = edit_block(text, "Tank_ChinaWarFactoryCommandSetUpgrade", factory)
    text = edit_block(text, "Tank_ChinaPropagandaCenterCommandSet", propcenter)
    text = edit_block(text, "Tank_ChinaPropagandaCenterCommandSetUpgrade", propcenter)
    return text


# ------------------------------------------------------------- CommandButton
NEW_BUTTONS = """\
CommandButton Tank_Command_ConstructChinaVehicleInfernoCannon
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = Tank_ChinaVehicleInfernoCannon
  TextLabel     = CONTROLBAR:ConstructChinaVehicleInfernoCannon
  ButtonImage   = SNInferno
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildInfernoCannon
End

CommandButton Tank_Command_ConstructChinaVehicleNukeLauncher
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = Tank_ChinaVehicleNukeLauncher
  TextLabel     = CONTROLBAR:ConstructChinaVehicleNukeLauncher
  ButtonImage   = SNNukeCannon
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildNukeLauncher
End

"""

CB_ANCHOR = """\
CommandButton Tank_Command_ConstructChinaVehicleHackerVan
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = Tank_ChinaVehicleHackerVan
  TextLabel     = CONTROLBAR:ConstructChinaVehicleHackerVan
  ButtonImage   = HackVan
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipChinaVehicleHackerVan
End

"""


def patch_commandbutton(text: str) -> str:
    for name in ("Tank_Command_ConstructChinaVehicleInfernoCannon",
                 "Tank_Command_ConstructChinaVehicleNukeLauncher"):
        assert name not in text, name + " already exists"
    return replace_once(text, CB_ANCHOR, CB_ANCHOR + NEW_BUTTONS)


# ------------------------------------------------------------- object stubs
# Mirrors ShockWave's own Kwai stubs (Tank_ChinaVehicleHackerVan /
# Tank_ChinaVehicleListeningOutpost) and the vanilla units' cost/time/KindOf.
# Vanilla ChinaVehicleInfernoCannon / ChinaVehicleNukeLauncher both require
# ChinaWarFactory + ChinaPropagandaCenter -> translated to Tank_ equivalents.
INFERNO_STUB = """\
; Kwai Artillery mini-mod: build stub letting China's Tank General (Kwai)
; produce the vanilla China Inferno Cannon from his War Factory.
; Same BuildVariations idiom ShockWave uses for Tank_ChinaVehicleHackerVan etc.

Object Tank_ChinaVehicleInfernoCannon

  ; *** ART Parameters ***
  SelectPortrait         = SNInferno_L
  ButtonImage            = SNInferno

  Draw = W3DModelDraw ModuleTag_01
    OkToChangeModelColor  = Yes
    DefaultConditionState
      Model               = NVInferno
      Turret              = Turret
      TurretPitch         = TurretEL
      WeaponFireFXBone    = PRIMARY Muzzle
      WeaponRecoilBone    = PRIMARY Barrel
      WeaponMuzzleFlash   = PRIMARY MuzzleFX
      WeaponLaunchBone    = PRIMARY Muzzle
    End
  End

  ; set cost and time fields here or else they won't work
  BuildCost          = 900
  BuildTime          = 15.0          ;in seconds

  Prerequisites
    Object        = Tank_ChinaWarFactory
    Object        = Tank_ChinaPropagandaCenter
  End

  Side = ChinaTankGeneral
  EditorSorting = VEHICLE
  BuildVariations = ChinaVehicleInfernoCannon

  KindOf = PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS VEHICLE SCORE

End
"""

NUKE_STUB = """\
; Kwai Artillery mini-mod: build stub letting China's Tank General (Kwai)
; produce the vanilla China Nuke Cannon from his War Factory.
; Same BuildVariations idiom ShockWave uses for Tank_ChinaVehicleHackerVan etc.

Object Tank_ChinaVehicleNukeLauncher

  ; *** ART Parameters ***
  SelectPortrait         = SNNukeCannon_L
  ButtonImage            = SNNukeCannon

  Draw = W3DModelDraw ModuleTag_01
    OkToChangeModelColor  = Yes
    DefaultConditionState
      Model               = NVNukeCn
      WeaponFireFXBone    = PRIMARY Muzzle
      WeaponLaunchBone    = PRIMARY Muzzle
    End
  End

  ; set cost and time fields here or else they won't work
  BuildCost       = 1600
  BuildTime       = 20.0          ;in seconds

  Prerequisites
    Object = Tank_ChinaWarFactory
    Object = Tank_ChinaPropagandaCenter
  End

  Side = ChinaTankGeneral
  EditorSorting = VEHICLE
  BuildVariations = ChinaVehicleNukeLauncher

  KindOf = PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS VEHICLE HUGE_VEHICLE SCORE

End
"""


# -------------------------------------------------------------- verification
def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def block_balance(text, opener):
    starts = sum(1 for l in text.splitlines() if l.startswith(opener + " "))
    ends = sum(1 for l in text.splitlines()
               if l == "End" or l.rstrip() == "End")
    return starts, ends


def verify_survival(cs_text):
    """Prior-layer hunks that must still be in the shipped CommandSet.ini."""
    checks = {
        # zzy_MammothBunker: Mammoth transport slots 4-8
        "Mammoth slots 4-8":
            "  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n"
            "  8  = Command_Evacuate\n",
        # zzyy_ChinaBunkers + zzyzz_PropTowers: Battlemaster exit + prop tower
        "Tank Battlemaster exit/prop-tower":
            "CommandSet Tank_ChinaVehicleBattleMasterCommandSet\n"
            "  1  = Command_TransportExit\n"
            "  2  = Command_TransportExit\n"
            "  3  = Command_TransportExit\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_Evacuate\n"
            "  10 = Command_UpgradeChinaOverlordPropagandaTower\n",
        # zzyzz_PropTowers: ERA variant command set
        "Tank Battlemaster ERA set":
            "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n",
        "vanilla Battlemaster exit/prop-tower":
            "CommandSet ChinaVehicleBattleMasterCommandSet\n"
            "  1  = Command_TransportExit\n",
    }
    for label, needle in checks.items():
        assert needle in cs_text, "SURVIVAL FAILED: " + label
        print("  survival OK:", label)


def main():
    # ---- read effective sources
    cs_src = find_entry(read_big(os.path.join(SPE_DIR, "zzyzz_PropTowers.big")),
                        CS_PATH).data.decode("latin-1")
    cb_src = find_entry(read_big(os.path.join(SPE_DIR, "zz_SPE_Shw_ini.big")),
                        CB_PATH).data.decode("latin-1")

    # ---- patch
    cs_new = patch_commandset(cs_src)
    cb_new = patch_commandbutton(cb_src)

    # ---- diff audit: only intended hunks
    cs_diff = unified(cs_src, cs_new)
    cb_diff = unified(cb_src, cb_new)
    print("CommandSet.ini diff (%d lines):" % len(cs_diff))
    for l in cs_diff:
        print("   ", l)
    exp_cs = sorted([
        "-  11 = Command_UpgradeChinaChainGuns",
        "+  11 = Tank_Command_ConstructChinaVehicleInfernoCannon",
        "-  12 = Command_UpgradeChinaBlackNapalm",
        "+  12 = Tank_Command_ConstructChinaVehicleNukeLauncher",
    ] * 2 + [
        "+  4  = Command_UpgradeChinaChainGuns",
        "+  5  = Command_UpgradeChinaBlackNapalm",
    ] * 2)
    assert sorted(cs_diff) == exp_cs, "unexpected CommandSet diff"
    print("CommandButton.ini diff: %d added lines, %d removed" % (
        sum(1 for l in cb_diff if l.startswith("+")),
        sum(1 for l in cb_diff if l.startswith("-"))))
    assert all(l.startswith("+") for l in cb_diff), "CommandButton must be add-only"
    assert len(cb_diff) == NEW_BUTTONS.count("\n"), "unexpected CommandButton diff size"

    # ---- block balance (delta vs source; the stock files themselves contain
    # commented/odd lines so absolute start==End equality does not hold)
    for label, text, src, opener, want in (
            ("CommandSet.ini", cs_new, cs_src, "CommandSet", 0),
            ("CommandButton.ini", cb_new, cb_src, "CommandButton", 2)):
        s, e = block_balance(text, opener)
        s0, e0 = block_balance(src, opener)
        print("%s blocks: %d starts / %d End lines (source %d/%d)" % (label, s, e, s0, e0))
        assert s - s0 == want, label + " unexpected block-start delta"
        assert e - e0 == want, label + " unexpected End delta"

    verify_survival(cs_new)

    # ---- package
    entries = [
        BigEntry(CS_PATH, cs_new.encode("latin-1")),
        BigEntry(CB_PATH, cb_new.encode("latin-1")),
        BigEntry(INFERNO_PATH, INFERNO_STUB.encode("latin-1")),
        BigEntry(NUKE_PATH, NUKE_STUB.encode("latin-1")),
    ]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_local)
    print("wrote", out_local, os.path.getsize(out_local), "bytes")

    # ---- sort-order check (engine: later-alphabetical wins)
    neighbors = sorted(["zzyzzzz_StatTune.big", OUT_NAME, "zzz_ControlBarProZH.big"])
    assert neighbors == ["zzyzzzz_StatTune.big", OUT_NAME, "zzz_ControlBarProZH.big"], neighbors
    print("sort order OK:", " < ".join(neighbors))

    # ---- install + re-read verification
    with open(out_local, "rb") as f:
        blob = f.read()
    for d in (SPE_DIR, SHW_DIR):
        dst = os.path.join(d, OUT_NAME)
        with open(dst, "wb") as f:
            f.write(blob)
        back = read_big(dst)
        assert [e.path for e in back] == [e.path for e in entries]
        for a, b in zip(back, entries):
            assert a.data == b.data, a.path
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
