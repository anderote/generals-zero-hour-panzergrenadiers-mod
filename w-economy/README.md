# W-Economy + UAV (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX — the
ECONOMY + UAV layer of the Panzergrenadiers stack. Four features, shipped
as pure top-layer file overrides (no lower layer was rebuilt):

1. **ALL CHINA INFANTRY: 50% cost, 2x build speed** — every buildable
   infantry object across ALL five China generals (32 objects).
2. **Kwai Scout Car recon buff** — VisionRange 450 → **900**,
   ShroudClearingRange 500 → **1000**.
3. **UAV FOR EVERYONE, NO REQUIREMENTS** — the kwai-uav Surveillance UAV
   deploy power is de-gated (research deleted) and put on **every
   faction's Command Center** (15 factions).
4. **Kwai production queue bump** — `MaxQueueEntries = 30` on his
   Barracks, War Factory and Airfield (engine default was 9).

Output archive: **`zzz-ZZZZZZZWEconomy.big`** (54 files, all INI — no new
art, strings, objects or identifiers except one module tag).
Case-insensitively `zzz-zzzzzzzw…` sorts **after**
`zzz-ZZZZZZZVetInsignia.big` (`w` > `v` at char 12) and **before**
`zzz_ControlBarPro*.big` (`-` 0x2D < `_` 0x5F) — verified against the real
directory listings of both mod dirs at build time, plus the invariant that
**no archive sorting after ours claims any path we ship**. This is now the
**last INI layer**.

## Feature 1 — China infantry at half cost / double speed

Scope was enumerated mechanically (and re-enumerated post-install as a
build gate): every China-side object with object-level `KindOf … INFANTRY`
and a `BuildCost` whose `UNIT_BUILD` construct button sits in a live
command set. Exactly **32 objects** qualify.

**BuildVariations cost semantics** (engine-verified, GeneralsX GeneralsMD
tree — the kwai-artillery/kwai-roster stub idiom):
`ProductionUpdate::queueCreateUnit` withdraws the **queued** template's
cost (`ProductionUpdate.cpp:424`) and the `BuildVariations` redirect
happens later, at `ThingFactory::newObject` (`ThingFactory.cpp:315`) — so
**the stub's BuildCost/BuildTime is what is charged** and a spawned
variation is never charged. Both the stubs **and** the shared donor
objects are halved; since each build path charges exactly one object,
**no double-halving is possible**. (Kwai's Sharpshooter stub redirects to
4 variation objects that carry **no** BuildCost at all — verified; only
the stub was halved.)

### Price table (cost $ / build time s)

