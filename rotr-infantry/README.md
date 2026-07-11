# ROTR Infantry (ShockWave / GeneralsX) — side branch `side/rotr-infantry`

Standalone add-on that ports **two infantry units from Rise of the Reds
(ROTR)** into our custom ShockWave stack, re-sided for **Kwai (China Tank
General)** and buildable at his Barracks:

| Unit | Object | Cost / time | Prereq | HP | Kit |
|---|---|---|---|---|---|
| **Shmel Trooper** | `Tank_ChinaInfantryShmelTrooper` | $350 / 8 s | Tank_ WF | 100 | Thermobaric rocket launcher (FLAME, clears garrisons — 3-kill `GarrisonHitKill`), smoke rocket (blinds/decoys), anti-toxin rocket (cleans toxin+radiation fields), heroic smoke/anti-toxin variants |
| **Shock Trooper** | `Tank_ChinaInfantryShockTrooper` (3 random skins `_Var1..3`) | **$800 / 10 s** | Tank_ WF | 250 | Un-crushable **elite tesla trooper** (reworked — see *Shock Trooper tesla rework*): tesla gun is the sole armament — AP damage + subdual **stun** vs vehicles, one-shot **ignite** + small AoE vs infantry, **chain lightning** to nearby enemies (two longer-lived arcs at heroic rank), cannot attack aircraft |

Shmel stats are donor-verbatim; the Shock Trooper is repriced
$450 → $800 / 7 → 10 s for its rework (no +20% China-infantry HP
convention on either — see *Tuning knobs*).

Output archive: **`zzz-ZZZZZZZRotrInfantry.big`** (phase 1: 47 files,
12.3 MB — 9 INI + 8 W3D + 30 textures).  Case-insensitively it sorts
**after `zzz-ZZZZZZZKwaiPDL.big` and `zzz-ZZZZZZZLKwaiInfantry.big`**
(`r` > `k`/`l` at char 12) and after every other stack layer, and `-`
(0x2D) < `_` (0x5F) keeps it **before `zzz_ControlBarPro*.big`** —
asserted against the real listings of both mod dirs at build time
("last INI layer except ControlBarPro").

---

## ⚠ TWO-PHASE DESIGN (read this before merging)

The main pipeline is actively evolving — **four layers landed in the
live mod dirs while this branch was being built** (`zzz-ZZZZZZZKwaiPDL`,
`zzz-ZZZZZZZLKwaiInfantry` — which took Barracks slots 6–8 —
`zzz-ZZZZZZZTTeslaCoil` and `zzz-ZZZZZZZVetInsignia`): the build
absorbed them automatically, the slot-conflict guard in `integrate.py`
caught the Barracks change in a live dry run, and the verifier now
flags that **TeslaCoil sorts after us and bakes 6 shared files without
our appends** (see merge-day step 5).  To stay merge-safe regardless of
what lands in between, this port ships in two phases:

**Phase 1 — `build.py` (already run; output committed).**
The archive contains everything **except command-set wiring**:

- the two unit object files (+ all their system objects),
- **baked copies of the six shared fixed-name INI files** it must extend
  (`Weapon.ini`, `Armor.ini`, `Locomotor.ini`, `FXList.ini`,
  `ParticleSystem.ini`, `ObjectCreationList.ini`) = the *build-time*
  effective copy + our appends (append-only, byte-asserted),
- mapped images, W3D models, textures.

It ships **no `CommandSet.ini`, no `CommandButton.ini`, no
`Generals.str`** (asserted).  The archive is deliberately **inert**: no
button anywhere references the units, so nothing can train them.
**Never install the phase-1 archive** — its baked shared files would mask
any layer that landed after this branch's build date.

Every append also exists as a plain-text **fragment** in `fragments/`
(nine files) — the durable source of truth phase 2 replays.

**Phase 2 — `integrate.py` (run on merge day).**

```
python3 integrate.py [--shmel-slot 9] [--shock-slot 10] [--install]
```

1. Re-extracts the **then-current** effective file space from
   `~/GeneralsX/mods/ShockWaveSPE` (excluding this archive — idempotent).
2. **Regenerates all six baked shared files** from the current effective
   sources + the frozen fragments (so whatever PDL/stubs/etc. shipped in
   the meantime is preserved underneath our appends).
