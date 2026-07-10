#!/usr/bin/env python3
"""Build zzy_MammothBunker.big — gives General Ironside's Mammoth Tank an
infantry bunker bay (Overlord/Helix-style) for ShockWave on GeneralsX.

Reads the effective source INIs from the ShockWave archives, applies the
patches below, and writes/installs the output archive.
Run:  python3 build.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, find_entry, write_big_file  # noqa: E402

OUT_NAME = "zzy_MammothBunker.big"

# Effective-source order: SPE overlay first, then base ShockWave, then vanilla.
SOURCE_ARCHIVES = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zz_SPE_Shw_ini.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave/!Shw_ini.big"),
    os.path.expanduser("~/GeneralsX/GeneralsZH/INIZH.big"),
]

INSTALL_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
]

# ---------------------------------------------------------------------------
# Patch 1: Mammoth.ini — swap OverlordContain for HelixContain.
#
# HelixContain keeps the PORTABLE_STRUCTURE rider (the Energy Shield sphere
# dummy created by OCL_AmericaEnergyShieldUpgrade_Mammoth) in a dedicated
# rider slot OUTSIDE the passenger list, so Evacuate / exit buttons can never
# eject it, it is always allowed to fire (engine rule for riders), and it
# does not consume infantry slots.  Infantry ride in the 4 normal transport
# slots and may fire out (fires from vehicle center; AVMammoth has no
# FIREPOINT bones — the engine falls back gracefully, see
# OpenContain::putObjAtNextFirePoint).  W3DOverlordTankDraw finds the rider
# via ContainModuleInterface::friend_getRider(), which HelixContain
# implements, so the shield visuals are unaffected.
# ---------------------------------------------------------------------------
MAMMOTH_PATH = r"Data\INI\Object\USA\Armor\Vehicles\Mammoth.ini"

MAMMOTH_OLD = """\
  Behavior = OverlordContain ModuleTag_ArmorAddon01
    Slots                   = 1
    DamagePercentToUnits    = 100%
    AllowInsideKindOf       = PORTABLE_STRUCTURE
    PassengersAllowedToFire = Yes
  End
"""

MAMMOTH_NEW = """\
  Behavior = HelixContain ModuleTag_ArmorAddon01
    Slots                   = 4
    DamagePercentToUnits    = 0%
    AllowInsideKindOf       = INFANTRY PORTABLE_STRUCTURE
    ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT
    EnterSound              = GarrisonEnter
    ExitSound               = GarrisonExit
    ExitDelay               = 100
    NumberOfExitPaths       = 1
    PassengersAllowedToFire = Yes
  End
"""

# ---------------------------------------------------------------------------
# Patch 2: CommandSet.ini — add passenger exit buttons + evacuate to the
# Mammoth's command set (slots 4-8 were free; 12/14 max slots in use after).
# Command_TransportExit / Command_Evacuate are existing generic ShockWave
# buttons (SSEvacButton art, CONTROLBAR:TransportExit / CONTROLBAR:Evacuate
# labels) — no new CSF strings or art needed.  Exit buttons must be
# contiguous (ControlBar::doTransportInventoryUI assumes it).
# ---------------------------------------------------------------------------
COMMANDSET_PATH = r"Data\INI\CommandSet.ini"

COMMANDSET_OLD = """\
CommandSet Armor_AmericaTankPaladinCommandSet
  1  = Command_ConstructAmericaVehicleBattleDrone
  2  = Command_ConstructAmericaVehicleScoutDrone
  3  = Command_ConstructAmericaVehicleHellfireDrone
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

COMMANDSET_NEW = """\
CommandSet Armor_AmericaTankPaladinCommandSet
  1  = Command_ConstructAmericaVehicleBattleDrone
  2  = Command_ConstructAmericaVehicleScoutDrone
  3  = Command_ConstructAmericaVehicleHellfireDrone
  4  = Command_TransportExit
  5  = Command_TransportExit
  6  = Command_TransportExit
  7  = Command_TransportExit
  8  = Command_Evacuate
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

PATCHES = [
    (MAMMOTH_PATH, MAMMOTH_OLD, MAMMOTH_NEW),
    (COMMANDSET_PATH, COMMANDSET_OLD, COMMANDSET_NEW),
]


def effective_entry(internal_path):
    """Return (data, source_archive) for the highest-priority copy."""
    for arc in SOURCE_ARCHIVES:
        try:
            return find_entry(read_big(arc), internal_path).data, arc
        except (KeyError, FileNotFoundError):
            continue
    raise KeyError(internal_path)


def apply_patch(data: bytes, old: str, new: str) -> bytes:
    """Apply a patch written with \n, matching the file's own line endings."""
    for eol in ("\r\n", "\n"):
        old_b = old.replace("\n", eol).encode("latin-1")
        new_b = new.replace("\n", eol).encode("latin-1")
        if data.count(old_b) == 1:
            return data.replace(old_b, new_b)
    raise ValueError("patch target not found exactly once")


def main():
    entries = []
    for internal_path, old, new in PATCHES:
        data, src = effective_entry(internal_path)
        patched = apply_patch(data, old, new)
        entries.append(BigEntry(internal_path, patched))
        print(f"patched {internal_path}  (source: {src}, "
              f"{len(data)} -> {len(patched)} bytes)")

    out_path = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_path)
    print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes)")

    for d in INSTALL_DIRS:
        dest = os.path.join(d, OUT_NAME)
        shutil.copyfile(out_path, dest)
        print(f"installed {dest}")


if __name__ == "__main__":
    main()
