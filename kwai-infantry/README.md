# Kwai Infantry (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. THREE new
Barracks infantry for **Kwai (China Tank General)** — two ShockWave
cross-general build stubs plus one **full cross-mod port from Zero Hour
Enhanced (ZHE)**.

Output archive: **`zzz-ZZZZZZZLKwaiInfantry.big`** (199 files, ~29.6 MB —
INI/STR + all Sharpshooter art and audio). Case-insensitively
`zzz-zzzzzzzl…` sorts **after** `zzz-ZZZZZZZKwaiPDL.big` (`k` < `l` at
char 11; PDL owns CommandSet/CommandButton/Upgrade/OCL/Weapon/Generals.str
this layers on), **before** any future `zzz-ZZZZZZZR*.big` (`l` < `r`,
probe-asserted) and **before** `zzz_ControlBarPro*.big` (`-` 0x2D < `_`
0x5F) — verified against the real directory listings of both mod dirs at
build time. This is now the **last INI layer**.

## The roster (Barracks, both set variants)

| Slot | Unit | Object | Builds / port | Cost / time | Prerequisites |
|---|---|---|---|---|---|
| 6 | **Flame Trooper** | `Tank_ChinaInfantryFlameThrower` | stub → `Spec_ChinaInfantryFlameThrower` (Leang) | $350 / 8 s | Tank_ Barracks + Tank_ War Factory (donor: Spec_ Barracks + Spec_ WF, translated) |
| 7 | **Minigunner** | `Tank_ChinaInfantryMiniGunner` | stub → `Infa_ChinaInfantryMiniGunner` (Fai — donor object name verified in `China\Infantry\Infantry\MiniGunner.ini`) | $550 / 14 s | Tank_ Barracks (donor: Infa_ Barracks, translated) |
| 8 | **Sharpshooter** | `Tank_ChinaInfantrySharpshooter` | **FULL PORT** of ZHE's `ChinaInfantrySharpshooter` | $1200 / 30 s (donor cost) | Tank_ Barracks + Tank_ Propaganda Center (spec; ZHE donor needed only ChinaBarracks — **documented deviation**) |

Barracks occupancy verified before placement: roster's Siege Soldier holds
slot 5; slots 6–11 were free in both `Tank_ChinaBarracksCommandSet` and
`…Upgrade`; 6–8 now used, **9–11 remain free**; 12–14 (capture research /
mines / sell) untouched.

Stubs follow the kwai-artillery / kwai-roster `BuildVariations` idiom
(donor-mirrored KindOf, donor default model on the stub draw, donor
art + CSF labels on the cloned construct buttons — no new strings or
textures for the two stubs).

### Stub stat notes

- **Flame Trooper** is Leang's stock unit. Its White Napalm weapon tier
  (`Upgrade_ChinaWhiteNapalm`) is Leang-only research — Kwai's copy fires
  the base flame weapon forever (inert hook, kwai-roster Buratino
  precedent).
