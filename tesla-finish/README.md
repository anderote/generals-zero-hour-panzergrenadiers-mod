# Tesla Finish (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX (macOS), for
**Kwai (China Tank General)**. One layer, three features:

1. **Tesla Tank** — the Red Alert Redux tesla vehicle, ported as a buildable
   Kwai medium tank at the War Factory.
2. **Tesla FX harmonization** — every tesla weapon in the Kwai roster now
   fires the same family bolt visual + zap sound.
3. **Overlord removal** — the plain Overlord build button is pulled from the
   War Factory roster (the Emperor + Tesla Tank fill that role); the Tesla
   Tank takes its slot.

Output archive: **`zzz-ZZZZZZZZZZZZZ0TeslaFinish.big`** (26 files, ~4.8 MB —
INI + STR + 6 W3D models + 13 donor textures; installed to both mod dirs).
13 Z's + `0` sorts **after** `zzz-ZZZZZZZZZZZZ0EmperorDefense.big` (12 Z's, the
previous top INI layer) and — because `-` (0x2D) < `_` (0x5F) < `z` (0x7A) —
**before** `zzzz_FXEnhance.big` and `zzz_ControlBarPro*`. Verified against the
real listings of both mod dirs at build time. **This is now the last INI
layer of the stack** (only fx-enhance / ControlBarPro sort after it, and they
claim none of our shipped paths).

## Asset provenance / credits

Tesla Tank object design, INI data, W3D models, textures and cameo originate
from **C&C Red Alert Redux 1.0.5 by sgtmyers88** (and team), extracted from
the mod's public distribution (`~/GeneralsX/donors/RARedux/` —
`00_CCRARDXINI.big` / `00_CCRARDXART.big`, read directly and drift-guarded at
build time). **Personal use only — no redistribution; all credit to
sgtmyers88 / the CCRARDX team.**

---

## Task 1 — RA Redux Tesla Tank

Donor object **`SovietTankTeslaTank`** (RARedux `SovietVehicle.ini`), ported
as **`Tank_ChinaTeslaTank`** — a buildable Kwai medium tank at the **War
Factory page 2 slot 4** (the slot the plain Overlord vacates, Task 3).

### Art choice: **BUNDLED** (donor provides its own model)

The donor ships a dedicated tesla-tank model, so the donor art is bundled
(the preferred option) rather than reskinning onto a Battlemaster/Gattling
chassis. Shipped from `00_CCRARDXART.big`:

- **6 W3D models**: `SOVTSLATNK` / `SOVTSLATNK_D` (hull + damaged) and the
  four wheel sub-meshes `SOVRADARJMR_W01/_W01D/_W02/_W02D` (the donor draws
  the tank as a treaded hull with visible wheels).
- **13 textures**: the 12 W3D-internal skins missing from the effective space
  (`18_v_treads`, `HousecolorRA(_d)`, `SovTnkWhl(_d)`, `barrels01`,
  `tankhatch(_d)`, `v_so_ttf_1(_d)`, `wheel2(_d)`) + the cameo
  `TeslaTankCameo.tga`. Textures already present in the effective space
  (`exteslaflare`, `reflect3`, `rep_glow`, `atsilverroof02*`,
  `lightbeamdiffuse` — shipped earlier by tesla-coil) are **referenced in
  place**, never re-shipped. Every model, every W3D-internal texture and the
  cameo are presence-asserted at build time against `effective ∪ archive`.

### Stats (donor → ours, deviations documented)

