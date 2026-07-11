# Kwai UAV (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Gives
**Kwai (China Tank General)** a researchable **UAV Surveillance Program**
and, once researched, a deployable **Surveillance UAV**: target any
location on the map and a stealthy recon drone spawns above it and
loiters there, providing vision and stealth detection until it is
destroyed.

Output archive: **`zzz-ZZZZZZKwaiUAV.big`** (8 files, INI + strings —
all art/sounds are live donor references). Case-insensitively
`zzz-zzzzzz…` sorts **after** `zzz-ZZZZZKwaiRoster.big` (`z` > `k` at
character 9; roster owns the CommandSet.ini / CommandButton.ini this
layers on) and `-` (0x2D) < `_` (0x5F) sorts it **before**
`zzz_ControlBarPro*.big` — verified against the real directory listings
of both mod dirs at build time. This is now the **last INI layer**.

## What you get

| Piece | Where | Cost / numbers |
|---|---|---|
| **UAV Surveillance Program** (one-shot `Type = PLAYER` upgrade) | **Internet Center slot 7** | $1000 / 30 s |
| **Deploy Surveillance UAV** (special power, player-targeted anywhere on the map) | **Internet Center slot 8** (greyed until researched) | free per use, **120 s shared reload** |
| **Surveillance UAV** (`Tank_ChinaSurveillanceUAV`) | spawns 300 units above the click, descends and loiters | 200 HP, unarmed, **innately stealthed**, **detects stealth**, VisionRange **350**, dynamic shroud clearing to **400**, **permanent until killed** |

## Donor mechanism (researched first, reused wholesale)

The vanilla/ShockWave **USA Spy Drone** is live in ShockWave
(`SCIENCE_SpyDrone` purchase + `Command_SpyDrone` on every USA command
center), so every asset in its chain ships and resolves:

- `SpecialPower SpecialPowerSpyDrone` (Enum `SPECIAL_SPY_DRONE`, reload
  150 s, `RadiusCursorRadius` aligned with the drone's vision) is fired
  by an **`OCLSpecialPower`** module on the USA command centers with
  `OCL = SUPERWEAPON_SpyDrone` and **`CreateLocation =
  CREATE_ABOVE_LOCATION`** (engine: spawns the OCL 300 above the click,
  `OCLSpecialPower.cpp:213-217`).
- The OCL creates **`AmericaVehicleSpyDrone`** ("Global Hawk",
  `Object\USA\Vanilla\Aircraft\SpyDrone.ini`): unarmed, 200 HP,
  `StealthUpdate` (innate stealth, revealed while taking damage),
  `StealthDetectorUpdate`, `DynamicShroudClearingRangeUpdate`
  (FinalVision 250), **no `LifetimeUpdate`** — permanent until killed.

This is the cleanest existing drone donor: purpose-built for exactly
this power. (ShockWave's `PredatorDrone` is an *armed* strike drone —
wrong flavor.)

### The clone

`Tank_ChinaSurveillanceUAV` (new file
`Data\INI\Object\China\Tank\Aircraft\SurveillanceUAV.ini`) is a
donor-exact clone except **5 changed lines + header comment**
(diff-audited at build time):

- renamed; `Side = America` → `ChinaTankGeneral`; `DisplayName` →
  `OBJECT:TankSurveillanceUAV` ("Surveillance UAV");
- `VisionRange` 250 → **350**; `FinalVision` 250 → **400** (the
  special-power radius cursor is 400 to match, donor comment idiom);
- the donor's drone-armor hooks (`UpgradeCameo1` + `MaxHealthUpgrade`
  on `Upgrade_AmericaDroneArmor`) are **dropped** — Kwai can never
  research that upgrade, so they would be permanently dead weight
  (kwai-roster's Hammer-Cannon-science precedent).

**Lifetime choice (documented): permanent-until-killed**, mirroring the
donor (no `LifetimeUpdate`; engine `LifetimeUpdate.cpp:85-90` would
`kill()` on expiry if we ever wanted a timed drone). Stealth-detection
comes from the donor's `StealthDetectorUpdate` module (there is no
"detector" KindOf in this engine). Everything else — model `AVSpyDr`
(ships in `!ShwW3D.big`), `GlobalHawkLocomtor`, `Genpower_AirplaneArmor`,
sentry-drone voices, `OCL_AmericaScoutDroneExplode` death FX,
`GlobalHawkCommandSet` — is donor-verbatim and asserted present in the
effective data.

## Gating choice + engine evidence