3. Builds `CommandSet.ini`: current effective + our two unit sets
   appended + **the Kwai Barracks sets patched** with the two construct
   buttons.  Slots are **parameterized** (defaults 9 and 10 — slot 5 is
   kwai-roster's Siege Soldier, 6–8 were taken mid-branch by the
   LKwaiInfantry stubs; only 9–11 remain).  The Barracks sets are
   **discovered from the effective `Tank_ChinaBarracks` object** (its
   `CommandSet` plus every `CommandSetUpgrade` module), so renames/new
   variants in interim layers are handled.  Occupied slots abort with a
   clear message — pick other slots (proven live when slots 6–8 filled).
4. Builds `CommandButton.ini` (+4 buttons) and `Data\Generals.str`
   (+14 entries) as pure appends on the current effective copies.
5. Repacks `zzz-ZZZZZZZRotrInfantry.big` **in place** and re-runs the
   full static verification in phase-2 mode (adds a CommandSet.ini
   diff-audit: barracks sets differ *only* by our slot lines, every other
   set byte-identical to the effective source).
6. `--install` copies it to both mod dirs; without it nothing is touched.

### Merge-day checklist

1. Merge `side/rotr-infantry` into the main branch.
2. Make sure every lower layer is final and rebuilt in its documented
   order (…, chaos-units, kwai-roster, kwai-uav, kwai-pdl, …) and
   installed in the mod dirs.
3. `cd rotr-infantry && python3 integrate.py` — review the output
   (barracks sets discovered, slots taken, verification green).
   If slots 9/10 are taken by then: `--shmel-slot N --shock-slot M`.
4. Re-run with `--install` to copy into both mod dirs.
5. **Rebuild every layer that sorts after this archive and bakes shared
   INI files** — currently `zzz-ZZZZZZZTTeslaCoil.big` (its baked
   Weapon.ini / ParticleSystem.ini / OCL / CommandSet / CommandButton /
   Generals.str were built without our appends and will mask this port
   until rebuilt on top of the installed archive; the verifier prints
   an explicit WARNING listing such layers).  `zzz-ZZZZZZZVetInsignia`
   is mapped-images-only and unaffected.
6. **Rebuild-order note (permanent):** like every layer that bakes shared
   files, this becomes the last INI layer.  If ANY lower layer is rebuilt
   later, re-run `integrate.py --install` afterwards.  Conversely, lower
   layers' builds must not see this archive — delete
   `zzz-ZZZZZZZRotrInfantry.big` from both mod dirs first, rebuild the
   lower chain, then re-run `integrate.py --install`.
7. Uninstall = delete `zzz-ZZZZZZZRotrInfantry.big` from both mod dirs
   (then rebuild the later-sorting layers once more so their baked
   shared files drop our appends).

---

## Shock Trooper tesla rework (the tesla gun is now the unit)

Per the follow-up spec the rocket-rifle mode was **removed outright**:
the donor's dual-mode draw was replaced by a tesla-only draw generated
from the donor's RIDER2 condition states (all three skins + the
buildable shell's preview draw), the nine `ModuleTag_Transform01..09`
rider/switch modules were stripped, and the rocket rifle, guided
missile, both mode-switch buttons/weapons/OCLs, the mode-trigger slave
objects, two locomotors and the `RIShkTrp*` skins/anims left the
closure.

### The engine facts that shaped the weapon (source evidence)

- **A unit only ever fires its ONE current weapon.**
  `AIAttackFireWeaponState::update` calls `obj->fireCurrentWeapon(...)`
  (AIStates.cpp:5258), which fires `m_weaponSet.getCurWeapon()` only
  (Object.cpp:1529-1549).  Multi-slot "volleys" from a single body or
  turret do not exist (the only all-slots loop is for LINKED multi-
  turret POSITION attacks, AIStates.cpp:5306-5318).  The initial
  three-slot volley design was therefore impossible; worse, the weapon
  chooser (`WeaponSet::chooseBestWeaponForTarget`, WeaponSet.cpp:802)
  picks the highest `estimateWeaponDamage`, and a subdual weapon
  estimates ~full damage vs any vehicle with a subdual cap
  (ActiveBody.cpp `estimateDamage`) — the unit would have locked onto
  the zero-health-damage stun beam against tanks forever.
