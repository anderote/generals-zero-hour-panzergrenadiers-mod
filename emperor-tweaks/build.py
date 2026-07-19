#!/usr/bin/env python3
"""zzz-ZZZZZZZZZZZZZZZZZ0EmperorTweaks.big -- TOP data layer (17 Z's + '0')
(ShockWave SPE / GeneralsX / macOS), for Kwai (China Tank General).

Two Emperor data tweaks for the Panzergrenadiers ShockWave stack:

  TWEAK 1 -- simplify the tier-3 paradrop ('Panzer Waffen Drop') to drop ONLY
    2 fully-upgraded Emperor tanks (was 2 Emperor + 4 Battlemaster + 2 Gattling
    + 2 Inferno Cannon).  We edit the drop-ladder's Tank_OCL_DropLadderT3 payload
    down to a single line (2x our new full-upgrade Emperor variant), and ship a
    brand-new object file (EmperorFullDrop.ini) defining Tank_DropEmperorFullUpgrade:
    a clone of the CURRENT effective Emperor (Tank_ChinaTankEmperor, owned by the
    15-Z emperor-innate-pdl layer, so the clone already carries the innate PDL +
    the EmperorDefense EDS_* suite + Shtora + doctrine wiring) with:
      * Overlord Gattling cannon mounted at spawn -- GrantUpgradeCreate grants the
        OBJECT-scoped Upgrade_ChinaOverlordGattlingCannon (the exact idiom already
        used 8x in the effective stack), which fires the Emperor's own
        ModuleTag_07 (gattling rider OCL) + ModuleTag_WeaponSetUpgrade01 (anti-air
        weaponset).  Object-scoped => no player-wide side effect.
      * Energy shield baked ALWAYS-ON: +2000 max/initial health baked into the
        ActiveBody (the EDS_Shield01 MaxHealthUpgrade removed so a researching
        player can't double it) + EDS_Shield02 AutoHeal forced StartsActive=Yes
        (gate removed) for shield regen.
      * ABM interceptors (EDS_ABM01) + reactive hull PDL (EDS_PDL01) forced
        StartsActive=Yes, gates removed -> always firing.
      * Fleet-shield aura (EDS_Fleet01) ungated to its 2%/s rate.
      * Innate proactive PDL (ModuleTag_EmperorInnatePDL) + Shtora APS
        (ModuleTag_ShtoraAuto01) inherited from the clone, both already always-on.
      * Fixed 8-man Waffen crew loaded at birth (HelixContain PayloadTemplateName)
        + Heroic rank (VeterancyGainCreate StartingLevel).  Factory GP_Crew
        modules stripped (drop variants carry their own fixed crew).
    NOTE: the player-wide China/doctrine upgrades (armour tiers, tungsten,
    uranium, nuclear, light-armour, subliminal) are deliberately NOT force-granted
    -- they are PLAYER-scoped (granting them would pollute the owner's tech state);
    the dropped Emperor still receives any the player has actually researched via
    its inherited TriggeredBy modules.  "Fully upgraded" here = the Emperor's own
    combat/defensive kit (Gattling, innate PDL, shield, ABM, hull PDL, fleet
    shield, Shtora, full crew, Heroic).
    The tier-3 tooltip (CONTROLBAR:ToolTipPanzerWaffenDrop) is updated to match.

  TWEAK 2 -- the Emperor's PDL is now innate (15-Z emperor-innate-pdl), so remove
    the buildable KwaiPDL purchase button from the Emperor's command set(s) while
    KEEPING the Gattling purchase button.  The PDL button is
    Tank_Command_UpgradeKwaiPDL; it is SHARED by 17 China command sets, so we touch
    ONLY the two Emperor sets (Tank_ChinaTankEmperorDefaultCommandSet slot 9 and
    Tank_ChinaTankEmperorPDLCommandSet slot 9), replacing each with
    Command_TransportExit.  Every other command set (incl. the 15 other units that
    legitimately still buy the PDL) is preserved byte-for-byte.  The now-dormant
    KPDL wiring on the Emperor object (ModuleTag_KPDL_Mount01/CmdSet01) is LEFT in
    place: it only fires on Tank_Upgrade_KwaiPDL, which is now un-buyable, so it
    never triggers -- and NOT re-shipping Emperor.ini keeps the innate PDL + EDS +
    crew + Shtora owned by emperor-innate-pdl untouched (zero risk).

Ships 4 files: ObjectCreationList.ini (edit T3 payload), a NEW EmperorFullDrop.ini
(the drop variant object), CommandSet.ini (drop 2 Emperor PDL buttons), and
Generals.str (retarget one tooltip).  Sorts ABOVE every data layer including a
possible 16-Z tesla-tune (17 Z's) and BELOW zzz_ControlBarPro*/zzzz_FXEnhance.
Disjoint from the concurrent tesla work (Weapon.ini / RotrShockTrooper.ini).
Reads effective sources from ~/GeneralsX/mods/ShockWaveSPE.  Depends on
../hotkey-addon/bigfile.py.
"""
import os, re, shutil, sys, hashlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-' + 'Z' * 17 + '0EmperorTweaks.big'   # 17 Z's + '0' (above 16-Z tesla-tune)
TAG = 'emperor-tweaks'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]
PRIMARY = MODDIRS[0]

