# Kwai Artillery (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave running under GeneralsX.
China's **Tank General (Ta Hun Kwai)** can build vanilla China's two
artillery units from his War Factory:

- **Inferno Cannon** (slot 11, $900, requires War Factory + Propaganda Center)
- **Nuke Cannon** (slot 12, $1600, requires War Factory + Propaganda Center)

Both are the stock vanilla-China units (`ChinaVehicleInfernoCannon`,
`ChinaVehicleNukeLauncher` — ShockWave's internal name for the Nuke Cannon)
with unchanged stats. Player-only: nothing is added to AI build lists.

## What it is

`zzyzzzzz_KwaiArtillery.big` — a BIG archive with four files:

| File in archive | Based on (effective copy) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzyzz_PropTowers.big` | 4 blocks touched (see below) |
| `Data\INI\CommandButton.ini` | `zz_SPE_Shw_ini.big` | 2 new buttons appended after the Tank Hacker Van button |
| `Data\INI\Object\China\Tank\Vehicles\InfernoCannon.ini` | new file | build stub `Tank_ChinaVehicleInfernoCannon` |
| `Data\INI\Object\China\Tank\Vehicles\NukeCannon.ini` | new file | build stub `Tank_ChinaVehicleNukeLauncher` |

The `zzyzzzzz_` prefix sorts after every other addon layer
(`zzyzzzz_StatTune`) and before the ControlBarPro archives (`zzz_`), so its
copies of CommandSet.ini / CommandButton.ini win at load time
(later-alphabetical wins). Both are based on the previously-effective copies,
so all sibling-mod hunks (Mammoth bunker slots, Battlemaster transport
exits, prop-tower upgrade button, ERA command set) survive — verified by
`build.py`.

## How it works (ShockWave's own idiom)

ShockWave gives generals cross-faction units via minimal "build stub"
objects: a stub with the right `Side`, `Prerequisites`, `BuildCost/BuildTime`
and `BuildVariations = <vanilla object>`. The factory queues the stub but the
`BuildVariations` redirect spawns the real vanilla unit. Kwai already uses
this for `Tank_ChinaVehicleHackerVan`, `Tank_ChinaVehicleListeningOutpost`,
`Tank_ChinaSpeakerTower`, etc. — the two new stubs copy that pattern exactly,
with prerequisites translated to Kwai's buildings
(`Tank_ChinaWarFactory` + `Tank_ChinaPropagandaCenter`, mirroring the vanilla
units' `ChinaWarFactory` + `ChinaPropagandaCenter`).

New object INIs under `Data\INI\Object\` are auto-loaded by the engine
(recursive directory scan, archives included), so no existing object file is
touched.

The two command buttons (`Tank_Command_ConstructChinaVehicleInfernoCannon`,
`Tank_Command_ConstructChinaVehicleNukeLauncher`) clone the vanilla construct
buttons and reuse their art (`SNInferno`, `SNNukeCannon`) and CSF labels —
no new strings or textures needed.

## Command-set slot decision

The engine's `MAX_COMMANDS_PER_SET` is 18, but slots above 14 are
script-only: ShockWave's `ControlBar.wnd` and ControlBarPro's both define
exactly 14 `ButtonCommand` windows, so slots 15+ never display. Kwai's War
Factory sets were full (10 units, 3 upgrades, Sell at 14). Room was made by
relocating the two **player-wide** upgrades — Chain Guns and Black Napalm —
from War Factory slots 11-12 to Kwai's **Propaganda Center** slots 4-5
(previously empty; that building already researches Nationalism /
Subliminal Messaging / Neutron Bomb via its ProductionUpdate, and both moved
upgrades are `PLAYER_UPGRADE`, so they research identically from there).
The per-building Mines upgrade (slot 13, `OBJECT_UPGRADE`) and Sell (14)
stay where they were. Net effect: same upgrades available, you just buy
Chain Guns / Black Napalm at the Propaganda Center now — which you need for
the artillery anyway.

Both command-set variants are patched (`Tank_ChinaWarFactoryCommandSet` +
`...Upgrade`, `Tank_ChinaPropagandaCenterCommandSet` + `...Upgrade`).

## How it was built

```
python3 build.py
```

Reads the effective source files from `~/GeneralsX/mods/ShockWaveSPE/`,
applies block-scoped edits (asserting each hunk lands exactly once and the
full diff matches the intended 12 CommandSet lines + 20 added CommandButton
lines), verifies prior-layer hunk survival and archive sort order, writes
`zzyzzzzz_KwaiArtillery.big` here, installs to both mod dirs, and re-reads
the installed archives to confirm byte-identical content.

`extracted/` holds reference copies of the source files pulled from the
archives during development.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzyzzzzz_KwaiArtillery.big`
- `~/GeneralsX/mods/ShockWave/zzyzzzzz_KwaiArtillery.big`

## Uninstall

Delete `zzyzzzzz_KwaiArtillery.big` from both directories above. No other
files are touched.

## Notes / accepted limitations

- **Science gate dropped for the Nuke Cannon.** Vanilla China's Nuke Cannon
  additionally requires `SCIENCE_NukeLauncher` (a general's-point promotion)
  — but Kwai's promotion tree cannot purchase that science
  (`Tank_SCIENCE_CHINA_CommandSetRank1/3/8` don't offer it), so carrying it
  over would make the unit permanently unbuildable. ShockWave's own
  precedent is followed instead: the Nuke General's variant
  (`Nuke_ChinaVehicleNukeLauncher`) requires only his War Factory +
  Propaganda Center, no science. Kwai gets the same gating.
- Vanilla artillery gains starting veterancy from
  `SCIENCE_ArtilleryTraining`; Kwai can't purchase that either, so his
  artillery starts unranked. Harmless.
- The built units are stock vanilla China artillery: they do **not** get
  Kwai's tank-flavor bonuses (horde/subliminal tank interactions) beyond
  whatever player upgrades (e.g. Nationalism, Black Napalm for the Inferno
  Cannon) naturally apply. Intentional.
- Nuke Cannon Neutron Shells: the vanilla unit's upgrade cameo references
  `Upgrade_ChinaNeutronShells`, which Kwai cannot research — the unit simply
  fires standard nuke shells.
- AI never builds these (no AIData/build-list changes).
