# Tesla Tune (ShockWave / GeneralsX)

Top data layer for **Kwai (China Tank General)** in ShockWave under GeneralsX
(macOS). Two features on the **Shock Trooper** (the tesla infantryman in the
Panzergrenadiers stack), pure data:

- **A — visible lightning when the trooper fires.**
- **B — nerf its fire rate, range, and damage.**

Output archive: **`zzz-ZZZZZZZZZZZZZZZZ0TeslaTune.big`** (2 files: `Weapon.ini`
+ `RotrShockTrooper.ini`). 16 `Z`s + `0` sorts **after** the previous top data
layer `zzz-ZZZZZZZZZZZZZZZ0EmperorInnatePDL.big` (15 `Z`s) — so it is the new
effective owner of both files — and, because `-` (0x2D) `<` `_` (0x5F) `<` `z`
(0x7A), **before** `zzz_ControlBarPro*` and `zzzz_FXEnhance.big`. Verified
against the real listings of both mod dirs at build time.

Installed to `~/GeneralsX/mods/ShockWave/` and `~/GeneralsX/mods/ShockWaveSPE/`
(md5-identical: `d48225b0879ebec42c76d8745a74c2fd`).

---

## Engine finding — can one weapon fire a projectile AND draw a LaserName bolt?

**No.** GeneralsMD `Weapon.cpp` `fireWeaponTemplate` (lines 1015-1094) is an
`if`/`else`:

- `if (getProjectileTemplate()==nullptr || isProjectileDetonation)` → the laser
  branch; `createLaser()` (the *only* code that draws the `LaserName` bolt,
  lines 1037/1043) lives here.
- `else` → the **projectile** branch (line 1094): spawns the `ProjectileObject`
  and **never calls `createLaser()`**.

So a weapon that has a `ProjectileObject` draws **no** beam on the initial shot.
At detonation the source handed in is the **projectile itself**
(`DumbProjectileBehavior.cpp:539` passes `obj`), so any laser there is a
degenerate zero-length flash at the impact point — not a bolt from the trooper.
`W3DLaserDraw` on the projectile object is also **non-viable**:
`W3DLaserDraw::doDrawModule` (`W3DLaserDraw.cpp:258-262`) hard-requires a
`ClientUpdate = LaserUpdate` module, and `LaserUpdate`'s endpoints are set
**only** by `Weapon::createLaser → initLaser` — which never runs for a
projectile — so the beam would render at the origin.

The Shock Trooper's primary **must** stay a projectile: its
`ProjectileDetonationOCL` spawns the stun/chain node **relative to the
projectile**, so the chain fires even when the trooper is garrisoned inside a
tank/building (`Weapon.cpp:952`). Breaking that was explicitly out of bounds.

## Task A — the fix that renders (and doesn't break garrisoned firing)

Since the bolt-beam mechanism is unavailable to a projectile weapon, the flying
**projectile is made clearly visible** instead. The projectile object
`ShockTrooperTeslaBoltProjectile` (draw = `W3DModelDraw`, `Model = NONE`) gets
one extra `ParticleSysBone`:

```
ParticleSysBone = None TeslaBoltSparks
```

`TeslaBoltSparks` is the tesla-coil family's own spark system —
**`SystemLifetime = 0` (emits for the entire flight)**, bright `ADDITIVE`
`EXFuzzyDot` sparks at `CRITICAL` priority. Attached to the moving projectile it
paints a **continuous crackling electric bolt-trail** from the trooper to the
target, visible even when firing from inside a container. The pre-existing
`TeslaTrooperFlare` puff (which only emits for 1 frame — `SystemLifetime = 1`)
is kept as a launch flash. Nothing about the projectile / flight /
`DumbProjectileBehavior` / detonation OCL wiring is touched, so **garrisoned
chain firing is preserved byte-for-byte**.

