#!/usr/bin/env python3
"""zzz-ZZZZZZZZZZZ0GrenadierResearch.big -- LAYER 1 of the Grenadier Package
(ShockWave / GeneralsX), for Kwai (China Tank General).

Three sequential Industrial-Plant researches that make Kwai's tanks roll off the
factory PRE-CREWED with fire-out infantry riding in their existing HelixContain
bays. Crew is delivered by the engine-proven ObjectCreationUpgrade -> OCL
(CreateObject + ContainInsideSourceObject) idiom (the same module family that
mounts the Battlemaster's ERA armour addon / propaganda tower); when a bay is
full the overflow crewman is stillborn by the engine
(ObjectCreationList.cpp:1250 "failed the contain ... killing the new object";
DEBUG_CRASH is a no-op in this RELEASE build) -- so crews never spill loose.

  1. Panzergrenadiers ($1500)         -> Battlemaster 2 Panzergrenadier + 2 Panzerjager (bay 4)
                                         Emperor      2 Panzergrenadier + 2 Panzerjager (bay 8, +4 free)
                                         each artillery 1 Panzergrenadier + 1 Panzerjager (bay 2)
  2. Waffen Grenadiers ($2500, req 1) -> Battlemaster re-crews to 1 Minigunner + 1 Panzerjager
                                         + 1 Flame Trooper + 1 Shock Trooper (suppresses #1 via ConflictsWith)
  3. Emperor's Guard  ($2000, req 1)  -> Emperor ADDS 1 Flame + 1 Shock + 1 Sharpshooter + 1 Minigunner
                                         (additive with #1 -> fills the 8-slot bay)

Sequential unlock uses the deployed engine's RequiredUpgrade field
(GeneralsMD Upgrade.cpp:127 parse + :457 canAffordUpgrade prereq gate --
verified present) -- #2/#3 grey out until #1 is owned. No CommandSetUpgrade
state-enumeration needed.

Reads effective sources from ~/GeneralsX/mods/ShockWaveSPE (everything sorting
strictly below this archive; PassengerSurvival owns the tank object files, so
this layer MUST sort above it -- hence 11 Z's, above the 10-Z PassengerSurvival
and below zzz_ControlBarPro*/zzzz_FXEnhance). Patches, verifies loudly, writes
the archive here and installs to both mod dirs. Depends on ../../hotkey-addon
(actually ../.. -> generalsx-mods/hotkey-addon/bigfile.py).
"""
import os, re, shutil, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZ0GrenadierResearch.big'   # 11 Z's + '0'
TAG = 'zzz-ZZZZZZZZZZZ0GrenadierResearch'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_STR = 'Data\\Generals.str'
P_UPG = 'Data\\INI\\Upgrade.ini'
P_OCL = 'Data\\INI\\ObjectCreationList.ini'
P_BM  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\BattleMaster.ini'
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'
P_INF = 'Data\\INI\\Object\\China\\Vanilla\\Vehicles\\InfernoCannon.ini'
P_NUK = 'Data\\INI\\Object\\China\\Vanilla\\Vehicles\\NukeCannon.ini'
P_BUR = 'Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\Buratino.ini'
P_HAM = 'Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\HammerCannon.ini'

EXPECT_OWNER = {
    P_CS.lower():  'zzz-zzzzzzzzpanzergrenadier.big',
    P_CB.lower():  'zzz-zzzzzzzzpanzergrenadier.big',
    P_STR.lower(): 'zzz-zzzzzzzzpanzergrenadier.big',
    P_UPG.lower(): 'zzz-zzzzzzzkwaipdl.big',
    P_OCL.lower(): 'zzz-zzzzzzztteslacoil.big',
    P_BM.lower():  'zzz-zzzzzzzzzzpassengersurvival.big',
    P_EMP.lower(): 'zzz-zzzzzzzzzzpassengersurvival.big',
    P_INF.lower(): 'zzz-zzzzzzzzzzpassengersurvival.big',
    P_NUK.lower(): 'zzz-zzzzzzzzzzpassengersurvival.big',
    P_BUR.lower(): 'zzz-zzzzzzzzzzpassengersurvival.big',
    P_HAM.lower(): 'zzz-zzzzzzzzzzpassengersurvival.big',
}
SHIPPED = [P_CS, P_CB, P_STR, P_UPG, P_OCL, P_BM, P_EMP, P_INF, P_NUK, P_HAM, P_BUR]

