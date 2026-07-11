import os, sys
sys.path.insert(0, os.path.expanduser('~/Documents/software/generalsx-mods/hotkey-addon'))
import bigfile
MOD = os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)
def effective(moddir, upto=None):
    eff={}
    for b in sorted_bigs(moddir):
        if upto and b.lower()>=upto.lower(): continue
        for e in bigfile.read_big(os.path.join(moddir,b)):
            eff[e.path.lower()]=(b,e.data)
    return eff
if __name__=='__main__':
    cmd=sys.argv[1]
    eff=effective(MOD)
    if cmd=='owner':
        for p in sys.argv[2:]:
            k=p.lower()
            print(eff[k][0] if k in eff else 'MISSING', p)
    elif cmd=='extract':
        p=sys.argv[2]; out=sys.argv[3]
        open(out,'wb').write(eff[p.lower()][1])
        print('wrote',out,'from',eff[p.lower()][0],len(eff[p.lower()][1]),'bytes')
