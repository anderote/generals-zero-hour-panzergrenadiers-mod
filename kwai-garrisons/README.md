# Kwai Garrisons (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Makes
**eight of Kwai's (China Tank General) buildings garrisonable**: up to
**10 infantry** each enter, **fire out** of the structure, and can be
evacuated from the command bar. Passengers automatically receive the
**GARRISONED weapon bonus** (with stat-tune's RANGE 175% this makes
garrisoned buildings serious strongpoints) — the engine sets/clears the
bonus itself in `GarrisonContain.cpp:1627/1667`, no extra work needed.

Output archive: **`zzz-ZZZKwaiGarrisons.big`** (installed to both mod
dirs). Case-insensitively `zzz-zzk…` < `zzz-zzz…` puts it **after**
`zzz-ZZKwaiBaseTech.big` (whose CommandSet.ini and building object files
it layers on) and `-` (0x2D) < `_` (0x5F) puts it **before**
`zzz_ControlBarPro*.big` — verified against the real directory listings
at build time.

## Garrisoned-building roster

| Building | Seats | Exit cameo buttons | Evacuate | Notes |
|---|---|---|---|---|
| Command Center | 10 | none | **slot 4** (the commented-out NapalmStrike hole; set was otherwise full) | Evacuate momentarily unreachable while the Taunt sub-menu is open — flip back first |
| War Factory | 10 | none | **slot 13** | **Sacrifice (documented):** the per-building Mines / EMP-Mines button was replaced — mines remain purchasable on every other Kwai structure; all 12 production buttons (incl. kwai-artillery's 11–12) and Sell preserved |
| Supply Center | 10 | slots 2–11 (all 10) | slot 12 | |
| Power Plant | 10 | slots 2–11 (all 10) | slot 12 | Got **new Kwai-only command sets** (see below) |
| Propaganda Center | 10 | none | **slot 12 in all 50 sets** (2 base + kwai-doctrine's 48 state sets) | Slot 12 was verified free in every set |
| Airfield | 10 | slots 3–9 (7) | slot 10 | Aircraft parking/landing untouched (see engine notes) |
| Industrial Plant | 10 | slots 3–11 (9) | slot 12 | |
| Nuclear Silo | 10 | slots 2–9 (8) | slot 10 | |

Both the base set and the EMP-mines `…CommandSetUpgrade` variant of every
building were patched identically.

### Skipped buildings (and why)

- **Barracks** — already carries **`HealContain ModuleTag_06`** (infantry
  enter to heal). An object supports only one contain module
  (`Object::getContain` returns a single interface); adding a
  GarrisonContain would double-contain. Skipped, heal-up behavior intact.
- **Internet Center** — already carries **`InternetHackContain`** with
  stat-tune's **30 hacker slots**; explicitly excluded so it is not
  double-contained. Untouched (not even shipped in the archive).
- Defenses (Tank Bunker, Gattling Cannon, Sentry Turret, Hacker Bunker,
  Speaker Tower) — out of scope: already garrison/contain structures or
  armed defenses.

## Mechanism (engine-source verified, GeneralsX GeneralsMD tree)

One `GarrisonContain` block per building, mirrored field-for-field from
the shipping faction precedents **GLAPalace** (`ModuleTag_10`) and
**ChinaBunker** (`ModuleTag_08`):

```
Behavior = GarrisonContain ModuleTag_KG_Garrison01
  ContainMax                    = 10
  EnterSound                    = GarrisonEnter
  ExitSound                     = GarrisonExit
  ImmuneToClearBuildingAttacks  = Yes
End
```

- `GarrisonContainModuleData` defaults `AllowInsideKindOf` to
  **INFANTRY** (`GarrisonContain.cpp:70`) — no kindof line needed.
- `MAX_GARRISON_POINTS = 40` (`GarrisonContain.h:185`) — all 10 riders
  get firing positions, auto-computed from the building geometry (no
  FIREPOINT bones needed).
- **Enemies can never enter**: `ActionManager::canEnterObject` rejects
  any non-owning player for faction structures ("faction structure...
  can't do it") — same as China bunkers.
- **Coexistence precedents**: **`TechWarFortress_Real`** ships with
  `AIUpdateInterface + GarrisonContain + ProductionUpdate +
  SpawnBehavior + WeaponSet` on a single object — a superset of every
  module combination this mod creates (the 5 basetech-armed buildings
  carry `AIUpdateInterface`/`WeaponSetUpgrade`/WeaponSets; all 8 carry
  `ProductionUpdate`; the Supply Center carries `SpawnBehavior`).
  **GLAPalace** = GarrisonContain + ProductionUpdate on a player-owned
  *production* building. Airfield: aircraft never use the contain module
  — `canEnterObject` short-circuits `KINDOF_AIRCRAFT` +
  `KINDOF_FS_AIRFIELD` into the `ParkingPlaceBehavior` path *before* the
  contain checks, so parking/landing is unaffected.
- **KindOf untouched** (no `GARRISONABLE_UNTIL_DESTROYED`): like
  civilian buildings, passengers are auto-ejected when the structure
  turns REALLYDAMAGED and can't re-enter until repaired
  (`GarrisonContain.cpp:1750`/`:564`). Deliberate: keeps every building
  diff pure-insertion and gives attackers counterplay (Kwai's doctrine
  armor tiers + basetech auto-repair already make these buildings tanky).

## UI / evacuate findings (engine-source verified)

- The dedicated **garrison-inventory panel** (`CB_CONTEXT_STRUCTURE_INVENTORY`,
  10 physical exit buttons) is used **only for objects whose command-set
  string is empty** (`ControlBar.cpp:1904` — "we only want to use this if
  we DON'T have a commandset. If we do, then trust that the commandset
  will handle it!"). That's why neutral civilian buildings get it and
  faction buildings don't. **Conclusion: no free engine UI for owned,
  garrisoned faction buildings — Evacuate must be a command button**, so
  every garrisoned building got one (table above).
- **`Command_Evacuate` works with or without an AIUpdateInterface**:
  `AIGroup::groupEvacuate` calls `contain->orderAllPassengersToExit`
  directly for AI-less `KINDOF_STRUCTURE`s, and
  `AIUpdateInterface::privateEvacuate` also goes straight to the contain
  (no locomotion involved). The button self-disables while the building
  is empty (`ControlBarCommand.cpp:1375`, `COMMAND_RESTRICTED`).
- **`Command_StructureExit`** (`EXIT_CONTAINER`) buttons are filled with
  passenger cameos by `ControlBar::doTransportInventoryUI`
  (`GarrisonContain::isDisplayedOnControlBar()` returns TRUE). Exit
  buttons **must be contiguous** in the set; when passengers outnumber
  exit buttons the overflow simply gets no cameo (the `DEBUG_CRASH` is
  compiled out in this build — the emperor-bunker finding). Partial exit
  rosters are therefore safe; **Evacuate always unloads everyone**.
- There is no right-click/hotkey evacuate path that bypasses the command
  bar for structures; hotkeys only trigger buttons present in the
  current set.

## The Power Plant special case

Kwai's power plant referenced **`ChinaPowerPlantCommandSet`/`…Upgrade` —
sets SHARED with vanilla China's power plant**. Patching them would leak
garrison buttons onto another general's building (doctrine's shared-file
rule), so instead:

- Two **new** sets `Tank_ChinaPowerPlantCommandSet` /
  `Tank_ChinaPowerPlantCommandSetUpgrade` are appended (Overcharge 1,
  exits 2–11, Evacuate 12, Mines/EMP-Mines 13, Sell 14) — matching the
  `Infa_`/`Nuke_`/`Spec_` naming convention the other generals already
  use for their own power-plant sets.
- `PowerPlant.ini`'s two set references are retargeted (2
  single-occurrence exact line swaps — the kwai-bunkers Dozer idiom).
- The vanilla-shared set pair is asserted **byte-identical** in the
  shipped file.

## Files in the archive (9, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZKwaiBaseTech.big` | 128 slot lines inserted (Evacuate in all 50 prop-center sets + exit/evacuate runs in 6 building-set pairs), the 2 WF mines lines replaced by Evacuate, 2 Kwai power-plant sets appended |
| `…\Tank\Buildings\{CommandCenter, WarFactory, SupplyCenter, PropagandaCenter, Airfield, IndustrialPlant, NuclearSilo}.ini` (7) | `zzz-ZZKwaiBaseTech.big` | +1 GarrisonContain block each (pure insertion) |
| `…\Tank\Buildings\PowerPlant.ini` | `zzz-ZZKwaiBaseTech.big` | +1 GarrisonContain block; 2 command-set reference lines retargeted |

No CommandButton.ini / Generals.str / Upgrade.ini / Weapon.ini changes —
`Command_StructureExit` and `Command_Evacuate` are existing ShockWave
buttons with existing strings and cameos. Barracks.ini and
InternetCenter.ini are **read for skip-validation only, not shipped**.

## Build-time verification (all enforced, build fails loudly otherwise)

- Effective-file ownership asserted per file (all `zzz-ZZKwaiBaseTech.big`;
  drift = abort); new identifiers (`ModuleTag_KG_Garrison01`, the 2 set
  names) collision-checked across the **entire effective INI space**
  (776 files).
- Contain-freedom asserted on all 8 targets; the Barracks/Internet-Center
  skip reasons asserted still true (HealContain / InternetHackContain
  present).
- Diff audits: every building file = pure insertion of exactly the
  garrison block (PowerPlant additionally exactly the 2 line swaps);
  CommandSet.ini additions/removals matched as exact line multisets.
- Garrison-set audit on final text: Evacuate reachable in **every**
  command set of every garrisoned building (incl. all 50 prop-center
  sets), exit buttons contiguous with Evacuate directly after the run,
  no slot collisions, nothing beyond the 14 UI windows, Sell intact.
- **Sibling survival re-asserted on the shipped and installed bytes**:
  basetech heal modules + armed weapon sets/AI + prop-center slots 10–11;
  doctrine's 48 state sets, slots 4–9 (all 50 sets) and all four armor
  tiers (with triggers) in every shipped object file; kwai-bunkers dozer
  pages + Hacker Bunker set; kwai-artillery factory slots 11–12;
  emperor-bunker Emperor set; mammoth-bunker slots 4–8; Battlemaster
  exit/tower/ERA sets; vanilla China dozer pages, prop-center sets and
  the **vanilla-shared power plant sets byte-untouched**; production
  modules (ProductionUpdate) still present on all 8 buildings.
- Archive sort position checked against the real directory listings;
  installed archives re-read and re-verified byte-for-byte; rebuild is
  idempotent (self-archive excluded from sourcing, hash-stable).

## Rebuild

```
python3 build.py
```

Reads the effective sources from `~/GeneralsX/mods/ShockWaveSPE/`
(excluding its own archive), patches, verifies, writes
`zzz-ZZZKwaiGarrisons.big` here and installs to both mod dirs. Depends
on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer** (directly
before the `zzz_ControlBarPro*` skins). If **any** lower layer is
rebuilt (kwai-basetech, kwai-bunkers, kwai-doctrine, stat-tune,
emperor-bunker, kwai-artillery, …), rebuild this archive afterwards — it
embeds full copies of their files and would otherwise mask their newer
versions. Conversely the lower layers' own builds must not see this
archive:

1. rebuilding **kwai-basetech** → delete `zzz-ZZZKwaiGarrisons.big` from
   both mod dirs first, rebuild it, then rerun this build;
2. rebuilding **kwai-bunkers** → delete both `zzz-ZZZKwaiGarrisons.big`
   and `zzz-ZZKwaiBaseTech.big` first, rebuild bunkers, rebuild
   basetech, then rerun this build;
3. rebuilding **kwai-doctrine** → delete all three
   (`…Garrisons`, `…BaseTech`, `…Bunkers`) first, rebuild doctrine →
   bunkers → basetech, then rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZKwaiGarrisons.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZKwaiGarrisons.big`

## Uninstall

Delete `zzz-ZZZKwaiGarrisons.big` from both directories above. No other
files are touched.

## Known limitations / risks

- **Save games**: 8 structures gained a contain module — saves crossing
  an install/uninstall boundary may not load. Start fresh games.
- Passengers are ejected automatically when a building reaches the
  REALLYDAMAGED (red) state and cannot re-enter until it's repaired —
  intended civilian-building semantics (no `GARRISONABLE_UNTIL_DESTROYED`).
- If the building dies with infantry inside, they die with it (standard
  garrison behavior).
- No garrison visuals: the buildings' models have no GARRISONED state or
  flag, so occupancy shows only via container pips, exit cameos and
  muzzle flashes from the auto-computed fire points.
- Command Center / War Factory / Propaganda Center have **no individual
  exit cameos** (sets were full) — use Evacuate; Airfield (7), Nuclear
  Silo (8) and Industrial Plant (9) have partial rosters; overflow
  passengers simply lack a cameo (safe, engine-verified).
- **War Factory sacrificed its per-building Mines/EMP-Mines button**
  (slot 13) for Evacuate — the WF itself can no longer buy its own
  minefield; every other Kwai structure still can.
- Evacuate on the Command Center is hidden while the Taunt menu is open
  (flip back with the exit-taunt button).
- Building captured by an enemy: the garrison contain transfers with the
  building (new owner may garrison it) — standard engine behavior, same
  as captured China bunkers.
- AI never garrisons its own buildings (no AI scripting added);
  player-facing only.
- Balance: 10 fire-out slots on tanky, self-repairing, (upgradably)
  armed structures makes a fully teched Kwai base extremely hard to
  storm with ground forces — intentional; bunker-buster jets, artillery
  and the red-damage auto-eject are the counterplay.
- NOT verified in-game (the game was deliberately not launched); all
  verification is static against the engine source and installed bytes.