- **Minigunner** is Fai's stock unit and **does** benefit from two
  upgrades Kwai can actually research: **Chain Guns** (weapon tier —
  Kwai buys it at his Propaganda Center since kwai-artillery) and
  **Capture Building** (`Upgrade_InfantryCaptureBuilding`, the same
  player upgrade Kwai's Redguard button researches).

## The Sharpshooter port (ZHE → our stack)

Donor: **Zero Hour Enhanced** local archives at
`~/GeneralsX/mods/Enhanced/ZHE_BIG100a/` — INI from `!ZHE8INI_99.big`,
strings from `!ZHE8Language_99.big`, W3D from `!ZHE8W3D_9x.big` +
`!ZHE8IUI_97.big`, textures from `!ZHE9Textures_9x.big`, cameo pages from
`!ZHE8CameoSD_99.zhe` (SD set), audio from `!ZHE8Audio_98/99.big`.
**Personal use only — all credit to the Zero Hour Enhanced authors.**

A $1200 stealthy China sniper with ZHE's full feature set, shipped
donor-stat-exact (nothing capped):

- **Type 79 sniper rifle**: 60 SNIPER damage / 2.5 s (2.25 s proned),
  300 range, 10-round clip, tracer + distant-report sound layers,
  heroic-tier FX.
- **Prone system** (ZHE's generic rider-switch infra,
  `RiderChangeContain` + 4 invisible rider objects): Prone button →
  sluggish crawl, steadier fire; Stand button returns. Incoming
  suppression (MICROWAVE chip damage, e.g. near-miss grenades via ZHE's
  suppression pulses) auto-forces him prone.
- **Innate stealth** while not firing (detectors: he also carries ZHE's
  five-band `StealthDetectorUpdate` suite — structures/vehicles/aircraft/
  drones/infantry at short range).
- **Type 86 grenade** (secondary, 30 s clip) and, after the per-unit
  **$300 Type 66 Claymore OBJECT upgrade** (slot 5 on the unit), a
  claymore **AP-mine-laying mode** instead (proximity demo-trap mine with
  radius + dual-cone detonation weapons).
- **Area Reconnaissance** (tertiary): binocular sweep that plants
  invisible 100-vision shroud-clearing detector markers.
- **Capture Building** — ZHE gives its sniper capture by default (30 s
  recharge, no research gate). Ported as-is: **the Sharpshooter can
  capture without Kwai's capture-upgrade research** (documented donor
  behavior; Redguards/Minigunners still need the research).
- **4 build variations** (`ObjectReskin` skins NIMRKMN01–04) and ZHE's
  **wounded-body mechanic**: ~20–33 % of non-violent deaths leave a
  wounded body for 20–30 s. ZHE's Field Medic (not in our stack) could
  revive it (EXTRA_3 death → revive OCL); without one it simply expires —
  the revive path ships for closure and points at our renamed stub.
- Nationalism horde bonus applies (upgrade cameo 1);
  `Upgrade_ChinaRevolutionaryHeroism` (armor tier) is ported for closure
  but **unresearchable in our stack** — inert hook.

### What was ported vs reused (closure trace: `work/portset.py`)

**Ported verbatim under donor names** (all word-boundary collision-checked
against the whole 891-file effective INI space — zero collisions, ZHE and
ShockWave never overlap here): **176 INI blocks** —

