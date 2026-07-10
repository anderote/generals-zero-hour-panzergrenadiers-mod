#!/usr/bin/env python3
"""Build zzyy_ChinaBunkers.big — China mini-mod for ShockWave on GeneralsX.

Feature 1: every China Battlemaster tank variant gets an INNATE 4-soldier
           bunker bay (infantry ride inside, fire out, exit/evacuate buttons).
Feature 2: China Troop Crawler APCs let their passengers fire out.

Reads the EFFECTIVE source copy of every file it modifies (highest-priority
archive first), applies exact-text patches (fails loudly if upstream drifts),
verifies the china-tank-buff values survived, writes the output archive and
installs it into both mod directories.

Run:  python3 build.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, find_entry, write_big_file  # noqa: E402

OUT_NAME = "zzyy_ChinaBunkers.big"

# Effective-source order (highest priority first).  zzx_ChinaTankBuff.big
# carries the buffed Battlemaster/Ravage object files; zzy_MammothBunker.big
# carries the already-patched CommandSet.ini.  Our archive name zzyy_ sorts
# after both (and after zz_SPE_*) but before zzz_ControlBarPro*.
SOURCE_ARCHIVES = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzx_ChinaTankBuff.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzy_MammothBunker.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zz_SPE_Shw_ini.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave/!Shw_ini.big"),
]

INSTALL_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
]

# ---------------------------------------------------------------------------
# Feature 1 — Battlemaster bunker bay.
#
# ChinaTankBattleMaster_Var1 / Nuke_ / Spec_ (Ravage) have NO contain module
# and NO rider/W3DOverlordTankDraw, so they get a plain TransportContain
# (vanilla fire-out-transport idiom, e.g. GLA Battle Bus / Infa Troop
# Crawler).  Var2-4 are ObjectReskin of Var1 and inherit the module.
#
# Tank_ChinaTankBattleMaster is the Mammoth situation: W3DOverlordTankDraw +
# an OverlordContain armor-addon rider (ChinaTankArmorUpgradeAddon_
# BattleMaster, a PORTABLE_STRUCTURE spawned by OCL_BattleMasterArmorAddons
# via Upgrade_TankLightArmor, ContainInsideSourceObject).  Swapping in
# HelixContain keeps the rider in its dedicated portable-structure slot
# (outside the passenger list: never on exit buttons, doesn't consume
# infantry slots, W3DOverlordTankDraw still finds it via friend_getRider)
# while the 4 normal slots take infantry — same proven design as
# zzy_MammothBunker.
#
# Infantry fire from the hull center (no FIREPOINT bones in the Battlemaster
# models; the engine falls back gracefully, same as the Mammoth).
# ---------------------------------------------------------------------------

BUNKER_BLOCK = """\
  Behavior = TransportContain ModuleTag_BunkerBay01
    Slots                   = 4
    DamagePercentToUnits    = 0%
    AllowInsideKindOf       = INFANTRY
    ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT
    EnterSound              = GarrisonEnter
    ExitSound               = GarrisonExit
    ExitDelay               = 100
    NumberOfExitPaths       = 1
    PassengersAllowedToFire = Yes
  End
"""

# Unique per-file anchor: the FlammableUpdate block (occurs once per file,
# only in the main object; reskins/aliases carry no behavior modules).
FLAMMABLE_BLOCK = """\
  Behavior = FlammableUpdate ModuleTag_21
    AflameDuration = 5000         ; If I catch fire, I'll burn for this long...
    AflameDamageAmount = 3       ; taking this much damage...
    AflameDamageDelay = 500       ; this often.
  End
"""

# NOTE: the original comment line ends with a trailing space — kept verbatim.
TANK_BM_OLD = """\
  Behavior = OverlordContain ModuleTag_ArmorAddon01 ; Like Transport, but when full, passes transport queries along to first passenger (redirects like tunnel)\x20
    Slots                   = 1
    DamagePercentToUnits    = 100%
    AllowInsideKindOf       = PORTABLE_STRUCTURE
    PassengersAllowedToFire = No
  End
