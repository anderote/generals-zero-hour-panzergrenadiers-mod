# Kwai Point Defense Laser (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Two
features:

1. **$500 per-vehicle POINT DEFENSE LASER** add-on for all of **Kwai's
   (China Tank General)** combat vehicles: an invisible rider pod that
   automatically shoots down incoming **SMALL_MISSILE**-class ordnance
   (Tomahawks, infantry rockets, AT missiles) near the vehicle with the
   USA Avenger's point-defense laser beam.
2. **Siege Soldier garrison rights**: the vanilla
   `ChinaInfantrySiegeSoldier` (the object Kwai's roster stub builds)
   loses `NO_GARRISON` **and** `BOAT` from KindOf, so it can enter
   building garrisons, bunker bays and tank bays.

Output archive: **`zzz-ZZZZZZZKwaiPDL.big`** (21 files, INI + strings —
all art/sounds are live donor references). Case-insensitively
`zzz-zzzzzzz…` sorts **after** `zzz-ZZZZZZKwaiUAV.big` (`z` > `k` at
char 11; UAV owns the CommandSet/CommandButton/Upgrade/OCL/Generals.str
this layers on), **before** `zzz_ControlBarPro*.big` (`-` 0x2D < `_`
0x5F) and **before** any future `zzz-ZZZZZZZR*.big` (`k` < `r`) —
verified against the real directory listings of both mod dirs at build
time. This is now the **last INI layer**.

## The mechanism (engine-source verified, GeneralsX GeneralsMD tree)

`PointDefenseLaserUpdate` (the Avenger's module,
`PointDefenseLaserUpdate.cpp`) is **not upgrade-gated natively** — its
module data parses only `WeaponTemplate`, `Primary/SecondaryTargetTypes`,
`ScanRate`, `ScanRange`, `PredictTargetVelocityFactor`. So the
**rider-pod pattern** is used (battlemaster-proptower precedent), and it
turns out **ShockWave itself ships the exact idiom**: the Leang
BlackShark Helix's ECM-jammer purchase —
`Command_UpgradeChinaBlackSharkReconUpgrade` ($500 OBJECT upgrade
`Upgrade_BlackSharkJammer`) → `ObjectCreationUpgrade` →
`OCL_BlackSharkECMJammer` (`ContainInsideSourceObject = Yes`) →
`ChinaBlackSharkMissileJammerModule`, a **PORTABLE_STRUCTURE rider with
`Model = NONE` carrying a `PointDefenseLaserUpdate`** targeting
SMALL_MISSILE. That donor proves every load-bearing claim: the pod needs
no visible model, no container draw-module changes, and **the module
scans and fires while mounted/contained** (asserted as drift guard each
build).

The chain (all new identities `Tank_…`, collision-checked):

- `Tank_Command_UpgradeKwaiPDL` — OBJECT_UPGRADE button, **slot 9** of
  every covered vehicle's command set, cameo `SNBlackSharkJammer`
  (the ShockWave missile-jammer icon; no new art).
- `Tank_Upgrade_KwaiPDL` — `Type = OBJECT`, **$500 / 10 s** (donor-parity
  with the BlackShark jammer, and with proptower's tower economics).
- `Tank_OCL_KwaiPDLPod` — spawns the pod straight into the buyer
  (`ContainInsideSourceObject = Yes`).
- `Tank_ChinaPDLPod` (new file `…\China\Tank\Vehicles\PDLPod.ini`) —
  invisible pod, jammer-donor shape: `W3DModelDraw` with `Model = NONE`
  (a drawable still exists — `LaserUpdate::updateStartPos()` needs one to
  anchor the beam, falling back to the drawable position when no bone is
  named, `LaserUpdate.cpp:147-151`), `InvulnerableAllArmor` (shares the
  host's damage model), `StructureBody` 100 HP, `DestroyDie`.
  `PointDefenseLaserUpdate`: `PrimaryTargetTypes = SMALL_MISSILE`,
  **`ScanRange = 160`** (spec ~150–175; the engine requires scan range >
  the weapon's 100 fire range, `PointDefenseLaserUpdate.cpp:109-117`),
  `ScanRate = 0` / `PredictTargetVelocityFactor = 1.0` (Avenger parity).
- `Tank_KwaiPDLLaserWeapon` — **exact clone of
  `AvengerPointDefenseLaserOne`** (100 LASER damage, 100 range, 800 ms
  between shots, `AntiSmallMissile`/`AntiProjectile`,
  `LaserName = AvengerPointDefenseLaserBeam` + the Avenger pulse-sound
  FireFX — beam object, particles and sound all live in base ShockWave,
  asserted) **minus `LaserBoneName = LazerSpot01`** — the pod has no
  bones; dropping the field makes the beam start cleanly at the host
  vehicle's hull instead of triggering a per-shot failed bone lookup.

Pod deviations from the jammer donor (all documented in the shipped
file header): `VisionRange` 200 → **0** (a mass $500 pod must not extend
host vision), **no `StealthDetectorUpdate`** (that is the jammer's ECM
flavor — per-tank stealth detection would be a balance leak), **no
radius-decal `FireWeaponUpdate`** (cosmetic ring dropped),
`PrimaryTargetTypes` = SMALL_MISSILE only (the Avenger also lists
BALLISTIC_MISSILE; SCUD-class interception is deliberately out of scope
per spec).

**NO `VeterancyBoost` fields are emitted anywhere** — the engine patch
for that is not deployed yet; this build asserts the pod carries no such
field. A follow-up layer flips it on once the engine supports it.

### Why a contain seat, and the two engine facts that gate the UI

- `HelixContain`'s **first PORTABLE_STRUCTURE goes into a dedicated
  rider slot regardless of `AllowInsideKindOf`**
  (`HelixContain.cpp:300-306`): it consumes no passenger seats, never
  appears on exit buttons, and is position-synced to the hull every
  frame. Vehicles without any contain get a minimal BlackShark-style bay
  (`Slots = 1`, `AllowInsideKindOf = PORTABLE_STRUCTURE`,
  `PassengersAllowedToFire = No`) — invisible rider ⇒ **no
  `W3DOverlordTankDraw` conversion needed anywhere** (that draw family
  only matters for rendering `W3DDependencyModelDraw` riders; our pod
  renders nothing).
- OBJECT_UPGRADE buttons **require a `ProductionUpdate`** on the object
  (`ControlBarCommand.cpp:1250-1254` greys the button otherwise) — added
  (`MaxQueueEntries = 1`) where missing.
- The engine does **not** grey a *conflicting* OBJECT_UPGRADE button (it
  charges you and the `ConflictsWith` module silently refuses), but
  `Object::canProduceUpgrade` (`Object.cpp:6244-6260`) only allows
  purchases whose button is in the object's **current** command set —
  which is exactly why the proptower **`ConflictsWith` +
  `CommandSetUpgrade`** exclusivity pattern works and is mirrored here.

## Coverage roster (button at slot 9 everywhere)

| Vehicle (object) | Mounting | Exclusivity / notes |
|---|---|---|
| **Battlemaster** `Tank_ChinaTankBattleMaster` | existing HelixContain rider slot (china-bunkers/proptower bay; infantry-only passenger list) | **3-way exclusive rider**: PDL × prop tower × ERA plates. Pod OCU `ConflictsWith = Upgrade_TankLightArmor Upgrade_ChinaOverlordPropagandaTower`; the tower OCU gains `Tank_Upgrade_KwaiPDL` in its ConflictsWith; two new CommandSetUpgrades swap to `…CommandSetPDL` (tower button hidden) / `…CommandSetTower` (PDL hidden); the existing ERA set (neither button) is unchanged. If ERA research completes after a pod is mounted, the cosmetic ERA plate rider is skipped on that tank but the ERA stat boosts still apply (proptower precedent). |
| **Emperor** `Tank_ChinaTankEmperor` | existing HelixContain (emperor-bunker bay) rider slot | **Bay reduced 10 → 8 seats** (per request) to free exit-cameo slot 9 for the button — taunt, gattling, Evacuate and all sibling buttons keep their slots; 7 exit cameos remain for 8 seats (occupant 8 uses Evacuate — same accepted overflow as emperor-bunker's original 10/8). **2-way exclusive rider**: PDL × gattling cannon, same ConflictsWith + CommandSetUpgrade pair (`…EmperorPDLCommandSet` / `…EmperorGattlingCommandSet`). Shtora, propaganda tower, doctrine armor tiers, 1320 HP all byte-preserved. |
| **Gattling Tank** `Tank_ChinaTankGattling` | new minimal HelixContain bay | + ProductionUpdate |
| **Dragon Tank** `Tank_ChinaTankDragon` | new bay | + ProductionUpdate. Its command sets were **vanilla-shared** (`ChinaTankDragon*CommandSet`, also used by vanilla China's Dragon + a CINE object) — **cloned to `Tank_…` names** with the button, Kwai's Dragon repointed (2 refs incl. the Black Napalm CommandSetUpgrade); the vanilla sets are byte-untouched, so no Dragon spillover. |
| **ECM Tank** `Tank_ChinaTankECM` | new bay | + ProductionUpdate. Stacks jamming + hard-kill. |
| **Reaper** `Tank_ChinaReaperTank_Real` | **OverlordContain → HelixContain swap** (emperor-bunker precedent; all existing fields are valid TransportContain fields) | The armor-addon rider (`ChinaTankArmorUpgradeAddon_Reaper`, granted **at spawn** via GrantUpgradeCreate) keeps the dedicated rider slot; the pod rides the **single passenger seat** (`Slots = 1`, allow-list `PORTABLE_STRUCTURE`). Enclosed passengers are position-synced (`containReactToTransformChange` → `redeployOccupants`) and enclosed modules still run (the jammer donor scans while contained). No exclusivity needed. Its `GenericCommandSet` (shared by dozens of objects) is **cloned** to `Tank_ChinaReaperCommandSet` and only the Reaper repointed. + ProductionUpdate. |
| **WarMaster** `Tank_ChinaTankWarMaster` | new bay | ProductionUpdate already present |
| **JS-7** `Tank_ChinaTankJS7` | new bay | + ProductionUpdate. Its chaos-units `RussianTankGolemCommandSet` is used only by the JS-7 — patched in place. |
| **Command Tank** `Tank_ChinaTankCommandTank` | new bay | ProductionUpdate already present. Button on the **main** page only (slot 9); the Generals-Abilities page flip is untouched — flipping away mid-queue is harmless (validity is checked at queue time). |
| **Nuke Cannon** `ChinaVehicleNukeLauncher` (SHARED vanilla object; kwai-artillery stub builds it) | new bay | ProductionUpdate already present (warhead switching). **Spillover**: vanilla China (and anyone owning this exact object) also gets the working purchase — pre-approved, see below. |
| **Inferno Cannon** `ChinaVehicleInfernoCannon` (SHARED vanilla) | new bay | + ProductionUpdate. Both command-set variants (Black Napalm state) get the button. Spillover as above. |
| **Hammer Cannon** `Spec_ChinaVehicleNukeLauncher` (SHARED Leang donor; kwai-roster stub builds it) | new bay | ProductionUpdate already present. Spillover to Leang. |
| **Buratino / TOS-1** `Spec_ChinaVehicleInfernoCannon` (SHARED Leang donor) | new bay | + ProductionUpdate. Spillover to Leang. |

### Skipped units (and why)

- **Overlord** (`ChinaTankOverlord`, roster stub): its OverlordContain
  rider slot *is* the unit's core three-way turret choice
  (bunker/gattling/speaker) on a vanilla-shared object — adding a fourth
  mutually-exclusive rider would rewire the vanilla Overlord's signature
  mechanic for every China player. Out of scope.
- **Scout Car** (`Tank_ChinaVehicleScoutCar`): $100 recon/taxi, not a
  combat vehicle.
- **Transports / dozers / supply** (Troop Crawler, Dozer, Supply Truck,
  Hacker Van, Listening Outpost) and **aircraft** (MiGs, Helix, UAV):
  per spec.
- **Command Tank powers page / Emperor ERA set** etc. carry no button by
  design (state sets where the pod can no longer be bought).

## Spillover (documented, pre-accepted)

- The four artillery objects are **shared donors**: any player who owns
  the same object (vanilla China's own Nuke/Inferno cannons, Leang's
  Hammer/TOS via her own build buttons) sees and can use the $500 PDL
  purchase. The pod object itself is `Side = ChinaTankGeneral` but works
  for whoever owns the host (standard cross-side reuse, proptower
  precedent).
- `CINE_ChinaVehicleNukeLauncher` / `CINE_…InfernoCannon` /
  `CINE_ChinaTankDragon` (campaign cinematic props) share the artillery
  sets → they'd show a permanently-greyed button if ever selectable in a
  cutscene (they lack the OCU/ProductionUpdate). Cosmetic, campaign-only.
  (The Dragon's *skirmish* sets were cloned precisely so vanilla China's
  playable Dragon does **not** see the button.)
- **Siege Soldier**: the patched object is the vanilla
  `ChinaInfantrySiegeSoldier` — vanilla China players' siege soldiers
  gain garrison rights too. The Nuke and Infantry generals' siege
  soldiers are **separate objects in separate files and are untouched**
  (asserted post-install) — less spillover than the spec guessed.

## Siege Soldier: why BOAT had to go too

Removing `NO_GARRISON` only opens `GarrisonContain` buildings
(`GarrisonContain.cpp:567` is the sole logic-side check). But ShockWave
also flags the soldier **`BOAT`**, and every bunker/tank bay in this
stack (china-bunkers Battlemasters, emperor-bunker, mammoth-bunker,
kwai-garrisons) carries `ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT` —
the soldier would still be refused from exactly the "bunker bays/tank
bays" the feature names. Removing `BOAT` from an infantryman is benign —
the engine's only other uses of `KINDOF_BOAT` are bomb-truck disguise
targeting (vehicles only), hijack/car-bomb crates (vehicles only) and
GPS-scrambler immunity (he becomes scramblable like all other infantry):
`ActionManager.cpp:1739-1743`, `ThingTemplate.cpp:437`,
`ConvertTo*CrateCollide.cpp`. Documented deviation from the one-flag
spec. (He could already ride Troop Crawlers — their contain has no
forbid list.)

## Files in the archive (21, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZKwaiUAV.big` | 12 slot-9 button lines inserted in place, Emperor exit-cameo 9 → button, **7 sets appended** (BM Tower/PDL, Emperor Gattling/PDL, Dragon ×2, Reaper) |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZZKwaiUAV.big` | +1 button appended |
| `Data\INI\Upgrade.ini` | `zzz-ZZZZZZKwaiUAV.big` | +1 upgrade appended |
| `Data\INI\ObjectCreationList.ini` | `zzz-ZZZZZZKwaiUAV.big` | +1 OCL appended |
| `Data\INI\Weapon.ini` | `zzz-ZZZZChaosUnits.big` | +1 weapon appended |
| `Data\Generals.str` | `zzz-ZZZZZZKwaiUAV.big` | +4 string entries appended |
| `…\Tank\Vehicles\PDLPod.ini` | **new file** | the pod |
| `…\Tank\Vehicles\BattleMaster.ini` | `zzz-KwaiDoctrine.big` | tower-OCU ConflictsWith extended; +OCU +2 CommandSetUpgrades |
| `…\Tank\Vehicles\Emperor.ini` | `zzz-ZZZZChaosUnits.big` | bay Slots 10→8; gattling-OCU +ConflictsWith; +OCU +2 CommandSetUpgrades |
| `…\Tank\Vehicles\GattlingTank.ini` | `zzz-KwaiDoctrine.big` | +bay +OCU +ProductionUpdate |
| `…\Tank\Vehicles\DragonTank.ini` | `zzz-KwaiDoctrine.big` | +bay +OCU +ProductionUpdate; 2 set refs repointed to the clones |
| `…\Tank\Vehicles\ECMTank.ini` | `zzz-KwaiDoctrine.big` | +bay +OCU +ProductionUpdate |
| `…\Tank\Vehicles\Reaper.ini` | `zzz-KwaiDoctrine.big` | OverlordContain→HelixContain; set repointed to clone; +OCU +ProductionUpdate |
| `…\Tank\Vehicles\WarMaster.ini` | `zzz-KwaiDoctrine.big` | +bay +OCU |
| `…\Tank\Vehicles\JS7.ini` | `zzz-ZZZZChaosUnits.big` | +bay +OCU +ProductionUpdate |
| `…\Tank\Vehicles\CommandTank.ini` | `zzz-ZZZZChaosUnits.big` | +bay +OCU |
| `…\Vanilla\Vehicles\NukeCannon.ini` | `zzz-KwaiDoctrine.big` | +bay +OCU |
| `…\Vanilla\Vehicles\InfernoCannon.ini` | `zzz-KwaiDoctrine.big` | +bay +OCU +ProductionUpdate |
| `…\SpecialWeapons\Vehicles\HammerCannon.ini` | `zz_SPE_Shw_ini.big` | +bay +OCU |
| `…\SpecialWeapons\Vehicles\Buratino.ini` | `zz_SPE_Shw_ini.big` | +bay +OCU +ProductionUpdate |
| `…\Vanilla\Infantry\SiegeSoldier.ini` | `zz_SPE_Shw_ini.big` | 1 KindOf line: `NO_GARRISON` + `BOAT` removed |

## Build-time verification (all enforced; build fails loudly otherwise)

- Effective-file ownership asserted per patched + donor file; the new
  pod INI path asserted unclaimed in every archive of both dirs; all 22
  new identifiers word-boundary collision-checked across the whole
  effective INI space (890 files).
- **Donor drift guards** re-asserted each build: Avenger PDL weapon
  shape (damage/range/rate/beam/bone/FX) + module (target types, scan
  200), the BlackShark jammer rider (PORTABLE_STRUCTURE, Model NONE,
  PDL module, SMALL_MISSILE), the jammer mount chain
  (OCL `ContainInsideSourceObject`, $500 OBJECT upgrade), and the laser
  beam object with its two particle systems.
- **Exact line-level diff audits on all 14 modified vehicle/infantry
  files** (added/removed line multisets must match the plan exactly — the
  strongest sibling-survival guarantee: doctrine armor tiers, chaos
  Shtora/JS7/CommandTank hunks, emperor-bunker bay, china-tank-buff HPs,
  proptower/ERA modules, roster stubs, warhead-switch machinery all
  byte-survive) + append-only base-byte identity for the 5 appended
  files + block-balance (End-count) deltas per file.
- Command-set survival on shipped **and installed** bytes: exact
  expected layouts for all 19 touched/cloned sets **and** the
  deliberately-untouched shared sets (vanilla Dragon ×2,
  GenericCommandSet); kwai-uav IC clones (research 7 / deploy 8 /
  Evacuate 9) + vanilla IC sets; all 50 prop-center sets full 14/14;
  roster WF page 2 / Barracks 5 / Airfield 3–4 + exits; artillery
  Inferno at WF 11 + page arrows; mammoth-bunker stems; dozer pages +
  Hacker Bunker; ≥60 Evacuates; vanilla China prop-center untouched.
- Cross-reference closure: button ↔ upgrade ↔ OCL ↔ pod ↔ weapon ↔ beam
  object ↔ FX ↔ pulse sound ↔ particles ↔ cameo ↔ strings; exactly one
  ProductionUpdate per host; every button in every touched set resolves
  to a CommandButton; the pod asserted to carry **no VeterancyBoost**.
- Sort position verified against the real listings of both mod dirs
  (incl. a probe that a future `zzz-ZZZZZZZRotrInfantry.big` sorts
  after us); installed archives re-read and byte-compared; an
  independent post-install audit recomputed the whole effective space
  in both dirs (ownership of all 21 files, effective content of every
  host, Nuke/Infantry siege soldiers untouched); rebuild is idempotent
  (hash-stable, self-archive excluded from sourcing).
  **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive), patches, verifies, writes `zzz-ZZZZZZZKwaiPDL.big`
here and installs to both mod dirs. Depends on
`../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer** (after
kwai-uav). If any lower layer is rebuilt (kwai-uav, kwai-roster,
chaos-units, kwai-garrisons, kwai-basetech, kwai-bunkers, kwai-doctrine,
emperor-bunker, kwai-artillery, stat-tune, …), rebuild this archive
afterwards — it embeds full copies of their files. Conversely, lower
layers' builds must not see this archive: delete
`zzz-ZZZZZZZKwaiPDL.big` from both mod dirs first, rebuild the lower
chain in its documented order (… → kwai-roster → kwai-uav), then rerun
this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZKwaiPDL.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZKwaiPDL.big`

## Uninstall

Delete `zzz-ZZZZZZZKwaiPDL.big` from both directories above. No other
files are touched.

## Notes / accepted limitations / balance

- **VeterancyBoost follow-up**: the pod deliberately ships without any
  veterancy coupling — the engine patch adding a `VeterancyBoost` field
  to `PointDefenseLaserUpdate` is not deployed yet. When it lands, a
  follow-up layer adds the field to `Tank_ChinaPDLPod`'s module (one
  line in `PDLPod.ini`).
- **Interception profile**: one beam per pod, 100 LASER damage per
  800 ms, 100 fire range / 160 scan radius, SMALL_MISSILE only — one pod
  reliably eats a rocket every 0.8 s; saturation volleys (Tomahawk
  batteries, rocket-buggy swarms) overwhelm singles but massed pods
  stack per vehicle. SCUDs/ballistic missiles are NOT intercepted
  (spec). Stealth missiles (none in practice) would be skipped until
  detected; friendly fire is impossible (relationship check).
- The purchase is once-per-vehicle, not refundable/removable; after
  purchase the button shows as already-produced (except where an
  exclusivity CommandSetUpgrade removes it, or on the Battlemaster once
  ERA research swaps every BM to the ERA set — pods already mounted
  keep working, only the button disappears).
- **Emperor bay is now 8 seats** (was 10; user-approved reduction) with
  7 individual exit cameos; Evacuate still empties everyone.
- Exclusivity races (buying the PDL the same instant the contested
  upgrade completes) can waste $500 — the ConflictsWith module refuses
  the second rider and the OCL payload is destroyed cleanly. One-frame
  window, unavoidable without engine changes.
- The beam originates at the host's hull center (no `LaserBoneName`) —
  cosmetically fine, the Avenger's beam bone is Avenger-specific.
- The pod grants no vision, no stealth detection, no XP: missiles killed
  by point-defense yield no experience (donor behavior).
- Container pips: hosts that gained a bay may show a 1-slot container
  pip once a pod is mounted; the pod never appears on exit/evacuate
  buttons (rider slot) — on the Reaper it sits enclosed in the single
  passenger seat and its set has no exit buttons.
- AI never buys pods (no AI scripting; object upgrades are player-only
  purchases). Siege-soldier garrisoning works for AI-scripted garrison
  actions too (the script-side NO_GARRISON check now passes).
- Save games crossing an install/uninstall boundary may not load
  (module lists changed on 13 vehicle objects + a new object type).
  Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the engine source (GeneralsX GeneralsMD tree) and the
  installed bytes.
