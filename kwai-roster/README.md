# Kwai Roster (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Gives
**Kwai (China Tank General)** SEVEN cross-general China units via
ShockWave's own **build-stub** idiom (see kwai-artillery/README.md) —
six stubs plus one full clone. Player-only: no AI build-list changes.

Output archive: **`zzz-ZZZZZKwaiRoster.big`** (9 files, INI only — all
art/strings/sounds are donor references that already resolve).
Case-insensitively `zzz-zzzzz…` sorts **after** `zzz-ZZZZChaosUnits.big`
(whose CommandSet.ini / CommandButton.ini it layers on) and `-` (0x2D) <
`_` (0x5F) sorts it **before** `zzz_ControlBarPro*.big` — verified
against the real directory listings of both mod dirs at build time.
This is now the **last INI layer**.

## The roster

| Unit | Stub / clone | Builds | Cost / time | Where | Prerequisites |
|---|---|---|---|---|---|
| **Overlord** | `Tank_ChinaTankOverlord` | `ChinaTankOverlord` (vanilla) | $2000 / 20 s | War Factory **page 2 slot 4** | Tank_ WF + Propaganda Center |
| **Buratino** (TOS-1 thermobaric MLRS) | `Tank_ChinaVehicleBuratino` | `Spec_ChinaVehicleInfernoCannon` (Leang) | $1400 / 16 s | WF **page 2 slot 5** | Tank_ WF + Propaganda Center |
| **Hammer Cannon** | `Tank_ChinaVehicleHammerCannon` | `Spec_ChinaVehicleNukeLauncher` (Leang) | $1800 / 20 s | WF **page 2 slot 6** | Tank_ WF + Propaganda Center (science gate dropped, see notes) |
| **Scout Car** | **CLONE** `Tank_ChinaVehicleScoutCar` | itself (no stub) | $100 / 3 s | WF **page 2 slot 7** | none (donor parity; gated by owning the WF) |
| **Siege Soldier** | `Tank_ChinaInfantrySiegeSoldier` | `ChinaInfantrySiegeSoldier` (vanilla) | $600 / 8 s | **Barracks slot 5** | Tank_ Barracks |
| **MiG** (napalm fighter) | `Tank_ChinaJetMIGFighter` | `ChinaJetMIG` (vanilla) | $1400 / 10 s | **Airfield slot 3** | Tank_ Airfield |
| **MiG Bomber** (EMP) | `Tank_ChinaJetMIGBomber` | `ChinaJetMIGBomber` (vanilla) | $1500 / 15 s | **Airfield slot 4** | Tank_ Airfield |

