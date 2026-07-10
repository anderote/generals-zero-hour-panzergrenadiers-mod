# ROTR Infantry (ShockWave / GeneralsX) — side branch `side/rotr-infantry`

Standalone add-on that ports **two infantry units from Rise of the Reds
(ROTR)** into our custom ShockWave stack, re-sided for **Kwai (China Tank
General)** and buildable at his Barracks:

| Unit | Object | Cost / time | Prereq | HP | Kit |
|---|---|---|---|---|---|
| **Shmel Trooper** | `Tank_ChinaInfantryShmelTrooper` | $350 / 8 s | Tank_ WF | 100 | Thermobaric rocket launcher (FLAME, clears garrisons — 3-kill `GarrisonHitKill`), smoke rocket (blinds/decoys), anti-toxin rocket (cleans toxin+radiation fields), heroic smoke/anti-toxin variants |
| **Shock Trooper** | `Tank_ChinaInfantryShockTrooper` (3 random skins `_Var1..3`) | $450 / 7 s | Tank_ WF | 250 | Un-crushable heavy trooper; **switchable weapon modes**: 8-round rocket rifle ↔ **tesla gun** (damage beam + vehicle-disabling `SUBDUAL_UNRESISTABLE` beam, heroic bolt variants) |

All stats are **donor-verbatim** (per spec: no +20% China-infantry HP
convention applied — see *Tuning knobs*).

Output archive: **`zzz-ZZZZZZZRotrInfantry.big`** (phase 1: 61 files,
13.4 MB — 9 INI + 20 W3D + 32 textures).  Case-insensitively it sorts
**after `zzz-ZZZZZZZKwaiPDL.big`** (`r` > `k` at char 12) and after every
other stack layer, and `-` (0x2D) < `_` (0x5F) keeps it **before
`zzz_ControlBarPro*.big`** — asserted against the real listings of both
mod dirs at build time ("last INI layer except ControlBarPro").

---

## ⚠ TWO-PHASE DESIGN (read this before merging)

