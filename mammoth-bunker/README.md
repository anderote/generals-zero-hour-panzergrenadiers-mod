# Mammoth Bunker — mini-mod for ShockWave (GeneralsX/macOS)

Gives General Ironside's (USA Armor General) **Mammoth Tank**
(`Armor_AmericaTankPaladin`) an infantry bunker bay like China's Overlord
battle bunker: up to **4 infantry** can garrison the tank and fire out, and
can be evacuated via new command-bar buttons.

Output archive: **`zzy_MammothBunker.big`** — the name is deliberate: inside a
`-mod` directory, later-alphabetical archives take priority (each archive
prepends), so it must sort after `zz_SPE_*.big` (SPE campaign overlay) but
before `zzz_ControlBarPro*.big` (UI skin).

## Design

The Overlord implements its bunker as a purchasable PORTABLE_STRUCTURE rider
mounted through `OverlordContain` (Slots = 1). The Mammoth **already uses that
single OverlordContain seat** for its Energy Shield rider
(`AmericaEnergyShieldSphereDummy_Mammoth`, spawned by
`OCL_AmericaEnergyShieldUpgrade_Mammoth` when the player-level
`Upgrade_AmericaEnergyShieldGenerator` completes). Adding an Overlord-style
bunker rider would therefore race the shield rider for that seat in *both*
purchase orders (verified in engine source, `OverlordContain.cpp`:
redirection uses `m_containList.front()->getContain()`), breaking either the
bunker or the shield.

Instead the mod swaps the Mammoth's `OverlordContain` for **`HelixContain`**
(the module the Helix uses to carry infantry *and* a gattling/bunker addon at
the same time). Engine-source facts that make this safe (`HelixContain.cpp`,
GeneralsX GeneralsMD tree):

- A PORTABLE_STRUCTURE entering a HelixContain is stored in a dedicated
  `m_portableStructureID` rider slot, **outside** the passenger list: it
  consumes no slots, never appears on exit/evacuate buttons, cannot be
  ejected, and is *always* allowed to fire. The Energy Shield rider therefore
  keeps working exactly as before (its anti-missile weapon included).
- `W3DOverlordTankDraw` (the Mammoth's draw module) locates the rider via
  `friend_getRider()`, which HelixContain implements — shield visuals intact.
- Infantry go into normal transport slots; `PassengersAllowedToFire = Yes`
  lets them fire out. `AVMammoth` has no FIREPOINT bones, so the engine falls
  back to firing from the vehicle center (`OpenContain::putObjAtNextFirePoint`)
  — graceful, same as many retail transports.
- The `OCL … ContainInsideSourceObject` path into HelixContain is proven by
  the retail Helix gattling/bunker upgrades.

The bay is **innate** (like the GLA Battle Bus) rather than upgrade-gated:
pure INI cannot gate a contain module behind an upgrade without the
rider-object approach that conflicts with the Energy Shield. Rocketpods and
Energy Shield upgrades are untouched.

## Files changed (both sourced from `zz_SPE_Shw_ini.big`; the copies in
`!Shw_ini.big` are byte-identical, so one patched copy overrides both)

1. `Data\INI\Object\USA\Armor\Vehicles\Mammoth.ini`
   — `Behavior = OverlordContain ModuleTag_ArmorAddon01` (Slots 1,
   PORTABLE_STRUCTURE only, 100% pass-through damage) becomes
   `Behavior = HelixContain ModuleTag_ArmorAddon01` with:
   `Slots = 4`, `AllowInsideKindOf = INFANTRY PORTABLE_STRUCTURE`,
   `ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT`,
   `DamagePercentToUnits = 0%` (garrisoned infantry protected, like the
   Overlord bunker's contain; the shield rider is invulnerable and is not in
   the damage-sharing list anyway), Garrison enter/exit sounds,
   `PassengersAllowedToFire = Yes`.

2. `Data\INI\CommandSet.ini`
   — `Armor_AmericaTankPaladinCommandSet` gains
   `4-7 = Command_TransportExit` (contiguous, as the control-bar code
   requires) and `8 = Command_Evacuate`. Slots 4-8 were free (drones occupy
   1-3; 11/13/14 are attack-move/guard/stop). Both buttons are existing
   generic ShockWave buttons (SSEvacButton art, `CONTROLBAR:TransportExit` /
   `CONTROLBAR:Evacuate` labels) — no new CSF strings or button art.

No other files are modified; the archive contains only these two full
patched copies at their original internal paths.

## Rebuild

```
python3 build.py
```

Reads the effective sources (SPE overlay → base ShockWave → vanilla INIZH),
re-applies the patches (fails loudly if the upstream text drifts), writes
`zzy_MammothBunker.big` here, and installs copies into both mod dirs.
Depends on `../hotkey-addon/bigfile.py`.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzy_MammothBunker.big`
- `~/GeneralsX/mods/ShockWave/zzy_MammothBunker.big`

## Uninstall

Delete `zzy_MammothBunker.big` from both directories above.

## Known limitations / risks

- Saved games made before installing (or mid-campaign saves made with the
  mod) reference a different module list for the Mammoth; loading across an
  install/uninstall boundary may fail — start fresh missions/skirmishes.
- Infantry fire from the tank's center (no FIREPOINT bones in the model), and
  there is no bunker visual on the hull; garrisoned state is conveyed by the
  container pips/exit buttons.
- HelixContain applies the GARRISONED weapon bonus to passengers (same as
  Helix riders) — a small intentional flavor buff.
- If the Energy Shield is researched, the shield rider mounts as the
  HelixContain "rider" slot, exactly one PORTABLE_STRUCTURE is supported —
  fine here since the shield dummy is the only such object that can enter.
