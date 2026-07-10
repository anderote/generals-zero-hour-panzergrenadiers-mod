#!/usr/bin/env python3
"""Build 000_ShowHotkeysZH.big — makes command-button hotkeys visible.

Pipeline:
  1. Extract Data\\English\\generals.csf from EnglishZH.big.
  2. Verify the CSF parser round-trips the unmodified file byte-identically.
  3. For every label starting with "CONTROLBAR:" (case-insensitive) whose
     first string contains '&' followed by an alphanumeric character,
     append " [X]" (X = that character uppercased) to the end of the
     string's first line. Idempotent: skips strings whose first line
     already ends with such a hint.
  4. Pack the modified CSF (same internal path) into 000_ShowHotkeysZH.big.
     The "000_" prefix sorts before "EnglishZH.big" so it wins: the engine
     loads *.big alphabetically (FilenameList is a case-insensitive
     std::set) and on duplicate internal paths the first-loaded archive
     wins (multimap append + instance-0 lookup, see README).
  5. Write the archive next to this script and copy it into the game dir.
"""

import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bigfile
import csf as csflib

GAME_DIR = os.path.expanduser("~/GeneralsX/GeneralsZH")
SOURCE_BIG = os.path.join(GAME_DIR, "EnglishZH.big")
INTERNAL_PATH = "Data\\English\\generals.csf"
OUTPUT_NAME = "000_ShowHotkeysZH.big"
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

HOTKEY_RE = re.compile(r"&([0-9A-Za-z])")
EXISTING_HINT_RE = re.compile(r" \[[0-9A-Z]\]$")


def add_hint(text: str):
    """Return (new_text, hotkey) or (text, None) if no change needed."""
    m = HOTKEY_RE.search(text)
    if not m:
        return text, None
    hotkey = m.group(1).upper()

    nl = text.find("\n")
    first_line, rest = (text, "") if nl < 0 else (text[:nl], text[nl:])
    cr = first_line.endswith("\r")
    if cr:
        first_line = first_line[:-1]
    if EXISTING_HINT_RE.search(first_line):
        return text, None  # already has a hint — idempotent
    first_line += f" [{hotkey}]"
    if cr:
        first_line += "\r"
    return first_line + rest, hotkey


def main():
    # 1. extract
    entries = bigfile.read_big(SOURCE_BIG)
    entry = bigfile.find_entry(entries, INTERNAL_PATH)
    original_csf_bytes = entry.data
    print(f"Extracted {entry.path} ({len(original_csf_bytes)} bytes) "
          f"from {SOURCE_BIG}")

    # 2. round-trip check on the unmodified file
    csf = csflib.parse(original_csf_bytes)
    if csflib.serialize(csf) != original_csf_bytes:
        raise SystemExit("FATAL: CSF round-trip is not byte-identical")
    print(f"CSF round-trip byte-identical OK "
          f"({len(csf.labels)} labels, {csf.num_strings} strings)")

    # 3. modify
    modified = 0
    samples = []
    for label in csf.labels:
        if not label.name.decode("latin-1").lower().startswith("controlbar:"):
            continue
        if not label.strings:
            continue
        s = label.strings[0]  # engine only uses the first string
        new_text, hotkey = add_hint(s.text)
        if hotkey is not None and new_text != s.text:
            if len(samples) < 5:
                samples.append((label.name.decode("latin-1"),
                                s.text, new_text))
            s.text = new_text
            modified += 1
    print(f"Modified {modified} CONTROLBAR strings")

    # 4. pack
    new_csf_bytes = csflib.serialize(csf)
    csflib.parse(new_csf_bytes)  # sanity: still parses
    out_big = bigfile.write_big(
        [bigfile.BigEntry(INTERNAL_PATH, new_csf_bytes)])

    work_out = os.path.join(WORK_DIR, OUTPUT_NAME)
    with open(work_out, "wb") as f:
        f.write(out_big)
    print(f"Wrote {work_out} ({len(out_big)} bytes)")

    # 5. install
    game_out = os.path.join(GAME_DIR, OUTPUT_NAME)
    shutil.copyfile(work_out, game_out)
    print(f"Installed {game_out}")

    # verification: re-open with our own reader, re-parse, compare
    check_entries = bigfile.read_big(game_out)
    check_entry = bigfile.find_entry(check_entries, INTERNAL_PATH)
    check_csf = csflib.parse(check_entry.data)
    assert len(check_csf.labels) == len(csf.labels)

    orig_csf = csflib.parse(original_csf_bytes)
    changed = unchanged_identical = mismatched = 0
    for old_l, new_l in zip(orig_csf.labels, check_csf.labels):
        assert old_l.name == new_l.name
        old_texts = [s.text for s in old_l.strings]
        new_texts = [s.text for s in new_l.strings]
        if old_texts == new_texts:
            # unmodified entry: serialized bytes must be identical
            one_old = csflib.serialize(csflib.CsfFile(3, 0, b"", [old_l]))
            one_new = csflib.serialize(csflib.CsfFile(3, 0, b"", [new_l]))
            if one_old == one_new:
                unchanged_identical += 1
            else:
                mismatched += 1
        else:
            changed += 1
    print(f"Verification: {changed} changed entries parse correctly, "
          f"{unchanged_identical} unchanged entries byte-identical, "
          f"{mismatched} mismatches")
    assert changed == modified and mismatched == 0

    print("\nSample before -> after:")
    for name, old, new in samples:
        print(f"  {name}\n    before: {old!r}\n    after:  {new!r}")


if __name__ == "__main__":
    main()
