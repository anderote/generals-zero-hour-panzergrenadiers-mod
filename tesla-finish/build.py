#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZ0TeslaFinish.big - the "Tesla Finish" layer for
Kwai (China Tank General), ShockWave under GeneralsX (macOS).

THREE features in one layer (sorts ABOVE zzz-ZZZZZZZZZZZZ0EmperorDefense.big
= 13 Z's, BELOW zzzz_FXEnhance / zzz_ControlBarPro):

TASK 1 - RA Redux TESLA TANK ported as a buildable Kwai medium tank:
  Tank_ChinaTeslaTank (donor SovietTankTeslaTank, RARedux SovietVehicle.ini).
  War Factory PAGE 2 SLOT 4 (the slot the plain Overlord vacates - Task 3).
  $1400 / 30 s, prereq Tank_ChinaWarFactory + Tank_ChinaPropagandaCenter.
  Tesla doctrine weapon: strong vs vehicles, chain-arc vs infantry, NO AA.
  Donor art BUNDLED (SOVTSLATNK models + wheels + TeslaTankCameo).

TASK 2 - TESLA FX HARMONIZATION at the weapon level (fx-enhance owns
  FXList/ParticleSystem and sorts above us, so ParticleSystem/FXList edits
  would be MASKED - see the masking finding in README; harmonization is done
  where we CAN affect it): every tesla weapon now fires the shared family
  bolt visual (LaserName = TeslaBoltRandom, the tesla-coil family bolt) and
  the shared family fire sound (TeslaCoilWeapon).  The Shock Trooper's chain
  zaps are repointed from their private TeslaTrooperLaserBeam bolts to the
  family TeslaBoltRandom.

TASK 3 - REMOVE the plain Overlord from Kwai's roster: WF page-2 slot 4
  (Tank_Command_ConstructChinaTankOverlord -> Tank_ChinaTankOverlord, the
  vanilla Overlord, cameo SNOverlord) is REPLACED by the Tesla Tank construct
  button.  The Emperor (Tank_ChinaTankEmperor, WF page-1 slot 6, distinct
  button/object) is NOT touched.  The Overlord stub object stays dormant.

DONOR: Red Alert Redux 1.0.5 by sgtmyers88 (extracted ~/GeneralsX/donors/
RARedux).  Personal use only, no redistribution; all credit to the CCRARDX
team.
"""

import os
import re
import sys
import difflib
import hashlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
DONOR_DIR = os.path.expanduser("~/GeneralsX/donors/RARedux")
GEN_DIR = os.path.expanduser("~/GeneralsX/GeneralsZH")

OUT_NAME = "zzz-ZZZZZZZZZZZZZ0TeslaFinish.big"
TAG = "tesla-finish"
PREV = "zzz-ZZZZZZZZZZZZ0EmperorDefense.big"       # archive immediately below us
ROTR = "zzz-ZZZZZZZRotrInfantry.big"               # owner of Locomotor.ini
# archives that sort ABOVE us and legitimately own shared files (they must be
# rebuilt after us if we ever touched their files - we deliberately do NOT
# ship ParticleSystem.ini / FXList.ini precisely because fx-enhance masks
# them; see the masking finding).  ControlBarPro claims none of our paths.
ABOVE_OK = {"zzzz_fxenhance.big", "zzz_controlbarproxh.big",
            "zzz_controlbarpro2160zh.big"}

CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
WPN_PATH = "Data\\INI\\Weapon.ini"
STR_PATH = "Data\\Generals.str"
LOCO_PATH = "Data\\INI\\Locomotor.ini"
OBJ_PATH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\TeslaTank.ini"
MI_PATH = "Data\\INI\\MappedImages\\HandCreated\\TeslaTankMappedImages.INI"

OWNERS = {CS_PATH: PREV, CB_PATH: PREV, WPN_PATH: PREV, STR_PATH: PREV,
          LOCO_PATH: ROTR}

# identifiers
OBJ = "Tank_ChinaTeslaTank"
BTN = "Tank_Command_ConstructChinaTeslaTank"
WPN = "TeslaTankWeapon"
WPNH = "TeslaTankWeaponHeroic"
LOCO = "TeslaTankLocomotor"
CAMEO = "RATeslaTank"
STR_NAME = "OBJECT:TankTeslaTank"
STR_CB = "CONTROLBAR:ConstructChinaTeslaTank"
STR_TIP = "CONTROLBAR:ToolTipChinaBuildTeslaTank"
NEW_NAMES = [OBJ, BTN, WPN, WPNH, LOCO, CAMEO, STR_NAME, STR_CB, STR_TIP]

# family / base identifiers we REFERENCE (must resolve in effective data)
FAMILY_BOLT = "TeslaBoltRandom"
FAMILY_SOUND = "TeslaCoilWeapon"
DEATH_OCL = "OCL_ChinaTankBattleMasterTGDebris"
DEATH_FX = "FX_BattleMasterExplosionOneFinal"

# the Overlord button being removed (Task 3) + its object (stays dormant)
OVL_BTN = "Tank_Command_ConstructChinaTankOverlord"
OVL_OBJ = "Tank_ChinaTankOverlord"
WF2_SET = "Tank_ChinaWarFactoryCommandSet_Down"

# harmonization targets (Task 2)
HARM = [("ShockTrooperTeslaChainZap", "TeslaTrooperLaserBeam"),
        ("HeroicShockTrooperTeslaChainZap", "HeroicTeslaTrooperLaserBeam")]


# ------------------------------------------------------------------ helpers
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(raw):
    return raw.replace("\r\n", "\n")


def from_lf(lf_text, eol):
    return lf_text.replace("\n", eol) if eol != "\n" else lf_text


def replace_exact(s, old, new, count=1):
    assert s.count(old) == count, \
        "expected %d occurrences of %r, found %d" % (count, old[:80],
                                                     s.count(old))
    return s.replace(old, new)


def sub_once(s, pattern, repl):
    new, n = re.subn(pattern, repl, s, count=1)
    assert n == 1, "expected 1 match for %r, found %d" % (pattern, n)
    return new


def cut_block(s, pattern):
    """Remove exactly one regex-matched span; return new text."""
    m = re.search(pattern, s)
    assert m, "block not found: " + pattern
    return s[:m.start()] + s[m.end():]


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


def top_block(lf, kw, name):
    m = re.search(r"(?m)^%s[ \t]+%s[ \t]*(;[^\n]*)?$" % (kw, re.escape(name)),
                  lf)
    assert m, "donor block not found: %s %s" % (kw, name)
    start = m.start()
    m2 = re.search(r"(?m)^End[ \t]*$", lf[start:])
    assert m2, "unterminated donor block: " + name
    return lf[start:start + m2.end()]


def parse_sets(cs_lf):
    sets = {}
    for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End",
                         cs_lf):
        slots = {}
        for line in m.group(2).splitlines():
            lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
            if lm:
                slots[int(lm.group(1))] = lm.group(2)
        sets[m.group(1)] = slots
    return sets


def get_set_block(cs_lf, name):
    m = re.search(r"(?ms)^CommandSet[ \t]+%s[ \t]*\n.*?^End[ \t]*\n"
                  % re.escape(name), cs_lf)
    assert m, "command set not found: " + name
    return m.group(0)


def base_of(p):
    return p.replace("/", "\\").rsplit("\\", 1)[-1].rsplit(".", 1)[0].lower()


# ================================================== 1. effective sources
archives = sorted((f for f in os.listdir(SPE_DIR)
                   if f.lower().endswith(".big")
                   and f.lower() < OUT_NAME.lower()),
                  key=str.lower, reverse=True)
cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}


def effective(path):
    want = path.lower()
    for a in archives:
        for e in cache[a]:
            if e.path.lower() == want:
                return e.data.decode("latin-1"), a
    return None, None


def EFFECTIVE(path):
    return effective(path)[0]


sources = {}
for path, owner in OWNERS.items():
    data, got = effective(path)
    assert data is not None, "effective source not found: " + path
    assert got == owner, "ownership drift for %s: %s (expected %s)" % (
        path, got, owner)
    sources[path] = data
print("effective-file ownership verified (%d files)" % len(sources))

# new file/asset paths must be unclaimed everywhere (except our own archive)
new_ini_paths = {p.lower() for p in [OBJ_PATH, MI_PATH]}
for d in (SPE_DIR, SHW_DIR):
    for a in (f for f in os.listdir(d) if f.lower().endswith(".big")
              and f.lower() != OUT_NAME.lower()):
        for e in read_big(os.path.join(d, a)):
            assert e.path.lower() not in new_ini_paths, (d, a, e.path)
print("new INI paths unclaimed across both mod dirs")

# identifier collision check across the whole effective INI/STR space
ini_space = []
seen = set()
for a in archives:
    for e in cache[a]:
        lp = e.path.lower()
        if lp in seen or not lp.endswith((".ini", ".str")):
            continue
        seen.add(lp)
        ini_space.append(e.data.decode("latin-1"))
blob = "\n".join(ini_space)
for name in NEW_NAMES:
    assert not re.search(r"(?<![\w:])%s(?![\w:])" % re.escape(name), blob), \
        "identifier collision: " + name
print("new identifiers collision-free (%d names, %d effective INI/STR files)"
      % (len(NEW_NAMES), len(seen)))

# referenced family / base identifiers must already resolve
assert re.search(r"(?m)^Object\s+%s\b" % FAMILY_BOLT, blob), \
    "family bolt not defined in effective data: " + FAMILY_BOLT
assert re.search(r"(?m)^AudioEvent\s+%s\b" % FAMILY_SOUND, blob), \
    "family sound not defined: " + FAMILY_SOUND
assert re.search(r"(?m)^ObjectCreationList\s+%s\b" % DEATH_OCL, blob), DEATH_OCL
assert re.search(r"(?m)^FXList\s+%s\b" % DEATH_FX, blob), DEATH_FX
for a in ("TankArmor",):
    assert re.search(r"(?m)^Armor\s+%s\b" % a, blob), a
print("referenced family/base identifiers resolve (bolt, sound, death OCL/FX,"
      " armor)")

# ================================================== 2. donor extraction
donor_ini = {e.path.lower(): e.data for e in
             read_big(os.path.join(DONOR_DIR, "00_CCRARDXINI.big"))}
donor_art = {e.path.lower(): e for e in
             read_big(os.path.join(DONOR_DIR, "00_CCRARDXART.big"))}


def donor_text(path):
    return to_lf(donor_ini[path.lower()].decode("latin-1"))


d_veh = donor_text("Data\\INI\\Object\\SOVIET\\SovietVehicle.ini")
d_wpn = donor_text("Data\\INI\\Weapon.ini")
d_loco = donor_text("Data\\INI\\Locomotor.ini")
d_mi = donor_text("Data\\INI\\MappedImages\\HandCreated\\"
                  "HandCreatedMappedImages.INI")

tank = top_block(d_veh, "Object", "SovietTankTeslaTank")
d_weapon = top_block(d_wpn, "Weapon", "TeslaTankWeapon")
d_locomotor = top_block(d_loco, "Locomotor", "TeslaTankLocomotor")
mi_block = top_block(d_mi, "MappedImage", "RATeslaTank")

# ---- donor drift guards (README stats depend on these exact donor numbers)
for needle in ("Object SovietTankTeslaTank", "Side                      = Soviet",
               "BuildCost       = 1000", "BuildTime       = 30.0",
               "Model         = SOVTSLATNK", "Weapon           = PRIMARY TeslaTankWeapon",
               "Locomotor       = SET_NORMAL TeslaTankLocomotor",
               "MaxHealth       = 600.0", "SubdualDamageCap = 760",
               "Object = SovietTechCenter",
               "Behavior = StealthUpdate ModuleTag_GapGenerator",
               "OCL = FINAL    OCL_TeslaTankDeathEffect"):
    assert needle in tank, "donor tank drift: " + needle
for needle in ("PrimaryDamage               = 80.0", "AttackRange                 = 200.0",
               "LaserName                   = TeslaBoltRandom",
               "FireSound                   = TeslaCoilWeapon",
               "DamageType                  = PARTICLE_BEAM",
               "AntiAirborneVehicle         = No"):
    assert needle in d_weapon, "donor weapon drift: " + needle
assert "Speed               = 40" in d_locomotor
assert "Texture = TeslaTankCameo.tga" in mi_block
print("donor drift guards OK (tank object, weapon, locomotor, cameo)")

# ================================================== 3. transform the tank
tank_ends0 = end_lines(tank)

tank = replace_exact(tank, "Object SovietTankTeslaTank", "Object " + OBJ)
# drop the RA tech-armor upgrade cameo (Kwai cannot research it)
tank = sub_once(tank, r"(?m)^  UpgradeCameo1 = Upgrade_AdvancedTankArmor\n", "")
tank = replace_exact(tank, "  DisplayName               = OBJECT:TeslaTank",
                     "  DisplayName               = " + STR_NAME)
tank = replace_exact(tank, "  Side                      = Soviet",
                     "  Side                      = ChinaTankGeneral ; " + TAG
                     + ": donor Soviet")
tank = replace_exact(tank, "  BuildCost       = 1000",
                     "  BuildCost       = 1400 ; " + TAG
                     + ": donor 1000 (Kwai medium-tesla specialist)")

# weapon set: donor single set -> base + HERO pair (family veterancy parity)
wset = re.search(r"(?ms)^  WeaponSet\n.*?^  End\n", tank).group(0)
assert "Weapon           = PRIMARY TeslaTankWeapon" in wset
tank = replace_exact(tank, wset, (
    "  WeaponSet\n"
    "    Conditions       = None\n"
    "    Weapon           = PRIMARY " + WPN + "\n"
    "  End\n"
    "  WeaponSet ; " + TAG + ": heroic-rank bolt - the engine flips"
    " WEAPONSET_HERO at heroic veterancy (Object.cpp:3187-3211)\n"
    "    Conditions       = HERO\n"
    "    Weapon           = PRIMARY " + WPNH + "\n"
    "  End\n"))

# drop the PLAYER_UPGRADE ArmorSet (its UpgradedTankArmor was gated by the
# dropped RA tech-armor upgrade) + the ArmorUpgrade module
tank = cut_block(tank, r"(?ms)^  ArmorSet\n    Conditions        = PLAYER_UPGRADE"
                       r"\n.*?^  End\n")
tank = cut_block(tank, r"(?ms)^  Behavior                = ArmorUpgrade "
                       r"ModuleTag_ArmorUp01\n.*?^  End\n")

# prerequisites: donor Soviet tech chain + science -> Kwai WF + Prop Center
prereq = re.search(r"(?ms)^  Prerequisites\n.*?^  End\n", tank).group(0)
assert "SovietTechCenter" in prereq and "SCIENCE_SovietTeslaTank" in prereq
tank = replace_exact(tank, prereq, (
    "  Prerequisites ; " + TAG + ": donor needed SovietTechCenter +"
    " SCIENCE_SovietTeslaTank\n"
    "    Object = Tank_ChinaWarFactory\n"
    "    Object = Tank_ChinaPropagandaCenter\n"
    "  End\n"))

# veterancy reachable for a combat tank (Battlemaster tiers)
tank = replace_exact(
    tank, "  ExperienceRequired  = 0 3500 4500 5500   ; Experience points"
    " needed to gain each level",
    "  ExperienceRequired  = 0 200 300 600   ; " + TAG + ": donor 0 3500 4500"
    " 5500 (unreachable) -> Battlemaster tiers")

# 2x -> +20% China-tank convention health
tank = replace_exact(tank, "    MaxHealth       = 600.0",
                     "    MaxHealth       = 720.0 ; " + TAG + ": donor 600 (+20%)")
tank = replace_exact(tank, "    InitialHealth   = 600.0",
                     "    InitialHealth   = 720.0 ; " + TAG)
tank = replace_exact(tank, "    SubdualDamageCap = 760",
                     "    SubdualDamageCap = 900 ; " + TAG)

# audio: RA Soviet voices are not in our space -> remap to China Battlemaster
for old, new in (
        ("VoiceSelect     = SovietVehicleVoiceSelect",
         "VoiceSelect     = BattleMasterTankVoiceSelect"),
        ("VoiceMove       = SovietVehicleVoiceMove",
         "VoiceMove       = BattleMasterTankVoiceMove"),
        ("VoiceGuard      = SovietVehicleVoiceMove",
         "VoiceGuard      = BattleMasterTankVoiceMove"),
        ("VoiceAttack     = SovietVehicleVoiceAttack",
         "VoiceAttack     = BattleMasterTankVoiceAttack"),
        ("    VoiceCreate     = SovietVehicleVoiceCreate",
         "    VoiceCreate     = BattleMasterTankVoiceCreate"),
        ("    VoiceEnter      = SovietVehicleVoiceMove",
         "    VoiceEnter      = BattleMasterTankVoiceMove")):
    tank = replace_exact(tank, old, new + " ; " + TAG + ": donor RA voice")
# move loop: RA MCV loop -> Battlemaster engine start; drop stealth sounds
tank = sub_once(tank, r"(?m)^  SoundMoveLoop = MCVMoveLoop01\n",
                "  SoundMoveStart = BattleMasterTankMoveStart ; " + TAG + "\n")
tank = sub_once(tank, r"(?m)^  SoundMoveLoopDamaged = MCVMoveLoop01\n",
                "  SoundMoveStartDamaged = BattleMasterTankMoveStart ; " + TAG + "\n")
tank = sub_once(tank, r"(?m)^  SoundStealthOn = StealthOn\n", "")
tank = sub_once(tank, r"(?m)^  SoundStealthOff = StealthOff\n", "")

# death: donor hulk (DeadTeslaTankHulk + GXMammoth debris - not ported) ->
# reuse the China Battlemaster death (resolves in effective data)
tank = replace_exact(tank, "    OCL = FINAL    OCL_TeslaTankDeathEffect",
                     "    OCL = FINAL    " + DEATH_OCL + " ; " + TAG
                     + ": donor OCL_TeslaTankDeathEffect (RA hulk, not ported)")
tank = replace_exact(tank, "    FX  = FINAL    FX_GenericTankDeathExplosion ",
                     "    FX  = FINAL    " + DEATH_FX + " ; " + TAG)

# drop StealthUpdate (gap generator) - the spec unit is a straightforward
# medium tesla tank; stealth-when-idle is an unrequested wrinkle
tank = cut_block(tank, r"(?ms)^  Behavior = StealthUpdate ModuleTag_GapGenerator"
                       r"\n.*?^  End\n")

# balance: removed 3 module/set blocks (2nd ArmorSet, ArmorUpgrade,
# StealthUpdate) + added 1 WeaponSet -> net End delta = -3 + 1 = -2
assert end_lines(tank) == tank_ends0 - 2, \
    "tank block balance: %d vs %d" % (end_lines(tank), tank_ends0)

# no RA/Soviet leftovers, no orphan upgrade refs
tank_code = "\n".join(l.split(";")[0] for l in tank.split("\n"))
for forbidden in ("Soviet", "MCVMoveLoop", "StealthUpdate", "UpgradedTankArmor",
                  "Upgrade_AdvancedTankArmor", "SCIENCE_SovietTeslaTank",
                  "OCL_TeslaTankDeathEffect", "DeadTeslaTankHulk"):
    assert forbidden not in tank_code, "tank leftover: " + forbidden
assert not re.search(r"AntiAirborne\w+\s*=\s*Yes", tank)

TANK_HEADER = (
    "; " + TAG + ": TESLA TANK for Kwai (China Tank General).\n"
    "; Ported from Red Alert Redux 1.0.5 by sgtmyers88 (donor object\n"
    "; SovietTankTeslaTank, Data\\INI\\Object\\SOVIET\\SovietVehicle.ini) -\n"
    "; personal use only, no redistribution, all credit to the authors.\n"
    "; A medium tank with a tesla-arc cannon (LaserName = " + FAMILY_BOLT + ",\n"
    "; the shared tesla-family bolt): strong vs vehicles, chain-arc vs\n"
    "; infantry, NO anti-air.  Deviations tagged '" + TAG + "' inline:\n"
    ";   Side/prereq/command translated to Kwai, BuildCost 1000->1400,\n"
    ";   HP 600->720 (+20% China-tank convention), veterancy retuned to\n"
    ";   reachable Battlemaster tiers + HERO weapon set, RA voices remapped\n"
    ";   to Battlemaster events, RA-only bits dropped (tech-armor upgrade +\n"
    ";   its ArmorSet, stealth gap-generator, hulk death OCL -> Battlemaster\n"
    ";   death).  Art (SOVTSLATNK models, wheels, cameo) bundled in this\n"
    "; archive.  Weapon/sound family reference: see Weapon.ini appendix.\n\n")

OBJ_INI = TANK_HEADER + tank + "\n"

# ================================================== 4. Weapon.ini
WPN_APPENDIX = """
;------------------------------------------------------------------------------
;;; %(tag)s: TESLA TANK cannon - ported from Red Alert Redux 'TeslaTankWeapon'
;;; (donor: 80 dmg x 2-bolt clip / 9 s / range 200 / PARTICLE_BEAM / arc hits
;;; ALLIES).  Tesla-family doctrine (deviations documented):
;;;   - PrimaryDamage 80 -> 120: STRONG vs vehicles (PARTICLE_BEAM 100%% vs
;;;     TankArmor -> 240/burst, ~55 dps) and one-shots infantry (HumanArmor
;;;     takes PARTICLE_BEAM at 150%% -> 180/bolt)
;;;   - SecondaryDamage 60 @ radius 25 = the chain arc to nearby infantry
;;;     (the family radius-arc approximation of chain lightning; donor had no
;;;     secondary), RadiusDamageAffects loses ALLIES so arcs never fry our own
;;;   - NO ANTI-AIR per family doctrine (donor already AntiAirborne* = No)
;;; Family reference (shared across Tesla Coil / Shock Trooper / Tesla Tank):
;;;   LaserName = %(bolt)s (jagged lightning bolt visual),
;;;   FireSound = %(snd)s (RA tesla zap).
Weapon %(wpn)s
  PrimaryDamage               = 120.0
  PrimaryDamageRadius         = 1.0
  SecondaryDamage             = 60.0
  SecondaryDamageRadius       = 25.0
  AttackRange                 = 200.0
  MinimumAttackRange          = 8.0
  DamageType                  = PARTICLE_BEAM
  DeathType                   = BURNED
  WeaponSpeed                 = 99999.0
  LaserName                   = %(bolt)s
  LaserBoneName               = WEAPONA01
  RadiusDamageAffects         = ENEMIES NEUTRALS
  DelayBetweenShots           = 400
  ClipSize                    = 2
  ClipReloadTime              = 4000
  PreAttackDelay              = 500
  PreAttackType               = PER_ATTACK
  FireSound                   = %(snd)s
  FireSoundLoopTime           = 4000
  AutoReloadsClip             = Yes
  AntiAirborneVehicle         = No
  AntiAirborneInfantry        = No
  AntiSmallMissile            = No
  AntiBallisticMissile        = No
  AntiGround                  = Yes
  ProjectileCollidesWith      = STRUCTURES
End

;;; %(tag)s: heroic-rank tesla bolt (WeaponSet Conditions = HERO on the tank).
Weapon %(wpnh)s
  PrimaryDamage               = 150.0
  PrimaryDamageRadius         = 1.0
  SecondaryDamage             = 80.0
  SecondaryDamageRadius       = 30.0
  AttackRange                 = 200.0
  MinimumAttackRange          = 8.0
  DamageType                  = PARTICLE_BEAM
  DeathType                   = BURNED
  WeaponSpeed                 = 99999.0
  LaserName                   = %(bolt)s
  LaserBoneName               = WEAPONA01
  RadiusDamageAffects         = ENEMIES NEUTRALS
  DelayBetweenShots           = 400
  ClipSize                    = 2
  ClipReloadTime              = 4000
  PreAttackDelay              = 500
  PreAttackType               = PER_ATTACK
  FireSound                   = %(snd)s
  FireSoundLoopTime           = 4000
  AutoReloadsClip             = Yes
  AntiAirborneVehicle         = No
  AntiAirborneInfantry        = No
  AntiSmallMissile            = No
  AntiBallisticMissile        = No
  AntiGround                  = Yes
  ProjectileCollidesWith      = STRUCTURES
End
""" % {"tag": TAG, "wpn": WPN, "wpnh": WPNH, "bolt": FAMILY_BOLT,
       "snd": FAMILY_SOUND}


def patch_weapon(src_lf):
    """Task 2 harmonization: repoint the Shock Trooper chain zaps to the
    shared family bolt, then append the tank weapons."""
    out = src_lf
    for wname, oldbeam in HARM:
        blk = top_block(out, "Weapon", wname)
        assert ("LaserName               = %s" % oldbeam) in blk, \
            "chain-zap beam drift: " + wname
        newblk = replace_exact(
            blk, "  LaserName               = %s\n" % oldbeam,
            "  LaserName               = %s ; %s tesla-FX harmonization:"
            " shared family bolt (was %s)\n" % (FAMILY_BOLT, TAG, oldbeam))
        out = replace_exact(out, blk, newblk)
    return out + WPN_APPENDIX


# ================================================== 5. CommandSet (Task 3)
def patch_commandset(src_lf):
    old = get_set_block(src_lf, WF2_SET)
    pre = parse_sets(old)[WF2_SET]
    assert pre.get(4) == OVL_BTN, "WF page-2 slot 4 is not the Overlord: " \
        + repr(pre.get(4))
    # confirm the Emperor CONSTRUCT button is NOT in this set (it is a page-1
    # button; the EmperorDefense *research* buttons at 8-11 are expected)
    assert not any("ConstructChinaTankEmperor" in v for v in pre.values()), \
        "unexpected Emperor construct button in WF page 2"
    line_re = re.compile(r"(?m)^  4  = %s\b.*$" % re.escape(OVL_BTN))
    m = line_re.search(old)
    assert m, "Overlord slot-4 line not found"
    new = old[:m.start()] + ("  4  = %s ; %s: replaces the plain Overlord"
                             % (BTN, TAG)) + old[m.end():]
    return replace_exact(src_lf, old, new)


# ================================================== 6. appendices
CB_APPENDIX = """
;;; %(tag)s: Tesla Tank construct button (War Factory page 2 slot 4, the slot
;;; the plain Overlord vacated).  Cameo is the donor's own RATeslaTank mapped
;;; image (TeslaTankCameo.tga, shipped in this archive).
CommandButton %(btn)s
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = %(obj)s
  TextLabel     = %(cb)s
  ButtonImage   = %(cameo)s
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = %(tip)s
End
""" % {"tag": TAG, "btn": BTN, "obj": OBJ, "cb": STR_CB, "cameo": CAMEO,
       "tip": STR_TIP}

STR_APPENDIX = (
    "\n" + STR_NAME + "\n\"Tesla Tank\"\nEND\n"
    "\n" + STR_CB + "\n\"&Tesla Tank\"\nEND\n"
    "\n" + STR_TIP + "\n\"Medium tank with a tesla-arc cannon. Strong against"
    " vehicles; its bolts one-shot infantry and arc to nearby enemies. \\n"
    " Cannot attack aircraft.\"\nEND\n")

LOCO_APPENDIX = (
    "\n; ---------------------------------------------------------------------"
    "--------\n"
    ";;; " + TAG + ": Tesla Tank locomotor, ported from Red Alert Redux"
    " (medium\n;;; tank, speed 40).\n\n" + d_locomotor + "\n")

MI_INI = (
    "; " + TAG + ": Tesla Tank cameo, ported from Red Alert Redux 1.0.5\n"
    "; (donor MappedImage RATeslaTank; TeslaTankCameo.tga shipped in this\n"
    "; archive).  Personal use only - credit sgtmyers88 / CCRARDX team.\n\n"
    + mi_block + "\n")

# ================================================== 7. build shipped texts
patched = {}
patched[WPN_PATH] = from_lf(patch_weapon(to_lf(sources[WPN_PATH])),
                            eol_of(sources[WPN_PATH]))
patched[CS_PATH] = from_lf(patch_commandset(to_lf(sources[CS_PATH])),
                           eol_of(sources[CS_PATH]))
patched[CB_PATH] = sources[CB_PATH] + from_lf(CB_APPENDIX,
                                              eol_of(sources[CB_PATH]))
patched[STR_PATH] = sources[STR_PATH] + from_lf(STR_APPENDIX,
                                                eol_of(sources[STR_PATH]))
patched[LOCO_PATH] = sources[LOCO_PATH] + from_lf(LOCO_APPENDIX,
                                                  eol_of(sources[LOCO_PATH]))
patched[OBJ_PATH] = OBJ_INI
patched[MI_PATH] = MI_INI

# ================================================== 8. verification
# ---- append-only files
for path in (CB_PATH, STR_PATH, LOCO_PATH):
    assert patched[path].startswith(sources[path]), path
print("append-only base-byte identity OK (CommandButton, Generals.str, "
      "Locomotor)")

# ---- Weapon.ini diff audit: exactly the 2 chain-zap LaserName lines changed,
# plus the appended tank weapons
w_appendix = from_lf(WPN_APPENDIX, eol_of(sources[WPN_PATH]))
assert patched[WPN_PATH].endswith(w_appendix)
w_base = to_lf(patched[WPN_PATH][:len(patched[WPN_PATH]) - len(w_appendix)])
wdiff = unified(to_lf(sources[WPN_PATH]), w_base)
wadd = [l[1:] for l in wdiff if l.startswith("+")]
wrem = [l[1:] for l in wdiff if l.startswith("-")]
assert len(wadd) == 2 and len(wrem) == 2, (wadd, wrem)
for r in wrem:
    assert "LaserName" in r and ("TeslaTrooperLaserBeam" in r), r
for a in wadd:
    assert ("LaserName               = %s ;" % FAMILY_BOLT) in a, a
wt = to_lf(w_appendix)
assert wt.count("\nWeapon ") == 2 and ("Weapon %s\n" % WPN) in wt \
    and ("Weapon %s\n" % WPNH) in wt
print("Weapon.ini diff audit OK (2 chain-zap beams harmonized to %s, "
      "2 tank weapons appended)" % FAMILY_BOLT)

# ---- CommandSet.ini diff audit: exactly slot-4 line swapped (Task 3)
csdiff = unified(to_lf(sources[CS_PATH]), to_lf(patched[CS_PATH]))
csadd = Counter(l[1:] for l in csdiff if l.startswith("+"))
csrem = Counter(l[1:] for l in csdiff if l.startswith("-"))
assert list(csrem) == ["  4  = %s ; zzz-ZZZZZKwaiRoster" % OVL_BTN], csrem
assert list(csadd) == ["  4  = %s ; %s: replaces the plain Overlord"
                       % (BTN, TAG)], csadd
print("CommandSet.ini diff audit OK (WF page-2 slot 4: Overlord -> Tesla Tank,"
      " nothing else changed)")

# ---- block-balance deltas
assert end_lines(to_lf(patched[CS_PATH])) == end_lines(to_lf(sources[CS_PATH]))
assert end_lines(to_lf(patched[CB_PATH])) - end_lines(to_lf(sources[CB_PATH])) == 1
assert end_lines(to_lf(patched[WPN_PATH])) - end_lines(to_lf(sources[WPN_PATH])) == 2
assert end_lines(to_lf(patched[LOCO_PATH])) - end_lines(to_lf(sources[LOCO_PATH])) == 1
assert (patched[STR_PATH].count("\nEND\n")
        - sources[STR_PATH].count("\nEND\n")) == 3
print("block-balance deltas OK")

# ---- object file content
obj_lf = to_lf(patched[OBJ_PATH])
for needle in ("Object " + OBJ, "Side                      = ChinaTankGeneral",
               "Object = Tank_ChinaWarFactory",
               "Object = Tank_ChinaPropagandaCenter",
               "CommandSet      = GenericCommandSet",
               "MaxHealth       = 720.0", "SubdualDamageCap = 900",
               "ExperienceRequired  = 0 200 300 600", "IsTrainable = Yes",
               "Conditions       = HERO",
               "Weapon           = PRIMARY " + WPN + "\n",
               "Weapon           = PRIMARY " + WPNH + "\n",
               "Locomotor       = SET_NORMAL " + LOCO,
               "Model         = SOVTSLATNK",
               "OCL = FINAL    " + DEATH_OCL,
               "FX  = FINAL    " + DEATH_FX,
               "VoiceSelect     = BattleMasterTankVoiceSelect"):
    assert needle in obj_lf, "object file missing: " + needle
print("object file content OK (donor draw fabric + documented Kwai edits; no "
      "Soviet/RA leftovers)")

# ---- weapon doctrine asserts
wpn_lf = to_lf(patched[WPN_PATH])
for w in (WPN, WPNH):
    t = top_block(wpn_lf, "Weapon", w)
    assert "AntiAirborneVehicle         = No" in t
    assert "AntiAirborneInfantry        = No" in t
    assert "ALLIES" not in t
    assert "LaserName                   = " + FAMILY_BOLT in t
    assert "FireSound                   = " + FAMILY_SOUND in t
    assert "DamageType                  = PARTICLE_BEAM" in t
print("tank weapon doctrine OK (no anti-air, no allied arc, family bolt+sound,"
      " PARTICLE_BEAM)")

# ---- Task 2 family coherence: every tesla weapon shares the fire sound, and
# every beam-drawn tesla weapon uses the family bolt
tesla_weapons = ["Tank_TeslaCoilWeapon", "Tank_TeslaCoilWeaponHeroic",
                 "ShockTrooperTeslaWeapon", "ShockTrooperTeslaChainZap",
                 "HeroicShockTrooperTeslaChainZap", WPN, WPNH]
for w in tesla_weapons:
    t = top_block(wpn_lf, "Weapon", w)
    assert ("FireSound               = %s" % FAMILY_SOUND) in t \
        or ("FireSound                   = %s" % FAMILY_SOUND) in t, \
        "tesla weapon not on family sound: " + w
    code = "\n".join(l.split(";")[0] for l in t.split("\n"))
    if "LaserName" in code:
        assert FAMILY_BOLT in code, "beam tesla weapon not on family bolt: " + w
        assert "TeslaTrooperLaserBeam" not in code, w
print("tesla-family FX coherence OK (%d weapons share %s; all beams use %s)"
      % (len(tesla_weapons), FAMILY_SOUND, FAMILY_BOLT))

# ---- cross-reference closure
cb_lf = to_lf(patched[CB_PATH])
b = top_block(cb_lf, "CommandButton", BTN)
assert ("Object        = %s\n" % OBJ) in b and ("ButtonImage   = %s\n" % CAMEO) in b
assert ("MappedImage %s\n" % CAMEO) in to_lf(patched[MI_PATH])
for lbl in (STR_NAME, STR_CB, STR_TIP):
    assert ("\n%s\n" % lbl) in patched[STR_PATH], lbl
assert re.search(r"(?m)^Locomotor\s+%s\b" % LOCO, to_lf(patched[LOCO_PATH]))
# tank's GenericCommandSet + all family/base refs resolve in effective data
for needle, kw in ((FAMILY_BOLT, "Object"), (DEATH_OCL, "ObjectCreationList"),
                   (DEATH_FX, "FXList"), ("GenericCommandSet", "CommandSet"),
                   ("BattleMasterTankVoiceSelect", "AudioEvent"),
                   ("BattleMasterTankMoveStart", "AudioEvent"),
                   ("TankArmor", "Armor")):
    assert re.search(r"(?m)^%s\s+%s\b" % (kw, re.escape(needle)), blob), \
        "unresolved reference: %s %s" % (kw, needle)
print("cross-reference closure OK (button->object->weapons->loco->cameo->"
      "strings; death/voice/armor/commandset refs resolve)")

# ================================================== 9. art closure + bundle
asset_paths = set()
for root in (GEN_DIR, os.path.join(GEN_DIR, "ZH_Generals"), SPE_DIR):
    if not os.path.isdir(root):
        continue
    for f in sorted(os.listdir(root)):
        if f.lower().endswith(".big") and f.lower() != OUT_NAME.lower():
            for e in read_big(os.path.join(root, f)):
                asset_paths.add(e.path.lower())

# models referenced by the tank draw
model_names = sorted(set(m.group(1) for m in re.finditer(
    r"(?m)^\s*Model\s*=\s*(\S+)", obj_lf) if m.group(1).upper() != "NULL"))
donor_by_base = {}
for p in donor_art:
    donor_by_base.setdefault(base_of(p), p)

ship = {}  # out-path -> bytes


def ship_w3d(name):
    lp = "art\\w3d\\%s.w3d" % name.lower()
    if lp in asset_paths:
        return
    src = donor_by_base.get(name.lower())
    assert src and src.lower().endswith(".w3d"), "W3D not in donor: " + name
    ship[donor_art[src].path] = donor_art[src].data


def ship_tex(name):
    b = name.rsplit(".", 1)[0].lower() if name.lower().endswith((".tga", ".dds")) \
        else name.lower()
    if any(("art\\textures\\%s.%s" % (b, ext)) in asset_paths
           for ext in ("tga", "dds")):
        return
    src = donor_by_base.get(b)
    assert src, "texture not in donor: " + name
    ship[donor_art[src].path] = donor_art[src].data


for mn in model_names:
    ship_w3d(mn)
# W3D-internal textures of every shipped/needed model
W3D_TEX_RE = re.compile(rb"[ -~]{3,60}\.(?:tga|dds|TGA|DDS)")
all_w3d = list(model_names)
for mn in all_w3d:
    src = donor_by_base.get(mn.lower())
    if src and src.lower().endswith(".w3d"):
        for t in W3D_TEX_RE.findall(donor_art[src].data):
            ship_tex(t.decode("latin-1"))
# the cameo texture
ship_tex("TeslaTankCameo.tga")

# every model + texture the tank references now resolves (effective + shipped)
shipped_bases = {base_of(p) for p in ship}
for mn in model_names:
    assert ("art\\w3d\\%s.w3d" % mn.lower()) in asset_paths \
        or mn.lower() in shipped_bases, "unresolved model: " + mn
# W3D-internal textures all resolve
for mn in all_w3d:
    src = donor_by_base.get(mn.lower())
    if not (src and src.lower().endswith(".w3d")):
        continue
    for t in W3D_TEX_RE.findall(donor_art[src].data):
        tb = base_of(t.decode("latin-1"))
        ok = tb in shipped_bases or any(
            ("art\\textures\\%s.%s" % (tb, ext)) in asset_paths
            for ext in ("tga", "dds"))
        assert ok, "unresolved W3D texture: %s in %s" % (t, mn)
# cameo resolves
assert "teslatankcameo" in shipped_bases or \
    any(("art\\textures\\teslatankcameo.%s" % e) in asset_paths for e in ("tga", "dds"))
print("art closure OK (%d W3D models needed; %d donor assets bundled: %s)"
      % (len(model_names), len(ship),
         ", ".join(sorted(base_of(p) for p in ship))))

# ================================================== 10. package + install
out_files = dict(patched)
for p, data in ship.items():
    out_files[p] = data
SHIPPED = sorted(out_files)
entries = [BigEntry(p, out_files[p] if isinstance(out_files[p], bytes)
                    else out_files[p].encode("latin-1")) for p in SHIPPED]
out_local = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_local)
print("wrote %s (%d files, %d bytes)" % (out_local, len(entries),
                                         os.path.getsize(out_local)))

# ---- BIG round-trip byte identity
rt = read_big(out_local)
assert [e.path for e in rt] == [e.path for e in entries]
for x, y in zip(rt, entries):
    assert x.data == y.data, x.path
print("BIG round-trip byte-identical")

# ---- sort order + no-masking invariant against the real listings
shipped_lc = {p.lower() for p in SHIPPED}
for d in (SPE_DIR, SHW_DIR):
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    assert listing[i - 1].lower() == PREV.lower(), listing
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        if later.lower() in ABOVE_OK:
            # fx-enhance / ControlBarPro sort above us; they must not claim any
            # path we ship (they don't - we deliberately avoid FXList/PSys)
            lp = os.path.join(d, later)
            if os.path.exists(lp):
                for e in read_big(lp):
                    assert e.path.lower() not in shipped_lc, \
                        "MASKED: %s claims our %s" % (later, e.path)
            continue
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, (d, later, e.path)
    cbp = [f for f in listing if f.lower().startswith("zzz_controlbarpro")]
    assert cbp and all(listing.index(c) > i for c in cbp), listing
    fx = [f for f in listing if f.lower() == "zzzz_fxenhance.big"]
    assert fx and listing.index(fx[0]) > i, "fx-enhance must sort after us"
    print("sort order OK in %s: %s < %s < ... < %s (nothing above masks our "
          "shipped paths)" % (d, PREV, OUT_NAME, listing[-1]))

# ---- install + re-read + effective-ownership audit in both dirs
blob_bytes = open(out_local, "rb").read()
md5s = {}
for d in (SPE_DIR, SHW_DIR):
    dst = os.path.join(d, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob_bytes)
    md5s[d] = hashlib.md5(open(dst, "rb").read()).hexdigest()
    back = read_big(dst)
    assert [e.path for e in back] == [e.path for e in entries]
    for x, y in zip(back, entries):
        assert x.data == y.data, x.path
    # post-install effective audit: our archive now owns exactly our paths
    arts = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")),
                  key=str.lower, reverse=True)
    ca = {a: read_big(os.path.join(d, a)) for a in arts}

    def eff2(path):
        w = path.lower()
        for a in arts:
            for e in ca[a]:
                if e.path.lower() == w:
                    return e.data.decode("latin-1"), a
        return None, None
    # our new files are ours; shared files are ours (we sort top of the -mod
    # for these, fx-enhance owns only FXList/PSys which we don't ship)
    for p in (OBJ_PATH, MI_PATH, CS_PATH, CB_PATH, WPN_PATH, STR_PATH, LOCO_PATH):
        _, own = eff2(p)
        assert own == OUT_NAME, "post-install owner drift %s: %s" % (p, own)
    # Task-3 proof on installed bytes: WF page-2 slot 4 is the Tesla Tank, the
    # Overlord button is gone from the set, the Overlord OBJECT still exists
    cs_i, _ = eff2(CS_PATH)
    sets_i = parse_sets(to_lf(cs_i))
    assert sets_i[WF2_SET][4] == BTN, sets_i[WF2_SET]
    assert OVL_BTN not in sets_i[WF2_SET].values()
    # Emperor button/object untouched (page-1 set still builds the Emperor)
    assert any("Tank_Command_ConstructChinaTankEmperor" in v
               for s in sets_i.values() for v in s.values()), \
        "Emperor construct button vanished!"
    ovl_obj, _ = eff2("Data\\INI\\Object\\China\\Tank\\Vehicles\\Overlord.ini")
    assert ovl_obj and re.search(r"(?m)^Object\s+%s\b" % OVL_OBJ, to_lf(ovl_obj)), \
        "Overlord stub object must remain dormant, not deleted"
    # Emperor object + its defense suite intact (survival)
    emp, _ = eff2("Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini")
    emp_lf = to_lf(emp)
    for needle in ("Object Tank_ChinaTankEmperor", "HelixContain",
                   "PropagandaTowerBehavior", "ModuleTag_EDS_Shield01",
                   "GP_Crew01"):
        assert needle in emp_lf, "Emperor survival broken: " + needle
    print("installed + audited OK in %s (owner=us for 7 files; WF2 slot4=Tesla"
          " Tank; Overlord button removed, object dormant; Emperor intact)"
          % dst)

assert md5s[SPE_DIR] == md5s[SHW_DIR], "archives differ across mod dirs"
print("both installed archives md5-match: %s" % md5s[SPE_DIR])
print("DONE")
