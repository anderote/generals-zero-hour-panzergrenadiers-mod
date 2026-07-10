#!/usr/bin/env python3
"""Build zzyzzzzzz_EmperorBunker.big — gives Kwai's EMPEROR tank
(Tank_ChinaTankEmperor) a 10-man infantry bunker bay (passengers fire out)
while preserving its built-in propaganda tower and Gattling cannon upgrade.

Emperor architecture (from the effective Emperor.ini, zzx_ChinaTankBuff.big):
  - The propaganda tower is NOT a rider: it is a PropagandaTowerBehavior
    module directly on the tank ("AffectsSelf = Yes ; Needs this since Tower
    is not seperate object for Emperor").  Untouched by this mod.
  - The Gattling cannon upgrade IS a rider: ObjectCreationUpgrade ->
    OCL_Tank_OverlordGattlingCannon -> Tank_ChinaTankOverlordGattlingCannon
    (PORTABLE_STRUCTURE, W3DDependencyModelDraw AttachToBoneInContainer =
    FIREPOINT01) entering via ContainInsideSourceObject into the tank's
    OverlordContain ModuleTag_06 (Slots = 1, PORTABLE_STRUCTURE only).

Contain design: swap OverlordContain -> HelixContain (same module the retail
Helix uses to carry infantry AND a gattling addon simultaneously).  Engine
source facts (GeneralsX GeneralsMD tree, read-only):
  - HelixContain.cpp: a PORTABLE_STRUCTURE is stored in a dedicated
    m_portableStructureID rider slot OUTSIDE the passenger list; accepted
    regardless of AllowInsideKindOf; consumes no seats; never appears on
    exit/evacuate buttons; ALWAYS allowed to fire (comment literally says
    "RIDERS ARE ALWAYS ALLOWED TO FIRE (GATTLING CANNONS)").
  - HelixContain::update() syncs the rider to hull position/orientation --
    byte-for-byte the same semantics as GeneralsX's own POSIX bugfix in
    OverlordContain::syncPortablePosition() (bone queries are broken on
    POSIX), so dropping OverlordContain changes nothing positionally.
  - W3DOverlordTankDraw (kept) finds the rider via friend_getRider(), which
    HelixContain implements, and clears the W3DDependencyModelDraw
    dependency -- gattling visuals intact.
  - HelixContain::redeployOccupants() overrides the base entirely (hull pos
    +8z), so putObjAtNextFirePoint / FIREPOINT bone placement is never used
    for passengers -- the POSIX bone-coordinate bug cannot bite even though
    NVEmperor HAS a FIREPOINT01 bone.
  - Dropped fields: PassengersInTurret (OpenContain field consumed only by
    putObjAtNextFirePoint, unreachable under HelixContain) and
    ExperienceSinkForRider (OverlordContain-ONLY field -- would be an INI
    parse error under HelixContain; gattling kills now give XP to the rider
    instead of the tank, same as the retail Helix gattling upgrade).

Command-set layout (engine-source verified):
  - UI shows 14 buttons; MAX_COMMANDS_PER_SET=18 but slots 15+ have no
    windows (verified by the kwai-artillery mod against ControlBar.wnd and
    ControlBarPro's).
  - ControlBar::doTransportInventoryUI (ControlBarCommand.cpp) fills
    firstInventoryIndex..lastInventoryIndex SEQUENTIALLY with passenger
    cameos -- a non-exit button inside that range would be clobbered, so
    exit buttons must be contiguous.
  - populateInvDataCallback: passengers beyond the last exit button hit
    "if (currIndex > maxIndex) { DEBUG_CRASH(...); return; }".  In this
    build DEBUG_CRASH == ((void)0): CMakeCache.txt (build/macos-vulkan) has
    RTS_BUILD_OPTION_DEBUG=OFF -> RTS_RELEASE -> no ALLOW_DEBUG_UTILS ->
    Debug.h line 205 "#define DEBUG_CRASH(m) ((void)0)".  Overflow
    passengers simply get no individual button; Evacuate still unloads all.
  - Emperor set uses 1 (taunt), 6 (gattling upgrade), 11/13/14.  Max
    contiguous free run keeping everything = 8 slots by moving the gattling
    upgrade 6 -> 10 (the Overlord-family upgrade slot, same one the
    prop-tower mods use):  exits at 2-9, gattling at 10, Evacuate at 12.
    9 exits (2-10) would leave no slot for mandatory Evacuate. 10 seats vs
    8 exit buttons is safe per the above.

Sources (effective-file rule, highest-priority archive containing each):
  Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini <- zzx_ChinaTankBuff.big
      (CRLF file; carries the tank-buff MaxHealth 1320 -- asserted)
  Data\\INI\\CommandSet.ini <- zzyzzzzz_KwaiArtillery.big
      (LF file; carries kwai-artillery / prop-tower / china-bunkers /
       mammoth-bunker hunks -- all asserted to survive)
No other files are shipped (Command_TransportExit / Command_Evacuate are
existing generic buttons in the effective CommandButton.ini).
"""

