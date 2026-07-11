import os, sys
sys.path.insert(0, os.path.expanduser("~/Documents/software/generalsx-mods/hotkey-addon"))
from bigfile import read_big

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
archives = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")), key=str.lower, reverse=True)
cache = {a: read_big(os.path.join(SPE,a)) for a in archives}

def effective(path):
    want = path.lower()
    for a in archives:
        for e in cache[a]:
            if e.path.lower() == want:
                return e.data, a
    return None, None

WANT = [
    "Data\\INI\\CommandSet.ini",
    "Data\\INI\\CommandButton.ini",
    "Data\\INI\\Upgrade.ini",
    "Data\\Generals.str",
    "Data\\INI\\SpecialPower.ini",
    "Data\\INI\\ObjectCreationList.ini",
    "Data\\INI\\Object\\China\\Tank\\Buildings\\InternetCenter.ini",
    "Data\\INI\\Object\\China\\Tank\\Buildings\\PropagandaCenter.ini",
]
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted")
os.makedirs(outdir, exist_ok=True)
for p in WANT:
    data, owner = effective(p)
    if data is None:
        print("MISSING:", p); continue
    fn = p.replace("\\", "__")
    open(os.path.join(outdir, fn), "wb").write(data)
    print("%-70s owner=%s  %d bytes" % (p, owner, len(data)))
