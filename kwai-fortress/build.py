#!/usr/bin/env python3
"""kwai-fortress -- the Fortress Bunker (ShockWave / GeneralsX), for Kwai
(China Tank General).

A new dozer-buildable defensive structure on Kwai's dozer page 2 (slot 8, the
slot freed by the hotfix layer's Hacker Bunker button removal): the FORTRESS
BUNKER (Tank_ChinaFortressBunker, $800) -- a full clone of the effective
Tank_ChinaBunker (Rebalance copy: 1875 HP HiveStructureBody, FireBaseArmor,
1-vehicle fire-out GarrisonContain, mines family, doctrine armor tiers,
vehicle-repair aura) with its own command bar carrying three PER-BUNKER
purchases (Type = OBJECT upgrades; player+object upgrade masks are OR'd when
modules are tested -- Object::updateUpgradeModules, GeneralsMD Object.cpp):

  1. Composite Armor   $500  MaxHealthUpgrade +50% of base HP (ADD_CURRENT_HEALTH_TOO)
  2. Point-Defense Laser $800  FireWeaponWhenDamagedBehavior anti-missile LASER
     burst (the EDS hull-PDL idiom, reusing Tank_EmperorPDLWeapon)
  3. Propaganda Tower  $500  gated AutoHealBehavior heal aura, radius 150,
     healing nearby friendly INFANTRY/VEHICLE/STRUCTURE incl. the bunker itself

ENGINE FACTS the deviations rest on (deployed branch feature/veterancy-8-levels,
tip 0b3daa0c9 'propaganda towers heal structures; PDL InterceptBallistics key'):
  * PointDefenseLaserUpdate has NO upgrade gate: its field table is exactly
    WeaponTemplate/PrimaryTargetTypes/SecondaryTargetTypes/ScanRate/ScanRange/
    PredictTargetVelocityFactor/VeterancyBoost/InterceptBallistics
    (PointDefenseLaserUpdate.cpp buildFieldParse) -- StartsActive/TriggeredBy
    would fail INI parse at startup. A purchasable per-bunker PDL therefore
    uses the gate-able REACTIVE idiom (FireWeaponWhenDamagedBehavior is a full
    UpgradeMux), exactly like the Emperor Defense Suite's Hull PDL. Same
    reason EDS documented in 2026: rider-pod gating needs a HelixContain
    rider slot the bunker (GarrisonContain) does not have.
  * PropagandaTowerBehavior cannot be OBJECT-gated: doScan() honors OBJECT
    upgrade masks (us->hasUpgrade) but only for pulse-FX choice; effectLogic()
    keys the heal rate off getControllingPlayer()->hasUpgradeComplete() -- the
    PLAYER mask -- so an OBJECT UpgradeRequired would heal at the base rate
    forever (0% if gated off). And the battlemaster-proptower OCL-rider
    pattern needs a Helix/Overlord contain rider slot + W3DOverlord*Draw;
    the bunker keeps its GarrisonContain (a rider would be refused and
    destroyed, ObjectCreationList payload rules). The purchase is therefore a
    gated AutoHealBehavior radius aura (full UpgradeMux; the deployed stack
    already proves OBJECT-gated MaxHealthUpgrade+AutoHealBehavior on
    Tank_ChinaTankBattleMaster via Tank_Upgrade_BattleMasterHull/Shield, and
    this very bunker parses gated AutoHealBehavior -- ModuleTag_KBT_Heal01).

Layer archive: zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big (21 Z's + '0Fortress':
sorts above zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big [20 Z's], below
zzz_ControlBarPro* / zzzz_FXEnhance).

Ships full modified copies of the effective sources:
  Data\\INI\\Object\\China\\Tank\\Defences\\FortressBunker.ini  NEW FILE (clone)
  Data\\INI\\CommandSet.ini    (TankUpgrades copy: dozer page-2 slot 8 + 2 sets)
  Data\\INI\\CommandButton.ini (TankUpgrades copy: +4 buttons appended)
  Data\\INI\\Upgrade.ini       (TankUpgrades copy: +3 OBJECT upgrades appended)
  Data\\Generals.str           (TankUpgrades copy: +12 entries appended)
Weapon.ini is NOT shipped: the PDL burst reuses the effective
Tank_EmperorPDLWeapon (owner Flagship, below us) -- existence drift-guarded.

Usage: python3 build.py [--stage]   (--stage: write layer .big only, no install)
"""
import os, re, sys, hashlib, shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big'   # 21 Z's + '0Fortress'
TAG = 'kwai-fortress'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]

