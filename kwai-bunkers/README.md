# Kwai Bunkers (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Gives
Kwai (China Tank General) two dozer-buildable structures:

1. **Tank Bunker** — `Tank_ChinaBunker` (3000 HP with stat-tune's 2x,
   holds 1 vehicle that fires out, WarFactory prerequisite, $200 / 8 s)
   has existed in ShockWave's data all along, together with a *finished*
   construct button `Tank_Command_ConstructChinaBunker` (DOZER_CONSTRUCT,
   `SNTankBunker` cameo, all strings already in `Generals.str`) — but the
   button was referenced by **no command set**, so Kwai could never build
   it. This mod wires it up.
2. **Hacker Bunker** (new) — `Tank_ChinaHackerBunker`: a fortified post
   where up to **4 Hackers keep hacking for cash inside**, at the
   Internet-Center *fast* rate. $1000 / 15 s, Barracks prerequisite,
   3000 HP (inherits Kwai's 2x-health bunker body, `FireBaseArmor`, the
   bunker's art/sounds/geometry **and** the four kwai-doctrine Composite
   Armor `MaxHealthUpgrade` tiers, +300 HP each).

Output archive: **`zzz-ZKwaiBunkers.big`** (installed to both mod dirs).
Case-insensitively `-` (0x2D) sorts before `_` (0x5F) and `k` < `z`
inside the `zzz-` group, so the archive lands **after**
`zzz-KwaiDoctrine.big` (whose CommandSet.ini / CommandButton.ini /
Generals.str / Dozer.ini it layers on) and **before**
`zzz_ControlBarPro*.big` — verified against the real directory listings
at build time.

## The dozer second page

Kwai's `Tank_ChinaDozerCommandSet` had **all 14 UI slots occupied**
(every other China general keeps slot 7 for his bunker; Kwai's slot 7 is
the Sentry Tower and slot 13 the Industrial Plant). The engine allows 18
commands per set but only 14 button windows exist in the control bar —
`MAX_COMMANDS_PER_SET = 18` with "user interface max is 14"
(ControlBar.h:411), and both `!Shw_wnd.big` and the installed
ControlBarPro skins define `ButtonCommand01..14` only (verified inside
the .wnd files). So the mod adds a **second page** using the
vanilla-China dozer page-flip idiom (`ChinaDozerCommandSet` ↔
`ChinaDozerCommandSet_Down`), copied field-for-field from
`Object\China\Vanilla\Vehicles\Dozer.ini`:

- **Page 1**: slots 1–12 and 14 unchanged; slot 13 Industrial Plant →
  **page-down arrow** (`Command_ChinaButtonCommandSetOneDown`).
- **Page 2** (`Tank_ChinaDozerCommandSet_Down`, new): 1 Industrial Plant
  (relocated) · **7 Tank Bunker** (the generals-wide bunker slot) ·
  **8 Hacker Bunker** · 13 page-up arrow · 14 disarm mines.

The arrows are free, instant `OBJECT`-type upgrades
(`Upgrade_GLAWorkerFakeCommandSet` / `Upgrade_GLAWorkerRealCommandSet`,
$0 / 0 s — shared engine-wide as page tokens, same as the GLA Worker and
the vanilla China dozer). Two `CommandSetUpgrade` modules on
`Tank_ChinaVehicleDozer` flip the set and `RemovesUpgrades` cross-clear
the tokens so the pages can be flipped forever; a
`ProductionUpdate MaxQueueEntries=1` module is added because
OBJECT_UPGRADE buttons need a production queue. Module tags
`ModuleTag_KB_Page01..03` (collision-checked).

## The Hacker Bunker (engine-source verified, GeneralsX GeneralsMD tree)

- **`InternetHackContain`** is a subclass of `TransportContain` whose
  *only* override is `onContaining` →
  `rider->getAI()->aiHackInternet(CMD_FROM_AI)`
  (InternetHackContain.cpp:80-86) — passengers auto-resume hacking the
  moment they enter, and `getPackTime()` returns 0 for contained hackers
  so they walk out without folding their gear.
- **Income**: contained hackers use `CashUpdateDelayFast` = **1600 ms**
  vs 2000 ms outside (HackInternetAIUpdate.cpp `getCashUpdateDelay`;
  values from `ChinaInfantryHacker`) — the same **+25% cash rate** the
  Internet Center gives. $5/6/8/10 per tick by veterancy.
- **No firing out**: `PassengersAllowedToFire = No` (a TransportContain
  field), matching the Internet Center — hackers are unarmed anyway.
  `AllowInsideKindOf = MONEY_HACKER` keeps everything else out.
- Contain fields mirror `Tank_ChinaInternetCenter`'s module
  (`HealthRegen%PerSec 10`, `DamagePercentToUnits 50%`, `ExitDelay 500`)
  but **Slots = 4** (IC has 8). `NumberOfExitPaths = 1`: the NBTnkBnk
  bunker model has no ExitStart/ExitEnd bones, but the engine falls back
  to the object position (Object.cpp:6141-6155) and
  `adjustToPossibleDestination` walks the rider to open ground.
- The object is a textual derivation of Kwai's `Tank_ChinaBunker`
  (single-occurrence exact-match edits, enforced): GarrisonContain →
  InternetHackContain; `HiveStructureBody` → `StructureBody`; KindOf
  drops CAN_ATTACK / SPAWNS_ARE_THE_WEAPONS /
  GARRISONABLE_UNTIL_DESTROYED etc.; the bunker's mines family
  (GenerateMinefield + mines CommandSetUpgrade + EMP ArmorUpgrade) and
  vehicle-repair aura are removed — so the object is **orthogonal to the
  doctrine's 50-set Propaganda-Center state machine** (it has no
  CommandSetUpgrade at all). 11 behavior modules total.