"""

TANK_BM_NEW = """\
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
# Feature 1 — CommandSet.ini additions (layered on the zzy_MammothBunker
# copy so the Mammoth's Armor_AmericaTankPaladinCommandSet patch survives).
# Exit buttons MUST be contiguous (ControlBar::doTransportInventoryUI);
# slots 1-10 were free on the three plain Battlemaster sets, 2-10 on the
# Ravage set.  Command_TransportExit / Command_Evacuate are existing generic
# ShockWave buttons — no new art or CSF strings.
# ---------------------------------------------------------------------------

CS_CHINA_OLD = """\
CommandSet ChinaVehicleBattleMasterCommandSet
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_CHINA_NEW = """\
CommandSet ChinaVehicleBattleMasterCommandSet
  1  = Command_TransportExit
  2  = Command_TransportExit
  3  = Command_TransportExit
  4  = Command_TransportExit
  5  = Command_Evacuate
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_NUKE_OLD = """\
CommandSet Nuke_ChinaVehicleBattleMasterCommandSet
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_NUKE_NEW = """\
CommandSet Nuke_ChinaVehicleBattleMasterCommandSet
  1  = Command_TransportExit
  2  = Command_TransportExit
  3  = Command_TransportExit
  4  = Command_TransportExit
  5  = Command_Evacuate
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_TANK_OLD = """\
CommandSet Tank_ChinaVehicleBattleMasterCommandSet
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_TANK_NEW = """\
CommandSet Tank_ChinaVehicleBattleMasterCommandSet
  1  = Command_TransportExit
  2  = Command_TransportExit
  3  = Command_TransportExit
  4  = Command_TransportExit
  5  = Command_Evacuate
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_SPEC_OLD = """\
CommandSet Spec_ChinaVehicleBattleMasterCommandSet
   1 = Command_FireRavageRamjetShell
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

CS_SPEC_NEW = """\
CommandSet Spec_ChinaVehicleBattleMasterCommandSet
   1 = Command_FireRavageRamjetShell
   2 = Command_TransportExit
   3 = Command_TransportExit
   4 = Command_TransportExit
   5 = Command_TransportExit
   6 = Command_Evacuate
  11 = Command_AttackMove
  13 = Command_Guard
  14 = Command_Stop
End
"""

# ---------------------------------------------------------------------------
# Feature 2 — Troop Crawler fire ports: add PassengersAllowedToFire = Yes as
# the first line of each real infantry TransportContain (same placement the
# Infantry General's crawler already uses).  Their command sets already have
# 8 contiguous Command_TransportExit buttons — no CommandSet change needed.
#
# Modified:  ChinaVehicleTroopCrawler, Nuke_, Tank_,
#            Spec_ChinaVehicleTroopCrawler (Support Crawler — it DOES carry
#            4 infantry), ChinaVehicleTroopCrawlerEmpty (the buildable
#            "empty" crawler in ChinaMisc.ini).
# Untouched: Infa_ChinaVehicleTroopCrawler (already fires out),
#            CINE_ChinaVehicleTroopCrawlerEmpty (cinematic-only prop).
# ---------------------------------------------------------------------------

def tc_patch(slots_line):
    old = "  Behavior = TransportContain ModuleTag_06\n" + slots_line
    new = ("  Behavior = TransportContain ModuleTag_06\n"
           "    PassengersAllowedToFire = Yes\n" + slots_line)
    return old, new


# (internal_path, old, new) — multiple patches per file are allowed.
P = r"Data\INI"
PATCHES = [
    # --- Battlemaster bunker bays -----------------------------------------
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     FLAMMABLE_BLOCK, FLAMMABLE_BLOCK + "\n" + BUNKER_BLOCK),
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini",
     FLAMMABLE_BLOCK, FLAMMABLE_BLOCK + "\n" + BUNKER_BLOCK),
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini",
     TANK_BM_OLD, TANK_BM_NEW),
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini",
     FLAMMABLE_BLOCK, FLAMMABLE_BLOCK + "\n" + BUNKER_BLOCK),
    # --- Battlemaster command sets ----------------------------------------
    (P + r"\CommandSet.ini", CS_CHINA_OLD, CS_CHINA_NEW),
    (P + r"\CommandSet.ini", CS_NUKE_OLD, CS_NUKE_NEW),
    (P + r"\CommandSet.ini", CS_TANK_OLD, CS_TANK_NEW),
    (P + r"\CommandSet.ini", CS_SPEC_OLD, CS_SPEC_NEW),
    # --- Troop Crawler fire ports -----------------------------------------
    (P + r"\Object\China\Vanilla\Vehicles\TroopCrawler.ini",
     *tc_patch("    Slots                 = 8\n"
               "    InitialPayload        = ChinaInfantryRedguard 8\n")),
    (P + r"\Object\China\Nuke\Vehicles\TroopCrawler.ini",
     *tc_patch("    Slots                 = 8\n"
               "    InitialPayload        = Nuke_ChinaInfantryRedguard 8\n")),
    (P + r"\Object\China\Tank\Vehicles\TroopCrawler.ini",
     *tc_patch("    Slots                 = 6\n"
               "    InitialPayload        = Tank_ChinaInfantryRedguard 6\n")),
    (P + r"\Object\China\SpecialWeapons\Vehicles\SupportCrawler.ini",
     *tc_patch("    Slots                 = 4\n")),
    (P + r"\Object\China\Vanilla\ChinaMisc.ini",
     *tc_patch("    Slots = 8\n")),   # Slots = 10 is the CINE prop; 8 is unique
]

# The tank-buff values that must survive in our patched copies.
BUFF_CHECKS = [
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     "MaxHealth       = 480.0"),
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini",
     "MaxHealth       = 480.0"),
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini",
     "MaxHealth       = 480.0"),
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini",
     "MaxHealth       = 576.0"),
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
    """Apply a patch written with \\n, matching the file's own line endings."""
    for eol in ("\r\n", "\n"):
        old_b = old.replace("\n", eol).encode("latin-1")
        new_b = new.replace("\n", eol).encode("latin-1")
        n = data.count(old_b)
        if n == 1:
            return data.replace(old_b, new_b)
        if n > 1:
            raise ValueError(f"patch target found {n} times (must be 1)")
    raise ValueError("patch target not found")


