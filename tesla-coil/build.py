#!/usr/bin/env python3
"""Build zzz-ZZZZZZZTTeslaCoil.big - the Red Alert Redux TESLA COIL base
defense, ported to Kwai (China Tank General).  ShockWave under GeneralsX.

DONOR: Red Alert Redux 1.0.5 by sgtmyers88 (extracted at
~/GeneralsX/donors/RARedux/ - INI/art/audio read straight from the mod's
00_CCRARDX*.big archives at build time, drift-guarded).  Personal use only,
no redistribution; all credit to sgtmyers88 / the CCRARDX team.

THE PORT (donor object `SovietTeslaCoil`, SovietBuilding.ini):
  Tank_ChinaTeslaCoil - dozer-buildable defense, DOZER PAGE 2 SLOT 9
  (kwai-bunkers page idiom: 7 Tank Bunker, 8 Hacker Bunker, 9 = next free).
    $1500 / 30 s (donor $1500 / 55 s), prereq Tank_ChinaPropagandaCenter
    (donor: SovietBarracks + SovietTechCenter), HP 1200 -> 2400 (stack 2x
    building convention), EnergyProduction -3 + KindOf POWERED (donor
    semantics kept: the coil goes DARK during low power - unlike the
    kwai-basetech Base Armaments, which fire through it), donor
    DeployStyleAIUpdate charge-up (1.5 s pack/unpack, TeslaCoilCharge loop).

  THE BOLT (family visual/audio reference - future tesla units REFERENCE
  these, they must NOT redefine them):
    laser-draw object  TeslaBoltRandom (BuildVariations TeslaBolt1..4,
      W3DLaserDraw, EXLightningBolt1..4 textures, 45-wide beam, 60-90 ms)
    muzzle/target particles  TeslaBoltSparks / TeslaBoltSparks03 (+Flare)
      (donor LiveWireSparks* - RENAMED: vanilla ZH already defines a
      different LiveWireSparks; 03/Flare renamed with it for family unity)
    fire sound   AudioEvent TeslaCoilWeapon (tesla1.wav, 8 s loop)
    charge sound AudioEvent TeslaCoilCharge (tslachg2.wav - Deploy/Undeploy/
      TurretMoveLoop on the coil)
    select sound AudioEvent TeslaCoilSelect (powerselect.wav)

  THE WEAPON - tesla-family doctrine (deviations from donor documented):
    Tank_TeslaCoilWeapon: 140 PARTICLE_BEAM x3-bolt clip / 8 s reload,
    range 320 (donor 320 - already > our 225 Gattling Cannon), 0.5 s
    PreAttack charge.  Donor was 230x3: HumanArmor takes PARTICLE_BEAM at
    150% -> donor one-shot infantry AND one-burst tanks; the family calls
    for DEVASTATING vs infantry / MODERATE vs vehicles, so 140 keeps the
    one-shot on every infantry in the stack, incl. the 120 HP
    Pathfinder-clone Sharpshooter (kwai-infantry v2),
    while a full burst is 420 vs the 660 HP Battlemaster.  Chain arc:
    SecondaryDamage 90 @ radius 25 (donor radius 1.0), RadiusDamageAffects
    loses ALLIES (arcs must not fry our own).  NO ANTI-AIR (family
    doctrine; donor already AntiAirborne* = No - re-asserted).
    Tank_TeslaCoilWeaponHeroic: 190 / 120 @ 30 on WeaponSet Conditions =
    HERO (engine flips WEAPONSET_HERO at heroic rank, Object.cpp:3187-3211).

  VETERANCY: the structure ranks up from kills - IsTrainable = Yes +
  ExperienceRequired = 0 80 200 300 (Tank_ChinaTankGattling tiers; the
  engine gates XP gain on IsTrainable, ExperienceTracker.cpp:176).
  ExperienceValue 200x4 (donor = our Gattling Cannon).  kwai-doctrine
  MaxHealthUpgrade tiers deliberately NOT integrated (owned by doctrine's
  enumeration - future work).

PACKAGING: zzz-ZZZZZZZTTeslaCoil.big - case-insensitively sorts AFTER
zzz-ZZZZZZZLKwaiInfantry.big ('t' > 'l') which owns every shared INI this
layers on, AFTER any zzz-ZZZZZZZR*.big side branch ('t' > 'r', probed) and
BEFORE zzz_ControlBarPro*.big ('-' 0x2D < '_' 0x5F).  Installed to both mod
dirs.  This becomes the LAST INI layer.
"""

import os
import re
import sys
import difflib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
DONOR_DIR = os.path.expanduser("~/GeneralsX/donors/RARedux")
OUT_NAME = "zzz-ZZZZZZZTTeslaCoil.big"
TAG = "zzz-ZZZZZZZTTeslaCoil"
# CHANGELOG (kwai-infantry v2 chain rebuild): kwai-infantry removed its ZHE
# Sharpshooter port and with it its copies of Weapon/OCL/ParticleSystem/
# SoundEffects .ini - ownership of the shared INIs is now split (see OWNERS).
# CHANGELOG (rotr-infantry merge): the side branch's
# zzz-ZZZZZZZRotrInfantry.big landed immediately below us ('r' < 't' - the
# probed slot) carrying Weapon/Armor/Locomotor/FXList/ParticleSystem/OCL/
# CommandSet/CommandButton .ini + Generals.str; it is now the archive we
# layer on and the owner of every shared file we bake except
# SoundEffects.ini (rotr audio is remapped, no SoundEffects shipped).  Its
# tesla gun REFERENCES our TeslaCoilWeapon fire sound (documented soft
# dependency, exactly the family doctrine below) - see the reference
# exemption in the collision check.
PREV = "zzz-ZZZZZZZRotrInfantry.big"        # archive immediately below us
# layers ABOVE us that legitimately claim paths we ship; they are rebuilt
# after us (rebuild order: kwai-infantry -> tesla-coil -> vehicle-kit ->
# w-economy; fx-enhance is owned by another session and rebuilt there)
REBUILT_AFTER = {"zzz-zzzzzzzvehiclekit.big", "zzz-zzzzzzzweconomy.big",
                 "zzzz_fxenhance.big"}

CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
STR_PATH = "Data\\Generals.str"
WPN_PATH = "Data\\INI\\Weapon.ini"
PSY_PATH = "Data\\INI\\ParticleSystem.ini"
OCL_PATH = "Data\\INI\\ObjectCreationList.ini"
SND_PATH = "Data\\INI\\SoundEffects.ini"
OBJ_PATH = "Data\\INI\\Object\\China\\Tank\\Defences\\TeslaCoil.ini"
MI_PATH = "Data\\INI\\MappedImages\\HandCreated\\TeslaCoilMappedImages.INI"

OWNERS = {CS_PATH: PREV, CB_PATH: PREV, STR_PATH: PREV,
          # rotr-infantry merge: it bakes these three too (append-only over
          # the previous owners zzz-ZZZZZZZKwaiPDL/zzz-ZZZZChaosUnits):
          WPN_PATH: PREV,
          OCL_PATH: PREV,
          PSY_PATH: PREV,
          SND_PATH: "zz_SPE_Shw_ini.big"}

OBJ = "Tank_ChinaTeslaCoil"
BTN = "Tank_Command_ConstructChinaTeslaCoil"
SET = "Tank_ChinaTeslaCoilCommandSet"
WPN = "Tank_TeslaCoilWeapon"
WPNH = "Tank_TeslaCoilWeaponHeroic"
OCL_NAME = "OCL_TeslaCoilVision"
VIS = "TeslaCoilVisionObject"
BOLTS = ["TeslaBoltRandom", "TeslaBolt1", "TeslaBolt2", "TeslaBolt3",
         "TeslaBolt4"]
PSYS = ["TeslaBoltSparks", "TeslaBoltSparks03", "TeslaBoltSparks03Flare"]
NEW_NAMES = ([OBJ, BTN, SET, WPN, WPNH, OCL_NAME, VIS,
              "TeslaCoilWeapon", "TeslaCoilCharge", "TeslaCoilSelect",
              "RATeslaCoil", "OBJECT:TankTeslaCoil",
              "CONTROLBAR:ConstructChinaTankTeslaCoil",
              "CONTROLBAR:ToolTipChinaBuildTankTeslaCoil"]
             + BOLTS + PSYS)

# donor art/audio shipped (paths exactly as in the donor archives)
ART_W3D = ["Art\\W3D\\SOVTESLACOIL.W3D", "Art\\W3D\\SOVTESLACOIL_D.W3D",
           "Art\\W3D\\SOVTESLACOIL_B.W3D"]
ART_TEX = ["Art\\Textures\\0204lathe.dds", "Art\\Textures\\0204lathe_d.dds",
           "Art\\Textures\\exteslarctb.dds", "Art\\Textures\\atmetal.dds",
           "Art\\Textures\\atmetald.dds",
           "Art\\Textures\\atsilverroof02d.dds",
           "Art\\Textures\\exteslaflare.dds", "Art\\Textures\\reflect3.dds",
           "Art\\Textures\\rep_glow.dds", "Art\\Textures\\greyscale.dds",
           "Art\\Textures\\exlightningbolt1.DDS",
           "Art\\Textures\\exlightningbolt2.DDS",
           "Art\\Textures\\exlightningbolt3.DDS",
           "Art\\Textures\\exlightningbolt4.DDS",
           "Art\\Textures\\TeslaCoilCameo.tga"]
AUDIO = ["Data\\Audio\\Sounds\\tesla1.wav", "Data\\Audio\\Sounds\\tslachg2.wav",
         "Data\\Audio\\Sounds\\powerselect.wav"]


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
        "expected %d occurrences of %r..., found %d" % (count, old[:90],
                                                        s.count(old))
    return s.replace(old, new)


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


def top_block(lf, kw, name):
    """Extract a top-level block: header line through the first
    column-0 'End'."""
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

# new file paths + shipped asset paths must be unclaimed everywhere
new_paths = {p.lower() for p in [OBJ_PATH, MI_PATH] + ART_W3D + ART_TEX + AUDIO}
for d in (SPE_DIR, SHW_DIR):
    for a in (f for f in os.listdir(d) if f.lower().endswith(".big")
              and f.lower() != OUT_NAME.lower()
              and f.lower() not in REBUILT_AFTER):
        for e in read_big(os.path.join(d, a)):
            assert e.path.lower() not in new_paths, (d, a, e.path)
print("new paths unclaimed across both mod dirs (%d paths)" % len(new_paths))

# identifier collision check across the whole effective INI space.
# CHANGELOG (rotr-infantry merge): rotr-infantry sorts below us and
# REFERENCES the tesla family we define (FireSound = TeslaCoilWeapon on its
# tesla gun + chain zaps - the documented soft dependency; exactly the
# "future tesla units must REFERENCE these, not redefine them" doctrine).
# Its files are therefore checked for DEFINITIONS only; every other archive
# keeps the strict any-reference check.
ini_space = []
rotr_space = []
seen = set()
for a in archives:
    for e in cache[a]:
        lp = e.path.lower()
        if lp in seen or not lp.endswith((".ini", ".str")):
            continue
        seen.add(lp)
        (rotr_space if a.lower() == PREV.lower() else
         ini_space).append(e.data.decode("latin-1"))
blob = "\n".join(ini_space)
rotr_blob = "\n".join(rotr_space)
for name in NEW_NAMES:
    assert not re.search(r"(?<![\w:])%s(?![\w:])" % re.escape(name), blob), \
        "identifier collision: " + name
    assert not re.search(
        r"(?m)^\s*(?:Weapon|Object|ParticleSystem|AudioEvent|"
        r"ObjectCreationList|CommandSet|CommandButton|MappedImage|Upgrade|"
        r"Armor|Locomotor|FXList)\s+%s(?![\w:])" % re.escape(name),
        rotr_blob), "identifier redefined by rotr-infantry: " + name
print("new identifiers collision-free (%d names, %d effective INI files; "
      "rotr-infantry checked definitions-only, documented soft dependency)"
      % (len(NEW_NAMES), len(seen)))

# ================================================== 2. donor extraction
donor_ini = {e.path.lower(): e.data for e in
             read_big(os.path.join(DONOR_DIR, "00_CCRARDXINI.big"))}
donor_art = {e.path.lower(): e for e in
             read_big(os.path.join(DONOR_DIR, "00_CCRARDXART.big"))}
donor_aud = {e.path.lower(): e for e in
             read_big(os.path.join(DONOR_DIR, "00_CCRARDXAUDIO.big"))}


def donor_text(path):
    return to_lf(donor_ini[path.lower()].decode("latin-1"))