# ---- tunable constants ----------------------------------------------------
BUNKER_COST      = 800     # Fortress Bunker build cost (base bunker: 200)
COST_ARMOR       = 500     # Composite Armor purchase
COST_PDL         = 800     # Point-Defense Laser purchase
COST_PROP        = 500     # Propaganda Tower purchase
UPG_BUILDTIME    = 10.0    # seconds, all three purchases
ARMOR_RATIO      = 0.5     # Composite Armor: +50% of base MaxHealth
PDL_TRIGGER_DMG  = 30      # min damage per hit that triggers the PDL burst
PROP_HEAL_AMOUNT = 20      # HP healed per pulse per target
PROP_HEAL_DELAY  = 1000    # msec between pulses
PROP_RADIUS      = 150     # aura radius (matches the speaker-tower envelope)

# ---- paths + expected effective owners ------------------------------------
P_BNK = 'Data\\INI\\Object\\China\\Tank\\Defences\\Bunker.ini'          # clone source
P_NEW = 'Data\\INI\\Object\\China\\Tank\\Defences\\FortressBunker.ini'  # NEW path
P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_UPG = 'Data\\INI\\Upgrade.ini'
P_STR = 'Data\\Generals.str'
P_WPN = 'Data\\INI\\Weapon.ini'                                # reference only
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'  # reference only

OWN_REB = 'zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big'
OWN_TU  = 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big'
OWN_FLG = 'zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big'
EXPECT_OWNER = {P_BNK: OWN_REB, P_CS: OWN_TU, P_CB: OWN_TU, P_UPG: OWN_TU,
                P_STR: OWN_TU, P_WPN: OWN_FLG, P_EMP: OWN_FLG}
SHIPPED = [P_NEW, P_CS, P_CB, P_UPG, P_STR]

# ---- new identifiers ------------------------------------------------------
OBJ_NEW  = 'Tank_ChinaFortressBunker'
CS_MAIN  = 'Tank_ChinaFortressBunkerCommandSet'
CS_UPGD  = 'Tank_ChinaFortressBunkerCommandSetUpgrade'
CB_BUILD = 'Tank_Command_ConstructChinaFortressBunker'
UP_ARMOR = 'Tank_Upgrade_FortressCompositeArmor'
UP_PDL   = 'Tank_Upgrade_FortressPDL'
UP_PROP  = 'Tank_Upgrade_FortressPropTower'
CB_ARMOR = 'Tank_Command_UpgradeFortressCompositeArmor'
CB_PDL   = 'Tank_Command_UpgradeFortressPDL'
CB_PROP  = 'Tank_Command_UpgradeFortressPropTower'
MODTAGS  = ['ModuleTag_KF_Armor01', 'ModuleTag_KF_PDL01', 'ModuleTag_KF_Prop01']
NEW_IDS  = [OBJ_NEW, CS_MAIN, CS_UPGD, CB_BUILD, UP_ARMOR, UP_PDL, UP_PROP,
            CB_ARMOR, CB_PDL, CB_PROP] + MODTAGS
NEW_LABELS = ['OBJECT:FortressBunker', 'CONTROLBAR:ConstructChinaFortressBunker',
              'CONTROLBAR:ToolTipChinaBuildFortressBunker']
for base in ['FortressCompositeArmor', 'FortressPDL', 'FortressPropTower']:
    NEW_LABELS += ['UPGRADE:' + base, 'CONTROLBAR:Upgrade' + base,
                   'CONTROLBAR:ToolTipUpgrade' + base]

# reused existing assets (drift-guarded, never redefined)
CAMEO_BUNKER, CAMEO_ARMOR = 'SNTankBunker', 'SSCompositeArmor'
CAMEO_PDL, CAMEO_PROP     = 'SNBlackSharkJammer', 'SSOLSpeaker'
W_PDL = 'Tank_EmperorPDLWeapon'
SND_ARMOR, SND_PDL = 'ReaperVoiceUpgrade', 'OverlordExpansion'
SND_PROP = 'OverlordTankPropagandaTowerVoiceCreate'

def die(msg): print('BUILD FAILED:', msg); sys.exit(1)
def check(c, msg):
    if not c: die(msg)
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)

# ---------------------------------------------------------------- sort order
for d in MODDIRS:
    probe = sorted(set(sorted_bigs(d)) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE); below = probe[:i]; above = probe[i+1:]
    for need in [OWN_REB, OWN_TU, OWN_FLG, 'zzz-ZZZZZZZZZZZZZZZZZZZ0TeslaHP.big']:
        check(need in below, f'{d}: {need} must sort below us')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (above Flagship [20Z], below ControlBarPro*/FXEnhance)')

