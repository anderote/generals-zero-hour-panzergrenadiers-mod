#!/usr/bin/env python3
"""flagship-emperor -- Emperor flagship rework + gattling turret buff.

Layer archive: zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big (20 Z's: sorts above
Rebalance (18Z), TankUpgrades (19Z'1'), TeslaHP (19Z'0'); below
zzz_ControlBarPro* / zzzz_FXEnhance).

Changes (all against the effective copies owned by Rebalance):

Emperor.ini (Tank_ChinaTankEmperor):
  1. BuildCost 2400 -> 19200 (8x flagship pricing).
  2. Main cannon repoint: PRIMARY Tank_OverlordTankGun_Dummy ->
     Tank_EmperorTankGun_Dummy, SECONDARY Tank_OverlordTankGun ->
     Tank_EmperorTankGun (both weapon-set variants). The Overlord shares
     Tank_OverlordTankGun, so the range buff must live on Emperor-only clones.
  3. EDS ABM interceptor array (ModuleTag_EDS_ABM01) baked always-on:
     StartsActive No->Yes, TriggeredBy Tank_Upgrade_EmperorABM removed
     (emperor-tweaks bake_active idiom). The purchase button becomes a no-op
     money sink; commandset surgery deliberately out of scope for this layer.
  4. InterceptBallistics = Yes on every PointDefenseLaserUpdate module
     (innate PDL + EDS hull PDL): Emperor lasers also shoot down artillery
     shells / nuke cannon shells. REQUIRES the fork engine with the
     InterceptBallistics module-data key -- older binaries fail INI parse.

Weapon.ini:
  5. Gattling turret (building) damage x1.2: Primary+Secondary damage of the
     6 Tank_[Advanced]GattlingBuildingGun* weapons (20->24, 8->9.6, 5.5->6.6).
  6. Appended Emperor-only cannon clones Tank_EmperorTankGun{,_Dummy}:
     byte-clones of the Overlord guns with AttackRange 175 -> 240.

Usage: python3 build.py [--stage]   (--stage: write layer .big only, no install)
"""
import os, re, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'
P_WEAP = 'Data\\INI\\Weapon.ini'
OWNER = 'zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big'
TAG = 'flagship-emperor'

NEW_COST = '19200'
OLD_COST = '2400'
CANNON_RANGE_OLD, CANNON_RANGE_NEW = '175', '240'
GATT_SCALE = 1.2
GATT_WEAPONS = ['Tank_GattlingBuildingGun', 'Tank_GattlingBuildingGunAir',
                'Tank_GattlingBuildingGunAntiArmor', 'Tank_AdvancedGattlingBuildingGun',
                'Tank_AdvancedGattlingBuildingGunAir', 'Tank_AdvancedGattlingBuildingGunAntiArmor']
INTERCEPT_KEY = 'InterceptBallistics'
P_PGREN = 'Data\\INI\\Object\\China\\Tank\\Infantry\\Panzergrenadier.ini'
PG_WEAPONS = ['Tank_PanzergrenadierRifle', 'Tank_PanzergrenadierGrenade']
PG_RANGE_OLD, PG_RANGE_NEW = '135', '175'
PG_VISION_NEW = '220'
# HEROIC6 bounty flag (fork engine >= 2026-07-19 batch 2: ThingTemplate key MaxRankBounty)
P_BMASTER = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Battlemaster.ini'
P_REDGUARD = 'Data\\INI\\Object\\China\\Tank\\Infantry\\Redguard.ini'
BOUNTY_OBJECTS = {P_BMASTER: 'Tank_ChinaTankBattleMaster',
                  P_REDGUARD: 'Tank_ChinaInfantryRedguard',
                  P_PGREN: 'Tank_ChinaInfantryPanzergrenadier'}
# DEATH-DEFIANCE data half: inert countdown proxy the engine looks up by name
P_MARKER = 'Data\\INI\\Object\\VeterancyRespawnMarker.ini'
MARKER_INI = '\n'.join([
    '; %s: data half of the DEATH-DEFIANCE max-rank perk. RespawnAtBuildingDie' % TAG,
    '; spawns this invisible proxy by name (GameData VeterancyMaxRankRespawnMarkerName,',
    '; default "VeterancyRespawnMarker"); RespawnMarkerUpdate carries the countdown and',
    '; recreates the fallen unit. The template itself needs no INI configuration.',
    'Object VeterancyRespawnMarker',
    '  EditorSorting = SYSTEM',
    '  KindOf = IMMOBILE INERT UNATTACKABLE NO_COLLIDE',
    '  RadarPriority = NOT_ON_RADAR',
    '  Draw = W3DModelDraw ModuleTag_Draw01',
    '    DefaultConditionState',
    '      Model = NONE',
    '    End',
    '  End',
    '  Body = InactiveBody ModuleTag_Body01',
    '  End',
    '  Behavior = RespawnMarkerUpdate ModuleTag_Respawn01',
    '  End',
    '  Behavior = DestroyDie ModuleTag_Die01',
    '  End',
    '  Geometry = Sphere',
    '  GeometryIsSmall = Yes',
    '  GeometryMajorRadius = 1.0',
    'End',
    ''])

