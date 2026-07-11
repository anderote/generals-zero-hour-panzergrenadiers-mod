#!/usr/bin/env python3
"""Build zzz-ZZZZZZZLKwaiInfantry.big — THREE new Barracks infantry for Kwai
(China Tank General), ShockWave under GeneralsX.

  Barracks slot 6  FLAME TROOPER   Tank_ChinaInfantryFlameThrower
     build stub -> Spec_ChinaInfantryFlameThrower (Leang, $350 / 8 s,
     donor prereqs Spec_ChinaBarracks + Spec_ChinaWarFactory translated to
     Tank_ChinaBarracks + Tank_ChinaWarFactory).
  Barracks slot 7  MINIGUNNER      Tank_ChinaInfantryMiniGunner
     build stub -> Infa_ChinaInfantryMiniGunner (Fai, $550 / 14 s, donor
     prereq Infa_ChinaBarracks translated to Tank_ChinaBarracks).
  Barracks slot 8  SHARPSHOOTER    Tank_ChinaInfantrySharpshooter
     FULL PORT of Zero Hour Enhanced's ChinaInfantrySharpshooter ($1200 /
     30 s China sniper) with its complete closure: 176 donor INI blocks
     (objects incl. 4 build variations + wounded bodies, prone rider-switch
     system, Type 79 sniper rifle, Type 86 grenade, Type 66 claymore AP-mine
     upgrade, area-reconnaissance ability, generic ZHE infantry infra),
     47 W3D files, textures, cameos (re-paged), ZHE voice set + weapon
     sounds.  Buildable prereq: Tank_ChinaBarracks + Tank_ChinaPropagandaCenter
     (spec; ZHE donor needed only ChinaBarracks).

Stubs follow the kwai-artillery/kwai-roster BuildVariations idiom.  The
sharpshooter port follows the chaos-units cross-mod asset-port pattern:
donor blocks are shipped verbatim under their donor names (all collision-
checked); only the buildable stub is renamed (Tank_..., Side, prereqs) and
the revive OCL repointed.  Effective-file rule: this layer sorts
case-insensitively AFTER zzz-ZZZZZZZKwaiPDL.big ('k' < 'l' at char 11) and
BEFORE zzz-ZZZZZZZR* / zzz_ControlBarPro* -> last INI layer; its copies of
the 13 patched files are based on the current owners' bytes.
"""
import difflib
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, os.path.join(HERE, "..", "chaos-units", "work"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402
from iniblocks import parse_blocks  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
ZHE_DIR = os.path.expanduser("~/GeneralsX/mods/Enhanced/ZHE_BIG100a")
BASE_DIRS = [os.path.expanduser("~/GeneralsX/GeneralsZH"),
             os.path.expanduser("~/GeneralsX/GeneralsZH/ZH_Generals")]
OUT_NAME = "zzz-ZZZZZZZLKwaiInfantry.big"
TAG = "zzz-ZZZZZZZLKwaiInfantry"

CS = "Data\\INI\\CommandSet.ini"
CB = "Data\\INI\\CommandButton.ini"
UPG = "Data\\INI\\Upgrade.ini"
OCL = "Data\\INI\\ObjectCreationList.ini"
WEA = "Data\\INI\\Weapon.ini"
STR = "Data\\Generals.str"
ARM = "Data\\INI\\Armor.ini"
LOC = "Data\\INI\\Locomotor.ini"
FXL = "Data\\INI\\FXList.ini"
PSY = "Data\\INI\\ParticleSystem.ini"
SPW = "Data\\INI\\SpecialPower.ini"
VOI = "Data\\INI\\Voice.ini"
SFX = "Data\\INI\\SoundEffects.ini"
IP = "Data\\INI\\Object\\China\\Tank\\Infantry\\"
MI = "Data\\INI\\MappedImages\\HandCreated\\KwaiInfantryMappedImages.INI"

EXPECT_OWNERS = {
    CS: "zzz-ZZZZZZZKwaiPDL.big", CB: "zzz-ZZZZZZZKwaiPDL.big",
    UPG: "zzz-ZZZZZZZKwaiPDL.big", OCL: "zzz-ZZZZZZZKwaiPDL.big",
    WEA: "zzz-ZZZZZZZKwaiPDL.big", STR: "zzz-ZZZZZZZKwaiPDL.big",
    ARM: "zzz-ZZZZChaosUnits.big", LOC: "zzz-ZZZZChaosUnits.big",
    FXL: "zzz-ZZZZChaosUnits.big", PSY: "zzz-ZZZZChaosUnits.big",
    SPW: "zzz-ZZZZZZKwaiUAV.big",
    VOI: "zz_SPE_Shw_ini.big", SFX: "zz_SPE_Shw_ini.big",
    # donor object files (read-only, drift guards)
    "Data\\INI\\Object\\China\\SpecialWeapons\\Infantry\\FlameThrower.ini":
        "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Infantry\\Infantry\\MiniGunner.ini":
        "zz_SPE_Shw_ini.big",
    IP + "SiegeSoldier.ini": "zzz-ZZZZZKwaiRoster.big",
}
NEW_INI_PATHS = [
    IP + "FlameTrooper.ini", IP + "MiniGunner.ini",
    IP + "Sharpshooter.ini", IP + "SharpshooterSupport.ini", MI,
]
NEW_IDENTIFIERS = [
    "Tank_ChinaInfantryFlameThrower", "Tank_ChinaInfantryMiniGunner",
    "Tank_ChinaInfantrySharpshooter",
    "Tank_Command_ConstructChinaInfantryFlameThrower",
    "Tank_Command_ConstructChinaInfantryMiniGunner",
    "Tank_Command_ConstructChinaInfantrySharpshooter",
]

# ------------------------------------------------------------- ZHE port set
# 176 blocks (see work/portset.py trace) shipped verbatim under donor names.
PORT = {  # dest file -> [(block type, name), ...] appended in this order
    CS: [("CommandSet", n) for n in [
        "ChinaInfantrySharpshooterCommandSet",
        "ChinaInfantrySharpshooterPronedCommandSet",
        "ChinaInfantrySharpshooterAPUpgradedCommandSet",
        "ChinaInfantrySharpshooterAPUpgradedPronedCommandSet"]],
    CB: [("CommandButton", n) for n in [
        "Command_CaptureBuildingDefault", "Command_CaptureBuildingDefaultDisabled",
        "Command_ChinaInfantrySharpshooterProne",
        "Command_ChinaInfantrySharpshooterStand",
        "Command_ChinaInfantrySharpshooterThrowGrenade",
        "Command_ChinaInfantrySharpshooterAreaReconnaissance",
        "Command_UpgradeType66APMine",
        "Command_ChinaInfantrySharpshooterUpgraded1Prone",
        "Command_ChinaInfantrySharpshooterUpgraded1Stand",
        "Command_ChinaInfantrySharpshooterLayMine"]],
    UPG: [("Upgrade", n) for n in [
        "Upgrade_APMineWeaponUpgrade", "Upgrade_ChinaRevolutionaryHeroism"]],
    OCL: [("ObjectCreationList", n) for n in [
        "OCL_AreaReconnaissanceObject", "OCL_ChinaInfantrySharpshooter_PronedWounded",
        "OCL_ChinaInfantrySharpshooter_Revived", "OCL_ChinaInfantrySharpshooter_Wounded",
        "OCL_DeleteMeOutside", "OCL_FusedType86Grenade", "OCL_FusedType86Grenade_Float",
        "OCL_GenericBulletWaterChecker", "OCL_GenericGrenadeWaterChecker_MildSuppressive",
        "OCL_GenericGrenadeWaterChecker_MildSuppressive_Float",
        "OCL_InfantryDeadExplosion", "OCL_InfantryWaterChecker", "OCL_Type66ClaymoreMine",
        "OCL_UpgradeViaRiderSwitch1", "OCL_UpgradeViaRiderSwitch2",
        "OCL_UpgradeViaRiderSwitch3", "OCL_UpgradeViaRiderSwitch4"]],
    WEA: [("Weapon", n) for n in [
        "10Radius_MineStackingPreventWeapon", "40Radius_MildSuppressionWeapon",
        "AreaReconnaissanceWeapon", "GenericGrenadeWaterCollideWeapon_FX",
        "GenericInfantryRiderSwitch2ResetWeapon", "GenericInfantryRiderSwitch3ResetWeapon",
        "GenericInfantryRiderSwitch4ResetWeapon", "GenericSmallArmsWaterCollideWeapon",
        "IngeniousInfantryCheckerWeapon", "IngeniousInfantryMovementWeapon",
        "PronedType79SniperRifleWeapon", "Type66ClaymoreMineLayingWeapon",
        "Type66ClaymoreMinePrimaryConeDetonationWeapon",
        "Type66ClaymoreMineRadiusDetonationWeapon",
        "Type66ClaymoreMineSecondaryConeDetonationWeapon", "Type79SniperRifleWeapon",
        "Type86GrenadeDetonationWeapon", "Type86GrenadeDetonationWeapon_Float",
        "Type86GrenadeWeapon", "UpgradeViaRiderSwitch_DeleteMeOutside"]],
    ARM: [("Armor", n) for n in [
        "HumanArmor_Brave", "UnsinkableProjectileArmor", "WaterCheckerArmor",
        "WoundedHumanArmor"]],
    LOC: [("Locomotor", n) for n in [
        "CheckerContainerLocomotor", "MidAirGrenadeLocomotor",
        "SluggishHumanLocomotor"]],
    FXL: [("FXList", n) for n in [
        "FX_BulletHit", "FX_BulletHitGround", "FX_BulletHitWater",
        "FX_ClaymorePrimaryConeDetonation", "FX_ClaymoreRadiusDetonation",
        "FX_ClaymoreSecondaryConeDetonation", "FX_GenericGrenadeExplosionHitGround",
        "FX_GenericGrenadeExplosionHitWater", "FX_GrenadeHitWater",
        "FX_HeroicType79SniperFire", "FX_InfantryDieCrushed", "FX_InfantryDieExploded",
        "FX_PronedWoundedRevived", "FX_RunOnDirt", "FX_RunOnWater",
        "FX_SmallGenericProjectileDeath", "FX_SoftGrenadeDetonation",
        "FX_SoftGrenadeDetonation_NoScorchMark", "FX_Type79SniperFire",
        "FX_WoundedRevived"]],
    PSY: [("ParticleSystem", n) for n in [
        "BloodExplodedPuddle", "BloodExplodedSplatter", "BloodPuddle", "BloodSplatter",
        "BloodTarget", "BloodTargetExploded", "BulletHit", "ClaymorePrimaryExplosion",
        "ClaymorePrimaryExplosionSmoke", "ClaymorePrimarySmokeFragments",
        "ClaymoreSecondarySmokeFragments", "FootstepLeft", "FootstepRight",
        "GenericHEMissileExplosion", "GenericMissileExplosionLenzflare",
        "GenericMissileExplosionSmoke", "GenericMissileExplosionSmokeRing",
        "GenericProjectileExplosionFragments", "GenericProjectileExplosionTrail",
        "GrenadeExplosion", "GrenadeExplosionDirtBlast", "GrenadeExplosionDirtCloud",
        "GrenadeExplosionDirtCloudUpward", "GrenadeExplosionDirtDebris",
        "GrenadeExplosionDirtSpray", "GrenadeExplosionShockwave",
        "GrenadeExplosionSmoke", "GrenadeExplosionSmokeRing",
        "GrenadeExplosionWaterBlast", "GrenadeExplosionWaterSplash",
        "GrenadeExplosionWaterSplashFoam", "GrenadeExplosionWaterSplashParticles",
        "GrenadeExplosionWaterWave", "GrenadeFlash", "GrenadeGenericTrail",
        "GrenadeImpactGreyDust", "GrenadeImpactWaterBlast", "GrenadeImpactWaterWave",
        "GrenadeSmokeFragments", "GrenadeSmokeTrail", "HeroicInfantryRifleLenzflare",
        "InfantryOverWaterSplash", "InfantryOverWaterWave", "InfantryRifleLenzflare",
        "SmallArmsImpactDirtBlast", "SmallArmsImpactWaterBlast",
        "SmallArmsImpactWaterWave"]],
    SPW: [("SpecialPower", n) for n in [
        "SpecialAbilityCaptureBuilding", "SpecialAbilityDisabledDummy",
        "SpecialAbilityProne", "SpecialAbilitySwitchToMain",
        "SpecialAbilityUpgraded1Prone", "SpecialAbilityUpgraded1SwitchToMain"]],
}
# ZHE support objects -> new file SharpshooterSupport.ini (donor order)
SUPPORT_OBJECTS = [
    ("Object", "GenericBullet"), ("Object", "GenericBulletWaterChecker"),
    ("Object", "GenericProjectile"), ("Object", "DummyInvisibleGroundCollider"),
    ("Object", "GenericGrenadeWaterChecker"), ("Object", "InfantryWaterChecker"),
    ("Object", "UpgradeViaRiderSwitch1"), ("Object", "UpgradeViaRiderSwitch2"),
    ("Object", "UpgradeViaRiderSwitch3"), ("Object", "UpgradeViaRiderSwitch4"),
    ("Object", "AreaReconnaissanceObject_InvisibleMarker"),
    ("Object", "40Radius_MildSuppressionObject"),
    ("Object", "Type86Grenade"), ("Object", "FusedType86Grenade"),
    ("Object", "FusedType86Grenade_Float"), ("Object", "Type66ClaymoreMine"),
]
SHARPSHOOTER_FAMILY = [  # everything in ZHE's Sharpshooter.ini, donor order
    ("Object", "ChinaInfantrySharpshooter"),
    ("Object", "ChinaInfantrySharpshooterVariation1"),
    ("ObjectReskin", "ChinaInfantrySharpshooterVariation2"),
    ("ObjectReskin", "ChinaInfantrySharpshooterVariation3"),
    ("ObjectReskin", "ChinaInfantrySharpshooterVariation4"),
    ("Object", "ChinaInfantrySharpshooter_Wounded"),
    ("Object", "ChinaInfantrySharpshooter_WoundedVariation1"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_WoundedVariation2"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_WoundedVariation3"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_WoundedVariation4"),
    ("Object", "ChinaInfantrySharpshooter_PronedWounded"),
    ("Object", "ChinaInfantrySharpshooter_PronedWoundedVariation1"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_PronedWoundedVariation2"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_PronedWoundedVariation3"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_PronedWoundedVariation4"),
]
# MappedImages ported (cameo pages re-shipped under new names; SSCaptureBuilding
# already exists in ShockWave and is reused, NOT ported)
PORT_IMAGES = ["SNSharpshooter", "SNSharpshooter_L", "SNType66Claymore",
               "SNType66ClaymorePlant", "SNType86", "SNRevolutionaryHeroism",
               "SSBinocular", "SSProneStealthed", "SSStand"]
PAGE_RENAME = {  # ZHE cameo page -> our collision-free name (512x512 SD pages)
    "SNNUserInterface512_004.tga": "KwaiZheSNN512_004.tga",
    "SNNUserInterface512_005.tga": "KwaiZheSNN512_005.tga",
    "SNNUserInterface512_006.tga": "KwaiZheSNN512_006.tga",
    "SNSUserInterface512_002.tga": "KwaiZheSNS512_002.tga",
}
# strings ported from ZHE generals.str (missing from ours; asserted)
PORT_STRINGS = [
    "OBJECT:Sharpshooter", "OBJECT:Type66ClaymoreMine",
    "CONTROLBAR:ConstructChinaInfantrySharpshooter",
    "CONTROLBAR:ToolTipChinaBuildSharpshooter",
    "CONTROLBAR:AreaReconnaissance", "CONTROLBAR:ToolTipAreaReconnaissance",
    "CONTROLBAR:LayType66ClaymoreAtPosition",
    "CONTROLBAR:ToolTipLayType66ClaymoreAtPosition",
    "CONTROLBAR:Prone", "CONTROLBAR:ToolTipInfantryProne",
    "CONTROLBAR:StandUp", "CONTROLBAR:ToolTipInfantryStandUp",
    "CONTROLBAR:ThrowType86PGrenade", "CONTROLBAR:ToolTipThrowType86PGrenade",
    "CONTROLBAR:UpgradeType66Claymore", "CONTROLBAR:TooltipUpgradeType66Claymore",
    "UPGRADE:ChinaAPMineWeapon", "UPGRADE:ChinaRevolutionaryHeroism",
]
W3D_FILES = [  # 47: 12 models/skins + skeleton's 36 animation files (traced)
    "CISPINF_SKL", "EXIndAPMine", "EXIndGnd", "EXInfSnp", "EXInfSnpAP",
    "EXWounded", "NIMRKMN01_SKN", "NIMRKMN02_SKN", "NIMRKMN03_SKN",
    "NIMRKMN04_SKN", "NIType66Mine", "NIType86",
    "CISPINF_ATA", "CISPINF_ATG1", "CISPINF_ATG2", "CISPINF_ATP",
    "CISPINF_ATR1", "CISPINF_ATR2", "CISPINF_ATR3", "CISPINF_BTA",
    "CISPINF_BTP", "CISPINF_DTA", "CISPINF_DTB", "CISPINF_DTC",
    "CISPINF_F2S", "CISPINF_FDTA", "CISPINF_FDTB", "CISPINF_FDTC",
    "CISPINF_FTA", "CISPINF_ML1", "CISPINF_ML2", "CISPINF_P2A",
    "CISPINF_PDTA", "CISPINF_PDTB", "CISPINF_PDTC", "CISPINF_PTD",
    "CISPINF_RNA", "CISPINF_RNB", "CISPINF_RNC", "CISPINF_RNP",
    "CISPINF_RTA", "CISPINF_RTP", "CISPINF_S2A", "CISPINF_S2F",
    "CISPINF_S2P", "CISPINF_S2R", "CISPINF_STD",
]


# ---------------------------------------------------------------- helpers
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(s):
    return s.replace("\r\n", "\n")


def from_lf(s, eol):
    return s.replace("\n", eol) if eol != "\n" else s


def lf_text(b):
    return to_lf(b.decode("latin-1"))


def replace_exact(s, old, new, count, what=""):
    got = s.count(old)
    assert got == count, "%s: expected %d of %r..., found %d" % (
        what, count, old[:80], got)
    return s.replace(old, new)


WORD = re.compile(r"[0-9A-Za-z_][A-Za-z0-9_\-]*")


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i, j = line.find(";"), line.find("//")
        if i >= 0 and (j < 0 or i < j):
            line = line[:i]
        elif j >= 0:
            line = line[:j]
        out.append(line)
    return "\n".join(out)


# ------------------------------------------------------------ load sources
print("== reading effective sources from", SPE_DIR)
bigs = sorted([f for f in os.listdir(SPE_DIR) if f.lower().endswith(".big")
               and f != OUT_NAME], key=str.lower)
eff_data, eff_owner = {}, {}
for b in bigs:
    for e in read_big(os.path.join(SPE_DIR, b)):
        eff_data[e.path] = e.data
        eff_owner[e.path] = b
for p, owner in EXPECT_OWNERS.items():
    assert eff_owner.get(p) == owner, \
        "ownership drift: %s owned by %s (expected %s)" % (p, eff_owner.get(p), owner)
for p in NEW_INI_PATHS:
    assert p not in eff_data, "new path already claimed: " + p

eff_ini_texts = {p: lf_text(d) for p, d in eff_data.items()
                 if p.lower().endswith(".ini") and p.startswith("Data\\INI")}
eff_all_text = "\n".join(eff_ini_texts.values())
eff_words = set(WORD.findall(eff_all_text))
eff_defined = {}
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _txt in parse_blocks(txt):
        eff_defined.setdefault(name, set()).add(t)

print("== reading ZHE donor archives from", ZHE_DIR)
zhe_asset, zhe_ini_texts = {}, {}
for f in sorted(os.listdir(ZHE_DIR)):
    if not f.lower().endswith((".big", ".zhe")):
        continue
    try:
        entries = read_big(os.path.join(ZHE_DIR, f))
    except Exception:
        continue
    for e in entries:
        lp = e.path.lower()
        # .big (active) archives beat .zhe (inactive) EXCEPT the SD cameo set,
        # which we prefer: its 512x512 pages match the TextureSize_512 coords.
        prefer = lp not in zhe_asset or (
            f == "!ZHE8CameoSD_99.zhe" and lp.startswith("art\\textures\\sn"))
        if prefer:
            zhe_asset[lp] = (f, e.data)
        if f == "!ZHE8INI_99.big" and lp.endswith((".ini", ".str")):
            zhe_ini_texts[e.path] = lf_text(e.data)

zhe_defs = {}
for p, txt in zhe_ini_texts.items():
    for t, name, _a, _b, btext in parse_blocks(txt):
        zhe_defs.setdefault((t, name), (p, btext))


def zhe_block(typ, name):
    key = (typ, name)
    assert key in zhe_defs, "ZHE block missing: %s %s" % key
    return zhe_defs[key][1]


# our full asset space (art + audio): base game + mod dir + this archive
asset_paths = set()
for root in BASE_DIRS + [SPE_DIR]:
    for f in sorted(os.listdir(root)):
        if f.lower().endswith(".big") and f != OUT_NAME:
            for e in read_big(os.path.join(root, f)):
                asset_paths.add(e.path.lower())

# ---------------------------------------------- donor drift sanity asserts
print("== donor sanity")
DONOR_EXPECT = [
    ("Spec_ChinaInfantryFlameThrower", 350, "8.0",
     ["Spec_ChinaBarracks", "Spec_ChinaWarFactory"],
     "Data\\INI\\Object\\China\\SpecialWeapons\\Infantry\\FlameThrower.ini"),
    ("Infa_ChinaInfantryMiniGunner", 550, "14.0",
     ["Infa_ChinaBarracks"],
     "Data\\INI\\Object\\China\\Infantry\\Infantry\\MiniGunner.ini"),
]
for name, cost, btime, prereqs, path in DONOR_EXPECT:
    blk = None
    for t, n, _a, _b, btext in parse_blocks(eff_ini_texts[path]):
        if n == name:
            blk = btext
    assert blk, name
    m = re.search(r"(?m)^\s*BuildCost\s*=\s*(\d+)", blk)
    assert m and int(m.group(1)) == cost, (name, "cost", m and m.group(1))
    m = re.search(r"(?m)^\s*BuildTime\s*=\s*(\S+)", blk)
    assert m and m.group(1) == btime, (name, "time", m and m.group(1))
    pm = re.search(r"(?ms)^\s*Prerequisites\s*\n(.*?)^\s*End", blk)
    got = [t for line in re.findall(r"(?m)^\s*Object\s*=\s*(.+?)\s*$", pm.group(1))
           for t in line.split()]
    assert got == prereqs, (name, "prereqs", got)
# ZHE sharpshooter donor cost
ss_stub_donor = zhe_block("Object", "ChinaInfantrySharpshooter")
assert re.search(r"(?m)^\s*BuildCost\s*=\s*1200\s*$", ss_stub_donor)
assert re.search(r"(?m)^\s*BuildTime\s*=\s*30\.0\s*$", ss_stub_donor)
# prereq targets we translate TO all exist
for n in ("Tank_ChinaBarracks", "Tank_ChinaWarFactory", "Tank_ChinaPropagandaCenter"):
    assert "Object" in eff_defined.get(n, set()), "missing Kwai building: " + n

# ------------------------------------------- identifier collision checks
port_names = sorted({n for lst in PORT.values() for _t, n in lst}
                    | {n for _t, n in SUPPORT_OBJECTS}
                    | {n for _t, n in SHARPSHOOTER_FAMILY}
                    | set(PORT_IMAGES))
for n in NEW_IDENTIFIERS:
    assert n not in eff_words, "identifier collision (new): " + n
for n in port_names:
    assert n not in eff_words, "identifier collision (ported donor name): " + n

# =========================================================== ported text
def ported_appendix(dest, title):
    blocks = []
    for t, n in PORT[dest]:
        blk = zhe_block(t, n).rstrip("\n") + "\n"
        if n == "OCL_ChinaInfantrySharpshooter_Revived":
            # repoint at the renamed buildable stub (donor spawned its own
            # stub object name, which we rename)
            blk = replace_exact(
                blk, "    ObjectNames = ChinaInfantrySharpshooter\n",
                "    ObjectNames = Tank_ChinaInfantrySharpshooter ; " + TAG +
                " (donor: ChinaInfantrySharpshooter)\n", 1, "revive OCL")
        blocks.append(blk)
    return ("\n;;; %s: %s (ported verbatim from Zero Hour Enhanced "
            "!ZHE8INI_99.big;\n;;; ZHE Sharpshooter closure -- see README)\n\n"
            % (TAG, title) + "\n".join(blocks))


# --- transforms applied to ported text (documented deviations)
def fix_sniper_distant(txt):
    # ZHE typo: sample 'kar98-l-3' does not exist (file is kar98-l-03.wav)
    return replace_exact(
        txt, "  Sounds = kar98-l-01 kar98-l-02 kar98-l-3\n",
        "  Sounds = kar98-l-01 kar98-l-02 kar98-l-03 ; %s: ZHE typo kar98-l-3 fixed\n" % TAG,
        1, "Type79SniperRifleDistant")


def build_sharpshooter_ini():
    """Full copy of ZHE's Sharpshooter.ini with the buildable stub renamed
    Tank_ChinaInfantrySharpshooter / Side ChinaTankGeneral / Kwai prereqs."""
    src = zhe_ini_texts["Data\\INI\\Object\\China\\Infantry\\Sharpshooter.ini"]
    out = src
    out = replace_exact(out, "Object ChinaInfantrySharpshooter\n",
                        "Object Tank_ChinaInfantrySharpshooter ; " + TAG +
                        ": renamed ZHE ChinaInfantrySharpshooter (buildable stub)\n",
                        1, "stub rename")
    # stub block only: donor 'Side = China' occurs in stub, Variation1, and
    # the two wounded Variation1 objects (4 total); the stub's is the FIRST.
    stub_end = out.index("\nEnd\n", out.index("Object Tank_ChinaInfantrySharpshooter"))
    stub_txt = out[:stub_end + 5]
    rest = out[stub_end + 5:]
    stub_txt = replace_exact(
        stub_txt, "  Side = China\n",
        "  Side = ChinaTankGeneral ; " + TAG + " (donor: China)\n", 1, "stub side")
    stub_txt = replace_exact(
        stub_txt,
        "  Prerequisites\n    Object = ChinaBarracks\n  End\n",
        "  Prerequisites\n"
        "    Object = Tank_ChinaBarracks ; " + TAG + " (donor: ChinaBarracks)\n"
        "    Object = Tank_ChinaPropagandaCenter ; " + TAG +
        ": spec adds the Propaganda Center gate\n  End\n", 1, "stub prereqs")
    header = ("; %s: FULL PORT of Zero Hour Enhanced's ChinaInfantrySharpshooter\n"
              "; ($1200 / 30 s China sniper).  Only the buildable stub is renamed\n"
              "; (Tank_..., Side, prerequisites); the 4 build variations, wounded\n"
              "; bodies and all referenced support blocks keep their ZHE donor names\n"
              "; (collision-checked).  Source: ZHE_BIG100a !ZHE8INI_99.big\n"
              "; Data\\INI\\Object\\China\\Infantry\\Sharpshooter.ini.\n\n" % TAG)
    return header + stub_txt + rest


def build_support_ini():
    blocks = []
    for t, n in SUPPORT_OBJECTS:
        src_path = zhe_defs[(t, n)][0]
        blocks.append("; from ZHE %s\n%s" % (src_path, zhe_block(t, n).rstrip("\n") + "\n"))
    return ("; %s: ZHE generic support objects required by the Sharpshooter port\n"
            "; (projectiles, water checkers, prone rider-switch riders, grenade,\n"
            "; claymore mine, recon marker, suppression pulse).  Ported verbatim\n"
            "; under donor names from ZHE_BIG100a !ZHE8INI_99.big.\n\n" % TAG
            + "\n".join(blocks))


def build_mapped_images():
    out = ["; %s: ZHE cameo art for the Sharpshooter port.  The ZHE 512x512 SD\n"
           "; cameo pages are shipped under NEW texture names (ShockWave has its\n"
           "; own, different SNN/SNS pages under the original names).\n" % TAG]
    for n in PORT_IMAGES:
        blk = zhe_block("MappedImage", n)
        for old, new in PAGE_RENAME.items():
            blk = blk.replace("Texture = " + old, "Texture = " + new)
        m = re.search(r"(?m)^\s*Texture\s*=\s*(\S+)", blk)
        assert m and m.group(1) in PAGE_RENAME.values(), (n, m and m.group(1))
        out.append(blk.rstrip("\n") + "\n")
    return "\n".join(out)


# ---------------------------------------------------------------- stubs
def stub(name, comment, portrait, image, model, cost, btime, prereqs, variation,
         kindof):
    return ("; %s: build stub letting China's Tank General (Kwai) produce\n"
            "; %s\n"
            "; Same BuildVariations idiom ShockWave uses for Tank_ChinaVehicleHackerVan\n"
            "; and AirF_AmericaInfantryPathfinder (kwai-roster/kwai-artillery pattern).\n"
            "\n"
            "Object %s\n"
            "\n"
            "  ; *** ART Parameters ***\n"
            "  SelectPortrait         = %s\n"
            "  ButtonImage            = %s\n"
            "\n"
            "  Draw = W3DModelDraw ModuleTag_01\n"
            "    OkToChangeModelColor  = Yes\n"
            "    DefaultConditionState\n"
            "      Model               = %s\n"
            "    End\n"
            "  End\n"
            "\n"
            "  ; set cost and time fields here or else they won't work\n"
            "  BuildCost       = %d\n"
            "  BuildTime       = %s          ;in seconds\n"
            "\n"
            "  Prerequisites\n%s"
            "  End\n"
            "\n"
            "  Side = ChinaTankGeneral\n"
            "  EditorSorting = INFANTRY\n"
            "  BuildVariations = %s\n"
            "\n"
            "  KindOf = %s\n"
            "\nEnd\n" % (TAG, comment, name, portrait, image, model, cost,
                         btime, "".join("    Object = %s\n" % p for p in prereqs),
                         variation, kindof))


STUBS = {
    IP + "FlameTrooper.ini": stub(
        "Tank_ChinaInfantryFlameThrower",
        "Leang's Flame Trooper (Spec_ChinaInfantryFlameThrower; donor prereqs\n"
        "; Spec_ChinaBarracks + Spec_ChinaWarFactory translated to Tank_).",
        "SNFlameTrooper_L", "SNFlameTrooper", "NIPYRO_SKN",
        350, "8.0", ["Tank_ChinaBarracks", "Tank_ChinaWarFactory"],
        "Spec_ChinaInfantryFlameThrower",
        "PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE"),
    IP + "MiniGunner.ini": stub(
        "Tank_ChinaInfantryMiniGunner",
        "Fai's Minigunner (Infa_ChinaInfantryMiniGunner; donor prereq\n"
        "; Infa_ChinaBarracks translated to Tank_ChinaBarracks).",
        "SNMiniGunner_L", "SNMiniGunner", "NICNSCI_SKN",
        550, "14.0", ["Tank_ChinaBarracks"],
        "Infa_ChinaInfantryMiniGunner",
        "PRELOAD SELECTABLE CAN_ATTACK ATTACK_NEEDS_LINE_OF_SIGHT "
        "CAN_CAST_REFLECTIONS INFANTRY SCORE PARACHUTABLE"),
}

# =========================================================== CommandSet.ini
BAR_ANCHOR = "  5 = Tank_Command_ConstructChinaInfantrySiegeSoldier ; zzz-ZZZZZKwaiRoster\n"
BAR_ADD = (
    "  6 = Tank_Command_ConstructChinaInfantryFlameThrower ; " + TAG + "\n"
    "  7 = Tank_Command_ConstructChinaInfantryMiniGunner ; " + TAG + "\n"
    "  8 = Tank_Command_ConstructChinaInfantrySharpshooter ; " + TAG + "\n")


def patch_commandset(lf):
    assert lf.count(BAR_ANCHOR) == 2  # both Barracks set variants
    lf = replace_exact(lf, BAR_ANCHOR, BAR_ANCHOR + BAR_ADD, 2, "Barracks 6-8")
    return lf + ported_appendix(CS, "Sharpshooter command sets")


# ========================================================= CommandButton.ini
BTN_APPENDIX = "".join("""\
CommandButton Tank_Command_Construct%s
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = %s
  TextLabel     = CONTROLBAR:%s
  ButtonImage   = %s
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:%s
End

""" % row for row in [
    ("ChinaInfantryFlameThrower", "Tank_ChinaInfantryFlameThrower",
     "ConstructChinaInfantryFlameTrooper", "SNFlameTrooper",
     "ToolTipChinaBuildFlameTrooper"),
    ("ChinaInfantryMiniGunner", "Tank_ChinaInfantryMiniGunner",
     "ConstructChinaInfantryMiniGunner", "SNMiniGunner",
     "ToolTipChinaBuildMiniGunner"),
    ("ChinaInfantrySharpshooter", "Tank_ChinaInfantrySharpshooter",
     "ConstructChinaInfantrySharpshooter", "SNSharpshooter",
     "ToolTipChinaBuildSharpshooter"),
])


def patch_commandbutton(lf):
    if not lf.endswith("\n"):
        lf += "\n"
    return (lf + "\n;;; " + TAG + ": construct buttons (Flame Trooper / "
            "Minigunner reuse donor art+labels; Sharpshooter uses ported ZHE "
            "art+labels)\n" + BTN_APPENDIX + ported_appendix(
                CB, "Sharpshooter ability buttons"))


# ============================================================== Generals.str
def zhe_str_entry(label, zstr_lf):
    m = re.search(r"(?ms)^%s[ \t]*\n(.*?)^END[ \t]*$" % re.escape(label), zstr_lf,
                  re.I)
    assert m, "ZHE string missing: " + label
    return "%s\n%sEND\n" % (label, m.group(1))


def patch_str(lf, zstr_lf):
    ours = set(re.findall(r"(?mi)^((?:CONTROLBAR|OBJECT|UPGRADE|SCIENCE|TOOLTIP|GUI):[A-Za-z0-9_\-]+)[ \t]*$", lf))
    for lab in PORT_STRINGS:
        assert lab not in ours, "string already present (would duplicate): " + lab
    add = "\n".join(zhe_str_entry(lab, zstr_lf) for lab in PORT_STRINGS)
    if not lf.endswith("\n"):
        lf += "\n"
    return (lf + "\n// " + TAG + ": ZHE Sharpshooter strings (ported from "
            "Zero Hour Enhanced generals.str)\n\n" + add)


# ============================================================== audio port
# every audio event referenced by shipped text that is missing from our
# effective space is ported from ZHE (Voice.ini events -> our Voice.ini,
# SoundEffects.ini events -> our SoundEffects.ini) with its sample files.
AUDIO_FIELD_RE = re.compile(
    r"^\s*(?:Voice[A-Za-z]*|Sound(?:MoveStart|OnDamaged|OnReallyDamaged|Created|"
    r"Ambient[A-Za-z]*|StealthOn|StealthOff|FX)?|UnitSpecificSound|InitiateSound|"
    r"FireSound|ProjectileSound|ResearchSound|BounceSound)\s*=\s*([A-Za-z0-9_\-]+)\s*$",
    re.I | re.M)
AUDIO_NONE = {"NoSound", "None", "NONE"}


def collect_audio_refs(texts):
    refs = set()
    for txt in texts:
        nc = strip_comments(txt)
        for m in AUDIO_FIELD_RE.finditer(nc):
            v = m.group(1)
            if v not in AUDIO_NONE:
                refs.add(v)
        # FXList / AudioEvent internal sound refs
        for m in re.finditer(r"(?ms)^\s*Sound\s*\n\s*Name\s*=\s*(\S+)", nc):
            refs.add(m.group(1))
    return refs


# =========================================================== build the text
print("== composing")
out_files = {}
zstr_lf = lf_text(next(d for p, d in (
    (e.path, e.data) for f in ["!ZHE8Language_99.big"]
    for e in read_big(os.path.join(ZHE_DIR, f))) if p.lower() == "data\\generals.str"))

sources = {}
for p in (CS, CB, UPG, OCL, WEA, STR, ARM, LOC, FXL, PSY, SPW, VOI, SFX):
    raw = eff_data[p].decode("latin-1")
    sources[p] = (to_lf(raw), eol_of(raw))

cs_new = patch_commandset(sources[CS][0])
cb_new = patch_commandbutton(sources[CB][0])
str_new = patch_str(sources[STR][0], zstr_lf)
appended = {UPG: ported_appendix(UPG, "Sharpshooter upgrades"),
            OCL: ported_appendix(OCL, "Sharpshooter OCLs"),
            WEA: ported_appendix(WEA, "Sharpshooter weapons"),
            ARM: ported_appendix(ARM, "Sharpshooter armors"),
            LOC: ported_appendix(LOC, "Sharpshooter locomotors"),
            FXL: ported_appendix(FXL, "Sharpshooter FX lists"),
            PSY: ported_appendix(PSY, "Sharpshooter particle systems"),
            SPW: ported_appendix(SPW, "Sharpshooter special powers")}

new_texts = {CS: cs_new, CB: cb_new, STR: str_new}
for p, app in appended.items():
    base = sources[p][0]
    if not base.endswith("\n"):
        base += "\n"
    new_texts[p] = base + app

ss_ini = build_sharpshooter_ini()
support_ini = build_support_ini()
mi_ini = build_mapped_images()
new_texts[IP + "Sharpshooter.ini"] = ss_ini
new_texts[IP + "SharpshooterSupport.ini"] = support_ini
new_texts[IP + "FlameTrooper.ini"] = STUBS[IP + "FlameTrooper.ini"]
new_texts[IP + "MiniGunner.ini"] = STUBS[IP + "MiniGunner.ini"]
new_texts[MI] = mi_ini

# ONLY the text this layer adds (closure checks must not re-audit the
# pre-existing effective content our patched copies embed)
new_content = [BAR_ADD, BTN_APPENDIX, ss_ini, support_ini, mi_ini,
               STUBS[IP + "FlameTrooper.ini"], STUBS[IP + "MiniGunner.ini"]] + \
              [ported_appendix(p, "x") for p in PORT]

# ---- audio events: decide port set mechanically over the NEW ini text
shipped_ini_texts = new_content
eff_audio = set()
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _tx in parse_blocks(txt):
        if t in ("AudioEvent", "DialogEvent", "MusicTrack"):
            eff_audio.add(name)

audio_needed = collect_audio_refs(shipped_ini_texts)
ported_audio_blocks = {VOI: [], SFX: []}
audio_done, audio_reused = set(), set()
frontier = sorted(audio_needed)
while frontier:
    ev = frontier.pop()
    if ev in audio_done:
        continue
    audio_done.add(ev)
    if ev in eff_audio:
        audio_reused.add(ev)
        continue
    src = zhe_defs.get(("AudioEvent", ev))
    assert src, "audio event unresolved anywhere: " + ev
    src_path, blk = src
    if src_path.lower().endswith("voice.ini"):
        ported_audio_blocks[VOI].append((ev, blk))
    else:
        ported_audio_blocks[SFX].append((ev, blk))

for p, title in ((VOI, "Sharpshooter voice set"), (SFX, "Sharpshooter sound effects")):
    blocks = []
    for ev, blk in sorted(ported_audio_blocks[p]):
        if ev == "Type79SniperRifleDistant":
            blk = fix_sniper_distant(blk)
        blocks.append(blk.rstrip("\n") + "\n")
    base = sources[p][0]
    if not base.endswith("\n"):
        base += "\n"
    new_texts[p] = base + ("\n;;; %s: %s (ported from Zero Hour Enhanced)\n\n"
                           % (TAG, title)) + "\n".join(blocks)

# ---- audio samples: ship every sample of ported events missing from ours
def event_samples(blk):
    s = set()
    nc = strip_comments(blk)
    for key in ("Sounds", "Attack", "Decay"):
        for m in re.finditer(r"(?m)^\s*%s\s*=\s*(.+?)\s*$" % key, nc):
            s.update(m.group(1).split())
    return s


audio_files = {}
for p in (VOI, SFX):
    for ev, blk in ported_audio_blocks[p]:
        if ev == "Type79SniperRifleDistant":
            blk = fix_sniper_distant(blk)
        for smp in event_samples(blk):
            lp = smp.lower()
            dst = "Data\\Audio\\Sounds\\%s.wav" % smp
            if any(("data\\audio\\sounds\\%s%s.wav" % (pre, lp)) in asset_paths
                   for pre in ("", "english\\")):
                continue  # exists in our space (base or mod)
            # ZHE source: flat or localized English folder
            src = None
            for cand in ("data\\audio\\sounds\\%s.wav" % lp,
                         "data\\audio\\sounds\\english\\%s.wav" % lp):
                if cand in zhe_asset:
                    src = zhe_asset[cand][1]
                    break
            assert src is not None, "audio sample missing in ZHE: " + smp
            audio_files[dst] = src

# ---- art: W3D files + their internal textures + particle/cameo textures
art_files = {}
for m in W3D_FILES:
    lp = "art\\w3d\\%s.w3d" % m.lower()
    assert lp not in asset_paths, "W3D collision with our space: " + m
    assert lp in zhe_asset, "W3D missing in ZHE: " + m
    art_files["Art\\W3D\\%s.W3D" % m] = zhe_asset[lp][1]

texre = re.compile(rb"[A-Za-z0-9_\-]+\.(?:tga|dds)", re.I)
tex_needed = set()
for m in W3D_FILES:
    for t in texre.findall(art_files["Art\\W3D\\%s.W3D" % m]):
        tex_needed.add(t.decode().lower())
for txt in shipped_ini_texts:
    for m in re.finditer(r"(?m)^\s*ParticleName\s*=\s*(\S+)", strip_comments(txt)):
        tex_needed.add(m.group(1).lower())


def tex_in_ours(base):
    return any(("art\\textures\\%s%s" % (base, ext)) in asset_paths
               for ext in (".tga", ".dds"))


for t in sorted(tex_needed):
    base = t.rsplit(".", 1)[0]
    if tex_in_ours(base):
        continue
    src = None
    for ext in (".dds", ".tga"):
        lp = "art\\textures\\%s%s" % (base, ext)
        if lp in zhe_asset:
            src = (lp, zhe_asset[lp][1])
            break
    assert src, "texture missing everywhere: " + t
    art_files["Art\\Textures\\" + src[0].split("\\")[-1]] = src[1]

# cameo pages (renamed, SD 512x512 variants preferred at load above)
for old, new in PAGE_RENAME.items():
    lp = "art\\textures\\" + old.lower()
    assert lp in zhe_asset, "cameo page missing in ZHE: " + old
    arc, data = zhe_asset[lp]
    assert arc == "!ZHE8CameoSD_99.zhe", (old, arc)
    import struct
    w, h = struct.unpack_from("<HH", data, 12)
    assert (w, h) == (512, 512), (old, w, h)
    newlp = "art\\textures\\" + new.lower()
    assert newlp not in asset_paths, "renamed page collides: " + new
    art_files["Art\\Textures\\" + new] = data

out_files = {}
for p, txt in new_texts.items():
    eol = sources[p][1] if p in sources else "\n"
    out_files[p] = from_lf(txt, eol).encode("latin-1")
out_files.update(art_files)
out_files.update(audio_files)

# ========================================================== VERIFICATION
print("== verifying")

# ---- 1. append-only + exact CS diff -----------------------------------
for p in (CB, UPG, OCL, WEA, ARM, LOC, FXL, PSY, SPW, VOI, SFX, STR):
    base_raw = eff_data[p]
    assert out_files[p].startswith(base_raw.rstrip(b"\r\n")), \
        "not append-only: " + p
cs_diff = [l for l in difflib.unified_diff(
    sources[CS][0].split("\n"), cs_new.split("\n"), lineterm="", n=0)
    if not l.startswith(("---", "+++", "@@"))]
removed = [l for l in cs_diff if l.startswith("-")]
added = Counter(l[1:] for l in cs_diff if l.startswith("+"))
assert not removed, removed[:5]
exp_added = Counter(BAR_ADD.rstrip("\n").split("\n") * 2)
exp_added.update(ported_appendix(CS, "Sharpshooter command sets").rstrip("\n").split("\n"))
assert added == exp_added, (added - exp_added, exp_added - added)
print("   CommandSet diff: +%d lines, -0, as intended" % sum(added.values()))

# ---- 2. block balance ---------------------------------------------------
EXPECT_NEW_BLOCKS = {CS: 4, CB: 13, UPG: 2, OCL: 17, WEA: 20, ARM: 4, LOC: 3,
                     FXL: 20, PSY: 47, SPW: 6,
                     VOI: len(ported_audio_blocks[VOI]),
                     SFX: len(ported_audio_blocks[SFX])}
for p, n in EXPECT_NEW_BLOCKS.items():
    got = len(parse_blocks(new_texts[p])) - len(parse_blocks(sources[p][0]))
    assert got == n, (p, got, n)
for p, n in ((IP + "Sharpshooter.ini", 15), (IP + "SharpshooterSupport.ini", 16),
             (IP + "FlameTrooper.ini", 1), (IP + "MiniGunner.ini", 1)):
    blocks = parse_blocks(new_texts[p])
    assert len(blocks) == n, (p, len(blocks), n)
    col0 = sum(1 for l in new_texts[p].split("\n")
               if l.rstrip() == "End" and not l.startswith((" ", "\t")))
    assert col0 == n, (p, col0)
mi_blocks = parse_blocks(new_texts[MI])
assert len(mi_blocks) == len(PORT_IMAGES) and \
    {n for _t, n, _a, _b, _x in mi_blocks} == set(PORT_IMAGES)

# ---- 3. full effective-space closure ------------------------------------
print("   closure ...")
final_texts = dict(eff_ini_texts)
for p, txt in new_texts.items():
    if p.lower().endswith(".ini"):
        final_texts[p] = txt
final_defined = {}
for p, txt in final_texts.items():
    for t, name, _a, _b, _tx in parse_blocks(txt):
        final_defined.setdefault(name, set()).add(t)
# renamed stub defined exactly once, donor family present
assert final_defined["Tank_ChinaInfantrySharpshooter"] == {"Object"}
assert "ChinaInfantrySharpshooter" not in final_defined  # rename complete
for _t, n in SHARPSHOOTER_FAMILY[1:]:
    assert n in final_defined, n
for _t, n in SUPPORT_OBJECTS:
    assert n in final_defined, n
for _dst, lst in PORT.items():
    for _t, n in lst:
        assert n in final_defined, "ported block lost: " + n

shipped_all = "\n".join(new_content + [new_texts[VOI][len(sources[VOI][0]):],
                                       new_texts[SFX][len(sources[SFX][0]):]])
REF_RULES = [
    (r"^\s*ProjectileObject\s*=\s*(\S+)", "Object"),
    (r"^\s*ObjectNames\s*=\s*(.+?)\s*$", "Object"),
    (r"^\s*SpawnTemplateName\s*=\s*(\S+)", "Object"),
    (r"^\s*BuildVariations\s*=\s*(.+?)\s*$", "Object"),
    (r"^\s*Object\s*=\s*([A-Za-z0-9_ \t]+?)\s*$", "Object"),
    (r"^\s*Weapon\s*=\s*(?:PRIMARY|SECONDARY|TERTIARY|INITIAL|MIDPOINT|FINAL)\s+(\S+)", "Weapon"),
    (r"^\s*(?:Collide|Reaction)Weapon\w*\s*=\s*(\S+)", "Weapon"),
    (r"^\s*Armor\s*=\s*([A-Za-z]\S*Armor)\s*$", "Armor"),
    (r"^\s*Locomotor\s*=\s*SET_\w+\s+(.+?)\s*$", "Locomotor"),
    (r"^\s*(?:Fire)?FX\s*=\s*(?:INITIAL\s+|MIDPOINT\s+|FINAL\s+)?(FX_\S+)", "FXList"),
    (r"^\s*ProjectileDetonationFX\s*=\s*(\S+)", "FXList"),
    (r"^\s*VeterancyFireFX\s*=\s*HEROIC\s+(\S+)", "FXList"),
    (r"^\s*(?:Fire|ProjectileDetonation)OCL\s*=\s*(\S+)", "ObjectCreationList"),
    (r"^\s*OCL\s*=\s*(?:INITIAL\s+|MIDPOINT\s+|FINAL\s+)?(OCL_\S+)", "ObjectCreationList"),
    (r"^\s*UpgradeObject\s*=\s*(\S+)", "ObjectCreationList"),
    (r"^\s*SpecialPower(?:Template)?\s*=\s*(\S+)", "SpecialPower"),
    (r"^\s*CommandSet\s*=\s*(\S+)", "CommandSet"),
    (r"^\s*Upgrade\s*=\s*(Upgrade_\S+)", "Upgrade"),
    (r"^\s*(?:TriggeredBy|ConflictsWith|RemovesUpgrades)\s*=\s*(.+?)\s*$", "Upgrade"),
    (r"^\s*ParticleSysBone\s*=\s*\S+\s+(\S+)", "ParticleSystem"),
]
unresolved = []
nc_all = strip_comments(shipped_all)
for line in nc_all.split("\n"):
    for pat, want in REF_RULES:
        m = re.match(pat, line, re.I)
        if not m:
            continue
        for tok in m.group(1).split():
            if tok in ("None", "NONE", "Yes", "No"):
                continue
            kinds = final_defined.get(tok, set())
            ok = want in kinds or (want == "Object" and "ObjectReskin" in kinds) \
                or (want == "Upgrade" and kinds)
            if not ok:
                unresolved.append((want, tok, line.strip()))
        break
assert not unresolved, "unresolved refs: %s" % unresolved[:10]

# nested FXList particle systems + sounds
for m in re.finditer(r"(?ms)^\s*ParticleSystem\s*\n\s*Name\s*=\s*(\S+)", nc_all):
    assert "ParticleSystem" in final_defined.get(m.group(1), set()), m.group(1)

# every command-set slot in ported sets resolves to a defined button
def parse_sets(txt):
    sets = {}
    for t, name, _a, _b, btext in parse_blocks(txt):
        if t != "CommandSet":
            continue
        slots = {}
        for sm in re.finditer(r"(?m)^\s*(\d+)\s*=\s*(\S+)", btext):
            slots[int(sm.group(1))] = sm.group(2)
        sets[name] = slots
    return sets


sets = parse_sets(cs_new)
for _t, n in PORT[CS]:
    for slot, btn in sets[n].items():
        assert 1 <= slot <= 18, (n, slot)
        assert "CommandButton" in final_defined.get(btn, set()), (n, btn)

# rider-switch chain closure on the ported unit
var1 = zhe_block("Object", "ChinaInfantrySharpshooterVariation1")
for rid in re.finditer(r"(?m)^\s*Rider\d\s*=\s*(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)", var1):
    assert "Object" in final_defined.get(rid.group(1), set()), rid.group(1)
    assert "CommandSet" in final_defined.get(rid.group(2), set()), rid.group(2)

# revive OCL points at the renamed stub
assert "ObjectNames = Tank_ChinaInfantrySharpshooter" in new_texts[OCL]
assert not re.search(r"(?m)^\s*ObjectNames\s*=\s*ChinaInfantrySharpshooter\s*$",
                     new_texts[OCL])

# ---- 4. strings ----------------------------------------------------------
str_lf = new_texts[STR]
str_defined = set(re.findall(
    r"(?mi)^((?:CONTROLBAR|OBJECT|UPGRADE|SCIENCE|TOOLTIP|GUI):[A-Za-z0-9_\-]+)[ \t]*$",
    str_lf))
lab_needed = set(re.findall(
    r"\b(?:CONTROLBAR|OBJECT|UPGRADE|SCIENCE|TOOLTIP|GUI):[A-Za-z0-9_\-]+",
    nc_all))
missing_labels = {l for l in lab_needed if l not in str_defined}
# grandfather: labels referenced by pre-existing effective text only
pre_labels = set(re.findall(
    r"\b(?:CONTROLBAR|OBJECT|UPGRADE|SCIENCE|TOOLTIP|GUI):[A-Za-z0-9_\-]+",
    strip_comments(eff_all_text)))
missing_labels -= {l for l in missing_labels if l in pre_labels and
                   l not in strip_comments(shipped_all)}
assert not missing_labels, "unresolved labels: %s" % sorted(missing_labels)
for lab in PORT_STRINGS:
    assert re.search(r"(?mi)^%s[ \t]*$" % re.escape(lab), str_lf), lab

# ---- 5. art closure -------------------------------------------------------
print("   art closure ...")
final_assets = set(asset_paths) | {p.lower() for p in out_files}


def art_ok_w3d(name):
    return ("art\\w3d\\%s.w3d" % name.lower()) in final_assets


def art_ok_tex(base):
    return any(("art\\textures\\%s%s" % (base.lower(), ext)) in final_assets
               for ext in (".tga", ".dds"))


for line in nc_all.split("\n"):
    m = re.match(r"^\s*Model\s*=\s*(\S+)", line, re.I)
    if m and m.group(1) not in ("None", "NONE"):
        assert art_ok_w3d(m.group(1)), "model missing: " + m.group(1)
    m = re.match(r"^\s*(?:Idle)?Animation\s*=\s*(\S+)\.(\S+)", line, re.I)
    if m:
        assert art_ok_w3d(m.group(2)) or art_ok_w3d(m.group(1)), line.strip()
    m = re.match(r"^\s*ParticleName\s*=\s*(\S+)", line, re.I)
    if m:
        assert art_ok_tex(m.group(1).rsplit(".", 1)[0]), "psys tex: " + m.group(1)
# W3D-internal textures all resolve
for w3dname, data in ((k, v) for k, v in art_files.items() if k.endswith(".W3D")):
    for t in texre.findall(data):
        base = t.decode().rsplit(".", 1)[0]
        assert art_ok_tex(base), "W3D-internal texture missing: %s (%s)" % (t, w3dname)
# mapped images used by shipped buttons/objects resolve
mapped_images = set()
for p, txt in final_texts.items():
    for t, name, _a, _b, _tx in parse_blocks(txt):
        if t == "MappedImage":
            mapped_images.add(name)
for m in re.finditer(r"(?m)^\s*(?:SelectPortrait|ButtonImage)\s*=\s*(\S+)", nc_all):
    assert m.group(1) in mapped_images, "mapped image missing: " + m.group(1)
for n in PORT_IMAGES:
    assert n in mapped_images
# UpgradeCameo refs resolve to Upgrade templates
for m in re.finditer(r"(?m)^\s*UpgradeCameo\d\s*=\s*(\S+)", nc_all):
    assert "Upgrade" in final_defined.get(m.group(1), set()), m.group(1)

# ---- 6. audio closure -----------------------------------------------------
print("   audio closure ...")
final_audio = set(eff_audio) | {ev for p in (VOI, SFX)
                                for ev, _b in ported_audio_blocks[p]}
for ev in collect_audio_refs([shipped_all]):
    assert ev in final_audio, "audio event unresolved: " + ev
# every sample of every ported event resolves in final space
final_sound_paths = final_assets
for p in (VOI, SFX):
    for ev, blk in ported_audio_blocks[p]:
        if ev == "Type79SniperRifleDistant":
            blk = fix_sniper_distant(blk)
        for smp in event_samples(blk):
            lp = smp.lower()
            ok = any(("data\\audio\\sounds\\%s%s.wav" % (pre, lp)) in final_sound_paths
                     for pre in ("", "english\\"))
            assert ok, "sample unresolved: %s (%s)" % (smp, ev)

# ---- 7. stub closure ------------------------------------------------------
for path, objname, target in (
        (IP + "FlameTrooper.ini", "Tank_ChinaInfantryFlameThrower",
         "Spec_ChinaInfantryFlameThrower"),
        (IP + "MiniGunner.ini", "Tank_ChinaInfantryMiniGunner",
         "Infa_ChinaInfantryMiniGunner"),
        (IP + "Sharpshooter.ini", "Tank_ChinaInfantrySharpshooter", None)):
    txt = strip_comments(new_texts[path])
    if target:
        m = re.search(r"(?m)^\s*BuildVariations\s*=\s*(\S+)\s*$", txt)
        assert m and m.group(1) == target, (path, m and m.group(1))
        assert "Object" in eff_defined.get(target, set()), target
    for pr in re.findall(r"(?m)^\s*Object\s*=\s*(\S+)\s*$", txt):
        assert "Object" in final_defined.get(pr, set()), (path, pr)
# stub costs per spec
for name, cost in (("Tank_ChinaInfantryFlameThrower", 350),
                   ("Tank_ChinaInfantryMiniGunner", 550),
                   ("Tank_ChinaInfantrySharpshooter", 1200)):
    for p in (IP + "FlameTrooper.ini", IP + "MiniGunner.ini", IP + "Sharpshooter.ini"):
        for t, n, _a, _b, btext in parse_blocks(new_texts[p]):
            if n == name:
                c = int(re.search(r"(?m)^\s*BuildCost\s*=\s*(\d+)", btext).group(1))
                assert c == cost, (name, c)

# ---- 8. sibling survival --------------------------------------------------
print("   sibling survival ...")


def verify_survival(cs_txt, installed=False):
    lf = to_lf(cs_txt)
    s = parse_sets(lf)
    # our layer: Barracks 1-8 + 12-14 (both variants)
    for n in ("Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade"):
        b = s[n]
        assert b[5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier", n
        assert b[6] == "Tank_Command_ConstructChinaInfantryFlameThrower", n
        assert b[7] == "Tank_Command_ConstructChinaInfantryMiniGunner", n
        assert b[8] == "Tank_Command_ConstructChinaInfantrySharpshooter", n
        assert b[12] == "Command_UpgradeChinaRedguardCaptureBuilding", n
        assert b[13] in ("Command_UpgradeChinaMines", "Command_UpgradeEMPMines"), n
        assert b[14] == "Command_Sell", n
        assert set(b) == {1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14}, (n, sorted(b))
    # PDL: 17 slot-9 buttons, state sets intact
    assert lf.count("Tank_Command_UpgradeKwaiPDL ;") == 17
    for n in ("Tank_ChinaVehicleBattleMasterCommandSetTower",
              "Tank_ChinaVehicleBattleMasterCommandSetPDL",
              "Tank_ChinaTankEmperorGattlingCommandSet",
              "Tank_ChinaTankEmperorPDLCommandSet",
              "Tank_ChinaTankDragonCommandSet",
              "Tank_ChinaTankDragonUpgradedCommandSet",
              "Tank_ChinaReaperCommandSet"):
        assert n in s, "PDL set lost: " + n
    # roster: WF page 2 slots 4-7, Airfield 3-4 + 5 exit cameos
    wf = s["Tank_ChinaWarFactoryCommandSet_Down"]
    assert wf[4] == "Tank_Command_ConstructChinaTankOverlord"
    assert wf[7] == "Tank_Command_ConstructChinaVehicleScoutCar"
    for i in (8, 9, 10, 11):
        assert i not in wf
    assert wf[12] == "Command_ChinaButtonCommandSetOneUp"
    for n in ("Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
        a = s[n]
        assert a[3] == "Tank_Command_ConstructChinaJetMIGFighter"
        assert a[4] == "Tank_Command_ConstructChinaJetMIGBomber"
        for i in (5, 6, 7, 8, 9):
            assert a[i] == "Command_StructureExit", (n, i)
        assert a[10] == "Command_Evacuate"
    # kwai-uav IC clones + vanilla IC sets
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):
        ic = s["Tank_ChinaInternetCenterCommandSet" + v]
        assert ic[7] == "Tank_Command_UpgradeKwaiUAVProgram" \
            and ic[8] == "Tank_Command_KwaiUAVDeploy" \
            and ic[9] == "Command_Evacuate", (v, ic)
        vs = s["ChinaInternetCenterCommandSet" + v]
        assert vs[7] == "Command_StructureExit" and vs[8] == "Command_StructureExit"
    # doctrine/garrisons prop-center machine: 50 sets full 14/14
    pc = {n: b for n, b in s.items() if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc) == 50, len(pc)
    for n, b in pc.items():
        assert sorted(b) == list(range(1, 15)), n
    # artillery / chaos WF page 1
    for n in ("Tank_ChinaWarFactoryCommandSet", "Tank_ChinaWarFactoryCommandSetUpgrade"):
        assert s[n][11] == "Tank_Command_ConstructChinaVehicleInfernoCannon", n
        assert s[n][12] == "Command_ChinaButtonCommandSetOneDown", n
    # mammoth-bunker transport slots
    stem = ("  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n")
    assert lf.count(stem + "  8  = Command_Evacuate\n") == 1
    assert lf.count(stem + "  8  = Command_Evacuate \n") == 4
    # kwai-bunkers dozer pages + hacker bunker + basetech power plant
    assert s["Tank_ChinaDozerCommandSet"][13] == "Command_ChinaButtonCommandSetOneDown"
    dz2 = s["Tank_ChinaDozerCommandSet_Down"]
    assert dz2[7] == "Tank_Command_ConstructChinaBunker"
    assert dz2[8] == "Tank_Command_ConstructChinaHackerBunker"
    for n in ("Tank_ChinaHackerBunkerCommandSet", "Tank_ChinaPowerPlantCommandSet",
              "Tank_ChinaPowerPlantCommandSetUpgrade", "GlobalHawkCommandSet"):
        assert n in s, "sibling set lost: " + n
    # emperor-bunker emperor set; garrisons evacuates; proptower ERA
    emp = s["Tank_ChinaTankEmperorDefaultCommandSet"]
    assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
    assert emp[12] == "Command_Evacuate"
    assert lf.count("Command_Evacuate") >= 60
    assert "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n" in lf
    vpc = s["ChinaPropagandaCenterCommandSet"]
    assert vpc[1] == "Command_UpgradeChinaNationalism" and 10 not in vpc
    print("   commandset survival OK%s" % (" (installed)" if installed else ""))


verify_survival(cs_new)
# CommandButton: chaos/roster/PDL/uav buttons all survive (pure-append asserted);
for bn in ("Tank_Command_UpgradeKwaiPDL", "Tank_Command_KwaiUAVDeploy",
           "Tank_Command_ConstructChinaTankJS7",
           "Tank_Command_ConstructChinaInfantrySiegeSoldier",
           "Tank_Command_ConstructChinaVehicleInfernoCannon"):
    assert ("CommandButton %s\n" % bn) in cb_new, bn

# ---- 9. archive name sort position (both real dirs) -----------------------
for d in (SPE_DIR, SHW_DIR):
    listing = sorted(set(os.listdir(d)) | {OUT_NAME, "zzz-ZZZZZZZRotrProbe.big"},
                     key=str.lower)
    i = listing.index(OUT_NAME)
    after = [f for f in listing[:i] if f.lower().endswith(".big")]
    before = [f for f in listing[i + 1:] if f.lower().endswith(".big")]
    assert "zzz-ZZZZZZZKwaiPDL.big" in after, d + ": must sort after PDL"
    assert "zzz-ZZZZZZZRotrProbe.big" in before, d + ": must sort before R*"
    assert any(f.startswith("zzz_ControlBarPro") for f in before), \
        d + ": must sort before ControlBarPro skins"
print("   sort order OK in both mod dirs")

# ============================================================ write + install
entries = [BigEntry(p, data) for p, data in sorted(out_files.items())]
out_path = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_path)
print("== wrote %s (%d files, %.1f MB)" % (
    OUT_NAME, len(entries), os.path.getsize(out_path) / 1e6))

with open(out_path, "rb") as f:
    blob = f.read()
for dest in (SPE_DIR, SHW_DIR):
    dst = os.path.join(dest, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob)
    back = read_big(dst)
    assert {e.path: e.data for e in back} == out_files, "install verify: " + dst
    verify_survival(next(e.data for e in back if e.path == CS).decode("latin-1"),
                    installed=True)
    print("== installed + re-verified:", dst)

print("\nOK.  Barracks 6 Flame Trooper ($350) / 7 Minigunner ($550) / "
      "8 Sharpshooter ($1200, ZHE port).")