# ------------------------------------------------- effective sources (below us)
def effective_below(d):
    eff = {}
    for b in sorted_bigs(d):
        if b.lower() >= ARCHIVE.lower():
            continue
        for e in bigfile.read_big(os.path.join(d, b)):
            eff[e.path.lower()] = (b, e.data)
    return eff

eff0 = effective_below(MODDIRS[0])
eff1 = effective_below(MODDIRS[1])
for p, owner in EXPECT_OWNER.items():
    check(p.lower() in eff0, f'missing effective file {p}')
    check(eff0[p.lower()][0] == owner, f'{p}: owner is {eff0[p.lower()][0]} not {owner}')
    check(p.lower() in eff1 and eff0[p.lower()][1] == eff1[p.lower()][1],
          f'{p} differs between mod dirs')
# nothing above us may claim our paths; the NEW path must be unclaimed EVERYWHERE
for d in MODDIRS:
    for b in sorted_bigs(d):
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        check(P_NEW.lower() not in claimed, f'{d}/{b} already claims new path {P_NEW}')
        if b.lower() > ARCHIVE.lower():
            for p in SHIPPED:
                check(p.lower() not in claimed, f'{d}/{b} (above us) claims {p}')
print('effective sources OK (owners Rebalance/TankUpgrades/Flagship; dirs byte-agree; '
      'new path unclaimed everywhere; nothing above claims shipped paths)')

bnk_src = eff0[P_BNK.lower()][1].decode('latin-1')
cs_src  = eff0[P_CS.lower()][1]
cb_src  = eff0[P_CB.lower()][1]
upg_src = eff0[P_UPG.lower()][1]
str_src = eff0[P_STR.lower()][1]
wpn_ref = eff0[P_WPN.lower()][1].decode('latin-1')
emp_ref = eff0[P_EMP.lower()][1].decode('latin-1')

# ------------------------------------------ collision check (definitions)
all_text = '\n'.join(data.decode('latin-1') for p, (b, data) in eff0.items()
                     if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_text),
          f'identifier collision: {ident} already exists in effective space')
print(f'new identifiers collision-free ({len(NEW_IDS)} ids, {len(NEW_LABELS)} labels)')

# ------------------------------------------ donor-idiom drift guards
# EDS hull-PDL module we copy (gate-able reactive point defense) still on Emperor
eds = re.search(r'^  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_EDS_PDL01\b.*?^  End[ \t\r]*$',
                emp_ref, re.M | re.S)
check(eds and 'StartsActive  = No' in eds.group(0) and W_PDL in eds.group(0),
      'EDS hull-PDL donor module drifted (copy source for the reactive PDL idiom)')
# the reused burst weapon (defined below us by Flagship's Weapon.ini copy)
wb = re.search(r'^Weapon %s\b(.*?)^End' % W_PDL, wpn_ref, re.M | re.S)
check(wb, f'{W_PDL} missing from effective Weapon.ini')
for need in ['DamageType          = LASER', 'RadiusDamageAffects = ENEMIES',
             'AntiSmallMissile    = Yes']:
    check(need in wb.group(1), f'{W_PDL} idiom drifted: {need!r} missing')
# armour-table facts the LASER burst rests on
def armor_val(name, dtype):
    m = re.search(r'^Armor\s+%s\b(.*?)^End' % name, all_text, re.M | re.S)
    check(m, f'armor {name} missing')
    v = re.search(r'^\s*Armor\s*=\s*%s\s+(\d+)%%' % dtype, m.group(1), re.M)
    return int(v.group(1)) if v else None
check(armor_val('StructureArmor', 'LASER') is not None, 'StructureArmor table missing LASER row')
check(armor_val('ProjectileArmor', 'LASER') == 100, 'ProjectileArmor LASER not 100% (missiles must die)')
# cameos exist as MappedImages
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff0.items()
                   if '\\mappedimages\\' in p)
for img in [CAMEO_BUNKER, CAMEO_ARMOR, CAMEO_PDL, CAMEO_PROP]:
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M),
          f'cameo MappedImage missing: {img}')
# sounds exist
for snd in [SND_ARMOR, SND_PDL, SND_PROP, 'MoneyWithdraw', 'TankBunkerSelectionSound']:
    check(re.search(r'^AudioEvent\s+%s\b' % snd, all_text, re.M), f'AudioEvent {snd} missing')
# reused buttons/upgrades on the cloned command bar still defined
cb_eff = cb_src.decode('latin-1')
for btn in ['Command_EvacuateTankBunker', 'Command_Stop', 'Command_Sell',
            'Command_UpgradeChinaMines', 'Command_UpgradeEMPMines']:
    check(re.search(r'^CommandButton\s+%s\b' % btn, cb_eff, re.M), f'button {btn} missing')
