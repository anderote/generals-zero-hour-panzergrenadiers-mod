# ShockWave Panzer Mod

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

### Engine fork (branch `feature/veterancy-8-levels` of GeneralsX)
- 8 veterancy levels with INI-configurable bonuses (`HealthBonus_Heroic2..5`,
  `WeaponBonus = HERO2..HERO5 ...`), backward-compatible XP parsing
- `VeterancyBoost = Yes` on `PointDefenseLaserUpdate`: interception range/cadence scale
  with the owner's rank

## What this integrates

The playable game is a five-deep integration stack, each level from a different source:

1. **Retail game data** (EA, user-supplied) — the copyrighted assets: models, sounds, maps
2. **GeneralsX engine** (open source) — native Apple Silicon binary; DirectX8 calls go
   through DXVK → Vulkan → MoltenVK → Metal. We run a **custom fork** with two features:
   8-level veterancy and rank-scaled point-defense lasers
3. **ShockWave 1.201 + SPE** (SWR Productions) — the base mod: 12 generals, ~100 new
   units, its own AI. Everything below modifies *this*
4. **This repo's ~18 layers** — the Panzer Mod itself: stat tuning, new mechanics,
   ported units (from Shockwave Chaos, ZHE, Rise of the Reds), invented research trees
5. **UI layer** (Control Bar Pro/HD) + **engine-config** (`SagePatch.ini`: veterancy
   curves, garrison bonuses, camera) + **user data** (maps, options)

The key integration mechanism is the engine's archive-priority rule: later-alphabetical
`.big` files override earlier ones *file-by-file* (whole files, not diffs). Each layer
carries complete modified copies of the files it changes, built by its `build.py` from
the *effective* copy beneath it — so layers compose without merge conflicts, at the cost
of strict rebuild ordering (documented per layer, enforced by asserts).

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

The mod is ~18 `.big` archives whose **filenames encode load priority**. Inside a `-mod`
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
zzz-ZZZZZZZKwaiPDL           $500 PDL pods on combat vehicles (in progress)
zzz_ControlBarPro*.big       Control Bar Pro UI (FAS & xezon)
```

**Every layer embeds full copies of the files it modifies from the layers beneath it.**
Rebuild order therefore matters: rebuilding a lower layer requires rebuilding every layer
above it that shares files (each `<layer>/build.py` asserts ownership and fails loudly on
drift — trust the asserts). Some rebuilds require temporarily removing higher archives;
each README documents its own requirements.

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

**⚠️ Do not publish the built `.big` archives publicly.** Several layers embed assets and
data extracted from the mods above (Chaos art, ZHE-derived content, ShockWave data copies
in every layer). That's fine for personal use; redistributing it requires those teams'
permission. If this repo goes public, strip the built archives and `donor-inis/` first —
the build scripts and documentation are the shareable part. The engine-fork patches
(veterancy-8, PDL scaling) are GPL like the engine and genuinely upstreamable.