def die(msg): print('BUILD FAILED:', msg); sys.exit(1)
def check(c, msg):
    if not c: die(msg)
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)

# ---------------------------------------------------------------- sort order
for d in MODDIRS:
    probe = sorted(set(sorted_bigs(d)) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE); below = probe[:i]; above = probe[i+1:]
    for need in [OWNER, 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big', 'zzz-ZZZZZZZZZZZZZZZZZZZ0TeslaHP.big']:
        check(need in below, f'{d}: {need} must sort below us')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
print('sort position OK in both dirs')

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
EXPECTED_OWNER = {P_EMP: OWNER, P_WEAP: OWNER, P_PGREN: OWNER, P_REDGUARD: OWNER,
                  P_BMASTER: 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big'}
for p in (P_EMP, P_WEAP, P_PGREN, P_BMASTER, P_REDGUARD):
    check(eff0[p.lower()][0] == EXPECTED_OWNER[p], f'{p} owner is {eff0[p.lower()][0]} not {EXPECTED_OWNER[p]}')
    check(eff0[p.lower()][1] == eff1[p.lower()][1], f'{p} differs between mod dirs')
    # nothing above us may claim our paths
    for d in MODDIRS:
        for b in sorted_bigs(d):
            if b.lower() <= ARCHIVE.lower(): continue
            claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
            check(p.lower() not in claimed, f'{d}/{b} (above us) claims {p}')
emp_src = eff0[P_EMP.lower()][1].decode('latin-1')
weap_src = eff0[P_WEAP.lower()][1].decode('latin-1')
pgren_src = eff0[P_PGREN.lower()][1].decode('latin-1')
bounty_src = {p: eff0[p.lower()][1].decode('latin-1') for p in (P_BMASTER, P_REDGUARD)}
check(P_MARKER.lower() not in eff0, 'VeterancyRespawnMarker.ini already exists in effective space')
print('effective sources OK (both dirs agree; owner Rebalance; nothing above claims)')

# ================================================================ Emperor.ini
t = emp_src
# (1) 8x cost
t, n = re.subn(r'^(\s*BuildCost\s*=\s*)%s\b' % OLD_COST,
               r'\g<1>%s   ; %s: 8x flagship pricing (was %s)' % (NEW_COST, TAG, OLD_COST), t, flags=re.M)
check(n == 1, f'BuildCost {OLD_COST} not found exactly once (got {n})')
# (2) cannon repoints (2 weapon-set variants)
t, n = re.subn(r'(PRIMARY\s+)Tank_OverlordTankGun_Dummy\b', r'\g<1>Tank_EmperorTankGun_Dummy', t)
check(n == 2, f'PRIMARY dummy repoint expected 2, got {n}')
t, n = re.subn(r'(SECONDARY\s+)Tank_OverlordTankGun\b', r'\g<1>Tank_EmperorTankGun', t)
check(n == 2, f'SECONDARY cannon repoint expected 2, got {n}')
check('Tank_OverlordTankGun_Dummy' not in t, 'stale dummy reference left')
# (3) ABM bake
m = re.search(r'^  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_EDS_ABM01\b.*?^  End[ \t\r]*$', t, re.M | re.S)
check(m, 'EDS_ABM01 module not found')
body = m.group(0)
body, a = re.subn(r'^(\s*StartsActive\s*=\s*)No\b[^\n]*', r'\g<1>Yes   ; %s: innate from spawn (was upgrade-gated)' % TAG, body, flags=re.M)
body, b = re.subn(r'\n[ \t]*TriggeredBy\s*=\s*Tank_Upgrade_EmperorABM[^\n]*', '', body)
check(a == 1 and b == 1, f'ABM bake failed (StartsActive={a}, TriggeredBy={b})')
t = t[:m.start()] + body + t[m.end():]
# (4) InterceptBallistics on every PointDefenseLaserUpdate module
pdl_mods = list(re.finditer(r'^  Behavior = PointDefenseLaserUpdate (\S+)\b.*?^  End[ \t\r]*$', t, re.M | re.S))
check(len(pdl_mods) >= 1, 'no PointDefenseLaserUpdate modules found on Emperor')
out, last = [], 0
for m in pdl_mods:
    body = m.group(0)
    check(INTERCEPT_KEY not in body, f'{m.group(1)} already has {INTERCEPT_KEY}')
    sr = re.search(r'^(\s*)ScanRange\s*=[^\n]*\n', body, re.M)
    check(sr, f'{m.group(1)}: no ScanRange anchor')
    body = body[:sr.end()] + f'{sr.group(1)}{INTERCEPT_KEY}         = Yes  ; {TAG}: lasers also intercept artillery/nuke-cannon shells (fork engine key)\n' + body[sr.end():]
    out.append(t[last:m.start()]); out.append(body); last = m.end()
out.append(t[last:]); t = ''.join(out)
emp_new = t
print(f'Emperor.ini patched (cost 8x, cannon repoint, ABM baked, {INTERCEPT_KEY} on {len(pdl_mods)} PDL modules)')

# ================================================================= Weapon.ini
t = weap_src
# (5) gattling turret damage x1.2
scaled = 0
for w in GATT_WEAPONS:
    m = re.search(r'^Weapon %s\b.*?^End' % re.escape(w), t, re.M | re.S)
    check(m, f'weapon block missing: {w}')
    body = m.group(0)
    def scale(mm):
        val = float(mm.group(2))
        new = val * GATT_SCALE
        news = ('%.1f' % new).rstrip('0').rstrip('.')
        if '.' not in news: news += '.0'
        return mm.group(1) + news + '   ; %s: x1.2 (was %s)' % (TAG, mm.group(2))
    body, k = re.subn(r'^(\s*(?:Primary|Secondary)Damage\s*=\s*)([0-9.]+)\b[^\n]*', scale, body, flags=re.M)
    check(k >= 1, f'{w}: no damage lines scaled')
    scaled += k
    t = t[:m.start()] + body + t[m.end():]
check(scaled >= 6, f'expected >=6 damage lines scaled, got {scaled}')
# (6) Emperor cannon clones, appended
appended = []
for src_name, new_name in [('Tank_OverlordTankGun', 'Tank_EmperorTankGun'),
                           ('Tank_OverlordTankGun_Dummy', 'Tank_EmperorTankGun_Dummy')]:
    check(not re.search(r'\b%s\b' % new_name, t), f'{new_name} already exists in Weapon.ini')
    m = re.search(r'^Weapon %s\b.*?^End' % re.escape(src_name), t, re.M | re.S)
    check(m, f'donor weapon missing: {src_name}')
    blk = m.group(0)
    blk = re.sub(r'^Weapon %s\b' % re.escape(src_name), 'Weapon ' + new_name, blk, count=1)
    blk, r = re.subn(r'^(\s*AttackRange\s*=\s*)%s(\.0)?\b[^\n]*' % CANNON_RANGE_OLD,
                     r'\g<1>%s.0   ; %s: flagship long-barrel (was %s)' % (CANNON_RANGE_NEW, TAG, CANNON_RANGE_OLD),
                     blk, flags=re.M)
    check(r == 1, f'{new_name}: AttackRange {CANNON_RANGE_OLD} not found exactly once (got {r})')
    appended.append('\n;------------------------------------------------------------------------------\n'
                    '; %s: Emperor-only clone of %s (AttackRange %s -> %s). The Overlord\n'
                    '; keeps the unmodified original.\n' % (TAG, src_name, CANNON_RANGE_OLD, CANNON_RANGE_NEW) + blk + '\n')
t = t + ''.join(appended)
# (7) Panzergrenadier rifle + grenade range 135 -> 150 (vision matched in object file)
pg_ranged = 0
for w in PG_WEAPONS:
    m = re.search(r'^Weapon %s\b.*?^End' % re.escape(w), t, re.M | re.S)
    check(m, f'weapon block missing: {w}')
    body, r = re.subn(r'^(\s*AttackRange\s*=\s*)%s\.0\b[^\n]*' % PG_RANGE_OLD,
                      r'\g<1>%s.0   ; %s: was %s' % (PG_RANGE_NEW, TAG, PG_RANGE_OLD),
                      m.group(0), flags=re.M)
    check(r == 1, f'{w}: AttackRange {PG_RANGE_OLD} not found exactly once (got {r})')
    pg_ranged += r
    t = t[:m.start()] + body + t[m.end():]
check(pg_ranged == 2, f'expected 2 PG range lines, got {pg_ranged}')
weap_new = t
# donor untouched
check(re.search(r'^Weapon Tank_OverlordTankGun\b.*?^End', weap_new, re.M | re.S).group(0)
      == re.search(r'^Weapon Tank_OverlordTankGun\b.*?^End', weap_src, re.M | re.S).group(0),
      'Overlord donor weapon was modified!')
print('Weapon.ini patched (6 gattling guns x1.2 [%d damage lines], 2 Emperor cannon clones appended)' % scaled)

# ====================================================== Panzergrenadier.ini
t = pgren_src
t, n = re.subn(r'^(\s*VisionRange = )135\b[^\n]*',
               r'\g<1>%s ; %s: scout-grade eyes (was 135)' % (PG_VISION_NEW, TAG), t, flags=re.M)
check(n == 1, f'PG VisionRange 135 not found exactly once (got {n})')
# shroud clear must keep pace with the new vision (was 200 < 220)
t, n = re.subn(r'^(\s*ShroudClearingRange = )200\b[^\n]*',
               r'\g<1>%s ; %s: >= VisionRange (was 200)' % (PG_VISION_NEW, TAG), t, flags=re.M)
check(n == 1, f'PG ShroudClearingRange 200 not found exactly once (got {n})')
pgren_new = t
print('Panzergrenadier.ini patched (VisionRange -> %s, ShroudClearingRange -> %s)' % (PG_VISION_NEW, PG_VISION_NEW))

# =================================================== MaxRankBounty flags (3 units)
def add_bounty_flag(src, objname, label):
    new, n = re.subn(r'^(Object %s[ \t\r]*)$' % re.escape(objname),
                     r'\g<1>\n  MaxRankBounty = Yes ; %s: HEROIC6 kill bounty (fork engine key, batch 2)' % TAG,
                     src, flags=re.M)
    check(n == 1, f'{label}: Object {objname} header not found exactly once (got {n})')
    return new
bounty_new = {}
for p, objname in BOUNTY_OBJECTS.items():
    src = pgren_new if p == P_PGREN else bounty_src[p]
    out = add_bounty_flag(src, objname, p.split('\\')[-1])
    if p == P_PGREN:
        pgren_new = out
    else:
        bounty_new[p] = out
print('MaxRankBounty = Yes flagged on %d unit objects' % len(BOUNTY_OBJECTS))

# ------------------------------------------------------------------ diff audit
def lines_multiset_diff(old, new):
    from collections import Counter
    co, cn = Counter(old.splitlines()), Counter(new.splitlines())
    return sum((co - cn).values()), sum((cn - co).values())
d_rm, d_add = lines_multiset_diff(emp_src, emp_new)
check(d_rm <= 8 and d_add <= 9, f'Emperor.ini diff larger than planned: -{d_rm}/+{d_add}')
print(f'Emperor.ini diff audit OK (-{d_rm}/+{d_add})')
w_rm, w_add = lines_multiset_diff(weap_src, weap_new)
check(w_rm == scaled + pg_ranged, f'Weapon.ini removed {w_rm} lines, expected {scaled} scaled + {pg_ranged} PG ranges')
print(f'Weapon.ini diff audit OK (-{w_rm}/+{w_add}: scaled lines + appended clones)')
# closure: emperor references resolve
for name in ['Tank_EmperorTankGun', 'Tank_EmperorTankGun_Dummy']:
    check(re.search(r'^Weapon %s\b' % name, weap_new, re.M), f'{name} not defined')
    check(re.search(r'\b%s\b' % name, emp_new), f'{name} not referenced by Emperor')

# ------------------------------------------------------------------ write big
entries = [bigfile.BigEntry(P_EMP, emp_new.encode('latin-1')),
           bigfile.BigEntry(P_WEAP, weap_new.encode('latin-1')),
           bigfile.BigEntry(P_PGREN, pgren_new.encode('latin-1')),
           bigfile.BigEntry(P_BMASTER, bounty_new[P_BMASTER].encode('latin-1')),
           bigfile.BigEntry(P_REDGUARD, bounty_new[P_REDGUARD].encode('latin-1')),
           bigfile.BigEntry(P_MARKER, MARKER_INI.encode('latin-1'))]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check(len(rt) == len(entries) and all(rt[k].data == entries[k].data for k in range(len(entries))),
      'BIG round-trip mismatch')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
with open(out_path, 'wb') as f: f.write(blob)
tagid = ' [hash-idempotent]' if prev == blob else ''
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} files){tagid}')

if '--stage' in sys.argv:
    print('STAGED ONLY (no install) -- run without --stage to install to both mod dirs')
    sys.exit(0)

# -------------------------------------------------------------------- install
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    with open(dst, 'wb') as f: f.write(blob)
    check(open(dst, 'rb').read() == blob, f'install verify failed: {dst}')
    posteff = {}
    for b in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b)):
            posteff[e.path.lower()] = (b, e.data)
    for e in entries:
        check(posteff[e.path.lower()] == (ARCHIVE, e.data), f'{d}: {e.path} not effectively ours post-install')
    print(f'installed + post-install effective audit OK: {dst}')
print('ALL CHECKS PASSED (flagship-emperor)')