upg_eff = upg_src.decode('latin-1')
for u in ['Upgrade_ChinaMines', 'Upgrade_ChinaEMPMines']:
    check(re.search(r'^Upgrade\s+%s\b' % u, upg_eff, re.M), f'upgrade {u} missing')
# OBJECT-purchase precedent still deployed (proves both gated mechanisms in-stack)
check(re.search(r'^Upgrade\s+Tank_Upgrade_BattleMasterHull\b.*?^\s*Type\s+=\s+OBJECT', upg_eff, re.M | re.S),
      'Tank_Upgrade_BattleMasterHull OBJECT precedent missing')
print('donor-idiom drift guards OK (EDS PDL module, burst weapon, armour table, cameos, sounds, buttons)')

# ---------------------------------------------------------------- helpers
def apply_patch(text, old, new, label):
    """Exact single-occurrence replacement; patch strings use \\n and are
    re-flowed to the file's own line endings by the caller."""
    n = text.count(old)
    check(n == 1, f'{label}: patch target found {n} times (must be 1): {old[:60]!r}')
    return text.replace(old, new)

def audit(label, old_text, new_text, exp_removed, exp_added):
    co = Counter(l.rstrip('\r') for l in old_text.split('\n'))
    cn = Counter(l.rstrip('\r') for l in new_text.split('\n'))
    removed = sorted((co - cn).elements()); added = sorted((cn - co).elements())
    check(removed == sorted(exp_removed),
          f'{label}: removed-line audit mismatch:\n got {removed}\n exp {sorted(exp_removed)}')
    check(added == sorted(exp_added),
          f'{label}: added-line audit mismatch:\n got {added}\n exp {sorted(exp_added)}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')

def get_block(text, kind, name, label):
    m = re.search(r'^%s\s+%s\b[^\n]*\n(.*?)^End[ \t\r]*$' % (kind, re.escape(name)),
                  text, re.M | re.S)
    check(m, f'{label}: {kind} {name} missing'); return m

# ================================================ FortressBunker.ini (clone)
base_hp = re.search(r'^\s*MaxHealth\s*=\s*(\d+)\s*$', bnk_src, re.M)
check(base_hp, 'Bunker.ini: MaxHealth line not found')
BASE_HP = int(base_hp.group(1))
check(BASE_HP == 1875, f'Bunker.ini base MaxHealth drifted: {BASE_HP} (expected 1875)')
ARMOR_ADD = BASE_HP * ARMOR_RATIO           # 937.5
ARMOR_ADD_S = ('%.1f' % ARMOR_ADD)

KF_MODS = [
    '  ; ------------------------------------------------------------------------------',
    f'  ; {TAG}: three per-bunker purchases (Type=OBJECT upgrades on this bunker\'s own',
    '  ; command bar; player+object upgrade masks are OR\'d -- Object::updateUpgradeModules).',
    f'  Behavior = MaxHealthUpgrade ModuleTag_KF_Armor01 ; {TAG}: Composite Armor -- +{int(ARMOR_RATIO*100)}% of base {BASE_HP}',
    f'    TriggeredBy   = {UP_ARMOR}',
    f'    AddMaxHealth  = {ARMOR_ADD_S}',
    '    ChangeType    = ADD_CURRENT_HEALTH_TOO',
    '  End',
    f'  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_KF_PDL01 ; {TAG}: Point-Defense Laser -- reactive anti-missile LASER burst (EDS hull-PDL idiom; PointDefenseLaserUpdate has no upgrade gate in the deployed engine)',
    '    StartsActive  = No',
    f'    TriggeredBy   = {UP_PDL}',
    '    DamageTypes   = ALL',
    f'    ReactionWeaponPristine      = {W_PDL}',
    f'    ReactionWeaponDamaged       = {W_PDL}',
    f'    ReactionWeaponReallyDamaged = {W_PDL}',
    f'    DamageAmount    = {PDL_TRIGGER_DMG}  ; medium+ hits (shells/rockets/missiles) trigger the pulse',
    '  End',
    f'  Behavior = AutoHealBehavior ModuleTag_KF_Prop01 ; {TAG}: Propaganda Tower -- heal aura for nearby friendlies incl. structures (PropagandaTowerBehavior cannot be OBJECT-gated: effectLogic keys the heal rate off the PLAYER upgrade mask only)',
    '    StartsActive  = No',
    f'    TriggeredBy   = {UP_PROP}',
    f'    HealingAmount = {PROP_HEAL_AMOUNT}',
    f'    HealingDelay  = {PROP_HEAL_DELAY} ; msec',
    f'    Radius        = {PROP_RADIUS}',
    '    KindOf        = INFANTRY VEHICLE STRUCTURE',
    '    SkipSelfForHealing = No',
    '  End',
]
BNK_PATCHES = [  # (old line, new line) -- all single-occurrence, full lines
    ('Object Tank_ChinaBunker',
     f'Object {OBJ_NEW} ; {TAG}: Fortress Bunker (clone of Tank_ChinaBunker)'),
    ('  DisplayName       = OBJECT:TankBunker',
     '  DisplayName       = OBJECT:FortressBunker'),
    ('  BuildCost        = 200',
     f'  BuildCost        = {BUNKER_COST}   ; {TAG}: fortress pricing (base bunker: 200)'),
    ('  CommandSet        = ChinaTankBunkerCommandSet',
     f'  CommandSet        = {CS_MAIN}'),
    ('    CommandSet = ChinaTankBunkerCommandSetUpgrade',
     f'    CommandSet = {CS_UPGD}'),
]
check('\r\n' in bnk_src, 'Bunker.ini expected CRLF line endings')
t = bnk_src
for old, new in BNK_PATCHES:
    t = apply_patch(t, old + '\r\n', new + '\r\n', 'FortressBunker')