- 15 sharpshooter-family objects (stub + 4 variations + wounded/proned-
  wounded families) → `…\China\Tank\Infantry\Sharpshooter.ini` (full copy
  of ZHE's file; only the stub block edited),
- 16 generic support objects (GenericBullet + water checkers, generic/
  grenade projectiles, `DummyInvisibleGroundCollider`,
  `UpgradeViaRiderSwitch1–4` riders, recon marker, suppression pulse,
  Type 86 grenade pair + float variant, Type 66 claymore) →
  `…\SharpshooterSupport.ini`,
- 20 weapons, 20 FX lists, 47 particle systems, 17 OCLs, 6 special powers,
  4 armors (`HumanArmor_Brave`, `WoundedHumanArmor`, `WaterCheckerArmor`,
  `UnsinkableProjectileArmor`), 3 locomotors (`SluggishHumanLocomotor`,
  `MidAirGrenadeLocomotor`, `CheckerContainerLocomotor`), 2 upgrades,
  10 command buttons, 4 command sets (appended to the effective owners'
  files),
- 9 MappedImages (cameos SNSharpshooter/_L, Type 66/Type 86 buttons,
  SSProneStealthed/SSStand/SSBinocular, SNRevolutionaryHeroism) →
  `Data\INI\MappedImages\HandCreated\KwaiInfantryMappedImages.INI`,
- 28 AudioEvents (11 Sharpshooter voice events → Voice.ini appendix; 17
  weapon/impact/footstep/UI events → SoundEffects.ini appendix, incl.
  `WeaponUpgrade`, `MeatBounce`, `Type79SniperRifle(+Distant)` — the
  mechanical rule ports every referenced event missing from our space),
- 18 `generals.str` entries (append-only to the PDL-owned file).

**Reused from our effective space** (verified defined): `HumanArmor`,
`InfantryDamageFX`, `EmptyDamageFX`, `InvulnerableArmor`, `MineArmor`,
`ProjectileArmor`, `BasicHumanLocomotor`, `DummyWeapon`, `FX_RedGuardDie`,
`FX_DieByFireChina`, `FX_DieByToxinChina`, `OCL_FlamingInfantry`,
`OCL_ToxicInfantry(+Beta/Gamma)`, `InfantryDustTrails`, `InfantryCrush`,
`SSCaptureBuilding` mapped image, `Command_AttackMove/Guard/
GuardWithoutPursuit/Stop` (slots 15–18), `Upgrade_Nationalism`,
`ChinaBarracks` (variation prereq), gradio radio click samples, and 9
particle textures already present (EXBlood, EXContrail, EXExplo03/04,
EXLnzFlar2–4, EXShockWav, EXSmokNew2, EXWater05).

**Renames / edits inside ported text** (everything else byte-identical):

1. `Object ChinaInfantrySharpshooter` → `Tank_ChinaInfantrySharpshooter`
   (buildable stub only), `Side = China` → `ChinaTankGeneral`, prereqs
   `ChinaBarracks` → `Tank_ChinaBarracks` + `Tank_ChinaPropagandaCenter`.
2. `OCL_ChinaInfantrySharpshooter_Revived` repointed at the renamed stub.
3. MappedImage `Texture =` lines repointed at the **renamed cameo pages**
   (see Art below).
4. `Type79SniperRifleDistant`: ZHE's sample typo `kar98-l-3` fixed to
   `kar98-l-03` (the file that actually exists — in ZHE it was silently
   missing).

### Art (80 files)

47 W3D (NIMRKMN01–04 skins, CISPINF skeleton + 35 animations, Type 86 /
Type 66 models, EXInfSnp/EXInfSnpAP/EXWounded/EXIndGnd/EXIndAPMine
housecolor indicators) + 29 textures (3 skin sheets, 7 W3D-internal
indicator textures, 19 particle textures missing from our space) — all at
their original internal paths, none present in (or colliding with) base
ZH + ShockWave + sibling layers (asserted).

**Cameo pages re-shipped under new names**: ShockWave ships its own,
*different* `SNNUserInterface512_004.tga` / `SNSUserInterface512_002.tga`
pages, so ZHE's pages could not be shipped under their original names.
The four needed **512×512 SD pages** (from `!ZHE8CameoSD_99.zhe` — the HD
set is 1024² and does not match the TextureSize_512 coordinate space) ship
as `KwaiZheSNN512_004/005/006.tga` / `KwaiZheSNS512_002.tga`, with the 9
ported MappedImage blocks repointed. No ShockWave art is overridden.

### Audio (101 samples + 28 events) / remaps

- ZHE's complete Sharpshooter **voice set is real and shipped** (44
  `ishp*.wav` files) — no remap to base China infantry was needed. ZHE
  stores voices under `Data\Audio\Sounds\English\`; they ship here at the
  **unlocalized** `Data\Audio\Sounds\` path so the engine's
  localized-first/unlocalized-fallback lookup finds them under any
  language setting (documented deviation).
- 57 more wavs for the ported weapon/impact/footstep/water/UI events
  (kar98 rifle reports, tracers, grenade toss/explosion, bullet/water
  impacts, footsteps, sloshes, `wweaupgr` upgrade jingle, …).
- Radio-click attack/decay samples (`gradio1a–f`, `gradio3a–e`) already
  exist in the base game and are reused, as is every sample already
  present in our space (per-sample checked; only missing ones ship).

## Files in the archive (199)

| Group | Files | Based on (effective owner) |
|---|---|---|
| `Data\INI\CommandSet.ini` | Barracks 6–8 inserted (both variants, +3 lines each, zero removed) + 4 ZHE sets appended | `zzz-ZZZZZZZKwaiPDL.big` |
| `Data\INI\CommandButton.ini` | +3 construct buttons + 10 ZHE buttons | `zzz-ZZZZZZZKwaiPDL.big` |
| `Data\INI\Upgrade.ini` / `ObjectCreationList.ini` / `Weapon.ini` | +2 / +17 / +20 blocks | `zzz-ZZZZZZZKwaiPDL.big` |
| `Data\Generals.str` | +18 ZHE entries (base bytes identical) | `zzz-ZZZZZZZKwaiPDL.big` |
| `Data\INI\Armor.ini` / `Locomotor.ini` / `FXList.ini` / `ParticleSystem.ini` | +4 / +3 / +20 / +47 blocks | `zzz-ZZZZChaosUnits.big` |
| `Data\INI\SpecialPower.ini` | +6 powers | `zzz-ZZZZZZKwaiUAV.big` |
| `Data\INI\Voice.ini` / `SoundEffects.ini` | +11 / +17 AudioEvents | `zz_SPE_Shw_ini.big` |
| `…\China\Tank\Infantry\FlameTrooper.ini` / `MiniGunner.ini` | **new files** — the stubs | — |
| `…\China\Tank\Infantry\Sharpshooter.ini` / `SharpshooterSupport.ini` | **new files** — 15 + 16 ported objects | — |
| `Data\INI\MappedImages\HandCreated\KwaiInfantryMappedImages.INI` | **new file** — 9 mapped images | — |
| `Art\W3D\*` (47), `Art\Textures\*` (33), `Data\Audio\Sounds\*.wav` (101) | ZHE assets (only what our space lacks) | — |

All 13 patched files are **append-only** except CommandSet.ini
(+6 insertion lines, 0 removed — exact line-diff asserted).

## Build-time verification (all enforced; build fails loudly otherwise)

- Ownership asserted for all 13 patched + 3 donor files; 5 new INI paths
  asserted unclaimed; 6 new identifiers **and all 176+ ported donor
  names** word-boundary collision-checked against the whole effective INI
  space.
- Donor drift guards: flame trooper $350/8 s + Spec_ prereqs, minigunner
  $550/14 s + Infa_ prereq, ZHE stub $1200/30 s re-parsed each build.
- Diff audits: CommandSet exact +55/-0 line multiset; every appended file
  asserts `startswith(base)`; block-balance (col-0 `End` count == block
  count) per new file; expected new-block counts per patched file.
- Closure on the shipped text: every Object/Weapon/Armor/Locomotor/FX/
  OCL/SpecialPower/CommandSet/Upgrade/ParticleSystem reference, every
  command-set slot, the rider-switch chain, every string label, every
  MappedImage, every Model/Animation W3D, every W3D-internal texture,
  every ParticleName texture, every AudioEvent and **every audio sample**
  resolves in effective data + this archive. Engine-side, every ported
  module type and unusual INI field was verified against the GeneralsX
  GeneralsMD parse tables (RiderChangeContain, DemoTrapUpdate,
  rider/status fields, PreAttackType, ExemptStatus, …).
- Sibling survival on shipped **and installed** bytes: PDL's 17 slot-9
  buttons + 7 exclusivity/state sets, roster Barracks 5 / WF page 2
  (4–7 used, 8–11 free) / Airfield 3–4 + 5 exit cameos, UAV Internet
  Center sets (research 7 / deploy 8 / Evacuate 9) + vanilla IC sets,
  doctrine/garrisons' 50 full prop-center sets, artillery WF page 1
  (Inferno 11 / page-down 12), mammoth-bunker transport stems ×5,
  kwai-bunkers dozer pages + Hacker Bunker, basetech power-plant sets,
  emperor-bunker Emperor set (gattling 10 / Evacuate 12), proptower ERA
  set, garrisons ≥60 Evacuates, vanilla China prop center untouched.
- Sort position vs the real listings of both mod dirs (incl. a
  `zzz-ZZZZZZZR*` probe); installed archives re-read and byte-compared;
  independent post-install audit recomputed the whole effective space in
  both dirs (ownership + content of all 199 files, Barracks sets, single
  definition of each new object, roster SiegeSoldier.ini still
  roster-owned); rebuild is idempotent (hash-stable).
  **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive) and donor data from `~/GeneralsX/mods/Enhanced/