- **A turret only aims the current weapon.**  `TurretAI::
  setTurretTargetObject` refuses any target while the owner's current
  weapon is not on that turret (TurretAI.cpp:559) — the donor turret
  idiom routes aiming, it does not parallel-fire.  The unit's internal
  turret was **removed** (the impact node keeps its own).
- **Detonation OCLs run at the projectile, not the shooter.**
  `ObjectCreationList::create(ocl, sourceObj, ...)` (Weapon.cpp:952-955)
  is invoked with the PROJECTILE as source when it detonates — so the
  warhead machinery is container-agnostic.
- **`VeterancyProjectileDetonationOCL` exists** (Weapon.cpp:200, same
  per-vet parser ShockWave already uses for the Grenadier's
  `VeterancyFireOCL`) — correcting this README's earlier claim that
  per-rank detonation OCLs were an engine gap.
- **Armor tables** (effective Armor.ini): `TankArmor` MELEE 0% (the
  donor beam literally could not hurt tanks here), **EXPLOSION 100% on
  BOTH `TankArmor` and `HumanArmor`**, FLAME 150% vs humans / 25% vs
  tanks, `SUBDUAL_UNRESISTABLE` 100% vs TankArmor, **0% vs HumanArmor**.

### The weapon (one slot, everything in the warhead)

`ShockTrooperTeslaWeapon` — **150 EXPLOSION, radius 20, range 140, one
bolt every 2.4 s**, `DeathType = BURNED`, fired from the `MUZZLE01`
launch bone; the bolt is `ShockTrooperTeslaBoltProjectile` (speed 400,
near-flat trajectory, crackling `TeslaTrooperFlare` trail), detonating
in the donor's `FX_ShockTrooperElectricRocketExplosion` electric blast:

- **vs infantry**: 150 (EXPLOSION = 100%) one-shots every standard
  infantryman (100-140 HP incl. buffed Red Guards) in a 20-radius blast;
  heroes at 200-300 HP survive (the documented no-unrealistic-hero-
  one-shot line).  `BURNED` death = they go up in flames
  (`OCL_FlamingInfantry`).
- **vs vehicles**: 150/2.4 s = **62.5 dps** — respectable, not token
  (plus splash from chain zaps).
- **STUN**: the warhead spawns an impact node whose `FireWeaponUpdate`
  (fire-field idiom, FireWeaponUpdate.cpp:101 fires at the node's own
  position) radiates `ShockTrooperTeslaStunPulse` — **220
  SUBDUAL_UNRESISTABLE, radius 16, every 450 ms** for the node's
  1.1-1.3 s life (~2-3 pulses per bolt).  Vehicles accumulate subdual
  until it passes MaxHealth → `DISABLED_SUBDUED` (ActiveBody.cpp:1330,
  onSubdualChange), decaying at the target's own heal rate: a
  Battlemaster (660 HP, cap 1130, decay 100/s) is stunned after ~2
  sustained volleys (~5 s of fire) and stays stunned up to ~4.7 s after
  fire shifts; light vehicles stun off the first bolt.  Infantry are
  immune (HumanArmor 0%).
- **CHAIN LIGHTNING**: the same node auto-acquires (vision 90, 3600°/s
  internal turret so it never needs to face) and zaps
  `ShockTrooperTeslaChainZap` — 100 FLAME, radius 12, range 90, `BURNED`
  — drawn with the real `TeslaTrooperLaserBeam` bolt objects: visible
  arcs from the impact point to 1-2 further enemies, one-shotting
  standard infantry (100 x 1.5 = 150 post-armor).  Depth-1 (the zap has
  no OCL of its own — no infinite chaining).
- **Rank scaling**: `VeterancyProjectileDetonationOCL = HEROIC
  OCL_ShockTrooperTeslaChainHeroic` on the same weapon — heroic bolts
  spawn **two** longer-lived (1.4-1.6 s) nodes with stronger pulses
  (280) and red heroic-bolt zaps (120 FLAME).  VETERAN/ELITE OCL steps
  are also possible with this field (single-line knobs) but only HEROIC
  is used, keeping the vanilla feel.
