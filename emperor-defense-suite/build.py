#!/usr/bin/env python3
"""zzz-ZZZZZZZZZZZZ0EmperorDefense.big -- the Emperor Defense Suite
(ShockWave / GeneralsX), for Kwai (China Tank General).

Four researchable, RequiredUpgrade-chained DEFENSIVE systems layered onto Kwai's
Emperor Overlord tank (Tank_ChinaTankEmperor), all ADDED on top of the crewed
Emperor shipped by the grenadier package (grenadier-research owns Emperor.ini):

  1. Hull Point-Defense Laser (PDL)   $1500/40s   -- reactive anti-missile LASER burst
  2. ABM Interceptor Array (req PDL)  $2500/60s   -- stronger/wider, anti-ballistic too
  3. Projected Energy Shield          $2500/50s   -- +2000 HP absorption buffer + recharge
  4. Fleet Shield Projection (req 3)  $2000/45s   -- projected regen field to nearby fleet

Two chains via the deployed engine's RequiredUpgrade field (GeneralsMD
Upgrade.cpp canAffordUpgrade prereq gate): PDL->ABM and Shield->Fleet. Chain
buttons grey out until their prereq is owned.

ENGINE IDIOMS (all pure data, evidence in effective ShockWave/vanilla + engine src):
  * PDL/ABM: FireWeaponWhenDamagedBehavior (a full UpgradeMux -> StartsActive=No +
    TriggeredBy is a clean off/on gate; the Emperor's own Shtora APS uses this exact
    module). Its reaction weapon forceFireWeapon()s a burst centred on the Emperor
    (FireWeaponWhenDamagedBehavior.cpp onDamage: forceFireWeapon(obj, obj->getPosition()).
    The burst weapon is DamageType=LASER (Armor.ini: LASER 0% vs TankArmor = the
    Emperor is unhurt, 100% vs ProjectileArmor = incoming missiles die, 50% vs
    BallisticMissileArmor) with RadiusDamageAffects=ENEMIES (Weapon.cpp
    WEAPON_AFFECTS_ENEMIES) so ONLY hostile projectiles/units in radius are hit --
    no self- or friendly-fire. Reuses the Avenger PDL fire FX
    (WeaponFX_AvengerPointDefenseLaser). Reactive point-defense (see README for why
    proactive PointDefenseLaserUpdate could not be ADDED gate-ably on this hull).
  * Shield: MaxHealthUpgrade (+2000, ADD_CURRENT_HEALTH_TOO) -- the ShockWave Mammoth
    'Energy Shield' idiom (Upgrade_AmericaEnergyShieldGenerator = ArmorUpgrade +
    MaxHealthUpgrade + shield FX), scaled up; plus a gated AutoHealBehavior recharge
    (the Industrial Plant's Automated-Repair idiom).
  * Fleet: a 2nd PropagandaTowerBehavior gated by UpgradeRequired with base heal 0%
    -> upgraded 2% (the Overlord speaker-tower heal-aura template the spec names as
    cleanest; the engine has no pure-data 'grant armor to nearby units' aura).

Host: War Factory page-2 (Tank_ChinaWarFactoryCommandSet_Down) slots 8-11 -- the
ONLY Kwai structure with contiguous free slots (Propaganda Center is 14/14 across
58 variants; Industrial Plant has only 3 exit slots for 4 buttons). Documented
deviation from 'Prop Center/Industrial Plant'; the War Factory (advanced-vehicle
page) hosts Emperor vehicle-defense tech and has a ProductionUpdate for upgrades.

Sorts ABOVE the 11-Z grenadier layers (12 Z's + '0') and BELOW
zzz_ControlBarPro*/zzzz_FXEnhance. Reads effective sources from
~/GeneralsX/mods/ShockWaveSPE. Depends on ../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZZ0EmperorDefense.big'   # 12 Z's + '0'
TAG = 'zzz-ZZZZZZZZZZZZ0EmperorDefense'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

GR = 'zzz-zzzzzzzzzzz0grenadierresearch.big'   # Layer 1 of grenadier package
DL = 'zzz-zzzzzzzzzzz1dropladder.big'          # Layer 2 of grenadier package

P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'
P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_UPG = 'Data\\INI\\Upgrade.ini'
P_WPN = 'Data\\INI\\Weapon.ini'
P_STR = 'Data\\Generals.str'

EXPECT_OWNER = {
    P_EMP.lower(): GR,
    P_CS.lower():  DL,
    P_CB.lower():  DL,
    P_UPG.lower(): GR,
    P_WPN.lower(): 'zzz-zzzzzzzzpanzergrenadier.big',
    P_STR.lower(): DL,
}
SHIPPED = [P_EMP, P_CS, P_CB, P_UPG, P_WPN, P_STR]

# ---- new identifiers ------------------------------------------------------
UP_PDL   = 'Tank_Upgrade_EmperorPDL'
UP_ABM   = 'Tank_Upgrade_EmperorABM'
UP_SHLD  = 'Tank_Upgrade_EmperorShield'
UP_FLEET = 'Tank_Upgrade_EmperorFleetShield'
CB_PDL   = 'Tank_Command_UpgradeEmperorPDL'
CB_ABM   = 'Tank_Command_UpgradeEmperorABM'
CB_SHLD  = 'Tank_Command_UpgradeEmperorShield'
CB_FLEET = 'Tank_Command_UpgradeEmperorFleetShield'
W_PDL    = 'Tank_EmperorPDLWeapon'
W_ABM    = 'Tank_EmperorABMWeapon'
MODTAGS  = ['ModuleTag_EDS_PDL01', 'ModuleTag_EDS_ABM01', 'ModuleTag_EDS_Shield01',
            'ModuleTag_EDS_Shield02', 'ModuleTag_EDS_Fleet01']

NEW_IDS = [UP_PDL, UP_ABM, UP_SHLD, UP_FLEET, CB_PDL, CB_ABM, CB_SHLD, CB_FLEET,
           W_PDL, W_ABM] + MODTAGS
NEW_LABELS = []
for base in ['EmperorPDL', 'EmperorABM', 'EmperorShield', 'EmperorFleetShield']:
    NEW_LABELS += ['UPGRADE:' + base, 'CONTROLBAR:Upgrade' + base,
                   'CONTROLBAR:ToolTipUpgrade' + base]

CAMEOS = {'PDL': 'SNBlackSharkJammer', 'ABM': 'SARocketAvenger',
          'SHLD': 'SSMammothShield', 'FLEET': 'SAPopupPatriot'}

def die(msg):
    print('BUILD FAILED:', msg); sys.exit(1)
def check(cond, msg):
    if not cond: die(msg)
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)

# ---------------------------------------------------------------- sort order
for d in MODDIRS:
    names = sorted_bigs(d)
    probe = sorted(set(names) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE)
    below = set(probe[:i]); above = set(probe[i+1:])
    for need in ['zzz-ZZZZZZZZZZZ0GrenadierResearch.big', 'zzz-ZZZZZZZZZZZ1DropLadder.big',
                 'zzz-ZZZZZZZZZZPassengerSurvival.big', 'zzz-ZZZZZZZZPanzergrenadier.big']:
        check(need in below, f'{d}: {need} must sort below us (got above/absent)')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (above grenadier layers, below ControlBarPro*/FXEnhance)')

# ------------------------------------------------- effective space (primary)
def load_effective(moddir):
    eff = {}
    for b in sorted_bigs(moddir):
        if str.lower(b) >= ARCHIVE.lower():
            continue
        for e in bigfile.read_big(os.path.join(moddir, b)):
            eff[e.path.lower()] = (b, e.data)
    return eff

eff = load_effective(PRIMARY)
for p, owner in EXPECT_OWNER.items():
    check(p in eff, f'missing effective file {p}')
    check(eff[p][0].lower() == owner, f'{p}: effective owner drifted: {eff[p][0]} (expected {owner})')
print('effective ownership OK:', {p.split(chr(92))[-1]: eff[p][0] for p in EXPECT_OWNER})

for d in MODDIRS:
    for b in sorted_bigs(d):
        if str.lower(b) <= ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        for p in SHIPPED:
            check(p.lower() not in claimed, f'{d}/{b} (sorts above us) claims {p}')
print('no higher-sorting archive claims any shipped path')

# ------------------------------------------ collision + drift + resolution
all_ini = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                    if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_ini),
          f'identifier collision: {ident} already exists in effective space')
print('new identifiers collision-free (%d ids, %d labels)' % (len(NEW_IDS), len(NEW_LABELS)))

# donor-idiom drift guards (the facts every mechanism rests on)
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items() if '\\mappedimages\\' in p)
for img in CAMEOS.values():
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M), f'cameo MappedImage missing: {img}')
for snd in ['MoneyWithdraw', 'ReaperVoiceUpgrade']:
    check(re.search(r'^AudioEvent\s+%s\b' % snd, all_ini, re.M), f'AudioEvent {snd} missing')
check(re.search(r'^FXList\s+WeaponFX_AvengerPointDefenseLaser\b', all_ini, re.M), 'Avenger PDL FireFX missing')
check(re.search(r'^FXList\s+FX_EmperorPropagandaPulse\b', all_ini, re.M), 'Emperor propaganda pulse FX missing')
# Avenger PDL weapon proves LASER anti-missile idiom
av = re.search(r'^Weapon\s+AvengerPointDefenseLaserOne\b(.*?)^End', all_ini, re.M | re.S)
check(av and 'DamageType          = LASER' in av.group(1) and 'AntiSmallMissile    = Yes' in av.group(1),
      'Avenger PDL weapon idiom drifted')
# armour-table facts the LASER burst rests on
def armor_val(name, dtype):
    m = re.search(r'^Armor\s+%s\b(.*?)^End' % name, all_ini, re.M | re.S)
    check(m, f'armor {name} missing')
    v = re.search(r'^\s*Armor\s*=\s*%s\s+(\d+)%%' % dtype, m.group(1), re.M)
    return int(v.group(1)) if v else None
check(armor_val('TankArmor', 'LASER') == 0, 'TankArmor LASER not 0% (self-damage guard)')
check(armor_val('ProjectileArmor', 'LASER') == 100, 'ProjectileArmor LASER not 100% (missiles must die)')
# ShockWave energy-shield idiom present (evidence for the shield mechanism)
check(re.search(r'^Upgrade\s+Upgrade_AmericaEnergyShieldGenerator\b', all_ini, re.M),
      'ShockWave energy-shield upgrade (idiom evidence) missing')
# FireWeaponWhenDamagedBehavior in use on the effective Emperor (Shtora) -> module valid here
print('donor-idiom drift guards OK (Avenger PDL LASER, armour table, energy-shield, pulse FX, cameos, sounds)')

# ---------------------------------------------------------------- helpers
def audit(label, old, new, exp_removed, exp_added):
    o = [l.rstrip('\r\n') for l in old.decode('latin-1').splitlines()]
    n = [l.rstrip('\r\n') for l in new.decode('latin-1').splitlines()]
    co, cn = Counter(o), Counter(n)
    removed = list((co - cn).elements()); added = list((cn - co).elements())
    check(sorted(removed) == sorted(exp_removed),
          f'{label}: removed-line audit mismatch:\n got {sorted(removed)}\n exp {sorted(exp_removed)}')
    check(sorted(added) == sorted(exp_added),
          f'{label}: added-line audit mismatch:\n got {sorted(added)}\n exp {sorted(exp_added)}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')

def get_block(text, kind, name, label):
    m = re.search(r'^%s\s+%s\b[^\n]*\n(.*?)^End[ \t\r]*$' % (kind, re.escape(name)), text, re.M | re.S)
    check(m, f'{label}: {kind} {name} missing'); return m

# ===================================================== Emperor.ini modules
EMP_MODS = [
    f'  ; ------------------------------------------------------------------------------',
    f'  ; {TAG}: Emperor Defense Suite -- 4 gated defensive systems (ADDED; all prior',
    f'  ; modules -- crew, Shtora, propaganda, gattling/PDL riders, doctrine -- preserved).',
    f'  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_EDS_PDL01 ; {TAG}: System 1 Hull Point-Defense Laser (reactive anti-missile LASER burst; Shtora APS idiom)',
    f'    StartsActive  = No',
    f'    TriggeredBy   = {UP_PDL}',
    f'    DamageTypes   = ALL',
    f'    ReactionWeaponPristine      = {W_PDL}',
    f'    ReactionWeaponDamaged       = {W_PDL}',
    f'    ReactionWeaponReallyDamaged = {W_PDL}',
    f'    DamageAmount    = 40  ; only heavy hits (rockets/missiles/shells) trigger the pulse',
    f'  End',
    f'  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_EDS_ABM01 ; {TAG}: System 2 ABM Interceptor Array (stronger/wider, also anti-ballistic; requires PDL)',
    f'    StartsActive  = No',
    f'    TriggeredBy   = {UP_ABM}',
    f'    DamageTypes   = ALL',
    f'    ReactionWeaponPristine      = {W_ABM}',
    f'    ReactionWeaponDamaged       = {W_ABM}',
    f'    ReactionWeaponReallyDamaged = {W_ABM}',
    f'    DamageAmount    = 25  ; wider trigger window -> more interceptor pulses',
    f'  End',
    f'  Behavior = MaxHealthUpgrade ModuleTag_EDS_Shield01 ; {TAG}: System 3 Projected Energy Shield -- +2000 absorption buffer (Mammoth Energy-Shield idiom, scaled)',
    f'    TriggeredBy   = {UP_SHLD}',
    f'    AddMaxHealth  = 2000.0',
    f'    ChangeType    = ADD_CURRENT_HEALTH_TOO',
    f'  End',
    f'  Behavior = AutoHealBehavior ModuleTag_EDS_Shield02 ; {TAG}: System 3 shield recharge (Automated-Repair idiom)',
    f'    StartsActive  = No',
    f'    TriggeredBy   = {UP_SHLD}',
    f'    HealingAmount = 40',
    f'    HealingDelay  = 1000',
    f'  End',
    f'  Behavior = PropagandaTowerBehavior ModuleTag_EDS_Fleet01 ; {TAG}: System 4 Fleet Shield Projection -- gated regen field to nearby fleet (speaker-tower idiom; requires Shield)',
    f'    Radius                        = 200.0',
    f'    DelayBetweenUpdates           = 2000',
    f'    HealPercentEachSecond         = 0%   ; gated OFF until researched (UpgradeRequired toggles the upgraded rate)',
    f'    UpgradeRequired               = {UP_FLEET}',
    f'    UpgradedHealPercentEachSecond = 2%   ; projected shield regen once researched',
    f'    PulseFX                       = FX_EmperorPropagandaPulse',
    f'    UpgradedPulseFX               = FX_EmperorPropagandaPulse',
    f'    AffectsSelf                   = No',
    f'  End',
]
emp_src = eff[P_EMP.lower()][1]
emp_text = emp_src.decode('latin-1')
# preserve every prior-layer hunk (fail loudly if any drifted away before we edit)
EMP_SURVIVE = ['MaxHealth       = 1320.0', 'Behavior = HelixContain ModuleTag_06',
               'Slots                   = 8', 'ModulePropaganda_15', 'ModuleTag_ShtoraAuto01',
               'Behavior = ObjectCreationUpgrade ModuleTag_07', 'ModuleTag_KPDL_Mount01',
               'ModuleTag_KPDL_CmdSet01', 'ModuleTag_GP_Crew01', 'ModuleTag_GP_Crew03',
               'ModuleTag_KD_Armor1', 'Behavior = VeterancyGainCreate ModuleTag_23',
               'ModuleTag_23', 'ModuleTag_Taunt02']
for n in EMP_SURVIVE:
    check(n in emp_text, f'Emperor prior-layer hunk missing before edit: {n!r}')
for t in MODTAGS:
    check(t not in emp_text, f'Emperor already has module tag {t}')
geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', emp_text, re.M))
check(len(geo) == 1, f'Emperor: need exactly one Geometry=BOX anchor (found {len(geo)})')
ins = geo[0].start()
emp_new_text = emp_text[:ins] + '\n'.join(EMP_MODS) + '\n' + emp_text[ins:]
emp_new = emp_new_text.encode('latin-1')
audit('Emperor.ini (+5 defense modules)', emp_src, emp_new, [], EMP_MODS)
# survival after edit
for n in EMP_SURVIVE:
    check(n in emp_new_text, f'Emperor prior-layer hunk lost after edit: {n!r}')
check(len(re.findall(r'Behavior\s*=\s*FireWeaponWhenDamagedBehavior\b', emp_new_text)) == 3,
      'expected 3 FireWeaponWhenDamagedBehavior (Shtora + PDL + ABM)')
check(len(re.findall(r'Behavior\s*=\s*PropagandaTowerBehavior\b', emp_new_text)) == 2,
      'expected 2 PropagandaTowerBehavior (innate tower + fleet aura)')
print('Emperor.ini: 5 defense modules inserted; all prior-layer hunks survive')

# ===================================================== Weapon.ini append
def weapon_block(name, dmg, radius, delay, extra):
    out = [f'Weapon {name}', f'  PrimaryDamage       = {dmg}', f'  PrimaryDamageRadius = {radius}',
           f'  AttackRange         = {radius}', '  DamageType          = LASER',
           '  DeathType           = LASERED', '  WeaponSpeed         = 999999.0',
           f'  DelayBetweenShots   = {delay}', '  ClipSize            = 0', '  ClipReloadTime      = 0',
           '  AcceptableAimDelta  = 180', '  RadiusDamageAffects = ENEMIES  ; no self/friendly fire',
           '  AntiSmallMissile    = Yes', '  AntiProjectile      = Yes', '  AntiAirborneVehicle = Yes']
    out += extra
    out += ['  FireFX              = WeaponFX_AvengerPointDefenseLaser', 'End']
    return '\n'.join(out)
WPN_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: Emperor point-defense burst weapons (LASER = 0% vs TankArmor,\n'
              '; 100% vs ProjectileArmor; RadiusDamageAffects=ENEMIES). Fired by the\n'
              '; FireWeaponWhenDamagedBehavior reaction modules on the Emperor.\n' +
    weapon_block(W_PDL, '100.0', '30.0', '1000', []) + '\n\n' +
    weapon_block(W_ABM, '250.0', '70.0', '800',
                 ['  AntiBallisticMissile= Yes  ; ABM upgrade intercepts SCUD/ballistic-class too']) + '\n')
wpn_src = eff[P_WPN.lower()][1]
check(wpn_src.endswith(b'\n'), 'Weapon.ini must end with newline to append')
wpn_new = wpn_src + WPN_APPEND.encode('latin-1')
check(wpn_new.startswith(wpn_src), 'Weapon.ini not append-only')
check(WPN_APPEND.count('\nWeapon ') == 2, 'Weapon append balance')
print('Weapon.ini: +2 point-defense burst weapons appended')

# ===================================================== Upgrade.ini append
def upgrade_block(name, display, cost, time, cameo, req=None):
    out = [f'Upgrade {name}', f'  DisplayName        = {display}', '  Type               = PLAYER',
           f'  BuildTime          = {time}', f'  BuildCost          = {cost}',
           f'  ButtonImage        = {cameo}', '  ResearchSound      = ReaperVoiceUpgrade']
    if req:
        out.append(f'  RequiredUpgrade    = {req} ; {TAG}: sequential prereq gate (deployed engine field, GeneralsMD Upgrade.cpp)')
    out.append('End')
    return '\n'.join(out)
UPG_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: four Emperor-defence researches (Type=PLAYER); two RequiredUpgrade chains.\n' +
    upgrade_block(UP_PDL,   'UPGRADE:EmperorPDL', 1500, 40.0, CAMEOS['PDL']) + '\n\n' +
    upgrade_block(UP_ABM,   'UPGRADE:EmperorABM', 2500, 60.0, CAMEOS['ABM'], UP_PDL) + '\n\n' +
    upgrade_block(UP_SHLD,  'UPGRADE:EmperorShield', 2500, 50.0, CAMEOS['SHLD']) + '\n\n' +
    upgrade_block(UP_FLEET, 'UPGRADE:EmperorFleetShield', 2000, 45.0, CAMEOS['FLEET'], UP_SHLD) + '\n')
upg_src = eff[P_UPG.lower()][1]
check(upg_src.endswith(b'\n'), 'Upgrade.ini must end with newline to append')
upg_new = upg_src + UPG_APPEND.encode('latin-1')
check(upg_new.startswith(upg_src), 'Upgrade.ini not append-only')
check(UPG_APPEND.count('\nUpgrade ') == 4 and UPG_APPEND.count('RequiredUpgrade    =') == 2, 'Upgrade append balance')
print('Upgrade.ini: +4 PLAYER upgrades appended (2 chained via RequiredUpgrade)')

# ===================================================== CommandButton.ini append
def cb_block(name, upgrade, text_label, cameo, tip):
    return '\n'.join([f'CommandButton {name}', '  Command       = PLAYER_UPGRADE',
        f'  Upgrade       = {upgrade}', f'  TextLabel     = {text_label}',
        f'  ButtonImage   = {cameo}', '  ButtonBorderType        = UPGRADE',
        f'  DescriptLabel           = {tip}', '  UnitSpecificSound = MoneyWithdraw', 'End'])
CB_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: four Emperor-defence research buttons (War Factory page-2 slots 8-11).\n' +
    cb_block(CB_PDL,   UP_PDL,   'CONTROLBAR:UpgradeEmperorPDL', CAMEOS['PDL'],
             'CONTROLBAR:ToolTipUpgradeEmperorPDL') + '\n\n' +
    cb_block(CB_ABM,   UP_ABM,   'CONTROLBAR:UpgradeEmperorABM', CAMEOS['ABM'],
             'CONTROLBAR:ToolTipUpgradeEmperorABM') + '\n\n' +
    cb_block(CB_SHLD,  UP_SHLD,  'CONTROLBAR:UpgradeEmperorShield', CAMEOS['SHLD'],
             'CONTROLBAR:ToolTipUpgradeEmperorShield') + '\n\n' +
    cb_block(CB_FLEET, UP_FLEET, 'CONTROLBAR:UpgradeEmperorFleetShield', CAMEOS['FLEET'],
             'CONTROLBAR:ToolTipUpgradeEmperorFleetShield') + '\n')
cb_src = eff[P_CB.lower()][1]
check(cb_src.endswith(b'\n'), 'CommandButton.ini must end with newline to append')
cb_new = cb_src + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src), 'CommandButton.ini not append-only')
check(CB_APPEND.count('\nCommandButton ') == 4, 'CB append balance')
print('CommandButton.ini: +4 research buttons appended')

# ===================================================== CommandSet.ini edit (WF page 2)
cs_src = eff[P_CS.lower()][1]
cs_text = cs_src.decode('latin-1')
WFSET = 'Tank_ChinaWarFactoryCommandSet_Down'
m = get_block(cs_text, 'CommandSet', WFSET, 'CS')
block = m.group(0)
# assert the 4 target slots are currently absent (free) and page/evac/sell survive
slots_before = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', m.group(1), re.M))
for s in ['8', '9', '10', '11']:
    check(s not in slots_before, f'{WFSET}: slot {s} unexpectedly occupied ({slots_before.get(s)})')
for s, want in [('12', 'Command_ChinaButtonCommandSetOneUp'), ('13', 'Command_Evacuate'),
                ('14', 'Command_Sell'), ('1', 'Tank_Command_ConstructChinaVehicleNukeLauncher')]:
    check(slots_before.get(s) == want, f'{WFSET}: slot {s} expected {want}, got {slots_before.get(s)}')
add_lines = [f'  8  = {CB_PDL} ; {TAG}', f'  9  = {CB_ABM} ; {TAG}',
             f'  10 = {CB_SHLD} ; {TAG}', f'  11 = {CB_FLEET} ; {TAG}']
# insert the four lines right after slot 7's line
s7 = re.search(r'^(\s*7\s*=\s*\S+[^\n]*)$', block, re.M)
check(s7, f'{WFSET}: slot 7 line not found for insertion anchor')
new_block = block[:s7.end()] + '\n' + '\n'.join(add_lines) + block[s7.end():]
cs_new_text = cs_text[:m.start()] + new_block + cs_text[m.end():]
cs_new = cs_new_text.encode('latin-1')
audit('CommandSet.ini (+4 WF page-2 slots)', cs_src, cs_new, [], add_lines)
# post-edit layout
sl = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(cs_new_text, 'CommandSet', WFSET, 'CS').group(1), re.M))
want = {'1': 'Tank_Command_ConstructChinaVehicleNukeLauncher', '2': 'Tank_Command_ConstructChinaTankJS7',
        '3': 'Tank_Command_ConstructChinaTankCommandTank', '4': 'Tank_Command_ConstructChinaTankOverlord',
        '5': 'Tank_Command_ConstructChinaVehicleBuratino', '6': 'Tank_Command_ConstructChinaVehicleHammerCannon',
        '7': 'Tank_Command_ConstructChinaVehicleScoutCar', '8': CB_PDL, '9': CB_ABM, '10': CB_SHLD,
        '11': CB_FLEET, '12': 'Command_ChinaButtonCommandSetOneUp', '13': 'Command_Evacuate', '14': 'Command_Sell'}
check(sl == want, f'{WFSET} post-edit layout wrong: {sl}')
# sibling command-set survival (untouched sets that other layers depend on)
for name, need in [('Tank_ChinaIndustrialPlantCommandSet', 'Tank_Command_UpgradeGrenadierPanzergrenadiers'),
                   ('Tank_ChinaIndustrialPlantCommandSet', 'Tank_Command_GrenadierDrop'),
                   ('Tank_ChinaTankEmperorDefaultCommandSet', 'Tank_Command_UpgradeKwaiPDL'),
                   ('Tank_ChinaWarFactoryCommandSet', 'Tank_Command_ConstructChinaTankBattleMaster')]:
    check(need in get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), f'survival: {name} lost {need}')
print('CommandSet.ini: WF page-2 slots 8-11 = defence buttons; siblings survive')

# ===================================================== Generals.str append
def s(label, val):
    return f'{label}\n"{val}"\nEND\n'
STR_APPEND = ('\n' +
    s('UPGRADE:EmperorPDL', 'Hull Point-Defense Laser') + '\n' +
    s('CONTROLBAR:UpgradeEmperorPDL', '&Hull Point-Defense Laser') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeEmperorPDL',
      'Emperors gain a reactive point-defense laser: when struck they pulse an\\n'
      ' anti-missile LASER burst that destroys incoming rockets and missiles nearby.') + '\n' +
    s('UPGRADE:EmperorABM', 'ABM Interceptor Array') + '\n' +
    s('CONTROLBAR:UpgradeEmperorABM', '&ABM Interceptor Array') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeEmperorABM',
      'Requires Hull Point-Defense Laser. Upgrades the point-defense to a wider,\\n'
      ' harder-hitting array that also intercepts ballistic (SCUD-class) missiles.') + '\n' +
    s('UPGRADE:EmperorShield', 'Projected Energy Shield') + '\n' +
    s('CONTROLBAR:UpgradeEmperorShield', '&Projected Energy Shield') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeEmperorShield',
      'Projects a damage-absorbing energy shield around the Emperor: a large\\n'
      ' hitpoint buffer that continuously recharges.') + '\n' +
    s('UPGRADE:EmperorFleetShield', "Fleet Shield Projection") + '\n' +
    s('CONTROLBAR:UpgradeEmperorFleetShield', '&Fleet Shield Projection') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeEmperorFleetShield',
      'Requires Projected Energy Shield. The Emperor extends a weaker regenerative\\n'
      ' shield field to nearby friendly units.'))
str_src = eff[P_STR.lower()][1]
check(str_src.endswith(b'\n'), 'Generals.str must end with newline to append')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src), 'Generals.str not append-only')
check(str_new.decode('latin-1').count('\nEND\n') == str_src.decode('latin-1').count('\nEND\n') + 12,
      'str append entry count (want +12)')
print('Generals.str: +12 entries appended')

# ===================================================== global closure
cb_f = cb_new.decode('latin-1'); upg_f = upg_new.decode('latin-1')
wpn_f = wpn_new.decode('latin-1'); str_f = str_new.decode('latin-1'); emp_f = emp_new_text
for cb, up in [(CB_PDL, UP_PDL), (CB_ABM, UP_ABM), (CB_SHLD, UP_SHLD), (CB_FLEET, UP_FLEET)]:
    b = get_block(cb_f, 'CommandButton', cb, 'CB').group(1)
    check(f'Upgrade       = {up}' in b, f'{cb} upgrade ref')
    check(re.search(r'^Upgrade\s+%s\b' % up, upg_f, re.M), f'{up} not defined')
# RequiredUpgrade prereqs resolve
for req in [UP_PDL, UP_SHLD]:
    check(re.search(r'^Upgrade\s+%s\b' % req, upg_f, re.M), f'RequiredUpgrade prereq {req} not defined')
check(re.search(r'RequiredUpgrade\s*=\s*%s\b' % UP_PDL, upg_f), 'ABM must require PDL')
check(re.search(r'RequiredUpgrade\s*=\s*%s\b' % UP_SHLD, upg_f), 'Fleet must require Shield')
# modules -> upgrades/weapons resolve
for up in [UP_PDL, UP_ABM, UP_SHLD, UP_FLEET]:
    check(f'= {up}' in emp_f or f'   {up}' in emp_f, f'Emperor module does not reference {up}')
for w in [W_PDL, W_ABM]:
    check(re.search(r'^Weapon\s+%s\b' % w, wpn_f, re.M), f'weapon {w} not defined')
    check(w in emp_f, f'Emperor reaction module does not reference {w}')
# every label resolves
for lab in NEW_LABELS:
    check(re.search(r'^%s$' % re.escape(lab), str_f, re.M), f'label {lab} missing from str')
# every button cameo resolves (already drift-guarded existence)
print('closure OK (buttons->upgrades->modules->weapons, RequiredUpgrade chains, labels, cameos)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_EMP, emp_new), bigfile.BigEntry(P_CS, cs_new),
           bigfile.BigEntry(P_CB, cb_new), bigfile.BigEntry(P_UPG, upg_new),
           bigfile.BigEntry(P_WPN, wpn_new), bigfile.BigEntry(P_STR, str_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries], 'BIG round-trip mismatch')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
open(out_path, 'wb').write(blob)
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} files)' + (' [hash-idempotent]' if prev == blob else ''))

# ------------------------------------------------------------------ install + audit
want_bytes = {e.path.lower(): e.data for e in entries}
md5s = []
import hashlib
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    shutil.copyfile(out_path, dst)
    data = open(dst, 'rb').read()
    check(data == blob, f'install verify failed: {dst}')
    md5s.append(hashlib.md5(data).hexdigest())
    posteff = {}
    for b in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b)):
            posteff[e.path.lower()] = (b, e.data)
    for p, dat in want_bytes.items():
        check(posteff[p][0] == ARCHIVE, f'{d}: {p} effective owner is {posteff[p][0]} not us')
        check(posteff[p][1] == dat, f'{d}: {p} installed bytes differ')
    # grenadier layers still own their non-overlapping files
    check(posteff['data\\ini\\specialpower.ini'][0] == 'zzz-ZZZZZZZZZZZ1DropLadder.big',
          f'{d}: DropLadder SpecialPower.ini ownership regressed')
    check(posteff['data\\ini\\objectcreationlist.ini'][0] == 'zzz-ZZZZZZZZZZZ1DropLadder.big',
          f'{d}: DropLadder OCL ownership regressed')
    # the crewed Emperor we shipped keeps the grenadier crew modules
    e_emp = posteff[P_EMP.lower()][1].decode('latin-1')
    for n in ['ModuleTag_GP_Crew01', 'ModuleTag_GP_Crew03', 'ModuleTag_ShtoraAuto01', 'MaxHealth       = 1320.0']:
        check(n in e_emp, f'{d}: installed Emperor lost {n}')
    print('installed + post-install effective audit OK:', dst)
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (Emperor Defense Suite)')
