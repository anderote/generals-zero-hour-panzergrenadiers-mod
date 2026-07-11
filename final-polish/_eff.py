"""Effective-stack resolver for the Panzergrenadier ShockWave stack."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hotkey-addon"))
from bigfile import read_big

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
# later-alphabetical (case-insensitive) wins -> iterate reverse-sorted, first hit wins
ARCHIVES = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")),
                  key=str.lower, reverse=True)
_CACHE = {a: read_big(os.path.join(SPE, a)) for a in ARCHIVES}

def effective(path):
    want = path.lower().replace("/", "\\")
    for a in ARCHIVES:
        for e in _CACHE[a]:
            if e.path.lower().replace("/", "\\") == want:
                return e.data.decode("latin-1"), a
    return None, None

def all_paths():
    seen = {}
    for a in ARCHIVES:
        for e in _CACHE[a]:
            lp = e.path.lower()
            if lp not in seen:
                seen[lp] = (e.path, a)
    return seen

if __name__ == "__main__":
    txt, owner = effective(sys.argv[1])
    if txt is None:
        print("NOT FOUND"); sys.exit(1)
    sys.stderr.write("owner: %s  (%d bytes)\n" % (owner, len(txt)))
    sys.stdout.write(txt)