d_bldg = donor_text("Data\\INI\\Object\\SOVIET\\SovietBuilding.ini")
d_wob = donor_text("Data\\INI\\Object\\WeaponObjects.ini")
d_sys = donor_text("Data\\INI\\Object\\System.ini")
d_wpn = donor_text("Data\\INI\\Weapon.ini")
d_psy = donor_text("Data\\INI\\ParticleSystem.ini")
d_snd = donor_text("Data\\INI\\SoundEffects.ini")
d_mi = donor_text("Data\\INI\\MappedImages\\HandCreated\\"
                  "HandCreatedMappedImages.INI")

coil = top_block(d_bldg, "Object", "SovietTeslaCoil")
bolt_blocks = {b: top_block(d_wob, "Object", b) for b in
               ["TeslaBoltRandom", "TeslaBolt1", "TeslaBolt2", "TeslaBolt3",
                "TeslaBolt4"]}
vision = top_block(d_sys, "Object", "VisionObjectBaseDefense")
d_weapon = top_block(d_wpn, "Weapon", "TeslaCoilWeapon")
psy_blocks = {p: top_block(d_psy, "ParticleSystem", p) for p in
              ["LiveWireSparks", "LiveWireSparks03", "LiveWireSparks03Flare"]}
snd_blocks = {s: top_block(d_snd, "AudioEvent", s) for s in
              ["TeslaCoilWeapon", "TeslaCoilCharge", "TeslaCoilSelect"]}
mi_block = top_block(d_mi, "MappedImage", "RATeslaCoil")

# ---- donor drift guards (README stats depend on these exact numbers)
for needle in ("PrimaryDamage               = 230.0",
               "AttackRange                 = 320.0",
               "LaserName                   = TeslaBoltRandom",
               "LaserBoneName               = WEAPONA01",
               "FireOCL                     = OCL_BaseDefenseVisionObject",
               "ClipSize                    = 3",
               "ClipReloadTime              = 8000",
               "PreAttackDelay              = 500",
               "FireSound                   = TeslaCoilWeapon",
               "AntiAirborneVehicle         = No",
               "AntiAirborneInfantry        = No"):
    assert needle in d_weapon, "donor weapon drift: " + needle
for needle in ("EnergyProduction    = -3", "BuildCost           = 1500",
               "MaxHealth     = 1200.0", "SubdualDamageCap = 1200",
               "Behavior = DeployStyleAIUpdate ModuleTag_04",
               "TurretMoveLoop  = TeslaCoilCharge",
               "Deploy              = TeslaCoilCharge",
               "AnimationsRequirePower = Yes",
               "Armor          = BaseDefenseArmor",
               "ExperienceValue     = 200 200 200 200",
               " POWERED ", "Model         = SOVTESLACOIL",
               "Model              = SOVTESLACOIL_B"):
    assert needle in coil, "donor coil drift: " + needle
assert "InnerBeamWidth = 45" in bolt_blocks["TeslaBolt1"]
assert "BuildVariations = TeslaBolt1 TeslaBolt2 TeslaBolt3 TeslaBolt4" \
    in bolt_blocks["TeslaBoltRandom"]
assert "Sounds = tesla1" in snd_blocks["TeslaCoilWeapon"]
assert "Sounds = tslachg2" in snd_blocks["TeslaCoilCharge"]
assert "Sounds = powerselect" in snd_blocks["TeslaCoilSelect"]
assert "Texture = TeslaCoilCameo.tga" in mi_block
print("donor drift guards OK (coil object, weapon numbers, bolts, sounds, "
      "cameo)")

# ================================================== 3. transform the coil
coil_ends0 = end_lines(coil)

coil = replace_exact(coil, "Object SovietTeslaCoil", "Object " + OBJ)
coil = replace_exact(coil, "  DisplayName         = OBJECT:TeslaCoil",
                     "  DisplayName         = OBJECT:TankTeslaCoil")
coil = replace_exact(coil, "  Side                = Soviet",
                     "  Side                = ChinaTankGeneral ; " + TAG
                     + ": donor Soviet")
coil = replace_exact(
    coil, "  BuildTime           = 55.0           ; in seconds",
    "  BuildTime           = 30.0           ; in seconds - " + TAG
    + ": donor 55 s (our Gattling Cannon builds in 20 s)")

# weapon sets: donor single set -> base + HERO pair
m = re.search(r"(?ms)^  WeaponSet\n.*?^  End\n", coil)
assert m and "Weapon              = SECONDARY TeslaCoilWeapon" in m.group(0)
coil = replace_exact(coil, m.group(0), (
    "  WeaponSet\n"
    "    Conditions          = None\n"
    "    Weapon              = SECONDARY " + WPN + "\n"
    "  End\n"
    "  WeaponSet ; " + TAG + ": heroic-rank bolt - the engine flips"
    " WEAPONSET_HERO at heroic veterancy (Object.cpp:3187-3211)\n"
    "    Conditions          = HERO\n"
    "    Weapon              = SECONDARY " + WPNH + "\n"
    "  End\n"))

# prerequisites: donor Soviet tech chain -> Kwai Propaganda Center
m = re.search(r"(?ms)^  Prerequisites\n.*?^  End\n", coil)
assert m and "SovietTechCenter" in m.group(0)
coil = replace_exact(coil, m.group(0), (
    "  Prerequisites ; " + TAG + ": donor needed SovietBarracks +"
    " SovietTechCenter\n"
    "    Object            = Tank_ChinaPropagandaCenter\n"
    "  End\n"))

coil = replace_exact(coil, "  CommandSet          = SovietBaseDefenseCommandSet",
                     "  CommandSet          = " + SET)
coil = replace_exact(
    coil, "  ExperienceValue     = 200 200 200 200  "
    "; Experience point value at each level",
    "  ExperienceValue     = 200 200 200 200  "
    "; Experience point value at each level\n"
    "  ExperienceRequired  = 0 80 200 300 ; " + TAG + ": the coil ranks up"
    " from kills (Tank_ChinaTankGattling tiers)\n"
    "  IsTrainable         = Yes ; " + TAG + ": XP gain is gated on this"
    " (ExperienceTracker.cpp:176)")

# 2x building-health convention
coil = replace_exact(coil, "    MaxHealth     = 1200.0",
                     "    MaxHealth     = 2400.0 ; " + TAG
                     + ": donor 1200, stack 2x building convention")
coil = replace_exact(coil, "    InitialHealth = 1200.0",
                     "    InitialHealth = 2400.0 ; " + TAG)
