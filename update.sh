#!/bin/bash
# One-command updater for an existing GeneralsX + Panzergrenadiers install.
# Pulls the latest mod layers + engine config from this repo and the latest
# play-build engine binary from GitHub Releases, then installs everything.
# Run it from a clone of this repo on the target Mac (Allison's updater):
#   cd ~/src/generalsx-mods && ./update.sh
# Requirements: the game was installed once via setup-macos.sh (or the
# transfer bundle) so ~/GeneralsX exists; network access; git.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GAME_DIR="$HOME/GeneralsX/GeneralsZH"
APPSUP="$HOME/Library/Application Support/GeneralsX/GeneralsZH"
RELEASE_URL="https://github.com/anderote/GeneralsX/releases/latest/download/GeneralsXZH"

step() { printf '\n==> %s\n' "$*"; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

[[ -f "$GAME_DIR/run.sh" ]] || fail "no install at $GAME_DIR -- run setup-macos.sh first (see SETUP.md)"
pgrep -x GeneralsXZH >/dev/null && fail "the game is running -- quit it first"

step "Pulling latest mod repo"
git -C "$REPO_DIR" pull --ff-only

step "Installing mod layers into both mod dirs"
# Every layer dir tracks its built archive; the effective stack is the union.
count=0
for big in "$REPO_DIR"/*/zz*.big; do
    [[ -e "$big" ]] || continue
    for d in "$HOME/GeneralsX/mods/ShockWaveSPE" "$HOME/GeneralsX/mods/ShockWave"; do
        [[ -d "$d" ]] && cp "$big" "$d/"
    done
    count=$((count+1))
done
echo "    $count layer archives installed"

step "Installing engine config (SagePatch.ini)"
mkdir -p "$APPSUP"
cp "$REPO_DIR/config/SagePatch.ini" "$APPSUP/SagePatch.ini"

step "Retiring stock script files that shadow ShockWave's AI"
# The depot-downloaded base game ships loose Data/Scripts files; loose files
# beat archives, so they shadow ShockWave's SkirmishScripts.scb -- which is
# why ShockWave's added generals (Armor/Leang/Salvage) had no AI at all.
for f in SkirmishScripts.scb MultiplayerScripts.scb Scripts.ini; do
    p="$GAME_DIR/Data/Scripts/$f"
    if [[ -f "$p" ]]; then
        mv "$p" "$p.stock-backup"
        echo "    $f -> $f.stock-backup"
    fi
done

step "Installing shared maps"
if [[ -d "$REPO_DIR/maps" ]]; then
    mkdir -p "$APPSUP/Maps"
    cp -R "$REPO_DIR/maps/"* "$APPSUP/Maps/"
    echo "    $(ls "$REPO_DIR/maps" | wc -l | tr -d ' ') map folders synced"
fi

step "Downloading latest play-build engine binary"
TMP="$(mktemp -d)"
curl -fsSL -o "$TMP/GeneralsXZH" "$RELEASE_URL" || fail "binary download failed"
[[ -s "$TMP/GeneralsXZH" ]] || fail "downloaded binary is empty"
mv "$TMP/GeneralsXZH" "$GAME_DIR/GeneralsXZH"
chmod +x "$GAME_DIR/GeneralsXZH"
xattr -d com.apple.quarantine "$GAME_DIR/GeneralsXZH" 2>/dev/null || true
codesign --force --sign - "$GAME_DIR/GeneralsXZH"
codesign -v "$GAME_DIR/GeneralsXZH" || fail "codesign verification failed"

printf '\nDone. Launch the game as usual.\n'
printf 'NOTE: multiplayer/LAN requires BOTH players to run update.sh before playing\n'
printf 'together -- the game has no version handshake and mismatched builds crash.\n'
