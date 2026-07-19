import os, sys, re
sys.path.insert(0, os.path.expanduser('~/Documents/software/generalsx-mods/hotkey-addon'))
import bigfile
def die(m): print('AUDIT FAIL:', m); sys.exit(1)
for D in [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
          os.path.expanduser('~/GeneralsX/mods/ShockWave')]:
    eff={}
    for b in sorted((f for f in os.listdir(D) if f.lower().endswith('.big')),key=str.lower):
        for e in bigfile.read_big(os.path.join(D,b)):
            eff[e.path.lower()]=(b,e.data)
    def txt(p): return eff[p.lower()][1].decode('latin-1')
    ini='\n'.join(v.decode('latin-1') for p,(b,v) in eff.items() if p.endswith('.ini'))
    strs='\n'.join(v.decode('latin-1') for p,(b,v) in eff.items() if p.endswith('.str'))
    mapped='\n'.join(v.decode('latin-1') for p,(b,v) in eff.items() if '\\mappedimages\\' in p)
    ARCH='zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big'
    # our files must be effectively owned by our archive
    for p in [r'data\ini\object\china\tank\vehicles\battlemaster.ini', r'data\ini\commandset.ini',
              r'data\ini\commandbutton.ini', r'data\ini\upgrade.ini', r'data\ini\armor.ini', r'data\generals.str']:
        if eff[p][0]!=ARCH: die(f'{D}: {p} not owned by us ({eff[p][0]})')
    ups=['Tank_Upgrade_BattleMasterReactiveArmor','Tank_Upgrade_BattleMasterHull','Tank_Upgrade_BattleMasterShield']
    cbs=['Tank_Command_UpgradeBattleMasterReactiveArmor','Tank_Command_UpgradeBattleMasterHull','Tank_Command_UpgradeBattleMasterShield']
    bm=txt(r'data\ini\object\china\tank\vehicles\battlemaster.ini')
    cs=txt(r'data\ini\commandset.ini')
    for u in ups:
        if not re.search(r'^Upgrade\s+%s\b'%u, ini, re.M): die(f'{u} undefined')
        if u not in bm: die(f'{u} not gated on Battlemaster')
    for c in cbs:
        if not re.search(r'^CommandButton\s+%s\b'%c, ini, re.M): die(f'{c} undefined')
        # on all 4 BM command sets
        for name in ['Tank_ChinaVehicleBattleMasterCommandSet','Tank_ChinaVehicleBattleMasterCommandSetERA',
                     'Tank_ChinaVehicleBattleMasterCommandSetPDL','Tank_ChinaVehicleBattleMasterCommandSetTower']:
            blk=re.search(r'^CommandSet\s+%s\b.*?^End'%name, cs, re.M|re.S).group(0)
            if c not in blk: die(f'{c} missing from {name}')
    # armor closure
    if not re.search(r'^Armor\s+Tank_BattleMasterReactiveArmor\b', ini, re.M): die('reactive armor undefined')
    if 'Armor           = Tank_BattleMasterReactiveArmor' not in bm: die('armorset not repointed')
    # cameos + labels
    for cam in ['SNTankTitaniumArmor','SSCompositeArmor','SSMammothShield']:
        if not re.search(r'^MappedImage\s+%s\s*$'%cam, mapped, re.M): die(f'cameo {cam} missing')
    for base in ['BattleMasterReactiveArmor','BattleMasterHull','BattleMasterShield']:
        for lab in ['UPGRADE:'+base,'CONTROLBAR:Upgrade'+base,'CONTROLBAR:ToolTipUpgrade'+base]:
            if not re.search(r'^%s$'%re.escape(lab), strs, re.M): die(f'label {lab} missing')
    # prior-layer survival across FULL stack
    if 'MaxHealth       = 400' not in bm: die('rebalance BM 400 HP cut lost')
    emp=txt(r'data\ini\object\china\tank\vehicles\emperor.ini')
    if 'MaxHealth       = 1100' not in emp: die('rebalance Emperor 1100 HP cut lost')
    if 'ModuleTag_EDS_Shield01' not in emp: die('Emperor energy-shield module lost')
    for tok in ['ModuleTag_PropTowerMount01','ModuleTag_KPDL_Mount01','ModuleTag_GP_Crew01','ModuleVet_01']:
        if tok not in bm: die(f'BM prior module {tok} lost')
    print(f'{D}: COMBINED-STACK CLOSURE OK')
print('ALL COMBINED-STACK AUDITS PASSED')