# ---- shipped paths
P_OCL  = 'Data\\INI\\ObjectCreationList.ini'
P_DROP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\EmperorFullDrop.ini'   # NEW file
P_CS   = 'Data\\INI\\CommandSet.ini'
P_STR  = 'Data\\Generals.str'
# ---- read-only source (cloned, NOT shipped)
P_EMP  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'

EXPECT_OWNER = {
    P_OCL.lower(): 'zzz-zzzzzzzzzzz1dropladder.big',
    P_CS.lower():  'zzz-zzzzzzzzzzzzz0teslafinish.big',
    P_STR.lower(): 'zzz-zzzzzzzzzzzzz0teslafinish.big',
    P_EMP.lower(): 'zzz-zzzzzzzzzzzzzzz0emperorinnatepdl.big',
}
SHIPPED = [P_OCL, P_DROP, P_CS, P_STR]

# ---- identifiers
NEW_OBJ   = 'Tank_DropEmperorFullUpgrade'
OCL_T3    = 'Tank_OCL_DropLadderT3'
PDL_BTN   = 'Tank_Command_UpgradeKwaiPDL'
GAT_BTN   = 'Tank_Command_UpgradeChinaOverlordGattlingCannon'
GAT_UPG   = 'Upgrade_ChinaOverlordGattlingCannon'
EMP_SETS  = ['Tank_ChinaTankEmperorDefaultCommandSet', 'Tank_ChinaTankEmperorPDLCommandSet']
STR_LABEL = 'CONTROLBAR:ToolTipPanzerWaffenDrop'
# crew (8, fills the HelixContain bay) + spawn rank
PZJ, MIN = 'Tank_ChinaInfantryTankHunter', 'Tank_ChinaInfantryMiniGunner'
FLM, SHK = 'Tank_ChinaInfantryFlameThrower', 'Tank_ChinaInfantryShockTrooper'
CREW = [MIN, MIN, PZJ, PZJ, FLM, FLM, SHK, SHK]
RANK = 'HEROIC'
BAY  = 8
SHIELD_HP = 2000.0   # EDS_Shield01 AddMaxHealth, baked into the body

def die(msg):
    print('BUILD FAILED:', msg); sys.exit(1)
def check(cond, msg):
    if not cond: die(msg)
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)

# ---------------------------------------------------------------- sort order
for d in MODDIRS:
    probe = sorted(set(sorted_bigs(d)) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE); below = set(probe[:i]); above = set(probe[i + 1:])
    for need in ['zzz-ZZZZZZZZZZZ1DropLadder.big', 'zzz-ZZZZZZZZZZZZZ0TeslaFinish.big',
                 'zzz-ZZZZZZZZZZZZZZZ0EmperorInnatePDL.big']:
        check(need in below, f'{d}: {need} must sort below us')
    # Layers that legitimately sort above us. Rebalance/TeslaHP share no files
    # with us; TankUpgrades embeds CommandSet.ini + Generals.str -- if a rebuild
    # ever changes OUR copies of those two files, TankUpgrades must be rebuilt
    # afterwards (verified byte-identical after the 2026-07-18 crash-fix rebuild).
    KNOWN_ABOVE = {'zzz-zzzzzzzzzzzzzzzzzz0rebalance.big',
                   'zzz-zzzzzzzzzzzzzzzzzzz1tankupgrades.big',
                   'zzz-zzzzzzzzzzzzzzzzzzz0teslahp.big'}
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_')
              or a.lower() in KNOWN_ABOVE,
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above), f'{d}: ControlBarPro must sort above us')
    # if a 16-Z tesla-tune is present it MUST sort below us
    for a in below | above:
        if 'teslatune' in a.lower():
            check(a in below, f'{d}: tesla-tune {a} must sort below us (17 Z beats 16 Z)')
