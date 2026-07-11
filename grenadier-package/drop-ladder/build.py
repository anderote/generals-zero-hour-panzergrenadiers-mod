#!/usr/bin/env python3
"""zzz-ZZZZZZZZZZZ1DropLadder.big -- LAYER 2 of the Grenadier Package
(ShockWave / GeneralsX), for Kwai (China Tank General). Sits ON TOP of Layer 1
(zzz-ZZZZZZZZZZZ0GrenadierResearch, whose CommandSet/CommandButton/OCL/Generals.str
it layers on -- shared files, so it MUST sort after Layer 1: 11 Z's + '1').

Three escalating parachute-drop powers hosted on Kwai's Industrial Plant
(the CC command set AND the generals-power shortcut set Tank_SpecialPowerShortcutChina
are BOTH full -- only 2 free shortcut slots for 3 powers -- so per the spec's
"shared-per-faction-set is a problem, document and use ... buttons" clause the
deploy buttons live on the Industrial Plant, the same tech building as the Layer-1
research; ShortcutPower=Yes is still set so the engine may surface them on the
shortcut bar when slots free up). Each is a real SpecialPower (cargo-plane
DeliverPayload OCL -- the proven ShockWave Tank-Paradrop idiom) with its own
steeply-scaled cooldown; available once the Industrial Plant is built ("all
available", the spec-permitted judgement -- ZH special powers have no per-use
cash cost, so escalation is via cooldown length).

Dropped tanks are CREWED variants that load a mixed fire-out crew at birth via
HelixContain's PayloadTemplateName list ("Any number of different passengers can
be loaded at init time" -- HelixContain.cpp:153; overflow is skipped safely) and
spawn AT RANK via VeterancyGainCreate StartingLevel (the JS-7 / Battlemaster
rank-on-spawn idiom).

  Tier 1 'Grenadier Drop'      (cooldown 150 s): 2 Gattling(2 Panzerjager, Regular)
     + loose 8 Panzergrenadier, 2 Sharpshooter, 2 Minigunner, 2 Flame Trooper (Regular)
  Tier 2 'Panzergrenadier Drop'(cooldown 240 s): 4 Battlemaster(2 Panzergrenadier
     + 1 Panzerjager + 1 Flame, VETERAN) + 1 Gattling(2 Panzerjager, HEROIC)
  Tier 3 'Panzer Waffen Drop'  (cooldown 420 s): 2 Emperor + 4 Battlemaster
     + 2 Gattling + 2 Inferno Cannon, all Waffen-mix crewed, all HEROIC

Reads effective from ~/GeneralsX/mods/ShockWaveSPE (everything below this
archive, incl. Layer 1). Depends on ../../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZ1DropLadder.big'   # 11 Z's + '1' (after Layer 1's '0')
TAG = 'zzz-ZZZZZZZZZZZ1DropLadder'
LAYER1 = 'zzz-zzzzzzzzzzz0grenadierresearch.big'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

P_SP  = 'Data\\INI\\SpecialPower.ini'
P_OCL = 'Data\\INI\\ObjectCreationList.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_CS  = 'Data\\INI\\CommandSet.ini'
P_STR = 'Data\\Generals.str'
P_IP  = 'Data\\INI\\Object\\China\\Tank\\Buildings\\IndustrialPlant.ini'
P_DR  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\GrenadierDrops.ini'   # new
# donor tank object files (read-only, cloned)
P_BM  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\BattleMaster.ini'
P_GAT = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\GattlingTank.ini'
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'
P_INF = 'Data\\INI\\Object\\China\\Vanilla\\Vehicles\\InfernoCannon.ini'

EXPECT_OWNER = {
    P_SP.lower():  'zzz-zzzzzzkwaiuav.big',
    P_OCL.lower(): LAYER1,
    P_CB.lower():  LAYER1,
    P_CS.lower():  LAYER1,
    P_STR.lower(): LAYER1,
    P_IP.lower():  'zzz-zzzkwaigarrisons.big',
    P_BM.lower():  LAYER1,   # Layer 1 re-shipped the tank with crew modules
    P_GAT.lower(): 'zzz-zzzzzzzzzzpassengersurvival.big',
    P_EMP.lower(): LAYER1,
    P_INF.lower(): LAYER1,
}
SHIPPED = [P_SP, P_OCL, P_CB, P_CS, P_STR, P_IP, P_DR]

# --- power / button / OCL identifiers
SP  = ['Tank_SpecialPowerGrenadierDrop', 'Tank_SpecialPowerPanzergrenadierDrop', 'Tank_SpecialPowerPanzerWaffenDrop']
ENUM = ['SPECIAL_PARADROP_AMERICA', 'INFA_SPECIAL_PARADROP_AMERICA', 'SPECIAL_CRATE_DROP']
COOLDOWN = [150000, 240000, 420000]
CB  = ['Tank_Command_GrenadierDrop', 'Tank_Command_PanzergrenadierDrop', 'Tank_Command_PanzerWaffenDrop']
OCL = ['Tank_OCL_DropLadderT1', 'Tank_OCL_DropLadderT2', 'Tank_OCL_DropLadderT3']
DROP_CAMEO = ['SNTankeGenGattlingTank', 'NVDBBmaster', 'SNEmpTank']

# --- crewed drop-variant objects: (newname, donorpath, donorobj, [crew...], rank)
PZG, PZJ = 'Tank_ChinaInfantryPanzergrenadier', 'Tank_ChinaInfantryTankHunter'
MIN, FLM = 'Tank_ChinaInfantryMiniGunner', 'Tank_ChinaInfantryFlameThrower'
SHK, SHP = 'Tank_ChinaInfantryShockTrooper', 'Tank_ChinaInfantrySharpshooter'
VARIANTS = [
    ('Tank_DropGattlingT1',      P_GAT, 'Tank_ChinaTankGattling',      [PZJ, PZJ],                          'REGULAR'),
    ('Tank_DropGattlingT2',      P_GAT, 'Tank_ChinaTankGattling',      [PZJ, PZJ],                          'HEROIC'),
    ('Tank_DropGattlingT3',      P_GAT, 'Tank_ChinaTankGattling',      [FLM, SHK],                          'HEROIC'),
    ('Tank_DropBattleMasterT2',  P_BM,  'Tank_ChinaTankBattleMaster',  [PZG, PZG, PZJ, FLM],                'VETERAN'),
    ('Tank_DropBattleMasterT3',  P_BM,  'Tank_ChinaTankBattleMaster',  [MIN, PZJ, FLM, SHK],                'HEROIC'),
    ('Tank_DropEmperorT3',       P_EMP, 'Tank_ChinaTankEmperor',       [MIN, MIN, PZJ, PZJ, FLM, FLM, SHK, SHK], 'HEROIC'),
    ('Tank_DropInfernoT3',       P_INF, 'ChinaVehicleInfernoCannon',   [MIN, PZJ],                          'HEROIC'),
]
BAY = {'Tank_ChinaTankGattling': 2, 'Tank_ChinaTankBattleMaster': 4,
       'Tank_ChinaTankEmperor': 8, 'ChinaVehicleInfernoCannon': 2}

# --- drop rosters (variant object, count) + loose infantry (object, count)
DROPS = [
    # tier 1
    ([('Tank_DropGattlingT1', 2)], [(PZG, 8), (SHP, 2), (MIN, 2), (FLM, 2)]),
    # tier 2
    ([('Tank_DropBattleMasterT2', 4), ('Tank_DropGattlingT2', 1)], []),
    # tier 3
    ([('Tank_DropEmperorT3', 2), ('Tank_DropBattleMasterT3', 4),
      ('Tank_DropGattlingT3', 2), ('Tank_DropInfernoT3', 2)], []),
]

CREW_ALL = {PZG, PZJ, MIN, FLM, SHK, SHP}
NEW_IDS = SP + CB + OCL + [v[0] for v in VARIANTS]
NEW_LABELS = []
for name in ['GrenadierDrop', 'PanzergrenadierDrop', 'PanzerWaffenDrop']:
    NEW_LABELS += [f'CONTROLBAR:{name}', f'CONTROLBAR:ToolTip{name}']

def die(msg):
    print('BUILD FAILED:', msg); sys.exit(1)
def check(cond, msg):
    if not cond: die(msg)
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)

# ---------------------------------------------------------------- sort order
for d in MODDIRS:
    probe = sorted(set(sorted_bigs(d)) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE); below = set(probe[:i]); above = set(probe[i+1:])
    for need in ['zzz-ZZZZZZZZZZZ0GrenadierResearch.big', 'zzz-ZZZZZZZZZZPassengerSurvival.big',
                 'zzz-ZZZZZZKwaiUAV.big', 'zzz-ZZZKwaiGarrisons.big']:
        check(need in below, f'{d}: {need} must sort below us')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above), f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (above Layer 1 + PassengerSurvival, below ControlBarPro*/FXEnhance)')

# ------------------------------------------------- effective space
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
print('effective ownership OK (Layer 1 owns CS/CB/OCL/STR + BM/Emperor/Inferno)')

for d in MODDIRS:
    for b in sorted_bigs(d):
        if str.lower(b) <= ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        for p in SHIPPED:
            check(p.lower() not in claimed, f'{d}/{b} (sorts above us) claims {p}')
print('no higher-sorting archive claims any shipped path')

# ------------------------------------------ collisions + prereq existence
all_ini_text = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                         if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_ini_text),
          f'identifier collision: {ident} already in effective space')
# our 3 enums must NOT be used by any Kwai (Tank_/Kwai) special power
for m in re.finditer(r'^SpecialPower\s+(\S+)\b(.*?)^End', all_ini_text, re.M | re.S):
    if m.group(1).startswith('Tank_') or 'Kwai' in m.group(1):
        en = re.search(r'Enum\s*=\s*(\S+)', m.group(2))
        if en:
            check(en.group(1) not in ENUM, f'enum {en.group(1)} already used by Kwai power {m.group(1)}')
print('new ids/labels collision-free; 3 drop enums unused by Kwai')

# crew infantry + cargo-plane + parachute + cameos resolve
for obj in CREW_ALL | {'ChinaJetCargoPlane', 'ChinaVehicleParachute'}:
    check(re.search(r'^Object\s+%s\b' % re.escape(obj), all_ini_text, re.M), f'referenced object missing: {obj}')
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items() if '\\mappedimages\\' in p)
for img in DROP_CAMEO:
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M), f'cameo MappedImage missing: {img}')
# donor Tank Paradrop drift guard (the idiom we clone)
tp = re.search(r'^SpecialPower\s+Tank_SuperweaponTankParadrop\b(.*?)^End', all_ini_text, re.M | re.S)
check(tp and 'ShortcutPower       = Yes' in tp.group(1) and 'Enum                = SPECIAL_TANK_PARADROP' in tp.group(1),
      'donor Tank Paradrop SpecialPower drifted')
check(re.search(r'^ObjectCreationList\s+Tank_SUPERWEAPON_TankParadrop1\b.*?Transport = ChinaJetCargoPlane.*?PutInContainer = ChinaVehicleParachute',
                all_ini_text, re.M | re.S), 'donor cargo-plane OCL idiom drifted')
print('crew/plane/parachute/cameos resolve; donor paradrop idiom intact')

# ---------------------------------------------------------------- helpers
def audit(label, old, new, exp_removed, exp_added):
    o = [l.rstrip('\r\n') for l in old.decode('latin-1').splitlines()]
    n = [l.rstrip('\r\n') for l in new.decode('latin-1').splitlines()]
    co, cn = Counter(o), Counter(n)
    removed = list((co - cn).elements()); added = list((cn - co).elements())
    check(sorted(removed) == sorted(exp_removed), f'{label}: removed audit:\n got {sorted(removed)}\n exp {sorted(exp_removed)}')
    check(sorted(added) == sorted(exp_added), f'{label}: added audit:\n got {sorted(added)}\n exp {sorted(exp_added)}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')
def get_block(text, kind, name, label):
    m = re.search(r'^%s\s+%s\b[^\n]*\n(.*?)^End[ \t\r]*$' % (kind, re.escape(name)), text, re.M | re.S)
    check(m, f'{label}: {kind} {name} missing'); return m

# ================================================= crewed drop-variant objects
def clone_tank(donor_text, donor_obj, new_obj, crew, rank, bay, label):
    t = donor_text
    check(len(re.findall(r'^Object\s+%s\b' % re.escape(donor_obj), t, re.M)) == 1, f'{label}: donor object not unique')
    t = re.sub(r'^(Object\s+)%s\b' % re.escape(donor_obj), r'\g<1>' + new_obj, t, count=1, flags=re.M)
    # strip Layer-1 factory-crew modules (drop variants carry their own fixed crew)
    t = re.sub(r'[ \t]*Behavior = ObjectCreationUpgrade ModuleTag_GP_Crew\d+.*?\n[ \t]*End[ \t]*\n', '', t, flags=re.S)
    check('ModuleTag_GP_Crew' not in t, f'{label}: GP_Crew strip incomplete')
    # rank-on-spawn: force EVERY VeterancyGainCreate StartingLevel to the target rank
    # (donor tanks carry an unconditional module plus a science-gated ELITE one; setting
    #  both guarantees the spec'd rank regardless of any promotion science)
    nlev = len(re.findall(r'^[ \t]*StartingLevel[ \t]*=', t, re.M))
    check(nlev >= 1, f'{label}: no VeterancyGainCreate StartingLevel to set')
    t, nsub = re.subn(r'^([ \t]*StartingLevel[ \t]*=[ \t]*)\w+', r'\g<1>' + rank, t, flags=re.M)
    check(nsub == nlev, f'{label}: set {nsub}/{nlev} StartingLevel lines -> {rank}')
    # load fixed crew into the (unique) HelixContain bay via PayloadTemplateName
    check(len(re.findall(r'^[ \t]*Behavior = HelixContain\b', t, re.M)) == 1, f'{label}: need exactly one HelixContain')
    slot = list(re.finditer(r'^([ \t]*)Slots[ \t]*=[ \t]*(\d+)[^\n]*$', t, re.M))
    check(len(slot) == 1, f'{label}: need exactly one Slots line (bay), found {len(slot)}')
    check(int(slot[0].group(2)) == bay and len(crew) <= bay, f'{label}: bay {slot[0].group(2)} vs crew {len(crew)} (want {bay})')
    indent = slot[0].group(1)
    ins = '\n'.join(f'{indent}PayloadTemplateName = {c}' for c in crew)
    at = slot[0].end()
    t = t[:at] + '\n' + ins + t[at:]
    return t

drop_objs = []
for new_obj, donorpath, donor_obj, crew, rank in VARIANTS:
    donor_text = eff[donorpath.lower()][1].decode('latin-1')
    body = clone_tank(donor_text, donor_obj, new_obj, crew, rank, BAY[donor_obj],
                      f'clone {new_obj}')
    # closure: every crew name is a known infantry unit; object header renamed
    for c in crew:
        check(c in CREW_ALL, f'{new_obj}: crew {c} unknown')
    check(re.search(r'^Object\s+%s\b' % new_obj, body, re.M), f'{new_obj}: header rename failed')
    drop_objs.append(f'; {TAG}: {new_obj} = drop variant of {donor_obj}, '
                     f'crew [{", ".join(crew)}] at {rank}.\n' + body.rstrip('\n') + '\n')
DR_TEXT = (f'; {TAG} -- crewed parachute-drop tank variants (Layer 2).\n'
           '; Clones of the effective Kwai tanks; factory-crew (GP_Crew) modules stripped;\n'
           '; fixed fire-out crew loaded at birth via HelixContain PayloadTemplateName;\n'
           '; spawn rank set via VeterancyGainCreate StartingLevel.\n\n'
           + '\n'.join(drop_objs))
dr_new = DR_TEXT.encode('latin-1')
check(len(re.findall(r'^Object\s+Tank_Drop', DR_TEXT, re.M)) == 7, 'expected 7 drop variant objects')
print('GrenadierDrops.ini: 7 crewed drop-variant objects built (crews + ranks)')

# ===================================================== SpecialPower.ini append
def sp_block(name, enum, reload_ms):
    return '\n'.join([f'SpecialPower {name}', f'  Enum                = {enum}',
        f'  ReloadTime          = {reload_ms}', '  PublicTimer         = No',
        '  SharedSyncedTimer   = Yes', '  RadiusCursorRadius  = 50',
        '  ViewObjectDuration  = 30000', '  ViewObjectRange     = 70',
        '  ShortcutPower       = Yes', '  AcademyClassify     = ACT_SUPERPOWER', 'End'])
SP_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: three drop powers (cooldown-tiered; hosted on the Industrial Plant).\n' +
    '\n\n'.join(sp_block(SP[i], ENUM[i], COOLDOWN[i]) for i in range(3)) + '\n')
sp_src = eff[P_SP.lower()][1]
check(sp_src.endswith(b'\n'), 'SpecialPower.ini must end with newline')
sp_new = sp_src + SP_APPEND.encode('latin-1')
check(sp_new.startswith(sp_src) and SP_APPEND.count('\nSpecialPower ') == 3, 'SpecialPower append balance')
print('SpecialPower.ini: +3 powers appended')

# ===================================================== ObjectCreationList append
def deliver_block(name, tanks, loose):
    out = [f'ObjectCreationList {name}', '  DeliverPayload', '    Transport = ChinaJetCargoPlane',
           '    StartAtPreferredHeight = Yes', '    StartAtMaxSpeed = Yes', '    MaxAttempts = 4',
           '    DropOffset = X:0 Y:0 Z:-10', '    DropDelay = 300', '    ParachuteDirectly = No',
           '    PutInContainer = ChinaVehicleParachute']
    for obj, cnt in tanks + loose:
        out.append(f'    Payload = {obj} {cnt}')
    out += ['    DeliveryDistance = 0', '    PreOpenDistance = 300', '    DeliveryDecalRadius = 50',
            '    DeliveryDecal', '      Texture           = SCCParadrop_USA', '      Style             = SHADOW_ALPHA_DECAL',
            '      OpacityMin        = 25%', '      OpacityMax        = 50%', '      OpacityThrobTime  = 500',
            '      Color             = R:227 G:229 B:22 A:255', '      OnlyVisibleToOwningPlayer = Yes',
            '    End', '  End', 'End']
    return '\n'.join(out)
OCL_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: three cargo-plane drop OCLs (mixed Payload lines).\n' +
    '\n\n'.join(deliver_block(OCL[i], DROPS[i][0], DROPS[i][1]) for i in range(3)) + '\n')
ocl_src = eff[P_OCL.lower()][1]
check(ocl_src.endswith(b'\n'), 'OCL.ini must end with newline')
ocl_new = ocl_src + OCL_APPEND.encode('latin-1')
check(ocl_new.startswith(ocl_src) and OCL_APPEND.count('\nObjectCreationList ') == 3
      and OCL_APPEND.count('  DeliverPayload') == 3, 'OCL append balance')
print('ObjectCreationList.ini: +3 cargo-plane drop OCLs appended')

# ===================================================== CommandButton.ini append
def cb_block(name, sp, label, cameo, tip):
    return '\n'.join([f'CommandButton {name}', '  Command             = SPECIAL_POWER',
        f'  SpecialPower        = {sp}', '  Options             = NEED_TARGET_POS CONTEXTMODE_COMMAND',
        f'  TextLabel           = {label}', f'  ButtonImage         = {cameo}',
        '  ButtonBorderType    = ACTION', f'  DescriptLabel       = {tip}',
        '  RadiusCursorType    = PARADROP', '  InvalidCursorName   = GenericInvalid',
        '  UnitSpecificSound   = VoiceEvaChinaSelectTarget', 'End'])
names = ['GrenadierDrop', 'PanzergrenadierDrop', 'PanzerWaffenDrop']
CB_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: three drop deploy buttons (Industrial Plant slots 9-11).\n' +
    '\n\n'.join(cb_block(CB[i], SP[i], f'CONTROLBAR:{names[i]}', DROP_CAMEO[i], f'CONTROLBAR:ToolTip{names[i]}')
                for i in range(3)) + '\n')
cb_src = eff[P_CB.lower()][1]
check(cb_src.endswith(b'\n'), 'CommandButton.ini must end with newline')
cb_new = cb_src + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src) and CB_APPEND.count('\nCommandButton ') == 3, 'CB append balance')
print('CommandButton.ini: +3 deploy buttons appended')

# ===================================================== CommandSet.ini (IP slots 9-11)
cs_src = eff[P_CS.lower()][1]; cs_text = cs_src.decode('latin-1')
def patch_ip(text, name):
    m = get_block(text, 'CommandSet', name, 'CS'); block = m.group(0); nb = block
    for slot, btn in [('9', CB[0]), ('10', CB[1]), ('11', CB[2])]:
        o = re.search(r'^(\s*%s\s*=\s*)Command_StructureExit\s*$' % slot, nb, re.M)
        check(o, f'{name}: slot {slot} not Command_StructureExit')
        nb = nb[:o.start()] + o.group(1) + btn + f' ; {TAG}' + nb[o.end():]
    return text[:m.start()] + nb + text[m.end():]
cs_new_text = cs_text
for sname in ['Tank_ChinaIndustrialPlantCommandSet', 'Tank_ChinaIndustrialPlantCommandSetUpgrade']:
    cs_new_text = patch_ip(cs_new_text, sname)
cs_new = cs_new_text.encode('latin-1')
# audit: exactly the 9/10/11 StructureExit lines of BOTH IP blocks are swapped for our buttons
exp_rm, exp_add = [], []
for sname, btnmap in [('Tank_ChinaIndustrialPlantCommandSet', dict(zip('9 10 11'.split(), CB))),
                      ('Tank_ChinaIndustrialPlantCommandSetUpgrade', dict(zip('9 10 11'.split(), CB)))]:
    blk = get_block(cs_text, 'CommandSet', sname, 'CS').group(0)
    for slot, btn in btnmap.items():
        m = re.search(r'^(\s*%s\s*=\s*)Command_StructureExit\s*$' % slot, blk, re.M)
        exp_rm.append(m.group(0).rstrip())
        exp_add.append((m.group(1) + btn + f' ; {TAG}').rstrip())
audit('CommandSet.ini', cs_src, cs_new, exp_rm, exp_add)
def slots(text, name):
    return dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', get_block(text, 'CommandSet', name, 'CS').group(1), re.M))
for name, mines in [('Tank_ChinaIndustrialPlantCommandSet', 'Command_UpgradeChinaMines'),
                    ('Tank_ChinaIndustrialPlantCommandSetUpgrade', 'Command_UpgradeEMPMines')]:
    s = slots(cs_new_text, name)
    check(s['3'].startswith('Tank_Command_UpgradeGrenadier') and s['9'] == CB[0] and s['10'] == CB[1]
          and s['11'] == CB[2] and s['6'] == 'Command_StructureExit' and s['7'] == 'Command_StructureExit'
          and s['8'] == 'Command_StructureExit' and s['12'] == 'Command_Evacuate' and s['13'] == mines
          and s['14'] == 'Command_Sell', f'{name} post-edit layout wrong: {s}')
# survival: Layer-1 researches at 3-5 survive, CC paradrop + barracks survive
check(all(get_block(cs_new_text, 'CommandSet', 'Tank_ChinaIndustrialPlantCommandSet', 'CS').group(1).count(x)
          for x in ['Tank_Command_UpgradeGrenadierPanzergrenadiers']), 'Layer-1 research survival')
check('Tank_Command_TankParadrop' in cs_new_text and
      '1 = Tank_Command_ConstructChinaInfantryPanzergrenadier' in cs_new_text, 'sibling CommandSet survival')
print('CommandSet.ini: IP drop buttons at 9-11 (3 exits->drops); Layer-1 researches + siblings survive')

# ===================================================== Generals.str append
def s(label, val):
    return f'{label}\n"{val}"\nEND\n'
STR_APPEND = ('\n' +
    s('CONTROLBAR:GrenadierDrop', '&Grenadier Drop') + '\n' +
    s('CONTROLBAR:ToolTipGrenadierDrop',
      'Airdrops 2 Gattling Tanks (2 Panzerj\xe4gers each) plus 8 Panzergrenadiers,\\n'
      ' 2 Sharpshooters, 2 Minigunners and 2 Flame Troopers. Cooldown 150 s.') + '\n' +
    s('CONTROLBAR:PanzergrenadierDrop', '&Panzergrenadier Drop') + '\n' +
    s('CONTROLBAR:ToolTipPanzergrenadierDrop',
      'Airdrops 4 Veteran Battlemasters (2 Panzergrenadier + 1 Panzerj\xe4ger + 1 Flame Trooper\\n'
      ' crew) and 1 Heroic Gattling Tank (2 Panzerj\xe4gers). Cooldown 240 s.') + '\n' +
    s('CONTROLBAR:PanzerWaffenDrop', '&Panzer Waffen Drop') + '\n' +
    s('CONTROLBAR:ToolTipPanzerWaffenDrop',
      'Superweapon-tier airborne assault: 2 Emperors, 4 Battlemasters, 2 Gattling Tanks and\\n'
      ' 2 Inferno Cannons, all Waffen-crewed and Heroic. Cooldown 420 s.'))
str_src = eff[P_STR.lower()][1]
check(str_src.endswith(b'\n'), 'Generals.str must end with newline')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src) and
      str_new.decode('latin-1').count('\nEND\n') == str_src.decode('latin-1').count('\nEND\n') + 6,
      'str append entry count (want +6)')
print('Generals.str: +6 entries appended')

# ===================================================== IndustrialPlant OCLSpecialPower
ip_src = eff[P_IP.lower()][1]; ip_text = ip_src.decode('latin-1')
mods = []
for i in range(3):
    mods += [f'  Behavior = OCLSpecialPower ModuleTag_GDrop{i+1} ; {TAG}: tier {i+1} drop power',
             f'    SpecialPowerTemplate = {SP[i]}', f'    OCL                  = {OCL[i]}', '  End']
for tag in ['ModuleTag_GDrop1', 'ModuleTag_GDrop2', 'ModuleTag_GDrop3']:
    check(tag not in ip_text, f'IP: module tag {tag} already present')
geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', ip_text, re.M))
check(len(geo) == 1, f'IP: need exactly one Geometry=BOX anchor (found {len(geo)})')
ip_new_text = ip_text[:geo[0].start()] + '\n'.join(mods) + '\n' + ip_text[geo[0].start():]
ip_new = ip_new_text.encode('latin-1')
audit('IndustrialPlant.ini (+3 OCLSpecialPower)', ip_src, ip_new, [], mods)
# survival: IP keeps its research/garrison/production machinery
for n in ['CommandSet          = Tank_ChinaIndustrialPlantCommandSet', 'ProductionUpdate ModuleTag_10',
          'GarrisonContain ModuleTag_KG_Garrison01', 'CommandSetUpgrade ModuleTag_25']:
    check(n in ip_new_text, f'IP survival lost: {n!r}')
print('IndustrialPlant.ini: +3 OCLSpecialPower modules (host the drop powers); machinery survives')

# ===================================================== global closure
sp_f = sp_new.decode('latin-1'); cb_f = cb_new.decode('latin-1')
ocl_f = ocl_new.decode('latin-1'); str_f = str_new.decode('latin-1'); ip_f = ip_new_text
for i in range(3):
    check(re.search(r'^SpecialPower\s+%s\b' % SP[i], sp_f, re.M), f'{SP[i]} not defined')
    b = get_block(cb_f, 'CommandButton', CB[i], 'CB').group(1)
    check(f'SpecialPower        = {SP[i]}' in b, f'{CB[i]} power ref')
    o = get_block(ocl_f, 'ObjectCreationList', OCL[i], 'OCL').group(1)
    check(f'SpecialPowerTemplate = {SP[i]}' in ip_f and f'OCL                  = {OCL[i]}' in ip_f,
          f'IP OCLSpecialPower for tier {i+1} missing')
    # every Payload object resolves (variant in our file, or known infantry)
    for pl in re.findall(r'Payload = (\S+)', o):
        check(pl in [v[0] for v in VARIANTS] or pl in CREW_ALL, f'{OCL[i]}: payload {pl} unresolved')
# drop-variant objects reference only defined crew (checked) and exist in our file
for v in VARIANTS:
    check(re.search(r'^Object\s+%s\b' % v[0], DR_TEXT, re.M), f'{v[0]} not in GrenadierDrops.ini')
for lab in NEW_LABELS:
    check(re.search(r'^%s$' % re.escape(lab), str_f, re.M), f'label {lab} missing from str')
# roster arithmetic (crew fits bays)
for new_obj, donorpath, donor_obj, crew, rank in VARIANTS:
    check(len(crew) <= BAY[donor_obj], f'{new_obj}: crew {len(crew)} exceeds bay {BAY[donor_obj]}')
print('closure OK (powers<->buttons<->OCLs<->variants<->crew, labels, bay capacities)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_SP, sp_new), bigfile.BigEntry(P_OCL, ocl_new),
           bigfile.BigEntry(P_CB, cb_new), bigfile.BigEntry(P_CS, cs_new),
           bigfile.BigEntry(P_STR, str_new), bigfile.BigEntry(P_IP, ip_new),
           bigfile.BigEntry(P_DR, dr_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries], 'BIG round-trip mismatch')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
open(out_path, 'wb').write(blob)
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} files)' + (' [hash-idempotent]' if prev == blob else ''))

# ------------------------------------------------------------------ install + audit
want_bytes = {e.path.lower(): e.data for e in entries}
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    shutil.copyfile(out_path, dst)
    check(open(dst, 'rb').read() == blob, f'install verify failed: {dst}')
    posteff = {}
    for b in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b)):
            posteff[e.path.lower()] = (b, e.data)
    for p, data in want_bytes.items():
        check(posteff[p][0] == ARCHIVE, f'{d}: {p} effective owner is {posteff[p][0]} not us')
        check(posteff[p][1] == data, f'{d}: {p} installed bytes differ')
    # Layer 1 still owns its non-overlapping files (Upgrade.ini)
    check(posteff['data\\ini\\upgrade.ini'.lower()][0] == 'zzz-ZZZZZZZZZZZ0GrenadierResearch.big',
          f'{d}: Layer-1 Upgrade.ini ownership regressed')
    print('installed + post-install effective audit OK:', dst)
print('ALL CHECKS PASSED (Layer 2)')
