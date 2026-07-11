import os, sys, re
sys.path.insert(0, os.path.expanduser("~/Documents/software/generalsx-mods/hotkey-addon"))
from bigfile import read_big
SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
archives = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")), key=str.lower, reverse=True)
pat = re.compile(sys.argv[1].encode(), re.I)
ctx = int(sys.argv[2]) if len(sys.argv)>2 else 0
seen=set()
for a in archives:
    for e in read_big(os.path.join(SPE,a)):
        if not e.path.lower().endswith(".ini"): continue
        if e.path.lower() in seen: continue
        if pat.search(e.data):
            seen.add(e.path.lower())
            lines = e.data.decode("latin-1").splitlines()
            for i,l in enumerate(lines):
                if pat.search(l.encode()):
                    print("%s [%s] :%d" % (e.path, a, i+1))
                    for j in range(max(0,i-ctx), min(len(lines), i+ctx+1)):
                        print("   ", lines[j])