print('sort position OK in both dirs (above DropLadder/TeslaFinish/EmperorInnatePDL + any 16-Z tesla-tune, below ControlBarPro*/FXEnhance)')

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
print('effective ownership OK (OCL<-DropLadder, CS/STR<-TeslaFinish, Emperor<-EmperorInnatePDL)')

# a higher-sorting archive must not already own a file we ship (informational for STR)
# TankUpgrades (built later, sorts above) legitimately re-ships CommandSet.ini
# and Generals.str with copies absorbed from our output -- those two paths are
# allowed above us, but ONLY in that archive. If our copies of them ever change,
# TankUpgrades must be rebuilt afterwards (its embedded copies would be stale).
SHARED_UP = {('zzz-zzzzzzzzzzzzzzzzzzz1tankupgrades.big', 'data\\ini\\commandset.ini'),
             ('zzz-zzzzzzzzzzzzzzzzzzz1tankupgrades.big', 'data\\generals.str')}
for d in MODDIRS:
    for b in sorted_bigs(d):
        if str.lower(b) <= ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        for p in SHIPPED:
            if (b.lower(), p.lower()) in SHARED_UP:
                continue
            check(p.lower() not in claimed, f'{d}/{b} (sorts above us) claims {p}')
print('no higher-sorting archive claims any shipped path (TankUpgrades CS/STR shares excepted)')

# warn (do not fail) if a lower 16-Z tesla-tune also ships Generals.str -- our
# 17-Z copy shadows it; our load_effective already builds on the winning copy, so
# rebuild THIS layer last if tesla-tune changes Generals.str.
for d in MODDIRS:
    for b in sorted_bigs(d):
        if not (str.lower(b) < ARCHIVE.lower() and 'teslatune' in b.lower()):
            continue
        if any(e.path.lower() == P_STR.lower() for e in bigfile.read_big(os.path.join(d, b))):
            print(f'NOTE: {d}/{b} also ships Generals.str; our 17-Z copy is built on the effective '
                  f'(winning) version -- rebuild emperor-tweaks LAST if tesla-tune changes strings.')

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
def module_block(text, modtag, label):
    """Isolate a 2-space-indent 'Behavior = <type> <modtag> ... End' block."""
    m = re.search(r'^  Behavior = \S+ %s\b.*?^  End[ \t\r]*$' % re.escape(modtag), text, re.M | re.S)
    check(m, f'{label}: module {modtag} not found'); return m

# ============================================================ closure prechecks
all_ini = '\n'.join(data.decode('latin-1') for p, (b, data) in eff.items()
                    if p.endswith('.ini'))
# our new object id must be definition-collision-free. Plain *references* are
# allowed: DropLadder (sorts below, built later) wires its tier-3 drop OCL to
# this object by name, so on a rebuild the name legitimately appears as a
# reference in the effective space -- only a competing *definition* is fatal.
check(not re.search(r'^\s*Object\s+%s\b' % re.escape(NEW_OBJ), all_ini, re.M),
      f'{NEW_OBJ} already DEFINED in effective space')
# gattling grant idiom + targets resolve
check(re.search(r'^Upgrade\s+%s\b' % re.escape(GAT_UPG), all_ini, re.M), f'{GAT_UPG} undefined')
gtype = re.search(r'^Upgrade\s+%s\b(.*?)^End' % re.escape(GAT_UPG), all_ini, re.M | re.S)
check('Type' in gtype.group(1) and re.search(r'Type\s*=\s*OBJECT', gtype.group(1)),
      f'{GAT_UPG} must be an OBJECT upgrade (object-scoped grant)')
check(re.search(r'^ObjectCreationList\s+OCL_Tank_OverlordGattlingCannon\b', all_ini, re.M),
      'gattling rider OCL_Tank_OverlordGattlingCannon missing')
check(re.search(r'Behavior = GrantUpgradeCreate\s+\S+\s*\n\s*UpgradeToGrant\s*=\s*%s' % re.escape(GAT_UPG),
                all_ini), 'GrantUpgradeCreate->gattling precedent missing from effective stack')