coil = replace_exact(coil, "    SubdualDamageCap = 1200",
                     "    SubdualDamageCap = 2400 ; " + TAG)

# stack parity: our defenses (Gattling Cannon) carry no MP_COUNT_FOR_VICTORY
# - a lone surviving coil must not keep a player alive (chaos-units
# precedent: no victory-condition side effects on additional buildables)
coil = replace_exact(
    coil,
    " FS_BASE_DEFENSE POWERED IMMUNE_TO_CAPTURE MP_COUNT_FOR_VICTORY "
    ";ATTACK_NEEDS_LINE_OF_SIGHT",
    " FS_BASE_DEFENSE POWERED IMMUNE_TO_CAPTURE "
    ";ATTACK_NEEDS_LINE_OF_SIGHT - " + TAG + ": MP_COUNT_FOR_VICTORY dropped"
    " (Gattling Cannon parity)")

# dropped donor modules (RA Redux-only infrastructure)
for mod_re, why in [
        (r"(?ms)^  Behavior +?= CreateObjectDie ModuleTag_09\n.*?^  End\n",
         "OCL_SovietInfantryEjection01"),
        (r"(?ms)^  Behavior = FireWeaponUpdate ModuleTag_EVAAnnounce\n.*?^  End\n",
         "EVAConstructionCompleteSpawnerWeaponSmall"),
        (r"(?ms)^  Behavior = FireWeaponUpdate ModuleTag_BuildArea\n.*?^  End\n",
         "ConstructionYardBuildRangeWeapon")]:
    m = re.search(mod_re, coil)
    assert m and why in m.group(0), "dropped-module anchor drift: " + why
    coil = replace_exact(coil, m.group(0), "")
assert end_lines(coil) == coil_ends0 - 3 + 1, "coil block balance"

COIL_HEADER = (
    "; " + TAG + ": TESLA COIL base defense for Kwai (China Tank General).\n"
    "; Ported from Red Alert Redux 1.0.5 by sgtmyers88 (donor object\n"
    "; SovietTeslaCoil, Data\\INI\\Object\\SOVIET\\SovietBuilding.ini) -\n"
    "; personal use only, no redistribution, all credit to the authors.\n"
    "; Deviations from the donor are tagged '" + TAG + "' inline:\n"
    ";   Side/prereq/command set translated to Kwai, BuildTime 55->30 s,\n"
    ";   HP 1200->2400 (stack 2x convention), veterancy enabled\n"
    ";   (IsTrainable + ExperienceRequired), HERO weapon set added,\n"
    ";   RA-only modules dropped (Soviet crew ejection, EVA announce\n"
    ";   spawner, construction-yard build-radius decal).\n"
    "; POWER: donor semantics kept - EnergyProduction -3 + KindOf POWERED:\n"
    ";   during low power the coil is DISABLED_UNDERPOWERED (turret stops,\n"
    ";   no firing, charge animation halts via AnimationsRequirePower).\n"
    "; Support objects below (TeslaBolt*, " + VIS + ") are the\n"
    "; TESLA-FAMILY visual reference - future tesla units (Shock Trooper,\n"
    "; Tesla Tank) must REFERENCE these, not redefine them.\n\n")

BOLT_HEADER = (
    "\n; ---------------------------------------------------------------------"
    "--------\n"
    "; " + TAG + ": the tesla bolt (donor Object\\WeaponObjects.ini).  A\n"
    "; random pick of 4 W3DLaserDraw lightning-texture beams per shot\n"
    "; (BuildVariations).  Donor LiveWireSparks* particle systems renamed\n"
    "; TeslaBoltSparks* (vanilla ZH already defines a different\n"
    "; LiveWireSparks).  OBJECT:Laser DisplayName kept - vanilla laser-draw\n"
    "; objects reference it identically (never displayed; INERT system"
    " object).\n")

VIS_HEADER = (
    "\n; ---------------------------------------------------------------------"
    "--------\n"
    "; " + TAG + ": per-shot vision reveal at the bolt impact point (donor\n"
    "; VisionObjectBaseDefense, Object\\System.ini - renamed).\n")

bolts_txt = ""
for b in BOLTS:
    t = bolt_blocks[b]
    if b != "TeslaBoltRandom":
        t = replace_exact(t, "    MuzzleParticleSystem = LiveWireSparks\n",
                          "    MuzzleParticleSystem = TeslaBoltSparks\n")
        t = replace_exact(t, "    TargetParticleSystem = LiveWireSparks03\n",
                          "    TargetParticleSystem = TeslaBoltSparks03\n")
    bolts_txt += "\n" + t + "\n"

vision = replace_exact(vision, "Object VisionObjectBaseDefense",
                       "Object " + VIS)

OBJ_INI = (COIL_HEADER + coil + "\n" + BOLT_HEADER + bolts_txt
           + VIS_HEADER + "\n" + vision + "\n")

