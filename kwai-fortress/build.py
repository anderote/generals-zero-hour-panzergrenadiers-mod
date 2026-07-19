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

SECOND FEATURE -- SATELLITE UPLINK (requires the fork engine >= batch 3):
A PLAYER research at Kwai's Propaganda Center (Tank_ChinaPropagandaCenter,
$2500 / 45 s) that permanently reveals the whole map via the fork's new
`Behavior = MapRevealUpgrade` UpgradeModule (standard TriggeredBy parsing, no
other fields). NOTE: MapRevealUpgrade does NOT exist in the currently deployed
engine binary -- this build must be STAGED ONLY until the batch-3 engine ships
(an older binary fails INI parse on the module name).
Command-set facts found (deviation from 'add to a free slot'): the Kwai
Propaganda Center has NO free UI slot anywhere -- all 50 command-set variants
(base + Upgrade + 48 CS_M{0,1}V{0-4}I{0-4} kwai-doctrine ladder states) are
14/14 full (UI max is 14 windows, ControlBar.h / ControlBarPro .wnd), and no
occupant is dead weight for Kwai (slots 1-5 vanilla researches all live --
Nationalism is engine-hardcoded horde logic, NeutronBomb feeds the Tank command
center; 6-11 doctrine/basetech researches; 12 Evacuate serves the
kwai-garrisons 10-man garrison; 14 Sell). The least-value occupant is the
slot-13 per-building mines purchase (Command_UpgradeChinaMines /
Command_UpgradeEMPMines, a $300 nicety every other Kwai structure also has),
so slot 13 is REPLACED with the Satellite Uplink button across all 50 variants.
The prop center's mines modules (GenerateMinefieldBehavior + the M0<->M1
command-set dimension) stay defined but become dormant/unreachable.

Ships full modified copies of the effective sources:
  Data\\INI\\Object\\China\\Tank\\Defences\\FortressBunker.ini  NEW FILE (clone)
  Data\\INI\\Object\\China\\Tank\\Buildings\\PropagandaCenter.ini
                               (Rebalance copy: +MapRevealUpgrade module)
  Data\\INI\\CommandSet.ini    (TankUpgrades copy: dozer page-2 slot 8 + 2 sets
                               + prop-center slot 13 -> Satellite Uplink x50)
  Data\\INI\\CommandButton.ini (TankUpgrades copy: +5 buttons appended)
  Data\\INI\\Upgrade.ini       (TankUpgrades copy: +3 OBJECT +1 PLAYER appended)
  Data\\Generals.str           (TankUpgrades copy: +15 entries appended)
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
COST_SAT         = 2500    # Satellite Uplink research cost
SAT_BUILDTIME    = 45.0    # seconds, Satellite Uplink research time
COST_BB          = 2000    # Expanded Battle Bunkers research cost
BB_BUILDTIME     = 40.0    # seconds, Expanded Battle Bunkers research time
BB_EMP_ADD       = 4       # Emperor HelixContain bay: 8 -> 12
BB_OVL_ADD       = 3       # Overlord battle-bunker rider TransportContain: 5 -> 8

# ---- paths + expected effective owners ------------------------------------
P_BNK = 'Data\\INI\\Object\\China\\Tank\\Defences\\Bunker.ini'          # clone source
P_NEW = 'Data\\INI\\Object\\China\\Tank\\Defences\\FortressBunker.ini'  # NEW path
P_PC  = 'Data\\INI\\Object\\China\\Tank\\Buildings\\PropagandaCenter.ini'
P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_UPG = 'Data\\INI\\Upgrade.ini'
P_STR = 'Data\\Generals.str'
P_WPN = 'Data\\INI\\Weapon.ini'                                # reference only
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'  # SHIPPED (bay +4)
P_MISC = 'Data\\INI\\Object\\China\\Vanilla\\ChinaMisc.ini'      # SHIPPED (rider +3)

OWN_REB = 'zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big'
OWN_TU  = 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big'
OWN_FLG = 'zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big'
OWN_PS  = 'zzz-ZZZZZZZZZZPassengerSurvival.big'
EXPECT_OWNER = {P_BNK: OWN_REB, P_PC: OWN_REB, P_CS: OWN_TU, P_CB: OWN_TU,
                P_UPG: OWN_TU, P_STR: OWN_TU, P_WPN: OWN_FLG, P_EMP: OWN_FLG,
                P_MISC: OWN_PS}
