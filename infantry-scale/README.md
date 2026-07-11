# zzz-ZZZZZZZZZInfantryScale.big — infantry-scale realism layer

Shrinks every **gameplay** infantry model in the Panzergrenadiers stack
(ShockWave layers under GeneralsX / macOS) by **~10%** for realistic
human/vehicle proportions. Pure top-layer file overrides; no lower layer is
rebuilt. Build + install: `python3 build.py` (writes the `.big` here and
installs to both `~/GeneralsX/mods/ShockWaveSPE` and `.../ShockWave`).

## What it changes (two fields per object)

1. **`Scale = 0.95`** added at the top level of each infantry `Object`.
   The engine **double-applies** Scale (baked into the W3D render prototype at
   load *and* multiplied again per-frame), so visual size ≈ `Scale²`.
   `0.95² = 0.9025` → ~10% smaller on screen (matches ZH Reborn's effective
   choice).
2. **`ShadowSizeX` / `ShadowSizeY` × 0.90.** Shadow decals are sized from the
   template and do not inherit the model shrink, so they are scaled explicitly
   (every infantry shadow in the stack is `14` → `12.6`). Objects with no
   ShadowSize fields keep the engine default.

Result: **158 objects scaled across 105 Object INI files** (+158 Scale
inserts, 240 shadow edits = 120 objects × 2 axes; 0 Scale *modifies* — no
in-scope object carried a prior Scale).

## Scope

Enumerated mechanically from the **effective stack** (highest-priority copy of
each file across all installed archives sorting below us). Included: every
`Object` whose object-level `KindOf` contains `INFANTRY`, all factions, every
per-general clone, plus this stack's custom units (Panzergrenadier, tesla
Shock Trooper + `_Var1`, Shmel Trooper, Sharpshooter clone, TeslaInfantry).
The **visible** angry-mob members and China-Infantry-general squad soldiers are
scaled; only their invisible nexus controllers are denied.

**Out of scope** (not the gameplay roster, left untouched):
- **`CINE_*`** cinematic-only actors (mission intros/outros, challenge
  cutscenes — never in skirmish/MP).
- **`maps\`** mission-embedded object definitions (scenario config; scaling
  scripted mission units risks their spawn/scripting assumptions).

These two categories are also the **only** source of ShockWaveSPE-vs-ShockWave
effective divergence (SPE overrides `americacineunit.ini` and adds the
`md_gla11` map). Excluding them makes every shipped file byte-identical across
both mod dirs, so **one archive serves both** (verified in-build).

## Denylist (kept at Scale 1.0 on purpose)

Applied to in-scope objects — **22 total**:

| Reason | Count | Objects |
| --- | --- | --- |
| `KindOf HERO` (readability) | 15 | Black Lotus ×5, Jarmen Kell ×5, Colonel Burton ×5 (all general clones) |
| `KindOf MOB_NEXUS` (invisible health-bar controllers) | 7 | `GLAInfantryAngryMobNexus` (Demo/Chem/vanilla), 3× `Infa_ChinaInfantry*SquadNexus`, `PlasmaBallOfDeathMaster` |

Additional notes:
- Hero **name** matching (Black Lotus / Jarmen Kell / Colonel Burton) also
  covers the non-HERO-tagged `CINE_` hero clones, but those are already out of
  scope via the cinematic exclusion.
- The shared **Parachute** object (and every faction/vehicle parachute) is
  naturally excluded: they are `KindOf PARACHUTE`, not `INFANTRY`, so they
  never enter the enumeration.
- No infantry "China Command Tank crew" object exists (the command-tank crew
  is not a `KindOf INFANTRY` object), so nothing to deny there.

## Packaging / sort order

`zzz-ZZZZZZZZZInfantryScale.big` case-insensitively sorts **after**
`zzz-ZZZZZZZZPanzergrenadier.big` (equal through `zzz-zzzzzzzz`, then char 13
`z` > `p` → we are the last Object-INI layer) and **before**
`zzz_ControlBarPro*.big` / `zzzz_FXEnhance.big` (`-` 0x2D < `_`/`z` at char 4).
Verified against the real listings of both mod dirs. We touch only `Object`
INI files — never fx-enhance's FXList/ParticleSystem files — and never source
from any archive at or above us.

## Verification (all in `build.py`, loud-fail)

Drift guards (158/105/deny 15+7) · cross-dir source parity · per-file
line-multiset diff audit (only Scale/Shadow lines change) · End-count balance
(0 delta — pure field edits) · non-target object byte-survival · inter-object
byte-survival · BIG round-trip · sort order + "no higher archive claims our
paths" (both dirs) · install + re-read equality · post-install effective
re-enumeration (158 scaled @0.95, 22 denied still at default 1.0).
