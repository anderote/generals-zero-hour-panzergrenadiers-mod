# Defense Veterancy (ShockWave / GeneralsX)

Gives **every combat base-defense STRUCTURE, all factions, all ShockWave
per-general variants** the ability to **earn veterancy from its own kills**.

Output archive: **`zzz-ZZZZZZZZZDefenseVet.big`** (30 object-INI files,
~872 KB; installed to both mod dirs). Adds only two INI fields per structure -
no new objects, no art/audio, no weapon numbers, no new identifiers.

## Mechanism (mirrors the Tesla Coil layer)

Vanilla/stack base defenses carry an `ExperienceValue` but never rank up
because they lack the trainable flag. The engine gates XP accrual on
`IsTrainable` (`ExperienceTracker.cpp:176`) and credits a kill to the firing
object's tracker (`Object.cpp:3565`). The fix per structure is two top-level
`Object` fields, inserted immediately after the existing `ExperienceValue`
line (exactly the Tesla Coil precedent):

```
  ExperienceRequired  = 0 120 300 500 ; base defense ranks up from kills
  IsTrainable         = Yes           ; XP accrual gate
```

Once a defense can rank, the stack's **global** veterancy bonuses apply to it
automatically. `Data\INI\GameData.ini` (effective owner `zz_SPE_Shw_ini.big`)
defines rank bonuses keyed on rank *status*, not per object:

```
WeaponBonus = VETERAN DAMAGE 110%   RATE_OF_FIRE 120%
WeaponBonus = ELITE   DAMAGE 120%   RATE_OF_FIRE 140%
WeaponBonus = HERO    DAMAGE 130%   RATE_OF_FIRE 160%
```

so a ranked defense fires faster / hits harder (plus the stack's rank
armor/health scaling and self-heal) with **zero per-structure bonus work** -
this layer only opens the gate. No HERO weapon-set variants are added (the
Tesla Coil needed one for its custom bolt swap; a global-bonus rank needs
none).

### `ExperienceRequired` tuning

`0 120 300 500` (V / E / H) - deliberately **heavier than the Tesla Coil's
`0 80 200 300`**. Defenses are stationary force-multipliers and should rank
slower than mobile units. `ExperienceValue` (XP *given* when the structure
dies) is left exactly as each structure already had it (200-per-rank for most,
100 for tunnels, 80 for the paradrop turret, 75 for the pillbox).

## The 30 structures (per faction / general)

Selection rule: `KindOf` has **FS_BASE_DEFENSE + STRUCTURE**, the object has an
**AIUpdateInterface**, and its `WeaponSet` names a **real damaging weapon**
(`PrimaryDamage > 0`, `DamageType != STATUS`, not a `*DUMMY` /
`*NotARealWeapon`). Every entry was enumerated and damage-verified against the
live effective ShockWave INI space.

**China (8)** - `Infa_ChinaGattlingCannon`, `Nuke_ChinaGattlingCannon`,
`Tank_ChinaGattlingCannon`, `Spec_ChinaGattlingCannon` (Sentinel),
`ChinaGattlingCannon` (vanilla), `ChinaFlameTower`, `Spec_ChinaHellStorm`,
`Tank_ChinaSentryTower` (Ramjet Turret).