SHIPPED = [P_NEW, P_PC, P_CS, P_CB, P_UPG, P_STR, P_EMP, P_MISC]

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
UP_SAT   = 'Tank_Upgrade_SatelliteUplink'
CB_SAT   = 'Tank_Command_UpgradeSatelliteUplink'
UP_BB    = 'Tank_Upgrade_ExpandedBattleBunkers'
CB_BB    = 'Tank_Command_UpgradeExpandedBattleBunkers'
MODTAGS  = ['ModuleTag_KF_Armor01', 'ModuleTag_KF_PDL01', 'ModuleTag_KF_Prop01',
            'ModuleTag_KF_Reveal01', 'ModuleTag_KF_Bay01', 'ModuleTag_KF_Bay02']
NEW_IDS  = [OBJ_NEW, CS_MAIN, CS_UPGD, CB_BUILD, UP_ARMOR, UP_PDL, UP_PROP,
            CB_ARMOR, CB_PDL, CB_PROP, UP_SAT, CB_SAT, UP_BB, CB_BB] + MODTAGS
NEW_LABELS = ['OBJECT:FortressBunker', 'CONTROLBAR:ConstructChinaFortressBunker',
              'CONTROLBAR:ToolTipChinaBuildFortressBunker']
for base in ['FortressCompositeArmor', 'FortressPDL', 'FortressPropTower',
             'SatelliteUplink', 'ExpandedBattleBunkers']:
    NEW_LABELS += ['UPGRADE:' + base, 'CONTROLBAR:Upgrade' + base,
                   'CONTROLBAR:ToolTipUpgrade' + base]

# reused existing assets (drift-guarded, never redefined)
CAMEO_BUNKER, CAMEO_ARMOR = 'SNTankBunker', 'SSCompositeArmor'
CAMEO_PDL, CAMEO_PROP     = 'SNBlackSharkJammer', 'SSOLSpeaker'
CAMEO_SAT = 'SSSpySat'   # America spy-satellite cameo, present in effective space
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
# nothing above us may claim our paths; the NEW path must be unclaimed by every
# OTHER archive (an installed copy of this very layer is fine -- idempotent rebuild)
for d in MODDIRS:
    for b in sorted_bigs(d):
        if b.lower() == ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        check(P_NEW.lower() not in claimed, f'{d}/{b} already claims new path {P_NEW}')
        if b.lower() > ARCHIVE.lower():
            for p in SHIPPED:
                check(p.lower() not in claimed, f'{d}/{b} (above us) claims {p}')
print('effective sources OK (owners Rebalance/TankUpgrades/Flagship; dirs byte-agree; '
      'new path unclaimed everywhere; nothing above claims shipped paths)')

bnk_src = eff0[P_BNK.lower()][1].decode('latin-1')
pc_src  = eff0[P_PC.lower()][1].decode('latin-1')
emp_src = eff0[P_EMP.lower()][1].decode('latin-1')
misc_src = eff0[P_MISC.lower()][1].decode('latin-1')
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
for img in [CAMEO_BUNKER, CAMEO_ARMOR, CAMEO_PDL, CAMEO_PROP, CAMEO_SAT]:
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

