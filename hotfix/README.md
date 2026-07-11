# Hotfix Layer (ShockWave / GeneralsX)

Small hot-fix layer for the Panzergrenadiers stack (Kwai / China Tank
General). Three items, shipped as pure top-layer file overrides:

1. **Internet Center capacity + pre-garrisoned hackers** —
   `Tank_ChinaInternetCenter`'s `InternetHackContain` `Slots` 30 → **60**,
   and the building now spawns with **10 hackers pre-garrisoned**
   (`InitialPayload = ChinaInfantryHacker 10`, the TroopCrawler idiom).
2. **PDL pod ballistic interception** — `Tank_ChinaPDLPod`'s
   `PointDefenseLaserUpdate` `PrimaryTargetTypes` `SMALL_MISSILE` →
   **`BALLISTIC_MISSILE SMALL_MISSILE`** (Avenger parity): Tomahawks and
   other `BALLISTIC_MISSILE`-class ordnance are now intercepted.
3. **Hacker Bunker build button removed** — Kwai's dozer page 2
   (`Tank_ChinaDozerCommandSet_Down`) loses the slot-8
   `Tank_Command_ConstructChinaHackerBunker` line. The
   `Tank_ChinaHackerBunker` object, its construct button, command set and
   strings all **stay defined but dormant** (nothing references the
   button; already-built bunkers on old saves would still function).

