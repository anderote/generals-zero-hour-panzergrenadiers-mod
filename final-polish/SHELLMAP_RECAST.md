# Kwai Shellmap Recast — what shipped, and the ceiling

**Goal.** Recast the main-menu shellmap (the scene behind the menu) to feature
the Panzergrenadier Kwai army. **Outcome: SHIPPED — a safe, non-corrupting,
pure-data partial recast** (`zzz-ZZZZZZZZZZZZZZ0ShellKwai.big`). The China
contingent in the menu scene now uses Kwai's **`Tank_`** (China Tank General)
roster. The full "showcase" vision (crewed Emperors, tesla units, paradrops,
PDL-zapping choreography) is **not** achievable in pure data and is documented
below as a World Builder task.

---

## The shellmap: identity, location, format

| | |
|---|---|
| **Which map loads** | `Data\INI\GameData.ini` sets `ShellMapName = Maps\ShellMapSHW\ShellMapSHW.map` (ShockWave overrides stock ZH's `ShellMapMD`). Present identically in `!Shw_ini.big` and `zz_SPE_Shw_ini.big`. |
| **Where it lives** | Inside **`!Shw_maps.big`** (both mod dirs), internal path `Maps\ShellMapSHW\ShellMapSHW.map`, 181,366 bytes. `!Shw_maps.big` is its **sole owner**. |
| **Format** | EA **RefPack**-compressed: `EAR\0` + LE-uint32 uncompressed size (1,282,022) + a `10 FB…` RefPack stream. Decompresses to a `CkMp` DataChunk payload. |
| **Chunk format** | `"CkMp"` + Int count + a symbol table (`1-byte len + name + UInt id`), then a chunk tree: each chunk = `UInt id, UShort version, Int dataSize, data`. `ObjectsList` holds `Object` chunks; each `Object` = `3×Real loc + Real angle + Int flags + AsciiString(2-byte len)template + Dict`. (Verified against `DataChunk.cpp`, `ScriptDialog.cpp:1661` `ParseObjectDataChunk`.) |

## Why the recast is safe (no corruption possible)

1. **Every China subfaction prefix is exactly 5 bytes**: `Spec_`, `Nuke_`,
   `Tank_`. Swapping a placed unit to its Kwai equivalent overwrites only the
   template ASCII bytes **in place** — the 2-byte length prefix and every chunk
   `dataSize` are unchanged. No reflow, no offset math.
2. We swap **only** base names with a verified `Tank_<base>` `Object` in the
   effective roster (**21 of 24** placed China types → **123 placements**). The
   3 Kwai-less types are left untouched (still valid `Spec_` units).
3. The engine **reads uncompressed maps** (`DataChunk.cpp` raw-`CkMp` path), so
   the edited buffer is stored **uncompressed** — no RefPack *encoder* is needed
   (the decoder was verified byte-identical to a reference decode; encoding is
   the error-prone half and is avoided entirely).
4. The edit is verified by **re-parsing** the output: identical object count and
   offsets, every swapped placement now `Tank_China*` and present in the roster,
   no `Spec_/Nuke_` leftovers among swapped bases.

## What the scene now shows (Kwai-ified, 123 placements)

Swapped `Spec_`/`Nuke_` → `Tank_` for: Battlemaster (7), Tank Hunter infantry (7),
Red Guard infantry (24), Flame Thrower infantry (4), Dragon (6), Gattling tank
(2), ECM tank (1), Troop Crawler (5), Inferno Cannon (4), Nuke Launcher (2),
Helix (2), Dozer (2), Gattling Cannon (5), Bunker (5), Listening Outpost (1),
and buildings: Power Plant (41), War Factory, Supply Center, Propaganda Center,
Internet Center, Nuclear Missile Launcher. **Left as-is** (Kwai has no
equivalent): HellStorm (4), Seismic Tank (2), Repair Station (1). USA and GLA
placements, civilians, terrain, waypoints, scripts and the attack-wave
choreography are **byte-untouched**.

## The ceiling — why the full showcase needs World Builder (not pure data)

The user's fuller vision — **2 crewed Heroic Emperors, tesla troopers in
garrisons, PDLs visibly zapping incoming GLA rockets, crewed drops** — is **not
data-swappable**, because:

- **Those objects are not on the stock map.** There is **no** Emperor, tesla
  unit, Panzergrenadier or drop anywhere in `ShellMapSHW`. Adding them means
  inserting **new `Object` chunks** (new coords + Dict), which **grows** the
  `ObjectsList` chunk and forces rewriting the `dataSize` of that chunk **and
  every ancestor up to the root** — feasible but delicate binary surgery, and
  still leaves them **unscripted** (static props).
- **The choreography is scripted.** PDLs zapping rockets, marching waves, camera
  beats live in the map's `PolygonTriggers`/`ScriptsPlayers` chunks. Authoring
  new scripted behaviour is a **World Builder** job, not a byte edit.
- **Distinctive Kwai infantry are longer strings.** `Tank_ChinaInfantryRedguard`
  (26) ≠ `Tank_ChinaInfantryPanzergrenadier` (33): swapping to the Panzergrenadier
  would be a non-equal-length edit (needs the dataSize propagation above), so the
  equal-length recast keeps the Kwai **red-guard** infantry object, not the
  Panzergrenadier. (Cosmetically a red guard; the underlying roster is Kwai's.)

**To do the full showcase (recommended path):** open
`Maps\ShellMapSHW\ShellMapSHW.map` in the GeneralsX **World Builder**, place the
crewed Emperors / tesla / drop units, grant the showcase upgrades via map
scripts (script-granted `Tank_Upgrade_*` so PDL/gattling/coax/Shtora are visibly
active), and re-save. World Builder handles chunk sizing and script chunks
correctly. Then repackage the saved `.map` into the same override archive
(`zzz-ZZZZZZZZZZZZZZ0ShellKwai.big`) — it may be stored compressed or
uncompressed; the engine reads both.

## Install / sort / uninstall

- Archive **`zzz-ZZZZZZZZZZZZZZ0ShellKwai.big`** (1,282,079 bytes, one entry:
  the uncompressed recast map). 14 Z's sorts **above** the top INI layer
  (13-Z `…TeslaFinish`) and — `zzz-` (`-`=0x2D) — **below**
  `zzz_ControlBarPro*`/`zzzz_FXEnhance`. Its only shared path is the shellmap,
  whose sole prior owner (`!Shw_maps.big`) it shadows; verified no
  higher-sorting archive claims that path.
- Installed to `~/GeneralsX/mods/ShockWaveSPE/` and `~/GeneralsX/mods/ShockWave/`
  (md5-identical).
- **Uninstall:** delete `zzz-ZZZZZZZZZZZZZZ0ShellKwai.big` from both dirs — the
  original compressed `!Shw_maps.big` shellmap reappears. Nothing else is touched.
- **Rebuild:** `python3 build_shellmap_recast.py` (idempotent; decompresses from
  `!Shw_maps.big`, re-swaps, re-verifies, reinstalls).

## Honest caveat

Not visually confirmed in-game (the game was deliberately **not launched**, per
the whole stack's static-verification practice). The change is **provably
structurally safe** (equal-length in-place edit, re-parsed, round-tripped); the
only unverified dimension is aesthetic. If the recast is not to taste, deleting
the one archive restores the stock scene instantly.
