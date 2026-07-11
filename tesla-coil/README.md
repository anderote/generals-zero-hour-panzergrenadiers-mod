# Tesla Coil (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Ports the
**TESLA COIL base defense from Red Alert Redux** to **Kwai (China Tank
General)** as a dozer-buildable defense:

**`Tank_ChinaTeslaCoil`** — $1500 / 30 s, **dozer page 2 slot 9**
(kwai-bunkers page: 7 Tank Bunker, 8 Hacker Bunker, 9 was next free),
prereq **Propaganda Center**, 2400 HP, needs power, and **the structure
gains veterancy from kills** (heroic rank upgrades the bolt).

Output archive: **`zzz-ZZZZZZZTTeslaCoil.big`** (30 files, ~7.7 MB — INI +
3 W3D models + 15 textures + 3 WAVs; installed to both mod dirs).
Case-insensitively `zzz-zzzzzzzt…` sorts **after**
`zzz-ZZZZZZZLKwaiInfantry.big` (`t` > `l` at char 12; the infantry layer
owns every shared INI this layers on), **after** any `zzz-ZZZZZZZR*.big`
side branch (`t` > `r`, probe-asserted), **before**
`zzz-ZZZZZZZVetInsignia.big` (`t` < `v` — that layer ships only its own
insignia files, verified disjoint) and **before** `zzz_ControlBarPro*.big`
(`-` 0x2D < `_` 0x5F) — checked against the real directory listings, plus a
stronger invariant: **no archive sorting after ours contains any path we
ship**.

## Asset provenance / credits

Object design, INI data, W3D models, textures, cameo and sounds originate
from **C&C Red Alert Redux 1.0.5 by sgtmyers88** (and team), extracted from
the mod's public distribution (`CCRARDX_1_0_5.zip` →
`~/GeneralsX/donors/RARedux/` — kept extracted for the planned Tesla Tank
port; the build reads `00_CCRARDXINI/ART/AUDIO.big` directly and
drift-guards the donor blocks). **Personal use only — no redistribution;
all credit to sgtmyers88 / the CCRARDX team.**

## How the donor's tesla bolt works (now the TESLA-FAMILY reference)

The bolt is **not** a particle effect or projectile — it is the ZH
laser-object idiom with a randomized twist:

- `Weapon … LaserName = TeslaBoltRandom` + `LaserBoneName = WEAPONA01`
  spawns a beam object per shot from the coil's `WEAPONA01` bone to the
  victim.
- **`TeslaBoltRandom`** is a template with
  `BuildVariations = TeslaBolt1 TeslaBolt2 TeslaBolt3 TeslaBolt4` — the
  engine (`ThingFactory.cpp:315`) picks a **random variation per shot**, so
  every discharge is a differently-jagged bolt.
- Each `TeslaBoltN` is a `W3DLaserDraw` (Texture `EXLightningBoltN.tga`,
  45-wide single beam, white/200α) + `ClientUpdate = LaserUpdate` with
  muzzle/impact spark systems + `DeletionUpdate` 60–90 ms — a bolt is a
  short-lived textured lightning streak, three per burst 30 ms apart.
- The **charge-up** is `DeployStyleAIUpdate` on the structure: the turret
  only functions "deployed" (1.5 s pack/unpack) and the deploy loop plays
  **`TeslaCoilCharge`** (`tslachg2.wav` — the iconic RA charge whine);
  the firing sound `TeslaCoilWeapon` (`tesla1.wav`) loops across the
  3-bolt clip. A 500 ms `PreAttackDelay PER_ATTACK` on the weapon adds the
  final crackle-pause before discharge.
- Each shot also fires `FireOCL` → a 5 s invisible **vision object at the
  impact point** (donor `OCL_BaseDefenseVisionObject`, ported as
  `OCL_TeslaCoilVision`/`TeslaCoilVisionObject`) so the coil can see what
  it is zapping at the edge of its 320 range (its own shroud clear is 300).

### Family template names (Shock Trooper / Tesla Tank: REFERENCE these, do not redefine)

