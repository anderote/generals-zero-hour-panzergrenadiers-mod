#!/usr/bin/env python3
"""zzz-ZZZZZZZXHotfix.big — Panzergrenadiers stack hot-fix layer (3 items).

1. Kwai Internet Center (Tank_ChinaInternetCenter): InternetHackContain
   Slots 30 -> 60, + InitialPayload = ChinaInfantryHacker 10 (TroopCrawler
   idiom; the concrete vanilla object the Tank_ stub's BuildVariations
   redirects to).
2. PDL pod (Tank_ChinaPDLPod): PointDefenseLaserUpdate PrimaryTargetTypes
   SMALL_MISSILE -> BALLISTIC_MISSILE SMALL_MISSILE (Avenger parity;
   Tomahawks/SCUD-class now intercepted).
3. Kwai dozer page 2 (Tank_ChinaDozerCommandSet_Down): slot-8 Hacker
   Bunker build button removed (object/button/strings stay dormant).

Reads effective sources from ~/GeneralsX/mods/ShockWaveSPE (excluding its
own archive AND every archive sorting above it: this layer must never
source from zzz_ControlBarPro*/zzzz_FXEnhance, which belong to other
sessions/purposes), patches, verifies loudly, writes the archive here and
installs to both mod dirs. Depends on ../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZXHotfix.big'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

P_CS  = 'Data\\INI\\CommandSet.ini'
P_IC  = 'Data\\INI\\Object\\China\\Tank\\Buildings\\InternetCenter.ini'
P_POD = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\PDLPod.ini'

EXPECT_OWNER = {
    P_CS.lower():  'zzz-zzzzzzzweconomy.big',
    P_IC.lower():  'zzz-zzzzzzzweconomy.big',
    P_POD.lower(): 'zzz-zzzzzzzkwaipdl.big',
}

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
    check('zzz-ZZZZZZZWEconomy.big' in below, f'{d}: WEconomy must sort below us')
    check('zzz-ZZZZZZZVetInsignia.big' in below, f'{d}: VetInsignia must sort below us')
    check('zzz-ZZZZZZZKwaiPDL.big' in below, f'{d}: KwaiPDL must sort below us')
    for a in list(above):
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzzz_fxenhance') for a in above) or
          not any(n.lower().startswith('zzzz_fxenhance') for n in names),
          f'{d}: FXEnhance must sort above us')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above) or
          not any(n.lower().startswith('zzz_controlbarpro') for n in names),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (after WEconomy, below ControlBarPro*/FXEnhance)')

# ------------------------------------------------- effective space (primary)
# Sources are read ONLY from archives sorting strictly below this one.
def load_effective(moddir):
    eff = {}          # lowpath -> (owner, bytes)
    order = sorted_bigs(moddir)
    for b in order:
        if b.lower() == ARCHIVE.lower():
            continue
        if str.lower(b) > ARCHIVE.lower():
            continue  # never source from layers above us (other sessions)
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
        for p in EXPECT_OWNER:
            check(p not in claimed, f'{d}/{b} (sorts above us) claims {p}')
print('no higher-sorting archive claims any shipped path')

# --------------------------------------------------------------- line editing
def edit_lines(data, plan, label):
    """plan: list of (old_line_content, [new_line_contents]) — content sans EOL.
    Each old line must occur exactly once. Returns new bytes + audit."""
    lines = data.decode('latin-1').splitlines(keepends=True)
    bare = [l.rstrip('\r\n') for l in lines]
    out = list(lines)
    removed, added = [], []
    for old, news in plan:
        idxs = [i for i, l in enumerate(bare) if l == old]
        check(len(idxs) == 1, f'{label}: line not unique ({len(idxs)}x): {old!r}')
        i = idxs[0]
        eol = lines[i][len(lines[i].rstrip("\r\n")):] or '\n'
        j = out.index(lines[i]) if lines.count(lines[i]) == 1 else None
        # positions may shift after edits; recompute against current 'out'
        cur_bare = [l.rstrip('\r\n') for l in out]
        k = cur_bare.index(old)
        out[k:k+1] = [n + eol for n in news]
        removed.append(old)
        added.extend(news)
    return ''.join(out).encode('latin-1'), removed, added

def audit(label, old, new, exp_removed, exp_added):
    o = [l.rstrip('\r\n') for l in old.decode('latin-1').splitlines()]
    n = [l.rstrip('\r\n') for l in new.decode('latin-1').splitlines()]
    from collections import Counter
    co, cn = Counter(o), Counter(n)
    removed = list((co - cn).elements())
    added = list((cn - co).elements())
    check(sorted(removed) == sorted(exp_removed),
          f'{label}: removed-line audit mismatch:\n got {removed}\n exp {exp_removed}')
    check(sorted(added) == sorted(exp_added),
          f'{label}: added-line audit mismatch:\n got {added}\n exp {exp_added}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')

# ------------------------------------------------------------ 1. Internet Center
TAG = 'zzz-ZZZZZZZXHotfix'
ic_owner, ic_src = eff[P_IC.lower()]
check(ic_src.decode('latin-1').count('Behavior = InternetHackContain') == 1,
      'IC: expected exactly one InternetHackContain')
check(re.findall(r'^Object\s+(\S+)', ic_src.decode('latin-1'), re.M) ==
      ['Tank_ChinaInternetCenter'], 'IC: unexpected object list')

OLD_SLOTS = '    Slots                 = 30'
NEW_SLOTS = f'    Slots                 = 60 ; {TAG}: was 30'
NEW_PAYLOAD = (f'    InitialPayload        = ChinaInfantryHacker 10 '
               f'; {TAG}: pre-garrisoned hackers (TroopCrawler idiom)')
ic_new, _, _ = edit_lines(ic_src, [(OLD_SLOTS, [NEW_SLOTS, NEW_PAYLOAD])], 'IC')
audit('InternetCenter.ini', ic_src, ic_new, [OLD_SLOTS], [NEW_SLOTS, NEW_PAYLOAD])

# InitialPayload semantic guards
vh = eff['data\\ini\\object\\china\\vanilla\\infantry\\hacker.ini'][1].decode('latin-1')
check(re.search(r'^Object\s+ChinaInfantryHacker\b', vh, re.M),
      'payload object ChinaInfantryHacker missing')
m = re.search(r'^\s*KindOf\s*=\s*([^\n;]+)', vh, re.M)
check(m and 'MONEY_HACKER' in m.group(1).split() and 'INFANTRY' in m.group(1).split(),
      'payload must be MONEY_HACKER INFANTRY (contain allow-mask / slot checks)')
m = re.search(r'TransportSlotCount\s*=\s*(\d+)', vh)
check(m and int(m.group(1)) * 10 <= 60, 'payload slot budget exceeded')
# TroopCrawler donor idiom drift guard
tc = eff['data\\ini\\object\\china\\vanilla\\vehicles\\troopcrawler.ini'][1].decode('latin-1')
check(re.search(r'InitialPayload\s*=\s*ChinaInfantryRedguard\s+8', tc),
      'TroopCrawler InitialPayload donor idiom drifted')
# the Kwai stub must still redirect to the payload object (economy/roster invariant)
th = eff['data\\ini\\object\\china\\tank\\infantry\\hacker.ini'][1].decode('latin-1')
check(re.search(r'BuildVariations\s*=\s*ChinaInfantryHacker\b', th),
      'Tank_ChinaInfantryHacker stub no longer redirects to ChinaInfantryHacker')
print('InitialPayload closure OK (payload object, KindOf, slot budget, donor idiom)')

# ------------------------------------------------------------------ 2. PDL pod
pod_owner, pod_src = eff[P_POD.lower()]
OLD_TT = '    PrimaryTargetTypes    = SMALL_MISSILE'
NEW_TT = ('    PrimaryTargetTypes    = BALLISTIC_MISSILE SMALL_MISSILE '
          f'; {TAG}: Avenger parity (Tomahawks/SCUD-class now intercepted)')
OLD_C1 = ';;;   - PrimaryTargetTypes = SMALL_MISSILE per spec (Avenger also lists'
OLD_C2 = ';;;     BALLISTIC_MISSILE; SCUD-class interception is deliberately out)'
NEW_C1 = ';;;   - PrimaryTargetTypes = BALLISTIC_MISSILE SMALL_MISSILE'
NEW_C2 = f';;;     ({TAG}: restored Avenger parity; was SMALL_MISSILE only)'
pod_new, _, _ = edit_lines(pod_src, [(OLD_TT, [NEW_TT]),
                                     (OLD_C1, [NEW_C1]), (OLD_C2, [NEW_C2])], 'POD')
audit('PDLPod.ini', pod_src, pod_new, [OLD_TT, OLD_C1, OLD_C2], [NEW_TT, NEW_C1, NEW_C2])

# Avenger-parity drift guard: the Avengers still list exactly these types
av = eff['data\\ini\\object\\usa\\vanilla\\vehicles\\avenger.ini'][1].decode('latin-1')
check(re.search(r'PrimaryTargetTypes\s*=\s*BALLISTIC_MISSILE SMALL_MISSILE', av),
      'Avenger PDL target types drifted')
# Tomahawk missiles must be BALLISTIC_MISSILE (the point of the fix)
wo = eff['data\\ini\\object\\weaponobjects.ini'][1].decode('latin-1')
check(re.search(r'Object\s+TomahawkMissile\b', wo) and
      re.search(r'KindOf\s*=\s*PROJECTILE BALLISTIC_MISSILE', wo),
      'TomahawkMissile BALLISTIC_MISSILE KindOf drifted')
# untouched pod fields survive
for needle in ['ScanRange             = 160.0',
               'WeaponTemplate        = Tank_KwaiPDLLaserWeapon',
               'PredictTargetVelocityFactor = 1.0']:
    check(needle in pod_new.decode('latin-1'), f'POD: sibling field lost: {needle}')
print('PDL parity + drift guards OK')

# --------------------------------------------------------------- 3. CommandSet
cs_owner, cs_src = eff[P_CS.lower()]
OLD_BTN = '  8  = Tank_Command_ConstructChinaHackerBunker'
NEW_NOTE = (f'  ; {TAG}: slot-8 Hacker Bunker build button removed '
            '(object/button/strings stay dormant)')
cs_new, _, _ = edit_lines(cs_src, [(OLD_BTN, [NEW_NOTE])], 'CS')
audit('CommandSet.ini', cs_src, cs_new, [OLD_BTN], [NEW_NOTE])

cs_text = cs_new.decode('latin-1')
def get_set(text, name):
    m = re.search(r'^CommandSet %s\n(.*?)^End$' % re.escape(name), text, re.M | re.S)
    check(m, f'CommandSet {name} missing')
    return m.group(1)

# post-edit dozer page-2 exact layout
pg2 = get_set(cs_text, 'Tank_ChinaDozerCommandSet_Down')
slots = dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)', pg2, re.M))
check(slots == {'1': 'Tank_Command_ConstructChinaIndustrialPlant',
                '7': 'Tank_Command_ConstructChinaBunker',
                '9': 'Tank_Command_ConstructChinaTeslaCoil',
                '13': 'Command_ChinaButtonCommandSetOneUp',
                '14': 'Command_DisarmMinesAtPosition'},
      f'dozer page-2 layout wrong: {slots}')
check('Tank_Command_ConstructChinaHackerBunker' not in cs_text,
      'Hacker Bunker button still referenced somewhere in CommandSet.ini')

# sibling survival: every earlier layer's set hunks (spot the critical ones,
# byte-level identity of everything else is enforced by the diff audit above)
for name, want in [
    ('Tank_ChinaBarracksCommandSet',
     ['Tank_Command_ConstructChinaInfantryShmelTrooper',
      'Tank_Command_ConstructChinaInfantryShockTrooper',
      'Tank_Command_ConstructChinaInfantrySharpshooter']),
    ('Tank_ChinaBarracksCommandSetUpgrade',
     ['Tank_Command_ConstructChinaInfantryShmelTrooper',
      'Tank_Command_ConstructChinaInfantryShockTrooper']),
    ('Tank_ChinaDozerCommandSet', ['Command_ChinaButtonCommandSetOneDown']),
    ('Tank_ChinaHackerBunkerCommandSet', ['Command_StructureExit', 'Command_Sell']),
    ('Tank_ChinaInternetCenterCommandSetOne', ['Command_Evacuate', 'Command_Sell']),
]:
    body = get_set(cs_text, name)
    for w in want:
        check(w in body, f'sibling survival: {name} lost {w}')
print('CommandSet survival OK (barracks rotr 9/10, dozer pages, bunker/IC sets)')

# closure: every slot of the edited set resolves; dormant defs still exist
cb_text = eff['data\\ini\\commandbutton.ini'][1].decode('latin-1')
for btn in slots.values():
    check(re.search(r'^CommandButton\s+%s\b' % re.escape(btn), cb_text, re.M),
          f'dangling button ref {btn}')
check(re.search(r'^CommandButton\s+Tank_Command_ConstructChinaHackerBunker\b',
                cb_text, re.M), 'dormant Hacker Bunker button definition vanished')
hb = eff.get('data\\ini\\object\\china\\tank\\defences\\hackerbunker.ini')
check(hb and re.search(r'^Object\s+Tank_ChinaHackerBunker\b',
                       hb[1].decode('latin-1'), re.M),
      'dormant Tank_ChinaHackerBunker object definition vanished')
print('closure OK (page-2 buttons resolve; dormant defs intact)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_CS, cs_new),
           bigfile.BigEntry(P_IC, ic_new),
           bigfile.BigEntry(P_POD, pod_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([ (e.path, e.data) for e in rt ] == [ (e.path, e.data) for e in entries ],
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
for d in MODDIRS:
    posteff = {}
    for b in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b)):
            posteff[e.path.lower()] = (b, e.data)
    for p, data in [(P_CS.lower(), cs_new), (P_IC.lower(), ic_new),
                    (P_POD.lower(), pod_new)]:
        check(posteff[p][0] == ARCHIVE, f'{d}: {p} effective owner is {posteff[p][0]}')
        check(posteff[p][1] == data, f'{d}: {p} installed bytes differ')
print('post-install effective-space audit OK in both dirs')
print('ALL CHECKS PASSED')