import os
import sys
import difflib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzyzzzzzz_EmperorBunker.big"

EMP_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini"
CS_PATH = "Data\\INI\\CommandSet.ini"


def replace_once(s: str, old: str, new: str) -> str:
    assert s.count(old) == 1, "expected exactly one occurrence of %r..." % old[:70]
    return s.replace(old, new)


# ---------------------------------------------------------------- Emperor.ini
# Exact current block (CRLF, note trailing space after "(redirects like tunnel)").
OLD_CONTAIN = (
    "  Behavior = OverlordContain ModuleTag_06 ; Like Transport, but when full,"
    " passes transport queries along to first passenger (redirects like tunnel) \r\n"
    "    Slots                 = 1\r\n"
    "    DamagePercentToUnits        = 100%\r\n"
    "    AllowInsideKindOf     = PORTABLE_STRUCTURE\r\n"
    "    PassengersAllowedToFire = Yes\r\n"
    "    PassengersInTurret = Yes ; My passengers ride in my turret, that's where the Firepoint bones are\r\n"
    "    ExperienceSinkForRider = Yes ; I get the Exp for things my turret friend kills\r\n"
    "  End\r\n"
)

NEW_CONTAIN = (
    "  Behavior = HelixContain ModuleTag_06 ; EmperorBunker mod: was OverlordContain."
    " Gattling rider lives in HelixContain's dedicated rider slot; infantry use the passenger seats.\r\n"
    "    Slots                   = 10\r\n"
    "    DamagePercentToUnits    = 0%\r\n"
    "    AllowInsideKindOf       = INFANTRY\r\n"
    "    ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT\r\n"
    "    EnterSound              = GarrisonEnter\r\n"
    "    ExitSound               = GarrisonExit\r\n"
    "    ExitDelay               = 100\r\n"
    "    NumberOfExitPaths       = 1\r\n"
    "    PassengersAllowedToFire = Yes\r\n"
    "  End\r\n"
)


def patch_emperor(text: str) -> str:
    return replace_once(text, OLD_CONTAIN, NEW_CONTAIN)


# ---------------------------------------------------------------- CommandSet
OLD_EMPEROR_SET = (
    "CommandSet Tank_ChinaTankEmperorDefaultCommandSet\n"
    "  1  = Command_OverlordTaunt\n"
    "  6  = Tank_Command_UpgradeChinaOverlordGattlingCannon\n"
    "  11 = Command_AttackMove\n"
    "  13 = Command_Guard\n"
    "  14 = Command_Stop\n"
    "End\n"
)

NEW_EMPEROR_SET = (
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
    "End\n"
)


def patch_commandset(text: str) -> str:
    return replace_once(text, OLD_EMPEROR_SET, NEW_EMPEROR_SET)


