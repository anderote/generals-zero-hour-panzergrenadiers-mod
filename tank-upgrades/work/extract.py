import os, sys
sys.path.insert(0, os.path.expanduser('~/Documents/software/generalsx-mods/hotkey-addon'))
import bigfile
D = os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)
eff={}
for b in sorted_bigs(D):
    for e in bigfile.read_big(os.path.join(D,b)):
        eff[e.path.lower()]=e.data
out = os.path.join('work','eff')
os.makedirs(out, exist_ok=True)
files = {
 'BattleMaster.ini': r'Data\INI\Object\China\Tank\Vehicles\BattleMaster.ini',
 'Emperor.ini': r'Data\INI\Object\China\Tank\Vehicles\Emperor.ini',
 'CommandSet.ini': r'Data\INI\CommandSet.ini',
 'CommandButton.ini': r'Data\INI\CommandButton.ini',
 'Upgrade.ini': r'Data\INI\Upgrade.ini',
 'Armor.ini': r'Data\INI\Armor.ini',
 'Generals.str': r'Data\Generals.str',
}
for name,p in files.items():
    open(os.path.join(out,name),'wb').write(eff[p.lower()])
    print(name, len(eff[p.lower()]))
