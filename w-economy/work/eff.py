#!/usr/bin/env python3
"""Effective-file helper: highest-priority archive per path in ShockWaveSPE."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hotkey-addon"))
from bigfile import read_big

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
EXCLUDE = {"zzz-zzzzzzzweconomy.big"}
archives = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")
                   and f.lower() not in EXCLUDE), key=str.lower, reverse=True)
_cache = {}
def arc(a):
    if a not in _cache:
        _cache[a] = read_big(os.path.join(SPE, a))
    return _cache[a]

def effective(path):
    want = path.lower().replace("/", "\\")
    for a in archives:
        for e in arc(a):
            if e.path.lower() == want:
                return e.data.decode("latin-1"), a
    return None, None

def all_paths(suffixes=(".ini", ".str")):
    seen = {}
    for a in archives:
        for e in arc(a):
            lp = e.path.lower()
            if lp.endswith(suffixes) and lp not in seen:
                seen[lp] = (e.path, a)
    return seen

if __name__ == "__main__":
    if sys.argv[1] == "get":
        data, a = effective(sys.argv[2])
        sys.stderr.write("OWNER: %s\n" % a)
        sys.stdout.write(data if data else "")
    elif sys.argv[1] == "owner":
        for p in sys.argv[2:]:
            print(p, "->", effective(p)[1])
    elif sys.argv[1] == "ls":
        pat = sys.argv[2].lower()
        for lp, (p, a) in sorted(all_paths().items()):
            if pat in lp:
                print(a.ljust(34), p)