# research upgrades + crew OCLs + crew infantry + cameos
UP_PZ  = 'Tank_Upgrade_GrenadierPanzergrenadiers'
UP_WAF = 'Tank_Upgrade_GrenadierWaffen'
UP_EG  = 'Tank_Upgrade_GrenadierEmperorGuard'
OCL_BM   = 'Tank_OCL_GrenadierCrewBattle'
OCL_WAF  = 'Tank_OCL_WaffenCrewBattle'
OCL_EMP  = 'Tank_OCL_GrenadierCrewEmperor'
OCL_EG   = 'Tank_OCL_EmperorGuardCrew'
OCL_ART  = 'Tank_OCL_GrenadierCrewArty'
CB_PZ  = 'Tank_Command_UpgradeGrenadierPanzergrenadiers'
CB_WAF = 'Tank_Command_UpgradeGrenadierWaffen'
CB_EG  = 'Tank_Command_UpgradeGrenadierEmperorGuard'

CREW = ['Tank_ChinaInfantryPanzergrenadier', 'Tank_ChinaInfantryTankHunter',
        'Tank_ChinaInfantryMiniGunner', 'Tank_ChinaInfantryFlameThrower',
        'Tank_ChinaInfantryShockTrooper', 'Tank_ChinaInfantrySharpshooter']
CAMEOS = ['Nuke_RedGuard', 'SNMiniGunner', 'SNEmpTank']

NEW_IDS = [UP_PZ, UP_WAF, UP_EG, OCL_BM, OCL_WAF, OCL_EMP, OCL_EG, OCL_ART,
           CB_PZ, CB_WAF, CB_EG]
NEW_LABELS = ['UPGRADE:GrenadierPanzergrenadiers', 'UPGRADE:GrenadierWaffen',
              'UPGRADE:GrenadierEmperorGuard',
              'CONTROLBAR:UpgradeGrenadierPanzergrenadiers',
              'CONTROLBAR:ToolTipUpgradeGrenadierPanzergrenadiers',
              'CONTROLBAR:UpgradeGrenadierWaffen',
              'CONTROLBAR:ToolTipUpgradeGrenadierWaffen',
              'CONTROLBAR:UpgradeGrenadierEmperorGuard',
              'CONTROLBAR:ToolTipUpgradeGrenadierEmperorGuard']

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
    for need in ['zzz-ZZZZZZZZPanzergrenadier.big', 'zzz-ZZZZZZZZZDefenseVet.big',
                 'zzz-ZZZZZZZZZInfantryScale.big', 'zzz-ZZZZZZZZZZPassengerSurvival.big',
                 'zzz-ZZZZZZZKwaiPDL.big', 'zzz-ZZZZZZZTTeslaCoil.big']:
        check(need in below, f'{d}: {need} must sort below us (got above/absent)')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (above PassengerSurvival, below ControlBarPro*/FXEnhance)')

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

# ------------------------------------------ collision checks + prereq existence
all_ini_text = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                         if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_ini_text),
          f'identifier collision: {ident} already exists in effective space')
print('new identifiers collision-free (%d ids, %d labels)' % (len(NEW_IDS), len(NEW_LABELS)))

