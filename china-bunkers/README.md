# China Bunkers — mini-mod for ShockWave (GeneralsX/macOS)

Two features for China across all generals:

1. **Battlemaster bunker bay** — every Battlemaster tank variant gets an
   INNATE 4-soldier bunker bay: infantry ride inside, fire out, and can be
   ejected via new exit/evacuate command-bar buttons.
2. **Troop Crawler fire ports** — China's Troop Crawler APCs let their
   passengers fire out of the vehicle.

Output archive: **`zzyy_ChinaBunkers.big`** — the name is deliberate: inside
a `-mod` directory, later-alphabetical archives take priority, so it must
sort after `zzx_ChinaTankBuff.big` and `zzy_MammothBunker.big` (whose files
this mod layers on) but before `zzz_ControlBarPro*.big` (UI skin).

## Design

### Battlemasters

| Object | General | Design |
|---|---|---|
| `ChinaTankBattleMaster_Var1` (Var2–4 inherit via ObjectReskin) | vanilla China | plain `TransportContain` |
| `Nuke_ChinaTankBattleMaster` | Nuke General | plain `TransportContain` |
| `Tank_ChinaTankBattleMaster` | Tank General | **`HelixContain`** (see below) |
| `Spec_ChinaTankBattleMaster` (Ravage Tank) | Special Weapons | plain `TransportContain` |

The vanilla, Nuke and Ravage Battlemasters have no contain module, no rider
and no `W3DOverlordTankDraw`, so they simply gain a new behavior block (the
vanilla fire-out-transport idiom):

```
Behavior = TransportContain ModuleTag_BunkerBay01
  Slots = 4, DamagePercentToUnits = 0% (garrisoned infantry protected),
  AllowInsideKindOf = INFANTRY, ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT,
  Garrison enter/exit sounds, PassengersAllowedToFire = Yes
```

The **Tank General's** Battlemaster is the same situation the Mammoth
Bunker mod solved: it uses `W3DOverlordTankDraw` plus an `OverlordContain`
(Slots = 1, PORTABLE_STRUCTURE) that seats the ERA armor-addon rider
(`ChinaTankArmorUpgradeAddon_BattleMaster`, spawned by
`OCL_BattleMasterArmorAddons` / `Upgrade_TankLightArmor` with
`ContainInsideSourceObject = Yes`). Adding a separate transport bay would
conflict, so — exactly like `zzy_MammothBunker` — the `OverlordContain` is
swapped for **`HelixContain`**: the PORTABLE_STRUCTURE rider lives in a
dedicated rider slot *outside* the passenger list (never on exit buttons,
consumes no slots, `W3DOverlordTankDraw` still finds it via
`friend_getRider()`), while 4 infantry ride in the normal slots and fire
out. The ERA armor upgrade is untouched.

Command sets (exit buttons must be contiguous — engine requirement):
`ChinaVehicleBattleMasterCommandSet`, `Nuke_…` and `Tank_…` gain
`1-4 = Command_TransportExit`, `5 = Command_Evacuate` (slots 1–10 were
free); `Spec_…` gains them at `2-5` / `6` (slot 1 is the Ramjet Shell
button). Both buttons are existing generic ShockWave buttons — no new art
or CSF strings.

Infantry fire from the hull center (the Battlemaster models have no
FIREPOINT bones; the engine falls back gracefully, same as the Mammoth and
many retail transports).

### Troop Crawlers

`PassengersAllowedToFire = Yes` added as the first line of the existing
infantry `TransportContain` (same placement the Infantry General's crawler
already uses):

- `ChinaVehicleTroopCrawler` (vanilla, 8 slots)
- `Nuke_ChinaVehicleTroopCrawler` (8 slots)
- `Tank_ChinaVehicleTroopCrawler` (6 slots)
- `Spec_ChinaVehicleTroopCrawler` (Support Crawler, 4 slots — it *does*
  carry infantry)
- `ChinaVehicleTroopCrawlerEmpty` (the buildable "empty" crawler in
  `ChinaMisc.ini`, 8 slots)

Untouched: `Infa_ChinaVehicleTroopCrawler` (already has
`PassengersAllowedToFire = Yes`) and `CINE_ChinaVehicleTroopCrawlerEmpty`
(cinematic-only prop). Crawler command sets already have 8 contiguous
`Command_TransportExit` buttons — no changes needed there.

## Files in the archive (full patched copies, original internal paths)

Layered on the **highest-priority** source of each file:

| File | Source archive |
|---|---|
| `Data\INI\Object\China\Vanilla\Vehicles\BattleMaster.ini` | `zzx_ChinaTankBuff.big` |
| `Data\INI\Object\China\Nuke\Vehicles\BattleMaster.ini` | `zzx_ChinaTankBuff.big` |
| `Data\INI\Object\China\Tank\Vehicles\BattleMaster.ini` | `zzx_ChinaTankBuff.big` |
| `Data\INI\Object\China\SpecialWeapons\Vehicles\RavageTank.ini` | `zzx_ChinaTankBuff.big` |
| `Data\INI\CommandSet.ini` | `zzy_MammothBunker.big` |
| `Data\INI\Object\China\Vanilla\Vehicles\TroopCrawler.ini` | `zz_SPE_Shw_ini.big` |
| `Data\INI\Object\China\Nuke\Vehicles\TroopCrawler.ini` | `zz_SPE_Shw_ini.big` |
| `Data\INI\Object\China\Tank\Vehicles\TroopCrawler.ini` | `zz_SPE_Shw_ini.big` |
| `Data\INI\Object\China\SpecialWeapons\Vehicles\SupportCrawler.ini` | `zz_SPE_Shw_ini.big` |
| `Data\INI\Object\China\Vanilla\ChinaMisc.ini` | `zz_SPE_Shw_ini.big` |

The china-tank-buff values (e.g. Battlemaster `MaxHealth = 480`, Ravage
`576`) and the Mammoth Bunker's `Armor_AmericaTankPaladinCommandSet` patch
are preserved — verified at build time; the build fails if they drift.

## Rebuild

```
python3 build.py
```

Reads the effective sources, re-applies the patches (fails loudly if the
upstream text changes), verifies buff survival and block structure, writes
`zzyy_ChinaBunkers.big` here, re-reads it to confirm round-trip integrity,
and installs copies into both mod dirs. Depends on
`../hotkey-addon/bigfile.py`.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzyy_ChinaBunkers.big`
- `~/GeneralsX/mods/ShockWave/zzyy_ChinaBunkers.big`

## Uninstall

Delete `zzyy_ChinaBunkers.big` from both directories above.

## Known limitations / risks

- **Save games**: saves made before installing (or with the mod, loaded
  after uninstalling) reference different module lists for these units —
  loading across an install/uninstall boundary may fail. Start fresh
  missions/skirmishes.
- If `zzx_ChinaTankBuff.big` or `zzy_MammothBunker.big` is later rebuilt
  with different content, **rebuild this archive too** — it embeds full
  copies of their files, and being later-alphabetical it would silently
  mask their newer versions.
- No bunker visual on the Battlemaster hull; garrisoned state shows via
  container pips and the exit buttons. Passengers fire from the hull
  center.
- HelixContain / garrison-style contains grant passengers the GARRISONED
  weapon bonus — a small intentional flavor buff, same as the Mammoth mod.
- The Support Crawler (Spec) keeps its 8 exit buttons for only 4 seats
  (pre-existing ShockWave quirk; extra buttons are simply blank).
- AI generals never load infantry into Battlemasters (no AI scripting was
  added); the feature is effectively player-facing.
