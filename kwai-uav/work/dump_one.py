import os, sys
sys.path.insert(0, os.path.expanduser("~/Documents/software/generalsx-mods/hotkey-addon"))
from bigfile import read_big
SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
archives = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")), key=str.lower, reverse=True)
def effective(path):
    want=path.lower()
    for a in archives:
        for e in read_big(os.path.join(SPE,a)):
            if e.path.lower()==want: return e.data, a
    return None,None
for p in sys.argv[1:]:
    data,owner=effective(p)
    fn=p.replace("\\","__")
    open(os.path.join("work/extracted",fn),"wb").write(data)
    print(p,"owner=",owner,len(data),"bytes")