# ================================================ PropagandaCenter.ini
# Satellite Uplink: fork batch-3 MapRevealUpgrade module, PLAYER-upgrade-gated.
# NOTE deliberately NO engine drift-guard here: MapRevealUpgrade is not in the
# currently deployed engine source -- this layer must stay STAGED until the
# batch-3 binary ships (older binaries fail INI parse on the module name).
check('\r\n' in pc_src, 'PropagandaCenter.ini expected CRLF line endings')
SAT_MODS = [
    f'  Behavior = MapRevealUpgrade ModuleTag_KF_Reveal01 ; {TAG}: Satellite Uplink -- permanently reveals the whole map (fork engine >= batch 3; STAGE-ONLY until deployed)',
    f'    TriggeredBy = {UP_SAT}',
    '  End',
]
pc_anchor = '  Behavior = GarrisonContain ModuleTag_KG_Garrison01'
check(pc_src.count(pc_anchor) == 1, 'PropagandaCenter GarrisonContain anchor not unique')
pc_new_text = pc_src.replace(pc_anchor, '\r\n'.join(SAT_MODS) + '\r\n' + pc_anchor, 1)
audit('PropagandaCenter.ini (+MapRevealUpgrade module)', pc_src, pc_new_text, [], SAT_MODS)
for need in ['Object Tank_ChinaPropagandaCenter', 'ModuleTag_KG_Garrison01',
             'Behavior = ProductionUpdate ModuleTag_10', 'ModuleTag_KD_CS_M0V0I1',
             'CommandSet          = Tank_ChinaPropagandaCenterCommandSet']:
    check(need in pc_new_text, f'PropagandaCenter lost hunk: {need!r}')
check(len(re.findall(r'Behavior = CommandSetUpgrade', pc_new_text))
      == len(re.findall(r'Behavior = CommandSetUpgrade', pc_src)),
      'PropagandaCenter CommandSetUpgrade ladder count changed')
pc_new = pc_new_text.encode('latin-1')
print('PropagandaCenter.ini patched (+MapRevealUpgrade gated by Satellite Uplink)')

# ================================================ Emperor.ini (bay 8 -> 12)
# Expanded Battle Bunkers: fork ContainCapacityUpgrade (deployed -- engine tip
# 'hard-AI scaling keys; unit hover tooltips; ContainCapacityUpgrade'; the bonus
# funnels through OpenContain::m_bonusSlots / getContainMax()).
EMP_SURVIVE = ['Behavior = HelixContain ModuleTag_06', 'Slots                   = 8',
               'ModuleTag_EDS_PDL01', 'ModuleTag_EDS_ABM01', 'ModuleTag_EDS_Shield01',
               'ModuleTag_EDS_Fleet01', 'ModuleTag_EmperorInnatePDL', 'InterceptBallistics',
               'BuildCost', '19200', 'Tank_EmperorTankGun', 'ModuleTag_GP_Crew01',
               'ModuleTag_KPDL_Mount01', 'ModulePropaganda_15']
for n in EMP_SURVIVE:
    check(n in emp_src, f'Emperor prior-layer hunk missing before edit: {n!r}')
EMP_BAY_MODS = [
    f'  Behavior = ContainCapacityUpgrade ModuleTag_KF_Bay01 ; {TAG}: Expanded Battle Bunkers -- Emperor bay 8 -> {8 + BB_EMP_ADD} (fork ContainCapacityUpgrade)',
    f'    TriggeredBy = {UP_BB}',
    f'    AddSlots    = {BB_EMP_ADD}',
    '  End',
]
geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', emp_src, re.M))
check(len(geo) == 1, f'Emperor: need exactly one Geometry=BOX anchor (found {len(geo)})')
emp_new_text = emp_src[:geo[0].start()] + '\n'.join(EMP_BAY_MODS) + '\n' + emp_src[geo[0].start():]
audit('Emperor.ini (+ContainCapacityUpgrade bay module)', emp_src, emp_new_text, [], EMP_BAY_MODS)
for n in EMP_SURVIVE:
    check(n in emp_new_text, f'Emperor prior-layer hunk lost after edit: {n!r}')
emp_new = emp_new_text.encode('latin-1')
print(f'Emperor.ini patched (HelixContain bay +{BB_EMP_ADD} via {UP_BB})')

# ================================================ ChinaMisc.ini (Overlord rider +3)
# The Kwai Overlord is a KwaiRoster BuildVariations stub for the VANILLA
# ChinaTankOverlord, whose battle-bunker purchase spawns the shared rider
# ChinaTankOverlordBattleBunker (OCL_OverlordBattleBunker,
# ContainInsideSourceObject). The module lives on the RIDER object: PLAYER
# upgrades trigger on every owned object, so existing riders upgrade on
# research completion and post-research riders upgrade at spawn. Other
# generals' AIs never own this Kwai-only research -- module stays dormant.
RIDER_RX = re.compile(r'^Object ChinaTankOverlordBattleBunker\b.*?\nEnd', re.M | re.S)
rm = RIDER_RX.search(misc_src)
check(rm, 'ChinaTankOverlordBattleBunker object missing from ChinaMisc.ini')
rider = rm.group(0)
check(rider.count('Behavior = TransportContain ModuleTag_03') == 1,
      'rider TransportContain anchor not unique inside the rider block')
