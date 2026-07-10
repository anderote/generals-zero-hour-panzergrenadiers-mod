#!/usr/bin/env python3
"""PHASE 2 (merge day): wire the ROTR infantry into the THEN-current
ShockWave stack.

build.py (phase 1) shipped an inert archive: object INIs, art, and baked
copies of the six shared INI files (Weapon / Armor / Locomotor / FXList /
ParticleSystem / ObjectCreationList) as of the side branch's build date —
but NO CommandSet.ini, CommandButton.ini or Generals.str.  This script,
run at merge time (after every other layer has landed and been rebuilt):

  1. re-extracts the current effective file space from the mod dir
     (excluding our own archive — idempotent),
  2. regenerates all six baked shared files from the CURRENT effective
     sources + the frozen fragments/ appends,
  3. builds CommandSet.ini  = current effective + our two unit sets
     appended + the Kwai Barracks sets patched with the two construct
     buttons (slots parameterized below),
  4. builds CommandButton.ini = current effective + our 6 buttons,
     Generals.str = current effective + our 14 entries,
  5. repacks zzz-ZZZZZZZRotrInfantry.big in place and re-runs the full
     static verification (phase-2 mode),
  6. with --install, copies the archive to both mod dirs.

Usage:
  python3 integrate.py [--shmel-slot 6] [--shock-slot 7]
                       [--mod-dir ~/GeneralsX/mods/ShockWaveSPE]
                       [--install]

The Barracks sets are discovered from the effective Tank_ChinaBarracks
object (its CommandSet plus every CommandSetUpgrade module), so the script
keeps working if intermediate layers rename or add set variants.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
FRAG_DIR = os.path.join(HERE, "fragments")
sys.path.insert(0, WORK)
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, os.path.join(HERE, "..", "chaos-units", "work"))

from bigfile import BigEntry, read_big, write_big_file  # noqa: E402
from iniblocks import load_tree, parse_blocks  # noqa: E402
import portdefs  # noqa: E402
import verify_lib  # noqa: E402

ARCHIVE = portdefs.ARCHIVE_NAME
SHARED = ["Weapon.ini", "Armor.ini", "Locomotor.ini", "FXList.ini",
          "ParticleSystem.ini", "ObjectCreationList.ini"]

APPEND_BANNER = ("\n\n; ===================================================================\n"
                 "; appended by rotr-infantry (integrate.py, merge day) -- ROTR Shmel\n"
                 "; Trooper + Shock Trooper closure.  Base content above is the\n"
                 "; effective copy at integration time.\n"
                 "; ===================================================================\n\n")


def frag(name):
    with open(os.path.join(FRAG_DIR, name + ".frag"), "rb") as f:
        return f.read()


def discover_barracks_sets(eff_ini_dir):
    """Return the command-set names used by the Kwai Barracks."""
    fp = os.path.join(eff_ini_dir, "Object", "China", "Tank", "Buildings",
                      "Barracks.ini")
    text = open(fp, "rb").read().decode("latin-1")
    m = re.search(r"^Object\s+Tank_ChinaBarracks\b(.*?)^End\s*$", text,
                  re.S | re.M)
    if not m:
        raise SystemExit("Tank_ChinaBarracks not found in effective Barracks.ini")
    body = m.group(1)
    sets = re.findall(r"^\s*CommandSet\s*=\s*([A-Za-z0-9_]+)", body, re.M)
    if not sets:
        raise SystemExit("no CommandSet references on Tank_ChinaBarracks")
    return sorted(set(sets))


def patch_barracks_sets(cs_text, set_names, slots):
    """Insert our construct buttons into each named set.  slots =
    [(slot, button), ...].  Fails if a slot is already occupied."""
    lines = cs_text.split("\n")
    blocks = {n: (a, b) for t, n, a, b, _bt in parse_blocks(cs_text)
              if t == "CommandSet"}
    inserts = {}   # line index (block End line) -> lines to insert before
    for sname in set_names:
        if sname not in blocks:
            raise SystemExit("barracks command set %s not found in CommandSet.ini"
                             % sname)
        a, b = blocks[sname]
        used = {}
        for i in range(a + 1, b):
            m = re.match(r"^\s*(\d+)\s*=\s*([A-Za-z0-9_]+)", lines[i])
            if m:
                used[int(m.group(1))] = (i, m.group(2))
        for slot, button in slots:
            if slot in used and used[slot][1] != button:
                raise SystemExit(
                    "slot %d of %s already holds %s — pick another slot "
                    "(--shmel-slot/--shock-slot)" % (slot, sname, used[slot][1]))
        new_lines = ["  %-2d = %s ; rotr-infantry" % (slot, button)
                     for slot, button in slots if slot not in used]
        # insert keeping ascending slot order: place right before End,
        # after the last numbered line <= our slot
        inserts.setdefault(b, []).extend(new_lines)
    out = []
    for i, line in enumerate(lines):
        if i in inserts:
            out.extend(inserts[i])
        out.append(line)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shmel-slot", type=int,
                    default=portdefs.BARRACKS_SLOT_DEFAULT_SHMEL)
    ap.add_argument("--shock-slot", type=int,
                    default=portdefs.BARRACKS_SLOT_DEFAULT_SHOCK)
    ap.add_argument("--mod-dir",
                    default=os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"))
    ap.add_argument("--install", action="store_true",
                    help="copy the rebuilt archive into both mod dirs")
    args = ap.parse_args()

    print("== extracting current effective space ==")
    subprocess.run([sys.executable, os.path.join(WORK, "extract_effective.py")],
                   check=True, stdout=subprocess.DEVNULL)
    eff_dir = os.path.join(WORK, "effective", "Data")
    eff_ini = os.path.join(eff_dir, "INI")

    # ---- read the phase-1 archive (object INIs + art travel unchanged)
    src_fp = os.path.join(HERE, ARCHIVE)
    entries = {e.path: e.data for e in read_big(src_fp)}

    # ---- 1-2: refresh the six shared files from current effective sources
    frag_texts = {}
    for fname in SHARED:
        base = open(os.path.join(eff_ini, fname), "rb").read()
        fr = frag(fname)
        entries["Data\\INI\\" + fname] = base + APPEND_BANNER.encode("latin-1") + fr
        frag_texts[fname] = fr.decode("latin-1")

    # ---- 3: CommandSet.ini (append unit sets + patch barracks slots)
    cs_base = open(os.path.join(eff_ini, "CommandSet.ini"), "rb").read()
    sets = discover_barracks_sets(eff_ini)
    print("Kwai Barracks sets discovered: %s" % ", ".join(sets))
    slots = [(args.shmel_slot, "Tank_Command_ConstructChinaInfantryShmelTrooper"),
             (args.shock_slot, "Tank_Command_ConstructChinaInfantryShockTrooper")]
    cs_patched = patch_barracks_sets(cs_base.decode("latin-1"), sets, slots)
    cs_final = cs_patched.encode("latin-1") + APPEND_BANNER.encode("latin-1") + \
        frag("CommandSet.ini")
    entries["Data\\INI\\CommandSet.ini"] = cs_final
    frag_texts["CommandSet.ini"] = frag("CommandSet.ini").decode("latin-1")

    # ---- 4: CommandButton.ini + Generals.str
    cb_base = open(os.path.join(eff_ini, "CommandButton.ini"), "rb").read()
    entries["Data\\INI\\CommandButton.ini"] = \
        cb_base + APPEND_BANNER.encode("latin-1") + frag("CommandButton.ini")
    frag_texts["CommandButton.ini"] = frag("CommandButton.ini").decode("latin-1")

    str_fp = os.path.join(eff_dir, "Generals.str")
    str_base = open(str_fp, "rb").read()
    entries["Data\\Generals.str"] = str_base + b"\n\n" + frag("Generals.str")
    frag_texts["Generals.str"] = frag("Generals.str").decode("latin-1")

    # ---- 5: repack + verify
    big_entries = [BigEntry(p, entries[p]) for p in sorted(entries, key=str.lower)]
    out_fp = os.path.join(HERE, ARCHIVE)
    write_big_file(big_entries, out_fp)
    print("repacked %s: %d files, %.1f MB" % (
        ARCHIVE, len(big_entries), os.path.getsize(out_fp) / 1e6))

    print("== verification (phase 2) ==")
    ddefs, dbyname = load_tree(portdefs.DONOR_INI)
    verify_lib.verify_all(out_fp, frag_texts, dbyname, phase2=True,
                          barracks_sets=sets, slots=slots)

    # ---- 6: install
    if args.install:
        for d in verify_lib.MOD_DIRS:
            shutil.copy2(out_fp, os.path.join(d, ARCHIVE))
            print("installed ->", os.path.join(d, ARCHIVE))
    else:
        print("NOT installed (rerun with --install to copy into the mod dirs)")
    print("INTEGRATE OK")


if __name__ == "__main__":
    main()