- **No anti-air** (spec): every tesla weapon pins `AntiGround = Yes`,
  `AntiAirborneVehicle/Infantry = No`; the tooltip says so.
- **XP note**: the 150-damage warhead is the trooper's own weapon, so
  kills level him; node stun/chain kills credit the node (bonus
  damage, no XP) — acceptable, documented.

**Tesla-family harmonization (landed)**: the RA-Redux **Tesla Coil**
(`zzz-ZZZZZZZTTeslaCoil.big`) shipped mid-branch with the authentic RA
tesla zap audio — our tesla gun and chain zaps now use its
`TeslaCoilWeapon` sound event (**soft dependency**: if that layer is
ever uninstalled the zaps go silent — single-line knob back to
`AvengerPointDefenseLaserPulse` in `work/portlib.py`).

**Command set**: attack-move / guard / stop only.  Cost **$800 / 10 s**
(coordinator range $700-900): 62 dps AT + stun + infantry deletion,
balanced by range 140 and total air/artillery helplessness.

## Contained / garrisoned fire (verified against engine source)

Requirement: Shock Troopers must fire from garrisoned buildings, China
bunkers and the stack's tank bays (Battlemaster/Emperor
`PassengersAllowedToFire` seats).  Static verification:

1. **KindOf gates pass.**  `GarrisonContain::isValidContainerFor` only
   rejects `KINDOF_NO_GARRISON` passengers (GarrisonContain.cpp:567) on
   top of the `OpenContain` allow/forbid masks (OpenContain.cpp:931-938),
   and garrison's default allow-mask is `INFANTRY`
   (GarrisonContain.cpp:70).  The trooper is `INFANTRY`, carries no
   `NO_GARRISON`/`AIRCRAFT`/`VEHICLE`/`BOAT` bits, and the stack's bays
   admit exactly that (effective Emperor bay: `AllowInsideKindOf =
   INFANTRY`, `ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT`,
   `PassengersAllowedToFire` present on Battlemaster/Emperor/bunkers).
   `ATTACK_NEEDS_LINE_OF_SIGHT` matches the vanilla Tank Hunter — which
   fires projectiles from garrisons all day — KindOf-for-KindOf.
2. **The firing path is the proven vanilla one.**  With the internal
   turret REMOVED (see above), a contained trooper attacks exactly like
   a garrisoned Tank Hunter: the aim state moves him to the container's
   `FIREPOINT` bones (`attemptBestFirePointPosition`,
   AIStates.cpp:4941-4955; `OpenContain::putObjAtNextFirePoint`,
   OpenContain.cpp:1278) and `fireCurrentWeapon` launches the bolt from
   there.  Garrisoned range bonus: the weapon keeps the donor's
   `WeaponBonus = GARRISONED RANGE 145% / DAMAGE 125%` lines
   (140 → 203 range from buildings).  Had the turret stayed, contained
   fire would have been hostage to the turret gate
   (TurretAI.cpp:559) — removing it was required by the volley findings
   anyway.
3. **The warhead is container-agnostic.**  The stun/chain node spawns
   from the PROJECTILE's detonation (Weapon.cpp:952:
   `ObjectCreationList::create(ocl, sourceObj=projectile, ...)`), whose
   position is the impact point — the shooter's containment never
   enters that code path.  (A `FireOCL` would have spawned at the
   garrisoned shooter — that is why the bolt is a projectile.)

## What was ported (closure: 99 new top-level blocks)