anchor = '  Behavior = GarrisonContain ModuleTag_07'
check(t.count(anchor) == 1, 'GarrisonContain anchor not unique')
t = t.replace(anchor, '\r\n'.join(KF_MODS) + '\r\n' + anchor, 1)
new_bnk_text = t
audit('FortressBunker.ini (clone + 3 purchase modules)', bnk_src, new_bnk_text,
      [o for o, n in BNK_PATCHES], [n for o, n in BNK_PATCHES] + KF_MODS)
# clone integrity: everything the bunker is must survive; no stale identity refs
for need in ['Behavior = GarrisonContain ModuleTag_07', 'ContainMax                    = 1',
             'Armor           = FireBaseArmor', f'MaxHealth          = {BASE_HP}',
             'ModuleTag_KD_Armor1', 'ModuleTag_KD_Armor2', 'ModuleTag_KD_Armor3',
             'ModuleTag_KD_Armor4', 'ModuleTag_KBT_Heal01', 'Behavior = ProductionUpdate ModuleTag_10',
             'GenerateMinefieldBehavior', 'Object = Tank_ChinaWarFactory',
             'ModuleTag_Repair01', 'VoiceSelect = TankBunkerSelectionSound']:
    check(need in new_bnk_text, f'FortressBunker lost clone hunk: {need!r}')
code_only = '\n'.join(l.split(';', 1)[0] for l in new_bnk_text.split('\n'))
check(not re.search(r'\bTank_ChinaBunker\b', code_only),
      'stale Tank_ChinaBunker reference (non-comment)')
check(not re.search(r'\bChinaTankBunkerCommandSet(Upgrade)?\b', code_only),
      'stale ChinaTankBunkerCommandSet reference (non-comment)')
check(len(re.findall(r'Behavior = GarrisonContain', new_bnk_text)) == 1, 'GarrisonContain count != 1')
check(len(re.findall(r'Behavior = MaxHealthUpgrade', new_bnk_text)) == 5,
      'expected 5 MaxHealthUpgrade (4 doctrine tiers + Composite Armor)')
check(len(re.findall(r'Behavior = AutoHealBehavior', new_bnk_text)) == 3,
      'expected 3 AutoHealBehavior (auto-repair research + vehicle aura + prop tower)')
bnk_new = new_bnk_text.encode('latin-1')
print(f'FortressBunker.ini built ({OBJ_NEW}: ${BUNKER_COST}, +{ARMOR_ADD_S} HP armor, '
      f'PDL burst trigger {PDL_TRIGGER_DMG}, prop aura {PROP_HEAL_AMOUNT}HP/{PROP_HEAL_DELAY}ms r{PROP_RADIUS})')

# ================================================ CommandSet.ini
cs_text = cs_src.decode('latin-1')
DOZER2 = 'Tank_ChinaDozerCommandSet_Down'
m = get_block(cs_text, 'CommandSet', DOZER2, 'CS')
block = m.group(0)
slots_before = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', m.group(1), re.M))
check('8' not in slots_before, f'{DOZER2}: slot 8 unexpectedly occupied ({slots_before.get("8")})')
for s, want in [('1', 'Tank_Command_ConstructChinaIndustrialPlant'),
                ('7', 'Tank_Command_ConstructChinaBunker'),
                ('9', 'Tank_Command_ConstructChinaTeslaCoil'),
                ('13', 'Command_ChinaButtonCommandSetOneUp'),
                ('14', 'Command_DisarmMinesAtPosition')]:
    check(slots_before.get(s) == want, f'{DOZER2}: slot {s} expected {want}, got {slots_before.get(s)}')
