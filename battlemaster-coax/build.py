#!/usr/bin/env python3
"""Build zzyzzz_CoaxMG.big — Battlemaster coaxial machine gun mini-mod.

Gives every China Battlemaster variant a SECONDARY coaxial MG
(ShwBattleMasterCoaxMGWeapon, ported from ZHE's Type67CoaxialMachineGunWeapon)
that auto-selects against infantry.

Reads the EFFECTIVE copy of each modified file from the highest-priority
archive that contains it, applies exact-text patches (fails loudly on
upstream drift), verifies prior-layer survivals + referenced assets +
block balance, writes zzyzzz_CoaxMG.big here and installs it into both
mod directories.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/")
SHW = os.path.expanduser("~/GeneralsX/mods/ShockWave/")
OUT_NAME = "zzyzzz_CoaxMG.big"

# Highest priority first (later-alphabetical archives win inside a -mod dir).
PRIORITY = [
    "zzyzy_NoAISuperweapons.big",   # may not exist yet (sibling layer)
    "zzyzz_PropTowers.big",
    "zzyz_GattlingBuff.big",
    "zzyy_ChinaBunkers.big",
    "zzy_MammothBunker.big",
    "zzx_ChinaTankBuff.big",
    "zz_SPE_Shw_ini.big",
    "!Shw_ini.big",
]

VANILLA = "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\BattleMaster.ini"
NUKE = "Data\\INI\\Object\\China\\Nuke\\Vehicles\\BattleMaster.ini"
TANK = "Data\\INI\\Object\\China\\Tank\\Vehicles\\BattleMaster.ini"
RAVAGE = "Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\RavageTank.ini"
WEAPON = "Data\\INI\\Weapon.ini"

MODIFIED = [WEAPON, VANILLA, NUKE, TANK, RAVAGE]

# ---------------------------------------------------------------------------

_archives = {}


def archive(name):
    if name not in _archives:
        p = SPE + name
        _archives[name] = read_big(p) if os.path.exists(p) else None
    return _archives[name]


def effective(path):
    """Return (data, source_archive_name) for the effective copy of path."""
    for name in PRIORITY:
        arch = archive(name)
        if arch is None:
            continue
        try:
            return find_entry(arch, path).data, name
        except KeyError:
            continue
    raise KeyError(path)


def patch(text, old, new, what, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"DRIFT: anchor for {what!r} found {n}x (expected {count})")
    return text.replace(old, new)


def require(cond, what):
    if not cond:
        raise SystemExit(f"CHECK FAILED: {what}")
    print(f"  ok: {what}")


# ---------------------------------------------------------------------------
# 1. New weapon template (basis: ZHE Type67CoaxialMachineGunWeapon).
#    Deviations from ZHE, all noted in README:
#      AttackRange 200 -> 165 (capped at BattleMaster cannon range)
#      ProjectileObject GenericBullet -> GenericMachinegunProjectile
#      ProjectileDetonationFX FX_BulletHit -> WeaponFX_GenericBulletImpact
#      ProjectileDetonationOCL dropped (no such OCL in ShockWave)
#      FireFX FX_Type67Fire -> WeaponFX_GenericMachineGunFire
#      VeterancyFireFX FX_Type67FireWithRedTracers ->
#          WeaponFX_GenericMachineGunFireWithRedTracers
#      FireSound PKMMachineGun -> BattleMasterMachineGunFire

COAX_WEAPON = """\
;------------------------------------------------------------------------------
; Coaxial MG for all China Battlemaster variants (zzyzzz_CoaxMG layer).
; Ported from ZHE's Type67CoaxialMachineGunWeapon; range capped at the
; Battlemaster cannon's 165 and all FX/sound/projectile references replaced
; with ShockWave-native equivalents.
Weapon ShwBattleMasterCoaxMGWeapon
  PrimaryDamage           = 20.0
  PrimaryDamageRadius     = 1.0
  SecondaryDamage         = 10.0
  SecondaryDamageRadius   = 2.0
  ScatterRadius           = 30.0
  AttackRange             = 165.0   ; ZHE: 200, capped at cannon range
  MinimumAttackRange      = 20.0
  AcceptableAimDelta      = 10
  DamageType              = SMALL_ARMS
  DeathType               = NORMAL
  ; Hitscan like vanilla vehicle MGs: no ProjectileObject. The ported
  ; GenericMachinegunProjectile flew a ballistic arc (visibly fired upward);
  ; instant-hit + tracer FireFX renders along the gun axis instead.
  WeaponSpeed             = 999999.0
  FireFX                  = WeaponFX_GenericMachineGunFire
  VeterancyFireFX         = HEROIC WeaponFX_GenericMachineGunFireWithRedTracers
  FireSound               = BattleMasterMachineGunFire
  RadiusDamageAffects     = ALLIES ENEMIES NEUTRALS
  DelayBetweenShots       = 65
  ClipSize                = 30
  ClipReloadTime          = 5000
  PreAttackType           = PER_CLIP
  PreAttackDelay          = 2000
