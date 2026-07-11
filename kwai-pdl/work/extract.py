#!/usr/bin/env python3
"""Extract the effective INI/STR space from ShockWaveSPE into work/effective/,
recording per-file owners in owners.json."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hotkey-addon"))
from bigfile import read_big

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
OUT = os.path.join(HERE, "effective")
EXCLUDE = {"zzz-zzzzzzzkwaipdl.big"}  # never self-source

archives = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")
                   and f.lower() not in EXCLUDE), key=str.lower, reverse=True)
owners = {}
for a in archives:
    for e in read_big(os.path.join(SPE, a)):
        lp = e.path.lower()
        if not lp.endswith((".ini", ".str")):
            continue
        if lp in owners:
            continue
        owners[lp] = {"owner": a, "path": e.path}
        fp = os.path.join(OUT, e.path.replace("\\", "/"))
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(e.data)
json.dump(owners, open(os.path.join(HERE, "owners.json"), "w"), indent=1)
print("extracted", len(owners), "effective INI/STR files from", len(archives), "archives")