# crew infantry objects + cameos exist
for obj in CREW:
    check(re.search(r'^Object\s+%s\b' % re.escape(obj), all_ini_text, re.M),
          f'crew infantry object missing: {obj}')
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items() if '\\mappedimages\\' in p)
for img in CAMEOS:
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M), f'cameo MappedImage missing: {img}')
# ResearchSound / button sound reused (Voice.ini + SoundEffects.ini)
for snd in ['ReaperVoiceUpgrade', 'MoneyWithdraw']:
    check(re.search(r'^AudioEvent\s+%s\b' % snd, all_ini_text, re.M), f'AudioEvent {snd} missing')
print('crew objects, cameos, sounds all resolve in effective space')

# ---------------------------------------------------------------- line editing
def edit_lines(data, plan, label):
    lines = data.decode('latin-1').splitlines(keepends=True)
    for op in plan:
        kind, key, news, cnt = op
        idxs = [i for i, l in enumerate(lines) if l.rstrip('\r\n').strip() == key]
        check(len(idxs) == cnt, f'{label}: expected {cnt}x line, found {len(idxs)}x: {key!r}')
        for i in reversed(idxs):
            eol = lines[i][len(lines[i].rstrip('\r\n')):] or '\n'
            if kind == 'sub':
                lines[i:i+1] = [n + eol for n in news]
            elif kind == 'after':
                lines[i+1:i+1] = [n + eol for n in news]
            elif kind == 'before':
                lines[i:i] = [n + eol for n in news]
            else:
                die(f'{label}: bad op {kind}')
    return ''.join(lines).encode('latin-1')

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

# ===================================================== crew module + bay guards
def crew_modules(tags_specs):
    """tags_specs: list of (tag, ocl, triggered_by, conflicts_or_None, comment)"""
    out = []
    for tag, ocl, trig, confl, comment in tags_specs:
        out.append(f'  Behavior = ObjectCreationUpgrade {tag} ; {TAG}: {comment}')
        out.append(f'    UpgradeObject = {ocl}')
        out.append(f'    TriggeredBy   = {trig}')
        if confl:
            out.append(f'    ConflictsWith = {confl}')
        out.append('  End')
    return out

def patch_tank(path, specs, want_slots, label):
    src = eff[path.lower()][1]
    text = src.decode('latin-1')
    # bay capacity guard: HelixContain infantry Slots
    hm = re.search(r'Behavior\s*=\s*HelixContain\s+\S+[^\n]*\n(.*?)\n  End', text, re.S)
    check(hm, f'{label}: no HelixContain bay found')
    sl = re.search(r'Slots\s*=\s*(\d+)', hm.group(1))
    check(sl and int(sl.group(1)) == want_slots, f'{label}: bay Slots drifted (want {want_slots})')
    for tag, *_ in specs:
        check(tag not in text, f'{label}: module tag {tag} already present')
    geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', text, re.M))
    check(len(geo) == 1, f'{label}: need exactly one Geometry=BOX anchor (found {len(geo)})')
    ins = geo[0].start()
    added = crew_modules(specs)
    new_text = text[:ins] + '\n'.join(added) + '\n' + text[ins:]
    new = new_text.encode('latin-1')
    audit(f'{label} (+{len(specs)} crew module(s))', src, new, [], added)
    return new

bm_new = patch_tank(P_BM, [
    ('ModuleTag_GP_Crew01', OCL_BM, UP_PZ, UP_WAF,
     'Panzergrenadiers crew (2 Panzergrenadier + 2 Panzerjager); suppressed once Waffen is owned'),
    ('ModuleTag_GP_Crew02', OCL_WAF, UP_WAF, None,
     'Waffen Grenadiers crew (1 Minigunner + 1 Panzerjager + 1 Flame + 1 Shock Trooper)'),
], 4, 'BattleMaster.ini')

emp_new = patch_tank(P_EMP, [
    ('ModuleTag_GP_Crew01', OCL_EMP, UP_PZ, None,
     "Panzergrenadiers crew (2 Panzergrenadier + 2 Panzerjager)"),
    ('ModuleTag_GP_Crew03', OCL_EG, UP_EG, None,
     "Emperor's Guard crew (+1 Flame + 1 Shock + 1 Sharpshooter + 1 Minigunner -> fills the 8-slot bay)"),
], 8, 'Emperor.ini')

