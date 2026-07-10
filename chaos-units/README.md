# Chaos Units (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Ports
**three systems from the *ShockWave Chaos* mod** to Kwai (China Tank
General):

| # | What | Cost / time | Prereqs | HP |
|---|---|---|---|---|
| 1 | **Emperor Shtora APS retrofit** — auto-firing blinding countermeasures on our existing `Tank_ChinaTankEmperor` | — (built-in) | — | unchanged (1320) |
| 2 | **JS-7 / IS-7** superheavy tank (`Tank_ChinaTankJS7`), war-factory page 2 | $1800 / 30 s | War Factory + Propaganda Center | **1140** (Chaos 950, +20% stack convention) |
| 3 | **China Command Tank** (`Tank_ChinaTankCommandTank`), hero mobile command center, war-factory page 2 | $2500 / 15 s | War Factory + Command Center | **1560** (Chaos 1300, +20%) |

Output archive: **`zzz-ZZZZChaosUnits.big`** (44 files, ~10.5 MB — INI +
all needed art in one archive; installed to both mod dirs).
Case-insensitively `zzz-zzzz…` sorts **after** `zzz-ZZZKwaiGarrisons.big`
(whose CommandSet.ini / Generals.str / WarFactory.ini it layers on) and
`-` (0x2D) < `_` (0x5F) sorts it **before** `zzz_ControlBarPro*.big` —
verified against the real directory listings at build time. This is now
the **last INI layer**.

## The war-factory second page (dozer page-flip idiom, both directions)

Kwai's war factory had all 14 UI slots in use (10 units, kwai-artillery
at 11–12, kwai-garrisons Evacuate at 13, Sell at 14). Exactly like
kwai-bunkers did for the dozer:

- **Page 1** (both set variants, base + EMP-mines `…Upgrade`): slots
  1–11, 13 (Evacuate), 14 (Sell) unchanged; **slot 12** (Nuke Cannon,
  kwai-artillery) → **page-down arrow**
  (`Command_ChinaButtonCommandSetOneDown`).
- **Page 2** (`Tank_ChinaWarFactoryCommandSet_Down`, new):
  **1 Nuke Cannon** (relocated) · **2 JS-7** · **3 Command Tank** ·
  **12 page-up arrow** · 13 Evacuate · 14 Sell.
  **Slots 4–11 are deliberately left free and contiguous** for the
  planned follow-up layer (Overlord, Buratino, Hammer Cannon, Scout
  Car).

Arrows in **both** directions are wired: two `CommandSetUpgrade`
modules on `Tank_ChinaWarFactory` (`ModuleTag_CU_Page01/02`) keyed to
the engine-wide page tokens `Upgrade_GLAWorkerFakeCommandSet` /
`…RealCommandSet` with `RemovesUpgrades` cross-clearing, so the pages
flip forever — field-for-field the kwai-bunkers dozer idiom.

**Factory queue semantics (differs from the dozer, engine-verified):**
the dozer got a private `MaxQueueEntries=1` queue; the WF already has a
real production queue (`ProductionUpdate ModuleTag_12`, untouched).
`ProductionUpdate::queueUpgrade` appends upgrades to the **end** of the
queue and an entry only completes at the queue **head**
(`ProductionUpdate.cpp`: only the first entry is processed per frame;
a 0-cost/0-time upgrade then completes instantly). So the page flip is
instant and free while the factory is idle, but **a flip issued while
units are building waits behind them** (it shows in the queue and can
be cancelled). This is inherent to putting pages on a producing
factory; documented rather than fought.

Interplay with the WF's own EMP-mines set flip (`ModuleTag_25`,
untouched): if EMP Mines research completes the WF snaps to page 1
(the `…Upgrade` variant). Harmless — since kwai-garrisons replaced the
mines buttons, the base and Upgrade variants are content-identical, and
the page-up arrow's static target (base variant) shows the same
buttons.

## 1. Emperor Shtora APS

Grafted from Chaos's AI-Emperor/Golem (donor `Emperor.ini`
`ModuleTag_1338` + `ModuleTag_Shtora01..03`), inserted as **pure
insertion** into our effective Emperor (the doctrine-owned copy, which
already carries the emperor-bunker HelixContain bay):