| Where | Blocks |
|---|---|
| `Object\China\Tank\Infantry\RotrShmelTrooper.ini` | 10 — unit, thermobaric rocket, smoke/anti-toxin projectiles (+2 heroic reskins), anti-toxin foam, smoke screen, burning-embers fire field, generic hit-scan pellet projectile |
| `Object\China\Tank\Infantry\RotrShockTrooper.ini` | 26 — buildable shell + `_Var1..3` skins (tesla-only draws), tesla bolt projectile, 2 stun/chain nodes, tesla beam + 8 bolts, heroic beam + 8 heroic bolts, tesla-death infantry |
| `MappedImages\HandCreated\RotrInfantryMappedImages.INI` | 6 cameos (unit + portrait + 2 Shmel ability icons) |
| `Weapon.ini` append | 15 (3 Shmel launchers + 2 heroic + pellets + fire-field weapons + smoke/foam field weapons; tesla gun + 2 stun pulses + 2 chain zaps) |
| `Armor.ini` append | 2 (`ShockTrooperArmor`, `InvulnerableArmorAll`) |
| `Locomotor.ini` append | 2 |
| `FXList.ini` append | 7 (incl. the **thermobaric `WeaponFX_ShmelRocketExplosion`** + upgraded variant, electric arc impact, tesla die FX) |
| `ParticleSystem.ini` append | 16 (Shmel explosion/exhaust/anti-toxin family, **ShmelPoolFire** fire-field, tesla flares + `ShockTrooperTeslaBlast`) |
| `ObjectCreationList.ini` append | 9 (incl. the 2 chain OCLs) |
| `CommandSet.ini` fragment | 2 unit sets |
| `CommandButton.ini` fragment | 4 (2 construct + smoke/anti-toxin fire buttons) |

**Reused from base instead of ported** (ShockWave shares a lot of
community stock with ROTR): `ChemSuitHumanArmor`,
`MissileDefenderLocomotor`, `OCL_FlamingInfantry/Toxic*/Microwaved/
Radiation*/Neutron*/BrutalBloody/BloodyGore`, `FX_GIDie*`,
`FX_InfantryGoreExplosion`, `NukeGroundAttack`/`TomahawkGroundAttack`
shared-cooldown specials, `ViralGasCloud`, `ToxicInfantryGamma`,
vanilla `NITHNT_*` Tank-Hunter animation set (Shmel is rigged on it) and
ShockWave's `NIGATT_*` tesla-trooper animation set (byte-identical to
ROTR's, see art section), `MoneyWithdraw`, `InfantryDustTrails`, etc.

## Deliberate drops / deviations (all verified absent from shipped bytes)

| Donor piece | Decision + rationale |
|---|---|
| **Grizon Airdrop** (`OCLSpecialPower` on both units) | dropped — Russia general-power hook; would pull the Grizon transport plane + paradrop closure |
| **Russia upgrades** MedPack / Larger Clips / Advanced Missile Engines (modules, `UpgradeCameo`s, PLAYER_UPGRADE weaponsets, `…UpgradedCommandSet`) | dropped — Kwai can never research them; the 5 "Upgraded" weapon variants go with them |
| **Anti-toxin rocket button** (donor: unlocked by Larger Clips) | in our single command set **from the start** (slot 3) — the tertiary weapon exists un-upgraded in the donor weaponset; only its button was gated |
| **Thermobaric fire-field** (`FireWeaponWhenDeadBehavior` on the rocket, donor `TriggeredBy = Upgrade_RussiaLargerClips`, `StartsActive = No`) | **re-keyed to `Upgrade_ChinaBlackNapalm`** — Kwai *can* research Black Napalm (kwai-artillery moved it to his Prop Center), so the burning-ground pools become his incendiary-upgrade payoff; donor's upgrade-gated balance preserved |
| **POW/surrender + suicide theatre** (surrender crate object, `EXTRA_8` death modules, `RussiaInfantryShockTrooperCommitingSuicide`, related FX/OCL) | dropped — nothing in base ShockWave inflicts the `EXTRA_8` surrender death; the crate chain drags in ROTR's CIA-intel/capture-science system.  Catch-all death modules re-own `EXTRA_8` (DeathTypes line edited) |
| **Berserker-on-death** (`CreateObjectDie → OCL_InfantryBeserkerObject`) | dropped — ROTR-wide rage-aura flavor system |
| **Cryogenic LASERED death** (`OCL_CrygenicDeathInfantry` + 7 `CICryoDth_*` body-part models) | dropped — in base ShockWave `LASERED` deaths come from *lasers* (Townes), not cryo weapons; a freeze-shatter would be wrong flavor.  Catch-all re-owns `LASERED` |
| **Rocket-rifle mode + RiderChangeContain switch machinery** (rocket rifle, guided missile, 2 switch weapons/buttons/OCLs, 2 mode-trigger slave objects, 2 locomotors, casing/tracer FX, `SCIENCE_TeslaTech` gate, `RIShkTrp*` skins/anims, `EXShkDrt` missile art) | dropped in the tesla rework — the tesla gun is the unit's sole armament (see the rework section); the buildable shell's preview draw was also switched to the tesla model.  The base `GenericFakeRider` framework it used remains untouched in base data |
| **Prerequisites** `RussiaWarFactory` / `RussiaWeaponsBunker` | remapped to `Tank_ChinaWarFactory` (porting them would pull the entire Russia faction — measured: closure exploded 120 → 972 blocks) |
| **Death-voice FX wrappers** (`FX_ShmelTrooperDie*`, `FX_ShockTrooperDie*` — donor FXLists that only wrap a ROTR voice line) | remapped to vanilla `FX_GIDie` (canonical infantry death FX) |
| `Side = Russia` | `ChinaTankGeneral` on the unit family (matches every Kwai-owned `Tank_*` object); system objects likewise, `TeslaInfantry` stays `Civilian` (donor) |
| **Kept** despite exotic death types | tesla death (`POISONED_GAMMA` → `OCL_TeslaDeathInfantry` + the `TeslaInfantry` electro-corpse; its `CITESLA_SKN` model already ships in `!ShwW3D.big`) and viral death (`EXTRA_3` → `OCL_ViralInfantryDeath`, resolves entirely against base objects) — both cheap and self-contained; our own tesla weapons inflict `POISONED_GAMMA`, so mirror-match deaths look right |