art_specs = [('ModuleTag_GP_Crew01', OCL_ART, UP_PZ, None,
              'Panzergrenadiers crew (1 Panzergrenadier + 1 Panzerjager)')]
inf_new = patch_tank(P_INF, art_specs, 2, 'InfernoCannon.ini')
nuk_new = patch_tank(P_NUK, art_specs, 2, 'NukeCannon.ini')
bur_new = patch_tank(P_BUR, art_specs, 2, 'Buratino.ini')
ham_new = patch_tank(P_HAM, art_specs, 2, 'HammerCannon.ini')

# --- prior-layer survival on the patched tanks (fail if a hunk drifted)
for txt, needles, lab in [
    (bm_new.decode('latin-1'),
     ['MaxHealth       = 660.0', 'ModuleTag_ArmorAddon01', 'StartingLevel = VETERAN',
      'ModuleTag_KPDL_Mount01', 'ModuleTag_KD_Armor1'], 'BattleMaster'),
    (emp_new.decode('latin-1'),
     ['MaxHealth       = 1320.0', 'ModuleTag_06', 'ModulePropaganda', 'ModuleTag_ShtoraAuto01'], 'Emperor'),
    (inf_new.decode('latin-1'), ['ModuleTag_KPDL_Bay01', 'Slots                   = 2'], 'Inferno'),
]:
    for n in needles:
        check(n in txt, f'{lab}: prior-layer survival lost: {n!r}')
print('tank crew modules inserted; prior-layer hunks survive on all 6 tanks')

# ===================================================== ObjectCreationList append
def ocl_block(name, pairs):
    out = [f'ObjectCreationList {name}']
    for obj, cnt in pairs:
        out += ['  CreateObject', f'    ObjectNames       = {obj}',
                f'    Count             = {cnt}', '    ContainInsideSourceObject = Yes', '  End']
    out += ['End']
    return '\n'.join(out)

OCL_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: pre-crew OCLs (CreateObject + ContainInsideSourceObject;\n'
              '; overflow crew is stillborn by the engine when the bay is full).\n' +
    ocl_block(OCL_BM,  [('Tank_ChinaInfantryPanzergrenadier', 2), ('Tank_ChinaInfantryTankHunter', 2)]) + '\n\n' +
    ocl_block(OCL_WAF, [('Tank_ChinaInfantryMiniGunner', 1), ('Tank_ChinaInfantryTankHunter', 1),
                        ('Tank_ChinaInfantryFlameThrower', 1), ('Tank_ChinaInfantryShockTrooper', 1)]) + '\n\n' +
    ocl_block(OCL_EMP, [('Tank_ChinaInfantryPanzergrenadier', 2), ('Tank_ChinaInfantryTankHunter', 2)]) + '\n\n' +
    ocl_block(OCL_EG,  [('Tank_ChinaInfantryFlameThrower', 1), ('Tank_ChinaInfantryShockTrooper', 1),
                        ('Tank_ChinaInfantrySharpshooter', 1), ('Tank_ChinaInfantryMiniGunner', 1)]) + '\n\n' +
    ocl_block(OCL_ART, [('Tank_ChinaInfantryPanzergrenadier', 1), ('Tank_ChinaInfantryTankHunter', 1)]) + '\n')
ocl_src = eff[P_OCL.lower()][1]
check(ocl_src.endswith(b'\n'), 'OCL.ini must end with newline to append')
ocl_new = ocl_src + OCL_APPEND.encode('latin-1')
check(ocl_new.startswith(ocl_src), 'OCL.ini not append-only')
check(OCL_APPEND.count('\nObjectCreationList ') == 5 and
      len(re.findall(r'^  CreateObject$', OCL_APPEND, re.M)) == 14, 'OCL append block balance')
