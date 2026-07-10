# China Tank Buff (ShockWave / GeneralsX)

Stat-buff mini-mod for C&C Generals Zero Hour: ShockWave running under
GeneralsX. Every Chinese tank (all five China generals) gets:

- **+20% max health** (MaxHealth and InitialHealth, rounded to integer)
- **+10% weapon range** (AttackRange on the tanks' weapon templates;
  MinimumAttackRange untouched; dummy targeting weapons untouched)
- **+5% movement speed** (Speed on the tanks' locomotors, including the
  nuclear/fusion-engine upgraded locomotors so the buff survives speed
  upgrades)

## What it is

`zzx_ChinaTankBuff.big` — a BIG archive containing full modified copies of
24 China vehicle INIs plus `Data\INI\Weapon.ini` and
`Data\INI\Locomotor.ini`, taken from `zz_SPE_Shw_ini.big` (the
ShockWaveSPE override archive). The `zzx_` prefix sorts after
`!Shw_ini.big` and `zz_SPE_Shw_ini.big` inside the -mod directories, so
these copies win at load time (later-alphabetical wins), and before
`zzy_`/`zzz_` addons.

Buffed units (24 objects): Battlemaster (vanilla/Nuke/Tank gen + campaign
variants), WarMaster, Emperor, Overlord (vanilla/Nuke), Battle Fortress,
Devastator, Reaper, Ravage Tank, Seismic (Anvil) Tank, Dragon Tank
(vanilla/Tank/Leang), Rad Tank, ECM Tank (vanilla/Tank gen), Gattling Tank
(vanilla/Nuke/Tank/Leang), Gattling APC, Tiger Shark.

Note: ShockWave removed the `TANK` KindOf flag from every object, so tanks
are matched by a curated whitelist in `build_china_tank_buff.py` rather
than by KindOf.

## How it was built

```
python3 build_china_tank_buff.py
```

The script reads `~/GeneralsX/mods/ShockWaveSPE/zz_SPE_Shw_ini.big`,
applies the multipliers with line-precise regex edits (only
MaxHealth/InitialHealth/AttackRange/Speed lines change; verified by diff),
writes `zzx_ChinaTankBuff.big` here, and installs it to both mod dirs.
`build_report.txt` holds the full old->new change table and the shared
weapon/locomotor spillover audit.

## Install locations

- `~/GeneralsX/mods/ShockWave/zzx_ChinaTankBuff.big`
- `~/GeneralsX/mods/ShockWaveSPE/zzx_ChinaTankBuff.big`

## Uninstall

Delete `zzx_ChinaTankBuff.big` from both directories above. No other files
are touched.

## Known spillover (shared templates, intentionally accepted)

- `TroopCrawlerWaterLocomotor` (+5% water speed): shared by all Troop
  Crawlers, GLA BRDM-1, Technical, Toxin Truck (amphibious/water movement
  only).
- `GattlingTankLocomotor` (+5%): also used by USA Armor General's
  Microwave Tank.
- `OverlordLocomotor` (+5%): also used by `Mech_Executioner`.
- `BattleMasterTankGun`, `OverlordTankGun`, Dragon Tank flame weapons
  (+10% range): also referenced by cinematic-only `CINE_*` objects.
