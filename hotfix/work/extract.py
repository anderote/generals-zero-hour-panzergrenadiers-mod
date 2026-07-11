import os, sys
sys.path.insert(0, '/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon')
import bigfile

MODDIR = os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
OUT = '/Users/andrewcote/Documents/software/generalsx-mods/hotfix/work/src'
os.makedirs(OUT, exist_ok=True)

want = {
  'data\\ini\\commandset.ini': ('zzz-ZZZZZZZWEconomy.big', 'CommandSet.ini'),
  'data\\ini\\object\\china\\tank\\buildings\\internetcenter.ini': ('zzz-ZZZZZZZWEconomy.big', 'InternetCenter.ini'),
  'data\\ini\\object\\china\\tank\\vehicles\\pdlpod.ini': ('zzz-ZZZZZZZKwaiPDL.big', 'PDLPod.ini'),
  'data\\ini\\object\\china\\tank\\infantry\\hacker.ini': ('zzz-ZZZZZZZWEconomy.big', 'TankHacker.ini'),
  'data\\ini\\object\\china\\vanilla\\infantry\\hacker.ini': ('zzz-ZZZZZZZWEconomy.big', 'VanillaHacker.ini'),
  'data\\ini\\object\\china\\vanilla\\vehicles\\troopcrawler.ini': ('zzyy_ChinaBunkers.big', 'TroopCrawler.ini'),
  'data\\ini\\commandbutton.ini': ('zzz-ZZZZZZZWEconomy.big', 'CommandButton.ini'),
}
for arch in set(a for a,_ in want.values()):
    entries = bigfile.read_big(os.path.join(MODDIR, arch))
    bypath = {e.path.lower(): e for e in entries}
    for p,(a,outname) in want.items():
        if a != arch: continue
        e = bypath.get(p)
        assert e, (arch, p)
        open(os.path.join(OUT, outname),'wb').write(e.data)
        print(outname, len(e.data), 'from', arch, 'as', e.path)

# also: list FXEnhance + ControlBarPro contents to prove no overlap with shipped paths
for a in ['zzzz_FXEnhance.big','zzz_ControlBarProZH.big','zzz_ControlBarPro2160ZH.big']:
    entries = bigfile.read_big(os.path.join(MODDIR,a))
    print('\n', a, len(entries), 'entries')
    for e in entries[:400]:
        print('   ', e.path)