- `FireWeaponWhenDamagedBehavior ModuleTag_ShtoraAuto01`: any single
  hit dealing **≥ 30 post-armor damage** fires
  `GolemTankShtoraAIWeapon` (0 damage, `FireOCL`), **30 s cooldown**
  (this engine checks `READY_TO_FIRE` before firing —
  `FireWeaponWhenDamagedBehavior.cpp:197` — so the donor's "AI fires
  without cooldown" comment does not apply here).
  **Engine finding:** reaction weapons are per-body-state; the donor
  wired only the DAMAGED slot, which would disarm the APS exactly in
  red state — `ReactionWeaponReallyDamaged` is additionally wired to
  the same weapon (documented deviation; the two state slots hold
  separate 30 s clocks, so crossing into red can grant one extra
  activation). **No auto-fire while pristine** (green) — donor
  semantics.
- The OCL spawns Chaos's two-object system: a 1 s **grenade launcher**
  object that lobs 2 blinding grenades (flash + spark FX, flashbang
  sound, zero damage) and an 8 s invisible **defence object** slaved to
  the tank that pulses a `STATUS MASKED` weapon every 66 ms —
  **the Emperor becomes untargetable for ~8 s** while remaining under
  player control.
- The donor's manual-ability trio (`OCLSpecialPower` /
  `FireWeaponCollide` / `MissileLauncherBuildingUpdate` on
  `SpecialAbilityRussianShtora`) is ported for fidelity but has **no
  command button on the Emperor** (its set is full at 14 since
  emperor-bunker); the modules are inert without one. The JS-7 carries
  the manual button instead.
- Preserved and re-asserted on shipped bytes: HelixContain 10-seat bay
  (`ModuleTag_06`), propaganda tower (`ModulePropaganda_15`), gattling
  upgrade chain (`ModuleTag_07`), doctrine armor tiers
  (`ModuleTag_KD_Armor1..4`, `ModuleTag_KD_Tungsten01`), china-tank-buff
  1320 HP, and the emperor-bunker command set (exits 2–9, gattling 10,
  Evacuate 12).

## 2. JS-7 (IS-7)

Chaos donor object verbatim except documented edits:

- 130 mm gun `JS7TankGun` (250/150 dmg, range 250, 8 s reload; 7 s
  `…Upgraded` via Kwai's Autoloader `WeaponSetUpgrade`), hull MG +
  AA MG (`GolemHeavyMachineGunGun/…Air`), melee anti-infantry splash
  OCL. Weapons stock per spec.
- **Spawns as VETERAN** (`VeterancyGainCreate`, donor design), armor
  hardens further with `Upgrade_TankLightArmor` (ERA skirts +
  `LolGitGudFuckerPlayMoreIS7` armor set — donor name kept), benefits
  from Uranium Shells / Nuclear Tanks / Nationalism / Autoloader
  (all pre-existing here).
- **Manual Shtora button** (slot 1 of its donor
  `RussianTankGolemCommandSet`) — same countermeasure system as the
  Emperor's, on a 30 s power timer.
- HP 950 → **1140** (+20% convention). Prereq changed per spec to
  War Factory + Propaganda Center (**Chaos used Industrial Plant +
  Propaganda Center** — deviation documented).
- **CARBOMB weapon-sets dropped** (they exist for Chaos's leech
  infection mechanic, whose closure was not ported; our stack's China
  tanks carry no CARBOMB sets either). Hijacker eject behaviors kept.
- Voice/sounds: Chaos's Soviet T26 voice samples and Golem gun sounds
  are not in any obtainable archive (`!ChaosArt.big` has no audio), so
  they are **remapped to base ShockWave events** (documented in the
  Weapon.ini appendix): Emperor/Overlord voice set, WarMasterTankFire
  cannon, HelixWeaponMachineGun MGs, TurretMoveLoop,
  ExplosionFlashBang for the grenade pop, NoSound for the MG whistle.

## 3. China Command Tank

Chaos donor `Tank_ChinaTankCommandTank` (the Tank-general variant from
`China/Vanilla/Vehicles/ChinaCommandTank.ini`) with documented edits:

- **Hero-style**: `MaxSimultaneousOfType = 1` (donor already set it;
  link-key `CommandTruck`), KindOf `HERO` + **`COMMANDCENTER` added
  per spec** (mirrors the donor's vanilla-China variant; owning the
  tank keeps the generals-powers shortcut bar alive without a command
  center).
- **APFSDS / HESH ammo switching**: two `SWITCH_WEAPON` buttons
  (donor): PRIMARY `Tank_ChinaCommandTankCannonAPFSDS` (600 dmg
  single-target sabot, LAND_MINE damage type = armor-piercing in
  ShockWave) ↔ SECONDARY `…HESH` (300/150 splash + vehicle-crew stun
  OCL). `ShareWeaponReloadTime`, `LockWeaponCreate` keeps PRIMARY
  locked at spawn.
- **Veterancy-crate dispensing**: `Command_ChinaCommandTankGrantVeterancy`
  (slot 10) fires `SuperweaponChinaCommandTankGrantVeterancy` (150 s,
  shared-synced, shortcut-capable) → drops an invisible 80-radius
  crate that grants **+1 veterancy level to armed units** (not dozers/
  drones) in the target area.
- **Two-page command set** (donor): main page ↔ "Generals Abilities"
  page via the same GLAWorker page tokens. The powers page hosts the
  shared-timer powers whose templates exist in our stack: Carpet Bomb,
  Tank Paradrop, Artillery Barrage, Emergency Repair, EMP Pulse (all
  gated by their sciences, timers shared with the Command Center).
  CashHack/Frenzy/CarpetBomb/etc. modules are also present for
  shortcut-bar use, matching the donor.
- Propaganda tower aura (heals nearby units, upgrades with Subliminal
  Messaging), $25/s `AutoDepositUpdate` trickle, death crates
  (Salvage/Elite/Heroic), nuclear-tanks death + speed upgrades,
  Battlemaster-black art (`NVBtMstrBl*`).
- HP 1300 → **1560** (+20%). Prereq per spec: War Factory + Command
  Center (**Chaos used Industrial Plant** — deviation documented).
- **Dropped donor modules** (their SpecialPower/OCL closures are
  Chaos-only and were not ported): Tesla-tank paradrop, V4 paradrop,
  global radar jammer, leech-infector drone, Sweet Tooth summon, and
  the invisible "is-a-structure" battle-drone pair (victory-condition
  side effects undesirable for an *additional* buildable). The
  build-button tooltip's "Counts as a structure" line was removed
  accordingly (only string edit).

## Files in the archive (44)

INI/STR (16) — full patched copies of the effective sources
(append-only unless noted):

| File | Effective owner it patches | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | zzz-ZZZKwaiGarrisons | 2 slot lines swapped (WF page-down, both variants) + 4 sets appended |
| `Data\INI\CommandButton.ini` | zzz-ZZKwaiBaseTech | +8 buttons |
| `Data\Generals.str` | zzz-ZZKwaiBaseTech | +16 Chaos entries (base bytes identical) |
| `Data\INI\Weapon.ini` | zzz-ZZKwaiBaseTech | +16 weapons |
| `Data\INI\Armor.ini` | zz_SPE_Shw_ini | +3 armors |
| `Data\INI\Locomotor.ini` | zzx_ChinaTankBuff | +5 locomotors |
| `Data\INI\FXList.ini` | zz_SPE_Shw_ini | +13 FX lists |
| `Data\INI\ParticleSystem.ini` | zz_SPE_Shw_ini | +7 particle systems |
| `Data\INI\ObjectCreationList.ini` | zz_SPE_Shw_ini | +8 OCLs |
| `Data\INI\SpecialPower.ini` | zz_SPE_Shw_ini | +2 special powers |
| `…\Tank\Vehicles\Emperor.ini` | zzz-KwaiDoctrine | +4 Shtora modules (pure insertion) |
| `…\Tank\Buildings\WarFactory.ini` | zzz-ZZZKwaiGarrisons | +2 page-flip modules (pure insertion) |
| `…\Tank\Vehicles\JS7.ini` | **new file** | the JS-7 |
| `…\Tank\Vehicles\CommandTank.ini` | **new file** | the Command Tank |
| `…\Tank\Vehicles\ChaosSupportObjects.ini` | **new file** | 12 support objects (projectiles, Shtora launcher/defence/grenade, hulks, veterancy crate) |
| `Data\INI\MappedImages\HandCreated\ChaosUnitsMappedImages.INI` | **new file** | SRIosif, SRIosif_L, SSGolemShtora |

Art (28): 11 W3D models (`RVIS7*`, `RVGolem_A1/A2`, `NVBtMstrBl*`) and
17 textures (JS-7 skins, Golem/T80 sheets, cameo sheets `RVIosif.tga` /
`SNRUserInterface512_003.tga`, particle textures, `exgolemtrack.dds`) —
only assets **missing** from the local effective space (base ZH +
ZH_Generals originals + ShockWave + all sibling layers) are shipped, at
their original internal paths.

**Asset closure**: every model/texture/particle/sound/string/identifier
referenced by the three units resolves in effective data + this archive
(verified by the build *and* an independent post-install audit).
Grandfathered by donor parity (missing from Chaos's **own** shipping
archives too, and harmless in-engine): `TracerCore.tga`, and the
`*TracerTrail*`/`*SparksTrail*` attached particle systems (the engine
skips missing attached systems — `ParticleSys.cpp:2063 if (tmp)`).

## Asset provenance / credits

Unit designs, INI data, models, textures and strings originate from
**C&C ShockWave** (SWR Productions) and the **ShockWave Chaos** addon
(Chaos team; moddb.com/mods/cc-shockwave-chaos). Extracted from the
mod's public distribution (`!ChaosArt.big`; 12 textures ranged-fetched
from `!ShwChaos !ShwTextures.big`; strings from its `!Shw_ini.big`,
which also byte-verified the local donor INI cache). **Personal use
only — all credit to SWR Productions and the ShockWave Chaos authors.**
Chaos's audio archive was not used; missing sounds are remapped to base
ShockWave events (see above).

