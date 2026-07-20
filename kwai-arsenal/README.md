# Kwai Arsenal — "upgrade the hell out of everything" horde-defense pack

Layer archive: **`zzz-ZZZZZZZZZZZZZZZZZZZZZZ0Arsenal.big`** (22 Z's + `0Arsenal`:
above `zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big` [21 Z's], below
`zzz_ControlBarPro*` / `zzzz_FXEnhance`; whitelisted by the rebuilt Flagship's
guards). **49 files** — full patched copies of every effective source it touches
plus two new objects. STAGE with `python3 build.py --stage`; install mode exists
but the coordinator installs.

## 1 — Battlemaster fleet researches + MBT parity kit

Per-tank Battlemaster purchases become PLAYER researches (War Factory page 3),
and the heavy-tank line gets the Battlemaster's baseline kit:

| Research | Cost | Covers | Mechanism |
|---|---|---|---|
| **Fleet Speaker Towers** | $3000/45s | Battlemaster | the existing tower mount OCU (`ModuleTag_PropTowerMount01` → `OCL_OverlordPropagandaTower`) repointed from the per-tank OBJECT upgrade to the PLAYER research. Retrofit is engine-guaranteed (`Player.cpp:3250` iterates all owned objects on research completion; new builds attempt at creation). |
| **Fleet Point-Defense** | $3000/45s | Battlemaster, Warmaster, JS-7, Overlord | `FireWeaponWhenDamagedBehavior` reactive anti-missile LASER burst (`Tank_EmperorPDLWeapon`, trigger ≥25 dmg) — the EDS/fortress idiom. |
| **Expanded Crew Bays** | $2500/40s | Battlemaster, Warmaster, JS-7 | `ContainCapacityUpgrade AddSlots=4` (BM 4→8, WM 4→8, JS-7 6→10). |

**Rider-coexistence finding**: the tower and the kwai-pdl pod can NEVER coexist
as riders — a HelixContain keeps exactly ONE portable-structure rider and there
are no per-rider mount bones. Resolution: the tower keeps the BM rider slot;
the fleet PDL is the burst module. The BM's pod machinery (mount OCU + 2
exclusivity CommandSetUpgrades) and the **cosmetic** ERA plate OCU
(`ModuleTag_ArmorAddon02`; the ERA **stat** modules stay) are removed so a
researched fleet always gets its towers regardless of ERA/pod order. The old
per-tank buttons (slots 9/10) leave all four BM sets; buttons/upgrades/OCLs/pod
object stay defined (dormant-stub discipline). Other units' pod purchases are
untouched.

**Parity kit findings (per tank)**:
- *Warmaster*: innate coax ✓ already present (vehicle-kit `ShwBattleMasterCoaxMGWeapon`
  TERTIARY), HordeUpdate ✓ already present. Added: the kwai-pdl pod-seat
  HelixContain widened to a **4-slot fire-out bay** (BM config: 25% damage-pass,
  INFANTRY allow, fire-out; the pod still rides the separate rider slot), exits
  2–5 + Evacuate 6 on its command set.
- *JS-7*: innate MGs ✓ (its own Golem HMG SECONDARY+TERTIARY), HordeUpdate ✓.
  Added: pod-seat → **6-slot fire-out bay**, exits 2–7 + Evacuate 8 (its
  `RussianTankGolemCommandSet` is JS-7-only — verified).
- *Overlord* (Kwai builds the vanilla `ChinaTankOverlord` via a roster stub):
  fleet PDL burst only. Towers/bays excluded — it has its own rider-choice
  system (gattling/bunker/tower) and its bunker rider already gets +3 from the
  Fortress layer (asserted exactly one `ContainCapacityUpgrade` on the rider).
- *Reaper*: excluded from the MBT kit — it is the gattling-family specialty
  platform and is covered by Gattling Doctrine II/III instead.

## 2 — War Factory page 3