**GLA (8)** - `GLATunnelNetwork` (vanilla) + `Demo_`/`Salv_`/`Slth_`/`Chem_`
tunnel variants + `GLATunnelNetworkNoSpawn` (all fire the built-in
`TunnelNetworkGun` / `Demo_TunnelNetWorkMissile` turret), `Salv_SA2Samsite`
(SA-2 SAM), `Salv_GLAStingerSite` (the Salvage Stinger/**Hornet** site - its
own `HornetRocketLauncherWeapon` turret, unlike other stinger sites).

**USA (14)** - Patriot batteries `AmericaPatriotBattery` +
`AirF_`/`Armor_`/`Lazr_`/`SupW_` variants + `Supw_AmericaPopUpPatriotBattery`;
Firebases `AmericaFireBase` + `AirF_`/`Lazr_`/`SupW_` variants;
`AmericaPillbox`, `Armor_AmericaVulcanTurret`,
`Armor_AmericaGuardianDefenceTurret`, `SupW_AmericaParaDropPopTurret`.

Weapon damages verified (sample): FireBaseHowitzerGun 60, PatriotMissileWeapon
35, SA2 250, HellStorm 100, GuardianTurret 80, Vulcan 10, Pillbox MG 20,
TunnelNetworkGun 15, Hornet 50, Sentinel gattling 15, LaserFireBase designator
10 (EXPLOSION - lethal, not STATUS).

## What was skipped, and why

| Skipped | Reason |
|---|---|
| **All Bunkers** (China Tank/Nuke/Infa/Spec/vanilla, GLA Junk, Hacker Bunker, Armor Module Bunker) | Garrison containers with **no own weapon** - the OCCUPANTS fire and get the XP; `IsTrainable` on the empty shell is inert. |
| **Speaker Towers** (all China) | "Weapon" is `ChinesePropagandaDecalWeapon` (0 damage propaganda decal) - effectively unarmed. |
| **Mortar Pit**, **Stinger Sites** (Demo/Slth/Chem/vanilla), **Machine-Gun Site** | `SPAWNS_ARE_THE_WEAPONS` - the spawned soldiers fire & rank, not the site. (Salvage Hornet site is the exception - it has its own turret, so it's INCLUDED.) |
| **Listening Post Tower**, **Gazer Turret** | Own weapons are `DamageType = STATUS` (target-marking / faerie-fire detection) - non-lethal, cannot get kills. |
| **Demo Traps / Mine Traps** | One-shot, not repeating base-defense turrets. |
| **Base-Armaments-armed economy buildings** (barracks, war factory, command center, power plant, supply/internet center...) | Armed by the kwai-basetech upgrade but **not** FS_BASE_DEFENSE dedicated defenses. **Scope decision:** kept out to keep this layer clean - only dedicated defense structures rank. |
| **Tesla Coil** (`Tank_ChinaTeslaCoil`) | Already `IsTrainable` (tesla-coil layer) - verified present, skipped. |

## Files + sources (effective-file rule)

Each structure's **highest-priority effective copy** is sourced, patched
(insert 2 lines after its `ExperienceValue`), and shipped whole so this
top-sorting layer's override wins. 30 object INIs: 28 sourced from
`zz_SPE_Shw_ini.big`, 2 (`China\Tank\Defences\GattlingCannon.ini` and
`China\Tank\Defences\Ramjet Turret.ini`) from `zzz-ZZKwaiBaseTech.big`.
Original file casing (incl. the space in `Ramjet Turret.ini`) and CRLF line
endings are preserved.

## Packaging / sort order

`zzz-ZZZZZZZZZDefenseVet.big` sorts (case-insensitive):
- **after** `zzz-ZZZZZZZZPanzergrenadier.big` (`P` < `Z` at char 13) and every
  INI layer below it - so its whole-file overrides beat their definitions;
- **before** `zzz-ZZZZZZZZZInfantryScale.big` (`D` < `I` at char 14) - the
  concurrently-built sibling. **Verified disjoint**: InfantryScale ships 105
  files, **zero** overlap with our 30 (structures vs infantry). Order between
  them is therefore irrelevant;
- **before** `zzz_ControlBarPro*` (`-` 0x2D < `_` 0x5F) and `zzzz_FXEnhance`.

Build-time guarantee: **no archive sorting after us claims any path we ship**
(checked against the real listings in both mod dirs, InfantryScale included).
`fx-enhance/` was not touched.

## Build-time verification (all enforced; build fails loudly otherwise)

- Effective source + owner resolved for all 30 files.
- Per-file diff audit: **exactly 2 lines inserted per structure, zero
  removals, zero foreign edits**, `End`-count stable, line-count delta == 2.
- Every target object carries `IsTrainable=Yes` + `ExperienceRequired` in its
  own region; `ExperienceValue` retained.
- Per-file `IsTrainable=Yes` delta == target count -> **no non-target object
  made trainable**.
- All shipped paths are under `Data\INI\Object\`; no new identifiers defined.
- Sort position vs the real listings + disjointness invariant; installed to
  both dirs, re-read, byte-compared, and every structure re-verified in the
  installed bytes. **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding its own
archive), patches, verifies, writes `zzz-ZZZZZZZZZDefenseVet.big` here and
installs to both mod dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note:** this archive embeds whole copies of 30 object INIs
owned by `zz_SPE_Shw_ini.big` / `zzz-ZZKwaiBaseTech.big`. If any lower layer
that owns one of these files is rebuilt, rebuild this archive afterwards so it
re-sources the updated copy. The sibling `zzz-ZZZZZZZZZInfantryScale.big` is
disjoint and order-independent.

## Install / uninstall

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZZZDefenseVet.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZZZDefenseVet.big`

Delete from both dirs to uninstall; no other files are touched.

## Known behaviour / risks

- **AI defenses also rank** from their kills - intended (symmetric; both sides'
  defenses benefit). AI build-lists are unchanged.
- **Slow to rank by design** (`0 120 300 500`); a defense must rack up real
  kills to hit Heroic. Stationary defenses see fewer kills than mobile units,
  so Heroic defenses will be rare and earned.
- Veteran structures draw rank chevrons; with `zzz-ZZZZZZZVetInsignia.big`
  installed they use that layer's art.
- **Save games**: whole-file INI overrides - saves crossing an
  install/uninstall boundary may not load. Start fresh.
- Garrison bunkers / stinger sites still don't rank as *structures* - their
  occupants/spawns are separate (already-trainable) units that rank on their
  own. This is correct: the kill credit goes to whoever fired.
- NOT verified in-game (deliberately not launched); all verification is static
  against the engine-source gate (`ExperienceTracker.cpp:176`) and the
  installed bytes.