| Piece | Name (defined by this archive) |
|---|---|
| Bolt visual | `LaserName = TeslaBoltRandom` (variants `TeslaBolt1..4`) |
| Muzzle sparks | `TeslaBoltSparks` |
| Impact sparks | `TeslaBoltSparks03` (slave `TeslaBoltSparks03Flare`) |
| Fire sound | `AudioEvent TeslaCoilWeapon` (tesla1.wav) |
| Charge sound | `AudioEvent TeslaCoilCharge` (tslachg2.wav) |
| Select sound | `AudioEvent TeslaCoilSelect` (powerselect.wav) |

(The donor's spark systems were `LiveWireSparks`/`03`/`03Flare` — renamed
because **vanilla ZH already defines a different `LiveWireSparks`**; the
03/Flare names were renamed with it for family unity.)

## Stats vs donor (deviations documented)

| Stat | Donor (`SovietTeslaCoil`) | Ours | Why |
|---|---|---|---|
| Cost | $1500 | **$1500** | top of the spec range; sits above the $1000 Gattling Cannon, well under superweapons |
| Build time | 55 s | **30 s** | our defenses build fast (Gattling Cannon 20 s) |
| HP | 1200 (+subdual cap 1200) | **2400** (+cap 2400) | stack 2x-building convention (Gattling Cannon 2000) |
| Prereq | SovietBarracks + SovietTechCenter | **Tank_ChinaPropagandaCenter** | spec tech gate |
| Range | 320 | **320** | donor already ≥ our 225 Gattling Cannon — no bump needed (spec asked for ≥200/~220) |
| Bolt damage | 230 PARTICLE_BEAM ×3-bolt clip / 8 s | **140 ×3 / 8 s** (HERO rank: **190**) | tesla-family doctrine, see below |
| Splash | radius 1.0, hits ALLIES | **Secondary 90 @ radius 25** (HERO: 120 @ 30), **ALLIES removed** | chain-arc feel without friendly fire |
| Anti-air | No | **No** (re-asserted) | family doctrine: coils cannot target air |
| Power | EnergyProduction −3, KindOf POWERED | **same** | see power behavior |
| Victory flag | MP_COUNT_FOR_VICTORY | **dropped** | Gattling Cannon parity; a lone coil must not keep a player alive (chaos-units precedent) |
| Veterancy | ExperienceValue 200×4 only | **+ `IsTrainable = Yes`, `ExperienceRequired = 0 80 200 300`** | see veterancy |
| ExperienceValue | 200 200 200 200 | same | equals our Gattling Cannon |

### Tesla-family damage doctrine (why 230 → 140)

Armor math in our effective `Armor.ini`: **HumanArmor takes PARTICLE_BEAM
at 150%**, TankArmor at 100%, StructureArmor at 200%.

- **Devastating vs infantry**: 140 → **210 per bolt** — one-shots every
  infantry in the stack (RedGuard 120 HP … Sharpshooter 190 HP). With
  3 bolts per burst retargeting as victims die, a burst can delete up to
  3 infantry, and the 90-damage arc (**135 post-armor**) kills clumped
  RedGuards around each impact.
- **Moderate vs vehicles**: 420 per burst every ~8.5 s vs the 660 HP
  Battlemaster (donor's 690 one-bursted it — that read as devastating,
  violating the family profile).
- **No anti-air**: `AntiAirborneVehicle/Infantry = No` asserted on both
  weapons at build time.

### Veterancy (structure ranks up from kills)

Vanilla/stack defenses carry `ExperienceValue` but never rank up — no
vanilla base defense is trainable, so the "mirror a precedent" idea was
replaced by engine-source verification: `ExperienceTracker.cpp:176` gates
`addExperiencePoints` on **`IsTrainable`**, and kills credit the killer's
tracker (`Object.cpp:3565`). The coil gets `IsTrainable = Yes` +
`ExperienceRequired = 0 80 200 300` (the tiers our `Tank_ChinaTankGattling`
uses), so SagePatch/global veterancy bonuses apply automatically. At
**heroic** rank the engine flips `WEAPONSET_HERO` (`Object.cpp:3187-3211`)
and the coil's second `WeaponSet Conditions = HERO` swaps in
`Tank_TeslaCoilWeaponHeroic` (190 dmg, 120 @ 30 arc) — the
GattlingTankGunHeroic pattern (113 `Conditions = HERO` precedents
in-stack). True chain-jumping (bolt hopping target-to-target) has no
engine support; the radius arc + heroic wider arc is the feasible
approximation — **documented as the family's "chain" mechanic**.

### Power behavior