Page 2 slot 13 (was the Fortress layer's Expanded Battle Bunkers button — moved)
becomes the page-3 flip. Two new **$0/0s OBJECT page tokens**
(`Tank_Upgrade_KwaiWFPageThree/-PageTwoReturn`, GLA-worker token idiom) + two
flip buttons chain pages 1↔2↔3 via `CommandSetUpgrade RemovesUpgrades` resets.

**Page 3 layout** (`Tank_ChinaWarFactoryCommandSet_Down2`): 1 Fleet Speaker
Towers · 2 Fleet Point-Defense · 3 Expanded Crew Bays · 4 Expanded Battle
Bunkers (moved) · 5 Gattling Doctrine II · 6 Gattling Doctrine III · 7 Composite
Armor V · 8 **Dragon Emperor** (construct) · 12 page-up · 13 Evacuate (restored
— serves the kwai-garrisons WF garrison) · 14 Sell.

## 3 — Gattling Doctrine II/III (hosted at WF page 3, NOT the prop center)

The prop center is 14/14 across all 50 doctrine-ladder sets (slot 13 already the
Satellite Uplink) — re-verified. **Mechanism deviation (engine fact)**: +25%
DAMAGE tiers are impossible in pure data — `WeaponBonusUpgrade` sets only the
single `WEAPONBONUSCONDITION_PLAYER_UPGRADE` bit (`WeaponBonusUpgrade.cpp:91`,
no fork selector) and Chain Guns already consumes it on the whole gattling
family (same block kwai-doctrine documents for Tungsten). Instead, the doctrine
ladders' own armor-tier idiom: **II** ($2500) +25% of base HP; **III** ($4000,
requires II) another +25% **plus `ExperienceScalarUpgrade AddXPScalar 1.0`**
(2× veterancy — the only data-legal stacking damage path). Covers Gattling Tank
(350), Reaper (`Tank_ChinaReaperTank_Real`, 700), Gattling Cannon (1250).

## 4 — Barracks page 2 (Kwai only)

Slot 11 was free on both Kwai barracks sets → page-down there (reuses the
shared GLA-worker OBJECT tokens + arrow buttons; OBJECT masks are per-object so
dozer/WF usage doesn't interfere). Return is **mines-aware** (two return
modules: `ConflictsWith Upgrade_ChinaMines` → base set; `RequiresAllTriggers`
with mines → EMP variant) so the EMP-mines button state survives flips.

**Page 2 layout** (`Tank_ChinaBarracksCommandSet_Down`): 1 Body Armor I · 2 Body
Armor II · 3 Weapons Package I · 4 Weapons Package II · 5 Infantry Conditioning
V · 11 page-up · 14 Sell.

- **Body Armor I/II** ($1500/$3000, II requires I): +20% of base HP each
  (stacking `MaxHealthUpgrade`) on Panzergrenadier, TankHunter, Hacker, Black
  Lotus, Sharpshooter, Shmel Trooper, Shock Trooper (`_Var1`). Excluded:
  FlameThrower/MiniGunner/SiegeSoldier — their real objects are other generals'
  units via BuildVariations stubs (the same units kwai-doctrine never covered).
- **Weapons Package I** ($2000): `WeaponBonusUpgrade` on the three units whose
  PLAYER_UPGRADE bit is free (Sharpshooter/Shmel/Shock; PG and TankHunter spend
  theirs on Advanced Infantry Doctrine). **Finding**: the rotr weapons already
  carry dormant `PLAYER_UPGRADE DAMAGE 125% / RANGE 133-145%` lines (rotr
  container-bonus idiom) — the module is the missing activator; only the
  Sharpshooter's shared `USAPathfinderSniperRifle` gets new lines (120%/110%),
  with a cross-faction leak guard (no other effective object uses these weapons
  AND a WeaponBonusUpgrade).
- **Weapons Package II** ($3500, requires I): the single-bit fact forbids a
  second stacked damage tier — it is `ExperienceScalarUpgrade AddXPScalar 1.0`
  on the five combat infantry (2× veterancy).