# crew units resolve
for c in set(CREW):
    check(re.search(r'^Object\s+%s\b' % re.escape(c), all_ini, re.M), f'crew object {c} missing')
# cargo plane + parachute for the drop
for obj in ['ChinaJetCargoPlane', 'ChinaVehicleParachute']:
    check(re.search(r'^Object\s+%s\b' % re.escape(obj), all_ini, re.M), f'{obj} missing')
print('closure prechecks OK (new id free; gattling upgrade=OBJECT + rider OCL + GrantUpgradeCreate precedent; crew/plane resolve)')

# ================================================= TWEAK 1a: full-upgrade variant
emp = eff[P_EMP.lower()][1].decode('latin-1')
# sanity: the source Emperor carries everything we rely on
for tok in ['Object Tank_ChinaTankEmperor', 'ModuleTag_EmperorInnatePDL', 'ModuleTag_ShtoraAuto01',
            'ModuleTag_EDS_PDL01', 'ModuleTag_EDS_ABM01', 'ModuleTag_EDS_Shield01', 'ModuleTag_EDS_Shield02',
            'ModuleTag_EDS_Fleet01', 'ModuleTag_07', 'ModuleTag_WeaponSetUpgrade01',
            'ModuleTag_GP_Crew01', 'ModuleTag_GP_Crew03', 'ModuleTag_23',
            'MaxHealth       = 1320.0', 'InitialHealth   = 1320.0', 'Slots                   = 8']:
    check(tok in emp, f'source Emperor missing expected token: {tok!r}')

t = emp
# (1) rename header
t, n = re.subn(r'^(Object\s+)Tank_ChinaTankEmperor\b', r'\g<1>' + NEW_OBJ, t, count=1, flags=re.M)
check(n == 1, 'rename Emperor header failed')
# (2) strip factory GP_Crew modules (drop variant carries its own fixed crew)
t, n = re.subn(r'[ \t]*Behavior = ObjectCreationUpgrade ModuleTag_GP_Crew\d+.*?\n[ \t]*End[ \t]*\n', '', t, flags=re.S)
check('ModuleTag_GP_Crew' not in t and n == 2, f'GP_Crew strip incomplete (removed {n}, want 2)')
# (3) Heroic rank on spawn (unconditional VeterancyGainCreate)
vb = module_block(t, 'ModuleTag_23', 'VeterancyGainCreate')
nb = vb.group(0).replace('StartingLevel = VETERAN', 'StartingLevel = %s' % RANK)
check(nb != vb.group(0), 'rank set failed')
t = t[:vb.start()] + nb + t[vb.end():]
# (4) load fixed crew via HelixContain PayloadTemplateName after the Slots line
check(len(re.findall(r'^  Behavior = HelixContain\b', t, re.M)) == 1, 'need exactly one HelixContain')
sm = re.search(r'^    Slots                   = %d\b[^\n]*$' % BAY, t, re.M)
check(sm, 'HelixContain Slots anchor not found')
crew_lines = ''.join('\n    PayloadTemplateName = %s' % c for c in CREW)
t = t[:sm.end()] + crew_lines + t[sm.end():]
# (5) bake the energy shield: +2000 into the body, remove the (now-redundant) MaxHealthUpgrade
t, n1 = re.subn(r'^    MaxHealth       = 1320\.0', '    MaxHealth       = %.1f' % (1320.0 + SHIELD_HP), t, flags=re.M)
t, n2 = re.subn(r'^    InitialHealth   = 1320\.0', '    InitialHealth   = %.1f' % (1320.0 + SHIELD_HP), t, flags=re.M)
check(n1 == 1 and n2 == 1, 'body health bake failed')
sh1 = module_block(t, 'ModuleTag_EDS_Shield01', 'EDS_Shield01')
t = t[:sh1.start()] + t[sh1.end():]           # drop the MaxHealthUpgrade module
t = re.sub(r'\n[ \t]*\n(  Behavior = AutoHealBehavior ModuleTag_EDS_Shield02)', r'\n\1', t, count=1)  # tidy blank
# (6) bake ABM / hull-PDL / shield-regen always-on: StartsActive->Yes, gate removed
def bake_active(text, modtag, upg, label):
    mb = module_block(text, modtag, label)
    body = mb.group(0)
    body, a = re.subn(r'^(    StartsActive  = )No\b[^\n]*$', r'\g<1>Yes                       ; ' + TAG + ': baked always-on', body, flags=re.M)
    check(a == 1, f'{label}: StartsActive->Yes failed')
    body, b = re.subn(r'\n[ \t]*TriggeredBy   = %s[ \t]*(?:;[^\n]*)?' % re.escape(upg), '', body)
    check(b == 1, f'{label}: gate removal failed')
    return text[:mb.start()] + body + text[mb.end():]