The main pipeline is actively evolving (the **KwaiPDL layer landed in the
live mod dirs while this branch was being built** — the build absorbed it
automatically; an infantry-stubs layer is expected too).  To stay
merge-safe regardless of what lands in between, this port ships in two
phases:

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
python3 integrate.py [--shmel-slot 6] [--shock-slot 7] [--install]
```

1. Re-extracts the **then-current** effective file space from
   `~/GeneralsX/mods/ShockWaveSPE` (excluding this archive — idempotent).
2. **Regenerates all six baked shared files** from the current effective
   sources + the frozen fragments (so whatever PDL/stubs/etc. shipped in
   the meantime is preserved underneath our appends).
3. Builds `CommandSet.ini`: current effective + our two unit sets
   appended + **the Kwai Barracks sets patched** with the two construct
   buttons.  Slots are **parameterized** (defaults 6 and 7; kwai-roster
   put Siege Soldier at 5, 6–11 were free).  The Barracks sets are
   **discovered from the effective `Tank_ChinaBarracks` object** (its
   `CommandSet` plus every `CommandSetUpgrade` module), so renames/new
   variants in interim layers are handled.  Occupied slots abort with a
   clear message — pick other slots.
4. Builds `CommandButton.ini` (+6 buttons) and `Data\Generals.str`
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
   If slots 6/7 are taken by then: `--shmel-slot N --shock-slot M`.
4. Re-run with `--install` to copy into both mod dirs.
5. **Rebuild-order note (permanent):** like every layer that bakes shared
   files, this becomes the last INI layer.  If ANY lower layer is rebuilt
   later, re-run `integrate.py --install` afterwards.  Conversely, lower
   layers' builds must not see this archive — delete
   `zzz-ZZZZZZZRotrInfantry.big` from both mod dirs first, rebuild the
   lower chain, then re-run `integrate.py --install`.
6. Uninstall = delete `zzz-ZZZZZZZRotrInfantry.big` from both mod dirs.

---

## What was ported (closure: 109 new top-level blocks)

| Where | Blocks |
|---|---|
| `Object\China\Tank\Infantry\RotrShmelTrooper.ini` | 10 — unit, thermobaric rocket, smoke/anti-toxin projectiles (+2 heroic reskins), anti-toxin foam, smoke screen, burning-embers fire field, generic hit-scan pellet projectile |
| `Object\China\Tank\Infantry\RotrShockTrooper.ini` | 26 — buildable shell + `_Var1..3` skins, guided missile, 2 mode-trigger objects, tesla beam + 8 bolts, heroic beam + 8 heroic bolts, tesla-death infantry |
| `MappedImages\HandCreated\RotrInfantryMappedImages.INI` | 8 cameos (unit + portrait + 4 ability icons) |
| `Weapon.ini` append | 17 (3 Shmel launchers + 2 heroic + pellets + fire-field weapons + smoke/foam field weapons, rocket rifle, 2×tesla + 2×heroic tesla, 2 mode-switch weapons) |
| `Armor.ini` append | 2 (`ShockTrooperArmor`, `InvulnerableArmorAll`) |
| `Locomotor.ini` append | 4 |
| `FXList.ini` append | 9 (incl. the **thermobaric `WeaponFX_ShmelRocketExplosion`** + upgraded variant, tesla die FX) |
| `ParticleSystem.ini` append | 16 (Shmel explosion/exhaust/anti-toxin family, **ShmelPoolFire** fire-field, tesla flares, rocket casings) |
| `ObjectCreationList.ini` append | 9 |
| `CommandSet.ini` fragment | 2 unit sets |
| `CommandButton.ini` fragment | 6 (2 construct + smoke/anti-toxin fire buttons + 2 mode switches) |

**Reused from base instead of ported** (61 identifier reuses, 46 art
reuses — ShockWave shares a lot of community stock with ROTR): the whole
**GenericFakeRider1/2 rider-switch framework** (`RiderChangeContain`
donor idiom works against base's own `FakeRiders.ini` +
`OCL_GenericDummyRider*_Normal`), `Upgrade_GLAWorkerReal/FakeCommandSet`
mode tokens (same engine-wide pair chaos-units uses for factory pages —
per-object, no cross-talk), `ChemSuitHumanArmor`,
`MissileDefenderLocomotor`, `OCL_FlamingInfantry/Toxic*/Microwaved/
Radiation*/Neutron*/BrutalBloody/BloodyGore`, `FX_GIDie*`,
`FX_InfantryGoreExplosion`, `NukeGroundAttack`/`TomahawkGroundAttack`
shared-cooldown specials, `ViralGasCloud`, `ToxicInfantryGamma`,
vanilla `NITHNT_*` Tank-Hunter animation set (Shmel is rigged on it),
`SuicideUnresistableWeapon`, `MoneyWithdraw`, `InfantryDustTrails`, etc.

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
| **`SCIENCE_TeslaTech` gate** on the tesla-mode switch | dropped — ROTR science Kwai can't buy; tesla mode is the unit's signature |
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
| `ShockTrooperVoiceMode{Rifle,TeslaGun}` (switch acks) | `PyroVoiceMove` | |
| `ShmelRocketLauncherWeapon` | `TankHunterWeapon` | |
| `ShmelRocketExplosion` | `ExplosionFire` | thermobaric fireball |
| `ShockTrooperRifleWeapon` | `RocketBuggyWeapon` | rapid rocket burst |
| `ShockTrooperTeslaWeaponSound` (40 ms loop) | `AvengerPointDefenseLaserPulse` | closest electric zap loop in base |
| `GenericAutoCannonDetonationImpact` | `ExplosionRocketBuggyMissile` | rifle-rocket impact |
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
- **Cameo pages are the exception**: ROTR's `SNRUserInterface512_002/3/4`
  collide by *name* with pages other layers ship (chaos-units ships its
  own `SNRUserInterface512_003.tga` with different contents!).  The five
  pages our 8 `MappedImage`s need are therefore force-shipped **renamed**
  (`Rotr_`-prefixed) with the MappedImage `Texture =` lines rewritten.
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
  alternative for `ShmelRocketExplosion`'s remap; the tesla loop is the
  weakest approximation (`AvengerPointDefenseLaserPulse`) — real ROTR
  audio is the better long-term fix.

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
- No identifier collisions: all 109 new block names word-checked against
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
  in-game checks to do: mode-switch button flip on the Shock Trooper
  (rider swap + set swap), tesla beam rendering (`W3DLaserDraw` bolts),
  smoke-screen pellet spread, anti-toxin field actually clearing toxins,
  fire-field spawning after Black Napalm.
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