ZHE_BIG100a`, patches, verifies, writes `zzz-ZZZZZZZLKwaiInfantry.big`
here and installs to both mod dirs. Depends on
`../hotkey-addon/bigfile.py` and `../chaos-units/work/iniblocks.py`.
`work/` holds the closure-tracing tooling (`portset.py`, `trace.py`,
`dump.py`, `extract.py`) and reference extractions.

**Rebuild-order note**: this is now the **last INI layer** (after
kwai-pdl). If any lower layer is rebuilt (kwai-pdl, kwai-uav,
kwai-roster, chaos-units, kwai-garrisons, kwai-basetech, kwai-bunkers,
kwai-doctrine, emperor-bunker, kwai-artillery, stat-tune, …), rebuild this
archive afterwards — it embeds full copies of their files. Conversely,
lower layers' builds must not see this archive: delete
`zzz-ZZZZZZZLKwaiInfantry.big` from both mod dirs first, rebuild the lower
chain in its documented order (… → kwai-uav → kwai-pdl), then rerun this
build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZLKwaiInfantry.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZLKwaiInfantry.big`

## Uninstall

Delete `zzz-ZZZZZZZLKwaiInfantry.big` from both directories above. No
other files are touched.

## Notes / accepted limitations / balance

- **No Emperor changes, no bay changes** in this layer (PDL's Emperor
  state stands, per spec).
