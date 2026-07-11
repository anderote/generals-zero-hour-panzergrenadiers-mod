import os, sys
sys.path.insert(0, '/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon')
import bigfile

MODDIR = os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
bigs = sorted([f for f in os.listdir(MODDIR) if f.lower().endswith('.big')], key=str.lower)
print("Archive order (low->high priority):")
for b in bigs: print("  ", b)

targets = {
    'data\\ini\\commandset.ini': [],
    'data\\ini\\commandbutton.ini': [],
}
# also find any path containing these basenames
interest = ['internetcenter.ini', 'pdlpod.ini', 'troopcrawler.ini', 'hacker']
found = {}
for b in bigs:
    entries = bigfile.read_big(os.path.join(MODDIR, b))
    for e in entries:
        low = e.path.lower()
        if low in targets:
            targets[low].append(b)
        base = low.rsplit('\\',1)[-1]
        for pat in interest:
            if pat in base:
                found.setdefault(low, []).append(b)
print("\nFixed-name targets:")
for k,v in targets.items():
    print(k, "-> owners:", v)
print("\nInterest paths:")
for k,v in sorted(found.items()):
    print(k, "->", v)
