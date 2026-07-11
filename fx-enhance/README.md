# fx-enhance — Explosion / FX enhancement layer

A **visual-only** data mod for the GeneralsX port of C&C Generals Zero Hour.
It makes explosions read as bigger and punchier by (a) adding a warm light
flash to every explosion effect and (b) modestly scaling the particle bursts
those explosions spawn — without touching gameplay in any way.

## What it changes

Two shipped INIs are transformed and repackaged as late/early-loading `.big`
layers:

### `FXList.ini` — light flash on explosions
* An **explosion FXList** is detected mod-name-agnostically as any `FXList`
  block that contains a `ViewShake` nugget (screen shake ⇒ big boom).
* Into every such block that does **not** already have a `LightPulse`, a warm
  orange flash is injected before the block's final `End`:

  ```
    LightPulse
      Color = R:255 G:156 B:64
      Radius = 80
      IncreaseTime = 80
      DecreaseTime = 600
    End
  ```

  Field spelling/order was copied from a real shipped `LightPulse` nugget and
  cross-checked against the engine parse table in `FXList.cpp`.
  `RadiusAsPercentOfObjectSize` is in the parse table but absent from real
  data, so it is intentionally omitted.

### `ParticleSystem.ini` — bigger bursts
For every particle system spawned by an explosion FXList (and any
`explosion|fireball|flame` slave of one), within its own block:

| Parameter  | Change | Notes |
|------------|--------|-------|
| `BurstCount` | ×1.75, rounded | per-value cap **120** |
| `Size`       | ×1.25 | start & end |
| `Lifetime`   | ×1.3 | **smoke systems only** (`ParticleName`/name contains `smoke`) |

Values are scaled in place preserving spacing, comments and line endings. A
value on a line containing `%` or that fails to parse as a float is skipped and
logged.

## Safety caps (protect the render ceiling)

The engine renders at most **2048 particles/system** and **10000 globally** at
Very High LOD. To stay well under:

* **Peak-concurrency estimate:** `BurstCount × (Lifetime_max / BurstDelay_min)`
  (one-shot systems count a single generation). If the post-scale estimate
  exceeds **2000**, the `BurstCount` multiplier for that system is reduced so it
  stays under, and the reduction is logged.
* **Never below source:** the effective `BurstCount` multiplier is floored at
  **1.0×** — a system whose scaled estimate cannot fit under the cap keeps its
  original `BurstCount` values untouched (logged as "kept at original"), and the
  per-value 120 cap likewise never reduces a value below what the game already
  ships. Explosions are never made *smaller* than the unmodified game.
* **Skipped entirely:** systems with `Type = VOLUME_PARTICLE` (6× fill cost) and
  `Priority = WEAPON_TRAIL` (continuous emitters).

## Determinism / safety rationale

* **Visual-only:** only `LightPulse` nuggets and particle `BurstCount`/`Size`/
  `Lifetime` are touched. No `Debris`, `OCL`, weapon, damage, armor or logic
  fields are changed, so simulation and multiplayer determinism are unaffected.
* **Byte-preserving:** the transformer detects each file's line-ending
  convention (vanilla uses `\r\n`; ShockWave's `FXList.ini` is `\n`,
  its `ParticleSystem.ini` is `\r\n`) and preserves every byte it does not
  intentionally change — critical because the port's INI parser hard-crashes on
  malformed lines.
* **Idempotent:** each transformed file is prefixed with a `; FXEnhance v1`
  marker; re-running the transform on its own output refuses to double-apply.
* **Self-verifying:** the build fails loudly unless every changed line matches an
  allowed pattern (scaled `BurstCount`/`Size`/`Lifetime`, injected `LightPulse`
  blocks, or the marker), the line-ending convention is unchanged, and the
  block counts reconcile.

## Layers produced

| Archive | Destination | Precedence |
|---------|-------------|------------|
| `zzzz_FXEnhance.big` | `~/GeneralsX/mods/ShockWave/`, `~/GeneralsX/mods/ShockWaveSPE/` | mod dir: later-alpha wins; `zzzz_` sorts after every `zz*`/`zzz*` layer |
| `000_FXEnhanceZH.big` | `~/GeneralsX/GeneralsZH/` | game dir: earlier-alpha wins; `000_` precedent = `000_ShowHotkeysZH.big` |

The mod-dir sources are resolved from the ShockWaveSPE dir (its INIs are byte
identical to ShockWave's) using later-alphabetical precedence; the game-dir
source is `INIZH.big`.

## Build / rebuild

```sh
python3 build.py                        # guard, build, verify, install
python3 build.py --no-install           # build + verify to ./build only
python3 build.py --allow-layer-conflict # proceed past the layer guard (see below)
```

The build is fully re-runnable (deterministic regeneration).

**Important — rebuild after layer changes:** this mod composes on top of the
*current effective* `FXList.ini`/`ParticleSystem.ini` (it embeds the winning
lower layer's copy, per this mod stack's convention). If any FX-bearing layer
that ships these INIs (e.g. ChaosUnits, KwaiInfantry, TeslaCoil) is rebuilt,
reordered, added or removed, **rerun `python3 build.py
--allow-layer-conflict`** so the enhancement re-composes on the new effective
base — otherwise this layer keeps serving a stale embedded copy of the lower
layers' content.

### Layer-ordering guard

Before building, the script asserts that no *other* custom mod layer already
contains `ParticleSystem.ini` / `FXList.ini`. Because a `.big` overrides these
files **whole**, if another custom layer also ships them, whichever archive
wins alphabetically supplies the entire file — so stacking this mod on top
could clobber (or be clobbered against) that layer's FX/particle edits. If such
a layer is found the build **stops** and prints which ones, so a human can make
the ordering call. Re-run with `--allow-layer-conflict` once resolved; in that
mode the source is resolved from the current effective (winning) layer, so this
mod's enhancements compose on top of it.

## Uninstall

Delete the three installed archives:

```sh
rm ~/GeneralsX/mods/ShockWave/zzzz_FXEnhance.big
rm ~/GeneralsX/mods/ShockWaveSPE/zzzz_FXEnhance.big
rm ~/GeneralsX/GeneralsZH/000_FXEnhanceZH.big
```