# ================================================== 4. appendices
WPN_APPENDIX = """
;------------------------------------------------------------------------------
;;; %(tag)s: Tesla Coil bolt - ported from Red Alert Redux 'TeslaCoilWeapon'
;;; (donor: 230 dmg x 3-bolt clip / 8 s reload / range 320 / PARTICLE_BEAM /
;;; radius 1.0 incl. ALLIES).  Tesla-family doctrine tuning (deviations):
;;;   - PrimaryDamage 230 -> 140: DEVASTATING vs infantry (HumanArmor takes
;;;     PARTICLE_BEAM at 150%% -> 210/bolt one-shots every infantry in the
;;;     stack, incl. the 120 HP Sharpshooter) but MODERATE vs vehicles
;;;     (TankArmor 100%% -> 420/burst vs the 660 HP Battlemaster; the donor's
;;;     690 one-bursted it)
;;;   - chain arc: SecondaryDamage 90 @ radius 25 (donor had radius 1.0);
;;;     RadiusDamageAffects loses ALLIES so arcs never fry our own troops
;;;   - NO ANTI-AIR per family doctrine (donor already AntiAirborne* = No)
;;; Family reference pieces: LaserName TeslaBoltRandom (bolt visual),
;;; FireSound TeslaCoilWeapon, charge sound TeslaCoilCharge (on the coil).
Weapon %(wpn)s
  PrimaryDamage               = 140.0
  PrimaryDamageRadius         = 1.0
  SecondaryDamage             = 90.0
  SecondaryDamageRadius       = 25.0
  AttackRange                 = 320.0
  MinimumAttackRange          = 8.0
  DamageType                  = PARTICLE_BEAM
  DeathType                   = BURNED
  WeaponSpeed                 = 99999.0
  LaserName                   = TeslaBoltRandom
  LaserBoneName               = WEAPONA01
  FireOCL                     = %(ocl)s
  RadiusDamageAffects         = ENEMIES NEUTRALS
  DelayBetweenShots           = 30
  ClipSize                    = 3
  ClipReloadTime              = 8000
  PreAttackDelay              = 500
  PreAttackType               = PER_ATTACK
  FireSound                   = TeslaCoilWeapon
  FireSoundLoopTime           = 8000
  AutoReloadsClip             = Yes
  AntiAirborneVehicle         = No
  AntiAirborneInfantry        = No
  AntiGround                  = Yes
  AntiBallisticMissile        = No
End

;;; %(tag)s: heroic-rank bolt (WeaponSet Conditions = HERO on the coil) -
;;; stronger bolt + wider arc.
Weapon %(wpnh)s
  PrimaryDamage               = 190.0
  PrimaryDamageRadius         = 1.0
  SecondaryDamage             = 120.0
  SecondaryDamageRadius       = 30.0
  AttackRange                 = 320.0
  MinimumAttackRange          = 8.0
  DamageType                  = PARTICLE_BEAM
  DeathType                   = BURNED
  WeaponSpeed                 = 99999.0
  LaserName                   = TeslaBoltRandom
  LaserBoneName               = WEAPONA01
  FireOCL                     = %(ocl)s
  RadiusDamageAffects         = ENEMIES NEUTRALS
  DelayBetweenShots           = 30
  ClipSize                    = 3
  ClipReloadTime              = 8000
  PreAttackDelay              = 500
  PreAttackType               = PER_ATTACK
  FireSound                   = TeslaCoilWeapon
  FireSoundLoopTime           = 8000
  AutoReloadsClip             = Yes
  AntiAirborneVehicle         = No
  AntiAirborneInfantry        = No
  AntiGround                  = Yes
  AntiBallisticMissile        = No
End
""" % {"tag": TAG, "wpn": WPN, "wpnh": WPNH, "ocl": OCL_NAME}

OCL_APPENDIX = """
; -----------------------------------------------------------------------------
;;; %s: per-shot shroud reveal at the bolt impact (donor
;;; OCL_BaseDefenseVisionObject, renamed with its object).
ObjectCreationList %s
  CreateObject
    ObjectNames = %s
    Count             = 1
    ContainInsideSourceObject = No
  End
End
""" % (TAG, OCL_NAME, VIS)

PSY_APPENDIX = (
    "\n; ------------------------------------------------------------------"
    "-----------\n"
    ";;; " + TAG + ": tesla-bolt muzzle/impact sparks, ported from Red Alert"
    " Redux\n"
    ";;; (donor LiveWireSparks / LiveWireSparks03 / LiveWireSparks03Flare -"
    " renamed:\n"
    ";;; vanilla ZH already defines a different LiveWireSparks).  Family"
    " reference.\n\n"
    + replace_exact(psy_blocks["LiveWireSparks"],
                    "ParticleSystem LiveWireSparks",
                    "ParticleSystem TeslaBoltSparks") + "\n\n"
    + replace_exact(
        replace_exact(psy_blocks["LiveWireSparks03"],
                      "ParticleSystem LiveWireSparks03",
                      "ParticleSystem TeslaBoltSparks03"),
        "  SlaveSystem = LiveWireSparks03Flare",
        "  SlaveSystem = TeslaBoltSparks03Flare") + "\n\n"
    + replace_exact(psy_blocks["LiveWireSparks03Flare"],
                    "ParticleSystem LiveWireSparks03Flare",
                    "ParticleSystem TeslaBoltSparks03Flare") + "\n")

SND_APPENDIX = (
    "\n;-----------------------------------------------------------------"
    "-------------\n"
    ";;; " + TAG + ": tesla-family sounds, ported from Red Alert Redux"
    " (tesla1.wav\n"
    ";;; bolt discharge, tslachg2.wav charge-up loop, powerselect.wav"
    " select).\n"
    ";;; Family reference - future tesla units reuse these events.\n\n"
    + snd_blocks["TeslaCoilWeapon"] + "\n\n"
    + snd_blocks["TeslaCoilCharge"] + "\n\n"
    + snd_blocks["TeslaCoilSelect"] + "\n")

CB_APPENDIX = """
;;; %(tag)s: Tesla Coil construct button (dozer page 2 slot 9) - the
;;; kwai-bunkers Hacker Bunker construct idiom; cameo is the donor's own
;;; RATeslaCoil mapped image (TeslaCoilCameo.tga, shipped).
CommandButton %(btn)s
  Command       = DOZER_CONSTRUCT
  UnitSpecificSound = MoneyWithdraw
  Object        = %(obj)s
  TextLabel     = CONTROLBAR:ConstructChinaTankTeslaCoil
  ButtonImage   = RATeslaCoil
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildTankTeslaCoil
End
""" % {"tag": TAG, "btn": BTN, "obj": OBJ}

STR_APPENDIX = (
    "\nOBJECT:TankTeslaCoil\n"
    "\"Tesla Coil\"\nEND\n"
    "\nCONTROLBAR:ConstructChinaTankTeslaCoil\n"
    "\"&Tesla Coil\"\nEND\n"
    "\nCONTROLBAR:ToolTipChinaBuildTankTeslaCoil\n"
    "\"Charged base defense. Devastating electric bolts one-shot infantry"
    " and arc to nearby enemies; moderate damage against vehicles. \\n"
    " Cannot attack aircraft. Shuts down without power.\"\nEND\n")

MI_INI = (
    "; " + TAG + ": Tesla Coil cameo, ported from Red Alert Redux 1.0.5\n"
    "; (donor MappedImage RATeslaCoil; TeslaCoilCameo.tga shipped in this\n"
    "; archive).  Personal use only - credit sgtmyers88 / CCRARDX team.\n\n"
    + mi_block + "\n")

SET_APPENDIX = (
    "\n;;; " + TAG + ": Tesla Coil structure set (Gattling Cannon idiom"
    " minus the\n"
    ";;; mines button - the coil carries no minefield modules).\n"
    "CommandSet " + SET + "\n"
    " 12  = Command_Stop\n"
    " 14  = Command_Sell\n"
    "End\n")

BTN_LINE = "  9  = %s ; %s\n" % (BTN, TAG)


