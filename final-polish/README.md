# Final Polish — Research Overview + Kwai Shellmap (ShockWave / GeneralsX)

Two final-polish tasks for the Panzergrenadiers stack (Kwai / China Tank
General). Both were scoped honestly against the pure-data ceiling.

| Task | Tier shipped | Ships |
|---|---|---|
| **1 — Research Overview** | **(c)** authoritative reference doc. (a) in-game panel = engine work; (b) no data-only in-game text surface exists. | `RESEARCH_OVERVIEW.md` (no `.big`) |
| **2 — Kwai shellmap recast** | **(a)** safe pure-data partial recast (China contingent → Kwai roster). Full showcase = World Builder. | `zzz-ZZZZZZZZZZZZZZ0ShellKwai.big` + `SHELLMAP_RECAST.md` |

---

## Task 1 — Research Overview

**Deliverable shipped: [`RESEARCH_OVERVIEW.md`](./RESEARCH_OVERVIEW.md)** — every
purchasable upgrade in the mod, **grouped by the building that researches it**,
with cost / research time / prerequisite / effect. **Harvested from the real
effective installed stack** (merged `Upgrade.ini`, `CommandSet.ini`,
`CommandButton.ini`, `Generals.str`), not hand-copied from specs. 32 distinct
building researches across 8 buildings (Propaganda Center doctrine tree ×15,
Industrial Plant ×5, War Factory / Emperor Defense ×4, Nuclear Silo ×2, Internet
Center ×2, Airfield ×2, Command Center ×1, Barracks ×1) + per-building mines +
5 vehicle field upgrades. Regenerate with `python3 harvest3.py`.

### Why not an in-game panel — the honest data-only limit

The user wants a **dynamic in-game screen** listing the tree. That is **not
achievable in pure data** in this engine:

- **(a) A clickable .wnd screen opened from a button — needs engine work.**
  Command buttons dispatch a **fixed** `GUICommandType` enum
  (`ControlBar.h`) — every entry is a gameplay verb (`UNIT_BUILD`,
  `PLAYER_UPGRADE`, `SPECIAL_POWER`, `PURCHASE_SCIENCE`, …). **There is no
  "open a window layout" command**, so no button can open a custom screen from
  data. And every `.wnd` menu is driven by a C++ `WindowLayout` callback keyed
  by filename; a new standalone layout with no registered callback can't be
  opened or populated. A real panel therefore needs: a new `GUICommandType`
  (e.g. `GUI_COMMAND_SHOW_RESEARCH_OVERVIEW`) + a `ResearchOverview.wnd` +
  a `WindowLayoutCallback` that iterates the player's buildings/upgrades and
  fills a listbox. Well-scoped, but **C++**, not data.
- **(b) No data-only in-game text surface fits.** Zero Hour has **no
  loading-screen tip system** (that was Generals 1 / later C&C titles). The only
  data-driven multi-line text a player sees in-game is a **button tooltip**
  (`DescriptLabel`) — per-button and short, so it fragments the reference rather
  than giving "the whole tree in one place," and the Kwai dozer build-buttons
  are largely vanilla-shared (editing them risks leaking into other China
  generals). Judged not worth shipping over the authoritative doc.

So the floor deliverable (c) is the ceiling for pure data. The doc is the
"whole tree in one place" the user asked for, just out-of-game.

---

## Task 2 — Kwai shellmap recast

**Deliverable shipped: `zzz-ZZZZZZZZZZZZZZ0ShellKwai.big`** — a **safe,
non-corrupting, pure-data partial recast** of the menu-background shellmap. The
scene's **China contingent (123 placed units/buildings) is swapped from the
stock `Spec_`/`Nuke_` roster to Kwai's `Tank_` roster** via equal-length in-place
template-name overwrites, stored uncompressed (the engine reads raw `CkMp`).
Full detail, format notes and the World-Builder path for the fuller showcase
(Emperors / tesla / drops / PDL choreography — **not** data-achievable, those
objects aren't on the map) are in **[`SHELLMAP_RECAST.md`](./SHELLMAP_RECAST.md)**.

Rebuild: `python3 build_shellmap_recast.py`.

---

## Verification (both tasks)

- **Task 1** harvested from the effective stack; costs/times read from installed
  `Upgrade` blocks, effects from installed tooltips, prereqs from installed
  `RequiredUpgrade` + documented `CommandSetUpgrade` chains. No game data changed
  (doc only).
- **Task 2** — RefPack decoder verified byte-identical to a reference decode;
  edit is equal-length in-place (buffer length unchanged); **edited buffer
  re-parsed** (identical object count/offsets, every `Tank_China*` placement
  resolves in the roster, no `Spec_/Nuke_` leftovers among swapped types); **BIG
  round-trip byte-identical**; **sort-position guard** (no higher-sorting archive
  claims the shellmap path); installed to **both** mod dirs with **md5-identical**
  archives + post-install re-read of the map entry. The archive ships **only**
  the one map file, so **no prior INI/STR layer is clobbered**. **Game not
  launched** — Task 2 is structurally safe but visually unverified (delete the
  one archive to restore stock).

## Files

| File | Role |
|---|---|
| `RESEARCH_OVERVIEW.md` | **Task 1 deliverable** — full building→upgrade reference |
| `SHELLMAP_RECAST.md` | **Task 2 doc** — what shipped + World Builder ceiling |
| `zzz-ZZZZZZZZZZZZZZ0ShellKwai.big` | **Task 2 deliverable** — recast shellmap (installed both dirs) |
| `build_shellmap_recast.py` | reproducible Task 2 build (decompress→swap→verify→install) |
| `refpack.py` | verified EA RefPack decoder (+ `EAR\0` unwrap) |
| `shellparse.py` | `CkMp` chunk-tree / ObjectsList parser (inventory) |
| `harvest.py` / `harvest2.py` / `harvest3.py` | Task 1 upgrade harvesters |
| `_eff.py` | effective-stack resolver (later-alphabetical wins) |