Output archive: **`zzz-ZZZZZZZXHotfix.big`** (3 files, all INI — no new
identifiers, art, strings, objects or module tags). Case-insensitively
`zzz-zzzzzzzx…` sorts **after** `zzz-ZZZZZZZWEconomy.big` (`x` > `w` at
char 12) and — because `-` (0x2D) < `_` (0x5F) < `z` (0x7A) — **before**
`zzz_ControlBarPro*.big` and `zzzz_FXEnhance.big`, verified against the
real directory listings of both mod dirs at build time (plus the
invariant that no archive sorting after ours claims any path we ship:
FXEnhance owns only ParticleSystem.ini/FXList.ini, ControlBarPro ships no
INI). This is now the **last INI layer of the stack chain** (fx-enhance
is a separate session's layer and stays above by design).

## Item 1 — Internet Center (InitialPayload findings)

Engine facts (GeneralsX GeneralsMD tree, verified read-only):

- `InitialPayload` is a `TransportContainModuleData` field
  (`TransportContain.cpp:107`); `InternetHackContainModuleData::
  buildFieldParse` chains to `TransportContainModuleData::buildFieldParse`
  (`InternetHackContain.cpp:50`), so the field parses inside an
  `InternetHackContain` block unchanged.
- `TransportContain::createPayload()` (`TransportContain.cpp:434-464`)
  runs from the **first `update()`** of the contain module: each payload
  is created via `ThingFactory::newObject` on the owner's default team,
  then admitted through the normal `isValidContainerFor` gates
  (`MONEY_HACKER` allow-mask ✓, same player ✓, `TransportSlotCount` 1 ×
  10 ≤ 60 slots ✓). `InternetHackContain` overrides neither `update` nor
  `createPayload`; its `onContaining` fires for payload riders too, so
  the 10 hackers **start hacking immediately** at the contained fast
  rate (1600 ms/tick, +25% vs outside).
- **Payload object choice**: `ThingFactory::newObject`
  (`ThingFactory.cpp:315-321`) applies `BuildVariations` redirects to
  payload templates, so Kwai's `Tank_ChinaInfantryHacker` stub *would*
  have worked (it redirects to `ChinaInfantryHacker`) — but the concrete
  **vanilla `ChinaInfantryHacker`** is used directly: deterministic, no
  needless redirect, and it is exactly the object Kwai's build button
  charges for and spawns. It carries `MONEY_HACKER INFANTRY` KindOf and
  the `HackInternetAIUpdate` the contain module drives (the stub itself
  has no AI/body modules and only exists to be redirected).
- **Timing**: `OBJECT_STATUS_UNDER_CONSTRUCTION` is a status bit, not a
  `DisabledType` — update modules are only gated by the disabled mask
  (`GameLogic.cpp:3878`), so the payload spawns **when construction
  starts**, and the hackers earn during the build. Cancelling
  construction does **not** leak free hackers: `OpenContain::onDelete`
  destroys all riders with the building (`OpenContain.cpp:888-897`).
  On building death the riders take the module's 50%
  `DamagePercentToUnits`, survivors pop out (vanilla IC behavior).
- The 10 payload hackers are **free** (no build cost is charged —
  `createPayload` never touches the production queue) and arrive at
  REGULAR veterancy ($5/tick fast). AI-owned Kwai ICs get them too
  (symmetric). The IC's exit UI is unchanged: 8 individual exit cameos +
  Evacuate serve any occupancy (Evacuate empties everyone).

## Item 2 — PDL pod

The pod's module previously listed `PrimaryTargetTypes = SMALL_MISSILE`
only (a deliberate scope cut in the kwai-pdl layer) — Tomahawks and all
`BALLISTIC_MISSILE`-class projectiles (`TomahawkMissile`,
`PlasmaTomahawkMissile(+Heroic)` are `KindOf = PROJECTILE
BALLISTIC_MISSILE`) flew straight through. Now `BALLISTIC_MISSILE
SMALL_MISSILE`, byte-matching all three ShockWave Avengers
(`AmericaTankAvenger`, `Lazr_`, `SupW_` — asserted as a drift guard each
build). The pod file's header deviation note was updated to match.
Weapon, scan range (160), scan rate and velocity factor are untouched.

## Item 3 — Hacker Bunker button removal

`Tank_ChinaDozerCommandSet_Down` (Kwai dozer page 2) post-edit:
1 Industrial Plant · 7 Tank Bunker · 9 Tesla Coil (tesla-coil layer,
survives) · 13 page-up · 14 disarm mines. Slot 8 is now empty; the
removed line is replaced in-file by an annotation comment. Deliberately
**not** removed: the `Tank_Command_ConstructChinaHackerBunker` button
definition, the `Tank_ChinaHackerBunker` object, its
`Tank_ChinaHackerBunkerCommandSet` and its `Generals.str` labels — all
dormant (an unreferenced button is inert; removing definitions would
have required shipping more shared files for zero gain).

## Files in the archive (3, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\Object\China\Tank\Buildings\InternetCenter.ini` | `zzz-ZZZZZZZWEconomy.big` | `Slots` 30 → 60 + 1 `InitialPayload` line |
| `Data\INI\Object\China\Tank\Vehicles\PDLPod.ini` | `zzz-ZZZZZZZKwaiPDL.big` | 1 `PrimaryTargetTypes` line + 2 header-comment lines |
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZWEconomy.big` | 1 slot line removed (→ annotation comment) |

New identifiers: **none**.

## Build-time verification (all enforced; build fails loudly otherwise)

- Effective ownership asserted for all 3 sourced files; sources are read
  **only** from archives sorting strictly below this one (never from
  fx-enhance/ControlBarPro); sort position + "no later archive claims any
  shipped path" against the real listings of both dirs.
- Exact line-level diff audits on all 3 files (added/removed line
  multisets must equal the planned edits — every sibling hunk
  byte-survives, everything else byte-identical to the effective source).
- InitialPayload closure: payload object defined, `MONEY_HACKER INFANTRY`
  KindOf, `TransportSlotCount`×10 ≤ 60, TroopCrawler donor idiom intact,
  Kwai stub still redirects to the payload object.
- PDL drift guards: Avenger `BALLISTIC_MISSILE SMALL_MISSILE` parity,
  `TomahawkMissile` KindOf, untouched pod fields present.
- CommandSet survival: dozer page-2 exact post-edit layout (Tesla Coil
  at 9 survives), page 1 untouched, barracks 9/10 rotr-infantry buttons,
  barracks 5–8 roster/LKwaiInfantry buttons, Hacker Bunker interior set,
  IC exit-cameo set (w-economy state) — plus the diff audit's global
  byte-identity for every other set.
- Closure: every slot of the edited set resolves to a CommandButton;
  zero remaining `Tank_Command_ConstructChinaHackerBunker` references in
  CommandSet.ini; the dormant button and `Tank_ChinaHackerBunker` object
  definitions asserted still present in the effective space.
- BIG round-trip byte-identity; installed archives re-read and
  byte-compared; post-install effective-space audit in both dirs (our
  archive owns exactly the 3 paths with exactly the patched bytes);
  rebuild is **hash-idempotent** (verified). **The game was deliberately
  not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive and everything sorting above it), patches, verifies,
writes `zzz-ZZZZZZZXHotfix.big` here and installs to both mod dirs.
Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the last INI layer of the stack
chain. If any lower layer is rebuilt (w-economy, vehicle-kit, tesla-coil,
rotr-infantry, kwai-pdl, …), rebuild this archive afterwards — it embeds
full copies of their files (CommandSet.ini + InternetCenter.ini from
w-economy, PDLPod.ini from kwai-pdl). Conversely, lower layers' builds
must not see this archive: delete `zzz-ZZZZZZZXHotfix.big` from both mod
dirs first, rebuild the lower chain in its documented order, then rerun
this build. (`zzzz_FXEnhance.big` belongs to another session and is
never read or rebuilt by this layer.)

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZXHotfix.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZXHotfix.big`

## Uninstall

Delete `zzz-ZZZZZZZXHotfix.big` from both directories above. No other
files are touched. (Uninstalling restores the 30-slot empty-spawning
Internet Center, the SMALL_MISSILE-only PDL pod, and the dozer page-2
Hacker Bunker build button.)

## Known limitations / risks / balance

- **10 free hackers per Internet Center** (≈$31/s at REGULAR fast rate
  once spawned) is a large economy buff, and they start earning during
  construction; the IC's $2500 price is unchanged. AI Kwai benefits
  symmetrically. Pre-approved.
- 60 slots with only 8 individual exit cameos: occupants 9+ have no
  per-head eject button — use Evacuate (same accepted overflow as
  emperor-bunker's original design).
- Ballistic interception makes massed Kwai armor with pods very strong
  against Tomahawk/ballistic-missile artillery — intended (Avenger
  parity); saturation volleys still overwhelm (one beam per 800 ms per
  pod).
- Save games crossing an install/uninstall boundary may not load (module
  list changed on the IC; a command-set line changed). Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX engine source
  (GeneralsMD tree).