All prerequisites mirror the donors' own (`ChinaWarFactory +
ChinaPropagandaCenter` → `Tank_ChinaWarFactory +
Tank_ChinaPropagandaCenter`, etc.).

### Variant choices (and why)

- **Overlord — deliberately the VANILLA `ChinaTankOverlord`** so the
  **Battle Bunker** turret option comes along (its own command set:
  bunker 6 / gattling 8 / propaganda tower 10; full closure —
  `ChinaTankOverlordBattleBunker`, upgrade, OCL — verified present).
  It also inherits china-tank-buff's **1320 HP** automatically (stubs
  spawn the real unit; the real unit carries the buff).
- **MiG — vanilla `ChinaJetMIG`** over the Nuke/Infantry/Spec variants:
  it *is* stock China ($1400, spec-exact), and its napalm missiles
  upgrade with **Black Napalm**, which Kwai *can* research
  (kwai-artillery moved that button to his Propaganda Center). The
  stub is named `Tank_ChinaJetMIGFighter` because **`Tank_ChinaJetMIG`
  is already Kwai's own Razor jet** (Airfield slot 1).
- **MiG Bomber — vanilla `ChinaJetMIGBomber`** ($1500), which in
  ShockWave is the **EMP MiG Bomber** — EMP flavor matches Kwai's EMP
  mines / EMP Pulse. The Nuke general's $1600 nuclear variant needs his
  Nuclear Research Plant, which Kwai has no equivalent of.
- **Siege Soldier — vanilla `ChinaInfantrySiegeSoldier`** (stock China
  mortar infantry; Infantry/Nuke variants are that general's flavor).

### The Scout Car clone (why not a stub)

Per spec the Scout Car is a **full clone** of vanilla
`ChinaVehicleBullfrog` (`Vanilla\Vehicles\ScoutCar.ini`) renamed
`Tank_ChinaVehicleScoutCar`, with **VisionRange 200 → 450** and
**ShroudClearingRange 200 → 500**. Cloning (instead of stubbing to the
shared object) keeps the vision buff off vanilla-China's own scout —
asserted: the effective vanilla Bullfrog still reads 200/200. Everything
else is donor-identical (build-audited: exactly 3 changed lines +
header comment), including its area-scan ability, taunt/car-horn
gimmick, Side = China and the donor's *absence* of a Prerequisites
block.

## Slot placement findings

- **War Factory page 2** (`Tank_ChinaWarFactoryCommandSet_Down`,
  chaos-units): slots 4–11 were reserved contiguous-free for this
  layer; slots **4–7** now used, **8–11 still free**. Page-flip arrows
  already exist in both directions (chaos-units WF modules) — nothing
  re-implemented, buttons only. Page-2 survival: Nuke Cannon 1, JS-7 2,
  Command Tank 3, page-up 12, Evacuate 13, Sell 14 — all asserted.
- **Barracks**: as predicted it was NOT garrisoned (kwai-garrisons
  skipped it for its HealContain), so both set variants had only
  1–4 + 12–14 used. Siege Soldier takes **slot 5**; 6–11 remain free.
- **Airfield**: the set was **full** — kwai-garrisons put 7 garrison
  exit cameo buttons at 3–9 and Evacuate at 10 for its 10-seat
  garrison. **Sacrifice (documented): exit cameos reduced 7 → 5**
  (now slots 5–9); the MiGs take **slots 3–4**. Garrisons' own
  precedent already gives several buildings fewer exit buttons than
  seats (Command Center / War Factory / Prop Center have zero);
  **Evacuate at 10 still empties all 10 occupants** — you only lose
  individual-eject cameos for occupants 6–10. Both set variants
  patched identically.

## Files in the archive (9)

| File in archive | Based on (effective owner) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZChaosUnits.big` | 10 added / 4 replaced slot lines across 5 sets (WF page 2, Barracks ×2, Airfield ×2) |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZChaosUnits.big` | +7 construct buttons appended (donor art + CSF labels reused — **no new strings, textures or sounds**) |
| `…\China\Tank\Vehicles\Overlord.ini` | new file | stub `Tank_ChinaTankOverlord` |
| `…\China\Tank\Vehicles\Buratino.ini` | new file | stub `Tank_ChinaVehicleBuratino` |
| `…\China\Tank\Vehicles\HammerCannon.ini` | new file | stub `Tank_ChinaVehicleHammerCannon` |
| `…\China\Tank\Vehicles\ScoutCar.ini` | new file (clone of `zz_SPE_Shw_ini`'s vanilla ScoutCar.ini) | `Tank_ChinaVehicleScoutCar` |
| `…\China\Tank\Infantry\SiegeSoldier.ini` | new file | stub `Tank_ChinaInfantrySiegeSoldier` |
| `…\China\Tank\Aircraft\MIG.ini` | new file | stub `Tank_ChinaJetMIGFighter` |
| `…\China\Tank\Aircraft\MIGBomber.ini` | new file | stub `Tank_ChinaJetMIGBomber` |

Donor sources (read-only): vanilla Overlord from `zzx_ChinaTankBuff.big`
(hence 1320 HP), ScoutCar / Buratino / HammerCannon / SiegeSoldier /
MIG / MIGBomber donors from `zz_SPE_Shw_ini.big` — owners asserted at
build time.

Stub idiom precedents mirrored field-for-field: vehicle
`Tank_ChinaVehicleHackerVan`, aircraft `SupW_AmericaJetRaptor` (KindOf
AIRCRAFT on the stub so the queue reserves an airfield parking space),
infantry `AirF_AmericaInfantryPathfinder`.

## Stats

Stubs inherit the donor units' stats automatically (the spawned object
is the real donor unit): Overlord arrives with china-tank-buff's
1320 HP; Buratino/Hammer Cannon are stock Leang artillery; the MiGs are
stock vanilla aircraft. The only stat change in this layer is the Scout
Car clone's vision (450/500).

## Build-time verification (all enforced; build fails loudly otherwise)

- Ownership asserted for every patched + donor file; the 7 new INI
  paths asserted unclaimed; all 14 new identifiers (7 objects + 7
  buttons) word-boundary collision-checked against the whole effective
  INI space.
- Donor drift guards: donor costs/times/prereqs/KindOf re-parsed and
  compared (incl. the Hammer Cannon's `Science = SCIENCE_HammerCannon`
  line we drop, and confirmation Kwai's promotion sets Rank1/3/8 cannot
  buy it).
- Diff audits: CommandSet exactly +10/−4 known lines; CommandButton
  pure-append (+7 blocks); ScoutCar clone exactly 3 changed lines +
  header; block balance per file.
- Closure: every stub's `BuildVariations` target, prerequisite objects,
  `SelectPortrait`/`ButtonImage` mapped images, and every button's
  Object/art/CONTROLBAR labels resolve in effective data (Generals.str
  is untouched — all labels pre-exist).
- Sibling survival re-asserted on shipped and installed bytes:
  chaos-units page-2 layout (slots 1–3, 12–14) and WF page-1 arrows,
  kwai-artillery Inferno at 11 + relocated Chain Guns / Black Napalm at
  the Prop Center, kwai-doctrine's **50** Prop Center sets, garrisons'
  ≥50 Evacuates + Airfield Evacuate at 10, emperor-bunker Emperor set
  (gattling 10 / Evacuate 12), kwai-bunkers dozer pages, mammoth-bunker
  transport slots, prop-tower Battlemaster sets, chaos buttons/sets.
- Archive sort position verified against the **real listings of both
  mod dirs**; installed archives re-read and byte-compared; plus an
  independent post-install audit recomputed the whole effective space
  in both dirs. **The game was deliberately not launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive), patches, verifies, writes `zzz-ZZZZZKwaiRoster.big`
and installs to both mod dirs. Depends on `../hotkey-addon/bigfile.py`
and `../chaos-units/work/iniblocks.py`.

**Rebuild-order note**: this is now the **last INI layer** (after
chaos-units). If any lower layer is rebuilt (chaos-units,
kwai-garrisons, kwai-basetech, kwai-bunkers, kwai-doctrine,
emperor-bunker, kwai-artillery, stat-tune, …), rebuild this archive
afterwards — it embeds full copies of CommandSet.ini /
CommandButton.ini. Conversely, lower layers' builds must not see this
archive: delete `zzz-ZZZZZKwaiRoster.big` from both mod dirs first,
rebuild the lower chain in its documented order (… → chaos-units), then
rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZKwaiRoster.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZKwaiRoster.big`