def patch_commandset(src_lf):
    old = get_set_block(src_lf, "Tank_ChinaDozerCommandSet_Down")
    assert " 13  = Command_ChinaButtonCommandSetOneUp\n" in old
    pre = parse_sets(old)["Tank_ChinaDozerCommandSet_Down"]
    assert sorted(pre) == [1, 7, 8, 13, 14], \
        "dozer page-2 occupancy drift: " + repr(pre)
    new = replace_exact(old, " 13  = Command_ChinaButtonCommandSetOneUp\n",
                        BTN_LINE + " 13  = Command_ChinaButtonCommandSetOneUp\n")
    return replace_exact(src_lf, old, new) + SET_APPENDIX


# ================================================== 5. build shipped texts
patched = {}
cs_eol = eol_of(sources[CS_PATH])
patched[CS_PATH] = from_lf(patch_commandset(to_lf(sources[CS_PATH])), cs_eol)
for path, appendix in ((CB_PATH, CB_APPENDIX), (STR_PATH, STR_APPENDIX),
                       (WPN_PATH, WPN_APPENDIX), (PSY_PATH, PSY_APPENDIX),
                       (OCL_PATH, OCL_APPENDIX), (SND_PATH, SND_APPENDIX)):
    patched[path] = sources[path] + from_lf(appendix, eol_of(sources[path]))
patched[OBJ_PATH] = OBJ_INI
patched[MI_PATH] = MI_INI

# ================================================== 6. verification
# ---- append-only base-byte identity
for path in (CB_PATH, STR_PATH, WPN_PATH, PSY_PATH, OCL_PATH, SND_PATH):
    assert patched[path].startswith(sources[path]), path
print("append-only base-byte identity OK (CB, STR, Weapon, ParticleSystem, "
      "OCL, SoundEffects)")

# ---- CommandSet.ini diff audit: exactly 1 inserted slot line + appendix
tail_i = patched[CS_PATH].index(from_lf(";;; " + TAG, cs_eol))
base_region = to_lf(patched[CS_PATH][:tail_i])
diff = unified(to_lf(sources[CS_PATH]), base_region)
added = Counter(l[1:] for l in diff if l.startswith("+"))
removed = Counter(l[1:] for l in diff if l.startswith("-"))
assert removed == Counter(), removed
assert added == Counter({BTN_LINE.rstrip("\n"): 1, "": 1}), added
tail = to_lf(patched[CS_PATH][tail_i:])
assert tail.count("\nCommandSet ") == 1 and ("CommandSet %s\n" % SET) in tail
print("CommandSet.ini diff audit OK (1 slot-9 line inserted in dozer page 2, "
      "1 set appended, nothing else)")

# ---- block-balance deltas
for path, delta in ((CS_PATH, 1), (CB_PATH, 1), (WPN_PATH, 2), (PSY_PATH, 3),
                    (OCL_PATH, 2), (SND_PATH, 3)):
    d = end_lines(to_lf(patched[path])) - end_lines(to_lf(sources[path]))
    assert d == delta, (path, d, delta)
assert (patched[STR_PATH].count("\nEND\n")
        - sources[STR_PATH].count("\nEND\n")) == 3
print("block-balance deltas OK")

# ---- object file content
obj_lf = to_lf(patched[OBJ_PATH])
for needle in ("Object " + OBJ, "Side                = ChinaTankGeneral",
               "Object            = Tank_ChinaPropagandaCenter",
               "CommandSet          = " + SET,
               "MaxHealth     = 2400.0", "SubdualDamageCap = 2400",
               "EnergyProduction    = -3",
               "ExperienceRequired  = 0 80 200 300",
               "IsTrainable         = Yes",
               "Conditions          = HERO",
               "Weapon              = SECONDARY " + WPN + "\n",
               "Weapon              = SECONDARY " + WPNH + "\n",
               "Behavior = DeployStyleAIUpdate ModuleTag_04",
               "Deploy              = TeslaCoilCharge",
               "TurretMoveLoop  = TeslaCoilCharge",
               "VoiceSelect     = TeslaCoilSelect",
               "AnimationsRequirePower = Yes",
               "Armor          = BaseDefenseArmor",
               "Object TeslaBoltRandom", "Object TeslaBolt1",
               "Object TeslaBolt4", "Object " + VIS,
               "MuzzleParticleSystem = TeslaBoltSparks",
               "TargetParticleSystem = TeslaBoltSparks03"):
    assert needle in obj_lf, "object file missing: " + needle
obj_code = "\n".join(l.split(";")[0] for l in obj_lf.split("\n"))
for forbidden in ("Soviet", "LiveWireSparks", "EVAConstructionComplete",
                  "ConstructionYardBuildRange", "TeslaBolt5",
                  "MaxHealthUpgrade", "VeterancyBoost",
                  "MP_COUNT_FOR_VICTORY"):
    assert forbidden not in obj_code, "object file leftover: " + forbidden
assert re.search(r"(?m)^\s*KindOf\s*=.*\bPOWERED\b", obj_lf)
assert not re.search(r"AntiAirborne\w+\s*=\s*Yes", obj_lf)
print("object file content OK (donor-verbatim draw fabric + documented edits;"
      " no Soviet/RA leftovers)")

# ---- weapons: doctrine asserts
wpn_lf = to_lf(patched[WPN_PATH])
for w in (WPN, WPNH):
    m = re.search(r"(?ms)^Weapon %s\n.*?^End$" % w, wpn_lf)
    assert m, w
    t = m.group(0)
    assert "AntiAirborneVehicle         = No" in t
    assert "AntiAirborneInfantry        = No" in t
    assert "ALLIES" not in t
    assert "LaserName                   = TeslaBoltRandom" in t
    assert "FireOCL                     = " + OCL_NAME in t
    assert "FireSound                   = TeslaCoilWeapon" in t
print("weapon doctrine OK (no anti-air, no allied arc damage, family bolt + "
      "sounds wired)")

# ---- cross-reference closure
cb_lf = to_lf(patched[CB_PATH])
m = re.search(r"(?ms)^CommandButton %s\n.*?^End$" % BTN, cb_lf)
assert m and ("Object        = %s\n" % OBJ) in m.group(0)
assert "ButtonImage   = RATeslaCoil" in m.group(0)
assert "MappedImage RATeslaCoil" in to_lf(patched[MI_PATH])
s = patched[STR_PATH]
for lbl in ("OBJECT:TankTeslaCoil", "CONTROLBAR:ConstructChinaTankTeslaCoil",
            "CONTROLBAR:ToolTipChinaBuildTankTeslaCoil"):
    assert ("\n%s\n" % lbl) in s, lbl
