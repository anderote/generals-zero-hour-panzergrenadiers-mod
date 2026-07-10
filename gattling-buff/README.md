# Gattling Tank Buff (ShockWave / GeneralsX)

Stat-buff mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX.
China's five gattling **tank** objects get, multiplicatively **on top of**
the already-installed `zzx_ChinaTankBuff` values:

- **+15% max health** (MaxHealth + InitialHealth; total 1.38x vanilla)
- **+20% weapon range** (AttackRange; total 1.32x vanilla)
- **+20% weapon damage** (PrimaryDamage; total 1.2x vanilla — tank buff
  never touched damage)
- **+10% fire rate** (DelayBetweenShots / 1.1, rounded: 400 -> 364 ms)

Buffed objects: `ChinaTankGattling` (vanilla), `Nuke_ChinaTankGattling`,
`Spec_ChinaTankGattling` (Leang), `Tank_ChinaTankGattling` (Kwai),
`Infa_ChinaTankGattling` (Fai's Gattling APC).

All 21 real weapon-stage templates those tanks use are scaled uniformly —
normal / PLAYER_UPGRADE ("Advanced"/"Upgraded" chaingun) / HERO variants,
ground and air guns — so the ContinuousFire spin-up progression stays
coherent (the RATE_OF_FIRE 200%/300% spin-up bonuses are percentages of
the base delay and scale with it: 400/200/133 becomes 364/182/121).

Gattling **buildings** (base-defense gattling cannons) and gattling
weapons of non-tank units (Helix guns, building guns) are untouched.

## The Spec (Leang) tank's dummy AA weapon

`Spec_ChinaTankGattling` is an Overlord-style hull: its real AA gun
(`Spec_GattlingTankGunAir`) sits on the independently-attacking rider
turret `Spec_ChinaTankGattlingTurret`, while the hull's SECONDARY slot
holds the near-zero-damage acquisition dummy `Spec_GattlingTankAirDummy`
(0.0001 STATUS damage, range 350) that defines the hull's AA engagement
envelope. That dummy template is **shared** with `Infa_ChinaVehicleHelix`
and `Spec_ChinaGattlingCannon` (Sentinel defense), whose real guns this
mod does not buff — so instead of scaling the shared dummy, the mod adds a
private clone **`Spec_GattlingTankAirDummyBuffed`** (range 420, matching
the buffed turret gun's 420) and repoints only the Spec gattling tank's
two WeaponSets at it. Helix/Sentinel keep the original 350 dummy.

Note: the china-tank-buff layer had missed `Spec_GattlingTankGunAir`
(the turret rider wasn't on its whitelist), so that weapon's range is
1.2x vanilla (350 -> 420), not 1.32x like the others.

## What it is

`zzyz_GattlingBuff.big` — full patched copies of 6 files, every one
extracted from the **highest-priority archive containing it**
(`zzx_ChinaTankBuff.big` for all six; verified that
`zzyy_ChinaBunkers.big` / `zzy_MammothBunker.big` contain none of them):

- `Data\INI\Weapon.ini` (63 stat lines changed + 25-line dummy clone)
- `Data\INI\Object\China\Vanilla\Vehicles\GattlingTank.ini` (health)
- `Data\INI\Object\China\Nuke\Vehicles\GattlingTank.ini` (health)
- `Data\INI\Object\China\SpecialWeapons\Vehicles\GattlingTank.ini` (health + dummy repoint)
- `Data\INI\Object\China\Tank\Vehicles\GattlingTank.ini` (health)
- `Data\INI\Object\China\Infantry\Vehicles\GattlingAPC.ini` (health)

The `zzyz_` prefix sorts (case-insensitively) after `zzx_`, `zzy_`,
`zzyy_` and before `zzz_ControlBarPro*`, so these copies win at load time
while the UI-skin archives (which share no files with this mod) still load
last.

All china-tank-buff values embedded in these copies survive unchanged
(spot-checked at build time: BattleMasterTankGun 165, OverlordTankGun
192.5, ChainGun 192.5, Tank_WarMasterTankGun 176; build fails on drift).

## Rebuild

```
python3 build.py
```

Reads `~/GeneralsX/mods/ShockWaveSPE/zzx_ChinaTankBuff.big` (asserts both
installed zzx copies are byte-identical), applies the multipliers with
line-precise regex edits, asserts every old value matches the expected
tank-buff-era value (fails loudly on upstream drift), verifies the diff
touches only intended lines and block `End` counts balance, writes
`zzyz_GattlingBuff.big` here, re-reads it for round-trip integrity, and
installs to both mod dirs.

## Install locations

- `~/GeneralsX/mods/ShockWave/zzyz_GattlingBuff.big`
- `~/GeneralsX/mods/ShockWaveSPE/zzyz_GattlingBuff.big`

## Uninstall

Delete `zzyz_GattlingBuff.big` from both directories above. No other
files are touched.

## Rebuild-order warning

This archive embeds **full copies** of `Data\INI\Weapon.ini` and the five
gattling object INIs taken from `zzx_ChinaTankBuff.big`. If
`zzx_ChinaTankBuff.big` (or any lower layer touching these files) is ever
rebuilt with different content, **rebuild this archive afterwards** —
being later-alphabetical it would otherwise silently mask the newer
versions of those six files. Conversely, `zzyy_ChinaBunkers.big` does not
overlap these files, so it can be rebuilt independently.

## Known spillover / risks

- No weapon spillover: an audit across every effective object INI shows
  all 21 buffed weapon templates are used exclusively by the five target
  tanks (+ the Spec tank's own rider turret). The shared AA dummy was
  cloned rather than modified precisely to avoid buffing the Helix and
  the Sentinel gattling cannon's acquisition envelopes.
- The Gattling APC air-gun range is now 303.6 (fractional ranges are
  already common in ShockWave, e.g. 192.5).
- Infa health rounds 303.6 -> 304 (1.3818x vanilla instead of exactly 1.38).
- Save games created without this mod may not load with it (and vice
  versa) if they reference these units; start fresh skirmishes.
- Do not extract this mod's Weapon.ini into `Data\INI\` loose files —
  loose INIs would override every archive.
