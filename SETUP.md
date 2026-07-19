# Installing on a new Apple Silicon Mac (transfer-bundle method)

This guide is written so that either a person or an AI agent can perform the
install end-to-end. It sets up the complete modded game — GeneralsX engine
fork + retail Zero Hour data + ShockWave + the Panzergrenadiers layer stack —
on a fresh Apple Silicon Mac, **without building anything from source**.

> **Agents**: follow the steps in order; each has a verification command with
> an expected result. The automated path is `./setup-macos.sh` (step 3), which
> performs steps 4–7 with checks. Do **not** launch the game yourself unless
> asked — hand the launcher to the user at the end.

## How this install works (read first)

This repo does **not** contain the game. It contains the mod layers
(`*/zz*.big`), build tooling, and this guide. A playable install is four
stacked pieces:

| Piece | What it is | Where it comes from |
|---|---|---|
| Engine | `GeneralsXZH` arm64 binary + bundled dylibs (SDL3, MoltenVK, DXVK, SagePatch), built from the [anderote/GeneralsX](https://github.com/anderote/GeneralsX) fork | transfer bundle |
| Game data | retail C&C Generals: Zero Hour files (Steam app 2732960) | transfer bundle (owner must have a retail license) |
| ShockWave | ShockWave 1.201 mod archives (+ SPE campaign overlay) | transfer bundle |
| This mod | the `zzz-*.big` layer archives | transfer bundle (already installed inside it) — also tracked in this repo |

All four arrive together as a single **transfer bundle**: a copy of a working
`~/GeneralsX` folder (~13 GB, or ~11.7 GB without the optional `donors/` and
`tools/` dev directories) delivered on a USB drive or external disk.

**Why not the official GeneralsX releases?** This mod stack requires the
custom engine fork: `SagePatch.ini` uses veterancy rank 5–8 keys
(`HealthBonus_Heroic2..5`, `WeaponBonus = HERO2..`) that **crash stock
engines**. The binary in the transfer bundle is the correct fork build —
use it, don't substitute a downloaded release.

## Prerequisites

- Apple Silicon Mac (`uname -m` → `arm64`); macOS 15+ (developed on macOS 26)
- ~15 GB free disk space
- Admin rights (for Homebrew)
- The transfer bundle (a `GeneralsX` folder, e.g. on a mounted USB drive at
  `/Volumes/<drive>/GeneralsX`)

Expected transfer-bundle layout:

```
GeneralsX/
├── GeneralsZH/          # game data + GeneralsXZH binary + run.sh + *.dylib (~2.9 GB)
│   ├── GeneralsXZH      #   the engine binary (arm64, ad-hoc signed)
│   ├── run.sh           #   launch wrapper (sets DYLD paths, Vulkan ICD, fontconfig)
│   ├── MoltenVK_icd.json
│   └── Data/ ...        #   retail ZH data + loose INI overrides
├── mods/
│   ├── ShockWave/       # ShockWave 1.201 + this repo's layer archives (54 .big)
│   └── ShockWaveSPE/    # SPE campaign overlay + same layers (57 .big)  ← default -mod target
├── donors/              # OPTIONAL, dev-only donor art (~1.4 GB) — skippable
└── tools/               # OPTIONAL, dev tooling (~82 MB) — skippable
```

## Step 1 — Homebrew dependencies

The engine binary links **ffmpeg** and **libpng** at absolute
`/opt/homebrew/opt/...` paths (everything else is bundled beside the binary).

```bash
# install Homebrew first if missing: https://brew.sh
brew install ffmpeg libpng
```

**Verify** (both files must exist — the binary wants these exact majors):

```bash
ls /opt/homebrew/opt/ffmpeg/lib/libavformat.62.dylib \
   /opt/homebrew/opt/libpng/lib/libpng16.16.dylib
```

If `libavformat.62` is missing because Homebrew's ffmpeg moved past major
version 8, install the versioned formula (e.g. `brew install ffmpeg@8`) and
symlink, or rebuild the engine against current ffmpeg (last resort — see the
fork repo).

## Step 2 — Get this repo

```bash
git clone https://github.com/anderote/generals-zero-hour-panzergrenadiers-mod.git ~/src/generalsx-mods
cd ~/src/generalsx-mods
```

## Step 3 — Run the installer

```bash
# with the USB drive mounted:
./setup-macos.sh /Volumes/<drive>/GeneralsX
# or, if ~/GeneralsX was already copied by hand:
./setup-macos.sh
```

The script performs steps 4–7 below with verification, and creates a
double-clickable `~/Desktop/Play GeneralsX ZH.command` launcher. If it
succeeds you can skip to **Step 8 — First launch**. The manual equivalents
follow, for transparency and for recovering from partial failures.

## Step 4 (manual) — Place the bundle

Copy the bundle to `~/GeneralsX` — the path matters; scripts and the engine
resolve it relative to `$HOME`:

```bash
rsync -a --exclude donors --exclude tools "/Volumes/<drive>/GeneralsX/" "$HOME/GeneralsX/"
```

**Verify**: `test -x ~/GeneralsX/GeneralsZH/run.sh && ls ~/GeneralsX/mods/ShockWaveSPE/*.big | wc -l` → 50+.

## Step 5 (manual) — De-quarantine and re-sign

macOS SIGKILLs copied ad-hoc-signed binaries at launch until they are
re-signed, and quarantines everything that arrived from external media:

```bash
xattr -dr com.apple.quarantine ~/GeneralsX 2>/dev/null || true
codesign --force --sign - ~/GeneralsX/GeneralsZH/GeneralsXZH \
  ~/GeneralsX/GeneralsZH/*.dylib
```

**Verify**: `codesign -v ~/GeneralsX/GeneralsZH/GeneralsXZH && echo OK` → `OK`.

## Step 6 (manual) — Engine config (SagePatch.ini)

The veterancy curves and QoL settings live outside the bundle, in the app
support directory. The exact file ships in this repo:

```bash
mkdir -p "$HOME/Library/Application Support/GeneralsX/GeneralsZH"
cp config/SagePatch.ini "$HOME/Library/Application Support/GeneralsX/GeneralsZH/SagePatch.ini"
```

Do **not** copy `Options.ini` from the source machine — it embeds the source
machine's LAN IP and display resolution. The game regenerates it; settings
are chosen in-game.

## Step 7 (manual) — Launcher

Canonical launch command (this is what the `.command` launcher runs, with
the resolution auto-detected):

```bash
cd ~/GeneralsX/GeneralsZH && ./run.sh -fullscreen -xres 3440 -yres 1440 \
  -forcefullviewport -mod ~/GeneralsX/mods/ShockWaveSPE
```

- Set `-xres/-yres` to the display's resolution.
- `-mod ~/GeneralsX/mods/ShockWave` for plain ShockWave (no SPE campaign overlay).
- `-win` instead of `-fullscreen` for windowed (useful for first-run testing).
- FPS overlay: prefix with `DXVK_HUD=fps` (off by default; see run.sh).

## Step 8 — First launch

1. Double-click `Play GeneralsX ZH.command` on the Desktop (or run the
   command above).
2. If Gatekeeper still blocks it: **System Settings → Privacy & Security →
   "Open Anyway"**, then launch again.
3. **Success criteria**: the shell map behind the main menu is the Kwai
   showcase scene (Chinese tank base, not the vanilla/ShockWave shellmap).
   In a skirmish as **China Tank General (Kwai)**, the Barracks builds
   **Panzergrenadier** in slot 1 (not Red Guard) and the Tank Hunter button
   reads **Panzerjäger**.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Binary dies instantly, `zsh: killed`, or SIGKILL in Console | Signature invalidated by the copy — redo Step 5 (`codesign --force --sign -`). |
| `dyld: Library not loaded: /opt/homebrew/opt/ffmpeg/...` | Step 1 missing or ffmpeg major mismatch — see Step 1 verify. |
| "App can't be opened" Gatekeeper dialog | Quarantine attr — redo Step 5 `xattr`, or Privacy & Security → Open Anyway. |
| Game runs but vanilla units / no Panzergrenadier | Launched without `-mod`, or mod dir path wrong. Use the launcher. |
| Crash on startup mentioning veterancy/INI keys | Wrong binary (stock engine) with our SagePatch.ini — use the bundle's `GeneralsXZH`, not a downloaded release. |
| Crash mid-game | Crash reports land in `~/Library/Application Support/GeneralsX/GeneralsZH/ReleaseCrashInfo.txt` — the fork's crash handler logs object template + module + backtrace. File it with that attached. |
| Black screen / swap-chain errors with FPS HUD | Known MoltenVK limitation — unset `DXVK_HUD`. |

## No transfer bundle? (from-scratch path)

Everything can be rebuilt from sources instead — engine fork build, game
data via DepotDownloader (requires owning ZH on Steam, app 2732960),
ShockWave 1.201 download, then this repo's layers. That path is documented
in [README.md → "Applying this from scratch"](README.md#applying-this-from-scratch)
and takes ~1–2 hours vs ~15 minutes for the bundle method.

## Licensing note

The transfer bundle contains retail game data. C&C Generals: Zero Hour is
~$5 on Steam — the person playing should own a copy.