## Uninstall

Delete `zzz-ZZZZZKwaiRoster.big` from both directories above. No other
files are touched.

## Notes / accepted limitations

- **Hammer Cannon science gate dropped** (`SCIENCE_HammerCannon`): Kwai
  cannot purchase it (his rank-1/3/8 promotion sets don't offer it), so
  carrying it over would make the unit permanently unbuildable — same
  reasoning and precedent as kwai-artillery's Nuke Cannon.
- Airfield individual-eject cameos for garrison occupants 6–10 are gone
  (7 → 5 exit buttons); Evacuate still ejects everyone.
- The spawned units are stock donor units: no Kwai tank-flavor bonuses
  beyond player upgrades that naturally apply (Black Napalm on the MiG,
  Nationalism etc. per donor upgrade hooks). Buratino's
  `SCIENCE_ArtilleryEliteTraining` starting-veterancy hook stays inert
  (Kwai can't buy it) — unit starts unranked, same as his artillery.
- The MiG stubs carry KindOf AIRCRAFT, so queuing them respects the
  airfield's 4 parking spaces (SupW Raptor stub precedent).
- WF page-2 flips queue behind in-progress production (chaos-units
  behavior, inherent to pages on a producing factory).
- Save games crossing an install/uninstall boundary may not load (new
  object types). Start fresh.
- AI never builds these (no AIData/build-list changes); player-only.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes.
