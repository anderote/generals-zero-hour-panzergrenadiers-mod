import os, sys
sys.path.insert(0, os.path.expanduser('~/Documents/software/generalsx-mods/hotkey-addon'))
import bigfile
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
targets = [
 r'Data\INI\Object\China\Tank\Vehicles\BattleMaster.ini',
 r'Data\INI\Object\China\Tank\Vehicles\Emperor.ini',
 r'Data\INI\CommandSet.ini',
 r'Data\INI\CommandButton.ini',
 r'Data\INI\Upgrade.ini',
 r'Data\INI\Armor.ini',
 r'Data\Generals.str',
]
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)
for d in MODDIRS:
    print('====',d)
    eff={}
    for b in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d,b)):
            eff[e.path.lower()]=(b,len(e.data))
    for t in targets:
        o=eff.get(t.lower())
        print(f'  {t:60s} -> {o[0] if o else "MISSING"}  ({o[1] if o else 0} bytes)')