**Chosen: option (b)** — gate the command button / special power
**directly by the upgrade**, with **no `CommandSetUpgrade` anywhere**.
The engine supports this natively, on both the client and logic sides,
and ShockWave itself ships the exact pattern (**GLA Radar Van Scan**,
`Object\GLA\Demo\Vehicles\RadarVan.ini` ModuleTag_06/07 +
`Command_RadarVanScan` — asserted at build time as the living
precedent):

- **Client side** — the deploy button carries `Options = … NEED_UPGRADE`
  + `Upgrade = Tank_Upgrade_KwaiUAVProgram`. Engine
  (GeneralsX GeneralsMD tree): `ControlBarCommand.cpp:1096-1113` — for a
  `UPGRADE_TYPE_PLAYER` template, `player->hasUpgradeComplete(...) ==
  FALSE` → `COMMAND_RESTRICTED` (button visible but greyed;
  `ControlBarCommand.cpp:847-866` maps it to `winEnable(FALSE)`).
- **Logic side** — the IC's new `OCLSpecialPower` has `StartsPaused =
  Yes` (`SpecialPowerModule.cpp:122-125` calls `pauseCountdown(TRUE)` at
  spawn; paused ⇒ `isReady()` is FALSE, `SpecialPowerModule.cpp:310`,
  and even scripted firing early-outs). A companion
  **`UnpauseSpecialPowerUpgrade`** module (`TriggeredBy =
  Tank_Upgrade_KwaiUAVProgram`) calls `pauseCountdown(FALSE)` on the
  matching template when the research completes
  (`UnpauseSpecialPowerUpgrade.cpp:83-94`). The engine header states
  this module exists precisely "so you can have [special powers]
  dependent on upgrades on the logic side, like NEED_UPGRADE does on the
  client side" (`UnpauseSpecialPowerUpgrade.h:27-29`).
- Because the module was *ready* when paused at spawn, unpausing shifts
  `m_availableOnFrame` forward by exactly the paused duration
  (`SpecialPowerModule.cpp:768-792`) — the power is **available
  immediately after research**; the 120 s reload starts on first use.
  `SharedSyncedTimer = Yes` (donor parity): all Internet Centers share
  one reload clock.
- ICs built *after* the research unpause at spawn (the engine re-runs
  upgrade modules for completed player upgrades on newly created
  objects — the same property kwai-doctrine's state machine relies on).

Why not the other options: **(a)** a CommandSetUpgrade pair on the IC
would have entangled the IC's *existing* two-module CommandSetUpgrade
state machine (SatelliteHack × Mines, with `CommandSetAlt`/`TriggerAlt`,
`CommandSetUpgrade.cpp:67-103` last-fired-wins) — adding a third
dimension means enumerating 8 sets and rewriting the trigger fabric.
Option (b) needs zero state sets and has a shipping ShockWave precedent
with the exact same semantics (an upgrade-unlocked, location-targeted
recon scan). The Propaganda Center CommandSetUpgrade machine (50 sets)
is untouched either way — adding a CSU there was forbidden and none was
added anywhere.

## Button placement (and the reported deviation)

**The spec's first choice — Propaganda Center slot 13 — is impossible:
all 50 Kwai prop-center sets are FULL 14/14** (asserted at build time):
1–3 vanilla research, 4–5 kwai-artillery's Chain Guns / Black Napalm,
6–9 kwai-doctrine ladders, 10–11 kwai-basetech, 12 kwai-garrisons
Evacuate, **13 = the per-building Mines/EMP-Mines state slot** (half the
doctrine state machine's reason for existing), 14 = Sell. There is no
free or sacrificeable slot in any of the 50 sets.

**Both buttons therefore live on the Internet Center** — the thematic
surveillance building (satellite hack, hacked spy-satellite scan, and
now the UAV program), Kwai-buildable from dozer page 1, and research +
deploy on one building is cleaner UX anyway.

Kwai's IC used the **vanilla-shared**
`ChinaInternetCenterCommandSet{One,OneUpgrade,Two,TwoUpgrade}` sets —
patching those would leak the buttons (including a purchasable $1000
upgrade!) to vanilla China and Leang. So the four sets are **cloned
verbatim to `Tank_…` names** (appended to CommandSet.ini; the vanilla
sets are byte-untouched) and only Kwai's IC object is repointed (5
references: the `CommandSet =` line + ModuleTag_31/32's
`CommandSet`/`CommandSetAlt` values). In the clones, **garrison-exit
cameos 7–8 become 7 = research / 8 = deploy**:

- slots 7–8 are the only slots identical across all four state sets
  (10/11 swap between the One/Two satellite states), so the buttons
  never move or vanish as the IC changes state;
- exit-cameo sacrifice is the established precedent (kwai-roster
  Airfield 7 → 5 exits; the IC showed 8 exit cameos for stat-tune's 30
  hacker seats anyway); **Evacuate at slot 9 still ejects everyone** —
  you lose only individual-eject cameos for occupants 7+.

IC clone layout: 1–6 exits · **7 UAV Program (research)** · **8 Deploy
UAV** · 9 Evacuate · 10 Satellite Hack 1 / 11 Satellite Scan (state) ·
12 System Hack · 13 Mines/EMP Mines (state) · 14 Sell.

## New INI identities

`Tank_Upgrade_KwaiUAVProgram` (Upgrade) ·
`Tank_Command_UpgradeKwaiUAVProgram` / `Tank_Command_KwaiUAVDeploy`
(CommandButtons) · `Tank_SpecialPowerKwaiUAV` (SpecialPower, Enum
`SPECIAL_SPY_DRONE` — enum sharing between templates is ubiquitous in
ShockWave, e.g. 181 templates share `SPECIAL_COMMUNICATIONS_DOWNLOAD`) ·
`Tank_SUPERWEAPON_KwaiUAV` (OCL) · `Tank_ChinaSurveillanceUAV` (Object) ·
`Tank_ChinaInternetCenterCommandSet{One,OneUpgrade,Two,TwoUpgrade}`
(CommandSets) · `ModuleTag_KUAV_Power01` / `ModuleTag_KUAV_Unpause01`.
All collision-checked (word-boundary) against the whole effective INI
space (889 files).

Deliberate deviations from donor parity on the SpecialPower: **no
`RequiredScience`** (gated by the upgrade instead) and **no
`ShortcutPower`** (a side-bar shortcut would require patching the
vanilla-shared China shortcut command set — leak). The deploy button
drops `NEED_SPECIAL_POWER_SCIENCE` for the same no-science reason.

Cameo: both buttons reuse ShockWave's mapped **`SASienceSpyDrone`**
(spy-drone cameo; UPGRADE vs ACTION border types distinguish them); the
drone keeps donor `SAScout`/`SAScout_L`. No new art, sounds, or textures
anywhere. 6 string entries appended to `Data\Generals.str`
(append-only, base bytes byte-identical). No AI wiring (player-only).

## Files in the archive (8, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZKwaiRoster.big` | +4 Tank_ IC set clones appended (pure append; vanilla sets untouched) |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZKwaiRoster.big` | +2 buttons appended |
| `Data\INI\Upgrade.ini` | `zzz-ZZKwaiBaseTech.big` | +1 Upgrade appended |
| `Data\INI\SpecialPower.ini` | `zzz-ZZZZChaosUnits.big` | +1 SpecialPower appended |
| `Data\INI\ObjectCreationList.ini` | `zzz-ZZZZChaosUnits.big` | +1 OCL appended |
| `Data\Generals.str` | `zzz-ZZZZChaosUnits.big` | +6 string entries appended |
| `…\China\Tank\Buildings\InternetCenter.ini` | `zzz-ZZKwaiBaseTech.big` | 5 set references repointed to the clones; +OCLSpecialPower (StartsPaused) +UnpauseSpecialPowerUpgrade |
| `…\China\Tank\Aircraft\SurveillanceUAV.ini` | new file (clone of `zz_SPE_Shw_ini.big`'s `USA\Vanilla\Aircraft\SpyDrone.ini`) | `Tank_ChinaSurveillanceUAV` |

## Build-time verification (all enforced; build fails loudly otherwise)

- Effective-file ownership asserted per patched + donor file; the new
  INI path asserted unclaimed in every archive of both dirs; all 18 new
  identifiers word-boundary collision-checked across the whole
  effective INI space.
- Donor drift guards: SpyDrone object shape (200 HP, innate stealth,
  detector, no lifetime, Global Hawk command set/locomotor), the Radar
  Van StartsPaused/Unpause/NEED_UPGRADE pairing, and the USA CC
  `CREATE_ABOVE_LOCATION` module re-asserted from source each build.
- Diff audits: CommandSet/CommandButton/Upgrade/SpecialPower/OCL/
  Generals.str asserted `startswith(source)` (append-only, base bytes
  identical) and the CommandSet appendix contains exactly the 4 clones;
  InternetCenter.ini diff = exactly 5 repointed lines + the 2 inserted
  modules; drone clone diff = exactly 5 changed lines + header with the
  armor-upgrade hooks dropped; block-balance (End-count) deltas exact
  per file.
- Cross-reference closure: button ↔ upgrade ↔ power ↔ OCL ↔ object ↔
  strings ↔ cameos ↔ sounds ↔ locomotor ↔ armor ↔ death OCL ↔ model
  (`AVSpyDr` in `!ShwW3D.big`); every button in the 4 new sets resolves
  to a CommandButton.
- Propaganda Center fullness (the deviation's justification) asserted
  across all 50 sets, incl. artillery 4–5, basetech 10–11, garrisons
  Evacuate 12, mines state 13, Sell 14.
- **Sibling survival re-asserted on shipped and installed bytes**:
  roster WF page-2 slots 4–7 (8–11 still free) + Barracks 5 (both
  variants) + Airfield 3–4 with exits 5–9/Evacuate 10 (both variants);
  chaos-units page arrows + page-2 slots 1–3; kwai-artillery Inferno at
  WF 11 (both variants); doctrine's 48 state sets + full 50-set layout;
  basetech's IC modules/weapon sets and 12 upgrade buttons + upgrades;
  emperor-bunker Emperor set; mammoth-bunker transport slots;
  prop-tower Battlemaster sets (incl. ERA); kwai-bunkers dozer pages +
  Hacker Bunker set; stat-tune IC 20000 HP / 30 hacker slots; vanilla
  China prop-center and Internet Center sets byte-untouched.
- Archive sort position verified against the **real listings of both
  mod dirs**; installed archives re-read and byte-compared; an
  independent post-install audit recomputed the whole effective space
  in both dirs; rebuild is idempotent (self-archive excluded from
  sourcing, hash-stable). **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive), patches, verifies, writes `zzz-ZZZZZZKwaiUAV.big` and
installs to both mod dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer** (after
kwai-roster). If any lower layer is rebuilt (kwai-roster, chaos-units,
kwai-garrisons, kwai-basetech, kwai-bunkers, kwai-doctrine,
emperor-bunker, kwai-artillery, stat-tune, …), rebuild this archive
afterwards — it embeds full copies of CommandSet.ini /
CommandButton.ini / Upgrade.ini / SpecialPower.ini /
ObjectCreationList.ini / Generals.str / InternetCenter.ini. Conversely,
lower layers' builds must not see this archive: delete
`zzz-ZZZZZZKwaiUAV.big` from both mod dirs first, rebuild the lower
chain in its documented order (… → chaos-units → kwai-roster), then
rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZKwaiUAV.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZKwaiUAV.big`