ocl_lf = to_lf(patched[OCL_PATH])
m = re.search(r"(?ms)^ObjectCreationList %s\n.*?^End$" % OCL_NAME, ocl_lf)
assert m and ("ObjectNames = %s\n" % VIS) in m.group(0)
psy_lf = to_lf(patched[PSY_PATH])
for p in PSYS:
    assert re.search(r"(?m)^ParticleSystem %s$" % p, psy_lf), p
snd_lf = to_lf(patched[SND_PATH])
for ev in ("TeslaCoilWeapon", "TeslaCoilCharge", "TeslaCoilSelect"):
    assert re.search(r"(?m)^AudioEvent %s$" % ev, snd_lf), ev
# referenced-but-not-shipped identifiers must exist in effective data
for path, needle in (
        ("Data\\INI\\Armor.ini", "Armor BaseDefenseArmor"),
        ("Data\\INI\\DamageFX.ini", "DamageFX StructureDamageFXNoShake"),
        ("Data\\INI\\ObjectCreationList.ini",
         "ObjectCreationList OCL_ABPowerPlantExplode"),
        ("Data\\INI\\FXList.ini", "FXList FX_SmallStructureDeath"),
        ("Data\\INI\\SoundEffects.ini", "AudioEvent UnderConstructionLoop"),
        ("Data\\INI\\SoundEffects.ini",
         "AudioEvent BuildingDamagedStateLight"),
        ("Data\\INI\\SoundEffects.ini", "AudioEvent BuildingDestroy"),
        ("Data\\INI\\Voice.ini", "AudioEvent MoneyWithdraw")):
    data = EFFECTIVE(path)
    if path == "Data\\INI\\Voice.ini" and (
            data is None or needle not in to_lf(data)):
        data = EFFECTIVE("Data\\INI\\SoundEffects.ini")  # SW moves events
    assert data and needle in to_lf(data), (path, needle)
# particle systems referenced by the draw fabric + our new ones
psys_defined = set(re.findall(r"(?m)^ParticleSystem\s+(\S+)", psy_lf))
for p in ("SmolderingSmoke", "SparksLarge", "SparksMedium", "SmolderingFire",
          "StructureTransitionTinySmoke", "StructureTransitionTinyExplosion",
          "StructureTransitionTinyShockwave", "AmphibDirt",
          "TeslaBoltSparks", "TeslaBoltSparks03", "TeslaBoltSparks03Flare"):
    assert p in psys_defined, "particle system missing: " + p
# prereq + reused buttons exist
pc = EFFECTIVE("Data\\INI\\Object\\China\\Tank\\Buildings\\PropagandaCenter.ini")
assert pc and re.search(r"(?m)^Object\s+Tank_ChinaPropagandaCenter\b",
                        to_lf(pc))
for b in ("Command_Stop", "Command_Sell"):
    assert re.search(r"(?m)^CommandButton\s+%s\b" % b, cb_lf), b
print("cross-reference closure OK (button->object->set->weapons->bolt->"
      "particles->OCL->vision, strings, cameo, armor, sounds, prereq)")

# ---- art + audio closure
asset_paths = set()
for root in (os.path.expanduser("~/GeneralsX/GeneralsZH"),
             os.path.expanduser("~/GeneralsX/GeneralsZH/ZH_Generals"),
             SPE_DIR):
    if not os.path.isdir(root):
        continue
    for f in sorted(os.listdir(root)):
        if f.lower().endswith(".big") and f.lower() != OUT_NAME.lower():
            for e in read_big(os.path.join(root, f)):
                asset_paths.add(e.path.lower())
out_files = dict(patched)
for p in ART_W3D + ART_TEX:
    out_files[p] = donor_art[p.lower()].data
for p in AUDIO:
    out_files[p] = donor_aud[p.lower()].data
for p in out_files:
    asset_paths.add(p.lower() if isinstance(p, str) else p)


def art_ok(name, kind):
    n = name.lower()
    if kind == "w3d":
        return ("art\\w3d\\%s.w3d" % n) in asset_paths
    base = n[:-4] if n.endswith((".tga", ".dds")) else n
    return any(("art\\textures\\%s%s" % (base, ext)) in asset_paths
               for ext in (".tga", ".dds"))


# models + textures referenced by our INI text
art_missing = set()
for line in (obj_lf + "\n" + to_lf(patched[MI_PATH])).split("\n"):
    line = line.split(";")[0]
    m = re.match(r"^\s*Model\s*=\s*(\S+)", line, re.I)
    if m and m.group(1).upper() not in ("NONE",):
        if not art_ok(m.group(1), "w3d"):
            art_missing.add(m.group(1))
    m = re.match(r"^\s*Texture\s*=\s*(\S+)", line, re.I)
    if m and not art_ok(m.group(1), "tex"):
        art_missing.add(m.group(1))
assert not art_missing, "unresolved art: %s" % sorted(art_missing)
# particle textures of our new systems
for m in re.finditer(r"(?m)^\s*ParticleName\s*=\s*(\S+)",
                     from_lf(PSY_APPENDIX, "\n")):
    assert art_ok(m.group(1), "tex"), "particle texture: " + m.group(1)
# W3D-internal textures resolve
W3D_TEX_RE = re.compile(rb"[ -~]{3,60}\.(?:tga|dds|TGA|DDS)")
for p in ART_W3D:
    for t in W3D_TEX_RE.findall(out_files[p]):
        t = t.decode("latin-1")
        assert art_ok(t, "tex"), "W3D texture unresolved: %s in %s" % (t, p)
# audio events -> shipped wav files
for ev, wav in (("TeslaCoilWeapon", "tesla1"), ("TeslaCoilCharge", "tslachg2"),
                ("TeslaCoilSelect", "powerselect")):
    assert ("Sounds = %s" % wav) in snd_blocks[ev]
    assert ("Data\\Audio\\Sounds\\%s.wav" % wav) in out_files
print("art + audio closure OK (models, buildup, fence mound, bolt/particle "
      "textures, W3D internals, cameo, wavs)")