t = bake_active(t, 'ModuleTag_EDS_ABM01', 'Tank_Upgrade_EmperorABM', 'EDS_ABM01')
t = bake_active(t, 'ModuleTag_EDS_PDL01', 'Tank_Upgrade_EmperorPDL', 'EDS_PDL01')
t = bake_active(t, 'ModuleTag_EDS_Shield02', 'Tank_Upgrade_EmperorShield', 'EDS_Shield02(AutoHeal)')
# (7) fleet-shield aura ungated to its 2%/s rate.
# The UpgradeRequired line MUST stay: PropagandaTowerBehavior::onObjectCreated
# resolves it via findUpgrade() and effectLogic() dereferences the result
# unguarded -- an absent name means findUpgrade("") == NULL and the first aura
# pulse segfaults (hasUpgradeComplete(NULL), crash verified 2026-07-18).
# Instead raise the *base* rate to 2% so the aura is always-on either way;
# the (kept) gate then only selects between two identical rates.
fb = module_block(t, 'ModuleTag_EDS_Fleet01', 'EDS_Fleet01')
body = fb.group(0)
body, a = re.subn(r'^(    HealPercentEachSecond         = )0%[^\n]*', r'\g<1>2%   ; ' + TAG + ': base rate = upgraded rate (always-on, gate kept for crash safety)', body, flags=re.M)
check(a == 1, 'fleet-shield ungate failed')
check('UpgradeRequired               = Tank_Upgrade_EmperorFleetShield' in body,
      'fleet-shield UpgradeRequired line missing from source module')
t = t[:fb.start()] + body + t[fb.end():]
# (8) mount the Gattling cannon at spawn via an OBJECT-scoped upgrade grant
grant = '\n'.join([
    '  ; ' + '-' * 76,
    '  ; %s: spawn with the Overlord Gattling cannon already mounted. Grants the' % TAG,
    '  ; OBJECT-scoped %s at creation (idiom used 8x in the effective' % GAT_UPG,
    '  ; stack) -> fires this object\'s own ModuleTag_07 (gattling rider OCL) and',
    '  ; ModuleTag_WeaponSetUpgrade01 (anti-air weaponset). Object-scoped: no player side effect.',
    '  Behavior = GrantUpgradeCreate ModuleTag_ET_GattlingGrant',
    '    UpgradeToGrant = %s' % GAT_UPG,
    '  End',
])
geo = list(re.finditer(r'^[ \t]*Geometry[ \t]*=[ \t]*BOX[ \t\r]*$', t, re.M))
check(len(geo) == 1, f'variant: need exactly one Geometry=BOX anchor (found {len(geo)})')
t = t[:geo[0].start()] + grant + '\n' + t[geo[0].start():]

# ---- verify the finished variant
check(re.search(r'^Object\s+%s\b' % NEW_OBJ, t, re.M), 'variant header missing')
check('Object Tank_ChinaTankEmperor' not in t, 'variant still named as base Emperor')
check('ModuleTag_GP_Crew' not in t, 'variant still has factory crew')
check(t.count('PayloadTemplateName = ') == len(CREW), f'variant crew count != {len(CREW)}')
check(re.search(r'StartingLevel = %s' % RANK, t), 'variant rank not HEROIC')
check('MaxHealth       = %.1f' % (1320.0 + SHIELD_HP) in t and 'InitialHealth   = %.1f' % (1320.0 + SHIELD_HP) in t,
      'variant shield HP not baked')
check('ModuleTag_EDS_Shield01' not in t, 'redundant Shield01 MaxHealthUpgrade should be removed')
# every baked defensive module is active with no gate; innate PDL + Shtora inherited
for modtag in ['ModuleTag_EDS_ABM01', 'ModuleTag_EDS_PDL01', 'ModuleTag_EDS_Shield02']:
    mb = module_block(t, modtag, modtag)
    check('StartsActive  = Yes' in mb.group(0), f'{modtag} not StartsActive=Yes')
    check('TriggeredBy' not in mb.group(0), f'{modtag} still gated')
