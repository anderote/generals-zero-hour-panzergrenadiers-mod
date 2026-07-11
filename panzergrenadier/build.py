#!/usr/bin/env python3
"""zzz-ZZZZZZZZPanzergrenadier.big — the Panzergrenadier unit layer of the
Panzergrenadiers stack (ShockWave / GeneralsX). Two features:

1. NEW UNIT Tank_ChinaInfantryPanzergrenadier — Kwai's namesake elite assault
   infantry, a full clone of the effective vanilla ChinaInfantryRedguard with:
   - Nuke-RG reskin (NINRDGRD meshes on the same NICNSC skeletons; the mesh's
     under-barrel grenade-launcher subobject 'WeaponA' shows by default) and
     the Nuke_RedGuard cameo/portrait — visually distinct, zero new art;
   - Tank_PanzergrenadierRifle: 18->22.5 damage (+25%), range 110->135,
     DamageType SMALL_ARMS->EXPLOSION ("GUN" is NOT a DamageType in this
     engine — Core/GameEngine/Include/GameLogic/Damage.h enum; EXPLOSION is
     unlisted in HumanArmor/HumveeArmor/TankArmor/StructureArmor = 100% vs
     all four, giving the spec'd vehicle/structure damage);
   - Tank_PanzergrenadierGrenade SECONDARY: 60 dmg r15 (+25 r30 secondary)
     EXPLOSION grenade, clip 1 / 8 s reload, auto-chosen when loaded
     (WeaponSet::chooseBestWeaponForTarget picks the higher single-shot
     estimate, 60 > 22.5, and never returns a reloading weapon while another
     is ready — so: grenade opener, rifle while reloading). PreferredAgainst
     was deliberately NOT used: a matching PreferredAgainst slot stays chosen
     even while merely reloading (WeaponSet.cpp: "preferred weapons are also
     kept if they are merely reloading"), which would cap the unit at the
     grenade's 7.5 dps against that KindOf class;
   - 144 HP (+20% over the ShockWave Red Guard's 120), elite XP ladder,
     BuildCost/BuildTime baked FINAL at 225/6.0 s (= spec $450/12 s
     pre-halved to match w-economy's China-infantry halving — that layer's
     32-object enumeration gate cannot admit a new unit without a rebuild).
   It REPLACES the Red Guard in Kwai's Barracks slot 1 (both set variants);
   the Tank_ChinaInfantryRedguard stub + its construct button stay defined
   but unreferenced (hotfix Hacker-Bunker dormancy idiom).
2. PANZERJAEGER RENAME (Kwai-scoped): the Tank_ChinaInfantryTankHunter stub
   gains DisplayName = OBJECT:TankPanzerjager and its construct button is
   relabeled "Panzerj\xe4ger" + new tooltip via append-only Generals.str
   entries. The vanilla Tank Hunter object/button/labels are untouched (the
   stub-spawned unit itself still reads "Tank Hunter" when selected —
   documented limitation).

Reads effective sources from ~/GeneralsX/mods/ShockWaveSPE (excluding its own
archive AND every archive sorting above it: zzz_ControlBarPro*/zzzz_FXEnhance
belong to other sessions), patches, verifies loudly, writes the archive here
and installs to both mod dirs. Depends on ../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZPanzergrenadier.big'
TAG = 'zzz-ZZZZZZZZPanzergrenadier'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_STR = 'Data\\Generals.str'
P_WPN = 'Data\\INI\\Weapon.ini'
P_TH  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\TankHunter.ini'
P_PZ  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\Panzergrenadier.ini'  # new
# read-only sources / drift-guard files
P_RGV = 'Data\\INI\\Object\\China\\Vanilla\\Infantry\\Redguard.ini'   # clone donor
P_RGN = 'Data\\INI\\Object\\China\\Nuke\\Infantry\\RedGuard.ini'      # reskin donor
P_RGT = 'Data\\INI\\Object\\China\\Tank\\Infantry\\RedGuard.ini'      # dormant stub
P_ARM = 'Data\\INI\\Armor.ini'

EXPECT_OWNER = {
    P_CS.lower():  'zzz-zzzzzzzxhotfix.big',
    P_CB.lower():  'zzz-zzzzzzzweconomy.big',
    P_STR.lower(): 'zzz-zzzzzzztteslacoil.big',
    P_WPN.lower(): 'zzz-zzzzzzztteslacoil.big',
    P_TH.lower():  'zzz-zzzzzzzweconomy.big',
    P_RGV.lower(): 'zzz-zzzzzzzweconomy.big',
    P_RGN.lower(): 'zzz-zzzzzzzweconomy.big',
    P_RGT.lower(): 'zzz-zzzzzzzweconomy.big',
    P_ARM.lower(): 'zzz-zzzzzzzrotrinfantry.big',
}
SHIPPED = [P_CS, P_CB, P_STR, P_WPN, P_TH, P_PZ]

NEW_IDS = ['Tank_ChinaInfantryPanzergrenadier', 'Tank_PanzergrenadierRifle',
           'Tank_PanzergrenadierGrenade',
           'Tank_Command_ConstructChinaInfantryPanzergrenadier']
NEW_LABELS = ['OBJECT:TankPanzergrenadier',
              'CONTROLBAR:ConstructTankPanzergrenadier',
              'CONTROLBAR:ToolTipTankBuildPanzergrenadier',
              'OBJECT:TankPanzerjager',
              'CONTROLBAR:ConstructTankPanzerjager',
              'CONTROLBAR:ToolTipTankBuildPanzerjager']

def die(msg):
    print('BUILD FAILED:', msg)
    sys.exit(1)

def check(cond, msg):
    if not cond:
        die(msg)

# ---------------------------------------------------------------- sort order
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')),
                  key=str.lower)

for d in MODDIRS:
    names = sorted_bigs(d)
    probe = sorted(set(names) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE)
    below = set(probe[:i]); above = set(probe[i+1:])
    for need in ['zzz-ZZZZZZZXHotfix.big', 'zzz-ZZZZZZZWEconomy.big',
                 'zzz-ZZZZZZZTTeslaCoil.big', 'zzz-ZZZZZZZRotrInfantry.big',
                 'zzz-ZZZZZZZLKwaiInfantry.big', 'zzz-ZZZZZKwaiRoster.big']:
        check(need in below, f'{d}: {need} must sort below us')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzzz_fxenhance') for a in above),
          f'{d}: FXEnhance must sort above us')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (after XHotfix, below ControlBarPro*/FXEnhance)')

# ------------------------------------------------- effective space (primary)
def load_effective(moddir):
    eff = {}          # lowpath -> (owner, bytes)
    for b in sorted_bigs(moddir):
        if str.lower(b) >= ARCHIVE.lower():
            continue  # never source from ourselves or layers above us
        for e in bigfile.read_big(os.path.join(moddir, b)):
            eff[e.path.lower()] = (b, e.data)
    return eff

eff = load_effective(PRIMARY)
for p, owner in EXPECT_OWNER.items():
    check(p in eff, f'missing effective file {p}')
    check(eff[p][0].lower() == owner,
          f'{p}: effective owner drifted: {eff[p][0]} (expected {owner})')
print('effective ownership OK:', {p.split("\\")[-1]: eff[p][0] for p in EXPECT_OWNER})

# no archive above us (in either dir) may claim any path we ship
for d in MODDIRS:
    for b in sorted_bigs(d):
        if str.lower(b) <= ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        for p in SHIPPED:
            check(p.lower() not in claimed, f'{d}/{b} (sorts above us) claims {p}')
print('no higher-sorting archive claims any shipped path')

# ------------------------------------------ new identifier collision checks
all_ini_text = '\n'.join(data.decode('latin-1')
                         for p, (b, data) in eff.items()
                         if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS + ['Panzergrenadier', 'Panzerjager']:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_ini_text),
          f'identifier collision: {ident} already exists in effective space')
print('new identifiers collision-free (%d ids, %d labels)'
      % (len(NEW_IDS), len(NEW_LABELS)))

# --------------------------------------------------------------- line editing
def edit_lines(data, plan, label):
    """plan: list of ops on stripped-line content:
       ('sub', old_stripped, [new_line_contents], expected_count)
       ('after', anchor_stripped, [new_line_contents], expected_count)
    Returns (new_bytes, removed_lines, added_lines) for auditing."""
    lines = data.decode('latin-1').splitlines(keepends=True)
    removed, added = [], []
    for op in plan:
        kind, key, news, cnt = op
        idxs = [i for i, l in enumerate(lines) if l.rstrip('\r\n').strip() == key]
        check(len(idxs) == cnt,
              f'{label}: expected {cnt}x line, found {len(idxs)}x: {key!r}')
        for i in reversed(idxs):
            eol = lines[i][len(lines[i].rstrip('\r\n')):] or '\n'
            if kind == 'sub':
                removed.append(lines[i].rstrip('\r\n'))
                lines[i:i+1] = [n + eol for n in news]
            elif kind == 'after':
                lines[i+1:i+1] = [n + eol for n in news]
            else:
                die(f'{label}: bad op {kind}')
            added.extend(news)
    return ''.join(lines).encode('latin-1'), removed, added

def audit(label, old, new, exp_removed, exp_added):
    o = [l.rstrip('\r\n') for l in old.decode('latin-1').splitlines()]
    n = [l.rstrip('\r\n') for l in new.decode('latin-1').splitlines()]
    co, cn = Counter(o), Counter(n)
    removed = list((co - cn).elements())
    added = list((cn - co).elements())
    check(sorted(removed) == sorted(exp_removed),
          f'{label}: removed-line audit mismatch:\n got {sorted(removed)}\n exp {sorted(exp_removed)}')
    check(sorted(added) == sorted(exp_added),
          f'{label}: added-line audit mismatch:\n got {sorted(added)}\n exp {sorted(exp_added)}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')

def get_block(text, kind, name, label):
    m = re.search(r'^%s\s+%s\b[^\n]*\n(.*?)^End[ \t\r]*$' % (kind, re.escape(name)),
                  text, re.M | re.S)
    check(m, f'{label}: {kind} {name} missing')
    return m

# =================================================================== donors
rgv_src = eff[P_RGV.lower()][1]
rgv_text = rgv_src.decode('latin-1')
rgn_text = eff[P_RGN.lower()][1].decode('latin-1')
arm_text = eff[P_ARM.lower()][1].decode('latin-1')
wpn_src = eff[P_WPN.lower()][1]
wpn_text = wpn_src.decode('latin-1')
cs_src = eff[P_CS.lower()][1]
cb_src = eff[P_CB.lower()][1]
str_src = eff[P_STR.lower()][1]
th_src = eff[P_TH.lower()][1]

# --- donor drift guards: vanilla Red Guard rifle (the numbers we scale from)
rg_rifle = get_block(wpn_text, 'Weapon', 'RedguardMachineGun', 'WPN').group(1)
check(re.search(r'PrimaryDamage\s*=\s*18\.0', rg_rifle), 'RG rifle damage drifted (want 18.0)')
check(re.search(r'AttackRange\s*=\s*110\.0', rg_rifle), 'RG rifle range drifted (want 110.0)')
check(re.search(r'DelayBetweenShots\s*=\s*1000\b', rg_rifle), 'RG rifle ROF drifted (want 1000)')
check(re.search(r'DamageType\s*=\s*SMALL_ARMS', rg_rifle), 'RG rifle damage type drifted')
for bonus in ['WeaponBonus           = PLAYER_UPGRADE DAMAGE 125%',
              'WeaponBonus           = PLAYER_UPGRADE RANGE 120%']:
    check(bonus in rg_rifle, f'RG rifle doctrine bonus line missing: {bonus}')

# --- armor-table facts the EXPLOSION choice rests on (unlisted = 100%)
for arm in ['HumanArmor', 'TankArmor', 'HumveeArmor', 'StructureArmor']:
    body = get_block(arm_text, 'Armor', arm, 'ARM').group(1)
    check(not re.search(r'^\s*Armor\s*=\s*EXPLOSION\b', body, re.M),
          f'{arm} now lists EXPLOSION explicitly — 100% assumption broken, re-tune')
check(re.search(r'Armor\s*=\s*SMALL_ARMS\s*25%',
                get_block(arm_text, 'Armor', 'TankArmor', 'ARM').group(1)),
      'TankArmor SMALL_ARMS drifted (want 25%)')

# --- Nuke RG reskin facts (mesh rides the vanilla NICNSC skeleton/anims)
check('Model               = NINRDGRD_SKN' in rgn_text and
      'IdleAnimation       = NICNSC_SKL.NICNSC_STA' in rgn_text,
      'Nuke RG no longer pairs NINRDGRD_SKN with NICNSC_SKL anims')
check('NINRDGRD_F_SKN' in rgn_text and 'NICNSC_F_SKL.NICNSC_F_FDP1' in rgn_text,
      'Nuke RG capture-flag reskin pairing drifted')
check('HideSubObject = WeaponA' in rgn_text,
      'Nuke RG WeaponA grenade-launcher subobject vanished from the mesh idiom')
# cameo images exist
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                   if '\\mappedimages\\' in p)
for img in ['Nuke_RedGuard', 'Nuke_RedGuard_L', 'SNTankHunter']:
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M),
          f'mapped image {img} missing')

# --- grenade ingredient closure (all live references, nothing shipped)
wo_text = eff['data\\ini\\object\\weaponobjects.ini'][1].decode('latin-1')
ig = get_block(wo_text, 'Object', 'InfantryGrenade', 'WO').group(1)
check('DumbProjectileBehavior' in ig, 'InfantryGrenade lost its arc behavior')
fx_text = eff['data\\ini\\fxlist.ini'][1].decode('latin-1')
for fx in ['FX_OICWGrenadeImpact', 'WeaponFX_GenericMachineGunFire',
           'WeaponFX_GenericMachineGunFireWithRedTracers']:
    check(re.search(r'^FXList\s+%s\b' % fx, fx_text, re.M), f'FXList {fx} missing')
snd_text = eff['data\\ini\\soundeffects.ini'][1].decode('latin-1')
for snd in ['RedGuardWeapon', 'FireOICWGrenadeBurton', 'MoneyWithdraw']:
    check(re.search(r'^AudioEvent\s+%s\b' % snd, snd_text, re.M),
          f'AudioEvent {snd} missing')

# --- upgrades/science the clone references must exist
up_text = eff['data\\ini\\upgrade.ini'][1].decode('latin-1')
for u in ['Tank_Upgrade_KwaiInfantryArmor1', 'Tank_Upgrade_KwaiInfantryArmor2',
          'Tank_Upgrade_KwaiInfantryArmor3', 'Tank_Upgrade_KwaiInfantryArmor4',
          'Tank_Upgrade_KwaiInfantryDoctrine', 'Upgrade_InfantryCaptureBuilding',
          'Upgrade_GLAWorkerFakeCommandSet', 'Upgrade_Nationalism']:
    check(re.search(r'^Upgrade\s+%s\b' % u, up_text, re.M), f'Upgrade {u} missing')
check('SCIENCE_RedGuardTraining' in
      eff['data\\ini\\science.ini'][1].decode('latin-1'),
      'SCIENCE_RedGuardTraining missing')
print('donor drift guards + ingredient closure OK')

# ============================================== 1a. the Panzergrenadier clone
CLONE_HEADER = [
 f'; {TAG}: Tank_ChinaInfantryPanzergrenadier - Kwai elite assault infantry.',
 '; Full clone of the effective vanilla ChinaInfantryRedguard (owner at build',
 '; time: zzz-ZZZZZZZWEconomy.big). Documented deltas vs the donor:',
 ';   renamed + Side = ChinaTankGeneral + DisplayName OBJECT:TankPanzergrenadier;',
 ';   prereq Tank_ChinaBarracks; Nuke-RG reskin (NINRDGRD_SKN/_F_SKN meshes on',
 ';   the same NICNSC skeletons/anims; the mesh WeaponA under-barrel grenade',
 ';   launcher shows by default because no HideSubObject line hides it) +',
 ';   Nuke_RedGuard cameo/portrait; SECONDARY fire/launch bones at Muzzle;',
 ';   weapons: PRIMARY Tank_PanzergrenadierRifle / SECONDARY',
 ';   Tank_PanzergrenadierGrenade (donor stun-bullet dropped) / TERTIARY donor',
 ';   bayonet; MaxHealth 120 -> 144 (+20%), doctrine armor tiers 18 -> 21.6;',
 ';   VisionRange 100 -> 135 (rifle range); ExperienceValue 5 5 10 20 ->',
 ';   6 6 12 24; ExperienceRequired 0 20 40 80 -> 0 25 50 100 (elite ladder);',
 ';   BuildCost/BuildTime FINAL 225/6.0 (= spec $450/12 s pre-halved: the',
 ';   w-economy layer halves all China infantry but its 32-object enumeration',
 ';   gate cannot admit this unit without a w-economy rebuild - so the halved',
 ';   price is baked here instead).',
]
clone_plan = [
 ('sub', 'Object ChinaInfantryRedguard',
  CLONE_HEADER + ['Object Tank_ChinaInfantryPanzergrenadier'], 1),
 ('sub', 'SelectPortrait         = SNRedGuard_L',
  [f'  SelectPortrait         = Nuke_RedGuard_L ; {TAG}: Nuke-RG reskin cameo'], 1),
 ('sub', 'ButtonImage            = SNRedGuard',
  [f'  ButtonImage            = Nuke_RedGuard ; {TAG}: Nuke-RG reskin cameo'], 1),
 ('sub', 'Model               = NICNSC_SKN',
  [f'      Model               = NINRDGRD_SKN ; {TAG}: Nuke-RG reskin mesh (same NICNSC skeleton)'], 1),
 ('sub', 'Model             = NICNSC_F_SKN',
  [f'      Model             = NINRDGRD_F_SKN ; {TAG}: Nuke-RG reskin flag mesh'], 4),
 ('after', 'WeaponMuzzleFlash   = PRIMARY MuzzleFX',
  [f'      WeaponFireFXBone    = SECONDARY Muzzle ; {TAG}: grenade launcher',
   f'      WeaponLaunchBone    = SECONDARY Muzzle ; {TAG}: grenade launcher'], 1),
 ('sub', 'DisplayName         = OBJECT:Redguard',
  ['  DisplayName         = OBJECT:TankPanzergrenadier'], 1),
 ('sub', 'Side                = China',
  ['  Side                = ChinaTankGeneral'], 1),
 ('sub', 'Weapon              = PRIMARY   RedguardMachineGun',
  [f'    Weapon              = PRIMARY   Tank_PanzergrenadierRifle ; {TAG}: HE rifle, +25% dmg / range 135'], 1),
 ('sub', 'Weapon              = SECONDARY RedguardStunBulletMachineGun',
  [f'    Weapon              = SECONDARY Tank_PanzergrenadierGrenade ; {TAG}: AoE grenade, auto-chosen when loaded (donor stun bullet dropped)'], 1),
 ('sub', 'AutoChooseSources   = SECONDARY NONE', [], 1),   # grenade is auto-chosen
 ('sub', 'VisionRange = 100',
  [f'  VisionRange = 135 ; {TAG}: was 100 (match rifle range)'], 1),
 ('sub', 'Object = ChinaBarracks', ['    Object = Tank_ChinaBarracks'], 1),
 ('sub', 'BuildCost     = 150 ; zzz-ZZZZZZZWEconomy: was 300 (50%)',
  [f'  BuildCost     = 225 ; {TAG}: FINAL price - spec $450 pre-halved for w-economy China-infantry parity'], 1),
 ('sub', 'BuildTime     = 5.0          ;in seconds       ; zzz-ZZZZZZZWEconomy: was 10.0 (2x build speed)',
  [f'  BuildTime     = 6.0          ;in seconds ; {TAG}: FINAL time - spec 12 s pre-halved for w-economy parity'], 1),
 ('sub', 'ExperienceValue = 5 5 10 20   ;Experience point value at each level',
  [f'  ExperienceValue = 6 6 12 24   ; {TAG}: elite (+20% over Red Guard)'], 1),
 ('sub', 'ExperienceRequired = 0 20 40 80  ;Experience points needed to gain each level',
  [f'  ExperienceRequired = 0 25 50 100  ; {TAG}: elite ladder (slightly elevated)'], 1),
 ('sub', 'MaxHealth       = 120.0',
  [f'    MaxHealth       = 144.0 ; {TAG}: +20% over Red Guard 120'], 1),
 ('sub', 'InitialHealth   = 120.0', ['    InitialHealth   = 144.0'], 1),
 ('sub', 'AddMaxHealth  = 18.0',
  [f'    AddMaxHealth  = 21.6 ; {TAG}: 15% of base 144.0'], 4),
]
for tagn in '1234':
    clone_plan.append((
        'sub',
        f'Behavior = MaxHealthUpgrade ModuleTag_KD_Armor{tagn} ; zzz-KwaiDoctrine: +15% of base 120.0 for ChinaInfantryRedguard',
        [f'  Behavior = MaxHealthUpgrade ModuleTag_KD_Armor{tagn} ; zzz-KwaiDoctrine idiom, rescaled by {TAG}'], 1))

pz_new, pz_removed, pz_added = edit_lines(rgv_src, clone_plan, 'PZ')
audit('Panzergrenadier.ini (clone vs donor)', rgv_src, pz_new, pz_removed, pz_added)
# the clone must keep every donor module (module-tag census donor==clone,
# minus nothing) and drop the stun bullet / keep the bayonet
pz_text = pz_new.decode('latin-1')
check(re.findall(r'ModuleTag_\w+', pz_text) == re.findall(r'ModuleTag_\w+', rgv_text),
      'clone module-tag census differs from donor')
check('RedguardStunBulletMachineGun' not in pz_text, 'stun bullet still referenced')
check('Weapon              = TERTIARY  RedguardBayonet' in pz_text and
      'AutoChooseSources   = TERTIARY  NONE' in pz_text, 'bayonet TERTIARY lost')
check('CommandSet    = ChinaInfantryRedguardCommandSet' in pz_text,
      'clone must keep the donor command set')
check('NICNSC_SKN' not in pz_text and 'NICNSC_F_SKN' not in pz_text,
      'vanilla meshes still referenced (reskin incomplete)')
check('NICNSC_SKL' in pz_text and 'NICNSC_F_SKL' in pz_text,
      'vanilla skeletons/anims must stay (the reskin rides them)')

# ================================================ 1b. the two weapons (append)
WEAPONS_APPEND = f'''
;------------------------------------------------------------------------------
; {TAG}: Panzergrenadier weapons.
; Rifle = clone of RedguardMachineGun (18 dmg / 1000 ms / range 110 /
; SMALL_ARMS) with +25% damage (22.5), range 135 and DamageType EXPLOSION:
; the engine has NO "GUN" DamageType (Core .. GameLogic/Damage.h enum), and
; EXPLOSION is unlisted in HumanArmor / HumveeArmor / TankArmor /
; StructureArmor = 100% vs all four (SMALL_ARMS is 100/50/25/50) - the spec's
; "meaningful vehicle damage" without touching any armor table.
; DPS: 22.5 vs infantry (+25% over Red Guard 18) / 22.5 vs Humvee (RG: 9) /
; 22.5 vs Battlemaster (RG: 4.5; a Tank Hunter does 32) / 22.5 vs structures.
; Grenade = area SECONDARY (60 EXPLOSION r15 + 25 r30, clip 1, 8 s reload):
; auto-chosen whenever loaded (60 > 22.5 single-shot estimate), rifle covers
; the reload - sustained ~+4.7 dps and AoE vs clustered infantry/structures.
; Both carry the kwai-doctrine PLAYER_UPGRADE bonus lines (the unit keeps the
; donor's WeaponBonusUpgrade module): +25% damage / +20% range researched.
Weapon Tank_PanzergrenadierRifle
  PrimaryDamage         = 22.5
  PrimaryDamageRadius   = 0.0       ; 0 primary radius means "hits only intended victim"
  AttackRange           = 135.0
  WeaponBonus           = PLAYER_UPGRADE DAMAGE 125% ; zzz-KwaiDoctrine Advanced Infantry Doctrine
  WeaponBonus           = PLAYER_UPGRADE RANGE 120% ; zzz-KwaiDoctrine Advanced Infantry Doctrine
  DamageType            = EXPLOSION
  DeathType             = NORMAL
  WeaponSpeed           = 999999.0          ; dist/sec (huge value == effectively instant)
  ProjectileObject      = NONE
  FireFX                = WeaponFX_GenericMachineGunFire
  VeterancyFireFX       = HEROIC WeaponFX_GenericMachineGunFireWithRedTracers
  FireSound             = RedGuardWeapon
  RadiusDamageAffects   = ALLIES ENEMIES NEUTRALS
  DelayBetweenShots     = 1000               ; time between shots, msec
  ClipSize              = 0                    ; how many shots in a Clip (0 == infinite)
  ClipReloadTime        = 0              ; how long to reload a Clip, msec
End

Weapon Tank_PanzergrenadierGrenade
  PrimaryDamage           = 60.0
  PrimaryDamageRadius     = 15.0
  SecondaryDamage         = 25.0
  SecondaryDamageRadius   = 30.0
  ScatterRadius           = 8.0
  ScatterRadiusVsInfantry = 10.0     ;When this weapon is used against infantry, it can randomly miss by as much as this distance.
  AttackRange             = 135.0
  MinimumAttackRange      = 5.0
  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125% ; zzz-KwaiDoctrine Advanced Infantry Doctrine
  WeaponBonus             = PLAYER_UPGRADE RANGE 120% ; zzz-KwaiDoctrine Advanced Infantry Doctrine
  DamageType              = EXPLOSION
  DeathType               = EXPLODED
  WeaponSpeed             = 150
  ProjectileObject        = InfantryGrenade
  ProjectileDetonationFX  = FX_OICWGrenadeImpact
  ProjectileCollidesWith  = STRUCTURES WALLS
  FireSound               = FireOICWGrenadeBurton
  RadiusDamageAffects     = ALLIES ENEMIES NEUTRALS
  DelayBetweenShots       = 0     ; time between shots, msec
  ClipSize                = 1              ; how many shots in a Clip (0 == infinite)
  ClipReloadTime          = 8000     ; how long to reload a Clip, msec
  AutoReloadsClip         = Yes
  PreAttackDelay          = 500
  PreAttackType           = PER_CLIP ; aim once per grenade
End
'''
check(wpn_src.endswith(b'\n'), 'Weapon.ini must end with a newline to append')
wpn_new = wpn_src + WEAPONS_APPEND.encode('latin-1')
check(wpn_new.startswith(wpn_src), 'Weapon.ini not append-only')
# block balance of the appended chunk
app = WEAPONS_APPEND
starts = len(re.findall(r'^Weapon\s+\S+', app, re.M))
ends = len(re.findall(r'^End\s*$', app, re.M))
check(starts == 2 and ends == 2, f'weapon append block balance {starts}/{ends}')
print('Weapon.ini: +2 weapon blocks appended (append-only verified)')

# ===================================================== 2. CommandButton.ini
cb_text = cb_src.decode('latin-1')
# 2a. append the construct button
CB_APPEND = f'''
; {TAG}: Panzergrenadier construct button (replaces the Red Guard's slot in
; Kwai's Barracks sets; Tank_Command_ConstructChinaInfantryRedguard stays
; defined but unreferenced - hotfix Hacker-Bunker dormancy idiom).
CommandButton Tank_Command_ConstructChinaInfantryPanzergrenadier
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = Tank_ChinaInfantryPanzergrenadier
  TextLabel     = CONTROLBAR:ConstructTankPanzergrenadier
  ButtonImage   = Nuke_RedGuard
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipTankBuildPanzergrenadier
End
'''
# 2b. Kwai-scoped Panzerjaeger relabel of the Tank Hunter construct button
m = get_block(cb_text, 'CommandButton',
              'Tank_Command_ConstructChinaInfantryTankHunter', 'CB')
block = m.group(0)
check(block.count('TextLabel     = CONTROLBAR:ConstructChinaInfantryTankHunter') == 1
      and block.count('DescriptLabel           = CONTROLBAR:ToolTipChinaBuildTankHunter') == 1,
      'TH button labels drifted')
new_block = block.replace(
    '  TextLabel     = CONTROLBAR:ConstructChinaInfantryTankHunter',
    f'  TextLabel     = CONTROLBAR:ConstructTankPanzerjager ; {TAG}: Kwai-scoped Panzerjaeger rename (vanilla labels untouched)'
).replace(
    '  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildTankHunter',
    f'  DescriptLabel           = CONTROLBAR:ToolTipTankBuildPanzerjager ; {TAG}: Kwai-scoped Panzerjaeger rename'
)
check(cb_text.endswith('\n'), 'CommandButton.ini must end with a newline to append')
cb_new_text = cb_text[:m.start()] + new_block + cb_text[m.end():] + CB_APPEND
cb_new = cb_new_text.encode('latin-1')
cb_append_lines = CB_APPEND.split('\n')[:-1]  # drop the '' after the final \n
audit('CommandButton.ini', cb_src, cb_new,
      ['  TextLabel     = CONTROLBAR:ConstructChinaInfantryTankHunter',
       '  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildTankHunter'],
      cb_append_lines + [
       f'  TextLabel     = CONTROLBAR:ConstructTankPanzerjager ; {TAG}: Kwai-scoped Panzerjaeger rename (vanilla labels untouched)',
       f'  DescriptLabel           = CONTROLBAR:ToolTipTankBuildPanzerjager ; {TAG}: Kwai-scoped Panzerjaeger rename'])
# every OTHER Tank Hunter construct button must be byte-identical pre/post
# (the rename is Kwai-scoped: only the Tank_ button block changed)
other_th = [b for b in re.findall(r'^CommandButton\s+(\S+)', cb_text, re.M)
            if 'TankHunter' in b and b != 'Tank_Command_ConstructChinaInfantryTankHunter']
check(other_th, 'expected other generals to have Tank Hunter construct buttons')
for vb in other_th:
    pre = re.search(r'^CommandButton\s+%s\b.*?^End' % re.escape(vb), cb_text, re.M | re.S)
    post = re.search(r'^CommandButton\s+%s\b.*?^End' % re.escape(vb), cb_new_text, re.M | re.S)
    check(pre and post and pre.group(0) == post.group(0),
          f'{vb} changed (rename must be Kwai-scoped)')
print('Kwai-scope guard OK: %d other Tank Hunter buttons byte-identical' % len(other_th))
print('CommandButton.ini: +1 button appended, TH button relabeled (Kwai-scoped)')

# ========================================================= 3. CommandSet.ini
cs_text = cs_src.decode('latin-1')
OLD_SLOT = '1 = Tank_Command_ConstructChinaInfantryRedguard'
NEW_SLOT = (f'  1 = Tank_Command_ConstructChinaInfantryPanzergrenadier '
            f'; {TAG}: replaces Red Guard (stub + button stay defined, unbuildable)')
cs_new, cs_removed, cs_added = edit_lines(cs_src, [('sub', OLD_SLOT, [NEW_SLOT], 2)], 'CS')
audit('CommandSet.ini', cs_src, cs_new, cs_removed, cs_added)
cs_new_text = cs_new.decode('latin-1')

def set_slots(text, name):
    body = get_block(text, 'CommandSet', name, 'CS').group(1)
    return dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', body, re.M))

EXPECT_BARRACKS = {
    '1': 'Tank_Command_ConstructChinaInfantryPanzergrenadier',
    '2': 'Tank_Command_ConstructChinaInfantryTankHunter',
    '3': 'Tank_Command_ConstructChinaInfantryHacker',
    '4': 'Tank_Command_ConstructChinaInfantryBlackLotus',
    '5': 'Tank_Command_ConstructChinaInfantrySiegeSoldier',
    '6': 'Tank_Command_ConstructChinaInfantryFlameThrower',
    '7': 'Tank_Command_ConstructChinaInfantryMiniGunner',
    '8': 'Tank_Command_ConstructChinaInfantrySharpshooter',
    '9': 'Tank_Command_ConstructChinaInfantryShmelTrooper',
    '10': 'Tank_Command_ConstructChinaInfantryShockTrooper',
    '12': 'Command_UpgradeChinaRedguardCaptureBuilding',
    '14': 'Command_Sell',
}
for name, mines in [('Tank_ChinaBarracksCommandSet', 'Command_UpgradeChinaMines'),
                    ('Tank_ChinaBarracksCommandSetUpgrade', 'Command_UpgradeEMPMines')]:
    slots = set_slots(cs_new_text, name)
    want = dict(EXPECT_BARRACKS); want['13'] = mines
    check(slots == want, f'{name} post-edit layout wrong: {slots}')
print('barracks sets post-edit layout OK (both variants; slots 5-10 survive)')

# sibling survival (hotfix's list + this stack's critical hunks)
dz2 = set_slots(cs_new_text, 'Tank_ChinaDozerCommandSet_Down')
check(dz2 == {'1': 'Tank_Command_ConstructChinaIndustrialPlant',
              '7': 'Tank_Command_ConstructChinaBunker',
              '9': 'Tank_Command_ConstructChinaTeslaCoil',
              '13': 'Command_ChinaButtonCommandSetOneUp',
              '14': 'Command_DisarmMinesAtPosition'},
      f'dozer page-2 layout wrong (hotfix hunk lost?): {dz2}')
check('Tank_Command_ConstructChinaHackerBunker' not in cs_new_text,
      'hotfix Hacker Bunker removal regressed')
for name, want in [
    ('Tank_ChinaDozerCommandSet', ['Command_ChinaButtonCommandSetOneDown']),
    ('Tank_ChinaHackerBunkerCommandSet', ['Command_StructureExit', 'Command_Sell']),
    ('Tank_ChinaInternetCenterCommandSetOne', ['Command_Evacuate', 'Command_Sell']),
    ('Tank_ChinaWarFactoryCommandSet_Down',
     ['Tank_Command_ConstructChinaTankOverlord',
      'Tank_Command_ConstructChinaVehicleScoutCar']),
    ('Tank_ChinaCommandCenterCommandSet', ['Tank_Command_KwaiUAVDeploy']),
    ('ChinaInfantryRedguardCommandSet',
     ['Command_ChinaInfantryRedGuardCaptureBuilding', 'Command_RedGuardTaunt',
      'Command_RedGuardBayonetAttack', 'Command_AttackMove']),
]:
    body = get_block(cs_new_text, 'CommandSet', name, 'CS').group(1)
    for wtn in want:
        check(wtn in body, f'sibling survival: {name} lost {wtn}')
print('CommandSet survival OK (dozer pages, bunker/IC/WF/CC sets, RG unit set)')

# ======================================================= 4. Generals.str
STR_APPEND = ('\n'
 'OBJECT:TankPanzergrenadier\n'
 '"Panzergrenadier"\n'
 'END\n'
 '\n'
 'CONTROLBAR:ConstructTankPanzergrenadier\n'
 '"&Panzergrenadier"\n'
 'END\n'
 '\n'
 'CONTROLBAR:ToolTipTankBuildPanzergrenadier\n'
 '"Elite assault infantry with an HE rifle and an under-barrel grenade launcher.\\n'
 ' Long-ranged rifle damages vehicles and structures; grenades blast grouped infantry.\\n'
 ' Can capture buildings.\\n\\n'
 ' Strong vs. infantry, light vehicles \\n Weak vs. aircraft"\n'
 'END\n'
 '\n'
 'OBJECT:TankPanzerjager\n'
 '"Panzerj\xe4ger"\n'
 'END\n'
 '\n'
 'CONTROLBAR:ConstructTankPanzerjager\n'
 '"Panzer&j\xe4ger"\n'
 'END\n'
 '\n'
 'CONTROLBAR:ToolTipTankBuildPanzerjager\n'
 '"Anti-tank infantry armed with a guided missile launcher.\\n'
 ' Can attack aircraft.\\n\\n'
 ' Strong vs. vehicles, aircraft \\n Weak vs. infantry"\n'
 'END\n')
check(str_src.endswith(b'\n'), 'Generals.str must end with a newline to append')
str_new = str_src + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src), 'Generals.str not append-only')
check(str_new.decode('latin-1').count('\nEND\n') ==
      str_src.decode('latin-1').count('\nEND\n') + 6, 'str append entry count')
print('Generals.str: +6 entries appended (Panzerjäger as latin-1 0xE4 - '
      'GameTextManager::translateCopy widens bytes 1:1 to widechars)')

# ================================== 5. TankHunter.ini stub (DisplayName only)
TH_DN = (f'  DisplayName            = OBJECT:TankPanzerjager '
         f'; {TAG}: Kwai-scoped rename (spawned vanilla unit keeps OBJECT:TankHunter when selected)')
th_new, th_removed, th_added = edit_lines(
    th_src, [('after', 'ButtonImage            = SNTankHunter', [TH_DN], 1)], 'TH')
audit('TankHunter.ini', th_src, th_new, th_removed, th_added)
th_text = th_new.decode('latin-1')
check(re.search(r'BuildVariations\s*=\s*ChinaInfantryTankHunter\b', th_text),
      'TH stub BuildVariations lost')
check('BuildCost             = 185' in th_text and 'BuildTime             = 5.0' in th_text,
      'TH stub w-economy pricing hunk lost')

# ====================================================== global closure checks
cb_final = cb_new.decode('latin-1')
def button_defined(btn):
    return re.search(r'^CommandButton\s+%s\b' % re.escape(btn), cb_final, re.M)

# every slot of every set we touched resolves; every set referenced by our unit
for name in ['Tank_ChinaBarracksCommandSet', 'Tank_ChinaBarracksCommandSetUpgrade']:
    for btn in set_slots(cs_new_text, name).values():
        check(button_defined(btn), f'dangling button ref {btn} in {name}')
# dormant Red Guard machinery still defined, zero live references
check(button_defined('Tank_Command_ConstructChinaInfantryRedguard'),
      'dormant Red Guard construct button definition vanished')
check('Tank_Command_ConstructChinaInfantryRedguard' not in cs_new_text,
      'Red Guard construct button still referenced in CommandSet.ini')
rgt_text = eff[P_RGT.lower()][1].decode('latin-1')
check(re.search(r'^Object\s+Tank_ChinaInfantryRedguard\b', rgt_text, re.M),
      'dormant Tank_ChinaInfantryRedguard stub object vanished')
# our new button's references resolve
newb = get_block(cb_final, 'CommandButton',
                 'Tank_Command_ConstructChinaInfantryPanzergrenadier', 'CB').group(1)
check('Object        = Tank_ChinaInfantryPanzergrenadier' in newb, 'button object ref')
# our new labels all present in the shipped str
str_final = str_new.decode('latin-1')
for lab in NEW_LABELS:
    check(re.search(r'^%s$' % re.escape(lab), str_final, re.M),
          f'label {lab} missing from shipped Generals.str')
# weapons referenced by the clone are defined in the shipped Weapon.ini
wpn_final = wpn_new.decode('latin-1')
for wname in ['Tank_PanzergrenadierRifle', 'Tank_PanzergrenadierGrenade',
              'RedguardBayonet']:
    check(re.search(r'^Weapon\s+%s\b' % wname, wpn_final, re.M),
          f'weapon {wname} not defined in shipped Weapon.ini')
# rotr / tesla appends still present in the shipped Weapon.ini (append-only anyway)
for wname in ['ShockTrooperTeslaWeapon', 'RussiaShmellTrooperMissileLauncher']:
    check(re.search(r'^Weapon\s+%s\b' % wname, wpn_final, re.M),
          f'sibling weapon {wname} lost from Weapon.ini')
# w-economy parity: our baked numbers are exactly half the spec sticker
check(225 * 2 == 450 and 6.0 * 2 == 12.0, 'halving arithmetic')
print('closure OK (buttons, labels, weapons, dormant RG machinery intact)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_CS, cs_new),
           bigfile.BigEntry(P_CB, cb_new),
           bigfile.BigEntry(P_STR, str_new),
           bigfile.BigEntry(P_WPN, wpn_new),
           bigfile.BigEntry(P_PZ, pz_new),
           bigfile.BigEntry(P_TH, th_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries],
      'BIG round-trip mismatch')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
open(out_path, 'wb').write(blob)
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} files)'
      + (' [hash-idempotent]' if prev == blob else ''))

# ------------------------------------------------------------------ install
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    shutil.copyfile(out_path, dst)
    check(open(dst, 'rb').read() == blob, f'install verify failed: {dst}')
    print('installed + re-read OK:', dst)

# ------------------------------------------------- post-install effective audit
want_bytes = {P_CS.lower(): cs_new, P_CB.lower(): cb_new, P_STR.lower(): str_new,
              P_WPN.lower(): wpn_new, P_PZ.lower(): pz_new, P_TH.lower(): th_new}
for d in MODDIRS:
    posteff = {}
    for b in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b)):
            posteff[e.path.lower()] = (b, e.data)
    for p, data in want_bytes.items():
        check(posteff[p][0] == ARCHIVE, f'{d}: {p} effective owner is {posteff[p][0]}')
        check(posteff[p][1] == data, f'{d}: {p} installed bytes differ')
    # untouched neighbours keep their owners
    check(posteff[P_RGV.lower()][0] == 'zzz-ZZZZZZZWEconomy.big',
          f'{d}: vanilla Redguard.ini owner drifted post-install')
    check(posteff[P_RGT.lower()][0] == 'zzz-ZZZZZZZWEconomy.big',
          f'{d}: RG stub owner drifted post-install')
print('post-install effective-space audit OK in both dirs')
print('ALL CHECKS PASSED')
