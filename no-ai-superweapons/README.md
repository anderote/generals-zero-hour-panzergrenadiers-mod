# No AI Superweapons — mini-mod for ShockWave (GeneralsX/macOS)

Stops the skirmish AI from ever **constructing** superweapon structures, for
all factions and all generals. Human players can still build and fire every
superweapon — nothing player-facing is touched.

Output archive: **`zzyzy_NoAISuperweapons.big`** — the name is deliberate:
inside a `-mod` directory, later-alphabetical archives take priority, so it
sorts after `zzyz_GattlingBuff.big` (and after the base `!Shw_*.big`
archives whose file it overrides) and before `zzyzz_PropTowers.big` /
`zzz_ControlBarPro*.big`.

Installed to both:

- `~/GeneralsX/mods/ShockWaveSPE/zzyzy_NoAISuperweapons.big`
- `~/GeneralsX/mods/ShockWave/zzyzy_NoAISuperweapons.big`

## How it works

The skirmish AI's base construction is driven entirely by the
`SkirmishBuildList <side>` blocks in `Data\INI\Default\AIData.ini`
(ShockWave ships it inside `!Shw_scripts.big`; identical file in both mod
dirs). Engine-verified chain (GeneralsX source):

- `AISkirmishPlayer::newMap()` copies the side's `SkirmishBuildList` from
  AIData into the player's build list — skirmish maps play no role.
- The AI's timed build scripts (`SkirmishScripts.scb`) order superweapons
  via the `SKIRMISH_BUILD_BUILDING` action, which calls
  `AISkirmishPlayer::buildSpecificAIBuilding()`. That function **only**
  queues entries already present in the build list; with no matching entry
  it logs a script-debug warning and does nothing.

So this mod ships one file — `Data\INI\Default\AIData.ini` with every
superweapon `Structure ... END` block commented out (20 blocks, 140 lines,
`;`-prefixed; nothing else changed). The build lists stay structurally
valid and every other structure keeps its position and rebuild settings.

## Removed build-list entries (per general)

| SkirmishBuildList | Structure removed | Count |
|---|---|---|
| America | AmericaParticleCannonUplink | 1 |
| AmericaAirForceGeneral | AirF_AmericaParticleCannonUplink | 1 |
| AmericaLaserGeneral | Lazr_AmericaParticleCannonUplink | 1 |
| AmericaSuperWeaponGeneral | SupW_AmericaParticleCannonUplink | 5 |
| AmericaArmorGeneral | Armor_AmericaParticleCannonUplink (Missile Silo) | 1 |
| China | ChinaNuclearMissileLauncher | 1 |
| ChinaInfantryGeneral | Infa_ChinaNuclearMissileLauncher | 1 |
| ChinaNukeGeneral | Nuke_ChinaNuclearMissileLauncher | 2 |
| ChinaTankGeneral | Tank_ChinaNuclearMissileLauncher | 1 |
| ChinaSpecialWeaponsGeneral | Spec_ChinaNuclearMissileLauncher (Temple of Gaia) | 1 |
| GLA | GLAScudStorm | 1 |
| GLADemolitionGeneral | Demo_GLAScudStorm | 1 |
| GLAStealthGeneral | Slth_GLAScudStorm | 1 |
| GLAToxinGeneral | Chem_GLAScudStorm | 1 |
| GLASalvageGeneral | Salv_GLABaikonurMissile (Soyuz/Baikonur) | 1 |

The superweapon set was enumerated from the object INIs by the engine's own
markers (`KindOf = ... FS_SUPERWEAPON` and
`MaxSimultaneousOfType = DeterminedBySuperweaponRestriction`). The
`GLAHoleScudStorm` rebuild-hole variants are never in build lists and need
no change. `Nuke_ChinaNuclearResearchPlant` is a tech building, not a
superweapon, and was left alone.

## The SkirmishScripts.scb caveat

`Data\Scripts\SkirmishScripts.scb` is binary and was **not** edited. It was
fully parsed (chunk format verified against GeneralsX `DataChunk.cpp` /
`Scripts.cpp`; see `tools/scb_scan.py`). Superweapon object names appear in
exactly two action kinds:

- `OBJECTLIST_ADDOBJECTTYPE` (225x) — builds the "Super Weapons" object
  list used for *attack-targeting priorities* (AI attacking enemy
  superweapons). Unaffected and intentionally left working.
- `SKIRMISH_BUILD_BUILDING` (49x) — the construction orders. These become
  harmless no-ops without build-list entries (engine-verified, see above).

No `AI_PLAYER_BUILD_TYPE_NEAREST_TEAM`, `SKIRMISH_BUILD_STRUCTURE_FRONT/
FLANK` or other build-list-bypassing action references a superweapon, so
build-list removal alone is sufficient. Superweapon *firing* scripts gate on
the structure existing/powering up, so they simply never trigger.

Not yet play-tested in game (verification here is data + engine-source
level); a quick skirmish vs. the SuperWeapon General on Hard is the best
smoke test.

## Files

- `src/AIData.ini.orig` — pristine extract from `!Shw_scripts.big`
- `src/AIData.ini` — edited copy (only `;` comment-outs)
- `src/SkirmishScripts.scb` — pristine extract, analysis only, not shipped
- `tools/scb_scan.py` — .scb parser used for the verification above
- `build.py` — rebuilds and reinstalls the archive
- `build/zzyzy_NoAISuperweapons.big` — the artifact

## Rebuild

```sh
python3 build.py
```

## Uninstall

```sh
rm ~/GeneralsX/mods/ShockWaveSPE/zzyzy_NoAISuperweapons.big \
   ~/GeneralsX/mods/ShockWave/zzyzy_NoAISuperweapons.big
```

No other files are touched; removing the archive fully restores stock AI
behavior.