| General | Unit (object) | Was | Now |
|---|---|---|---|
| **vanilla China** | Red Guard ×2 (`ChinaInfantryRedguard`) | 300 / 10 | **150 / 5** |
| | Tank Hunter (`ChinaInfantryTankHunter`) | 300 / 5 | **150 / 2.5** |
| | Siege Soldier (`ChinaInfantrySiegeSoldier`) | 600 / 8 | **300 / 4** |
| | Hacker (`ChinaInfantryHacker`) | 600 / 13 | **300 / 6.5** |
| | Black Lotus (`ChinaInfantryBlackLotus`) | 1500 / 20 | **750 / 10** |
| **Kwai (Tank)** | Red Guard ×2 stub (`Tank_ChinaInfantryRedguard`) | 400 / 12 | **200 / 6** |
| | Tank Hunter stub (`Tank_ChinaInfantryTankHunter`) | 375 / 10 | **185 / 5** ¹ |
| | Hacker stub (`Tank_ChinaInfantryHacker`) | 300 / 13 | **150 / 6.5** |
| | Siege Soldier stub (`Tank_ChinaInfantrySiegeSoldier`) | 600 / 8 | **300 / 4** |
| | Flame Trooper stub (`Tank_ChinaInfantryFlameThrower`) | 350 / 8 | **175 / 4** |
| | Minigunner stub (`Tank_ChinaInfantryMiniGunner`) | 550 / 14 | **275 / 7** |
| | Sharpshooter (`Tank_ChinaInfantrySharpshooter`) | 1200 / 30 | **600 / 15** |
| | Black Lotus stub (`Tank_ChinaInfantryBlackLotus`) | 1500 / 20 | **750 / 10** |
| **Fai (Infantry)** | Red Guard ×3 (`Infa_ChinaInfantryRedguard`) | 450 / 14 | **225 / 7** |
| | Tank Hunter (`Infa_ChinaInfantryTankHunter`) | 350 / 6 | **175 / 3** |
| | Minigunner ×2 (`Infa_ChinaInfantryMiniGunner`) | 550 / 14 | **275 / 7** |
| | Siege Soldier (`Infa_ChinaInfantrySiegeSoldier`) | 600 / 8 | **300 / 4** |
| | Hacker (`Infa_ChinaInfantryHacker`) | 700 / 13 | **350 / 6.5** |
| | Black Lotus (`Infa_ChinaInfantryBlackLotus`) | 1500 / 20 | **750 / 10** |
| | Red Guard Squad (`Infa_ChinaInfantryRedGuardSquadNexus`) | 2000 / 25 | **1000 / 12.5** |
| | Minigunner Squad (`Infa_ChinaInfantryMinigunnerSquadNexus`) | 2000 / 25 | **1000 / 12.5** |
| | Tank Hunter Squad (`Infa_ChinaInfantryTankHunterSquadNexus`) | 2000 / 25 | **1000 / 12.5** |
| **Tao (Nuke)** | Red Guard ×2 (`Nuke_ChinaInfantryRedguard`) | 300 / 12 | **150 / 6** |
| | Tank Hunter (`Nuke_ChinaInfantryTankHunter`) | 350 / 7 | **175 / 3.5** |
| | Siege Soldier (`Nuke_ChinaInfantrySiegeSoldier`) | 600 / 8 | **300 / 4** |
| | Hacker (`Nuke_ChinaInfantryHacker`) | 600 / 13 | **300 / 6.5** |
| | Black Lotus (`Nuke_ChinaInfantryBlackLotus`) | 1500 / 20 | **750 / 10** |
| **Leang (SpecWeap)** | Red Guard ×2 (`Spec_ChinaInfantryRedguard`) | 325 / 10 | **160 / 5** ¹ |
| | Tank Hunter (`Spec_ChinaInfantryTankHunter`) | 300 / 5 | **150 / 2.5** |
| | Flame Trooper (`Spec_ChinaInfantryFlameThrower`) | 350 / 8 | **175 / 4** |
| | Hacker stub (`Spec_ChinaInfantryHacker`) | 600 / 13 | **300 / 6.5** |
| | Black Lotus stub (`Spec_ChinaInfantryBlackLotus`) | 1500 / 20 | **750 / 10** |

¹ .5-dollar halves rounded **down** to the nearest $5 (player-favourable):
325 → 160, 375 → 185.

"×N" = the barracks' `QuantityModifier` (untouched): one purchase yields
N soldiers — those prices got even better per head. Deliberately **not**
halved (never charged through a build queue): CINE_/parade props, Agent,
Secret Police, the unbuildable Officers, `Squad_…` squad members (spawned
free by `SpawnBehavior InitialBurst`), and the MortarPit's internal
soldier. Kwai's stub costs are what his queue charges (stub idiom above),
so his cross-general discounts stack exactly once.

## Feature 2 — Kwai Scout Car vision

`Tank_ChinaVehicleScoutCar` (the kwai-roster clone; effective copy owned
by vehicle-kit, which added its 2-seat infantry bay): `VisionRange`
450 → **900**, `ShroudClearingRange` 500 → **1000**. The vehicle-kit bay,
clone command set and everything else byte-survive; the **vanilla**
Bullfrog scout stays 200/200 (asserted).

## Feature 3 — UAV for everyone, no requirements

The kwai-uav **Surveillance UAV** (`Tank_ChinaSurveillanceUAV`, the
Kwai-branded Global Hawk clone: 200 HP, unarmed, innately stealthed,
detects stealth, vision 350 / dynamic shroud clear 400, permanent until
killed) is now deployable by **every faction** with **no research**:

- **Gating removed** (both halves of the Radar-Van idiom kwai-uav used):
  - client: the deploy button (`Tank_Command_KwaiUAVDeploy`) lost
    `NEED_UPGRADE` + its `Upgrade =` ref;
  - logic: the Internet Center's `StartsPaused` `OCLSpecialPower` and its
    `UnpauseSpecialPowerUpgrade` companion were **removed**;
  - the research button (`Tank_Command_UpgradeKwaiUAVProgram`) was
    **deleted** from CommandButton.ini and from the IC sets. The orphaned
    `Tank_Upgrade_KwaiUAVProgram` block stays defined in Upgrade.ini
    (kwai-infantry-owned) but is unreachable — shipping that whole shared
    file just to delete an orphan was not worth the surface (documented;
    its Generals.str labels are likewise inert).
- **Every Command Center** gained the module (verbatim kwai-uav module
  minus `StartsPaused`; `SpecialPowerModule.cpp:66` — unpaused is the
  default):
  `OCLSpecialPower → Tank_SpecialPowerKwaiUAV → Tank_SUPERWEAPON_KwaiUAV →
  CREATE_ABOVE_LOCATION`. 120 s reload, `SharedSyncedTimer` (all of a
  player's CCs share one clock, ready as soon as the first CC stands).
- **Engine safety for USA** (their CCs already carry the same-enum
  `SpecialPowerSpyDrone`): player-click firing resolves modules **by
  template** (`Object.cpp:5442 getSpecialPowerModule/isModuleForPower`)
  and shared timers are keyed **by template ID** (`Player.cpp:3319`), so
  the two spy-drone-enum powers never cross-fire or share reloads.

### Button placement per faction (all 15 command centers)

| Faction | Command set(s) | Slot | Note |
|---|---|---|---|
| USA vanilla / Air Force / Laser / SuperWeapon / Armor | `…CommandCenterCommandSet` ×5 | **12** | free in all five |
| GLA vanilla / Toxin / Demo / Stealth / Salvage | `…CommandCenterCommandSet` ×5 + `Demo_…Upgrade` (suicide-upgrade state) | **11** | free in all six |
| Leang (China SpecWeap) | `Spec_…CommandSet` + `…Upgrade` | **10** | free — she keeps her taunt menu |
| vanilla China / **Kwai** / Fai / Tao | main + mines-upgrade set ×8 | **12** | sets were FULL 14/14 — **replaces the China taunt-menu button** (see below) |

- **China taunt-menu sacrifice**: the four full China CC rosters lose
  `Command_ChinaTauntMenu` (a voice-line gimmick menu). The taunt
  machinery (CommandSetUpgrade pairs + the 14-button taunt sets) is fully
  intact and Leang still carries the button, so nothing dangles. USA/GLA
  taunt menus (slot 13) untouched.
- **Kwai consistency**: his deploy button **moved** from the Internet
  Center to his CC like everyone else; IC clone slots **7–8 are garrison
  exit cameos again** (the pre-kwai-uav state — hackers 7+ regain their
  individual eject buttons).
- Each patched CC command set is referenced **only** by its own CC object
  (verified) — zero campaign/CINE spillover.
- All factions deploy the **same Kwai-branded drone** (USA Global Hawk
  model, China-tank-general Side, works for whoever owns the deploying
  CC — standard cross-side OCL reuse, pre-approved).

## Feature 4 — Kwai production queues

`MaxQueueEntries = 30` (engine default is 9, `ProductionUpdate.cpp:104`;
none of the three set it explicitly — verified) on:

| Building | ProductionUpdate | Was → Now |
|---|---|---|
| `Tank_ChinaBarracks` | `ModuleTag_10` (keeps the ×2 Redguard QuantityModifier) | 9 → **30** |
| `Tank_ChinaWarFactory` | `ModuleTag_12` | 9 → **30** |
| `Tank_ChinaAirfield` | `ModuleTag_11` | 9 → **30** |

(The Airfield's 4 parking spaces still cap *simultaneous* aircraft; the
queue just holds more.)

## Files in the archive (54, full patched copies of the effective sources)

| File(s) | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZVehicleKit.big` | 13 deploy-button insertions, 8 taunt→deploy replacements, 4×2 IC-clone lines restored to exits; **zero sets added/removed** |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZZZTTeslaCoil.big` | research button deleted (−1 block), deploy button de-gated (2 lines) |
| `…\China\Tank\Buildings\InternetCenter.ini` | `zzz-ZZZZZZKwaiUAV.big` | the 2 gating modules removed (−2 blocks) |
| 15 × `…\<faction>\Buildings\CommandCenter.ini` | `zz_SPE_Shw_ini.big` ×14, `zzz-ZZZKwaiGarrisons.big` (Kwai) | +1 `OCLSpecialPower ModuleTag_WEco_UAV01` each |
| `…\China\Tank\Vehicles\ScoutCar.ini` | `zzz-ZZZZZZZVehicleKit.big` | 2 vision lines |
| `…\China\Tank\Buildings\Barracks.ini` / `WarFactory.ini` / `Airfield.ini` | `zzz-ZZKwaiBaseTech.big` / `zzz-ZZZZChaosUnits.big` / `zzz-ZZZKwaiGarrisons.big` | +1 `MaxQueueEntries = 30` line each |
| 32 × infantry object files | vanilla 4× `zzz-KwaiDoctrine.big` + `zzz-ZZZZZZZKwaiPDL.big` (SiegeSoldier); Kwai's Hacker `zzz-KwaiDoctrine.big`, SiegeSoldier `zzz-ZZZZZKwaiRoster.big`, FlameTrooper/MiniGunner/Sharpshooter `zzz-ZZZZZZZLKwaiInfantry.big`; the other 19 `zz_SPE_Shw_ini.big` | 2 lines each (BuildCost + BuildTime) |

New identifiers: **none** except the module tag `ModuleTag_WEco_UAV01`
(collision-checked against all 899 effective INI files; reused across the
15 CC objects — module tags only need per-object uniqueness, kwai-pdl
precedent).

## Build-time verification (all enforced; build fails loudly otherwise)

- Effective ownership asserted for all 54 sourced files; sort position +
  "no later archive claims any shipped path" against the real listings of
  both dirs.
- **Exact line-level diff audits on all 54 files** (added/removed line
  multisets must equal the planned edits — every sibling hunk
  byte-survives) + block-balance deltas (CB −1, IC −2, 15 CCs +1, rest 0).
- Scheme drift guards: UAV power/OCL/drone shapes (120 s, shared timer,
  no science, no shortcut, drone stealth+detector), research/deploy
  buttons referenced only by the 4 IC clones pre-edit, CC occupancy
  (USA 12 / GLA 11 / Spec 10 free; taunt at 12 in the 8 full China sets —
  if a slot frees up or the taunt moves, the build stops and the decision
  re-opens), queue defaults (no explicit `MaxQueueEntries`, exactly one
  ProductionUpdate per building).
- **Infantry completeness re-enumeration**: the "buildable China
  infantry" set is recomputed from the patched (and again from the
  installed) effective space and must equal exactly the 32 planned
  objects at exactly the new numbers — a unit added by a future layer
  fails this build.