## Build-time verification (all enforced; build fails loudly otherwise)

- Ownership asserted per patched file; new INI paths asserted unclaimed;
  all new identifiers collision-checked against the whole effective INI
  space; donor cache byte-verified against Chaos's `!Shw_ini.big` (15
  files, md5).
- Diff audits: append-only files assert `startswith(source)`;
  Emperor.ini / WarFactory.ini assert pure-insertion of exactly the new
  modules (line-multiset diff); CommandSet.ini asserts exactly 2
  swapped lines + the appendix; STR base bytes identical.
- Closure: every donor-defined identifier referenced by shipped text is
  defined in the final space; every powers-page button's SpecialPower
  has a matching module on the Command Tank; string labels, audio
  events, W3D-internal textures all resolve; block-balance and
  block-count checks per file.
- Sibling survival re-asserted on shipped and installed bytes:
  garrisons WF contain module + Evacuate (both pages/variants) +
  50 prop-center Evacuates, basetech heal/armaments hunks, doctrine's
  50 sets and Emperor armor tiers, emperor-bunker bay/set, artillery
  Inferno at 11 (Nuke relocated to page 2 slot 1 — **documented
  relocation**), kwai-bunkers dozer pages, power-plant sets.
- Archive sort position vs real listings; installed archives re-read
  and byte-compared. **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive), donor INIs from `../donor-inis/shw_base_ini`, art
from `donor-art/` (ChaosArt.big + `fetched/`), patches, verifies,
writes `zzz-ZZZZChaosUnits.big` and installs to both mod dirs. Depends
on `../hotkey-addon/bigfile.py` and `work/iniblocks.py`.

**Rebuild-order note**: this is now the **last INI layer**. If any
lower layer is rebuilt (kwai-garrisons, kwai-basetech, kwai-bunkers,
kwai-doctrine, emperor-bunker, kwai-artillery, stat-tune, …), rebuild
this archive afterwards — it embeds full copies of their files.
Conversely, lower layers' own builds must not see this archive: delete
`zzz-ZZZZChaosUnits.big` from both mod dirs first, rebuild the lower
chain in its documented order (…doctrine → bunkers → basetech →
garrisons), then rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZChaosUnits.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZChaosUnits.big`

Uninstall: delete the archive from both directories. No other files are
touched.

## Known limitations / risks

- **Save games**: the Emperor and War Factory gained modules and new
  object types exist — saves crossing an install/uninstall boundary may
  not load. Start fresh.
- WF page flips queue behind in-progress unit production (see above);
  flips are instant when the queue is idle. A multi-selected group of
  factories flips only those whose queue is clear.
- The Nuke Cannon build button moved to page 2 slot 1 — deliberate
  relocation; muscle memory may object.
- Emperor Shtora never auto-fires at full (green) health — it arms once
  the hull is in the yellow/red damage state and a hit deals ≥ 30
  post-armor damage; ~8 s untargetability per activation, 30 s cooldown
  per damage-state slot (crossing yellow→red can chain one extra
  activation). MASKED also drops the tank from enemy auto-acquire —
  strong vs single big hitters, weak vs chip damage (< 30 per hit never
  triggers it).
- The Shtora launcher flash briefly renders Golem launcher art at the
  hull (donor object shared with the JS-7, where it matches) — cosmetic.
- JS-7's Shtora is manual (button); Emperor's is automatic (no free
  button slot). The Shtora button sound was dropped (event undefined in
  Chaos itself).
- Command Tank: $25/s passive income, propaganda aura and shared-timer
  powers on one hero tank is deliberately strong (donor balance);
  its powers page buttons stay dark until the matching sciences are
  bought. As a COMMANDCENTER it may draw AI superweapon targeting
  priority (moot with the no-ai-superweapons layer).
- Chaos-authentic voices/gun sounds could not be shipped (audio archive
  out of scope); remaps listed above. The tracer lens-flare texture is
  missing in Chaos itself (renders untextured/blank — donor parity).
- AI never builds the new units (no AI scripting); player-facing only.
- NOT verified in-game (deliberately not launched); all verification is
  static against the engine source (GeneralsX GeneralsMD tree) and the
  installed bytes.
