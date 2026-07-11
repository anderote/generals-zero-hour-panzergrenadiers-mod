#!/usr/bin/env python3
"""zzz-ZZZZZZZZZZZZZZZ0EmperorInnatePDL.big -- Emperor Innate Point-Defense Laser
(ShockWave / GeneralsX / macOS), for Kwai (China Tank General).

ONE always-on, INNATE (no upgrade, no pod, no contain slot) proactive
Point-Defense Laser added directly to Kwai's Emperor Overlord tank
(Tank_ChinaTankEmperor) -- exactly how USA's Avenger carries
PointDefenseLaserUpdate as a plain vehicle module.

WHY: the Emperor's research-gated PDL (emperor-defense-suite) is REACTIVE
(FireWeaponWhenDamagedBehavior, fires only when hit) because gating a PROACTIVE
PointDefenseLaserUpdate required an invisible rider-pod and the Emperor's
HelixContain rider slot is contested by the gattling cannon. The user wants the
Emperor to simply START with a proactive PDL. A proactive PDL that is always-on
from spawn needs no gate, so it drops straight onto the hull as a plain Behavior
module -- no pod, no contain slot, no upgrade. Pure data, NO engine change.

REFERENCE PATTERNS (both live in the effective stack, verified by this build):
  * Direct-module idiom: Lazr_AmericaTankAvenger (effective !Shw_ini stack,
    USA/Laser/Vehicles/Avenger.ini) carries Behavior = PointDefenseLaserUpdate
    DIRECTLY on the vehicle (ModuleTag_Laser_One/Two): WeaponTemplate,
    PrimaryTargetTypes = BALLISTIC_MISSILE SMALL_MISSILE, ScanRate=0,
    ScanRange=200, PredictTargetVelocityFactor=1.0. No pod.
  * Weapon reuse: the effective PDLPod.ini (owned by zzz-ZZZZZZZXHotfix) uses
    WeaponTemplate = Tank_KwaiPDLLaserWeapon with the same target types and
    ScanRange = 160.0. We REUSE Tank_KwaiPDLLaserWeapon (AttackRange 100.0,
    LASER, AntiSmallMissile/AntiProjectile, FireFX WeaponFX_AvengerPointDefense-
    Laser) so FX/sound match the rest of Kwai's PDLs. ScanRange 160.0 safely
    exceeds the weapon's 100.0 AttackRange (PointDefenseLaserUpdate engine
    assert requires ScanRange > weapon range).

Sorts ABOVE every data layer (15 Z's + '0'; the current Emperor.ini owner to
beat is 12-Z emperor-defense-suite, with TeslaFinish 13-Z and ShellKwai 14-Z
above it but neither claims Emperor.ini) and BELOW zzz_ControlBarPro*/zzzz_
FXEnhance. Re-ships ONLY the Emperor object file -- nothing else is clobbered.
Reads effective sources from ~/GeneralsX/mods/ShockWaveSPE. Depends on
../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys, hashlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZZZZZ0EmperorInnatePDL.big'   # 15 Z's + '0'
TAG = 'emperor-innate-pdl'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'
# effective winning owner of the Emperor object (12-Z defense-suite layer)
EMP_OWNER = 'zzz-ZZZZZZZZZZZZ0EmperorDefense.big'.lower()
WEAPON = 'Tank_KwaiPDLLaserWeapon'
NEW_MODTAG = 'ModuleTag_EmperorInnatePDL'
SCAN_RANGE = 160.0

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
    for need in ['zzz-ZZZZZZZZZZZZ0EmperorDefense.big', 'zzz-ZZZZZZZZZZZZZ0TeslaFinish.big',
                 'zzz-ZZZZZZZZZZZZZZ0ShellKwai.big']:
        check(need in below, f'{d}: {need} must sort below us (got above/absent)')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (above all data layers incl. EmperorDefense/TeslaFinish/ShellKwai, below ControlBarPro*/FXEnhance)')

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
check(P_EMP.lower() in eff, f'missing effective {P_EMP}')
check(eff[P_EMP.lower()][0].lower() == EMP_OWNER,
      f'Emperor effective owner drifted: {eff[P_EMP.lower()][0]} (expected {EMP_OWNER})')
print(f'effective ownership OK: Emperor.ini owned by {eff[P_EMP.lower()][0]}')

# no higher-sorting archive claims the file we re-ship
for d in MODDIRS:
    for b in sorted_bigs(d):
        if str.lower(b) <= ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        check(P_EMP.lower() not in claimed, f'{d}/{b} (sorts above us) claims {P_EMP}')
print('no higher-sorting archive claims the Emperor object file')

# ------------------------------------------------------------ closure: weapon
all_ini = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                    if p.endswith('.ini'))
wm = re.search(r'^Weapon\s+%s\b(.*?)^End' % re.escape(WEAPON), all_ini, re.M | re.S)
check(wm, f'reused weapon {WEAPON} not defined in effective stack')
wtxt = wm.group(1)
arm = re.search(r'^\s*AttackRange\s*=\s*([\d.]+)', wtxt, re.M)
check(arm, f'{WEAPON}: no AttackRange found')
attack_range = float(arm.group(1))
# PointDefenseLaserUpdate engine assert: ScanRange must exceed the weapon's range
check(SCAN_RANGE > attack_range,
      f'ScanRange {SCAN_RANGE} must exceed weapon AttackRange {attack_range} (engine assert)')
print(f'weapon closure OK: {WEAPON} AttackRange={attack_range} < ScanRange={SCAN_RANGE} (assert-safe)')
# FireFX / LaserName resolve (already proven working by the effective PDLPod, re-verified)
firefx = re.search(r'^\s*FireFX\s*=\s*(\S+)', wtxt, re.M)
check(firefx and re.search(r'^FXList\s+%s\b' % re.escape(firefx.group(1)), all_ini, re.M),
      'weapon FireFX FXList does not resolve')
laser = re.search(r'^\s*LaserName\s*=\s*(\S+)', wtxt, re.M)
check(laser is None or laser.group(1) in all_ini, 'weapon LaserName token does not resolve')
# direct-module reference pattern present (Avenger carries PDL directly on the vehicle)
check(re.search(r'^\s*Behavior\s*=\s*PointDefenseLaserUpdate\b', all_ini, re.M),
      'reference PointDefenseLaserUpdate direct-module idiom missing from effective stack')
print(f'FX/laser closure OK (FireFX={firefx.group(1)}); Avenger direct-module idiom present')

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

# ===================================================== Emperor.ini: +1 module
NEW_MODULE = [
    f'  ; ------------------------------------------------------------------------------',
    f'  ; {TAG}: INNATE always-on proactive Point-Defense Laser (ADDED; every prior',
    f'  ; module -- crew, HelixContain bay, Shtora APS, propaganda, gattling/PDL riders,',
    f'  ; doctrine armour, defense-suite EDS_* -- preserved). Direct vehicle module, the',
    f'  ; Avenger idiom: no upgrade gate, no rider pod, no contain slot. Reuses Kwai\'s',
    f'  ; PDL weapon so FX/sound match the rest of Kwai\'s point-defense lasers.',
    f'  Behavior = PointDefenseLaserUpdate {NEW_MODTAG} ; {TAG}: always-on from spawn',
    f'    WeaponTemplate              = {WEAPON}',
    f'    PrimaryTargetTypes          = BALLISTIC_MISSILE SMALL_MISSILE',
    f'    ScanRate                    = 0',
    f'    ScanRange                   = {SCAN_RANGE:.1f} ; > weapon AttackRange {attack_range:.0f} (PointDefenseLaserUpdate engine assert); matches PDLPod',
    f'    PredictTargetVelocityFactor = 1.0',
    f'  End',
]

emp_src = eff[P_EMP.lower()][1]
emp_text = emp_src.decode('latin-1')

# every prior-layer module hunk that MUST survive byte-for-byte
EMP_SURVIVE = [
    'Object Tank_ChinaTankEmperor',
    'MaxHealth       = 1320.0',
    'Behavior = MaxHealthUpgrade ModuleTag_KD_Armor1',
    'Behavior = MaxHealthUpgrade ModuleTag_KD_Armor2',
    'Behavior = MaxHealthUpgrade ModuleTag_KD_Armor3',
    'Behavior = MaxHealthUpgrade ModuleTag_KD_Armor4',
    'Behavior = WeaponBonusUpgrade ModuleTag_KD_Tungsten01',
    'Behavior = VeterancyGainCreate ModuleTag_23',
    'Behavior = HelixContain ModuleTag_06',
    'Slots                   = 8',
    'Behavior = ObjectCreationUpgrade ModuleTag_07',
    'Behavior        = PropagandaTowerBehavior ModulePropaganda_15',
    'Behavior = FireWeaponWhenDamagedBehavior ModuleTag_ShtoraAuto01',
    'ModuleTag_Shtora01', 'ModuleTag_Shtora02', 'ModuleTag_Shtora03',
    'Behavior = ObjectCreationUpgrade ModuleTag_KPDL_Mount01',
    'Behavior = CommandSetUpgrade ModuleTag_KPDL_CmdSet01',
    'Behavior = CommandSetUpgrade ModuleTag_KPDL_CmdSet02',
    'Behavior = ObjectCreationUpgrade ModuleTag_GP_Crew01',
    'Behavior = ObjectCreationUpgrade ModuleTag_GP_Crew03',
    'Behavior = FireWeaponWhenDamagedBehavior ModuleTag_EDS_PDL01',
    'Behavior = FireWeaponWhenDamagedBehavior ModuleTag_EDS_ABM01',
    'Behavior = MaxHealthUpgrade ModuleTag_EDS_Shield01',
    'Behavior = AutoHealBehavior ModuleTag_EDS_Shield02',
    'Behavior = PropagandaTowerBehavior ModuleTag_EDS_Fleet01',
    'Behavior = ObjectCreationUpgrade ModuleTag_Taunt02',
]
for n in EMP_SURVIVE:
    check(n in emp_text, f'Emperor prior-layer hunk missing before edit: {n!r}')
check(NEW_MODTAG not in emp_text, f'Emperor already has {NEW_MODTAG}')
# the Emperor object itself must not yet carry a direct PointDefenseLaserUpdate
check(not re.search(r'^\s*Behavior\s*=\s*PointDefenseLaserUpdate\b', emp_text, re.M),
      'Emperor object already carries a direct PointDefenseLaserUpdate module')

# insert before the single Geometry = BOX anchor
geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', emp_text, re.M))
check(len(geo) == 1, f'Emperor: need exactly one Geometry=BOX anchor (found {len(geo)})')
ins = geo[0].start()
emp_new_text = emp_text[:ins] + '\n'.join(NEW_MODULE) + '\n' + emp_text[ins:]
emp_new = emp_new_text.encode('latin-1')

# byte-for-byte survival of everything else: removed=[], added = exactly our block
audit('Emperor.ini (+1 innate PDL module)', emp_src, emp_new, [], NEW_MODULE)
for n in EMP_SURVIVE:
    check(n in emp_new_text, f'Emperor prior-layer hunk lost after edit: {n!r}')
# exactly one new PointDefenseLaserUpdate; prior reactive/gattling/etc counts unchanged
check(len(re.findall(r'Behavior\s*=\s*PointDefenseLaserUpdate\b', emp_new_text)) == 1,
      'expected exactly 1 PointDefenseLaserUpdate on the Emperor')
check(emp_new_text.count(NEW_MODTAG) == 1, f'{NEW_MODTAG} must appear exactly once')
check(len(re.findall(r'Behavior\s*=\s*FireWeaponWhenDamagedBehavior\b', emp_new_text)) == 3,
      'reactive FireWeaponWhenDamagedBehavior count changed (Shtora + EDS_PDL + EDS_ABM = 3)')
check(len(re.findall(r'Behavior\s*=\s*PropagandaTowerBehavior\b', emp_new_text)) == 2,
      'PropagandaTowerBehavior count changed (innate tower + fleet aura = 2)')
check(emp_new_text.count('Behavior = ObjectCreationUpgrade ModuleTag_KPDL_Mount01') == 1,
      'existing purchasable KwaiPDL pod wiring must survive untouched')
print('Emperor.ini: 1 innate PDL module inserted; full prior module list survives byte-for-byte')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_EMP, emp_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries], 'BIG round-trip mismatch')
print('BIG round-trip byte-identity OK (1 file)')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
open(out_path, 'wb').write(blob)
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} file)' + (' [hash-idempotent]' if prev == blob else ''))

# ------------------------------------------------------- install + post-audit
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
    check(posteff[P_EMP.lower()][0] == ARCHIVE, f'{d}: Emperor effective owner is {posteff[P_EMP.lower()][0]} not us')
    check(posteff[P_EMP.lower()][1] == emp_new, f'{d}: installed Emperor bytes differ')
    e_emp = posteff[P_EMP.lower()][1].decode('latin-1')
    for n in EMP_SURVIVE + [NEW_MODTAG, f'WeaponTemplate              = {WEAPON}']:
        check(n in e_emp, f'{d}: installed Emperor missing {n!r}')
    check(len(re.findall(r'Behavior\s*=\s*PointDefenseLaserUpdate\b', e_emp)) == 1,
          f'{d}: installed Emperor PDL count wrong')
    # the reused weapon still resolves in the post-install effective stack
    posteff_ini = '\n'.join(v[1].decode('latin-1') for k, v in posteff.items() if k.endswith('.ini'))
    check(re.search(r'^Weapon\s+%s\b' % re.escape(WEAPON), posteff_ini, re.M),
          f'{d}: reused weapon {WEAPON} does not resolve post-install')
    print('installed + post-install effective audit OK:', dst)
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (Emperor Innate PDL)')