- Closure: every slot of all 25 touched sets resolves to a CommandButton;
  no new dangling refs anywhere (baseline-aware — ShockWave itself ships
  one dead ref, `Demo_SCIENCE_GLA_CommandSetRank1` slot 11, untouched);
  the deploy chain button→power→OCL→drone resolves in the installed
  effective space of both dirs; zero remaining references to the deleted
  research button; the orphaned upgrade has no live referent.
- Sibling survival on shipped **and installed** bytes: tesla-coil dozer
  page-2 + coil set, kwai-infantry Barracks 5–8, roster WF page 2 /
  Barracks 5, artillery WF 11, kwai-pdl's 17 slot-9 buttons + Emperor +
  Dragon/CommandTruck sets, vehicle-kit's 6 bay sets + Scout Car clone
  set, doctrine's 50 prop-center sets, kwai-bunkers/basetech/garrisons
  sets, ≥60 Evacuates, vanilla IC + Bullfrog + Overlord/Dragon/Generic
  sets frozen, USA spy drone at 7, taunt sets intact.
- Installed archives re-read and byte-compared; post-install
  effective-space audit in both dirs (ownership + exact content of all 54
  paths, untouched neighbours keep their owners); rebuild is
  **hash-idempotent** (verified). **The game was deliberately not
  launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive), patches, verifies, writes `zzz-ZZZZZZZWEconomy.big` here
