#!/usr/bin/env python3
"""Build zzyzy_NoAISuperweapons.big and install it into both ShockWave mod dirs.

The archive contains a single file, Data\\INI\\Default\\AIData.ini, extracted
from !Shw_scripts.big with every superweapon Structure block in the
SkirmishBuildList sections commented out (see src/AIData.ini{,.orig}).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "hotkey-addon"))
from bigfile import BigEntry, write_big_file  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "zzyzy_NoAISuperweapons.big"
INSTALL_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
]


def main():
    data = open(os.path.join(HERE, "src", "AIData.ini"), "rb").read()
    entries = [BigEntry("Data\\INI\\Default\\AIData.ini", data)]
    out = os.path.join(HERE, "build", NAME)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    write_big_file(entries, out)
    print(f"built {out} ({os.path.getsize(out)} bytes)")
    for d in INSTALL_DIRS:
        dest = os.path.join(d, NAME)
        with open(out, "rb") as fsrc, open(dest, "wb") as fdst:
            fdst.write(fsrc.read())
        print(f"installed {dest}")


if __name__ == "__main__":
    main()