check('Slots                 = 5' in rider, 'rider bunker Slots=5 drifted')
check('DamagePercentToUnits  = 15%' in rider, 'PassengerSurvival rider hunk drifted')
RIDER_MODS = [
    f'  Behavior = ContainCapacityUpgrade ModuleTag_KF_Bay02 ; {TAG}: Expanded Battle Bunkers -- Overlord battle bunker 5 -> {5 + BB_OVL_ADD} (fork ContainCapacityUpgrade)',
    f'    TriggeredBy = {UP_BB}',
    f'    AddSlots    = {BB_OVL_ADD}',
    '  End',
]
rider_anchor = '  Behavior = TransportContain ModuleTag_03'
rider_new = rider.replace(rider_anchor, '\n'.join(RIDER_MODS) + '\n' + rider_anchor, 1)
misc_new_text = misc_src[:rm.start()] + rider_new + misc_src[rm.end():]
audit('ChinaMisc.ini (+rider bay module)', misc_src, misc_new_text, [], RIDER_MODS)
for n in ['Object ChinaHelixBattleBunker', 'Object ChinaTankOverlordGattlingCannon',
          'Object ChinaTankOverlordPropagandaTower']:
    check(n in misc_new_text, f'ChinaMisc sibling object lost: {n!r}')
check(misc_new_text.count('DamagePercentToUnits  = 15%') == misc_src.count('DamagePercentToUnits  = 15%'),
      'PassengerSurvival hunk count changed')
misc_new = misc_new_text.encode('latin-1')
print(f'ChinaMisc.ini patched (Overlord battle-bunker rider +{BB_OVL_ADD} via {UP_BB})')

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

# --- Satellite Uplink button: prop-center slot 13 across ALL 50 doctrine-state
# variants (every set is 14/14 full -- the mines/EMP-mines purchase is the
# sacrificed occupant; see module docstring).
PC_SET_RX = re.compile(r'^CommandSet (Tank_ChinaPropagandaCenter\S*)[^\n]*\n(.*?)^End',
                       re.M | re.S)
pc_sets_before = {n: dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', b, re.M))
                  for n, b in PC_SET_RX.findall(cs_new_text)}
check(len(pc_sets_before) == 50, f'expected 50 prop-center sets, found {len(pc_sets_before)}')
check(all(len(s) == 14 for s in pc_sets_before.values()),
      'expected every prop-center set to be 14/14 full')
flavors = Counter(s['13'] for s in pc_sets_before.values())
check(flavors == {'Command_UpgradeChinaMines': 25, 'Command_UpgradeEMPMines': 25},
      f'prop-center slot-13 flavors drifted: {dict(flavors)}')
SAT_LINE = f' 13  = {CB_SAT} ; {TAG}: Satellite Uplink (was mines/EMP-mines purchase)'
sat_removed = []
def _swap13(mm):
    body = mm.group(0)
    lines = re.findall(r'^[ \t]*13[ \t]*=[ \t]*(?:Command_UpgradeChinaMines|Command_UpgradeEMPMines)[^\n]*$',
                       body, re.M)
    check(len(lines) == 1, f'{mm.group(1)}: expected exactly one mines slot-13 line, got {lines}')
    sat_removed.append(lines[0])
    return body.replace(lines[0], SAT_LINE, 1)
cs_new_text = PC_SET_RX.sub(_swap13, cs_new_text)
check(len(sat_removed) == 50, f'slot-13 replacements: {len(sat_removed)} != 50')

