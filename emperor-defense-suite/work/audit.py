import os, re, sys
sys.path.insert(0, os.path.expanduser('~/Documents/software/generalsx-mods/hotkey-addon'))
import bigfile
MOD=os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE')
def sorted_bigs(d): return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')),key=str.lower)
eff={}
for b in sorted_bigs(MOD):
    for e in bigfile.read_big(os.path.join(MOD,b)):
        eff[e.path.lower()]=(b,e.data)
ini='\n'.join(d.decode('latin-1') for p,(b,d) in eff.items() if p.endswith('.ini'))
strs='\n'.join(d.decode('latin-1') for p,(b,d) in eff.items() if p.endswith('.str'))
mapped='\n'.join(d.decode('latin-1') for p,(b,d) in eff.items() if '\\mappedimages\\' in p)
fails=[]
def has(pat,text=ini,flags=re.M): 
    return re.search(pat,text,flags) is not None
def want(cond,msg):
    if not cond: fails.append(msg)

# who owns the touched files now?
for f in ['data\\ini\\object\\china\\tank\\vehicles\\emperor.ini','data\\ini\\commandset.ini',
          'data\\ini\\commandbutton.ini','data\\ini\\upgrade.ini','data\\ini\\weapon.ini','data\\generals.str']:
    print('OWNER', eff[f][0], f.split('\\')[-1])

# --- my objects/weapons/upgrades/buttons defined exactly once (in my archive) ---
ARCH='zzz-ZZZZZZZZZZZZ0EmperorDefense.big'
for w in ['Tank_EmperorPDLWeapon','Tank_EmperorABMWeapon']:
    want(len(re.findall(r'^Weapon\s+%s\b'%w,ini,re.M))==1, f'{w} not defined exactly once')
for u in ['Tank_Upgrade_EmperorPDL','Tank_Upgrade_EmperorABM','Tank_Upgrade_EmperorShield','Tank_Upgrade_EmperorFleetShield']:
    want(len(re.findall(r'^Upgrade\s+%s\b'%u,ini,re.M))==1, f'{u} not defined exactly once')
for c in ['Tank_Command_UpgradeEmperorPDL','Tank_Command_UpgradeEmperorABM','Tank_Command_UpgradeEmperorShield','Tank_Command_UpgradeEmperorFleetShield']:
    want(len(re.findall(r'^CommandButton\s+%s\b'%c,ini,re.M))==1, f'{c} not defined exactly once')

# --- closure: WF page-2 set: every button resolves to a CommandButton ---
m=re.search(r'^CommandSet\s+Tank_ChinaWarFactoryCommandSet_Down\b(.*?)^End',ini,re.M|re.S)
for slot,btn in re.findall(r'^\s*(\d+)\s*=\s*(\S+)',m.group(1),re.M):
    want(has(r'^CommandButton\s+%s\b'%re.escape(btn)), f'WF page2 slot {slot} button {btn} unresolved')

# --- closure: buttons -> upgrades ; upgrades -> cameos ; RequiredUpgrade -> exists ---
for c,u,cam in [('Tank_Command_UpgradeEmperorPDL','Tank_Upgrade_EmperorPDL','SNBlackSharkJammer'),
                ('Tank_Command_UpgradeEmperorABM','Tank_Upgrade_EmperorABM','SARocketAvenger'),
                ('Tank_Command_UpgradeEmperorShield','Tank_Upgrade_EmperorShield','SSMammothShield'),
                ('Tank_Command_UpgradeEmperorFleetShield','Tank_Upgrade_EmperorFleetShield','SAPopupPatriot')]:
    want(has(r'^Upgrade\s+%s\b'%u), f'{u} missing')
    want(has(r'^MappedImage\s+%s\s*$'%cam,mapped), f'cameo {cam} missing')
for a,b in [('Tank_Upgrade_EmperorABM','Tank_Upgrade_EmperorPDL'),('Tank_Upgrade_EmperorFleetShield','Tank_Upgrade_EmperorShield')]:
    blk=re.search(r'^Upgrade\s+%s\b(.*?)^End'%a,ini,re.M|re.S).group(1)
    want('RequiredUpgrade    = %s'%b in blk, f'{a} must RequiredUpgrade {b}')

# --- closure: Emperor modules -> weapons/upgrades ; weapon FX/armor ---
emp=re.search(r'^Object\s+Tank_ChinaTankEmperor\b(.*?)^End\s*$',ini,re.M|re.S)
# use the winning copy explicitly
emp_txt=eff['data\\ini\\object\\china\\tank\\vehicles\\emperor.ini'][1].decode('latin-1')
for t in ['ModuleTag_EDS_PDL01','ModuleTag_EDS_ABM01','ModuleTag_EDS_Shield01','ModuleTag_EDS_Shield02','ModuleTag_EDS_Fleet01']:
    want(t in emp_txt, f'Emperor missing my module {t}')
want('TriggeredBy   = Tank_Upgrade_EmperorPDL' in emp_txt,'PDL module trigger')
want('UpgradeRequired               = Tank_Upgrade_EmperorFleetShield' in emp_txt,'Fleet UpgradeRequired')
for w in ['Tank_EmperorPDLWeapon','Tank_EmperorABMWeapon']:
    want(w in emp_txt, f'Emperor missing reaction weapon ref {w}')
want(has(r'^FXList\s+WeaponFX_AvengerPointDefenseLaser\b'),'Avenger FX missing')
want(has(r'^FXList\s+FX_EmperorPropagandaPulse\b'),'pulse FX missing')

# --- prior-layer survival across whole stack ---
for n in ['ModuleTag_GP_Crew01','ModuleTag_GP_Crew03','ModuleTag_ShtoraAuto01','ModulePropaganda_15',
          'MaxHealth       = 1320.0','Behavior = HelixContain ModuleTag_06','ModuleTag_KPDL_Mount01',
          'ModuleTag_07']:
    want(n in emp_txt, f'Emperor prior hunk lost: {n}')
# drop-ladder owns SpecialPower/OCL/IP still
want(eff['data\\ini\\specialpower.ini'][0]=='zzz-ZZZZZZZZZZZ1DropLadder.big','DropLadder SP owner')
want(eff['data\\ini\\object\\china\\tank\\buildings\\industrialplant.ini'][0]=='zzz-ZZZZZZZZZZZ1DropLadder.big','DropLadder IP owner')
# grenadier IP research buttons + drop buttons still in commandset
cs=eff['data\\ini\\commandset.ini'][1].decode('latin-1')
for n in ['Tank_Command_UpgradeGrenadierPanzergrenadiers','Tank_Command_GrenadierDrop','Tank_Command_UpgradeKwaiPDL']:
    want(n in cs, f'CommandSet lost {n}')

# --- weapon sanity: my weapons carry RadiusDamageAffects ENEMIES + LASER ---
for w in ['Tank_EmperorPDLWeapon','Tank_EmperorABMWeapon']:
    blk=re.search(r'^Weapon\s+%s\b(.*?)^End'%w,ini,re.M|re.S).group(1)
    want('DamageType          = LASER' in blk, f'{w} not LASER')
    want('RadiusDamageAffects = ENEMIES' in blk, f'{w} not ENEMIES-only')

print('FAILS:', len(fails))
for f in fails: print('  -',f)
print('COMBINED-STACK CLOSURE:', 'OK' if not fails else 'FAILED')