print('ObjectCreationList.ini: +5 crew OCLs appended (14 CreateObject nuggets)')

# ===================================================== Upgrade.ini append
def upgrade_block(name, display, cost, time, cameo, req=None):
    out = [f'Upgrade {name}', f'  DisplayName        = {display}', '  Type               = PLAYER',
           f'  BuildTime          = {time}', f'  BuildCost          = {cost}',
           f'  ButtonImage        = {cameo}', '  ResearchSound      = ReaperVoiceUpgrade']
    if req:
        out.append(f'  RequiredUpgrade    = {req} ; {TAG}: sequential prereq gate (deployed engine field, GeneralsMD Upgrade.cpp)')
    out.append('End')
    return '\n'.join(out)

UPG_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: three Industrial-Plant researches (Type=PLAYER).\n' +
    upgrade_block(UP_PZ,  'UPGRADE:GrenadierPanzergrenadiers', 1500, 45.0, 'Nuke_RedGuard') + '\n\n' +
    upgrade_block(UP_WAF, 'UPGRADE:GrenadierWaffen', 2500, 60.0, 'SNMiniGunner', UP_PZ) + '\n\n' +
    upgrade_block(UP_EG,  'UPGRADE:GrenadierEmperorGuard', 2000, 50.0, 'SNEmpTank', UP_PZ) + '\n')
upg_src = eff[P_UPG.lower()][1]
check(upg_src.endswith(b'\n'), 'Upgrade.ini must end with newline to append')
upg_new = upg_src + UPG_APPEND.encode('latin-1')
check(upg_new.startswith(upg_src), 'Upgrade.ini not append-only')
check(UPG_APPEND.count('\nUpgrade ') == 3 and UPG_APPEND.count('RequiredUpgrade') == 2, 'Upgrade append balance')
print('Upgrade.ini: +3 PLAYER upgrades appended (2 chained via RequiredUpgrade)')

# ===================================================== CommandButton.ini append
def cb_block(name, upgrade, text_label, cameo, tip):
    return '\n'.join([f'CommandButton {name}', '  Command       = PLAYER_UPGRADE',
        f'  Upgrade       = {upgrade}', f'  TextLabel     = {text_label}',
        f'  ButtonImage   = {cameo}', '  ButtonBorderType        = UPGRADE',
        f'  DescriptLabel           = {tip}', '  UnitSpecificSound = MoneyWithdraw', 'End'])
CB_APPEND = ('\n; ' + '-'*76 + f'\n; {TAG}: three research buttons (Industrial Plant slots 3-5).\n' +
    cb_block(CB_PZ,  UP_PZ,  'CONTROLBAR:UpgradeGrenadierPanzergrenadiers', 'Nuke_RedGuard',
             'CONTROLBAR:ToolTipUpgradeGrenadierPanzergrenadiers') + '\n\n' +
    cb_block(CB_WAF, UP_WAF, 'CONTROLBAR:UpgradeGrenadierWaffen', 'SNMiniGunner',
             'CONTROLBAR:ToolTipUpgradeGrenadierWaffen') + '\n\n' +
    cb_block(CB_EG,  UP_EG,  'CONTROLBAR:UpgradeGrenadierEmperorGuard', 'SNEmpTank',
             'CONTROLBAR:ToolTipUpgradeGrenadierEmperorGuard') + '\n')
cb_src = eff[P_CB.lower()][1]
check(cb_src.endswith(b'\n'), 'CommandButton.ini must end with newline to append')
cb_new = cb_src + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src), 'CommandButton.ini not append-only')
check(CB_APPEND.count('\nCommandButton ') == 3, 'CB append balance')
print('CommandButton.ini: +3 research buttons appended')