for gate in ['Tank_Upgrade_EmperorABM', 'Tank_Upgrade_EmperorPDL', 'Tank_Upgrade_EmperorShield']:
    check(gate not in t, f'variant still references defensive gate {gate}')
# Fleet gate is deliberately KEPT (crash safety, see step 7) with equal rates.
fleet = module_block(t, 'ModuleTag_EDS_Fleet01', 'EDS_Fleet01(verify)').group(0)
check('UpgradeRequired               = Tank_Upgrade_EmperorFleetShield' in fleet,
      'fleet-shield module lost its UpgradeRequired line (would segfault in PropagandaTowerBehavior)')
check(re.search(r'HealPercentEachSecond         = 2%', fleet) and 'UpgradedHealPercentEachSecond = 2%' in fleet,
      'fleet-shield rates not both 2%')
for keep in ['ModuleTag_EmperorInnatePDL', 'ModuleTag_ShtoraAuto01', 'ModuleTag_07',
             'ModuleTag_WeaponSetUpgrade01', 'ModuleTag_EDS_Fleet01']:
    check(keep in t, f'variant lost inherited module {keep}')
check(re.search(r'Behavior = GrantUpgradeCreate ModuleTag_ET_GattlingGrant\s*\n\s*UpgradeToGrant = %s'
                % re.escape(GAT_UPG), t), 'gattling grant module malformed')
check(t.count('Behavior = PointDefenseLaserUpdate') == 1, 'innate PDL count wrong on variant')
DROP_TEXT = ('; %s -- Tank_DropEmperorFullUpgrade: fully-kitted airborne Emperor for the\n'
             '; tier-3 Panzer Waffen Drop. Clone of the effective Emperor (innate PDL + EDS\n'
             '; suite + Shtora inherited) with Gattling granted, shield/ABM/hull-PDL/fleet\n'
             '; baked always-on, %d-man Waffen crew, Heroic. Built by emperor-tweaks/build.py.\n\n'
             % (TAG, len(CREW))) + t.rstrip('\n') + '\n'
drop_new = DROP_TEXT.encode('latin-1')
print('EmperorFullDrop.ini: %s built (gattling granted; shield/ABM/hull-PDL/fleet baked; %d crew; %s)'
      % (NEW_OBJ, len(CREW), RANK))

# ================================================= TWEAK 1b: edit the T3 drop OCL
ocl_src = eff[P_OCL.lower()][1]; ocl_text = ocl_src.decode('latin-1')
om = get_block(ocl_text, 'ObjectCreationList', OCL_T3, 'OCL T3')
oblock = om.group(0)
old_payloads = re.findall(r'^    Payload = [^\n]*$', oblock, re.M)
check([p.strip() for p in old_payloads] ==
      ['Payload = Tank_DropEmperorT3 2', 'Payload = Tank_DropBattleMasterT3 4',
       'Payload = Tank_DropGattlingT3 2', 'Payload = Tank_DropInfernoT3 2'],
      f'T3 payload drifted: {old_payloads}')
new_payload = '    Payload = %s 2' % NEW_OBJ
# replace the contiguous run of 4 Payload lines with our single line
nblock = re.sub(r'(?:^    Payload = [^\n]*\n){4}', new_payload + '\n', oblock, count=1, flags=re.M)
check(nblock.count('    Payload = ') == 1 and NEW_OBJ in nblock, 'T3 payload rewrite failed')
ocl_new_text = ocl_text[:om.start()] + nblock + ocl_text[om.end():]
ocl_new = ocl_new_text.encode('latin-1')
audit('ObjectCreationList.ini (T3 payload -> 2 Emperors)', ocl_src, ocl_new,
      [p.rstrip() for p in old_payloads], [new_payload])
# survival: tier-1/tier-2 OCLs + their payloads untouched
for keep in ['ObjectCreationList Tank_OCL_DropLadderT1', 'ObjectCreationList Tank_OCL_DropLadderT2',
             'Payload = Tank_DropBattleMasterT2 4', 'Payload = Tank_DropGattlingT2 1',
             'Payload = Tank_DropGattlingT1 2']:
    check(keep in ocl_new_text, f'OCL survival lost: {keep!r}')
print('ObjectCreationList.ini: T3 payload now a single line (2x %s); T1/T2 intact' % NEW_OBJ)