SLOT8 = f'  8  = {CB_BUILD} ; {TAG}'
s7 = re.search(r'^(\s*7\s*=\s*\S+[^\n]*)$', block, re.M)
check(s7, f'{DOZER2}: slot 7 anchor not found')
new_block = block[:s7.end()] + '\n' + SLOT8 + block[s7.end():]
CS_APPEND_LINES = [
    f';;; {TAG}: Fortress Bunker command bars (three per-bunker OBJECT purchases at 2-4;',
    ';;; mines research swaps to the Upgrade variant, same as the base Tank Bunker).',
    f'CommandSet {CS_MAIN}',
    '  1  = Command_EvacuateTankBunker',
    f'  2  = {CB_ARMOR}',
    f'  3  = {CB_PDL}',
    f'  4  = {CB_PROP}',
    ' 12 = Command_Stop',
    ' 13 = Command_UpgradeChinaMines',
    ' 14 = Command_Sell',
    'End',
    '',
    f'CommandSet {CS_UPGD}',
    '  1  = Command_EvacuateTankBunker',
    f'  2  = {CB_ARMOR}',
    f'  3  = {CB_PDL}',
    f'  4  = {CB_PROP}',
    ' 12 = Command_Stop',
    ' 13 = Command_UpgradeEMPMines',
    ' 14 = Command_Sell',
    'End',
]
check(cs_text.endswith('\n'), 'CommandSet.ini must end with newline to append')
cs_new_text = cs_text[:m.start()] + new_block + cs_text[m.end():] + '\n' + '\n'.join(CS_APPEND_LINES) + '\n'
audit('CommandSet.ini (dozer page-2 slot 8 + 2 fortress sets)', cs_text, cs_new_text,
      [], [SLOT8] + CS_APPEND_LINES + [''])   # trailing '' = the blank joiner line
# post-edit layouts
sl = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(cs_new_text, 'CommandSet', DOZER2, 'CS').group(1), re.M))
check(sl == {'1': 'Tank_Command_ConstructChinaIndustrialPlant', '7': 'Tank_Command_ConstructChinaBunker',
             '8': CB_BUILD, '9': 'Tank_Command_ConstructChinaTeslaCoil',
             '13': 'Command_ChinaButtonCommandSetOneUp', '14': 'Command_DisarmMinesAtPosition'},
      f'{DOZER2} post-edit layout wrong: {sl}')
for name, thirteen in [(CS_MAIN, 'Command_UpgradeChinaMines'), (CS_UPGD, 'Command_UpgradeEMPMines')]:
    sl = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), re.M))
    check(sl == {'1': 'Command_EvacuateTankBunker', '2': CB_ARMOR, '3': CB_PDL, '4': CB_PROP,
                 '12': 'Command_Stop', '13': thirteen, '14': 'Command_Sell'},
          f'{name} layout wrong: {sl}')
# sibling survival (spot checks on sets other layers own)
for name, need in [('ChinaTankBunkerCommandSet', 'Command_UpgradeChinaMines'),
                   ('Tank_ChinaDozerCommandSet', 'Command_ChinaButtonCommandSetOneDown'),
                   ('Tank_ChinaWarFactoryCommandSet_Down', 'Tank_Command_UpgradeEmperorPDL'),
                   ('Tank_ChinaHackerBunkerCommandSet', 'Command_StructureExit')]:
    check(need in get_block(cs_new_text, 'CommandSet', name, 'CS').group(1),
          f'survival: {name} lost {need}')
cs_new = cs_new_text.encode('latin-1')
print(f'CommandSet.ini patched (dozer page-2 slot 8 = {CB_BUILD}; +2 fortress sets)')

# ================================================ CommandButton.ini (append)
def upg_button(name, upgrade, base, cameo):
    return '\n'.join([
        f'CommandButton {name}', '  Command       = OBJECT_UPGRADE',
        f'  Upgrade       = {upgrade}', '  Options       = OK_FOR_MULTI_SELECT NOT_QUEUEABLE',
        f'  TextLabel     = CONTROLBAR:Upgrade{base}', f'  ButtonImage   = {cameo}',
        '  ButtonBorderType        = UPGRADE',
        f'  DescriptLabel           = CONTROLBAR:ToolTipUpgrade{base}',
        f'  PurchasedLabel          = CONTROLBAR:ToolTipUpgrade{base}',
        '  UnitSpecificSound = MoneyWithdraw', 'End'])
