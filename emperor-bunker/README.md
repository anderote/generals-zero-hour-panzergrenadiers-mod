# Emperor Bunker — mini-mod for ShockWave (GeneralsX/macOS)

Gives Kwai's (China Tank General) **EMPEROR tank** (`Tank_ChinaTankEmperor`)
an infantry bunker bay: up to **10 infantry** garrison the tank, fire out,
and can be ejected via new exit/evacuate command-bar buttons. The tank's
**built-in propaganda tower** and its **Gattling cannon upgrade** are both
fully preserved.

Output archive: **`zzyzzzzzz_EmperorBunker.big`** — the name is deliberate:
inside a `-mod` directory, later-alphabetical archives take priority, so it
must sort after `zzyzzzzz_KwaiArtillery.big` (whose CommandSet.ini it layers
on) and before `zzz_ControlBarPro*.big` (UI skin). Verified case-insensitive
in the build.

## Emperor architecture (why this design)

- The Emperor's **propaganda tower is NOT a rider object**: it is a
  `PropagandaTowerBehavior` module directly on the tank itself
  (`AffectsSelf = Yes ; Needs this since Tower is not seperate object for
  Emperor`). This mod does not touch it — it keeps healing/buffing (and
  upgrading via Subliminal Messaging) exactly as before.
- The **Gattling cannon upgrade IS a rider**: `ObjectCreationUpgrade` →
  `OCL_Tank_OverlordGattlingCannon` →
  `Tank_ChinaTankOverlordGattlingCannon` (a PORTABLE_STRUCTURE with its own
  turret, drawn by `W3DDependencyModelDraw` attached to the Emperor's
  `FIREPOINT01` bone) entering via `ContainInsideSourceObject` into the
  tank's single-seat `OverlordContain ModuleTag_06`.

So this is the mammoth-bunker / china-bunkers situation (single rider in an
OverlordContain seat): the `OverlordContain` is swapped for
**`HelixContain`** — the module the retail Helix uses to carry infantry
*and* a gattling addon at the same time.

### Engine-source facts (GeneralsX GeneralsMD tree, read-only)

- `HelixContain.cpp`: a PORTABLE_STRUCTURE goes into a dedicated
  `m_portableStructureID` rider slot **outside** the passenger list. It is
  accepted regardless of `AllowInsideKindOf`, consumes no seats, never
  appears on exit/evacuate buttons, and is **always allowed to fire** — the
  code comment literally reads "RIDERS ARE ALWAYS ALLOWED TO FIRE (GATTLING
  CANNONS)".
