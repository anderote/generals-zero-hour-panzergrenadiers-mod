#!/bin/bash
# Installs the Panzergrenadiers modded GeneralsX stack on an Apple Silicon Mac
# from a transfer bundle (a copied working ~/GeneralsX folder). See SETUP.md.
#
# Usage:
#   ./setup-macos.sh [/path/to/transfer/GeneralsX]
#
# With an argument, the bundle is rsynced to ~/GeneralsX first (donors/ and
# tools/ are skipped — dev-only). Without one, ~/GeneralsX must already exist.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/GeneralsX"
GAME_DIR="$DEST/GeneralsZH"
APPSUP="$HOME/Library/Application Support/GeneralsX/GeneralsZH"
SRC="${1:-}"

step()  { printf '\n==> %s\n' "$*"; }
fail()  { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

step "Checking machine"
[[ "$(uname -m)" == "arm64" ]] || fail "Apple Silicon (arm64) required; this is $(uname -m)"

step "Checking Homebrew dependencies (ffmpeg, libpng)"
command -v brew >/dev/null 2>&1 || fail "Homebrew not installed — install from https://brew.sh first"
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list libpng >/dev/null 2>&1 || brew install libpng
# The binary links these exact majors at absolute paths (see SETUP.md step 1).
for lib in /opt/homebrew/opt/ffmpeg/lib/libavformat.62.dylib \
           /opt/homebrew/opt/libpng/lib/libpng16.16.dylib; do
    [[ -e "$lib" ]] || fail "$lib missing — Homebrew ffmpeg/libpng major version mismatch (SETUP.md step 1)"
done

if [[ -n "$SRC" ]]; then
    step "Copying bundle from $SRC to $DEST (~12 GB, this takes a while)"
    [[ -d "$SRC/GeneralsZH" ]] || fail "$SRC does not look like a GeneralsX bundle (no GeneralsZH/ inside)"
    rsync -a --exclude donors --exclude tools "$SRC/" "$DEST/"
fi

step "Verifying bundle layout at $DEST"
[[ -f "$GAME_DIR/GeneralsXZH" ]] || fail "$GAME_DIR/GeneralsXZH missing — copy the bundle first (SETUP.md step 4)"
[[ -f "$GAME_DIR/run.sh" ]] || fail "$GAME_DIR/run.sh missing"
MOD_DIR="$DEST/mods/ShockWaveSPE"
[[ -d "$MOD_DIR" ]] || MOD_DIR="$DEST/mods/ShockWave"
[[ -d "$MOD_DIR" ]] || fail "no mod dir found under $DEST/mods"
BIGS=$(find "$MOD_DIR" -maxdepth 1 -name '*.big' | wc -l | tr -d ' ')
[[ "$BIGS" -ge 40 ]] || fail "$MOD_DIR has only $BIGS .big archives — incomplete copy?"

step "Removing quarantine attributes"
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true

step "Re-signing binary and dylibs (copied binaries SIGKILL until re-signed)"
codesign --force --sign - "$GAME_DIR/GeneralsXZH" "$GAME_DIR"/*.dylib
codesign -v "$GAME_DIR/GeneralsXZH" || fail "codesign verification failed"

step "Installing SagePatch.ini (veterancy curves + engine QoL)"
mkdir -p "$APPSUP"
if [[ -f "$APPSUP/SagePatch.ini" ]] && ! cmp -s "$REPO_DIR/config/SagePatch.ini" "$APPSUP/SagePatch.ini"; then
    cp "$APPSUP/SagePatch.ini" "$APPSUP/SagePatch.ini.bak"
    echo "    (existing SagePatch.ini differed — backed up to SagePatch.ini.bak)"
fi
cp "$REPO_DIR/config/SagePatch.ini" "$APPSUP/SagePatch.ini"

step "Creating Desktop launcher"
XRES=1920; YRES=1080
RES_LINE=$(system_profiler SPDisplaysDataType 2>/dev/null | awk '/Resolution:/ {print $2, $4; exit}')
if [[ "$RES_LINE" =~ ^[0-9]+\ [0-9]+$ ]]; then
    XRES=${RES_LINE% *}; YRES=${RES_LINE#* }
fi
LAUNCHER="$HOME/Desktop/Play GeneralsX ZH.command"
cat > "$LAUNCHER" <<EOF
#!/bin/bash
cd "\$HOME/GeneralsX/GeneralsZH" && ./run.sh -fullscreen -xres $XRES -yres $YRES \\
  -forcefullviewport -mod "$MOD_DIR"
EOF
chmod +x "$LAUNCHER"

printf '\nDone.\n'
printf '  Mod dir:    %s\n' "$MOD_DIR"
printf '  Resolution: %sx%s (edit the launcher to change)\n' "$XRES" "$YRES"
printf '  Launcher:   %s\n' "$LAUNCHER"
printf '\nDouble-click the launcher to play. If macOS blocks the first launch:\n'
printf 'System Settings -> Privacy & Security -> "Open Anyway", then retry.\n'
printf 'Success check: main-menu background is the Kwai tank-base showcase, and\n'
printf 'the Kwai Barracks builds "Panzergrenadier" in slot 1. See SETUP.md step 8.\n'