# ================================================= TWEAK 2: drop the Emperor PDL button
cs_src = eff[P_CS.lower()][1]; cs_text = cs_src.decode('latin-1')
total_pdl_before = cs_text.count(PDL_BTN)
exp_rm, exp_add = [], []
cs_new_text = cs_text
for sname in EMP_SETS:
    m = get_block(cs_new_text, 'CommandSet', sname, 'CS')
    blk = m.group(0)
    line = re.search(r'^(\s*9\s*=\s*)%s\b[^\n]*$' % re.escape(PDL_BTN), blk, re.M)
    check(line, f'{sname}: slot-9 PDL button not found')
    newline = line.group(1) + 'Command_TransportExit ; %s: PDL now innate, buy button removed' % TAG
    exp_rm.append(line.group(0).rstrip()); exp_add.append(newline.rstrip())
    nblk = blk[:line.start()] + newline + blk[line.end():]
    check(PDL_BTN not in nblk, f'{sname}: PDL button still present after edit')
    check(GAT_BTN in nblk if sname == EMP_SETS[0] else True, f'{sname}: gattling button lost')
    cs_new_text = cs_new_text[:m.start()] + nblk + cs_new_text[m.end():]
cs_new = cs_new_text.encode('latin-1')
audit('CommandSet.ini (2 Emperor PDL buttons removed)', cs_src, cs_new, exp_rm, exp_add)
check(cs_new_text.count(PDL_BTN) == total_pdl_before - 2,
      'exactly 2 PDL-button references (the Emperor sets) must be removed')
# the gattling button survives in the Emperor default set; PDL button gone from both Emperor sets
check(GAT_BTN in get_block(cs_new_text, 'CommandSet', EMP_SETS[0], 'CS').group(0),
      'Gattling button lost from Emperor default set')
for sname in EMP_SETS:
    check(PDL_BTN not in get_block(cs_new_text, 'CommandSet', sname, 'CS').group(0),
          f'{sname} still shows the PDL button')
# the OTHER 15 command sets that share the PDL button keep it (byte survival via audit above)
for other in ['Tank_ChinaVehicleBattleMasterCommandSet', 'Tank_ChinaVehicleGattlingTankCommandSet',
              'ChinaVehicleInfernoCannonCommandSet', 'RussianTankGolemCommandSet']:
    check(PDL_BTN in get_block(cs_new_text, 'CommandSet', other, 'CS').group(0),
          f'{other}: shared PDL button wrongly removed')
print('CommandSet.ini: PDL button removed from the 2 Emperor sets; Gattling kept; 15 other sets keep PDL')

# ================================================= TWEAK 1c: tier-3 tooltip text
str_src = eff[P_STR.lower()][1]; str_text = str_src.decode('latin-1')
sm = re.search(r'(^%s\s*\n)"(.*?)"(\s*\nEND\s*$)' % re.escape(STR_LABEL), str_text, re.M | re.S)
check(sm, f'{STR_LABEL} entry not found')
check('2 Emperors, 4 Battlemasters' in sm.group(2), 'tooltip does not enumerate the old payload as expected')
NEW_TIP = ('Superweapon-tier airborne assault: 2 fully-upgraded Emperor tanks -- Overlord Gattling'
           ' cannon,\\n innate point-defence laser, energy shield, ABM interceptors and Shtora APS,'
           ' Heroic and Waffen-crewed. Cooldown 420 s.')
old_line = '"%s"' % sm.group(2)
new_line = '"%s"' % NEW_TIP
str_new_text = str_text[:sm.start(2) - 1] + new_line + str_text[sm.end(2) + 1:]
str_new = str_new_text.encode('latin-1')
audit('Generals.str (T3 tooltip retargeted)', str_src, str_new, [old_line], [new_line])
check(str_new_text.count(STR_LABEL) == 1 and NEW_OBJ not in str_new_text, 'str: single label, no id leak')
check(str_new_text.count('\nEND\n') == str_text.count('\nEND\n'), 'str entry count changed (must be in-place)')
print('Generals.str: tier-3 tooltip updated in place (single-entry value swap; all other strings preserved)')

