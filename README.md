# Panzergrenadiers

*(a ShockWave overhaul)*

A personal overhaul of **C&C Generals: Zero Hour — ShockWave** centered on General Ta Hun Kwai
(China Tank), built and played natively on Apple Silicon via
[GeneralsX](https://github.com/fbraz3/GeneralsX). Kwai becomes a full combined-arms fortress
faction: tanks that carry infantry, artillery with escorts, self-repairing armed bases,
a research economy, surveillance drones, point-defense lasers, and an extended 8-rank
veterancy ladder running on a custom engine fork.

> Personal project. Nothing here is affiliated with or endorsed by EA. See
> [Credits & Asset Policy](#credits--asset-policy) before sharing anything.

## What it changes

### Kwai's army
- **Battlemaster** (660 HP, 198-range gun): coax machine gun, 4-slot fire-out infantry bay,
  purchasable propaganda tower ($500), purchasable point-defense laser ($500)
- **Emperor**: 10-man fire-out bunker bay, Shtora blinding APS (auto-triggers when hit),
  propaganda aura, gattling upgrade
- **Gattling tanks** (450 HP): 250 ground range / 462 AA, +20% damage, +10% ROF
- **New buildables**: JS-7 superheavy (spawns Veteran), China Command Tank (hero unit —
  veterancy aura, $25/s income, generals-abilities menu), Overlord (with Battle Bunker),
  Buratino, Hammer Cannon, Nuke Cannon (800 range), Inferno Cannon (350 range, 300 HP),
  450-vision Scout Car, Siege Soldier, MiG, MiG Bomber
- **War Factory & Dozer build menus paginated** (both-way arrows) to fit the roster

### Kwai's base
- **8 buildings garrisonable** (10 infantry, fire-out) with Evacuate buttons
- **Internet Center**: 30 hacker slots (garrisoned hackers earn +25%), 20,000 HP
- **Hackers**: $300, no Propaganda Center prerequisite; dozer-buildable **Hacker Bunker**
  (4 hackers keep earning inside) and **Tank Bunker** (SWR shipped the button unwired)
- **Research tree at the Propaganda Center** (sequential unlock ladders):
  Composite Armor I–IV (all vehicles + buildings), Infantry Conditioning I–IV,
  Tungsten Shells, Advanced Infantry Doctrine, Automated Repair Systems (1%/s self-heal),
  Base Armaments (defensive guns on 7 main buildings)
- **UAV Surveillance Program** (Internet Center): research once, deploy permanent
  recon/stealth-detection drones anywhere, 120s reload

### Global rules (SagePatch.ini, engine-level)
- **Veterancy, 4 ranks cranked**: Heroic = 215% dmg / 215% ROF / 247% HP / 150% range
- **Ranks 5–8** (custom engine): up to **400% HP / ~350% dmg / ~282% ROF / ~197% range**
  at Heroic V; XP thresholds auto-extrapolate (×1.75 per rank)
- **Garrisoned infantry fire at 175% range**
- **AI never builds superweapons** (build lists stripped; proven sufficient by parsing the
  binary AI scripts); AI still targets yours
- Ironside's Howitzer nerfed to 250 range

### Engine fork ([anderote/GeneralsX](https://github.com/anderote/GeneralsX), branch `feature/veterancy-8-levels`)
- **8 veterancy levels** with INI-configurable bonuses (`HealthBonus_Heroic2..5`,
  `WeaponBonus = HERO2..HERO5 ...`), backward-compatible XP parsing
- **`VeterancyBoost`** on `PointDefenseLaserUpdate`: interception range/cadence scale with rank
- **XP readout**: rank + XP progress drawn under the health bar on single selection
- **Rank insignia** lookups for levels 5-8 (data-optional; art ships in the insignia layer)
- **`RespawnAtBuildingDie`** ("Edge of Tomorrow"): upgrade-gated, rank-gated respawn at a
  friendly building with exact XP preserved (data wiring pending)
- **Crash diagnostics**: uncaught exceptions now report stage, logic frame, the exact
  object template + module being updated, exception type, and a throw-site backtrace
  (macOS stack dumps were empty stubs upstream — fixed)
- **Container-death crash family fixed at the root**: `destroyObject()` defers teardown,
  leaving dead riders in the contain list that get re-placed and dereferenced; guarded at
  the source (`removeFromContainViaIterator` on `isDestroyed()`) plus downstream null-guards,
  with a full call-tree audit
- **Command & Control batch**: combat stances (aggressive/guard/hold-fire, `DefaultUnitStance`
  per producer), multi-select buildings bulk-build, guard-a-moving-unit escort, BAR-style
  line/formation move (RMB drag) — each dispatched as a proper networked message
- **QoL batch**: `RequiredUpgrade` prereqs, vision scaling with veterancy, per-unit kill
  counters, single-unit stats panel, shift-click ×5 queueing, hackers-hack-anywhere
- **Engine batch 4**: multi-point waypoints (shift-click) + patrol loop, persistent vehicle
  wrecks (`WreckLifetimeScale`), drawable weapon tracers (`ExtraTracers`) — all
  determinism-safe (see [MULTIPLAYER_COMPATIBILITY.md](MULTIPLAYER_COMPATIBILITY.md))

### Graphics (engine branch `feature/graphics-quality` + `fx-enhance` layer)

All client-side/visual only — the deterministic 30 Hz sim (and thus replays/multiplayer
sync) is untouched.

- **Denser particle effects**: per-system render cap raised 512 → 2048; Very High detail
  particle budget raised 5,000 → 10,000 (**set Options → Detail → Very High** to get it)
- **Explosion overhaul** (`zzzz_FXEnhance.big`, generated by `fx-enhance/build.py`):
  every explosion-class FXList (detected by its screen-shake nugget) gains an orange
  **dynamic light pulse** that flashes the terrain (180 injected), and its particle
  systems get ×1.75 burst counts, ×1.25 sizes, and ×1.3 smoke lifetimes (434 systems) —
  floored so nothing ever drops below stock, capped to stay inside the render budget.
  A vanilla-game variant ships as `000_FXEnhanceZH.big` in the game dir.
- **Forced 16× anisotropic filtering** at the DXVK layer (`dxvk.conf`
  `d3d9.samplerAnisotropy = 16`) — sharper ground textures at grazing angles,
  overrides the in-game setting
- Phase 2 (planned): more simultaneous dynamic lights (4 → 8 per object), LDR bloom,
  heat-haze verification under DXVK, larger terrain atlas, client-only cosmetic debris

## What this integrates

The playable game is a five-deep integration stack, each level from a different source:

1. **Retail game data** (EA, user-supplied) — the copyrighted assets: models, sounds, maps
2. **GeneralsX engine** (open source) — native Apple Silicon binary; DirectX8 calls go
   through DXVK → Vulkan → MoltenVK → Metal. We run a **custom fork** with two features:
   8-level veterancy and rank-scaled point-defense lasers
3. **ShockWave 1.201 + SPE** (SWR Productions) — the base mod: 12 generals, ~100 new
   units, its own AI. Everything below modifies *this*
4. **This repo's 20+ layers** — the Panzer Mod itself: stat tuning, new mechanics,
   ported units (from Shockwave Chaos, ZHE, Rise of the Reds), invented research trees
5. **UI layer** (Control Bar Pro/HD) + **engine-config** (`SagePatch.ini`: veterancy
   curves, garrison bonuses, camera) + **user data** (maps, options)

The key integration mechanism is the engine's archive-priority rule: later-alphabetical
`.big` files override earlier ones *file-by-file* (whole files, not diffs). Each layer
carries complete modified copies of the files it changes, built by its `build.py` from
the *effective* copy beneath it — so layers compose without merge conflicts, at the cost
of strict rebuild ordering (documented per layer, enforced by asserts).

## Building & installing

> **Installing on a fresh Apple Silicon Mac from a copied working install?**
> See [SETUP.md](SETUP.md) — agent-friendly guide + `./setup-macos.sh`, no source build needed.

### 1. Build the engine (once, ~15 min first time)

```bash
# deps
brew install cmake ninja meson pkgconf ffmpeg glm sdl3
# LunarG Vulkan SDK from https://vulkan.lunarg.com/sdk/home#mac (NOT homebrew) -> ~/VulkanSDK/
git clone https://github.com/microsoft/vcpkg ~/vcpkg && ~/vcpkg/bootstrap-vcpkg.sh -disableMetrics

# engine fork — the unified branch has everything (veterancy-8 + graphics)
git clone https://github.com/anderote/GeneralsX ~/src/GeneralsX
cd ~/src/GeneralsX && git checkout feature/graphics-quality   # or feature/veterancy-8-levels
source ~/VulkanSDK/*/setup-env.sh
cmake --preset macos-vulkan
cmake --build build/macos-vulkan --target z_generals -j$(sysctl -n hw.logicalcpu)
./scripts/build/macos/deploy-macos-zh.sh    # installs binary + Vulkan runtime + run.sh
```

Game data prerequisite: your own retail Zero Hour (Steam app 2732960) merged into
`~/GeneralsX/GeneralsZH/` (DepotDownloader works headlessly on macOS; steamcmd does not).

### 2. Install ShockWave + this mod's layers

```bash
# ShockWave 1.201 from SWR's public server (see RESEARCH.md §E) -> ~/GeneralsX/mods/ShockWave/
# then copy every layer archive from this repo into the mod dir:
cp */zz*.big */zzz*.big ~/GeneralsX/mods/ShockWave/     # each layer dir holds its built .big
cp 340_ControlBarPro*.big ControlBarHD*.big ~/GeneralsX/GeneralsZH/   # UI (from their sources)
```

Or rebuild any layer from source: `cd <layer>/ && python3 build.py` — each builder
re-derives from the archives below it, verifies, and installs. **Rebuild order matters**:
rebuilding a layer requires rebuilding every layer above it that shares files (each
build.py fails loudly if the stack drifted — trust the asserts, read the layer README).

### 3. Engine config + launch

Apply the SagePatch.ini settings (veterancy curves etc. — documented above) in
`~/Library/Application Support/GeneralsX/GeneralsZH/`, then:

```bash
cd ~/GeneralsX/GeneralsZH && ./run.sh -fullscreen -xres <W> -yres <H> -forcefullviewport \
  -mod ~/GeneralsX/mods/ShockWave
```

## Applying this from scratch

On a fresh Apple Silicon Mac:

1. **Engine**: clone GeneralsX, check out the `feature/veterancy-8-levels` branch (in
   `~/Documents/software/generalsx-vet8` here), install deps (`brew install cmake ninja
   meson pkgconf ffmpeg glm sdl3` + LunarG Vulkan SDK + vcpkg with the pinned baseline),
   `cmake --preset macos-vulkan && cmake --build build/macos-vulkan --target z_generals`
2. **Game data**: copy retail Zero Hour (Steam depots) to `~/GeneralsX/GeneralsZH/`,
   run the repo's deploy script (`deploy-macos-zh.sh`) to install binary + Vulkan runtime
3. **ShockWave**: download from SWR's public server into `~/GeneralsX/mods/ShockWave/`
   (see RESEARCH.md §E for the scriptable method), optionally + SPE campaign overlay
   as `~/GeneralsX/mods/ShockWaveSPE/`
4. **This mod**: copy every `zz*`/`zzz*` archive from the layer directories into the mod
   folder(s); copy `340_ControlBarPro*.big` + `ControlBarHD*.big` into the game folder
5. **Engine config**: apply the `SagePatch.ini` documented above (veterancy curves,
   `WeaponBonus = GARRISONED RANGE 175%`) — **only on the fork engine**; stock engines
   crash on the rank 5–8 keys
6. **Launch**: `./run.sh -fullscreen -xres <W> -yres <H> -forcefullviewport -mod
   ~/GeneralsX/mods/ShockWaveSPE` (or the ShockWave.app launcher)

To rebuild any layer after changing it: run its `build.py`, then rebuild every layer
above it that shares files (each build fails loudly if you get this wrong).

## Requirements

1. **Game data**: retail C&C Generals: Zero Hour (Steam) in `~/GeneralsX/GeneralsZH/`
2. **Engine**: GeneralsX built from the `feature/veterancy-8-levels` fork branch
   (stock GeneralsX works for everything except ranks 5–8 and PDL scaling — but will
   **crash** on the rank 5–8 SagePatch.ini keys; remove them if running stock)
3. **ShockWave 1.201** in `~/GeneralsX/mods/ShockWave/` (+ optional SPE campaign overlay
   in `~/GeneralsX/mods/ShockWaveSPE/`)
4. This repo's `.big` layers copied into the mod folder(s)
5. `SagePatch.ini` settings applied in `~/Library/Application Support/GeneralsX/GeneralsZH/`

Launch: `./run.sh -fullscreen -xres 3440 -yres 1440 -forcefullviewport -mod ~/GeneralsX/mods/ShockWaveSPE`

## Architecture: layered override archives

The mod is 20+ `.big` archives whose **filenames encode load priority**. Inside a `-mod`
directory the engine gives *later-alphabetical* archives higher priority (each prepends;
confirmed in `ArchiveFileSystem.cpp`) — the reverse of the game dir. Load order:

```
!Shw*.big                    ShockWave 1.201 (SWR Productions)
zz_SPE_*.big                 ShockWave SPE campaign overlay
zzx_ChinaTankBuff            all 24 China tanks +20% HP / +10% range / +5% speed
zzy_MammothBunker            USA Mammoth 4-slot bay (HelixContain, shield-safe)
zzyy_ChinaBunkers            Battlemaster bays, Troop Crawler fire ports
zzyz_GattlingBuff            gattling damage/range/ROF/HP
zzyzy_NoAISuperweapons       AI build lists stripped of 15 superweapon structures
zzyzz_PropTowers             prop tower purchase on Battlemasters (ERA-exclusive on Kwai's)
zzyzzz_CoaxMG                coax MG (hitscan) on Battlemasters
zzyzzzz_StatTune             absolute stat targets (BM/gattling/artillery/IC/buildings)
zzyzzzzz_KwaiArtillery       Nuke + Inferno Cannon for Kwai (build stubs)
zzyzzzzzz_EmperorBunker      Emperor 10-slot bay
zzz-KwaiDoctrine             20-upgrade PropCenter tree, $300 hackers (50-set button matrix)
zzz-ZKwaiBunkers             dozer page 2, Tank Bunker, Hacker Bunker
zzz-ZZKwaiBaseTech           auto-repair + Base Armaments
zzz-ZZZKwaiGarrisons         garrisonable buildings
zzz-ZZZZChaosUnits           JS-7, Command Tank, Emperor Shtora (from Shockwave Chaos)
zzz-ZZZZZKwaiRoster          Overlord/Buratino/Hammer/ScoutCar/SiegeSoldier/MiGs (stubs)
zzz-ZZZZZZKwaiUAV            UAV surveillance program
zzz-ZZZZZZZKwaiPDL           $500 PDL pods on ~10 vehicle types (invisible-rider idiom)
zzz-ZZZZZZZLKwaiInfantry     Flame Trooper + Minigunner stubs; simple Sharpshooter
                             (Pathfinder clone — the 199-file ZHE port was purged)
zzz-ZZZZZZZRotrInfantry      Shmel Trooper + tesla Shock Trooper (ROTR port, side-branch merge)
zzz-ZZZZZZZTTeslaCoil        RA Redux Tesla Coil — first rank-earning base defense
zzz-ZZZZZZZVehicleKit        2-slot bays (gattlings/scout/artillery); coax MGs
zzz-ZZZZZZZVetInsignia       rank 5-8 insignia art (stars + chevrons)
zzz-ZZZZZZZWEconomy          China infantry 50% cost / 2x speed; 900-vision scouts;
                             UAV ungated on all 15 command centers; 30-slot queues
zzz-...ZZ Panzergrenadier     Panzergrenadier infantry (replaces Red Guard)
zzz-...Z0 GrenadierResearch   Industrial-Plant research: Panzergrenadiers / Waffen
                              Grenadiers / Emperor's Guard — battle tanks roll off pre-crewed
zzz-...Z1 DropLadder          three parachute drop powers (Grenadier / Panzergrenadier /
                              Panzer Waffen), crewed tank variants at set ranks
zzz-...ZZ0 EmperorDefense     Emperor hull PDL, ABM interceptor array, projected energy
                              shield, fleet-shield regen aura (War Factory page 2)
zzz-...ZZZ0 TeslaFinish       RA Redux Tesla Tank (bundled art); tesla-FX harmonization;
                              plain Overlord swapped out of the buildable roster
zzz-...ZZZZ0 ShellKwai        Kwai main-menu shellmap recast (123 placements → Kwai roster)
zzz_ControlBarPro*.big       Control Bar Pro UI (FAS & xezon)
zzzz_FXEnhance               explosion overhaul: light pulses + scaled particle systems
                             (composes the FX INIs of every layer below — see rebuild rule)
```

## Roadmap

**Shipped since the original roadmap:** grenadier research chain (Panzergrenadiers / Waffen
Grenadiers / Emperor's Guard — crewed vehicles off the production line, Tank Hunters renamed
Panzerjägers) · Panzergrenadier unit · the three-tier parachute drop ladder (up to 2 Emperors
+ 4 Battlemasters + escorts, all crewed, arriving at Heroic rank) · the QoL / Command & Control
engine batches (RequiredUpgrade, vision-scaling veterancy, kill counters, shift-click ×5,
hackers-hack-anywhere, stats panel, combat stances, multi-select build, guard-moving-unit,
line-move) · engine batch 4 (waypoints/patrol, persistent wrecks, weapon tracers) · the Emperor
defense suite (hull PDL, ABM interceptor array, projected energy shield, fleet-wide regen aura)
· tesla-family FX harmonization · RA Redux Tesla Tank · plain-Overlord removal · a Research
Overview reference ([RESEARCH_OVERVIEW.md](final-polish/RESEARCH_OVERVIEW.md)) · Kwai shellmap
recast · a full [multiplayer/replay determinism audit](MULTIPLAYER_COMPATIBILITY.md) (PASS).

**Still in the pipeline:** Edge of Tomorrow data wiring · a true in-game Research Overview
*panel* (needs a new `GUICommandType` + `.wnd` + engine callback — the doc is the pure-data
floor) · the waypoint drag-preview ghost line · the full crewed-Emperor/tesla shellmap
showcase (World Builder) · and the Research Directorate arc: a Research Lab generating research
points spent in a dedicated science-tab tree with permanent unlocks that survive building loss.

**Every layer embeds full copies of the files it modifies from the layers beneath it.**
Rebuild order therefore matters: rebuilding a lower layer requires rebuilding every layer
above it that shares files (each `<layer>/build.py` asserts ownership and fails loudly on
drift — trust the asserts). Some rebuilds require temporarily removing higher archives;
each README documents its own requirements. In particular `zzzz_FXEnhance` transforms the
*effective* `FXList.ini`/`ParticleSystem.ini` of the whole stack — rerun
`fx-enhance/build.py --allow-layer-conflict` after rebuilding, adding, or removing any
FX-bearing layer (currently ChaosUnits, KwaiInfantry, TeslaCoil).

## Repo layout

- `<layer-name>/` — one directory per layer: `build.py` (idempotent builder with
  verification asserts), `README.md` (design, risks, uninstall), the built `.big`
- `hotkey-addon/` — the shared tooling: `bigfile.py` (BIG read/write), `csf.py`
  (CSF string files), plus the vanilla hotkey-hints addon
- `donor-inis/` — extracted INI trees from donor mods (reference only, not shipped)
- `RESEARCH.md` — mod-ecosystem survey (compatibility, download automation, maps)
- `listbucket.py`, `manifests/` — GenLauncher registry tooling

## Credits & Asset Policy

Standing on many shoulders:

- **EA / EA Los Angeles** — Zero Hour and the 2003 engine (GPL source release, 2025)
- **[TheSuperHackers](https://github.com/TheSuperHackers/GeneralsGameCode)** — the
  community engine continuation GeneralsX builds on
- **[fbraz3 / GeneralsX](https://github.com/fbraz3/GeneralsX)** — the macOS/Linux
  native port that makes any of this possible
- **SWR Productions** — [ShockWave](https://www.moddb.com/mods/cc-shockwave)
- **Shockwave Chaos** team — JS-7, Command Tank, Shtora (ported content)
- **VectorIV / Zero Hour Enhanced** — Sharpshooter (ported content), coax MG design
- **FAS & xezon** — Control Bar Pro; **xezon** — Control Bar HD
- **SWR / GenLauncher community** — the public file infrastructure

**Attribution & takedown policy.** This repo includes built archives that contain data and
art derived from the mods credited above, distributed here as a non-commercial fan project
with attribution. Specific derived content: ShockWave INI data (SWR Productions) embedded in
every layer's override files; JS-7 / Command Tank / Shtora models and data (Shockwave Chaos);
the Sharpshooter unit — models, audio, design (Zero Hour Enhanced, VectorIV); Shmel & Shock
Trooper units (Rise of the Reds, SWR Productions — side branch); Tesla Coil (Red Alert Redux,
sgtmyers88); Minigunner/Flame Trooper/artillery and other cross-general units (ShockWave).
Engine patches are GPL, matching the EA source release and GeneralsX. Nothing here is sold or
claimed as original work. **If you are a rights holder of any included content and want it
removed, open an issue — it will be taken down promptly.**
