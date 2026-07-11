import os, sys, re
sys.path.insert(0, os.path.expanduser("~/Documents/software/generalsx-mods/hotkey-addon"))
from bigfile import read_big
SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
archives = sorted((f for f in os.listdir(SPE) if f.lower().endswith(".big")), key=str.lower, reverse=True)
needles = [b"AmericaVehicleSpyDrone", b"PredatorDrone", b"SurveillanceUAV"]
seen = {}
for a in archives:
    for e in read_big(os.path.join(SPE,a)):
        if not e.path.lower().endswith((".ini",".str")): continue
        for n in needles:
            if n in e.data:
                isdef = re.search(rb"(?m)^Object\s+" + n, e.data)
                key=(n,e.path)
                if key not in seen:
                    seen[key]=a
                    print("%-28s %-70s %s %s" % (n.decode(), e.path, a, "DEFINES" if isdef else ""))
