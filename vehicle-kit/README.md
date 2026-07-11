# Vehicle Kit (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Two
features for **Kwai (China Tank General)**:

1. **2-seat fire-out infantry bays** on the Gattling Tank, the Kwai Scout
   Car clone and **all four artillery pieces** Kwai builds (Nuke Cannon,
   Inferno Cannon, Hammer Cannon, Buratino/TOS-1 — shared donor objects,
   spillover documented below).
2. **Coaxial machine guns** for the remaining tanks, reusing the **proven
   hitscan `ShwBattleMasterCoaxMGWeapon`** from the battlemaster-coax layer
   (the weapon carries **no `ProjectileObject`** — the earlier projectile
   version fired visible ballistic arcs; drift-guarded at build time so a
   regression in that layer fails this build).

Output archive: **`zzz-ZZZZZZZVehicleKit.big`** (10 files, all INI — no new
art, audio, strings, weapons or objects). Case-insensitively
`zzz-zzzzzzzveh…` sorts **after** `zzz-ZZZZZZZTTeslaCoil.big` (`v` > `t` at
char 12; tesla-coil owns the CommandSet.ini this layers on), **before**
`zzz-ZZZZZZZVetInsignia.big` (`veh` < `vet` — that layer ships only its own
insignia art, verified to claim none of our paths) and **before**
`zzz_ControlBarPro*.big` (`-` 0x2D < `_` 0x5F) — checked against the real
directory listings of both mod dirs at build time. This is now the **last
INI layer**.

## Feature 1 — infantry bays

Bay fabric (the china-bunkers BattleMaster bay idiom): `HelixContain`,
`Slots = 2`, `DamagePercentToUnits = 0%`, `AllowInsideKindOf = INFANTRY`,
`ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT`, garrison enter/exit sounds,
`PassengersAllowedToFire = Yes`, 1 exit path.

### The PDL merge (one contain per object)

kwai-pdl already gave the Gattling Tank and all four artillery a minimal
`HelixContain` **PDL-pod rider seat** (`Slots = 1`, PORTABLE_STRUCTURE
only). An object has **one** contain module, so that module was **extended
in place**, not duplicated: the PDL pod mounts into HelixContain's
**dedicated PORTABLE_STRUCTURE rider slot**
(`HelixContain.cpp` `addToContain`/`isValidContainerFor` — the first
PORTABLE_STRUCTURE bypasses `AllowInsideKindOf` and the `Slots` count, and
never appears on exit/evacuate buttons). Both infantry seats therefore stay
free and the **$500 PDL purchase co-exists with garrisoned infantry** —
asserted every build. `Command_Evacuate` also cannot eject the pod: the
rider is stored outside the contained-items list.

| Unit (object) | Bay | Command set changes |
|---|---|---|
| **Gattling Tank** `Tank_ChinaTankGattling` | PDL seat extended | `Tank_ChinaVehicleGattlingTankCommandSet`: exits at **7–8**, Evacuate at **10** (12 is `Command_GuardFlyingUnitsOnly`) |
| **Scout Car** `Tank_ChinaVehicleScoutCar` (kwai-roster clone) | **new** bay (`ModuleTag_VKitBay01` — the scout had no contain and no PDL) | vanilla-shared `ChinaVehicleBullfrogCommandSet` **cloned** to `Tank_ChinaVehicleScoutCarCommandSet` (kwai-pdl Dragon/Reaper precedent) with exits 7–8 + Evacuate 12; the scout repointed; vanilla China's scout set untouched. **Vision untouched** (450/500 stays — a queued economy layer owns it). |
| **Nuke Cannon** `ChinaVehicleNukeLauncher` (SHARED vanilla; kwai-artillery stub builds it) | PDL seat extended | `ChinaVehicleNukeCannonCommandSet`: exits 7–8, Evacuate 12 |
| **Inferno Cannon** `ChinaVehicleInfernoCannon` (SHARED vanilla) | PDL seat extended | both warhead-state sets (`…InfernoCannonCommandSet` / `…UpgradedCommandSet`): exits 7–8, Evacuate 12 |
| **Hammer Cannon** `Spec_ChinaVehicleNukeLauncher` (SHARED Leang donor) | PDL seat extended | `ChinaVehicleHammerCannonCommandSet`: exits 7–8, Evacuate 12 |
| **Buratino / TOS-1** `Spec_ChinaVehicleInfernoCannon` (SHARED Leang donor) | PDL seat extended | `ChinaVehicleTOSCommandSet`: exits 7–8, Evacuate 12 |

