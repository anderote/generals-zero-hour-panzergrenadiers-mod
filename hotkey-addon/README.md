# Show Hotkeys addon for C&C Generals Zero Hour (GeneralsX)

Makes command-button hotkeys visible in the UI text. The game marks a
hotkey with a `&` before a letter in a command-button label (e.g.
`&Guard`), which is normally only shown as an underline in tooltips.
This addon appends an explicit ` [X]` hint to every such string, e.g.
`&Guard` becomes `&Guard [G]`, so the hotkey is readable on build-menu
tooltips and labels. 317 `CONTROLBAR:` strings are modified; everything
else in `generals.csf` is byte-identical to the original.

## How it works

- `Data\English\generals.csf` is extracted from `EnglishZH.big`,
  patched, and repacked into `000_ShowHotkeysZH.big` with the same
  internal path.
- Override priority: the engine loads `*.big` files in case-insensitive
  alphabetical order (`FilenameList` is a `std::set` with
  `rts::less_than_nocase`, `Core/GameEngine/Include/Common/FileSystem.h:66`).
  When two archives contain the same internal path, the entry is
  appended to a multimap (`ArchiveFileSystem::loadIntoDirectoryTree`,
  `Core/GameEngine/Source/Common/System/ArchiveFileSystem.cpp:158-169`)
  and lookups take instance 0 = the first-inserted entry
  (`getArchiveFile`, same file lines 318-331). So the alphabetically
  first archive wins — `000_ShowHotkeysZH.big` sorts before
  `EnglishZH.big` and overrides it. (Same trick as ShockWave's `!`
  prefix and Control Bar Pro's `340_` prefix.)

## Files

- `bigfile.py` — BIGF archive reader/writer (stdlib only).
- `csf.py` — CSF string-file reader/writer; round-trips the shipped
  file byte-identically. Strings are UTF-16LE with every byte
  bitwise-NOTed (XOR 0xFF).
- `build_hotkey_addon.py` — the build pipeline (extract, patch, pack,
  install, verify).

## Rebuild

```sh
python3 build_hotkey_addon.py
```

Requires Python 3 (stdlib only) and the game data at
`~/GeneralsX/GeneralsZH/EnglishZH.big`. The script writes
`000_ShowHotkeysZH.big` to this directory and copies it into
`~/GeneralsX/GeneralsZH/`. It is idempotent: strings that already end
with a ` [X]` hint are left alone.

## Uninstall

Delete the addon archive from the game directory:

```sh
rm ~/GeneralsX/GeneralsZH/000_ShowHotkeysZH.big
```

No other game files are touched.