# --- Expanded Battle Bunkers button: War Factory page 2 slot 13. All three WF
# sets (page 1, its vestigial mines variant, page 2) are 14/14 full, but page 2
# slot 13 duplicates page 1's Command_Evacuate (the kwai-garrisons 10-man
# garrison keeps its page-1 Evacuate) -- the only zero-loss occupant anywhere
# on the two candidate hosts, so it is the sacrifice.
WF2 = 'Tank_ChinaWarFactoryCommandSet_Down'
wfm = get_block(cs_new_text, 'CommandSet', WF2, 'CS')
wf_before = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', wfm.group(1), re.M))
check(len(wf_before) == 14, f'{WF2}: expected 14/14 full, got {len(wf_before)}')
for s, want in [('8', 'Tank_Command_UpgradeEmperorPDL'), ('12', 'Command_ChinaButtonCommandSetOneUp'),
                ('13', 'Command_Evacuate'), ('14', 'Command_Sell')]:
    check(wf_before.get(s) == want, f'{WF2}: slot {s} expected {want}, got {wf_before.get(s)}')
WF_EVAC_LINE = '  13 = Command_Evacuate'
BB_LINE = f'  13 = {CB_BB} ; {TAG}: Expanded Battle Bunkers (page-1 Evacuate keeps serving the garrison)'
wf_block = wfm.group(0)
check(len(re.findall(r'^%s$' % re.escape(WF_EVAC_LINE), wf_block, re.M)) == 1,
      f'{WF2}: expected exactly one {WF_EVAC_LINE!r} line')
wf_block_new = re.sub(r'^%s$' % re.escape(WF_EVAC_LINE), BB_LINE, wf_block, count=1, flags=re.M)
cs_new_text = cs_new_text[:wfm.start()] + wf_block_new + cs_new_text[wfm.end():]

audit('CommandSet.ini (dozer slot 8 + 2 fortress sets + prop-center slot 13 x50 + WF2 slot 13)',
      cs_text, cs_new_text,
      sat_removed + [WF_EVAC_LINE],
      [SLOT8] + CS_APPEND_LINES + [''] + [SAT_LINE] * 50 + [BB_LINE])  # '' = blank joiner
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
# prop-center post-edit: slot 13 is the uplink everywhere, all other slots untouched
pc_sets_after = {n: dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', b, re.M))
                 for n, b in PC_SET_RX.findall(cs_new_text)}
check(set(pc_sets_after) == set(pc_sets_before), 'prop-center set names changed')
for n, after in pc_sets_after.items():
    check(after['13'] == CB_SAT, f'{n}: slot 13 is {after["13"]} not {CB_SAT}')
    before = dict(pc_sets_before[n]); before['13'] = CB_SAT
    check(after == before, f'{n}: non-slot-13 slots changed: {after}')
pc_chunk = '\n'.join(mm.group(0) for mm in PC_SET_RX.finditer(cs_new_text))
check('Command_UpgradeChinaMines' not in pc_chunk and 'Command_UpgradeEMPMines' not in pc_chunk,
      'mines buttons still referenced by prop-center sets')
# WF page-2 post-edit: only slot 13 changed; page 1 keeps its garrison Evacuate
wf_after = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(cs_new_text, 'CommandSet', WF2, 'CS').group(1), re.M))
wf_want = dict(wf_before); wf_want['13'] = CB_BB
check(wf_after == wf_want, f'{WF2} post-edit layout wrong: {wf_after}')
for name in ['Tank_ChinaWarFactoryCommandSet', 'Tank_ChinaWarFactoryCommandSetUpgrade']:
    sl = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), re.M))
    check(sl.get('13') == 'Command_Evacuate' and sl.get('6') == 'Tank_Command_ConstructChinaTankEmperor',
          f'{name}: page-1 layout drifted: {sl}')
# sibling survival (spot checks on sets other layers own; mines buttons stay
# live everywhere OUTSIDE the prop center, incl. our own fortress sets)
for name, need in [('ChinaTankBunkerCommandSet', 'Command_UpgradeChinaMines'),
                   ('ChinaTankBunkerCommandSetUpgrade', 'Command_UpgradeEMPMines'),
                   ('Tank_ChinaDozerCommandSet', 'Command_ChinaButtonCommandSetOneDown'),
                   ('Tank_ChinaWarFactoryCommandSet_Down', 'Tank_Command_UpgradeEmperorPDL'),
                   ('Tank_ChinaHackerBunkerCommandSet', 'Command_StructureExit')]:
    check(need in get_block(cs_new_text, 'CommandSet', name, 'CS').group(1),
          f'survival: {name} lost {need}')