and installs to both mod dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer** (after
vehicle-kit). If any lower INI layer is rebuilt (vehicle-kit, tesla-coil,
kwai-infantry, kwai-pdl, kwai-uav, kwai-roster, chaos-units,
kwai-garrisons, kwai-basetech, kwai-bunkers, kwai-doctrine,
emperor-bunker, kwai-artillery, stat-tune, china-tank-buff, …), rebuild
this archive afterwards — it embeds full copies of their files
(CommandSet.ini from vehicle-kit, CommandButton.ini from tesla-coil,
InternetCenter.ini from kwai-uav, infantry files from doctrine/pdl/roster/
kwai-infantry, Kwai buildings from basetech/chaos/garrisons, …).
Conversely, lower layers' builds must not see this archive: delete
`zzz-ZZZZZZZWEconomy.big` from both mod dirs first, rebuild the lower
chain in its documented order (… → tesla-coil → vehicle-kit), then rerun
this build. (`zzz-ZZZZZZZVetInsignia.big` is disjoint and
order-independent.)

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZWEconomy.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZWEconomy.big`

## Uninstall

Delete `zzz-ZZZZZZZWEconomy.big` from both directories above. No other
files are touched. (Uninstalling restores the researched, IC-based Kwai
UAV, full-price infantry, 450/500 scout vision and 9-deep queues.)

## Known limitations / risks / balance

- **UAV from second zero for everyone**: the power is ready the moment a
  CC exists (shared 120 s clock per player thereafter). USA effectively
  gets a second, better, science-free spy drone next to their gated
  `Command_SpyDrone`; drones accumulate (permanent until killed) — any AA
  clears them (200 HP, revealed while taking damage). Pre-approved.
- **China (vanilla/Kwai/Fai/Tao) lose the CC taunt menu** — the four full
  rosters had no free slot; the voice-line gimmick was judged the only
  sacrificeable button (units, powers, radar, mines, Evacuate and Sell
  all matter). Leang, USA and GLA keep taunts.
- **AI unaffected**: AI never deploys the UAV (no scripting), AI China
  builds infantry cheaper/faster too only insofar as its scripts queue
  the same objects (they do — a mild AI-China buff, symmetric with the
  player's).
- **Half-price snipers/hackers**: $600 Sharpshooters and $150–350 hackers
  are deliberately strong (spec'd); squad nexuses at $1000 for 13 men are
  the biggest swarm enabler.
- The orphaned `Tank_Upgrade_KwaiUAVProgram` (and its str labels) stay
  defined but unreachable — cosmetically invisible, no engine impact.
- Save games crossing an install/uninstall boundary may not load (module
  lists changed on 16 buildings). Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX engine source
  (GeneralsMD tree).

## CHANGELOG

- **2026-07-10 — kwai-infantry v2 chain rebuild** (performed by the
  kwai-infantry session): kwai-infantry replaced its ZHE Sharpshooter port
  with a single-object vanilla-Pathfinder clone (still 1200/30 at its
  layer; still halved here to 600/15 — INF_PLAN unchanged). `build.py`
  edits: (1) docstring fact about ZHE BuildVariations replaced (the clone
  has exactly one BuildCost line); (2) post-install sibling-owner
  expectations reverted: `Data\INI\Upgrade.ini` ->
  `zzz-ZZZZZZZKwaiPDL`, `Data\INI\SpecialPower.ini` ->
  `zzz-ZZZZZZKwaiUAV` (kwai-infantry no longer ships them); (3) sources
  now read ONLY from archives sorting strictly below this one
  (fx-enhance sorts above and is owned by another session). Archive
  rebuilt (on top of the rebuilt kwai-infantry -> tesla-coil ->
  vehicle-kit chain) and reinstalled to both mod dirs; all original
  assertions green, incl. the 32-object buildable-China-infantry
  re-enumeration at half cost/time.
