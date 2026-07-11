import os, sys
sys.path.insert(0, os.path.expanduser('~/Documents/software/generalsx-mods/hotkey-addon'))
import bigfile
MOD=os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
def sorted_bigs(d): return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')),key=str.lower)
eff={}
for b in sorted_bigs(MOD):
    for e in bigfile.read_big(os.path.join(MOD,b)):
        eff[e.path.lower()]=(b,e.data)
os.makedirs('effall',exist_ok=True)
import json
open('effall/_index.json','w').write(json.dumps({k:v[0] for k,v in eff.items()}))
# concatenate all ini+str for grepping, prefixed with filename markers
with open('effall/ALLINI.txt','w') as out:
    for k in sorted(eff):
        if k.endswith('.ini'):
            out.write('\n\n##### FILE: %s (owner %s) #####\n'%(k,eff[k][0]))
            out.write(eff[k][1].decode('latin-1'))
print('done', len(eff),'files')
