#!/usr/bin/env python3
"""Build zzyzz_PropTowers.big — Battlemaster propaganda-tower mini-mod for
ShockWave on GeneralsX.

Every China Battlemaster tank variant can buy a per-tank PROPAGANDA TOWER
add-on (the Overlord's speaker-tower rider: heals/buffs nearby friendlies),
mounted in the HelixContain dedicated rider slot so the 4-man bunker bay
from zzyy_ChinaBunkers is untouched.

Mechanism (all retail idioms, verified against GeneralsX engine source):
  * The Overlord's own shared per-object upgrade + button are reused:
    Upgrade_ChinaOverlordPropagandaTower ($500, SSOLSpeaker art, existing
    CSF labels) / Command_UpgradeChinaOverlordPropagandaTower.
  * An ObjectCreationUpgrade fires an existing OCL that spawns the tower
    rider with ContainInsideSourceObject = Yes; a HelixContain stores the
    first PORTABLE_STRUCTURE in a dedicated rider slot OUTSIDE the passenger
    list (HelixContain.cpp: isValidContainerFor returns TRUE for a portable
    when the slot is free, bypassing Allow/Forbid lists).
  * OBJECT_UPGRADE purchases run through the object's production queue, so
    each tank gains a ProductionUpdate (MaxQueueEntries = 1), like the
    Overlord/Helix.
  * The rider's W3DDependencyModelDraw only renders after the container's
    draw module calls notifyDrawableDependencyCleared() — only the
    W3DOverlord*Draw family does that.  W3DOverlordTankDraw is a strict
    drop-in extension of W3DTankDraw (no extra INI fields), so the plain
    Battlemasters' W3DTankDraw modules are converted (Kwai's already is one).

Per-general rider objects (existing; no new objects are defined):
  vanilla China : OCL_OverlordPropagandaTower      -> ChinaTankOverlordPropagandaTower
  Nuke (Tao)    : OCL_OverlordPropagandaTower_Nuke -> ChinaTankOverlordPropagandaTower_Nuke
  Tank (Kwai)   : OCL_OverlordPropagandaTower      -> ChinaTankOverlordPropagandaTower
                  (Tank_OCL_OverlordPropagandaTower exists but references
                  Tank_ChinaTankOverlordPropagandaTower which is NOT defined
                  anywhere in ShockWave — a dead OCL; the vanilla rider is
                  used instead.  Retail precedent: the Nuke & Infantry
                  generals' Helixes mount the Side=China ChinaHelixPropagandaTower.)
  Spec (SpecialWeapons / Ravage Tank): OCL_OverlordPropagandaTower (no
                  Spec-specific tower rider exists in ShockWave).

Kwai ERA interaction (Tank_ChinaTankBattleMaster already had HelixContain
with the ERA armor rider from zzyy_ChinaBunkers):
  * HelixContain has NO rider replacement: first portable structure wins the
    rider slot; a second one falls through to the PASSENGER list.  To stop a
    second portable from stealing an infantry seat (and appearing on exit
    buttons), PORTABLE_STRUCTURE is dropped from AllowInsideKindOf — the
    rider-slot bypass ignores the allow list, and an OCL payload the contain
    refuses is cleanly destroyed (ObjectCreationList.cpp:1240-1253).
  * Tower and ERA are made mutually exclusive:
      - the tower's ObjectCreationUpgrade gets ConflictsWith =
        Upgrade_TankLightArmor (player+object upgrade masks are OR'd when
        modules are tested — Object::updateUpgradeModules), and
      - a CommandSetUpgrade swaps to a new ERA command set (same buttons
        minus the tower button) when Upgrade_TankLightArmor completes, so
        the button disappears instead of wasting $500.
      - Reverse order (tower bought before ERA research): the tank KEEPS the
        tower and still receives ERA's +115 HP / armor set (those are
        modules on the tank itself); only the cosmetic ERA plate rider is
        skipped on that tank.

Reads the EFFECTIVE source copy of every modified file (highest-priority
archive first, including the sibling zzyz_GattlingBuff.big if it exists),
applies exact-text patches (fails loudly on upstream drift), verifies the
prior layers survived, writes the archive and installs into both mod dirs.

Run:  python3 build.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, find_entry, write_big_file  # noqa: E402

OUT_NAME = "zzyzz_PropTowers.big"

# Effective-source order (highest priority first).  zzyz_GattlingBuff.big is
# a sibling mod that may not exist yet — checked in both mod dirs and used if
# present.  Our name zzyzz_ sorts after zzyz_ and zzyy_ but before
# zzz_ControlBarPro* (case-insensitive).
SOURCE_ARCHIVES = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzyz_GattlingBuff.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave/zzyz_GattlingBuff.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzyy_ChinaBunkers.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzy_MammothBunker.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzx_ChinaTankBuff.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zz_SPE_Shw_ini.big"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave/!Shw_ini.big"),
]

INSTALL_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
]

P = r"Data\INI"

# ---------------------------------------------------------------------------
# Contain conversion — vanilla/Nuke/Spec Battlemasters: the china-bunkers
# TransportContain bay becomes a HelixContain (identical fields).  The
# passengers keep their 4 slots + fire ports; the tower rider lives in the
# dedicated portable-structure slot outside the passenger list (never on
# exit buttons, consumes no seats).
# ---------------------------------------------------------------------------

BUNKER_OLD = """\
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