## 5 — Battle Bunker (dozer page 2, slot 10)

**`Tank_ChinaBattleBunker`** ($800/8s, `SNSuperBunk` cameo) — clone of the
Infantry General's `Infa_ChinaBunker` (2200 HP, **5-man fire-out
GarrisonContain**, mines family) adapted to Kwai (Side/prereq
`Tank_ChinaBarracks`/command sets swapped), + the four Kwai doctrine armor tiers
(+220 each; the Infa original has none) + three per-bunker OBJECT purchases
(fortress idiom, own command bar slots 7–9): **Reinforced Armor** $600 (+1100 =
+50%), **PDL** $800 (reactive burst), **Speaker Tower** $500 (gated
`AutoHealBehavior` aura, 20 HP/s r150 incl. self). Prop-tower re-check: a real
tower rider is still infeasible on a structure (one contain per object) and
`PropagandaTowerBehavior`'s heal rate cannot be OBJECT-gated (`effectLogic()`
reads the PLAYER mask only) — the aura is what works.

## 6 — Doctrine tier V (standalone researches)

Extending the 50-set prop-center ladder to tier V would need 72 sets + module
cross-products — combinatorially unreasonable, so tier V is **standalone**:
**Composite Armor V** (WF page 3 slot 7) and **Infantry Conditioning V**
(barracks page 2 slot 5), $5000/60s each, `RequiredUpgrade` tier IV.
**Exact tier-IV coverage parity, computed dynamically**: every effective object
carrying a tier-IV `MaxHealthUpgrade` gets a tier-V clone of that very module
(same magnitude — tier IV adds exactly 10% of base). 45 modules across 39
files; 25 files pulled in as full copies solely for this (Airfield, Bunker,
CommandCenter, Dozer, DragonTank, ECMTank, EmperorFullDrop, FortressBunker,
GrenadierDrops, HackerBunker, Helix, IndustrialPlant, InfernoCannon,
InternetCenter, NuclearSilo, NukeCannon, PowerPlant, PropagandaCenter,
Ramjet Turret, Razor, Redguard, ShellEmperorElite, SupplyCenter, SupplyTruck,
TroopCrawler).

## 7 — Dragon Emperor

**`Tank_ChinaDragonEmperor`** — clone of the effective (Fortress-owned) Emperor:
**$50000 / 90 s**, HP ×2 (2200), cannons repointed to new clones
`Tank_DragonEmperorTankGun{,_Dummy}` (damage ×1.5, range 240→**260**; donors
untouched), bay 8→**12** (the Fortress Expanded-Battle-Bunkers module carries
over: 12+4=16, asserted), `Scale = 1.15`, `MaxSimultaneousOfType = 3`
(precedented fields). Keeps the full Emperor stack (EDS systems, innate PDL,
doctrine tiers incl. new tier V, crew, propaganda) and the Emperor command set.
Built from WF page 3 slot 8, `SNEmpTank` cameo.

## 8 — Panzerjäger (Tank Hunter follow-up)