# ---- sibling survival (shipped text)
def verify_survival(cs_text, cb_text, str_text, label=""):
    lf = to_lf(cs_text)
    sets = parse_sets(lf)
    dz1 = sets["Tank_ChinaDozerCommandSet"]
    assert dz1[9] == "Tank_Command_ConstructChinaGattlingCannon"
    assert dz1[13] == "Command_ChinaButtonCommandSetOneDown"     # kwai-bunkers
    dz2 = sets["Tank_ChinaDozerCommandSet_Down"]
    assert dz2 == {1: "Tank_Command_ConstructChinaIndustrialPlant",
                   7: "Tank_Command_ConstructChinaBunker",
                   8: "Tank_Command_ConstructChinaHackerBunker",
                   9: BTN,
                   13: "Command_ChinaButtonCommandSetOneUp",
                   14: "Command_DisarmMinesAtPosition"}, dz2
    for n in ("Tank_ChinaBarracksCommandSet",
              "Tank_ChinaBarracksCommandSetUpgrade"):             # infantry
        b = sets[n]
        assert b[5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier"
        assert b[6] == "Tank_Command_ConstructChinaInfantryFlameThrower"
        assert b[7] == "Tank_Command_ConstructChinaInfantryMiniGunner"
        assert b[8] == "Tank_Command_ConstructChinaInfantrySharpshooter"
    wf2 = sets["Tank_ChinaWarFactoryCommandSet_Down"]             # chaos/roster
    assert wf2[2] == "Tank_Command_ConstructChinaTankJS7"
    assert wf2[7] == "Tank_Command_ConstructChinaVehicleScoutCar"
    assert wf2[12] == "Command_ChinaButtonCommandSetOneUp"
    for n in ("Tank_ChinaWarFactoryCommandSet",
              "Tank_ChinaWarFactoryCommandSetUpgrade"):           # artillery
        assert sets[n][11] == "Tank_Command_ConstructChinaVehicleInfernoCannon"
        assert sets[n][12] == "Command_ChinaButtonCommandSetOneDown"
    assert lf.count("Tank_Command_UpgradeKwaiPDL ;") == 17        # kwai-pdl
    emp = sets["Tank_ChinaTankEmperorDefaultCommandSet"]
    assert emp[9] == "Tank_Command_UpgradeKwaiPDL"
    assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
    pc_sets = {n for n in sets if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc_sets) == 50, len(pc_sets)                       # doctrine+
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):          # kwai-uav
        ic = sets["Tank_ChinaInternetCenterCommandSet" + v]
        assert ic[7] == "Tank_Command_UpgradeKwaiUAVProgram"
        assert ic[8] == "Tank_Command_KwaiUAVDeploy"
    assert "Tank_ChinaHackerBunkerCommandSet" in sets             # kwai-bunkers
    gat = sets["Tank_ChinaGattlingCannonCommandSet"]
    assert gat == {12: "Command_Stop", 13: "Command_UpgradeChinaMines",
                   14: "Command_Sell"}, gat
    assert sets[SET] == {12: "Command_Stop", 14: "Command_Sell"}
    cbl = to_lf(cb_text)
    for b in ("Tank_Command_ConstructChinaInfantrySharpshooter",  # infantry
              "Tank_Command_UpgradeKwaiPDL",                      # pdl
              "Tank_Command_ConstructChinaHackerBunker",          # bunkers
              "Tank_Command_UpgradeKwaiUAVProgram"):              # uav
        assert re.search(r"(?m)^CommandButton\s+%s\b" % b, cbl), b
    for needle in ("\nOBJECT:TankHackerBunker\n",                 # bunkers
                   "\nOBJECT:KwaiPDLPod\n",                       # pdl
                   "\nOBJECT:TankSurveillanceUAV\n",              # uav
                   "\nOBJECT:TankTeslaCoil\n"):                   # ours
        assert needle in str_text, needle
    print("  sibling survival OK" + (" (%s)" % label if label else ""))


verify_survival(patched[CS_PATH], patched[CB_PATH], patched[STR_PATH],
                "shipped")
wl = to_lf(patched[WPN_PATH])
for w in ("JS7TankGun", "Tank_KwaiPDLLaserWeapon"):               # chaos, pdl
    assert re.search(r"(?m)^Weapon\s+%s\b" % w, wl), w
print("  sibling weapon appendices OK")

# ================================================== 7. package + install
SHIPPED = sorted(out_files)
entries = [BigEntry(p, out_files[p] if isinstance(out_files[p], bytes)
                    else out_files[p].encode("latin-1")) for p in SHIPPED]
out_local = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_local)
print("wrote %s (%d files, %d bytes)" % (out_local, len(entries),
                                         os.path.getsize(out_local)))

# ---- sort order against the real listings
shipped_lc = {p.lower() for p in SHIPPED}
for d in (SPE_DIR, SHW_DIR):
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    after = listing[i - 1]
    assert after.lower() == PREV.lower(), listing
    # nothing that sorts after us may claim any path we ship (they would
    # override our bytes) - this is the real effective-file guarantee
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        if later.lower() in REBUILT_AFTER:
            continue  # documented: rebuilt after us, may claim shared INIs
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, (d, later, e.path)
    # we still sort before the ControlBarPro skins
    cbp = [f for f in listing if f.lower().startswith("zzz_controlbarpro")]
    assert cbp and all(listing.index(c) > i for c in cbp), listing
    probe = sorted(listing + ["zzz-ZZZZZZZRShockTrooper.big"], key=str.lower)
    assert probe.index("zzz-ZZZZZZZRShockTrooper.big") < probe.index(OUT_NAME)
    print("sort order OK in %s: %s < %s < %s (later archives claim none of "
          "our paths; after any zzz-ZZZZZZZR*)"
          % (d, after, OUT_NAME, listing[i + 1]))

# ---- install + re-read verification
blob_bytes = open(out_local, "rb").read()
for d in (SPE_DIR, SHW_DIR):
    dst = os.path.join(d, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob_bytes)
    back = read_big(dst)
    assert [e.path for e in back] == [e.path for e in entries]
    for x, y in zip(back, entries):
        assert x.data == y.data, x.path
    verify_survival(find_entry(back, CS_PATH).data.decode("latin-1"),
                    find_entry(back, CB_PATH).data.decode("latin-1"),
                    find_entry(back, STR_PATH).data.decode("latin-1"),
                    "installed " + d)
    inst_obj = to_lf(find_entry(back, OBJ_PATH).data.decode("latin-1"))
    assert "Object " + OBJ in inst_obj and "IsTrainable" in inst_obj
    print("installed + re-read OK:", dst)

print("DONE")