Donor semantics kept: `EnergyProduction = -3` (same drain as our Gattling
Cannon) + `KindOf … POWERED`. During low power the coil is
`DISABLED_UNDERPOWERED` — turret stops, no firing, and the charge
animation halts (`AnimationsRequirePower = Yes`). Note this differs from
the kwai-basetech Base Armaments guns, which fire through low power (their
README documents that); the coil is deliberately the classic RA "coils die
with the grid" piece.

## Files in the archive (30)

INI/STR (9):

| File | Effective owner it patches | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | zzz-ZZZZZZZLKwaiInfantry | dozer page-2 slot 9 inserted + 1 set appended (`Tank_ChinaTeslaCoilCommandSet`: 12 Stop / 14 Sell — Gattling idiom minus the mines button, the coil has no minefield modules) |
| `Data\INI\CommandButton.ini` | zzz-ZZZZZZZLKwaiInfantry | +1 construct button (`Tank_Command_ConstructChinaTeslaCoil`, cameo `RATeslaCoil`) |
| `Data\Generals.str` | zzz-ZZZZZZZLKwaiInfantry | +3 entries (name / `&Tesla Coil` / tooltip), base bytes identical |
| `Data\INI\Weapon.ini` | zzz-ZZZZZZZLKwaiInfantry | +2 weapons (base + heroic bolt) |
| `Data\INI\ParticleSystem.ini` | zzz-ZZZZZZZLKwaiInfantry | +3 systems (`TeslaBoltSparks*`) |
| `Data\INI\ObjectCreationList.ini` | zzz-ZZZZZZZLKwaiInfantry | +1 OCL (impact vision) |
| `Data\INI\SoundEffects.ini` | zzz-ZZZZZZZLKwaiInfantry | +3 AudioEvents (donor-verbatim) |
| `…\China\Tank\Defences\TeslaCoil.ini` | **new file** | the coil (donor draw fabric verbatim: day/night/snow × damage × firing states, `SOVTESLACOIL/_D/_B` buildup, CTMound02 construction fence) + `TeslaBoltRandom` + `TeslaBolt1..4` + `TeslaCoilVisionObject` |
| `…\MappedImages\HandCreated\TeslaCoilMappedImages.INI` | **new file** | `MappedImage RATeslaCoil` |

Art (18): `SOVTESLACOIL.W3D`, `SOVTESLACOIL_D.W3D`, `SOVTESLACOIL_B.W3D`
+ 14 textures (coil skins/damage skins, `exlightningbolt1..4`,
`exteslaflare`, `exteslarctb`, `greyscale` buildup sheet,
`TeslaCoilCameo.tga`) — only assets missing from the local effective space
(base ZH + ShockWave + all sibling layers) are shipped; `CTMound02`,
`EXFuzzyDot`, `exlnzflar3`, `atsilverroof02` etc. already resolve locally.