Supporting FX (unchanged, all confirmed resolving after fx-enhance's rebuild):
the chain arcs `ShockTrooperTeslaChainZap` still draw the real hitscan
`LaserName = TeslaBoltRandom` lightning bolt (`WeaponSpeed = 99999`); the impact
plays `FX_ShockTrooperElectricRocketExplosion`; `FireSound = TeslaCoilWeapon`.
So the full effect reads: spark bolt streaks out → electric blast → lightning
arcs to nearby enemies.

**FX masking status: resolved (no debt).** The current effective
`ParticleSystem.ini` / `FXList.ini` (owner `zzzz_FXEnhance.big`) already contain
`TeslaBoltSparks`, `TeslaTrooperFlare`, `ShockTrooperTeslaBlast` and
`FX_ShockTrooperElectricRocketExplosion` — the earlier masking finding was fixed
when the fx-enhance session rebuilt. This layer references those systems in
place and does **not** touch `ParticleSystem.ini` / `FXList.ini`.

## Task B — nerf (every Shock Trooper weapon variant)

| Weapon | Field | Old → New | Note |
|---|---|---|---|
| `ShockTrooperTeslaWeapon` (PRIMARY) | PrimaryDamage | **150 → 120** | −20% |
| | AttackRange | **140 → 100** | shorter |
| | DelayBetweenShots | **2400 → 3200** | ~33% slower fire rate |
| `ShockTrooperTeslaChainZap` (chain arc) | PrimaryDamage | **100 → 80** | −20% |
| | AttackRange | **90 → 65** | shorter chain reach |
| `HeroicShockTrooperTeslaChainZap` (chain arc, heroic) | PrimaryDamage | **120 → 96** | keeps +20% heroic bump over the reduced 80 base |
| | AttackRange | **90 → 65** | shorter chain reach |
| `ShockTrooperTeslaStunPulse` (stun) | AttackRange | **20 → 15** | ~−25% stun reach |
| `HeroicShockTrooperTeslaStunPulse` (stun, heroic) | AttackRange | **20 → 15** | ~−25% stun reach |

**Left deliberately unchanged (documented judgment):**

- **Chain/stun `DelayBetweenShots` (500 / 450)** — these are the internal cadence
  of the **spawned node's own arcs** (fired via `FireWeaponUpdate` on the node
  the primary's detonation OCL creates), *not* the trooper's own fire rate. Only
  the **PRIMARY** `DelayBetweenShots` gates how fast the trooper shoots, so only
  that one was slowed.
- **Stun subdual damage (220 / 280)** — the task asked to cut stun *range* only.
- **No separate Heroic PRIMARY weapon exists** — heroic-ness on the primary comes
  from `VeterancyProjectileDetonationOCL = HEROIC OCL_ShockTrooperTeslaChainHeroic`,
  not a `HERO` weapon set, so the primary is nerfed once. The Heroic chain and
  Heroic stun variants are nerfed alongside their regular counterparts.
- All `WeaponBonus` (GARRISONED / PLAYER_UPGRADE RANGE+DAMAGE), `DamageType`,
  `DeathType`, `WeaponSpeed`, `PrimaryDamageRadius`, projectile / OCL / detonation
  and anti-air lines are preserved verbatim.

---

## Files in the archive (2)

| File | Effective source (owner) | Change |
|---|---|---|
| `Data\INI\Weapon.ini` | `zzz-ZZZZZZZZZZZZZ0TeslaFinish.big` | 9 field lines changed across the 5 Shock Trooper weapons; every other byte identical |
| `…\China\Tank\Infantry\RotrShockTrooper.ini` | `zzz-ZZZZZZZZZInfantryScale.big` | +1 `ParticleSysBone = None TeslaBoltSparks` on the projectile; flight/detonation wiring unchanged |

## Build-time verification (all enforced; build fails loudly otherwise)

- **Effective ownership** of both re-shipped files (`Weapon.ini` ← TeslaFinish,
  `RotrShockTrooper.ini` ← InfantryScale) before editing.
- **Closure**: `TeslaBoltSparks`, `TeslaBoltRandom`, `OCL_ShockTrooperTeslaChain`
  (+ Heroic), `FX_ShockTrooperElectricRocketExplosion`, `TeslaCoilWeapon` all
  resolve in effective data.
- **Exact diff audits**: `Weapon.ini` = exactly the 9 intended field lines
  changed (byte-for-byte identical elsewhere); `RotrShockTrooper.ini` = exactly 1
  line inserted. Block (`End`) counts unchanged in both.
- **Doctrine preservation**: primary projectile/OCL/WeaponBonus/DamageType lines
  intact; node cadences 500/450 and stun subdual damage untouched.
- **Sort position + no-masking**: all data layers sort below us; only
  ControlBarPro / fx-enhance sort above and are asserted to claim **none** of our
  paths; `ParticleSystem.ini` stays fx-enhance's (we never ship it).
- BIG round-trip byte-identity; install to both mod dirs; post-install
  effective-ownership + installed-byte audit; both archives **md5-match**.
- **Not launched / not playtested** (static verification only, per convention).

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE`, patches, verifies,
writes `zzz-ZZZZZZZZZZZZZZZZ0TeslaTune.big` here, installs to both mod dirs.
Depends on `../hotkey-addon/bigfile.py`. This is the **last data layer**; rebuild
it after any lower layer that re-ships `Weapon.ini` or `RotrShockTrooper.ini`
(e.g. tesla-finish, infantry-scale). Uninstall: delete the archive from both
directories.