- Sharpshooter balance is **donor-exact ZHE** dropped into ShockWave:
  60 SNIPER/2.5 s at 300 range one-shots nothing but chews infantry;
  SNIPER-vs-armor behavior follows *our* armor tables (ZHE's armors were
  not imported for existing units). Innate stealth + default capture
  (no research gate, unlike our Redguards) is deliberately strong for
  $1200 — donor behavior, documented.
- The prone/AP-mine buttons occupy unit-command slots 1–5; ZHE's slots
  15–18 (attack-move/guard/stop) are kept for donor parity but
  ControlBarPro renders only 14 button windows — those commands remain
  available via standard hotkeys.
- MICROWAVE chip damage (< the sniper's death threshold, e.g. USA
  Microwave Tank beams or ZHE-style suppression) auto-forces the sniper
  prone — that is the ported suppression feature working as designed.
- Wounded bodies grant kill XP to the enemy and expire in 20–30 s (no
  medic exists in our stack to revive them). The revived-spawn path is
  shipped but effectively dead code.
- The claymore upgrade is per-unit ($300 OBJECT upgrade via the unit's
  own `ProductionUpdate`), irreversible, and swaps the grenade away
  (donor design). Mines are DEMOTRAP-class: stealthy, proximity-fired,
  cleared by dozers/overbuild.
- Flame Trooper / Minigunner are stock donor units (see stub stat notes);
  the stubs add no AI build-list entries — **AI never builds any of the
  three** (player-only, prior-art convention).
- Save games crossing an install/uninstall boundary may not load (new
  object types + modules appended to shared INIs). Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX engine source.

## Asset provenance / credits

Sharpshooter design, INI data, models, textures, voices and sounds
originate from **Zero Hour Enhanced** (ZHE team); extracted from the
mod's local distribution archives listed above. Flame Trooper /
Minigunner remain **C&C ShockWave** (SWR Productions) donor units
referenced in place. **Personal use only — all credit to the ZHE authors
and SWR Productions.**