cs_new = cs_new_text.encode('latin-1')
print(f'CommandSet.ini patched (dozer page-2 slot 8 = {CB_BUILD}; +2 fortress sets; '
      f'prop-center slot 13 = {CB_SAT} across 50 sets; WF page-2 slot 13 = {CB_BB})')

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
    upg_button(CB_PROP, UP_PROP, 'FortressPropTower', CAMEO_PROP) + '\n\n' + '\n'.join([
    f'CommandButton {CB_SAT} ; {TAG}: Satellite Uplink research (prop-center slot 13)',
    '  Command       = PLAYER_UPGRADE',
    f'  Upgrade       = {UP_SAT}',
    '  Options       = OK_FOR_MULTI_SELECT',
    '  TextLabel     = CONTROLBAR:UpgradeSatelliteUplink',
    f'  ButtonImage   = {CAMEO_SAT}',
    '  ButtonBorderType        = UPGRADE',
    '  DescriptLabel           = CONTROLBAR:ToolTipUpgradeSatelliteUplink',
    '  PurchasedLabel          = CONTROLBAR:ToolTipUpgradeSatelliteUplink',
    '  UnitSpecificSound = MoneyWithdraw', 'End']) + '\n\n' + '\n'.join([
    f'CommandButton {CB_BB} ; {TAG}: Expanded Battle Bunkers research (War Factory page-2 slot 13)',
    '  Command       = PLAYER_UPGRADE',
    f'  Upgrade       = {UP_BB}',
    '  Options       = OK_FOR_MULTI_SELECT',
    '  TextLabel     = CONTROLBAR:UpgradeExpandedBattleBunkers',
    f'  ButtonImage   = {CAMEO_BUNKER}',
    '  ButtonBorderType        = UPGRADE',
    '  DescriptLabel           = CONTROLBAR:ToolTipUpgradeExpandedBattleBunkers',
    '  PurchasedLabel          = CONTROLBAR:ToolTipUpgradeExpandedBattleBunkers',
    '  UnitSpecificSound = MoneyWithdraw', 'End']) + '\n')
check(cb_src.endswith(b'\n'), 'CommandButton.ini must end with newline to append')
cb_new = cb_src + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src), 'CommandButton.ini not append-only')
check(CB_APPEND.count('\nCommandButton ') == 6, 'CB append balance')
print('CommandButton.ini: +6 buttons appended (1 construct + 3 purchases + 2 researches)')

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
    upgrade_block(UP_PROP, 'FortressPropTower', COST_PROP, CAMEO_PROP, SND_PROP) + '\n\n' + '\n'.join([
    f'Upgrade {UP_SAT} ; {TAG}: Satellite Uplink -- permanent full-map reveal (fork engine >= batch 3)',
    '  DisplayName        = UPGRADE:SatelliteUplink',
    '  Type               = PLAYER',
    f'  BuildTime          = {SAT_BUILDTIME}',
    f'  BuildCost          = {COST_SAT}',
    f'  ButtonImage        = {CAMEO_SAT}',
    f'  ResearchSound      = {SND_ARMOR}', 'End']) + '\n\n' + '\n'.join([
    f'Upgrade {UP_BB} ; {TAG}: Expanded Battle Bunkers -- Emperor bay +{BB_EMP_ADD}, Overlord bunker +{BB_OVL_ADD} (fork ContainCapacityUpgrade)',
    '  DisplayName        = UPGRADE:ExpandedBattleBunkers',
    '  Type               = PLAYER',
    f'  BuildTime          = {BB_BUILDTIME}',
    f'  BuildCost          = {COST_BB}',
    f'  ButtonImage        = {CAMEO_BUNKER}',
    f'  ResearchSound      = {SND_ARMOR}', 'End']) + '\n')
check(upg_src.endswith(b'\n'), 'Upgrade.ini must end with newline to append')
upg_new = upg_src + UPG_APPEND.encode('latin-1')
check(upg_new.startswith(upg_src), 'Upgrade.ini not append-only')
check(UPG_APPEND.count('\nUpgrade ') == 5 and UPG_APPEND.count('Type               = OBJECT') == 3
      and UPG_APPEND.count('Type               = PLAYER') == 2, 'Upgrade append balance')