- **Build 2 per click**: `QuantityModifier = Tank_ChinaInfantryTankHunter 2` on
  the Kwai Barracks (this layer's copy, inserted next to Flagship's PG ×2 line —
  Flagship must be rebuilt first if it changes Barracks.ini). **The STUB name is
  correct**: matching happens at queue time against the queued template
  (`ProductionUpdate.cpp` `queueCreateUnit`, `isEquivalentTo(unitType)` — the
  construct button's Object), while `BuildVariations` resolves later per spawned
  unit inside `ThingFactory::newObject` (`ProductionUpdate.cpp:815`), and
  `isEquivalentTo` covers identity/override/reskin only
  (`ThingTemplate.cpp:1547-1561`) — never BuildVariations. Flagship's stub-named
  Redguard modifier is the same pattern.
- **Kwai-scoped horde bonus**: new file `…\Tank\Infantry\Panzerjager.ini` with
  **`Tank_ChinaInfantryPanzerjager`** — a concrete clone of the fully-patched
  effective vanilla `ChinaInfantryTankHunter` (module census 31+1: inherits the
  4 doctrine tiers, InfantryDoctrine hook, Body Armor I/II, WP-II XP, tier V)
  plus `HordeUpdate ModuleTag_KA_Horde01` (Panzergrenadier config: RubOffRadius
  60 / Radius 30 / UpdateRate 1000 / KindOf INFANTRY / Count 5 / HORDE),
  `DisplayName = OBJECT:TankPanzerjager` (label exists since the
  panzergrenadier layer — asserted), `Side = ChinaTankGeneral`. The shared
  weapon (`ChinaInfantryTankHunterMissileLauncher`) and vanilla command set are
  deliberate reuse. The Kwai stub (`…\Tank\Infantry\TankHunter.ini`, owner
  Rebalance, now shipped) repoints `BuildVariations` to the clone; its own
  Scale/art/DisplayName/cost overrides are untouched, and every external
  reference (construct button, quantity modifier, command sets) keeps the stub
  name — the shared vanilla unit is untouched for other generals.

## Files (51) / identifiers / verification

Top copies of `CommandSet.ini` / `CommandButton.ini` / `Upgrade.ini` /
`Generals.str` (from Fortress) and `Weapon.ini` (from Flagship; +2 sniper lines,
+2 Dragon guns); object files as listed per feature (owners: Fortress, Flagship,
Rebalance, TeslaHP, KwaiPDL, KwaiDoctrine, ZKwaiBunkers, BaseTech, EmperorTweaks,
DropLadder, ShellKwai, PassengerSurvival, GrenadierResearch, zz_SPE — recorded
per file at build time); 2 new object files (`BattleBunker.ini`,
`DragonEmperor.ini`, both asserted unclaimed stack-wide).

2 new object files became 4 (`BattleBunker.ini`, `DragonEmperor.ini`,
`Panzerjager.ini` new paths + the Tank Hunter stub file). 63 new identifiers +
48 str labels, all word-boundary collision-checked. 16
button→upgrade→module chains closed; 5 `RequiredUpgrade` chains; page 1↔2↔3 and
barracks 1↔2 reachability; exact line-multiset diff audits on every modified
file; append-only asserts on CB/UPG/STR; post-edit layout asserts on 13 command
sets + sibling survival; BIG round-trip; hash-idempotent rebuild; install mode
(not run) re-verifies post-install effective ownership of all 49 paths.

```
python3 build.py --stage   # write layer archive here only (no install)
python3 build.py           # + install to both mod dirs (coordinator only)
```

## Rebuild rules / uninstall

Rebuild this layer whenever ANY lower layer changes — it embeds full copies from
more than a dozen owners (two-way coupling with **Fortress** — its
CommandSet/CB/UPG/STR/Emperor/PropagandaCenter/FortressBunker/ChinaMisc copies
feed this layer — and with **Flagship** — Weapon.ini/Battlemaster/Barracks/
Panzergrenadier/Redguard). Lower layers' builders must not see this archive:
delete `zzz-ZZZZZZZZZZZZZZZZZZZZZZ0Arsenal.big` from both mod dirs first.
Uninstall = delete that archive from both mod dirs; nothing else is touched.

## Known limitations

- Fleet PDL is reactive (pulses on hits ≥25), not a scanning Avenger PDL.
- Warmaster/JS-7 keep their per-tank PDL pod buttons — a pod-equipped tank plus
  the fleet burst stack (pod = proactive interception, burst = reactive).
- The WM/JS-7 bays fire from hull center (no FIREPOINT bones — china-bunkers
  precedent); their models show no garrison visual.
- Old saves crossing the install boundary will not load (module lists changed
  on ~40 objects). AI never uses the new researches/units.
- NOT verified in-game (deliberately not launched); static verification against
  installed bytes + the deployed engine source only.