Slots 7–8 were free in **every** covered set (kwai-pdl's button owns slot 9
everywhere; warhead/hold-fire/ability buttons own 1–6; 11/13/14 are
AttackMove/Guard/Stop) — occupancy asserted per set before insertion;
nothing sibling-owned was moved or sacrificed.

The **Emperor's bay is untouched** (8 seats, exits 2–8, Evacuate 12 — the
kwai-pdl state stands).

### Spillover (documented, pre-accepted — same sets/objects as kwai-pdl)

- The four artillery objects are shared donors: vanilla China's own
  Nuke/Inferno cannons and Leang's Hammer/TOS get the working 2-seat bay
  and the exit/Evacuate buttons too (exactly the units that already show
  the kwai-pdl button at slot 9).
- `CINE_ChinaVehicleNukeLauncher` / `CINE_…InfernoCannon` (campaign
  cinematic props defined separately in `ChinaMisc.ini`) share the
  artillery command sets but are **separate objects without the bay
  module** — their exit buttons stay hidden (no contain) and Evacuate is
  inert; cosmetic, campaign-only (the kwai-pdl slot-9 button precedent).
- The Scout Car set was cloned precisely so vanilla China's scout car sees
  **no** spillover.

## Feature 2 — coaxial machine guns

The weapon: `ShwBattleMasterCoaxMGWeapon` **reused by reference** (defined
once by the battlemaster-coax layer; 20 dmg SMALL_ARMS, 165 range, 65 ms /
30-round clip / 5 s reload / 2 s pre-aim, hitscan tracers). No clone, no
Weapon.ini changes. All three hosts' cannons out-range it
(Emperor/Overlord 192.5, WarMaster 176), so it never extends engagement
range.

Engine facts that shaped the scheme (GeneralsX GeneralsMD tree, asserted
as drift guards where load-bearing):

- **3 weapon slots only** (`WeaponSet.h`: PRIMARY/SECONDARY/TERTIARY).
- `WeaponSetUpgrade.cpp:56` hard-codes **WEAPONSET_PLAYER_UPGRADE** — it is
  the *only* upgrade-driven weapon-set flag, so a "$300 purchasable coax"
  requires that flag to be free on the unit.
- Weapon-set matching is best-effort (`SparseMatchFinder.h`
  `findBestInfoSlow`): a unit whose only set is `Conditions =
  PLAYER_UPGRADE` uses it whether or not the flag is set (the WarMaster
  case).
- `PreferredAgainst` weapons all tie at `HUGE_DAMAGE` and **ties go to the
  lowest slot** (`WeaponSet.cpp` `chooseBestWeaponForTarget`) — so a
  cannon carrying `PreferredAgainst … INFANTRY` would keep a TERTIARY coax
  permanently unselected. Where a cannon had that preference it was
  **moved to the coax** (Emperor None-set, Overlord both sets).
- `ShareWeaponReloadTime = Yes` propagates **every** weapon's next-shot
  frame and status to **all** slots in the set (`Weapon.cpp`
  `reloadWithBonus` ≈1994, `privateFireWeapon` ≈2753,
  `onWeaponBonusChange` ≈2057) — the Command Tank blocker, see below.

### Per-unit outcomes (after re-verifying every flag and slot)