## Uninstall

Delete `zzz-ZZZZZZKwaiUAV.big` from both directories above. No other
files are touched.

## Notes / accepted limitations / balance

- **Pre-research presentation**: the deploy button is *visible but
  greyed* from the moment the IC is built (`NEED_UPGRADE` →
  `COMMAND_RESTRICTED`); this is the Radar Van's standard presentation,
  not a hidden button.
- **Drones accumulate**: 120 s reload + permanent-until-killed means a
  patient player can blanket the map over time. The drone is 200 HP,
  unarmed, and stealth-*revealed while taking damage*, so any AA or
  base defense clears it — same economy as the vanilla Spy Drone
  (150 s), slightly faster per the ~2 min spec. All ICs share one
  reload clock (`SharedSyncedTimer`, donor parity).
- IC individual-eject cameos for hacker occupants 7+ are gone (8 → 6
  exit buttons); Evacuate still ejects everyone.
- The deploy power needs the IC *functional*: `OCLSpecialPower` won't
  fire from a disabled (e.g. hacked/subdued) building; the IC is not
  `POWERED`, so low power alone does not block it — same as the
  satellite scan.
- Capture scenarios cannot arise: the Internet Center carries
  `IMMUNE_TO_CAPTURE` (verified in the shipped file). If a *hacked*
  (disabled) IC changes hands by other means, upgrade-gated
  buttons/powers re-evaluate for the owning player — standard engine
  semantics.
- The drone keeps donor KindOf (incl. `SCORE`): each deployed UAV
  counts in end-game unit stats; kills of it feed the enemy's score.
  Cosmetics: USA Global Hawk model + sentry-drone voice set on a China
  unit (documented reuse; no China drone art exists in ShockWave).
- Save games crossing an install/uninstall boundary may not load (new
  object + modules on the IC). Start fresh.
- AI never researches or deploys it (no AIData/build-list changes);
  player-only.
- NOT verified in-game (deliberately not launched); all verification is
  static against the engine source and installed bytes.