print(f'Upgrade.ini: +3 OBJECT (${COST_ARMOR}/${COST_PDL}/${COST_PROP}) '
      f'+2 PLAYER (${COST_SAT}/${COST_BB}) upgrades appended')

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
      ' (including the bunker itself).') + '\n' +
    s('UPGRADE:SatelliteUplink', 'Satellite Uplink') + '\n' +
    s('CONTROLBAR:UpgradeSatelliteUplink', 'Satellite &Uplink') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeSatelliteUplink',
      'Satellite Uplink: reveals the entire battlefield permanently.') + '\n' +
    s('UPGRADE:ExpandedBattleBunkers', 'Expanded Battle Bunkers') + '\n' +
    s('CONTROLBAR:UpgradeExpandedBattleBunkers', 'E&xpanded Battle Bunkers') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeExpandedBattleBunkers',
      'Enlarge the battle bunkers of the fleet: Emperor bunker bays hold 4 more\\n'
      ' soldiers and Overlord battle bunkers hold 3 more.'))
check(str_src.endswith(b'\n'), 'Generals.str must end with newline to append')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src), 'Generals.str not append-only')
check(str_new.decode('latin-1').count('\nEND\n') == str_src.decode('latin-1').count('\nEND\n') + 18,
      'str append entry count (want +18)')
print('Generals.str: +18 entries appended')

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
# Satellite Uplink chain: button -> PLAYER upgrade -> MapRevealUpgrade module
sb = get_block(cb_f, 'CommandButton', CB_SAT, 'CB').group(1)
check(f'Upgrade       = {UP_SAT}' in sb, f'{CB_SAT} upgrade ref')
sub = get_block(upg_f, 'Upgrade', UP_SAT, 'UPG').group(1)
check('Type               = PLAYER' in sub, f'{UP_SAT} not PLAYER-scoped')
check(f'TriggeredBy = {UP_SAT}' in pc_new_text, f'prop center has no module triggered by {UP_SAT}')
check('Behavior = MapRevealUpgrade ModuleTag_KF_Reveal01' in pc_new_text,
      'MapRevealUpgrade module missing from prop center')
# Expanded Battle Bunkers chain: button -> PLAYER upgrade -> 2 capacity modules
bb = get_block(cb_f, 'CommandButton', CB_BB, 'CB').group(1)
check(f'Upgrade       = {UP_BB}' in bb, f'{CB_BB} upgrade ref')
bub = get_block(upg_f, 'Upgrade', UP_BB, 'UPG').group(1)
check('Type               = PLAYER' in bub, f'{UP_BB} not PLAYER-scoped')
check('Behavior = ContainCapacityUpgrade ModuleTag_KF_Bay01' in emp_new_text
      and f'TriggeredBy = {UP_BB}' in emp_new_text, 'Emperor bay module missing/unwired')
check('Behavior = ContainCapacityUpgrade ModuleTag_KF_Bay02' in misc_new_text
      and f'TriggeredBy = {UP_BB}' in misc_new_text, 'rider bay module missing/unwired')
check(f'AddSlots    = {BB_EMP_ADD}' in emp_new_text and f'AddSlots    = {BB_OVL_ADD}' in misc_new_text,
      'AddSlots values missing')
# every slot of the new/edited sets resolves
for name in [CS_MAIN, CS_UPGD, WF2] + sorted(pc_sets_after):
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
entries = [bigfile.BigEntry(P_NEW, bnk_new), bigfile.BigEntry(P_PC, pc_new),
           bigfile.BigEntry(P_EMP, emp_new), bigfile.BigEntry(P_MISC, misc_new),
           bigfile.BigEntry(P_CS, cs_new), bigfile.BigEntry(P_CB, cb_new),
           bigfile.BigEntry(P_UPG, upg_new), bigfile.BigEntry(P_STR, str_new)]
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
    # (Emperor.ini is now OURS post-install -- covered by the entries loop above)
    check(posteff[P_WPN.lower()][0] == OWN_FLG, f'{d}: Weapon.ini ownership regressed')
    print(f'installed + post-install effective audit OK: {dst}')
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (kwai-fortress)')
