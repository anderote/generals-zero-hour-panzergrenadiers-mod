#!/usr/bin/env python3
"""Extract the effective INI/str file space of ~/GeneralsX/mods/ShockWaveSPE
into work/effective/ (INI/str only + full path->owner map for everything).

Read-only against the live mod dirs; excludes our own archive if present
(idempotent rebuilds).  Also indexes which archive owns every non-text path
(W3D / textures / audio presence checks read owners_all.json).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hotkey-addon"))
from bigfile import read_big

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
OUR = "zzz-zzzzzzzrotrinfantry.big"   # our own archive (any case)
OUT = os.path.join(HERE, "effective")

# CHANGELOG (merge day): STRICTLY-BELOW sourcing - only archives sorting
# below our own are read (was: everything except our own archive).  Layers
# that sort after us (zzz-ZZZZZZZTTeslaCoil / VehicleKit / WEconomy,
# zzzz_FXEnhance, zzz_ControlBarPro*) bake their own copies of the shared
# INI files ON TOP of ours and are rebuilt after integrate.py --install
# (fx-enhance is owned by another session and rebuilt there); deriving our
# baked files from a space that includes them would bake upper-layer
# content into this lower layer (layering inversion: their rebuilds would
# then re-append their own content on top of itself).  Matches the
# strictly-below sourcing the chain builds adopted in the kwai-infantry v2
# rework.
bigs = sorted([f for f in os.listdir(SPE) if f.lower().endswith(".big")
               and f.lower() < OUR], key=str.lower)
print("load order (later wins):")
for b in bigs:
    print("  ", b)

owner = {}   # lower path -> (real path, archive)
data = {}    # lower path -> bytes
for b in bigs:
    for e in read_big(os.path.join(SPE, b)):
        k = e.path.lower()
        owner[k] = (e.path, b)
        data[k] = e.data

os.makedirs(OUT, exist_ok=True)
n = 0
for k, (rp, arch) in owner.items():
    if not (k.endswith(".ini") or k.endswith(".str")):
        continue
    fp = os.path.join(OUT, rp.replace("\\", "/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "wb") as f:
        f.write(data[k])
    n += 1
with open(os.path.join(HERE, "owners.json"), "w") as f:
    json.dump({rp: arch for rp, arch in owner.values()}, f, indent=0)
print("wrote", n, "text files;", len(owner), "total paths in owner map")