## Audio remaps (ROTR voices are not in any obtainable INI-space match; full table)

ROTR's voice *definitions* are in the donor Voice.ini/SoundEffects.ini,
but the .wav data lives in `!Rotr_Voice.gib` (373 MB) / `!Rotr_Audio.gib`
(183 MB) and porting them would also mean merging two more shared INI
files (Voice.ini, SoundEffects.ini).  Per spec they are **remapped to
base events** instead (future option: ranged-fetch the ~15 needed .wavs
and ship real voices — the fetch tooling in `work/rotrfetch.py` already
supports it).

| ROTR event | Base event | Note |
|---|---|---|
| `ShmelTrooperVoice{Select,Move,Attack,Fear,Create,Die}` | `TankHunterVoice{…}` | China missile infantry — closest vanilla kin |
| `ShmelTrooperVoice{SmokeAttack,AntiToxinAttack}` | `TankHunterVoiceAttack` | |
| `ShockTrooperVoice{Select,Move,Attack,AttackTesla,Fear,Create,Garrison}` | `PyroVoice{…}` (`AttackTesla`→`Attack`) | ShockWave China suited flame trooper — heavy-suit flavor |
| `ShmelRocketLauncherWeapon` | `TankHunterWeapon` | |
| `ShmelRocketExplosion` | `ExplosionFire` | thermobaric fireball |
| tesla zap `FireSound` (gun + chain, authored weapons) | `TeslaCoilWeapon` | the RA tesla zap from the `zzz-ZZZZZZZTTeslaCoil` layer (soft dependency; fallback knob: `AvengerPointDefenseLaserPulse`) |
| `ShockTrooperRocketElectricExplosion` | `ExplosionPatriotEMP` | arc impact (inside `FX_ShockTrooperElectricRocketExplosion`) |
| `InfantryTeslaDeathShock` | `ExplosionPatriotEMP` | tesla death zap |
| `MoleBombDirstSound` | `ExplosionDirt` | smoke rocket ground burst |
| `ShmelRocketAntiToxin{Activated,Detonation}` | `ExplosionFlashBang` | foam pop |
| fire-field ambient `GenericFireMediumLoop` | — | already exists in base (no remap) |

## Strings: what ROTR uses, what we ship

**Finding:** ROTR uses **`Data\Generals.str`** (760 KB, inside
`!Rotr_English.gib`) — the *same* mechanism as our stack (engine prefers
`Data\Generals.str`; GeneralsX falls back to the CSF for missing labels).
ROTR's donor INI tree contains no .str/.csf; the file was ranged-fetched
from the bucket and the **authentic donor texts** extracted for our 14
append-only entries (fresh collision-safe keys: `OBJECT:TankShmelTrooper`,
`CONTROLBAR:TankShmel*` / `…TankShockTrooper*`).  Two edits: the
"Fights harder when a nearby comrade falls" tooltip line went with the
berserker drop, and a donor typo (doubled closing quote) was fixed.