CB_APPEND = ('\n; ' + '-' * 76 + f'\n; {TAG}: Fortress Bunker construct button (dozer page-2 slot 8) and the\n'
             '; three per-bunker purchase buttons on its own command bar.\n' + '\n'.join([
    f'CommandButton {CB_BUILD}', '  Command       = DOZER_CONSTRUCT',
    '  UnitSpecificSound = MoneyWithdraw', f'  Object        = {OBJ_NEW}',
    '  TextLabel     = CONTROLBAR:ConstructChinaFortressBunker',
    f'  ButtonImage   = {CAMEO_BUNKER}', '  ButtonBorderType        = BUILD',
    '  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildFortressBunker', 'End']) + '\n\n' +
    upg_button(CB_ARMOR, UP_ARMOR, 'FortressCompositeArmor', CAMEO_ARMOR) + '\n\n' +
    upg_button(CB_PDL, UP_PDL, 'FortressPDL', CAMEO_PDL) + '\n\n' +
    upg_button(CB_PROP, UP_PROP, 'FortressPropTower', CAMEO_PROP) + '\n')
check(cb_src.endswith(b'\n'), 'CommandButton.ini must end with newline to append')
cb_new = cb_src + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src), 'CommandButton.ini not append-only')
check(CB_APPEND.count('\nCommandButton ') == 4, 'CB append balance')
print('CommandButton.ini: +4 buttons appended (1 construct + 3 purchases)')

# ================================================ Upgrade.ini (append)
def upgrade_block(name, base, cost, cameo, snd):
    return '\n'.join([f'Upgrade {name}', f'  DisplayName        = UPGRADE:{base}',
                      '  Type               = OBJECT', f'  BuildTime          = {UPG_BUILDTIME}',
                      f'  BuildCost          = {cost}', f'  ButtonImage        = {cameo}',
                      f'  ResearchSound      = {snd}', 'End'])
UPG_APPEND = ('\n; ' + '-' * 76 + f'\n; {TAG}: three per-bunker purchases for the Fortress Bunker (Type=OBJECT --\n'
              '; bought on the bunker itself, one bunker at a time, Overlord-add-on idiom).\n' +
    upgrade_block(UP_ARMOR, 'FortressCompositeArmor', COST_ARMOR, CAMEO_ARMOR, SND_ARMOR) + '\n\n' +
    upgrade_block(UP_PDL, 'FortressPDL', COST_PDL, CAMEO_PDL, SND_PDL) + '\n\n' +
    upgrade_block(UP_PROP, 'FortressPropTower', COST_PROP, CAMEO_PROP, SND_PROP) + '\n')
check(upg_src.endswith(b'\n'), 'Upgrade.ini must end with newline to append')
upg_new = upg_src + UPG_APPEND.encode('latin-1')
check(upg_new.startswith(upg_src), 'Upgrade.ini not append-only')
check(UPG_APPEND.count('\nUpgrade ') == 3 and UPG_APPEND.count('Type               = OBJECT') == 3,
      'Upgrade append balance')
print(f'Upgrade.ini: +3 OBJECT upgrades appended (${COST_ARMOR}/${COST_PDL}/${COST_PROP})')

# ================================================ Generals.str (append)
def s(label, val):
    return f'{label}\n"{val}"\nEND\n'
STR_APPEND = ('\n' +
    s('OBJECT:FortressBunker', 'Fortress Bunker') + '\n' +
    s('CONTROLBAR:ConstructChinaFortressBunker', '&Fortress Bunker') + '\n' +
    s('CONTROLBAR:ToolTipChinaBuildFortressBunker',
      'Fortified bunker that garrisons one combat vehicle, which fires out.\\n'
      ' Can be individually fitted with Composite Armor, a Point-Defense Laser\\n'
      ' and a Propaganda Tower.') + '\n' +
    s('UPGRADE:FortressCompositeArmor', 'Composite Armor') + '\n' +
    s('CONTROLBAR:UpgradeFortressCompositeArmor', '&Composite Armor') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeFortressCompositeArmor',
      'Bolt composite armor plating onto this bunker: permanently adds 50%\\n'
      ' more hit points (and heals the bunker by the added amount).') + '\n' +
    s('UPGRADE:FortressPDL', 'Point-Defense Laser') + '\n' +
    s('CONTROLBAR:UpgradeFortressPDL', '&Point-Defense Laser') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeFortressPDL',
      'Fit this bunker with a point-defense laser: when struck, it pulses an\\n'
      ' anti-missile LASER burst that destroys incoming rockets and missiles\\n'
      ' around the bunker.') + '\n' +
    s('UPGRADE:FortressPropTower', 'Propaganda Tower') + '\n' +
    s('CONTROLBAR:UpgradeFortressPropTower', '&Propaganda Tower') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeFortressPropTower',
      'Mount propaganda speakers on this bunker: projects a healing aura that\\n'
      ' continuously repairs nearby friendly troops, vehicles and structures\\n'
      ' (including the bunker itself).'))
