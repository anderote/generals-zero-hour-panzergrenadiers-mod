# Flagship Emperor (+ gattling turret buff)

Layer archive: **`zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big`** (20 Z's — last
data layer of the stack: above Rebalance/TankUpgrades/TeslaHP, below
`zzz_ControlBarPro*`/`zzzz_FXEnhance`). Ships full modified copies of the two
Rebalance-owned files it changes: `Emperor.ini` + `Weapon.ini`.

## Emperor flagship rework (2026-07-19)

| Change | Detail |
|---|---|
| **8× price** | BuildCost 2400 → **19200** (build time unchanged) |
| **Long-barrel cannons** | Main guns repointed to new Emperor-only clones `Tank_EmperorTankGun{,_Dummy}` with AttackRange 175 → **240**. The Overlord keeps the unmodified shared originals. |
| **Innate ABM** | `ModuleTag_EDS_ABM01` interceptor array baked `StartsActive = Yes`, upgrade gate removed. Known wart: the ABM purchase button remains and is now a no-op money sink (commandset surgery out of scope). |
| **Shell-intercepting lasers** | `InterceptBallistics = Yes` added to the Emperor's `PointDefenseLaserUpdate` module (innate PDL): lasers also shoot down artillery shells incl. nuke-cannon shells. **Requires the fork engine ≥ 2026-07-19** (the key is a fork addition — older binaries fail INI parse at startup). |

## Gattling turret (building) buff

All 6 `Tank_[Advanced]GattlingBuildingGun*` weapons: Primary/Secondary damage
**×1.2** (20 → 24, 8 → 9.6, 5.5 → 6.6). Ranges/ROF untouched.

## Build / install

```
python3 build.py --stage   # write layer archive only
python3 build.py           # + install to both mod dirs (game must not be mid-session)
```

Verifies: sort position, Rebalance ownership of both sources, both mod dirs
byte-agree, nothing above claims our paths, exact diff audits, donor Overlord
gun untouched, closure of new weapon names, BIG round-trip, post-install
effective ownership.

## Rebuild rule

Rebuild this layer whenever Rebalance (or anything below it that feeds
`Emperor.ini`/`Weapon.ini`) is rebuilt — this layer embeds full copies of both.

## Uninstall

Delete `zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big` from both mod dirs (also
required before rebuilding any lower layer that ships these two files, or
their builders will see our copies as drift).
