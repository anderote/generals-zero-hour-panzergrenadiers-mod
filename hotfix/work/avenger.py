import os, sys, re
sys.path.insert(0, '/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon')
import bigfile
MODDIR = os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
bigs = sorted([f for f in os.listdir(MODDIR) if f.lower().endswith('.big')], key=str.lower)
# effective space for avenger + tomahawk missile
eff = {}
for b in bigs:
    for e in bigfile.read_big(os.path.join(MODDIR,b)):
        low = e.path.lower()
        if low.endswith('.ini'):
            eff[low] = (b, e.data)
hits = []
for p,(b,d) in eff.items():
    t = d.decode('latin-1')
    if 'PointDefenseLaserUpdate' in t:
        for m in re.finditer(r'Object\s+(\S+)(.*?)\nEnd', t, re.S):
            if 'PointDefenseLaserUpdate' in m.group(2):
                mm = re.search(r'PrimaryTargetTypes\s*=\s*([^\n;]+)', m.group(2))
                sm = re.search(r'SecondaryTargetTypes\s*=\s*([^\n;]+)', m.group(2))
                hits.append((m.group(1), p, b, mm and mm.group(1).strip(), sm and sm.group(1).strip()))
for h in hits: print(h)
# tomahawk missile kindof
for p,(b,d) in eff.items():
    t = d.decode('latin-1')
    for name in ['TomahawkMissile','ScudTransport','Object .*Scud']:
        for m in re.finditer(r'Object\s+(\w*Tomahawk\w*Missile\w*|\w*ScudMissile\w*)\b(.*?)\nEnd\n', t, re.S):
            k = re.findall(r'\n\s*KindOf\s*=\s*([^\n;]+)', m.group(2))
            if k: print('KINDOF', m.group(1), p.split('\\')[-1], b, k[0].strip())
        break