check(str_src.endswith(b'\n'), 'Generals.str must end with newline to append')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src), 'Generals.str not append-only')
check(str_new.decode('latin-1').count('\nEND\n') == str_src.decode('latin-1').count('\nEND\n') + 12,
      'str append entry count (want +12)')
print('Generals.str: +12 entries appended')

# ================================================ global closure
cb_f = cb_new.decode('latin-1'); upg_f = upg_new.decode('latin-1')
str_f = str_new.decode('latin-1')
# construct button -> object -> command sets
b = get_block(cb_f, 'CommandButton', CB_BUILD, 'CB').group(1)
check(f'Object        = {OBJ_NEW}' in b, 'construct button object ref')
check(re.search(r'^Object %s\b' % OBJ_NEW, new_bnk_text, re.M), f'{OBJ_NEW} not defined')
check(f'CommandSet        = {CS_MAIN}' in new_bnk_text, 'object -> main command set ref')
check(f'CommandSet = {CS_UPGD}' in new_bnk_text, 'object -> upgraded command set ref')
# purchase buttons -> upgrades -> modules
for cb, up in [(CB_ARMOR, UP_ARMOR), (CB_PDL, UP_PDL), (CB_PROP, UP_PROP)]:
    bb = get_block(cb_f, 'CommandButton', cb, 'CB').group(1)
    check(f'Upgrade       = {up}' in bb, f'{cb} upgrade ref')
    ub = get_block(upg_f, 'Upgrade', up, 'UPG').group(1)
    check('Type               = OBJECT' in ub, f'{up} not OBJECT-scoped')
    check(f'TriggeredBy   = {up}' in new_bnk_text, f'no module triggered by {up}')
# every slot of the two new sets resolves to a defined button
for name in [CS_MAIN, CS_UPGD]:
    for _, btn in re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), re.M):
        check(re.search(r'^CommandButton\s+%s\b' % re.escape(btn), cb_f, re.M),
              f'{name}: slot button {btn} undefined')
# reaction weapon resolves (defined below us; we do not ship Weapon.ini)
check(new_bnk_text.count(W_PDL) == 3, 'PDL reaction-weapon refs != 3')
check(re.search(r'^Weapon %s\b' % W_PDL, wpn_ref, re.M), f'{W_PDL} not defined below us')
# labels resolve
for lab in NEW_LABELS:
    check(re.search(r'^%s$' % re.escape(lab), str_f, re.M), f'label {lab} missing from str')
    used = lab in new_bnk_text or lab in cb_f or lab in upg_f
    check(used, f'label {lab} defined but unreferenced')
print('closure OK (construct->object->sets->buttons->upgrades->modules->weapon, labels)')

# ------------------------------------------------------------------ write big
entries = [bigfile.BigEntry(P_NEW, bnk_new), bigfile.BigEntry(P_CS, cs_new),
           bigfile.BigEntry(P_CB, cb_new), bigfile.BigEntry(P_UPG, upg_new),
           bigfile.BigEntry(P_STR, str_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries], 'BIG round-trip mismatch')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
with open(out_path, 'wb') as f:
    f.write(blob)
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} files)'
      + (' [hash-idempotent]' if prev == blob else ''))

if '--stage' in sys.argv:
    print('STAGED ONLY (no install) -- run without --stage to install to both mod dirs')
    print('ALL CHECKS PASSED (kwai-fortress, staged)')
    sys.exit(0)

# -------------------------------------------------------------------- install
md5s = []
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    shutil.copyfile(out_path, dst)
    data = open(dst, 'rb').read()
    check(data == blob, f'install verify failed: {dst}')
    md5s.append(hashlib.md5(data).hexdigest())
    posteff = {}
    for b_ in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b_)):
            posteff[e.path.lower()] = (b_, e.data)
    for e in entries:
        check(posteff[e.path.lower()] == (ARCHIVE, e.data),
              f'{d}: {e.path} not effectively ours post-install')
    # spot-check: lower layers keep their non-overlapping ownership
    check(posteff[P_WPN.lower()][0] == OWN_FLG, f'{d}: Weapon.ini ownership regressed')
    check(posteff[P_EMP.lower()][0] == OWN_FLG, f'{d}: Emperor.ini ownership regressed')
    print(f'installed + post-install effective audit OK: {dst}')
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (kwai-fortress)')