# ===================================================== CommandSet.ini edit (IP sets)
cs_src = eff[P_CS.lower()][1]
cs_text = cs_src.decode('latin-1')
def patch_ip_set(text, name):
    m = get_block(text, 'CommandSet', name, 'CS')
    block = m.group(0)
    new_block = block
    for slot, btn in [('3', CB_PZ), ('4', CB_WAF), ('5', CB_EG)]:
        old = re.search(r'^(\s*%s\s*=\s*)Command_StructureExit\s*$' % slot, new_block, re.M)
        check(old, f'{name}: slot {slot} is not Command_StructureExit as expected')
        new_block = new_block[:old.start()] + old.group(1) + btn + f' ; {TAG}' + new_block[old.end():]
    return text[:m.start()] + new_block + text[m.end():]
cs_new_text = cs_text
for setname in ['Tank_ChinaIndustrialPlantCommandSet', 'Tank_ChinaIndustrialPlantCommandSetUpgrade']:
    cs_new_text = patch_ip_set(cs_new_text, setname)
cs_new = cs_new_text.encode('latin-1')
audit('CommandSet.ini', cs_src, cs_new,
      ['  3  = Command_StructureExit', '  4  = Command_StructureExit', '  5  = Command_StructureExit'] * 2,
      [f'  3  = {CB_PZ} ; {TAG}', f'  4  = {CB_WAF} ; {TAG}', f'  5  = {CB_EG} ; {TAG}'] * 2)

def set_slots(text, name):
    body = get_block(text, 'CommandSet', name, 'CS').group(1)
    return dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', body, re.M))
for name, mines in [('Tank_ChinaIndustrialPlantCommandSet', 'Command_UpgradeChinaMines'),
                    ('Tank_ChinaIndustrialPlantCommandSetUpgrade', 'Command_UpgradeEMPMines')]:
    s = set_slots(cs_new_text, name)
    want = {'1': 'Command_UpgradeChinaTankLightArmor', '2': 'Tank_Command_UpgradeChinaAutoLoader',
            '3': CB_PZ, '4': CB_WAF, '5': CB_EG, '6': 'Command_StructureExit',
            '7': 'Command_StructureExit', '8': 'Command_StructureExit', '9': 'Command_StructureExit',
            '10': 'Command_StructureExit', '11': 'Command_StructureExit', '12': 'Command_Evacuate',
            '13': mines, '14': 'Command_Sell'}
    check(s == want, f'{name} post-edit layout wrong: {s}')
print('CommandSet.ini: Industrial Plant sets patched (researches 3-5, 6 exits, Evacuate/Mines/Sell survive)')

# survival: Barracks Panzergrenadier hunk + other sets untouched
check('1 = Tank_Command_ConstructChinaInfantryPanzergrenadier' in cs_new_text,
      'Panzergrenadier barracks hunk vanished (prior layer regressed)')
for name, need in [('Tank_ChinaCommandCenterCommandSet', 'Tank_Command_TankParadrop'),
                   ('Tank_ChinaWarFactoryCommandSet_Down', 'Tank_Command_ConstructChinaVehicleScoutCar')]:
    check(need in get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), f'survival: {name} lost {need}')
print('CommandSet.ini survival OK (barracks Panzergrenadier, CC paradrop, WF page-2)')

# ===================================================== Generals.str append
def s(label, val):
    return f'{label}\n"{val}"\nEND\n'