def balanced(data: bytes) -> bool:
    """Crude block-structure check: top-level opener lines vs End lines."""
    openers = 0
    ends = 0
    for raw in data.decode("latin-1").splitlines():
        line = raw.split(";", 1)[0].rstrip()
        if line.strip() == "End":
            ends += 1
    # Compare against source file's own delta instead of absolute count —
    # handled by the caller (we only added blocks with matching End count).
    return ends  # returns count; caller compares before/after


def main():
    # group patches by file, preserving order
    by_file = {}
    for path, old, new in PATCHES:
        by_file.setdefault(path, []).append((old, new))

    entries = []
    sources = {}
    for internal_path, patches in by_file.items():
        data, src = effective_entry(internal_path)
        sources[internal_path] = (src, data)
        before_ends = balanced(data)
        patched = data
        for old, new in patches:
            patched = apply_patch(patched, old, new)
        # every added block contributes exactly matching Behavior/End pairs;
        # verify End-line count grew by the expected amount
        added_ends = sum(n.count("\nEnd\n") + n.count("  End\n") -
                         (o.count("\nEnd\n") + o.count("  End\n"))
                         for o, n in patches)
        after_ends = balanced(patched)
        if after_ends - before_ends != added_ends:
            raise AssertionError(
                f"{internal_path}: End-count delta {after_ends - before_ends} "
                f"!= expected {added_ends}")
        entries.append(BigEntry(internal_path, patched))
        print(f"patched {internal_path}")
        print(f"        source: {src}")
        print(f"        {len(data)} -> {len(patched)} bytes, "
              f"{len(patches)} patch(es), End-lines +{added_ends}")

    # buff-survival checks
    for internal_path, needle in BUFF_CHECKS:
        ent = next(e for e in entries if e.path == internal_path)
        if needle.encode("latin-1") not in ent.data:
            raise AssertionError(f"{internal_path}: buff value missing: {needle!r}")
        print(f"buff OK  {internal_path}: {needle!r} present")

    out_path = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_path)
    print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes)")

    # re-read the built archive and verify round-trip
    reread = read_big(out_path)
    assert len(reread) == len(entries)
    for e in entries:
        r = find_entry(reread, e.path)
        assert r.data == e.data, f"round-trip mismatch: {e.path}"
    print(f"verified: archive re-read OK, {len(reread)} entries match")

    for d in INSTALL_DIRS:
        dest = os.path.join(d, OUT_NAME)
        shutil.copyfile(out_path, dest)
        print(f"installed {dest}")


if __name__ == "__main__":
    main()