## Art download approach (ranged fetch — no 158/204 MB downloads)

`work/rotrfetch.py` never downloads the .gib archives whole: one Range
request reads the 16-byte BIGF header, one more pulls the index table,
then each needed file is fetched by its exact byte range from
`http://gen.insave.ovh:9000/rotr/rotr-individual-files/`.  Total
transferred: ~9 MB for 20 W3D + 37 textures + the 760 KB Generals.str.

- **Archive preference for duplicate paths**: `!!!Rotr_Intrnl_Main.gib` >
  `!!Rotr_Patch.gib` > `!Rotr_W3D.gib` / `!Rotr_Textures.gib` /
  `!Rotr_2D.gib` / `!Rotr_English.gib` — ROTR's `!!!/!!/!` naming is
  built around the original engine's first-archive-wins order, so the
  earliest-sorting archive is the newest hotfix layer (e.g. the Shmel
  skin `RIShmlTrp_SKN.W3D` comes from the Patch gib).
- Everything is cached under `cache/` (per-archive index JSONs +
  `cache/fetched/<archive>/…`), so rebuilds are **offline** and the cache
  is **reusable for future ROTR ports** (the indexes cover all six
  archives; any file can be fetched by basename).
- Base-presence first: an asset is only shipped if its basename is
  missing from vanilla (`ZH_Generals/W3D.big`, `Textures.big`,
  `W3DZH.big`, `TexturesZH.big`, …) and the whole SPE mod dir.  Shipping
  a same-named file would globally override the base copy (we sort last),
  so W3D-internal textures resolve against base wherever possible.
  **Same-name safety verified**: ShockWave and ROTR are both SWR mods and
  share asset stock — every ROTR-named W3D we reuse from `!ShwW3D.big`
  (`NIGATT_*` tesla-trooper anim set, `CITESLA_SKN`) was byte-compared
  against ROTR's copy and is **identical**, so the `RITslTrp*` meshes rig
  onto the exact skeleton they were built for (`NIGATT_IDC`/`NIGATT_PAT`
  are ROTR-only additions and ship in the archive).
- **Cameo pages are the exception**: ROTR's `SNRUserInterface512_00N`
  pages collide by *name* with pages other layers ship (chaos-units ships
  its own `SNRUserInterface512_003.tga` with different contents!).  The
  four pages our 6 `MappedImage`s need are therefore force-shipped
  **renamed** (`Rotr_`-prefixed) with the `Texture =` lines rewritten.
  (`Rotr_Russia_ScoreScreenuserinterface.tga` is a 3 MB 1024² page that
  hosts one 60×48 icon — donor layout kept for fidelity; cropping it is a
  possible size optimization.)
- W3D binaries are chunk-parsed (`work/resolve_art.py`) to close over
  **internal texture references** (that's how `Zhca_RI*.tga`,
  `EXRedGrdnt.dds`, `EXShkTrpRk.dds` were found), and every model
  condition state / animation / particle / shadow / cameo texture is
  presence-asserted at build time.

## Stats / tuning knobs (not applied — ship donor stats per spec)

- **No +20% China-infantry HP convention.** To apply later: `MaxHealth`
  100→120 (Shmel) / 250→300 (Shock Trooper) in the two object files.
- **Infantry Conditioning (kwai-doctrine +15%/tier)** does NOT cover
  these units — doctrine's `MaxHealthUpgrade` modules target specific
  vanilla objects.  Future integration option: add 4 `MaxHealthUpgrade`
  modules per unit (`TriggeredBy Upgrade_KD_InfCond1..4`, +15/+37.5 HP
  per tier) — but that belongs in kwai-doctrine's build, which would then
  need to own these files' modules (coordinate, don't duplicate).
- Fire-field availability: re-keyed to Black Napalm (see above); to make
  it innate instead, set `StartsActive = Yes` and drop `TriggeredBy` on
  `ModuleTag_MoreBoom01` in `RotrShmelTrooper.ini`.