BUNKER_HELIX = """\
  Behavior = HelixContain ModuleTag_BunkerBay01
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


def tower_blocks(ocl):
    """ObjectCreationUpgrade + ProductionUpdate appended after the contain."""
    return f"""
  Behavior = ObjectCreationUpgrade ModuleTag_PropTowerMount01
    UpgradeObject = {ocl}
    TriggeredBy   = Upgrade_ChinaOverlordPropagandaTower
  End

  Behavior = ProductionUpdate ModuleTag_PropTowerProduction01
    MaxQueueEntries = 1 ; the per-tank tower purchase runs through this queue
  End
"""


# ---------------------------------------------------------------------------
# Kwai (Tank general) — already HelixContain (zzyy_ChinaBunkers).  Narrow the
# passenger allow-list so a SECOND portable structure (tower after ERA, or
# ERA after tower) is refused/destroyed instead of stealing an infantry seat;
# the rider slot itself bypasses the allow list for the FIRST portable.
# ---------------------------------------------------------------------------

TANK_ALLOW_OLD = "    AllowInsideKindOf       = INFANTRY PORTABLE_STRUCTURE\n"
TANK_ALLOW_NEW = "    AllowInsideKindOf       = INFANTRY\n"

TANK_ERA_OCU = """\
  Behavior = ObjectCreationUpgrade ModuleTag_ArmorAddon02
    UpgradeObject = OCL_BattleMasterArmorAddons
    TriggeredBy = Upgrade_TankLightArmor
  End
"""

TANK_TOWER_BLOCKS = """
  Behavior = ObjectCreationUpgrade ModuleTag_PropTowerMount01
    UpgradeObject = OCL_OverlordPropagandaTower
    TriggeredBy   = Upgrade_ChinaOverlordPropagandaTower
    ConflictsWith = Upgrade_TankLightArmor ; ERA rider owns the HelixContain rider slot
  End

  Behavior = CommandSetUpgrade ModuleTag_PropTowerCmdSet01
    CommandSet  = Tank_ChinaVehicleBattleMasterCommandSetERA ; hide the tower button once ERA is researched
    TriggeredBy = Upgrade_TankLightArmor
  End

  Behavior = ProductionUpdate ModuleTag_PropTowerProduction01
    MaxQueueEntries = 1 ; the per-tank tower purchase runs through this queue
  End