# -------------------------------------------------------------- verification
def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def verify_emperor_survival(text):
    """Prior-layer content that must remain in the shipped Emperor.ini."""
    checks = {
        # zzx_ChinaTankBuff: buffed health (SPE base is 1100)
        "china-tank-buff MaxHealth 1320":
            "    MaxHealth       = 1320.0\r\n"
            "    InitialHealth   = 1320.0\r\n",
        # built-in propaganda tower (module on the tank itself)
        "propaganda tower behavior":
            "  Behavior        = PropagandaTowerBehavior ModulePropaganda_15\r\n",
        "propaganda tower AffectsSelf":
            "    AffectsSelf                   = Yes",
        # gattling upgrade chain
        "gattling ObjectCreationUpgrade":
            "    UpgradeObject = OCL_Tank_OverlordGattlingCannon\r\n"
            "    TriggeredBy   = Upgrade_ChinaOverlordGattlingCannon\r\n",
        "gattling WeaponSetUpgrade":
            "  Behavior = WeaponSetUpgrade ModuleTag_WeaponSetUpgrade01\r\n"
            "    TriggeredBy = Upgrade_ChinaOverlordGattlingCannon\r\n",
        "gattling ProductionUpdate (OBJECT_UPGRADE queue)":
            "  Behavior = ProductionUpdate ModuleTag_10\r\n",
        # draw module that renders the rider (friend_getRider path)
        "W3DOverlordTankDraw kept":
            "  Draw = W3DOverlordTankDraw ModuleTag_01\r\n",
        # new contain
        "HelixContain in place":
            "  Behavior = HelixContain ModuleTag_06",
        "10 passenger slots":
            "    Slots                   = 10\r\n",
    }
    for label, needle in checks.items():
        assert needle in text, "EMPEROR SURVIVAL FAILED: " + label
        print("  emperor OK:", label)
    assert "Behavior = OverlordContain" not in text, "old contain still present"
    assert "ExperienceSinkForRider" not in text, "OverlordContain-only field leaked"
    assert "PassengersInTurret" not in text, "OverlordContain-era field leaked"


def verify_commandset_survival(cs_text):
    """Prior-layer hunks that must still be in the shipped CommandSet.ini."""
    checks = {
        # zzyzzzzz_KwaiArtillery: factory slots 11-12 (both variants => count 2)
        ("Kwai artillery factory slots 11-12", 2):
            "  11 = Tank_Command_ConstructChinaVehicleInfernoCannon\n"
            "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n",
        # zzyzzzzz_KwaiArtillery: relocated upgrades at PropCenter 4-5 (both variants)
        ("Kwai artillery prop-center slots 4-5", 2):
            "  4  = Command_UpgradeChinaChainGuns\n"
            "  5  = Command_UpgradeChinaBlackNapalm\n",
        # zzy_MammothBunker: Mammoth transport slots 4-8
        ("Mammoth slots 4-8", 1):
            "  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n"
            "  8  = Command_Evacuate\n",
        # zzyy_ChinaBunkers + zzyzz_PropTowers: Kwai Battlemaster exits + tower
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
        ("vanilla Battlemaster exits", 1):
            "CommandSet ChinaVehicleBattleMasterCommandSet\n"
            "  1  = Command_TransportExit\n",
    }
    for (label, count), needle in checks.items():
        assert cs_text.count(needle) == count, "CS SURVIVAL FAILED: " + label
        print("  commandset OK:", label)


def block_starts(text, opener):
    return sum(1 for l in text.splitlines() if l.strip().startswith(opener + " "))