# ================================================= global closure
ocl_f = ocl_new_text
# T3 OCL now references only our variant, which exists in our new file
o3 = get_block(ocl_f, 'ObjectCreationList', OCL_T3, 'OCL T3').group(0)
check(re.findall(r'Payload = (\S+)', o3) == [NEW_OBJ], 'T3 references something other than our variant')
check(re.search(r'^Object\s+%s\b' % NEW_OBJ, DROP_TEXT, re.M), 'variant object not in shipped file')
# variant crew all resolve; gattling grant target resolves; no dangling defensive gate
for c in CREW:
    check(re.search(r'PayloadTemplateName = %s\b' % re.escape(c), DROP_TEXT), f'variant crew {c} missing')
check(GAT_UPG in DROP_TEXT and 'OCL_Tank_OverlordGattlingCannon' in all_ini, 'gattling closure broken')
print('closure OK (T3->variant->crew/gattling all resolve; no dangling PDL button; disjoint files)')

# ------------------------------------------------------------------ package
entries = [bigfile.BigEntry(P_OCL, ocl_new), bigfile.BigEntry(P_DROP, drop_new),
           bigfile.BigEntry(P_CS, cs_new), bigfile.BigEntry(P_STR, str_new)]
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries], 'BIG round-trip mismatch')
print('BIG round-trip byte-identity OK (%d files)' % len(entries))
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
    # we own our 4 files effectively -- except the two paths TankUpgrades
    # (above us, built later) re-ships. TankUpgrades' copies are DERIVED from
    # ours (absorbed at its build time, plus its own edits), so it owning them
    # is correct and its bytes legitimately differ. The rebuild discipline that
    # keeps this sound: if a rebuild of THIS layer changes our CommandSet.ini
    # or Generals.str bytes vs the previously shipped archive, tank-upgrades
    # must be rebuilt afterwards (verify old-vs-new members when rebuilding).
    for p, dat in want_bytes.items():
        owner = posteff[p][0]
        if owner != ARCHIVE and (owner.lower(), p) in SHARED_UP:
            continue
        check(owner == ARCHIVE, f'{d}: {p} effective owner is {owner} not us')
        check(posteff[p][1] == dat, f'{d}: {p} installed bytes differ')
    # prior-layer Emperor object: originally owned by emperor-innate-pdl; the
    # later Rebalance layer legitimately re-ships a rebalanced Emperor.ini above
    # us. Our variant clones from the below-us effective copy either way.
    check(posteff[P_EMP.lower()][0].lower() in ('zzz-zzzzzzzzzzzzzzz0emperorinnatepdl.big',
                                                'zzz-zzzzzzzzzzzzzzzzzz0rebalance.big'),
          f'{d}: Emperor.ini owner changed: {posteff[P_EMP.lower()][0]}')
    e_emp = posteff[P_EMP.lower()][1].decode('latin-1')
    for tok in ['ModuleTag_EmperorInnatePDL', 'ModuleTag_ShtoraAuto01', 'ModuleTag_EDS_Shield01',
                'ModuleTag_EDS_ABM01', 'ModuleTag_GP_Crew01', 'ModuleTag_07',
                'Behavior = ObjectCreationUpgrade ModuleTag_KPDL_Mount01']:
        check(tok in e_emp, f'{d}: prior Emperor module lost: {tok}')
    # DropLadder still owns GrenadierDrops.ini + SpecialPower.ini (we did NOT clobber them)
    check(posteff['data\\ini\\object\\china\\tank\\vehicles\\grenadierdrops.ini'][0].lower() == 'zzz-zzzzzzzzzzz1dropladder.big',
          f'{d}: GrenadierDrops.ini ownership regressed')
    check(posteff['data\\ini\\specialpower.ini'][0].lower() == 'zzz-zzzzzzzzzzz1dropladder.big',
          f'{d}: SpecialPower.ini ownership regressed')
    # post-install effective closure: T3 -> our variant -> resolves; PDL button gone from Emperor sets only
    peff_ini = '\n'.join(v[1].decode('latin-1') for k, v in posteff.items() if k.endswith('.ini'))
    check(re.search(r'^Object\s+%s\b' % NEW_OBJ, peff_ini, re.M), f'{d}: variant not effective')
    peff_cs = posteff[P_CS.lower()][1].decode('latin-1')
    check(peff_cs.count(PDL_BTN) == total_pdl_before - 2, f'{d}: PDL button count wrong post-install')
    check(GAT_BTN in get_block(peff_cs, 'CommandSet', EMP_SETS[0], 'CS').group(0), f'{d}: gattling button lost post-install')
    print('installed + post-install effective audit OK:', dst)
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (Emperor Tweaks)')