"""

# ---------------------------------------------------------------------------
# Draw conversions — the rider only renders when the container's draw module
# clears its draw dependency; W3DOverlordTankDraw is a strict W3DTankDraw
# extension that does exactly that (plus hides/tints the rider with the tank).
# One conversion per drawable object.  Kwai's tank already uses it.
# ---------------------------------------------------------------------------

VAN_VAR1_DRAW_OLD = "  Draw = W3DTankDraw ModuleTag_01\n"
VAN_VAR1_DRAW_NEW = "  Draw = W3DOverlordTankDraw ModuleTag_01\n"

VAN_VAR2_DRAW_OLD = ("ObjectReskin ChinaTankBattleMaster_Var2 ChinaTankBattleMaster_Var1\n"
                     "\n"
                     "  Draw = W3DTankDraw ModuleTag_Chassis01\n")
VAN_VAR2_DRAW_NEW = ("ObjectReskin ChinaTankBattleMaster_Var2 ChinaTankBattleMaster_Var1\n"
                     "\n"
                     "  Draw = W3DOverlordTankDraw ModuleTag_Chassis01\n")

VAN_VAR3_DRAW_OLD = VAN_VAR2_DRAW_OLD.replace("_Var2 ", "_Var3 ")
VAN_VAR3_DRAW_NEW = VAN_VAR2_DRAW_NEW.replace("_Var2 ", "_Var3 ")

VAN_VAR4_DRAW_OLD = "  Draw = W3DTankDraw ModuleTag_Turret01\n"
VAN_VAR4_DRAW_NEW = "  Draw = W3DOverlordTankDraw ModuleTag_Turret01\n"

# ---------------------------------------------------------------------------
# CommandSet.ini — add the Overlord's existing tower button at slot 10 (the
# same slot the Overlord family uses); slots 1-5 (1-6 on the Ravage) are the
# china-bunkers exit buttons, 11/13/14 attack-move/guard/stop.  Kwai gets an
# extra ERA set (identical minus the tower button) for the CommandSetUpgrade.
# ---------------------------------------------------------------------------

TOWER_BTN = "  10 = Command_UpgradeChinaOverlordPropagandaTower\n"


def cs_plain(name):
    old = (f"CommandSet {name}\n"
           "  1  = Command_TransportExit\n"
           "  2  = Command_TransportExit\n"
           "  3  = Command_TransportExit\n"
           "  4  = Command_TransportExit\n"
           "  5  = Command_Evacuate\n"
           "  11 = Command_AttackMove\n"
           "  13 = Command_Guard\n"
           "  14 = Command_Stop\n"
           "End\n")
    new = old.replace("  11 = Command_AttackMove\n",
                      TOWER_BTN + "  11 = Command_AttackMove\n")
    return old, new


CS_TANK_OLD, CS_TANK_WITHBTN = cs_plain("Tank_ChinaVehicleBattleMasterCommandSet")
# after the patched Tank set, append the ERA set (original content, no tower)
CS_TANK_NEW = CS_TANK_WITHBTN + "\n" + CS_TANK_OLD.replace(
    "CommandSet Tank_ChinaVehicleBattleMasterCommandSet\n",
    "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n")

CS_SPEC_OLD = """\
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
CS_SPEC_NEW = CS_SPEC_OLD.replace("  11 = Command_AttackMove\n",
                                  TOWER_BTN + "  11 = Command_AttackMove\n")

# ---------------------------------------------------------------------------
# (internal_path, old, new) — multiple patches per file are allowed.
# ---------------------------------------------------------------------------

PATCHES = [
    # --- vanilla China (Var1 carries behaviors; Var2-4 reskins inherit them
    #     but own their draw sets, so each needs its draw converted) --------
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     BUNKER_OLD, BUNKER_HELIX + tower_blocks("OCL_OverlordPropagandaTower")),
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     VAN_VAR1_DRAW_OLD, VAN_VAR1_DRAW_NEW),
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     VAN_VAR2_DRAW_OLD, VAN_VAR2_DRAW_NEW),
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     VAN_VAR3_DRAW_OLD, VAN_VAR3_DRAW_NEW),
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",
     VAN_VAR4_DRAW_OLD, VAN_VAR4_DRAW_NEW),
    # --- Nuke general (Tao) ------------------------------------------------
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini",
     BUNKER_OLD, BUNKER_HELIX + tower_blocks("OCL_OverlordPropagandaTower_Nuke")),
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini",
     VAN_VAR1_DRAW_OLD, VAN_VAR1_DRAW_NEW),
    # --- Special Weapons (Ravage Tank) -------------------------------------
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini",
     BUNKER_OLD, BUNKER_HELIX + tower_blocks("OCL_OverlordPropagandaTower")),
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini",
     VAN_VAR1_DRAW_OLD, VAN_VAR1_DRAW_NEW),
    # --- Tank general (Kwai) — draw is already W3DOverlordTankDraw ---------
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini",
     TANK_ALLOW_OLD, TANK_ALLOW_NEW),
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini",
     TANK_ERA_OCU, TANK_ERA_OCU + TANK_TOWER_BLOCKS),
    # --- command sets -------------------------------------------------------
    (P + r"\CommandSet.ini", *cs_plain("ChinaVehicleBattleMasterCommandSet")),
    (P + r"\CommandSet.ini", *cs_plain("Nuke_ChinaVehicleBattleMasterCommandSet")),
    (P + r"\CommandSet.ini", CS_TANK_OLD, CS_TANK_NEW),
    (P + r"\CommandSet.ini", CS_SPEC_OLD, CS_SPEC_NEW),
]