- New file `Data\INI\Object\China\Tank\Defences\HackerBunker.ini` — the
  engine loads `Data\INI\Object` with `subdirs=TRUE`
  (GameEngine.cpp:673 → INI::loadFileDirectory), so new INI paths inside
  a .big are picked up automatically. Path asserted unclaimed across the
  whole archive chain at build time.
- Own command set `Tank_ChinaHackerBunkerCommandSet`: 4 ×
  `Command_StructureExit`, `Command_Evacuate`, `Command_Sell` (Internet
  Center idiom). Construct button reuses the Internet Center cameo
  (`SNIntCnt`); the structure keeps the bunker select-portrait.

## Files in the archive (5, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-KwaiDoctrine.big` | dozer slot 13 → page-down; +2 sets appended (page 2, hacker bunker) |
| `Data\INI\CommandButton.ini` | `zzz-KwaiDoctrine.big` | +1 construct button appended (hacker bunker) |
| `Data\Generals.str` | `zzz-KwaiDoctrine.big` | +3 string entries appended (append-only, base bytes identical) |
| `…\Tank\Vehicles\Dozer.ini` | `zzz-KwaiDoctrine.big` | +2 CommandSetUpgrade + 1 ProductionUpdate modules |
| `…\Tank\Defences\HackerBunker.ini` | **new file** | the Hacker Bunker object |

Not shipped but read: `…\Tank\Defences\Bunker.ini` (clone source),
`…\Tank\Buildings\InternetCenter.ini` and `Data\INI\Upgrade.ini`
(reference asserts). No new art, sounds or upgrades — everything reuses
existing assets.

## Build-time verification (all enforced, build fails loudly otherwise)

- Effective-file ownership asserted per file (all `zzz-KwaiDoctrine.big`;
  drift = abort); the new object path asserted absent everywhere; all
  new identifiers collision-checked.
- Diff audits: CommandSet.ini = exactly 1 slot line swapped + the two-set
  appendix; Dozer.ini = 3 modules inserted, zero lines removed;
  CommandButton.ini and Generals.str asserted `startswith(source)`
  (STR base bytes byte-identical, entries only appended).
- Hacker bunker: required lines present (contain, slots, MONEY_HACKER,
  3000 HP body, FireBaseArmor, cost, prereq, all four doctrine armor
  tiers with their `Tank_Upgrade_KwaiVehicleArmor*` triggers), leftover
  bunker-isms forbidden (GarrisonContain, mines, CAN_ATTACK, …),
  behavior-module count == 11, block balance vs the source.
- Cross-reference closure: every command in the new sets has a button;
  construct buttons point at existing objects; the page upgrades exist
  and are OBJECT/free/instant; every new string label exists.
- **Sibling survival re-asserted on the shipped and installed bytes**:
  kwai-doctrine's 48 appended state sets + doctrine slots 8-9 across all
  50 Propaganda-Center sets + its 10 buttons / 30 strings / dozer armor
  tiers; kwai-artillery factory slots 11-12; emperor-bunker Emperor set;
  mammoth-bunker slots 4-8; china-bunkers/prop-towers Battlemaster sets;
  Kwai dozer page-1 slots 1-12 byte-identical; vanilla China dozer pages
  untouched.
- Archive sort position checked against the real directory listings;
  installed archives re-read and re-verified byte-for-byte; rebuild is
  idempotent (self-archive excluded from sourcing, hash-stable).

## Rebuild

```
python3 build.py
```

Reads the effective sources from `~/GeneralsX/mods/ShockWaveSPE/`
(excluding its own archive), patches, verifies, writes
`zzz-ZKwaiBunkers.big` here and installs to both mod dirs. Depends on
`../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the last INI layer — it embeds full
copies of kwai-doctrine-owned files. If **any** lower layer is rebuilt
(kwai-doctrine, stat-tune, emperor-bunker, kwai-artillery, …), rebuild
this archive afterwards. Conversely, **kwai-doctrine's own build must
not see this archive**: its ownership asserts would (correctly, loudly)
fail because this archive now owns CommandSet.ini etc. — delete
`zzz-ZKwaiBunkers.big` from both mod dirs first, rebuild kwai-doctrine,
then rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZKwaiBunkers.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZKwaiBunkers.big`

## Uninstall

Delete `zzz-ZKwaiBunkers.big` from both directories above. No other
files are touched.

## Known limitations / risks

- **Save games**: the dozer gained modules and a new object type exists —
  saves crossing an install/uninstall boundary may not load. Start fresh.
- The page-flip arrows go through the dozer's (new) 1-slot production
  queue: the flip is instant and free, but a multi-selected dozer group
  flips only the dozers whose queue is empty (vanilla China dozers behave
  the same way).
- The Industrial Plant construct button moved to page 2 slot 1 — a
  deliberate relocation (built once per game) to free the page-arrow
  slot; muscle memory may object.
- The Hacker Bunker's sandbag "garrisoned" model state never shows
  (TransportContain doesn't set the GARRISONED draw condition) — purely
  cosmetic.
- Exit uses the bone-fallback path (no ExitStart/ExitEnd in NBTnkBnk):
  hackers pop out at the bunker's footprint and pathfind clear. Looks
  slightly less staged than the Internet Center's scripted walk-out.
- `&Hacker Bunker` hotkey (H) is untested against every page-2 label;
  worst case two buttons share a mnemonic (engine cycles, harmless).
- AI never builds either structure (no AI script/build-list changes);
  player-facing only.
- Balance: a 3000 HP, $1000 bunker generating ≈ $12.5/s when packed with
  4 regular hackers ($3.125/s each at the fast rate) pays for itself in
  ~80 s of uptime and is very hard to crack behind Kwai's armor tiers —
  intentional, he had no forward economy piece.