- Sound flavor knobs: `ExplosionDaisyCutter` is a beefier (fuel-air!)
  alternative for `ShmelRocketExplosion`'s remap; the tesla zaps now use
  the Tesla Coil layer's authentic `TeslaCoilWeapon` (soft dependency —
  single-line fallback to `AvengerPointDefenseLaserPulse` in
  `work/portlib.py`).
- Shock Trooper balance knobs (all in `work/portlib.py` `AUTHORED` /
  `SHOCK_COST`): warhead 150 EXPLOSION r20 @ 2.4 s, stun pulse 220
  SUBDUAL r16 @ 450 ms (heroic 280), chain zap 100 FLAME r12 (heroic
  120), node life 1.1-1.3 s (heroic 1.4-1.6 s x2), $800/10 s.

## Build-time verification (all enforced; build fails loudly)

- BIG round-trips byte-identically; archive is asserted the **last INI
  layer** (only `zzz_ControlBarPro*` after it) against the real listings
  of both mod dirs.
- Phase-1 invariant: no `CommandSet.ini` / `CommandButton.ini` /
  `Generals.str` in the archive (phase 2 asserts the opposite, plus the
  CommandSet diff-audit: barracks sets differ only by our slot lines,
  every other set byte-identical to the effective source).
- Baked shared files assert `startswith(effective source)` (append-only).
- Closure: every donor-defined identifier referenced by shipped text
  resolves in vanilla ∪ effective ∪ this archive; every DROPPED
  identifier is asserted absent; string labels resolve against our
  fragment ∪ effective `Generals.str` ∪ vanilla `generals.csf`;
  `DamageType`/`DeathType` tokens all appear in the base `Weapon.ini`
  (`SUBDUAL_UNRESISTABLE`, `MELEE`, `EXTRA_*` all verified in use there).
- Art: every model / animation (incl. skeletons) / texture /
  W3D-internal texture / cameo page resolves in archive ∪ base archives.
- No identifier collisions: all 99 new block names word-checked against
  the full base INI space.
- Block balance: every shipped chunk re-parses with zero stray content.
- **The game was deliberately not launched** (static verification only).

## Rebuild

```
python3 build.py        # phase 1: regenerates fragments + archive; never installs
python3 integrate.py    # phase 2: merge-day wiring; --install to deploy
```

Depends on `../hotkey-addon/bigfile.py` (+`csf.py`) and
`../chaos-units/work/iniblocks.py` (both in this repo), the donor tree at
`../donor-inis/rotr_ini/` (falls back to the main worktree's copy), the
local game install (`~/GeneralsX/GeneralsZH` incl. `ZH_Generals/`) and
mod dirs (read-only for phase 1).  Network only on cold cache.

`work/trace_closure.py` regenerates `work/closure_report.txt` (the
port/reuse/drop audit this port was designed from).

## Known limitations

- **Not game-tested** (side branch; static verification only).  First
  in-game checks to do: the bolt projectile's flat flight + electric
  burst, the chain node auto-acquiring and arcing (`W3DLaserDraw`
  bolts) to a second victim, vehicle stun onset/duration under
  sustained fire, one-shot-ignite on standard infantry vs hero
  survival, **firing from a garrisoned building / China bunker /
  Battlemaster-Emperor bay** (enter, attack, fire-point placement,
  garrison range bonus), that the unit refuses air targets,
  smoke-screen pellet spread, anti-toxin field actually clearing
  toxins, fire-field spawning after Black Napalm.
- Phase-1 archive is inert by design; units are unreachable until
  `integrate.py` runs.
- Voice/weapon audio are base-ShockWave approximations (table above).
- The smoke rocket's `TomahawkGroundAttack` / anti-toxin's
  `NukeGroundAttack` shared-cooldown special-power tokens are also used
  by their vanilla owners — same-player Tomahawk/Nuke-cannon ground
  attacks share reload timers with these rockets (donor behaves the same
  way; cosmetic at worst).
- Save games crossing an install/uninstall boundary may not load (new
  object types). Start fresh.
- AI never builds these (no AIData/build-list changes); player-only.

## Provenance

Unit designs, INI data, models, textures and strings originate from
**Rise of the Reds** by SWR Productions; ported for personal use from the
mod's public distribution on the listable bucket.  Base-game and
ShockWave assets are referenced in place, never redistributed.