# Prior-layer values that must survive in our shipped copies.
SURVIVAL_CHECKS = [
    # china-tank-buff HP buffs
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini", "MaxHealth       = 480.0"),
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini", "MaxHealth       = 480.0"),
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini", "MaxHealth       = 480.0"),
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini", "MaxHealth       = 576.0"),
    # china-bunkers 4-slot bays (now inside HelixContain)
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini", "ModuleTag_BunkerBay01"),
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini", "Slots                   = 4"),
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini", "Slots                   = 4"),
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini", "Slots                   = 4"),
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini", "Slots                   = 4"),
    # mammoth-bunker CommandSet hunk
    (P + r"\CommandSet.ini",
     "CommandSet Armor_AmericaTankPaladinCommandSet\n"
     "  1  = Command_ConstructAmericaVehicleBattleDrone\n"
     "  2  = Command_ConstructAmericaVehicleScoutDrone\n"
     "  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
     "  4  = Command_TransportExit"),
    # china-bunkers exit buttons still on all four sets (spot check)
    (P + r"\CommandSet.ini", "CommandSet ChinaVehicleBattleMasterCommandSet\n"
                             "  1  = Command_TransportExit"),
]


def effective_entry(internal_path):
    """Return (data, source_archive) for the highest-priority copy."""
    for arc in SOURCE_ARCHIVES:
        if not os.path.exists(arc):
            continue
        try:
            return find_entry(read_big(arc), internal_path).data, arc
        except KeyError:
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
    raise ValueError(f"patch target not found: {old[:70]!r}...")


def end_count(data: bytes) -> int:
    n = 0
    for raw in data.decode("latin-1").splitlines():
        if raw.split(";", 1)[0].strip() == "End":
            n += 1
    return n


def expected_end_delta(old: str, new: str) -> int:
    return end_count(new.encode("latin-1")) - end_count(old.encode("latin-1"))


def main():
    for arc in SOURCE_ARCHIVES[:2]:
        print(("using   " if os.path.exists(arc) else "absent  ") + arc)

    by_file = {}
    for path, old, new in PATCHES:
        by_file.setdefault(path, []).append((old, new))

    entries = []
    for internal_path, patches in by_file.items():
        data, src = effective_entry(internal_path)
        before_ends = end_count(data)
        patched = data
        for old, new in patches:
            patched = apply_patch(patched, old, new)
        delta = sum(expected_end_delta(o, n) for o, n in patches)
        after_ends = end_count(patched)
        if after_ends - before_ends != delta:
            raise AssertionError(
                f"{internal_path}: End-count delta {after_ends - before_ends}"
                f" != expected {delta}")
        entries.append(BigEntry(internal_path, patched))
        print(f"patched {internal_path}")
        print(f"        source: {src}")
        print(f"        {len(data)} -> {len(patched)} bytes, "
              f"{len(patches)} patch(es), End-lines +{delta}")

    # prior-layer survival checks
    for internal_path, needle in SURVIVAL_CHECKS:
        ent = next(e for e in entries if e.path == internal_path)
        found = False
        for eol in ("\r\n", "\n"):
            if needle.replace("\n", eol).encode("latin-1") in ent.data:
                found = True
                break
        if not found:
            raise AssertionError(f"{internal_path}: prior-layer value missing: {needle!r}")
    print(f"prior-layer survival: all {len(SURVIVAL_CHECKS)} checks OK")

    # no leftover plain contain/draw on the four tanks
    for e in entries:
        if e.path.endswith("CommandSet.ini"):
            assert e.data.count(b"Command_UpgradeChinaOverlordPropagandaTower") >= 5, \
                "tower button missing from patched command sets"
            continue
        assert b"TransportContain ModuleTag_BunkerBay01" not in e.data, e.path
        assert b"ModuleTag_PropTowerMount01" in e.data, e.path

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