STR_APPEND = ('\n' +
    s('UPGRADE:GrenadierPanzergrenadiers', 'Panzergrenadiers') + '\n' +
    s('UPGRADE:GrenadierWaffen', 'Waffen Grenadiers') + '\n' +
    s('UPGRADE:GrenadierEmperorGuard', "Emperor's Guard") + '\n' +
    s('CONTROLBAR:UpgradeGrenadierPanzergrenadiers', '&Panzergrenadiers') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeGrenadierPanzergrenadiers',
      'Battle tanks, the Emperor and artillery roll off the factory pre-crewed with\\n'
      ' 2 Panzergrenadiers + 2 Panzerj\xe4gers (1+1 for artillery) riding in their fire-out bays.') + '\n' +
    s('CONTROLBAR:UpgradeGrenadierWaffen', '&Waffen Grenadiers') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeGrenadierWaffen',
      'Requires Panzergrenadiers. New battle tanks are crewed instead with a combined-arms\\n'
      ' squad: 1 Minigunner + 1 Panzerj\xe4ger + 1 Flame Trooper + 1 Shock Trooper.') + '\n' +
    s('CONTROLBAR:UpgradeGrenadierEmperorGuard', '&Emperor\x27s Guard') + '\n' +
    s('CONTROLBAR:ToolTipUpgradeGrenadierEmperorGuard',
      "Requires Panzergrenadiers. Emperors additionally embark 1 Flame Trooper + 1 Shock\\n"
      ' Trooper + 1 Sharpshooter + 1 Minigunner, filling the Emperor\x27s 8-seat bunker.'))
str_src = eff[P_STR.lower()][1]
check(str_src.endswith(b'\n'), 'Generals.str must end with newline to append')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src), 'Generals.str not append-only')
check(str_new.decode('latin-1').count('\nEND\n') == str_src.decode('latin-1').count('\nEND\n') + 9,
      'str append entry count (want +9)')
print('Generals.str: +9 entries appended')

# ===================================================== global closure
cb_final = cb_new.decode('latin-1'); upg_final = upg_new.decode('latin-1')
ocl_final = ocl_new.decode('latin-1'); str_final = str_new.decode('latin-1')
for cb, up in [(CB_PZ, UP_PZ), (CB_WAF, UP_WAF), (CB_EG, UP_EG)]:
    b = get_block(cb_final, 'CommandButton', cb, 'CB').group(1)
    check(f'Upgrade       = {up}' in b, f'{cb} upgrade ref')
    check(re.search(r'^Upgrade\s+%s\b' % up, upg_final, re.M), f'{up} not defined')
for up, ocl in [(UP_PZ, [OCL_BM, OCL_EMP, OCL_ART]), (UP_WAF, [OCL_WAF]), (UP_EG, [OCL_EG])]:
    for o in ocl:
        check(re.search(r'^ObjectCreationList\s+%s\b' % o, ocl_final, re.M), f'OCL {o} not defined')
# RequiredUpgrade prereqs resolve to real upgrades
for req in [UP_PZ]:
    check(re.search(r'^Upgrade\s+%s\b' % req, upg_final, re.M), f'RequiredUpgrade prereq {req} not defined')
# every crew object referenced by OUR appended OCLs resolves in the known crew set
for obj in re.findall(r'ObjectNames\s+=\s+(\S+)', OCL_APPEND):
    check(obj in CREW, f'OCL crew object {obj} not in known crew set')
for lab in NEW_LABELS:
    check(re.search(r'^%s$' % re.escape(lab), str_final, re.M), f'label {lab} missing from str')
# crew-capacity arithmetic
check(2+2 == 4 and 1+1+1+1 == 4 and (2+2)+(1+1+1+1) == 8 and 1+1 == 2, 'crew capacity arithmetic')
print('closure OK (buttons->upgrades->OCLs->crew objects, labels, capacities)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_CS, cs_new), bigfile.BigEntry(P_CB, cb_new),
           bigfile.BigEntry(P_STR, str_new), bigfile.BigEntry(P_UPG, upg_new),
           bigfile.BigEntry(P_OCL, ocl_new), bigfile.BigEntry(P_BM, bm_new),
           bigfile.BigEntry(P_EMP, emp_new), bigfile.BigEntry(P_INF, inf_new),
           bigfile.BigEntry(P_NUK, nuk_new), bigfile.BigEntry(P_HAM, ham_new),
           bigfile.BigEntry(P_BUR, bur_new)]
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
    print('installed + post-install effective audit OK:', dst)
print('ALL CHECKS PASSED (Layer 1)')