- `HelixContain::update()` syncs the rider to the hull position/orientation
  — **identical semantics** to GeneralsX's own POSIX bugfix in
  `OverlordContain::syncPortablePosition()` ("bone queries return wrong
  world coords on POSIX, so override with the host tank's position"), so
  nothing is lost by dropping OverlordContain's `PassengersInTurret = Yes`
  on this platform.
- `W3DOverlordTankDraw` (kept) locates the rider via `friend_getRider()`,
  which HelixContain implements, and clears the `W3DDependencyModelDraw`
  render dependency — gattling visuals intact.
- `HelixContain::redeployOccupants()` overrides the base class entirely
  (all passengers placed at hull position +8z), so
  `putObjAtNextFirePoint()` / FIREPOINT-bone placement is **never used for
  passengers** — the POSIX bone-coordinate bug cannot bite even though the
  NVEmperor model *does* have a FIREPOINT01 bone.

### Fields dropped from the old contain block

- `PassengersInTurret = Yes` — an OpenContain field consumed only by
  `putObjAtNextFirePoint()`, which is unreachable under HelixContain.
- `ExperienceSinkForRider = Yes` — an **OverlordContain-only** INI field
  (would be a parse error under HelixContain). Consequence: gattling-cannon
  kills now grant XP to the rider object instead of the tank — the same
  behavior as the retail Helix gattling upgrade. Minor.

## Command-set layout (engine-source verified)

The UI renders exactly **14** buttons (`MAX_COMMANDS_PER_SET` is 18, but
ShockWave's ControlBar.wnd and ControlBarPro's define only 14
`ButtonCommand` windows — verified by the kwai-artillery mod). Twelve—or
ten—individual exit buttons cannot fit.

`ControlBar::doTransportInventoryUI` (`ControlBarCommand.cpp`):

- Passenger cameos are filled **sequentially** across the range
  `firstInventoryIndex..lastInventoryIndex` — any non-exit button inside
  that range would be clobbered, so exit buttons **must be contiguous**.
- When passengers outnumber exit buttons, `populateInvDataCallback` hits
  `if (currIndex > maxIndex) { DEBUG_CRASH(...); return; }`. In this build
  `DEBUG_CRASH` compiles to `((void)0)`: `build/macos-vulkan/CMakeCache.txt`
  has `RTS_BUILD_OPTION_DEBUG=OFF` → `RTS_RELEASE` → no
  `ALLOW_DEBUG_UTILS` → `Debug.h` defines `DEBUG_CRASH(m) ((void)0)`.
  Overflow passengers simply get no individual cameo/exit button — safe.
  **Evacuate always unloads everyone.**

Chosen layout for `Tank_ChinaTankEmperorDefaultCommandSet` (the Emperor's
only command set — verified no upgraded/speaker variants exist anywhere in
the effective INIs):

| Slot | Button |
|---|---|
| 1 | `Command_OverlordTaunt` (unchanged) |
| 2–9 | `Command_TransportExit` × 8 (contiguous) |
| 10 | `Tank_Command_UpgradeChinaOverlordGattlingCannon` (moved from 6) |
| 11 | `Command_AttackMove` (unchanged) |
| 12 | `Command_Evacuate` (new) |
| 13 / 14 | `Command_Guard` / `Command_Stop` (unchanged) |

Moving the gattling upgrade from slot 6 to slot 10 (the Overlord-family
upgrade slot, same one the prop-tower mods use) yields the maximum
contiguous exit run: 8 buttons. Nine exits (2–10) would leave no slot for
the mandatory Evacuate. With 10 seats and 8 exit buttons, passengers 9–10
have no individual button (harmless, see above); Evacuate covers all.

## Files in the archive (full patched copies, original internal paths)

| File | Effective source (highest-priority owner) | Change |
|---|---|---|
| `Data\INI\Object\China\Tank\Vehicles\Emperor.ini` | `zzx_ChinaTankBuff.big` | `OverlordContain ModuleTag_06` → `HelixContain ModuleTag_06` (Slots 10, `DamagePercentToUnits = 0%`, `AllowInsideKindOf = INFANTRY`, `ForbidInsideKindOf = AIRCRAFT VEHICLE BOAT`, garrison enter/exit sounds, `PassengersAllowedToFire = Yes`) |
| `Data\INI\CommandSet.ini` | `zzyzzzzz_KwaiArtillery.big` | Emperor set only, as per the table above |

`AllowInsideKindOf` deliberately excludes PORTABLE_STRUCTURE: the gattling
rider bypasses the allow-list into the rider slot (engine fact above), and
excluding it prevents any stray second portable from stealing an infantry
seat (same narrowing battlemaster-proptower applied to Kwai Battlemasters).

Prior layers verified surviving at build time (build fails if they drift):

- Emperor `MaxHealth/InitialHealth = 1320` (china-tank-buff; SPE base is 1100),
- Emperor propaganda tower + gattling upgrade module chain,
- kwai-artillery war-factory slots 11–12 and prop-center slots 4–5 (both variants),
- mammoth-bunker Mammoth slots 4–8 hunk,
- china-bunkers/prop-towers Battlemaster exit + tower hunks and the ERA set.

## Rebuild

```
python3 build.py
```

Reads the effective sources from `~/GeneralsX/mods/ShockWaveSPE/`, verifies
archive ownership hasn't shifted, applies exact-text patches (fails loudly
on upstream drift), audits the full diff hunk-by-hunk, checks block balance
and prior-layer survival, writes `zzyzzzzzz_EmperorBunker.big` here,
installs to both mod dirs and re-reads the installed archives, re-running
all survival checks on the shipped bytes. Depends on
`../hotkey-addon/bigfile.py`.

**Rebuild order note**: if `zzx_ChinaTankBuff.big` or
`zzyzzzzz_KwaiArtillery.big` (or anything below them touching these two
files) is rebuilt with different content, rebuild this archive too — it
embeds full copies of their files and, being later-alphabetical, would
silently mask their newer versions.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzyzzzzzz_EmperorBunker.big`
- `~/GeneralsX/mods/ShockWave/zzyzzzzzz_EmperorBunker.big`

## Uninstall

Delete `zzyzzzzzz_EmperorBunker.big` from both directories above. No other
files are touched.

## Known limitations / risks

- **Save games**: the Emperor's module list changed — saves crossing an
  install/uninstall boundary may fail to load. Start fresh missions or
  skirmishes.
- Infantry fire from the hull center (HelixContain places passengers at the
  hull, not at FIREPOINT bones); no bunker visual on the hull — garrisoned
  state shows via container pips and the exit buttons.
- HelixContain grants passengers the GARRISONED weapon bonus (same as Helix
  riders and the sibling bunker mods) — a small intentional flavor buff.
- Gattling-cannon kills no longer feed XP to the tank (rider keeps them),
  matching retail Helix gattling behavior.
- Only 8 of 10 passengers get individual exit cameos (14-button UI limit);
  use Evacuate to unload everyone at once.
- The gattling upgrade button moved from slot 6 to slot 10 — cosmetic,
  consistent with the Overlord family's upgrade slot.
- AI Emperors never garrison infantry (no AI scripting added); the feature
  is player-facing.
- Balance: 10 fire-out seats on a 2400-cost hull with a built-in heal aura
  makes lone Emperors much stronger vs infantry/ambush — intentional.