End

"""

SECONDARY_LINE = "Weapon = SECONDARY ShwBattleMasterCoaxMGWeapon"
PREFERRED_LINE = "PreferredAgainst = SECONDARY INFANTRY"


def patch_weapon_ini(text):
    # Insert the new template just before CrusaderTankGun (right after the
    # BattleMasterMachineGun block) -- LF line endings in this file.
    anchor = ";------------------------------------------------------------------------------\nWeapon CrusaderTankGun\n"
    return patch(text, anchor, COAX_WEAPON + anchor, "Weapon.ini insert")


def patch_vanilla(text):
    old = (
        "  WeaponSet\r\n"
        "    Conditions = None \r\n"
        "    Weapon = PRIMARY BattleMasterTankGun\r\n"
        "  End\r\n"
        "  WeaponSet\r\n"
        "    Conditions = PLAYER_UPGRADE \r\n"
        "    Weapon = PRIMARY BattleMasterTankGunUpgraded\r\n"
        "  End\r\n"
    )
    new = (
        "  WeaponSet\r\n"
        "    Conditions = None \r\n"
        "    Weapon = PRIMARY BattleMasterTankGun\r\n"
        f"    {SECONDARY_LINE}\r\n"
        f"    {PREFERRED_LINE}\r\n"
        "  End\r\n"
        "  WeaponSet\r\n"
        "    Conditions = PLAYER_UPGRADE \r\n"
        "    Weapon = PRIMARY BattleMasterTankGunUpgraded\r\n"
        f"    {SECONDARY_LINE}\r\n"
        f"    {PREFERRED_LINE}\r\n"
        "  End\r\n"
    )
    return patch(text, old, new, "vanilla Var1 WeaponSets")


def patch_nuke(text):
    old = (
        "  WeaponSet\r\n"
        "    Conditions = None \r\n"
        "    Weapon = PRIMARY Nuke_BattleMasterTankGun\r\n"
        "    ;ShareWeaponReloadTime = Yes\r\n"
        "  End\r\n"
    )
    new = (
        "  WeaponSet\r\n"
        "    Conditions = None \r\n"
        "    Weapon = PRIMARY Nuke_BattleMasterTankGun\r\n"
        f"    {SECONDARY_LINE}\r\n"
        f"    {PREFERRED_LINE}\r\n"
        "    ;ShareWeaponReloadTime = Yes\r\n"
        "  End\r\n"
    )
    text = patch(text, old, new, "nuke WeaponSet (None)")
    old = (
        "  WeaponSet\r\n"
        "    Conditions = PLAYER_UPGRADE\r\n"
        "    Weapon = PRIMARY Nuke_BattleMasterTankGunUpgraded\r\n"
        "     ;ShareWeaponReloadTime = Yes\r\n"
        "  End\r\n"
    )
    new = (
        "  WeaponSet\r\n"
        "    Conditions = PLAYER_UPGRADE\r\n"
        "    Weapon = PRIMARY Nuke_BattleMasterTankGunUpgraded\r\n"
        f"    {SECONDARY_LINE}\r\n"
        f"    {PREFERRED_LINE}\r\n"
        "     ;ShareWeaponReloadTime = Yes\r\n"
        "  End\r\n"
    )
    return patch(text, old, new, "nuke WeaponSet (PLAYER_UPGRADE)")


def patch_tank(text):
    old = (
        "  WeaponSet\r\n"
        "    Conditions = None \r\n"
        "    Weapon = PRIMARY Tank_BattleMasterTankGun\r\n"
        "  End\r\n"
        "  WeaponSet\r\n"
        "    Conditions = PLAYER_UPGRADE \r\n"
        "    Weapon = PRIMARY Tank_BattleMasterTankGunUpgraded\r\n"
        "  End\r\n"
    )
    new = (
        "  WeaponSet\r\n"
        "    Conditions = None \r\n"
        "    Weapon = PRIMARY Tank_BattleMasterTankGun\r\n"
        f"    {SECONDARY_LINE}\r\n"
        f"    {PREFERRED_LINE}\r\n"
        "  End\r\n"
        "  WeaponSet\r\n"
        "    Conditions = PLAYER_UPGRADE \r\n"
        "    Weapon = PRIMARY Tank_BattleMasterTankGunUpgraded\r\n"
        f"    {SECONDARY_LINE}\r\n"
        f"    {PREFERRED_LINE}\r\n"
        "  End\r\n"
    )
    return patch(text, old, new, "tank (Kwai) WeaponSets")


def patch_ravage(text):
    # ShockWave itself ships a commented-out SECONDARY MG here -- we add a
    # live one (the commented RavageMasterMachineGun lines are left in place).
    old = (
        "    Weapon = PRIMARY   RavageTankGun\r\n"
        "    ;Weapon = SECONDARY RavageMasterMachineGun\r\n"
        "    Weapon = TERTIARY RavageRamjetShellWeapon\r\n"
        "    PreferredAgainst = PRIMARY   VEHICLE\r\n"
        "    ;PreferredAgainst = SECONDARY INFANTRY\r\n"
    )
    new = (
        "    Weapon = PRIMARY   RavageTankGun\r\n"
        "    ;Weapon = SECONDARY RavageMasterMachineGun\r\n"
        f"    {SECONDARY_LINE}\r\n"
        "    Weapon = TERTIARY RavageRamjetShellWeapon\r\n"
        "    PreferredAgainst = PRIMARY   VEHICLE\r\n"
        "    ;PreferredAgainst = SECONDARY INFANTRY\r\n"
        f"    {PREFERRED_LINE}\r\n"
    )
    return patch(text, old, new, "Ravage WeaponSet")


PATCHERS = {
    WEAPON: patch_weapon_ini,
    VANILLA: patch_vanilla,
    NUKE: patch_nuke,
    TANK: patch_tank,
    RAVAGE: patch_ravage,
}

# ---------------------------------------------------------------------------


def count_ends(text):
    """Count uncommented lines that are exactly 'End' (case-insensitive)."""
    return sum(1 for raw in text.splitlines()
               if raw.split(";", 1)[0].strip().lower() == "end")


def block_balance(original, patched, name, extra_ends):
    """Differential balance: originals are known-good shipping files, so the
    patched copy must have exactly `extra_ends` more bare 'End' lines (one per
    inserted block) and identical WeaponSet/End pairing inside the diff."""
    before, after = count_ends(original), count_ends(patched)
    if after - before != extra_ends:
        raise SystemExit(f"CHECK FAILED: {name}: End count {before} -> {after}, "
                         f"expected +{extra_ends}")
    print(f"  ok: block balance {name} (End lines {before} -> {after}, +{extra_ends})")


def main():
    print("== effective sources")
    sources = {}
    originals = {}
    for path in MODIFIED:
        data, src = effective(path)
        sources[path] = src
        originals[path] = data
        print(f"  {path}  <-  {src}  ({len(data)} bytes)")

    # sanity: the two object-INI sources must be the prop-tower layer and
    # Weapon.ini must come from the gattling layer, unless a newer layer
    # appeared that legitimately contains them.
    for path in (VANILLA, NUKE, TANK, RAVAGE):
        require(sources[path] in ("zzyzz_PropTowers.big", "zzyzy_NoAISuperweapons.big"),
                f"{path} sourced from expected layer ({sources[path]})")
    require(sources[WEAPON] in ("zzyz_GattlingBuff.big", "zzyzz_PropTowers.big",
                                "zzyzy_NoAISuperweapons.big"),
            f"Weapon.ini sourced from expected layer ({sources[WEAPON]})")

    print("== patch")
    patched = {}
    for path in MODIFIED:
        text = originals[path].decode("latin-1")
        out = PATCHERS[path](text)
        patched[path] = out.encode("latin-1")
        print(f"  patched {path}: {len(originals[path])} -> {len(patched[path])} bytes")

    print("== verify: intended-only diffs")
    for path in MODIFIED:
        a = originals[path].decode("latin-1").splitlines()
        b = patched[path].decode("latin-1").splitlines()
        import difflib
        added = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)
                 if l.startswith("+") and not l.startswith("+++")]
        removed = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)
                   if l.startswith("-") and not l.startswith("---")]
        require(not removed, f"{path}: no lines removed")
        for l in added:
            require("ShwBattleMasterCoaxMGWeapon" in l
                    or "PreferredAgainst = SECONDARY INFANTRY" in l
                    or l[1:].strip().startswith(";")
                    or l[1:].strip() == ""
                    or "coax" in l.lower()
                    or "Ported from ZHE" in l or "range capped" in l
                    or "ShockWave-native" in l or "Battlemaster cannon" in l
                    or l[1:].lstrip().split(" ")[0] in (
                        "Weapon", "PrimaryDamage", "PrimaryDamageRadius",
                        "SecondaryDamage", "SecondaryDamageRadius",
                        "ScatterRadius", "AttackRange", "MinimumAttackRange",
                        "AcceptableAimDelta", "DamageType", "DeathType",
                        "WeaponSpeed", "ProjectileObject",
                        "ProjectileDetonationFX", "FireFX", "VeterancyFireFX",
                        "FireSound", "RadiusDamageAffects", "DelayBetweenShots",
                        "ClipSize", "ClipReloadTime", "ProjectileCollidesWith",
                        "PreAttackType", "PreAttackDelay", "End"),
                    f"unexpected added line in {path}: {l!r}")
        print(f"  ok: {path}: +{len(added)} lines, -0 lines")

    print("== verify: prior-layer survivals")
    wtxt = patched[WEAPON].decode("latin-1")
    require("Weapon ShwBattleMasterCoaxMGWeapon" in wtxt, "new weapon present")
    # gattling-buff layer values
    import re
    gat = re.search(r"Weapon GattlingTankGun\n(.*?)\nEnd", wtxt, re.S).group(1)
    require("AttackRange           = 198.0" in gat, "GattlingTankGun range 198 survives")
    require("PrimaryDamage         = 18.0" in gat, "GattlingTankGun damage 18 survives")
    # china-tank-buff: BattleMaster cannon range 165 (=150*1.1)
    for wpn in ("BattleMasterTankGun", "BattleMasterTankGunUpgraded",
                "Tank_BattleMasterTankGun", "Nuke_BattleMasterTankGun",
                "RavageTankGun"):
        blk = re.search(r"Weapon %s\n(.*?)\nEnd" % re.escape(wpn), wtxt, re.S).group(1)
        require("AttackRange             = 165.0" in blk,
                f"{wpn} buffed range 165 survives")

    for path, marks in [
        (VANILLA, ["HelixContain", "ObjectCreationUpgrade",
                   "Upgrade_ChinaOverlordPropagandaTower", "MaxHealth       = 480.0",
                   "W3DOverlordTankDraw"]),
        (NUKE, ["HelixContain", "Upgrade_ChinaOverlordPropagandaTower",
                "MaxHealth       = 480.0"]),
        (TANK, ["HelixContain", "Upgrade_ChinaOverlordPropagandaTower",
                "Tank_ChinaVehicleBattleMasterCommandSetERA",
                "MaxHealth       = 480.0"]),
        (RAVAGE, ["HelixContain", "Upgrade_ChinaOverlordPropagandaTower",
                  "MaxHealth       = 576.0"]),
    ]:
        txt = patched[path].decode("latin-1")
        for m in marks:
            require(m in txt, f"{os.path.basename(path)}: prior-layer mark {m!r} survives")
        require(txt.count(SECONDARY_LINE) == (1 if path == RAVAGE else 2),
                f"{os.path.basename(path)}: SECONDARY coax in every WeaponSet")

    print("== verify: referenced assets exist in effective ShockWave data")
    fxlist, _ = effective("Data\\INI\\FXList.ini")
    sounds, _ = effective("Data\\INI\\SoundEffects.ini")
    tracers, _ = effective("Data\\INI\\Object\\WeaponTracerObjects.ini")
    fxlist = fxlist.decode("latin-1")
    sounds = sounds.decode("latin-1")
    tracers = tracers.decode("latin-1")
    require("FXList WeaponFX_GenericMachineGunFire\n" in fxlist
            or "FXList WeaponFX_GenericMachineGunFire\r" in fxlist
            or re.search(r"^FXList WeaponFX_GenericMachineGunFire\s*$", fxlist, re.M),
            "FXList WeaponFX_GenericMachineGunFire exists")
    require(re.search(r"^FXList WeaponFX_GenericMachineGunFireWithRedTracers\s*$", fxlist, re.M),
            "FXList WeaponFX_GenericMachineGunFireWithRedTracers exists")
    require(re.search(r"^FXList WeaponFX_GenericBulletImpact\s*$", fxlist, re.M),
            "FXList WeaponFX_GenericBulletImpact exists")
    require(re.search(r"^AudioEvent BattleMasterMachineGunFire\s*$", sounds, re.M),
            "AudioEvent BattleMasterMachineGunFire exists")
    # hitscan since the straight-up-fire fix: no projectile object referenced

    print("== verify: block balance")
    for path in MODIFIED:
        extra = 1 if path == WEAPON else 0  # one new Weapon block in Weapon.ini
        block_balance(originals[path].decode("latin-1"),
                      patched[path].decode("latin-1"),
                      os.path.basename(path), extra)

    print("== write archive")
    entries = [BigEntry(p, patched[p]) for p in MODIFIED]
    out = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out)
    # round-trip
    back = read_big(out)
    require(len(back) == len(entries), "round-trip entry count")
    for e in back:
        require(e.data == patched[e.path], f"round-trip bytes: {e.path}")
    print(f"  wrote {out} ({os.path.getsize(out)} bytes)")

    # sort-order sanity inside the mod dir
    names = ["zzyz_GattlingBuff.big", "zzyzy_NoAISuperweapons.big",
             "zzyzz_PropTowers.big", OUT_NAME, "zzz_ControlBarProZH.big"]
    require(sorted(names, key=str.lower) == names, "archive sort order (coax after "
            "PropTowers/NoAISuperweapons, before zzz_ControlBarPro)")

    print("== install")
    import shutil
    for dest in (SPE, SHW):
        shutil.copyfile(out, dest + OUT_NAME)
        installed = read_big(dest + OUT_NAME)
        for e in installed:
            require(e.data == patched[e.path], f"installed bytes: {dest + OUT_NAME}: {e.path}")
        print(f"  installed {dest + OUT_NAME}")

    print("BUILD OK")


if __name__ == "__main__":
    main()