| Stat | Donor `SovietTankTeslaTank` | Ours | Why |
|---|---|---|---|
| Object | `SovietTankTeslaTank` | `Tank_ChinaTeslaTank` | Kwai `Tank_` family naming |
| Side | Soviet | **ChinaTankGeneral** | re-sided to Kwai |
| Cost | $1000 | **$1400** | Kwai medium-tesla specialist (sits at the Buratino tier on WF page 2) |
| Build time | 30 s | **30 s** | kept |
| HP | 600 | **720** | +20% China-tank convention (china-tank-buff) |
| Prereq | SovietTechCenter + `SCIENCE_SovietTeslaTank` | **Tank_ChinaWarFactory + Tank_ChinaPropagandaCenter** | WF page-2 roster convention; science gate dropped (Kwai can't buy it — Hammer Cannon precedent) |
| Veterancy | `ExperienceRequired 0 3500 4500 5500` (unreachable) | **`0 200 300 600`** | Battlemaster tiers so heroic is actually reachable; `IsTrainable = Yes` kept |
| Weapon | `TeslaTankWeapon` (80 dmg ×2 clip / 9 s / range 200) | **retuned** (see below) | tesla-family doctrine |
| Locomotor | `TeslaTankLocomotor` (FOUR_WHEELS, speed 40) | **kept** (shipped) | medium-tank mobility |
| Armor | `TankArmor` + `UpgradedTankArmor` (PLAYER_UPGRADE) | **`TankArmor` only** | the upgraded set was gated by the dropped RA `Upgrade_AdvancedTankArmor`; its `ArmorUpgrade` module + `UpgradeCameo1` dropped |
| Death | `OCL_TeslaTankDeathEffect` (RA `DeadTeslaTankHulk` + Mammoth debris) + `FX_GenericTankDeathExplosion` | **`OCL_ChinaTankBattleMasterTGDebris` + `FX_BattleMasterExplosionOneFinal`** | avoids porting the donor hulk object/model; reuses the China tank death (resolves in effective data) |
| Stealth | `StealthUpdate` gap-generator (stealth when idle) | **dropped** | the spec unit is a straightforward medium tesla tank; stealth-when-idle is an unrequested wrinkle |
| Voices | `SovietVehicleVoice*` / `MCVMoveLoop01` | **`BattleMasterTankVoice*` / `BattleMasterTankMoveStart`** | RA audio not in our space (chaos-units remap precedent) |
| Command set | `GenericCommandSet` | **kept** (attack-move / guard / stop) | standard combat vehicle |
| Cameo | `RATeslaTank` | **kept** (bundled) | the donor's own tesla-themed cameo (spec: reuse a tesla-themed one) |

### The weapon — tesla doctrine (strong vs vehicles, chain vs infantry, no AA)

`TeslaTankWeapon` (deviations from the donor's 80-dmg gun documented inline):

- **PrimaryDamage 80 → 120**, `PARTICLE_BEAM`, `ClipSize 2 / ClipReloadTime
  4000` → **~55 dps vs vehicles** (TankArmor 100% → 240/burst) = *strong vs
  vehicles*; **one-shots infantry** (HumanArmor takes PARTICLE_BEAM at 150% →
  180/bolt).
- **SecondaryDamage 60 @ radius 25** (donor had none) = the **chain arc** to
  nearby infantry (the tesla family's radius-arc approximation of chain
  lightning). `RadiusDamageAffects` loses **ALLIES** (donor had it) so arcs
  never fry our own troops.
- **NO ANTI-AIR** (`AntiAirborne* = No`, asserted) — family doctrine.
- `LaserName = TeslaBoltRandom`, `FireSound = TeslaCoilWeapon` — the shared
  family visual + sound (see Task 2).
- **`TeslaTankWeaponHeroic`** (150 / 80 @ 30) on a `WeaponSet Conditions =
  HERO` — the engine flips `WEAPONSET_HERO` at heroic rank (family parity with
  the Tesla Coil).

---

## Task 2 — Tesla FX harmonization (+ the masking finding)

### What was harmonized (at the level we can actually affect)

Every tesla-flavored weapon in the Kwai roster now shares:

- **Fire sound** `TeslaCoilWeapon` (the RA tesla zap, tesla-coil layer) —
  Tesla Coil, Tesla Tank, Shock Trooper gun **and** the Shock Trooper chain
  zaps all already used it; asserted as a family-coherence closure check
  (7 weapons: `Tank_TeslaCoilWeapon(+Heroic)`, `ShockTrooperTeslaWeapon`,
  `ShockTrooperTeslaChainZap(+Heroic)`, `TeslaTankWeapon(+Heroic)`).
- **Bolt visual** `TeslaBoltRandom` (the tesla-coil family's random 1-of-4
  jagged `EXLightningBolt` beam, carrying `TeslaBoltSparks*` muzzle/impact
  particles). The Tesla Coil and Tesla Tank use it via `LaserName`. **The
  Shock Trooper's chain zaps were repointed** from their private
  `TeslaTrooperLaserBeam` / `HeroicTeslaTrooperLaserBeam` bolts to
  `TeslaBoltRandom` — so the whole family now arcs with the *same* lightning
  bolt. (This is a `Weapon.ini` edit — two `LaserName` lines — audited as
  exactly two changed lines. The old beam objects stay defined but unused.)

The Shock Trooper's **damage types are deliberately NOT changed** (its
`EXPLOSION` warhead + `SUBDUAL` stun are a balance design owned by the
rotr-infantry session; harmonization is FX/sound coherence, not rebalancing).
The "Shmel" is a thermobaric FLAME rocket unit — **not** a tesla weapon — so
it is correctly excluded.

### ⚠ The masking finding (documented, NOT fixed — another session owns it)

`zzzz_FXEnhance.big` ships **full copies of `ParticleSystem.ini` (2.5 MB) and
`FXList.ini` (409 KB)** and **sorts above every `zzz-*` layer** (in a `-mod`
dir later-alphabetical wins). So **fx-enhance is the effective owner of those
two files, and any edit a lower layer makes to them is masked.** Concretely,
its baked `ParticleSystem.ini`:

- **contains** `TeslaBoltSparks` / `TeslaBoltSparks03` (the Tesla Coil sparks
  — baked in), so the coil/tank bolt particles render; **but**
- is **missing** `TeslaTrooperFlare` and `ShockTrooperTeslaBlast` (the Shock
  Trooper's tesla-bolt trail + electric-blast particle systems, shipped by
  the later-built `zzz-ZZZZZZZRotrInfantry.big`), and its `FXList.ini` is
  missing `FX_ShockTrooperElectricRocketExplosion`.

**Consequence:** the Shock Trooper's projectile trail and detonation-burst
FX are currently **masked/absent in-game** (the engine silently skips missing
attached particle systems / FXLists — `ParticleSys.cpp:2063 if (tmp)`). This
is the "tesla lightning masked by a layer-ordering problem" the task refers
to. Because fx-enhance is owned by a separate FX session, **this layer does
not touch it** — and deliberately does **no** `ParticleSystem.ini` /
`FXList.ini` edits itself (they would be masked too). Our harmonization is
therefore done purely at the `Weapon.ini` / object level, which fx-enhance
does not own.

**Recommended fix (for the fx-enhance session):** re-run
`fx-enhance/build.py --allow-layer-conflict` **after** rotr-infantry landed —
its own README already notes it must be rebuilt after any FX-bearing layer
(ChaosUnits/KwaiInfantry/TeslaCoil, and now RotrInfantry). That single rebuild
would re-bake the Shock Trooper particles into fx-enhance's copies and restore
(and, with our weapon-level bolt unification, fully harmonize) the Shock
Trooper's tesla FX. The chain-zap bolt harmonization we shipped is **not**
masked and takes effect immediately.

---

## Task 3 — Overlord removed from the roster

The Kwai roster has a **separate plain Overlord** distinct from the Emperor
(so this is the "remove it" case, not the "skip" case):

- **Plain Overlord**: build button `Tank_Command_ConstructChinaTankOverlord`
  → object **`Tank_ChinaTankOverlord`** (vanilla Overlord stub, cameo
  `SNOverlord`), at **War Factory page-2 slot 4** (from kwai-roster). This is
  the **only** slot referencing it (count = 1 across the whole CommandSet).
- **Emperor** (do NOT touch): build button
  `Tank_Command_ConstructChinaTankEmperor` → object **`Tank_ChinaTankEmperor`**
  (carries the entire defense suite / bunker / crew work), at **WF page-1 slot
  6** — a *different* set, button, object and cameo.

**Action:** WF page-2 slot 4 is rewritten from the Overlord button to the new
`Tank_Command_ConstructChinaTeslaTank` (the Tesla Tank replaces the Overlord
in its exact slot). The `Tank_ChinaTankOverlord` **object is left dormant**
(defined, no build button — as specified). Proof (asserted on installed
bytes): slot 4 = Tesla Tank; the Overlord button appears in **no** command
set; the Overlord object still exists; the Emperor construct button + object +
full module list (`HelixContain`, `PropagandaTowerBehavior`, `Shtora`,
`ModuleTag_EDS_PDL01/ABM01/Shield01/Shield02/Fleet01`, grenadier `GP_Crew01`)
survive byte-for-byte (Emperor.ini owner unchanged = `EmperorDefense` — this
layer never opens it).

---

## Files in the archive (26)

| File | Effective source (owner) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZZZZZZ0EmperorDefense.big` | WF page-2 slot 4: Overlord → Tesla Tank (1 line swapped, nothing else) |
| `Data\INI\CommandButton.ini` | EmperorDefense | +1 construct button (`Tank_Command_ConstructChinaTeslaTank`, cameo `RATeslaTank`) |
| `Data\INI\Weapon.ini` | EmperorDefense | 2 chain-zap `LaserName` lines → `TeslaBoltRandom` (harmonize) + 2 tank weapons appended |
| `Data\Generals.str` | EmperorDefense | +3 entries (name / `&Tesla Tank` / tooltip), base bytes identical |
| `Data\INI\Locomotor.ini` | `zzz-ZZZZZZZRotrInfantry.big` | +1 (`TeslaTankLocomotor`, append-only) |
| `…\China\Tank\Vehicles\TeslaTank.ini` | **new file** | the Tesla Tank (donor draw fabric verbatim + documented Kwai edits) |
| `…\MappedImages\HandCreated\TeslaTankMappedImages.INI` | **new file** | `MappedImage RATeslaTank` |
| 6 W3D + 13 textures | **new (donor)** | bundled tesla-tank art |

New identifiers (all collision-checked against the whole effective INI/STR
space): `Tank_ChinaTeslaTank`, `Tank_Command_ConstructChinaTeslaTank`,
`TeslaTankWeapon`, `TeslaTankWeaponHeroic`, `TeslaTankLocomotor`,
`RATeslaTank`, and 3 string labels. **No new CommandSet** (the tank uses the
shared `GenericCommandSet`); **no new ParticleSystem/FXList/OCL/AudioEvent**
(all referenced pieces are the shared tesla family + base ShockWave, which
resolve — and, critically, we avoid the fx-enhance-masked files).

## Build-time verification (all enforced; build fails loudly otherwise)

- Sort position + effective ownership of all 5 sourced files (both dirs);
  fx-enhance / ControlBarPro sort after us and are asserted to claim **none**
  of our shipped paths (no masking of *our* content).
- Donor drift guards (tank object, weapon numbers, locomotor, cameo).
- **Exact diff audits**: `Weapon.ini` = exactly 2 `LaserName` lines changed +
  2 weapons appended; `CommandSet.ini` = exactly the slot-4 line swapped,
  everything else byte-identical; CommandButton/Generals.str/Locomotor
  append-only (`startswith(source)`); block-balance deltas per file.
- **Tesla-family coherence**: 7 tesla weapons share `TeslaCoilWeapon`; every
  beam-drawn tesla weapon uses `TeslaBoltRandom`; no `TeslaTrooperLaserBeam`
  active reference remains; tank weapons carry no anti-air, no allied arc.
- **Closure**: button → object → weapons → locomotor → cameo → strings all
  resolve; family bolt/sound, death OCL/FX, voices, armor, `GenericCommandSet`
  all resolve in effective data; every tank model + W3D-internal texture +
  cameo resolves in `effective ∪ archive`.
- **Prior-layer survival** (installed bytes): Emperor object + full module
  list intact; Overlord object dormant (not deleted); WF page-2 all 14 slots
  resolve to defined buttons; Emperor construct button still present.
- **Combined-stack closure** (independent audit over the real game view,
  including fx-enhance + ControlBarPro): all of the above re-verified.
- BIG round-trip byte-identity; both installed archives **md5-match**
  (`0aca8effa4e492c505f2381b62cb9f3f`); post-install effective-ownership audit
  in both dirs. **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (everything
sorting below this archive), donor content from `~/GeneralsX/donors/RARedux/`,
patches, verifies, writes `zzz-ZZZZZZZZZZZZZ0TeslaFinish.big` here and installs
to both mod dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is the **last INI layer**. If any lower layer is
rebuilt, rebuild this afterwards (it embeds full copies of CommandSet /
CommandButton / Weapon / Generals.str / Locomotor). Conversely, lower layers'
builds must not see this archive — delete it from both mod dirs first, rebuild
the lower chain, then rerun this build. `zzzz_FXEnhance.big` /
`zzz_ControlBarPro*` sort after us and are unaffected by our rebuilds (we ship
none of their paths).

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZZZZZZZ0TeslaFinish.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZZZZZZZ0TeslaFinish.big`

Uninstall: delete the archive from both directories. No other files touched.
(The Overlord returns to the roster only if you also rebuild/re-source the
kwai-roster chain; simply deleting this archive restores nothing else, since
the roster's slot-4 Overlord line lives in lower layers that this archive
masks — deleting us un-masks the original Overlord button.)

## Known limitations / risks

- **Shock Trooper projectile trail + detonation burst remain masked** by the
  stale `zzzz_FXEnhance.big` (see the masking finding) — the chain-bolt
  harmonization we shipped is unaffected, but the trooper's gun trail/blast
  only return after the fx-enhance session rebuilds. Not fixed here by design.
- The Tesla Tank is drawn as a **treaded hull with wheels** (donor
  `W3DTankTruckDraw` + `FOUR_WHEELS` locomotor) — donor-authentic; wheel
  models bundled.
- No anti-air by doctrine — pair with gattling/AA escorts.
- Reaching HERO rank (stronger bolt) is combat-earned; `ExperienceRequired`
  retuned to Battlemaster tiers so it is reachable.
- kwai-doctrine armor `MaxHealthUpgrade` tiers are **not** on the tank (they
  are per-object enumerated; the tank isn't in that list — same as the Tesla
  Coil). It stays 720 HP through armor research.
- Save games crossing an install/uninstall boundary may not load (new object
  type + a swapped command-set slot). Start fresh.
- AI never builds the Tesla Tank (no AI build-list changes); player-facing.
- **NOT verified in-game** (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX GeneralsMD engine
  source.