| Unit | Outcome | Finding |
|---|---|---|
| **Emperor** `Tank_ChinaTankEmperor` | **INNATE**, `None` set only | TERTIARY free in the `None` set (PRIMARY targeting dummy, SECONDARY cannon) — coax added there with `PreferredAgainst = TERTIARY INFANTRY` (the cannon's INFANTRY preference moved to it). **Deviation from the spec's "both sets"**: the `PLAYER_UPGRADE` set is **full** — its TERTIARY is `Tank_GattlingBuildingGunAirDummy`, the manual anti-air targeting dummy for the $1200 mounted gattling turret. Once the gattling rider is bought the coax is superseded by the turret (which shreds infantry anyway); sacrificing manual AA was not acceptable. |
| **WarMaster** `Tank_ChinaTankWarMaster` | **INNATE** (fallback) | PLAYER_UPGRADE flag **TAKEN**: ERA research (`Upgrade_TankLightArmor` → `WeaponSetUpgrade ModuleTag_Armor_02`) flips it for the `WEAPONSET_PLAYER_UPGRADE` armor-plate draw states. A $300 purchase on that flag would hand every WarMaster a free coax at ERA research and sprout phantom ERA plates on coax buyers. Its **single** weapon set (always selected) gains the TERTIARY coax + INFANTRY preference. |
| **Overlord** `ChinaTankOverlord` (vanilla-shared) | **INNATE** (fallback), **both** sets | Flag **TAKEN** by the per-unit gattling-turret purchase (`WeaponSetUpgrade ModuleTag_WeaponSetUpgrade01` ← `Upgrade_ChinaOverlordGattlingCannon`). TERTIARY is free in **both** sets (the PLAYER_UPGRADE set's SECONDARY is the manual-AA dummy), so the coax rides both and survives every turret choice (bunker/gattling/speaker riders unaffected — they are contain riders). Cannon's `PreferredAgainst = PRIMARY INFANTRY` moved to the coax in both sets. **Spillover: every ChinaTankOverlord owner** (vanilla China incl. Kwai's roster stub) gets the coax — pre-approved. |
| **Dragon** `Tank_ChinaTankDragon` | **NO COAX** (fallback ladder exhausted) | Flag TAKEN (Black Napalm `WeaponSetUpgrade ModuleTag_05`) **and all 3 slots full in both sets** (flame / firewall ability / napalm-puddle ability — the latter two are button-driven `AutoChooseSources = NONE` weapons that cannot be dropped). Not even an innate coax fits. File not shipped; asserted to stay coax-free post-install. Its flame weapon is already the anti-infantry tool. |
| **Command Tank** `Tank_ChinaTankCommandTank` | **NO COAX** (engine blocker, documented) | **Flag FREE and TERTIARY free** — the purchasable idiom *looked* viable. But the APFSDS/HESH switch set carries `ShareWeaponReloadTime = Yes` (with `LockWeaponCreate` + `SWITCH_WEAPON` buttons; sharing exists to stop switch-toggle reload skipping). The engine stamps every firing weapon's next-shot frame onto **all** weapons in the set: a 65 ms coax would overwrite the cannons' **10 s** cycle with ready-in-65 ms (a 3–5× DPS exploit on a $2500 hero unit), and each 5 s coax clip reload would randomly jam the cannons. An **innate** coax is equally affected, so the unit is skipped entirely. The blocker facts (shared reload present, no WeaponSetUpgrade, 10 s cannon clip) are asserted each build — if chaos-units ever drops the shared reload, the build fails and the decision re-opens. |
| **JS-7** | **SKIPPED** per spec | has its own MG. |

**Net result: no unit qualified for the "$300 — Coaxial Machine Gun"
OBJECT_UPGRADE + WeaponSetUpgrade idiom** (the two flag-free candidates
were blocked by slot occupancy / shared-reload). The archive therefore
ships **no** Upgrade entries, no CommandButtons, no Generals.str changes —
feature 2 is pure WeaponSet text on three object files.

### Coax × PDL co-purchasability (user requirement)

The coax is innate weapon-set text; the PDL pod is a contain-rider OCL —
different mechanisms with no shared state. Verified each build: **no
`ConflictsWith` is added anywhere** (in either direction), the PDL pod
object carries no weapon-set machinery (`WeaponSetUpgrade` /
`GrantUpgradeCreate` / `ConflictsWith` all absent from `PDLPod.ini`), and
the pod's OCL only does `ContainInsideSourceObject`. A pod-equipped
Emperor/WarMaster/Overlord keeps its coax; a coax host can buy the pod.
Existing rider exclusivities (Emperor gattling × PDL, Battlemaster
tower × PDL × ERA) are byte-untouched.

### Cosmetic notes

- None of the three hosts declares TERTIARY fire-FX bones — the MG muzzle
  flash/tracers render from the hull position (the battlemaster-coax
  "bone fallback" precedent; on the Nuke Battlemaster that layer already
  accepted cannon-muzzle tracers).
- The coax slot is not in any turret's `ControlledWeaponSlots`
  (deliberately untouched), so hosts aim it by rotating the hull — exactly
  how the Emperor/Overlord manual anti-air dummy already behaves.

## Files in the archive (10, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZTTeslaCoil.big` | 18 lines inserted (6 sets × exits 7–8 + Evacuate), 1 cloned set appended, 0 removed |
| `…\China\Tank\Vehicles\Emperor.ini` | `zzz-ZZZZZZZKwaiPDL.big` | None-set: +TERTIARY coax, INFANTRY preference moved; PLAYER_UPGRADE set byte-identical |
| `…\China\Tank\Vehicles\WarMaster.ini` | `zzz-ZZZZZZZKwaiPDL.big` | single set: +TERTIARY coax + preference |
| `…\China\Vanilla\Vehicles\Overlord.ini` | `zzx_ChinaTankBuff.big` | both sets: +TERTIARY coax, preference moved |
| `…\China\Tank\Vehicles\GattlingTank.ini` | `zzz-ZZZZZZZKwaiPDL.big` | PDL seat → 2-seat fire-out bay |
| `…\China\Tank\Vehicles\ScoutCar.ini` | `zzz-ZZZZZKwaiRoster.big` | +new bay module; set repointed to the clone |
| `…\China\Vanilla\Vehicles\NukeCannon.ini` | `zzz-ZZZZZZZKwaiPDL.big` | PDL seat → bay |
| `…\China\Vanilla\Vehicles\InfernoCannon.ini` | `zzz-ZZZZZZZKwaiPDL.big` | PDL seat → bay |
| `…\China\SpecialWeapons\Vehicles\HammerCannon.ini` | `zzz-ZZZZZZZKwaiPDL.big` | PDL seat → bay |
| `…\China\SpecialWeapons\Vehicles\Buratino.ini` | `zzz-ZZZZZZZKwaiPDL.big` | PDL seat → bay |

New identifiers: **one** (`Tank_ChinaVehicleScoutCarCommandSet`),
collision-checked against all 899 effective INI files.

## Build-time verification (all enforced; build fails loudly otherwise)

- Effective ownership asserted for all 10 sourced files; the single new
  identifier collision-checked; sort position + "no later archive claims
  any path we ship" (covers VetInsignia + ControlBarPro) against the real
  listings of both dirs.
- **Scheme re-verification as drift guards**: Emperor PLAYER_UPGRADE set
  still full (air dummy on TERTIARY); WarMaster flag still taken by ERA
  and still single-set; Overlord flag still taken by the gattling
  purchase with TERTIARY free ×2; Dragon still full+taken; Command Tank
  still `ShareWeaponReloadTime = Yes` + flag free + 10 s cannon clip. Any
  drift re-opens the corresponding decision.
- Coax weapon drift guard: the effective `ShwBattleMasterCoaxMGWeapon` must
  stay hitscan (**no `ProjectileObject`**, 165 range, SMALL_ARMS, 65 ms).
- PDL coexistence: pod INI free of weapon-set machinery; **zero
  `ConflictsWith` lines added by this layer** (diff-checked).
- Exact line-level diff audits on **all 10 files** (added/removed line
  multisets must match the plan exactly — doctrine armor tiers, Shtora,
  prop modules, PDL mount OCUs + exclusivity CommandSetUpgrades, Emperor
  8-seat bay, warhead machinery, roster vision buff all byte-survive) +
  block-balance deltas (CommandSet +1 End, ScoutCar +1, others 0) + exactly
  one contain module per touched object.
- Cross-reference closure: every slot of every touched/cloned set resolves
  to an effective CommandButton; garrison sounds + coax weapon exist
  effectively.
- Sibling survival on shipped **and installed** bytes: tesla-coil dozer
  page-2 slot 9 + coil set, kwai-pdl's 17 slot-9 buttons + Emperor 9/10 +
  PDL/Gattling exclusivity sets + Dragon set clones, infantry Barracks
  5–8 (both variants), roster WF page 2 (JS7/ScoutCar), artillery WF 11–12,
  doctrine's 50 propaganda-center sets, kwai-uav IC sets, kwai-bunkers
  dozer pages + Hacker Bunker, Gattling Cannon defense set, ≥60 Evacuates,
  and the untouched vanilla-shared sets (Bullfrog, vanilla Dragon,
  Overlord default, Nuke general's cannon set, GenericCommandSet) frozen.
- Post-install effective-space audit in **both** dirs: our archive owns
  exactly the 10 shipped paths with exact bytes; CommandButton/Weapon/
  Generals.str stay tesla-owned, Upgrade.ini infantry-owned, PDLPod +
  DragonTank + CommandTank stay kwai-pdl-owned (and provably coax-free),
  vanilla ScoutCar keeps the Bullfrog set and no contain.
- Installed archives re-read and byte-compared; rebuild is
  **hash-idempotent** (verified). **The game was deliberately not
  launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding its
own archive), patches, verifies, writes `zzz-ZZZZZZZVehicleKit.big` here
and installs to both mod dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer** (after
tesla-coil). If any lower INI layer is rebuilt (tesla-coil, kwai-infantry,
kwai-pdl, kwai-uav, kwai-roster, chaos-units, kwai-garrisons, kwai-basetech,
kwai-bunkers, kwai-doctrine, emperor-bunker, kwai-artillery, stat-tune,
china-tank-buff, …), rebuild this archive afterwards — it embeds full
copies of their files (CommandSet.ini from tesla-coil, 7 vehicle files from
kwai-pdl, ScoutCar from kwai-roster, Overlord from china-tank-buff).
Conversely, lower layers' builds must not see this archive: delete
`zzz-ZZZZZZZVehicleKit.big` from both mod dirs first, rebuild the lower
chain in its documented order (… → kwai-pdl → kwai-infantry → tesla-coil),
then rerun this build. (`zzz-ZZZZZZZVetInsignia.big` is disjoint and
order-independent.)

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZVehicleKit.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZVehicleKit.big`

## Uninstall

Delete `zzz-ZZZZZZZVehicleKit.big` from both directories above. No other
files are touched.

## Known limitations / risks / balance

- **No $300 purchasable coax shipped** — every candidate fell to a
  verified blocker (see the outcome table). If a future layer frees a
  flag (e.g. chaos-units drops the Command Tank's shared reload), the
  build's drift guards will flag it.
- **Emperor loses the coax when the $1200 gattling turret is mounted**
  (PLAYER_UPGRADE set has no room) — the gattling rider is the better
  anti-infantry weapon, so this reads as an upgrade, but the MG tracers
  stop.
- **Overlord spillover**: vanilla China's Overlords (any general using the
  shared object) gain the innate coax and now strafe infantry with the MG
  instead of cannon-sniping them — a behavior change for non-Kwai China
  (the MG out-damages the cannon vs infantry; the cannon keeps splash for
  force-fire on ground).
- Artillery-bay spillover mirrors the kwai-pdl button spillover: vanilla
  China and Leang get working bays on the shared artillery.
- Infantry firing from inside a bay shoot from the vehicle's hull position
  (TransportContain fire-point behavior, emperor-bunker precedent);
  passengers are safe from splash (`DamagePercentToUnits = 0%`) but die
  with the vehicle. Missile-armed passengers (tank hunters) will fire out;
  the bay forbids nothing about who shoots.
- The coax is hull-aimed (not turret-controlled) and its FX render from
  the hull center — cosmetic, precedent-accepted.
- Bays add container pips under the health bar; exit buttons show only
  while the matching seat is occupied. The PDL pod never appears on
  exit/Evacuate buttons and cannot be dismounted (rider slot).
- AI never garrisons the new bays on its own (no AI script changes);
  player-facing.
- Save games crossing an install/uninstall boundary may not load (module
  lists changed on 6 vehicles + weapon sets on 3 more). Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX engine source
  (GeneralsMD tree).

## CHANGELOG

- **2026-07-10 — kwai-infantry v2 chain rebuild** (performed by the
  kwai-infantry session): kwai-infantry removed its ZHE Sharpshooter port.
  `build.py` edits: (1) post-install owner expectation for
  `Data\INI\Upgrade.ini` reverted from `zzz-ZZZZZZZLKwaiInfantry` to
  `zzz-ZZZZZZZKwaiPDL` (kwai-infantry no longer ships it); (2) sources now
  read ONLY from archives sorting strictly below this one; (3) the "no
  later archive claims a shipped path" check and the post-install
  effective-space audit skip `zzz-ZZZZZZZWEconomy.big` (REBUILT_AFTER —
  it layers on our CommandSet/ScoutCar and is rebuilt right after us).
  Archive rebuilt (on top of the rebuilt tesla-coil) and reinstalled to
  both mod dirs; all original assertions green.
