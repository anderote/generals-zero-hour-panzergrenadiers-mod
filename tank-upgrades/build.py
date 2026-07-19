#!/usr/bin/env python3
"""zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big -- customizable Battlemaster field upgrades
(ShockWave / GeneralsX, macOS), for Kwai (China Tank General).

Design: the rebalance layer cut the Kwai Battlemaster (Tank_ChinaTankBattleMaster)
to STOCK (MaxHealth 400). This layer lets the player make individual Battlemasters
ELITE by BUYING per-unit field upgrades -- the same OBJECT-scoped Upgrade +
CommandButton + gated-module idiom the tank already uses for its Prop Tower ($500),
PDL pod ($500) and coax MG. Three NEW per-tank purchases, each on ALL FOUR
Battlemaster command sets (default / ERA / PDL / Tower) so they persist through the
existing CommandSetUpgrade swaps:

  1. Reactive Armor    ($800)  -- ArmorUpgrade -> reduced-damage ArmorSet (20% less
                                  vs AP/explosion/cannon; the previously-cosmetic
                                  PLAYER_UPGRADE armorset, repointed to a real armor).
  2. Hull Reinforcement ($600) -- MaxHealthUpgrade +160 (+40% of stock 400),
                                  ADD_CURRENT_HEALTH_TOO.
  3. Projected Shield  ($1000) -- MaxHealthUpgrade +250 buffer + gated AutoHealBehavior
                                  15 HP/s recharge (the Emperor energy-shield idiom,
                                  scaled down from +2000 / 40 HP/s).

All ADD onto the tank; every prior module (KwaiDoctrine armor tiers, Tungsten,
Light-Armor, Nuclear, AutoLoader weaponset, Prop Tower OCU/CmdSet/Production, Kwai-PDL
OCU/CmdSet, grenadier crew, veterancy) and the rebalance stat cuts are preserved.

ENGINE NOTE (Reactive Armor): ArmorUpgrade.cpp only ever calls
setArmorSetFlag(ARMORSET_PLAYER_UPGRADE) -- there is NO pure-data way to set a
dedicated per-upgrade armorset bit (VETERAN/ELITE/HERO are rank; CRATE_UPGRADE_* are
salvage pickups; PLAYER_UPGRADE is the only upgrade-settable flag). That single bit is
already owned on this tank by the doctrine Upgrade_TankLightArmor, whose
PLAYER_UPGRADE armorset was COSMETIC only (same TankArmor, different DamageFX). So we
repoint that armorset to a real reduced-damage armor: the reduced-damage set is now
granted by EITHER the per-unit Reactive Armor purchase OR the doctrine Light Armor
(documented coupling -- both are "earned"). This is the spec's "else document the
mechanism" fallback.

Autoloader (optional global RATE_OF_FIRE research): SKIPPED -- Tank_Upgrade_ChinaTank-
AutoLoader already exists on this tank (a WeaponSetUpgrade to the upgraded gun), so a
second "autoloader" would be redundant/confusing. Kept the menu focused per spec.

Emperor/Overlord: NOT touched (its kit is already rich). Verified its Emperor.ini,
upgrade buttons and modules survive byte-for-byte.

Sorts ABOVE every data layer (19 Z's + '1' > rebalance's 18 Z's + '0') and BELOW
zzz_ControlBarPro*/zzzz_FXEnhance ('-' 0x2D < '_' 0x5F < 'z' 0x7A). Verified against
both real mod-dir listings. Depends on ../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys, hashlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big'   # 19 Z's + '1'
TAG = 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

# effective owners (verified live; build fails if they drift)
OWN_REBAL = 'zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big'
OWN_TWEAK = 'zzz-ZZZZZZZZZZZZZZZZZ0EmperorTweaks.big'
OWN_TESLA = 'zzz-ZZZZZZZZZZZZZ0TeslaFinish.big'
OWN_EDS   = 'zzz-ZZZZZZZZZZZZ0EmperorDefense.big'
OWN_ROTR  = 'zzz-ZZZZZZZRotrInfantry.big'

P_BM  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\BattleMaster.ini'
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'  # verify-only, not shipped
P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_UPG = 'Data\\INI\\Upgrade.ini'
P_ARM = 'Data\\INI\\Armor.ini'
P_STR = 'Data\\Generals.str'

EXPECT_OWNER = {
    P_BM.lower():  OWN_REBAL,
    P_CS.lower():  OWN_TWEAK,
    P_CB.lower():  OWN_TESLA,
    P_UPG.lower(): OWN_EDS,
    P_ARM.lower(): OWN_ROTR,
    P_STR.lower(): OWN_TWEAK,
}
SHIPPED = [P_BM, P_CS, P_CB, P_UPG, P_ARM, P_STR]

# ---- new identifiers ------------------------------------------------------
UP_REACT = 'Tank_Upgrade_BattleMasterReactiveArmor'
UP_HULL  = 'Tank_Upgrade_BattleMasterHull'
UP_SHLD  = 'Tank_Upgrade_BattleMasterShield'
CB_REACT = 'Tank_Command_UpgradeBattleMasterReactiveArmor'
CB_HULL  = 'Tank_Command_UpgradeBattleMasterHull'
CB_SHLD  = 'Tank_Command_UpgradeBattleMasterShield'
ARMOR    = 'Tank_BattleMasterReactiveArmor'
MODTAGS  = ['ModuleTag_TU_Reactive01', 'ModuleTag_TU_Hull01',
            'ModuleTag_TU_Shield01', 'ModuleTag_TU_Shield02']
NEW_IDS = [UP_REACT, UP_HULL, UP_SHLD, CB_REACT, CB_HULL, CB_SHLD, ARMOR] + MODTAGS
NEW_LABELS = []
for base in ['BattleMasterReactiveArmor', 'BattleMasterHull', 'BattleMasterShield']:
    NEW_LABELS += ['UPGRADE:' + base, 'CONTROLBAR:Upgrade' + base,
                   'CONTROLBAR:ToolTipUpgrade' + base]

CAM_REACT = 'SNTankTitaniumArmor'
CAM_HULL  = 'SSCompositeArmor'
CAM_SHLD  = 'SSMammothShield'
CAMEOS = [CAM_REACT, CAM_HULL, CAM_SHLD]

BM_SETS = ['Tank_ChinaVehicleBattleMasterCommandSet',
           'Tank_ChinaVehicleBattleMasterCommandSetERA',
           'Tank_ChinaVehicleBattleMasterCommandSetPDL',
           'Tank_ChinaVehicleBattleMasterCommandSetTower']

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
    check(OWN_REBAL in below, f'{d}: {OWN_REBAL} must sort below us')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
    check(any(a.lower().startswith('zzzz_fxenhance') for a in above),
          f'{d}: FXEnhance must sort above us')
print('sort position OK in both dirs (above all data layers incl. Rebalance; below ControlBarPro*/FXEnhance)')

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
    check(eff[p][0].lower() == owner.lower(), f'{p}: effective owner drifted: {eff[p][0]} (expected {owner})')
check(P_EMP.lower() in eff and eff[P_EMP.lower()][0].lower() == OWN_REBAL.lower(),
      'Emperor.ini effective owner drifted')
print('effective ownership OK:', {p.split(chr(92))[-1]: eff[p][0] for p in EXPECT_OWNER})

for d in MODDIRS:
    for b in sorted_bigs(d):
        if str.lower(b) <= ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        for p in SHIPPED + [P_EMP]:
            check(p.lower() not in claimed, f'{d}/{b} (sorts above us) claims {p}')
print('no higher-sorting archive claims any shipped path (or Emperor.ini)')

# ------------------------------------------ collision + drift + resolution
all_ini = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                    if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_ini),
          f'identifier collision: {ident} already exists in effective space')
print('new identifiers collision-free (%d ids, %d labels)' % (len(NEW_IDS), len(NEW_LABELS)))

# donor-idiom drift guards (facts each mechanism rests on)
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items() if '\\mappedimages\\' in p)
for img in CAMEOS:
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M), f'cameo MappedImage missing: {img}')
check(re.search(r'^Armor\s+TankArmor\b', all_ini, re.M), 'TankArmor (base armor) missing')
check(re.search(r'^AudioEvent\s+MoneyWithdraw\b', all_ini, re.M), 'AudioEvent MoneyWithdraw missing')
bm_eff = eff[P_BM.lower()][1].decode('latin-1')
check('Behavior = MaxHealthUpgrade' in bm_eff, 'MaxHealthUpgrade idiom absent on Battlemaster')
check('Behavior = ArmorUpgrade' in bm_eff, 'ArmorUpgrade idiom absent on Battlemaster')
check('Behavior = AutoHealBehavior' in all_ini, 'AutoHealBehavior idiom absent in effective space')
check('Command       = OBJECT_UPGRADE' in eff[P_CB.lower()][1].decode('latin-1'),
      'OBJECT_UPGRADE command-button idiom absent')
print('donor-idiom drift guards OK (cameos, TankArmor, MaxHealth/Armor/AutoHeal modules, OBJECT_UPGRADE button, sound)')

# ---------------------------------------------------------------- helpers
def audit(label, old, new, exp_removed, exp_added):
    o = [l.rstrip('\r\n') for l in old.decode('latin-1').splitlines()]
    n = [l.rstrip('\r\n') for l in new.decode('latin-1').splitlines()]
    co, cn = Counter(o), Counter(n)
    removed = list((co - cn).elements()); added = list((cn - co).elements())
    check(sorted(removed) == sorted([x.rstrip('\r\n') for x in exp_removed]),
          f'{label}: removed-line audit mismatch:\n got {sorted(removed)}\n exp {sorted(exp_removed)}')
    check(sorted(added) == sorted([x.rstrip('\r\n') for x in exp_added]),
          f'{label}: added-line audit mismatch:\n got {sorted(added)}\n exp {sorted(exp_added)}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')

def get_block(text, kind, name, label):
    m = re.search(r'^%s\s+%s\b[^\n]*\n(.*?)^End[ \t\r]*$' % (kind, re.escape(name)), text, re.M | re.S)
    check(m, f'{label}: {kind} {name} missing'); return m

# ===================================================== BattleMaster.ini edit
EMP_MODS = [
    '  ; ----------------------------------------------------------------------------',
    f'  ; {TAG}: per-unit purchasable field upgrades (ADDED; all prior modules preserved).',
    f'  Behavior = ArmorUpgrade ModuleTag_TU_Reactive01 ; {TAG}: Reactive Armor -- sets ARMORSET_PLAYER_UPGRADE -> reduced-damage armorset (shared bit; see build.py)',
    f'    TriggeredBy  = {UP_REACT}',
    '  End',
    f'  Behavior = MaxHealthUpgrade ModuleTag_TU_Hull01 ; {TAG}: Hull Reinforcement -- +160 HP (+40% of stock 400)',
    f'    TriggeredBy   = {UP_HULL}',
    '    AddMaxHealth  = 160.0',
    '    ChangeType    = ADD_CURRENT_HEALTH_TOO',
    '  End',
    f'  Behavior = MaxHealthUpgrade ModuleTag_TU_Shield01 ; {TAG}: Projected Shield -- +250 absorption buffer (Emperor energy-shield idiom, scaled down)',
    f'    TriggeredBy   = {UP_SHLD}',
    '    AddMaxHealth  = 250.0',
    '    ChangeType    = ADD_CURRENT_HEALTH_TOO',
    '  End',
    f'  Behavior = AutoHealBehavior ModuleTag_TU_Shield02 ; {TAG}: Projected Shield recharge -- 15 HP/s (smaller than the Emperor 40 HP/s)',
    '    StartsActive  = No',
    f'    TriggeredBy   = {UP_SHLD}',
    '    HealingAmount = 15',
    '    HealingDelay  = 1000',
    '  End',
]
bm_src = eff[P_BM.lower()][1]
bm_text = bm_src.decode('latin-1')
# prior-layer hunks that MUST survive (fail loudly if any drifted away before we edit)
BM_SURVIVE = ['MaxHealth       = 400', 'InitialHealth   = 400',
              'ModuleTag_KD_Armor1', 'ModuleTag_KD_Armor4', 'ModuleTag_KD_Tungsten01',
              'ModuleTag_28', 'ModuleTag_Armor_02', 'ModuleTag_17',
              'Behavior = HelixContain ModuleTag_ArmorAddon01',
              'ModuleTag_PropTowerMount01', 'ModuleTag_PropTowerProduction01',
              'ModuleTag_KPDL_Mount01', 'ModuleTag_KPDL_CmdSet01', 'ModuleTag_KPDL_CmdSet02',
              'ModuleTag_GP_Crew01', 'ModuleTag_GP_Crew02',
              'Behavior = VeterancyGainCreate ModuleVet_01',
              'ShwBattleMasterCoaxMGWeapon',
              'CommandSet       = Tank_ChinaVehicleBattleMasterCommandSet']
for n in BM_SURVIVE:
    check(n in bm_text, f'BattleMaster prior-layer hunk missing before edit: {n!r}')
for t in MODTAGS:
    check(t not in bm_text, f'BattleMaster already has module tag {t}')

# (a) repoint the PLAYER_UPGRADE ArmorSet (cosmetic today) -> real reduced-damage armor
mA = re.search(r'(Conditions\s*=\s*PLAYER_UPGRADE\s*\r?\n[ \t]*)(Armor\s*=\s*)TankArmor\b', bm_text)
check(mA, 'PLAYER_UPGRADE armorset "Armor = TankArmor" line not found')
# capture the exact matched Armor line text (2nd line of the match)
armor_line_m = re.search(r'^[ \t]*Armor\s*=\s*TankArmor\b[^\n]*$', mA.group(0), re.M)
old_armor_line = armor_line_m.group(0).rstrip('\r\n')
new_armor_line = old_armor_line.replace('TankArmor', ARMOR)
bm_text2 = bm_text[:mA.start()] + mA.group(1) + mA.group(2) + ARMOR + bm_text[mA.end():]
check(bm_text2.count('= TankArmor') == bm_text.count('= TankArmor') - 1, 'exactly one TankArmor ref must change')
check(ARMOR in bm_text2, 'reactive armor ref not inserted')

# (b) insert the 4 gated modules just before Geometry = BOX
geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', bm_text2, re.M))
check(len(geo) == 1, f'BattleMaster: need exactly one Geometry=BOX anchor (found {len(geo)})')
ins = geo[0].start()
bm_new_text = bm_text2[:ins] + '\r\n'.join(EMP_MODS) + '\r\n' + bm_text2[ins:]
bm_new = bm_new_text.encode('latin-1')
audit('BattleMaster.ini (+4 upgrade modules, armorset repoint)', bm_src, bm_new,
      [old_armor_line], EMP_MODS + [new_armor_line])
for n in BM_SURVIVE:
    check(n in bm_new_text, f'BattleMaster prior-layer hunk lost after edit: {n!r}')
# module-count sanity (stack, don't clobber)
check(len(re.findall(r'Behavior\s*=\s*MaxHealthUpgrade\b', bm_new_text)) == 7,
      'expected 7 MaxHealthUpgrade (KD_Armor1-4 + LightArmor_28 + Hull + Shield)')
check(len(re.findall(r'Behavior\s*=\s*ArmorUpgrade\b', bm_new_text)) == 2,
      'expected 2 ArmorUpgrade (LightArmor + Reactive)')
check(len(re.findall(r'Behavior\s*=\s*AutoHealBehavior\b', bm_new_text)) == 1, 'expected 1 AutoHealBehavior')
print('BattleMaster.ini: 4 modules inserted + PLAYER_UPGRADE armorset repointed; all prior hunks survive')

# ===================================================== Armor.ini append (reduced-damage armor)
# Tank_BattleMasterReactiveArmor = TankArmor's explicit resistances, plus DEFAULT 80%
# (20% less from all otherwise-unlisted types: ARMOR_PIERCING / EXPLOSION / cannon, the
# meat of tank combat). Explicit lines below preserve TankArmor's own behaviour.
CRLF = '\r\n'
arm_lines = [
    'Armor ' + ARMOR + '  ; ' + TAG + ': Reactive Armor field upgrade (Battlemaster)',
    '  Armor = DEFAULT            80%      ; 20% less from AP / explosion / cannon (reactive plating)',
    '  Armor = INFANTRY_MISSILE   80%',
    '  Armor = CRUSH              50%',
    '  Armor = SMALL_ARMS         25%',
    '  Armor = GATTLING           10%',
    '  Armor = COMANCHE_VULCAN    25%',
    '  Armor = FLAME              25%',
    '  Armor = RADIATION          50%',
    '  Armor = MICROWAVE           0%',
    '  Armor = POISON             15%',
    '  Armor = SNIPER              0%',
    '  Armor = MELEE               0%',
    '  Armor = LASER               0%',
    '  Armor = HAZARD_CLEANUP      0%',
    '  Armor = PARTICLE_BEAM     100%',
    '  Armor = KILL_PILOT        100%',
    '  Armor = SURRENDER           0%',
    '  Armor = SUBDUAL_MISSILE     0%',
    '  Armor = SUBDUAL_VEHICLE   100%',
    '  Armor = SUBDUAL_BUILDING    0%',
    '  Armor = HACK                0%',
    'End',
]
ARM_APPEND = CRLF + '; ' + '-'*74 + CRLF + '; ' + TAG + ': reduced-damage armor for the Reactive Armor field upgrade.' + CRLF + CRLF.join(arm_lines) + CRLF
arm_src = eff[P_ARM.lower()][1]
check(arm_src.endswith(b'\n'), 'Armor.ini must end with newline to append')
arm_new = arm_src + ARM_APPEND.encode('latin-1')
check(arm_new.startswith(arm_src), 'Armor.ini not append-only')
check(ARM_APPEND.count('\nArmor ') == 1, 'Armor append balance (want 1 new Armor block)')
print('Armor.ini: +1 reduced-damage armor appended')

# ===================================================== Upgrade.ini append (3 OBJECT upgrades)
def upgrade_block(name, display, cost, time, cameo):
    return '\n'.join([f'Upgrade {name}', f'  DisplayName        = {display}',
        '  Type               = OBJECT', f'  BuildTime          = {time}',
        f'  BuildCost          = {cost}', f'  ButtonImage        = {cameo}',
        '  ResearchSound      = OverlordExpansion', 'End'])
UPG_APPEND = ('\n; ' + '-'*74 + f'\n; {TAG}: three per-unit Battlemaster field upgrades (Type=OBJECT, bought per tank).\n' +
    upgrade_block(UP_REACT, 'UPGRADE:BattleMasterReactiveArmor', 800, 10.0, CAM_REACT) + '\n\n' +
    upgrade_block(UP_HULL,  'UPGRADE:BattleMasterHull', 600, 10.0, CAM_HULL) + '\n\n' +
    upgrade_block(UP_SHLD,  'UPGRADE:BattleMasterShield', 1000, 12.0, CAM_SHLD) + '\n')
upg_src = eff[P_UPG.lower()][1]
check(upg_src.endswith(b'\n'), 'Upgrade.ini must end with newline to append')
upg_new = upg_src + UPG_APPEND.encode('latin-1')
check(upg_new.startswith(upg_src), 'Upgrade.ini not append-only')
check(UPG_APPEND.count('\nUpgrade ') == 3, 'Upgrade append balance (want 3)')
check(UPG_APPEND.count('Type               = OBJECT') == 3, 'all 3 upgrades must be Type=OBJECT')
print('Upgrade.ini: +3 OBJECT upgrades appended')

# ===================================================== CommandButton.ini append (3 buttons)
def cb_block(name, upgrade, text_label, cameo, tip):
    return '\n'.join([f'CommandButton {name}', '  Command       = OBJECT_UPGRADE',
        f'  Upgrade       = {upgrade}', '  Options       = OK_FOR_MULTI_SELECT NOT_QUEUEABLE',
        f'  TextLabel     = {text_label}', f'  ButtonImage   = {cameo}',
        '  ButtonBorderType        = UPGRADE', f'  DescriptLabel           = {tip}',
        f'  PurchasedLabel          = {tip}', '  UnitSpecificSound = MoneyWithdraw', 'End'])
CB_APPEND = ('\n; ' + '-'*74 + f'\n; {TAG}: three per-unit Battlemaster field-upgrade buttons.\n' +
    cb_block(CB_REACT, UP_REACT, 'CONTROLBAR:UpgradeBattleMasterReactiveArmor', CAM_REACT,
             'CONTROLBAR:ToolTipUpgradeBattleMasterReactiveArmor') + '\n\n' +
    cb_block(CB_HULL,  UP_HULL,  'CONTROLBAR:UpgradeBattleMasterHull', CAM_HULL,
             'CONTROLBAR:ToolTipUpgradeBattleMasterHull') + '\n\n' +
    cb_block(CB_SHLD,  UP_SHLD,  'CONTROLBAR:UpgradeBattleMasterShield', CAM_SHLD,
             'CONTROLBAR:ToolTipUpgradeBattleMasterShield') + '\n')
cb_src = eff[P_CB.lower()][1]
check(cb_src.endswith(b'\n'), 'CommandButton.ini must end with newline to append')
cb_new = cb_src + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src), 'CommandButton.ini not append-only')
check(CB_APPEND.count('\nCommandButton ') == 3, 'CB append balance (want 3)')
print('CommandButton.ini: +3 field-upgrade buttons appended')

# ===================================================== CommandSet.ini edit (4 BM sets, slots 6-8)
cs_src = eff[P_CS.lower()][1]
cs_text = cs_src.decode('latin-1')
add_lines_per_set = [f'  6  = {CB_REACT} ; {TAG}',
                     f'  7  = {CB_HULL} ; {TAG}',
                     f'  8  = {CB_SHLD} ; {TAG}']
cs_new_text = cs_text
all_added = []
for name in BM_SETS:
    m = get_block(cs_new_text, 'CommandSet', name, 'CS')
    block = m.group(0)
    slots = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', m.group(1), re.M))
    for s in ['6', '7', '8']:
        check(s not in slots, f'{name}: slot {s} unexpectedly occupied ({slots.get(s)})')
    anchor = re.search(r'^(\s*5\s*=\s*Command_Evacuate[^\n]*)$', block, re.M)
    check(anchor, f'{name}: slot 5 (Command_Evacuate) anchor not found')
    new_block = block[:anchor.end()] + '\n' + '\n'.join(add_lines_per_set) + block[anchor.end():]
    cs_new_text = cs_new_text[:m.start()] + new_block + cs_new_text[m.end():]
    all_added += add_lines_per_set
cs_new = cs_new_text.encode('latin-1')
audit('CommandSet.ini (+3 slots x 4 BM sets)', cs_src, cs_new, [], all_added)
# post-edit layout of every set: our 3 buttons present + prior buttons intact
for name in BM_SETS:
    body = get_block(cs_new_text, 'CommandSet', name, 'CS').group(1)
    sl = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', body, re.M))
    check(sl.get('6') == CB_REACT and sl.get('7') == CB_HULL and sl.get('8') == CB_SHLD,
          f'{name}: our slots 6-8 wrong: {sl}')
    check(sl.get('5') == 'Command_Evacuate' and sl.get('11') == 'Command_AttackMove'
          and sl.get('14') == 'Command_Stop', f'{name}: prior slots disturbed: {sl}')
# the tower/PDL prior buttons still live where they were
d = get_block(cs_new_text, 'CommandSet', BM_SETS[0], 'CS').group(1)
check('Tank_Command_UpgradeKwaiPDL' in d and 'Command_UpgradeChinaOverlordPropagandaTower' in d,
      'default BM set lost its PDL/tower buttons')
# untouched sibling sets survive
for name, need in [('Tank_ChinaWarFactoryCommandSet', 'Tank_Command_ConstructChinaTankBattleMaster'),
                   ('Tank_ChinaTankEmperorDefaultCommandSet', 'Tank_Command_UpgradeChinaOverlordGattlingCannon')]:
    check(need in get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), f'survival: {name} lost {need}')
print('CommandSet.ini: slots 6-8 added to all 4 BM sets; PDL/tower/siblings survive')

# ===================================================== Generals.str append
def s(label, val):
    return f'{label}\n"{val}"\nEND\n'
STR_APPEND = ('\n' +
    s('UPGRADE:BattleMasterReactiveArmor', 'Reactive Armor') + '\n' +
    s('CONTROLBAR:UpgradeBattleMasterReactiveArmor', '&Reactive Armor') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeBattleMasterReactiveArmor',
      'Bolt reactive armor plating onto this Battlemaster: reduces incoming\\n'
      ' armor-piercing, explosive and cannon damage by 20%.') + '\n' +
    s('UPGRADE:BattleMasterHull', 'Hull Reinforcement') + '\n' +
    s('CONTROLBAR:UpgradeBattleMasterHull', '&Hull Reinforcement') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeBattleMasterHull',
      'Reinforce this Battlemaster\'s hull: permanently adds 160 hit points\\n'
      ' (and heals it to the new maximum).') + '\n' +
    s('UPGRADE:BattleMasterShield', 'Projected Shield') + '\n' +
    s('CONTROLBAR:UpgradeBattleMasterShield', '&Projected Shield') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeBattleMasterShield',
      'Fit this Battlemaster with a projected energy shield: a 250-point\\n'
      ' absorption buffer that continuously recharges at 15 HP/second.'))
str_src = eff[P_STR.lower()][1]
check(str_src.endswith(b'\n'), 'Generals.str must end with newline to append')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src), 'Generals.str not append-only')
check(str_new.decode('latin-1').count('\nEND\n') == str_src.decode('latin-1').count('\nEND\n') + 9,
      'str append entry count (want +9)')
print('Generals.str: +9 entries appended')

# ===================================================== global closure
cb_f = cb_new.decode('latin-1'); upg_f = upg_new.decode('latin-1')
arm_f = arm_new.decode('latin-1'); str_f = str_new.decode('latin-1'); bm_f = bm_new_text
cs_f = cs_new_text
for cb, up, cam, lab in [(CB_REACT, UP_REACT, CAM_REACT, 'BattleMasterReactiveArmor'),
                         (CB_HULL, UP_HULL, CAM_HULL, 'BattleMasterHull'),
                         (CB_SHLD, UP_SHLD, CAM_SHLD, 'BattleMasterShield')]:
    b = get_block(cb_f, 'CommandButton', cb, 'CB').group(1)
    check(f'Upgrade       = {up}' in b, f'{cb} upgrade ref')
    check(cam in b, f'{cb} cameo ref')
    check(re.search(r'^Upgrade\s+%s\b' % up, upg_f, re.M), f'{up} not defined')
    # button is on all 4 BM command sets
    for name in BM_SETS:
        check(cb in get_block(cs_f, 'CommandSet', name, 'CS').group(1), f'{cb} missing from {name}')
    # every label resolves
    for lp in ['UPGRADE:'+lab, 'CONTROLBAR:Upgrade'+lab, 'CONTROLBAR:ToolTipUpgrade'+lab]:
        check(re.search(r'^%s$' % re.escape(lp), str_f, re.M), f'label {lp} missing from str')
# modules -> upgrades resolve
for up in [UP_REACT, UP_HULL, UP_SHLD]:
    check(up in bm_f, f'Battlemaster module does not reference {up}')
# reactive armor -> armor def resolves; armorset -> armor
check(re.search(r'^Armor\s+%s\b' % ARMOR, arm_f, re.M), f'{ARMOR} not defined in Armor.ini')
check(('Armor           = ' + ARMOR) in bm_f or ('Armor = ' + ARMOR) in bm_f, 'BM armorset not repointed to reactive armor')
# cameos resolve (already drift-guarded existence)
print('closure OK (buttons->upgrades->modules; armorset->armor->def; labels; cameos; buttons on all 4 sets)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_BM, bm_new), bigfile.BigEntry(P_CS, cs_new),
           bigfile.BigEntry(P_CB, cb_new), bigfile.BigEntry(P_UPG, upg_new),
           bigfile.BigEntry(P_ARM, arm_new), bigfile.BigEntry(P_STR, str_new)]
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
    # rebalance stat cuts survive on the installed, effective bytes
    e_bm = posteff[P_BM.lower()][1].decode('latin-1')
    for n in ['MaxHealth       = 400', 'InitialHealth   = 400', 'ModuleTag_KD_Armor1',
              'ModuleTag_PropTowerMount01', 'ModuleTag_KPDL_Mount01', 'ModuleTag_GP_Crew01']:
        check(n in e_bm, f'{d}: installed Battlemaster lost {n}')
    # Emperor.ini untouched -> still owned by rebalance, still 1100 HP + its kit
    check(posteff[P_EMP.lower()][0] == OWN_REBAL, f'{d}: Emperor.ini owner regressed')
    e_emp = posteff[P_EMP.lower()][1].decode('latin-1')
    for n in ['MaxHealth       = 1100', 'ModuleTag_EDS_Shield01', 'ModuleTag_KPDL_Mount01']:
        check(n in e_emp, f'{d}: Emperor lost {n} (should be byte-for-byte untouched)')
    print('installed + post-install effective audit OK:', dst)
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (Tank Upgrades -- customizable Battlemaster field upgrades)')