def main():
    # ---- read effective sources (effective-file rule)
    emp_src = find_entry(read_big(os.path.join(SPE_DIR, "zzx_ChinaTankBuff.big")),
                         EMP_PATH).data.decode("latin-1")
    cs_src = find_entry(read_big(os.path.join(SPE_DIR, "zzyzzzzz_KwaiArtillery.big")),
                        CS_PATH).data.decode("latin-1")

    # sanity: nothing between zzx_ChinaTankBuff and the top owns Emperor.ini,
    # and nothing above zzyzzzzz_KwaiArtillery owns CommandSet.ini
    for arch, path, expect in (
            ("zzyzzzz_StatTune.big", EMP_PATH, False),
            ("zzyzzz_CoaxMG.big", EMP_PATH, False),
            ("zzyzz_PropTowers.big", EMP_PATH, False),
            ("zzyzy_NoAISuperweapons.big", EMP_PATH, False),
            ("zzyz_GattlingBuff.big", EMP_PATH, False),
            ("zzyy_ChinaBunkers.big", EMP_PATH, False),
            ("zzy_MammothBunker.big", EMP_PATH, False),
            ("zzyzzzz_StatTune.big", CS_PATH, False)):
        entries = read_big(os.path.join(SPE_DIR, arch))
        has = any(e.path == path for e in entries)
        assert has == expect, "%s ownership of %s changed!" % (arch, path)
    print("effective-file ownership verified")

    # ---- patch
    emp_new = patch_emperor(emp_src)
    cs_new = patch_commandset(cs_src)

    # ---- diff audit: only the intended hunks
    emp_diff = unified(emp_src, emp_new)
    print("Emperor.ini diff (%d lines):" % len(emp_diff))
    for l in emp_diff:
        print("   ", l)
    exp_emp = unified(OLD_CONTAIN.replace("\r\n", "\n"),
                      NEW_CONTAIN.replace("\r\n", "\n"))
    assert sorted(emp_diff) == sorted(exp_emp), "unexpected Emperor.ini diff"

    cs_diff = unified(cs_src, cs_new)
    print("CommandSet.ini diff (%d lines):" % len(cs_diff))
    for l in cs_diff:
        print("   ", l)
    # difflib reports "11 = Command_AttackMove" as moved (removed + re-added)
    # because eight insertions land between slot 1 and it; net change is nil.
    exp_cs = [
        "-  6  = Tank_Command_UpgradeChinaOverlordGattlingCannon",
        "-  11 = Command_AttackMove",
        "+  2  = Command_TransportExit",
        "+  3  = Command_TransportExit",
        "+  4  = Command_TransportExit",
        "+  5  = Command_TransportExit",
        "+  6  = Command_TransportExit",
        "+  7  = Command_TransportExit",
        "+  8  = Command_TransportExit",
        "+  9  = Command_TransportExit",
        "+  10 = Tank_Command_UpgradeChinaOverlordGattlingCannon",
        "+  11 = Command_AttackMove",
        "+  12 = Command_Evacuate",
    ]
    assert sorted(cs_diff) == sorted(exp_cs), "unexpected CommandSet diff"

    # ---- block balance deltas (no structural drift)
    assert block_starts(emp_new, "Behavior") == block_starts(emp_src, "Behavior")
    assert emp_new.count("\r\nEnd\r\n") == emp_src.count("\r\nEnd\r\n")
    assert emp_new.count("  End\r\n") == emp_src.count("  End\r\n")
    assert block_starts(cs_new, "CommandSet") == block_starts(cs_src, "CommandSet")
    assert cs_new.count("\nEnd\n") == cs_src.count("\nEnd\n")
    print("block balance OK")

    # ---- prior-layer survival
    verify_emperor_survival(emp_new)
    verify_commandset_survival(cs_new)

    # ---- generic buttons must exist in the effective CommandButton.ini
    cb = find_entry(read_big(os.path.join(SPE_DIR, "zzyzzzzz_KwaiArtillery.big")),
                    "Data\\INI\\CommandButton.ini").data.decode("latin-1")
    assert "CommandButton Command_TransportExit" in cb
    assert "CommandButton Command_Evacuate" in cb
    assert "CommandButton Tank_Command_UpgradeChinaOverlordGattlingCannon" in cb
    print("generic command buttons present in effective CommandButton.ini")

    # ---- package
    entries = [
        BigEntry(EMP_PATH, emp_new.encode("latin-1")),
        BigEntry(CS_PATH, cs_new.encode("latin-1")),
    ]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_local)
    print("wrote", out_local, os.path.getsize(out_local), "bytes")

    # ---- sort-order check (engine loads alphabetically; later wins).
    # Case-insensitive, must land after zzyzzzzz_KwaiArtillery, before zzz_*.
    names = ["zzyzzzzz_KwaiArtillery.big", OUT_NAME,
             "zzz_ControlBarPro2160ZH.big", "zzz_ControlBarProZH.big"]
    assert sorted(names, key=str.lower) == names, sorted(names, key=str.lower)
    print("sort order OK:", " < ".join(names))

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
        # re-run survival checks on the installed bytes
        verify_emperor_survival(find_entry(back, EMP_PATH).data.decode("latin-1"))
        verify_commandset_survival(find_entry(back, CS_PATH).data.decode("latin-1"))
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