Audio (3): `tesla1.wav`, `tslachg2.wav`, `powerselect.wav` at
`Data\Audio\Sounds\` (donor paths).

Donor modules dropped (RA Redux-only infrastructure, documented in the
shipped file header): Soviet crew ejection on death
(`OCL_SovietInfantryEjection01` — its OCL closure was not ported), the EVA
"construction complete" announcer weapon, and the construction-yard
build-radius decal weapon. Everything else the coil references
(`OCL_ABPowerPlantExplode`, `FX_SmallStructureDeath`, `BaseDefenseArmor`,
`StructureDamageFXNoShake`, `UnderConstructionLoop`,
`BuildingDamagedStateLight/Destroy`, all draw-fabric particle systems)
already exists in the effective space — asserted at build time.

## Build-time verification (all enforced; build fails loudly otherwise)

- Ownership asserted for all 7 shared files (owner
  `zzz-ZZZZZZZLKwaiInfantry.big` — the infantry layer landed mid-port and
  was re-sourced, per the sibling package-time rule); new INI/art/audio
  paths asserted unclaimed in every archive of both dirs; 22 new
  identifiers collision-checked against 897 effective INI files
  (this caught vanilla's `LiveWireSparks` → renamed).
- Donor drift guards on every extracted block (weapon numbers, coil
  modules, bolt beam width, sound sample names, cameo texture).
- Diff audits: 6 append-only files assert `startswith(source)`;
  CommandSet.ini asserts exactly 1 inserted slot-9 line + 1 appended set;
  coil block-balance vs donor (−3 dropped modules, +1 weapon set);
  block-balance deltas on every shared file.
- Closure: construct button→object→command set→weapons→bolt objects→
  particles→OCL→vision object→strings→cameo→armor→sounds→prereq; art
  closure incl. **W3D-internal texture scan** of the 3 shipped models;
  audio events → shipped wav files; doctrine asserts (no `AntiAirborne* =
  Yes`, no ALLIES in arc damage, POWERED present, no
  `MP_COUNT_FOR_VICTORY`, no Soviet/RA leftovers in non-comment text).
- Sibling survival re-asserted on shipped **and installed** bytes:
  kwai-bunkers dozer pages + hacker bunker, kwai-infantry barracks 5–8,
  chaos/roster WF pages, kwai-artillery WF 11–12, kwai-pdl's 17 buttons +
  Emperor 9/10, doctrine's 50 propaganda-center sets, kwai-uav IC sets,
  sibling strings/weapons.
- Sort position vs the real listings + the disjointness invariant (no
  later-sorting archive claims our paths — covers the concurrently landed
  `zzz-ZZZZZZZVetInsignia.big`); installed archives re-read and
  byte-compared; rebuild is hash-idempotent.
  **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding its
own archive), donor content from `~/GeneralsX/donors/RARedux/`
(`00_CCRARDXINI.big` / `00_CCRARDXART.big` / `00_CCRARDXAUDIO.big` — keep
that directory; the repo carries no donor bytes), patches, verifies, writes
`zzz-ZZZZZZZTTeslaCoil.big` here and installs to both mod dirs. Depends on
`../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this archive embeds full copies of
kwai-infantry-owned files. If **any** lower INI layer is rebuilt
(kwai-infantry, kwai-pdl, kwai-uav, kwai-roster, chaos-units,
kwai-garrisons, kwai-basetech, kwai-bunkers, kwai-doctrine, …), rebuild
this archive afterwards. Conversely, lower layers' own builds must not see
this archive — delete `zzz-ZZZZZZZTTeslaCoil.big` from both mod dirs first,
rebuild the lower chain in its documented order, then rerun this build.
(`zzz-ZZZZZZZVetInsignia.big` is disjoint and order-independent.)

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZTTeslaCoil.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZTTeslaCoil.big`

## Uninstall

Delete `zzz-ZZZZZZZTTeslaCoil.big` from both directories above. No other
files are touched. (`~/GeneralsX/donors/RARedux/` is only needed to
rebuild — and for the future Tesla Tank port.)

## Known limitations / risks

- **Save games**: a new object type + shared-file layering — saves crossing
  an install/uninstall boundary may not load. Start fresh.
- **Low power turns the coil off completely** (deliberate, donor/RA
  semantics). Kwai's power math matters: coil + Gattling Cannon each drain
  3.
- The doctrine Composite Armor `MaxHealthUpgrade` tiers are **not** on the
  coil (they are owned per-object by kwai-doctrine's enumeration) — the
  coil stays 2400 HP through armor research. Future work: a doctrine
  rebuild that enumerates the coil, then this layer re-sources it.
- True target-hopping chain lightning has no engine support; the "arc" is
  radius splash (90 @ 25 / heroic 120 @ 30) — reads well on infantry
  blobs, invisible on lone targets.
- `DeployStyleAIUpdate` charge-up means the first bolt of an engagement
  arrives ~2 s after acquisition (1.5 s unpack + 0.5 s pre-attack). It
  re-centers/undeploys after idling — the charge whine on
  deploy/undeploy/turret-move is authentic but frequent in busy bases.
- The bolts' `DisplayName = OBJECT:Laser` is a missing string label even in
  vanilla (never displayed; INERT system objects) — donor/vanilla parity.
- Veteran structures draw rank chevrons; with `zzz-ZZZZZZZVetInsignia.big`
  installed they use that layer's art. The coil earning HERO rank is slow
  by design (300 XP at 8 s per 3-kill burst).
- AI never builds the coil (no AI build-list changes); player-facing only.
- The select sound (`powerselect.wav`) is a UI-typed event at volume 50 —
  quiet by donor design.
- NOT verified in-game (deliberately not launched); all verification is
  static against the engine source (GeneralsX GeneralsMD tree) and the
  installed bytes.
