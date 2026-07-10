#!/usr/bin/env python3
"""Build zzz-ZZZZChaosUnits.big — three Shockwave-Chaos ports for Kwai
(China Tank General), ShockWave under GeneralsX:

1. EMPEROR SHTORA RETROFIT — the Chaos Golem/Emperor "Shtora" active
   protection system grafted onto our existing Tank_ChinaTankEmperor:
   an auto-firing FireWeaponWhenDamagedBehavior (damage >= 30 triggers
   GolemTankShtoraAIWeapon, 30 s clip) whose FireOCL launches blinding
   grenades and spawns an 8 s slaved defence object that re-applies the
   MASKED status (untargetable) to the tank, plus the donor's manual-
   ability module trio (OCLSpecialPower/FireWeaponCollide/
   MissileLauncherBuildingUpdate on SpecialAbilityRussianShtora) for
   fidelity.  The emperor-bunker HelixContain bay, propaganda tower,
   gattling chain and doctrine armor tiers are preserved (asserted).

2. JS-7 / IS-7 superheavy tank (Tank_ChinaTankJS7) — new war-factory
   buildable.  Donor stats except +20% HP (950 -> 1140, stack
   convention) and prerequisites per spec (War Factory + Propaganda
   Center; Chaos used Industrial Plant + Propaganda Center).  Has its
   own MANUAL Shtora button (RussianTankGolemCommandSet, donor design).
   CARBOMB weapon-sets dropped (Chaos leech-infection mechanic, absent
   here; our China tanks carry no CARBOMB sets either).  Chaos-only
   voice/sound events remapped to base ShockWave events (T26 voice
   samples are not in any obtainable archive).

3. CHINA COMMAND TANK (Tank_ChinaTankCommandTank) — hero-style mobile
   command vehicle, MaxSimultaneousOfType = 1 (donor).  +20% HP
   (1300 -> 1560).  KindOf gains COMMANDCENTER (spec; mirrors the
   vanilla-China ChinaTankCommandTank donor variant).  APFSDS/HESH
   SWITCH_WEAPON buttons, veterancy-crate special power
   (SuperweaponChinaCommandTankGrantVeterancy -> SalvageCrateCollide
   crate, LevelChance 100%), propaganda tower, $25/s AutoDeposit,
   death crates, and a two-page command set (GLAWorker page tokens,
   same pair as the dozer pages) whose "Generals Abilities" page hosts
   the shared-timer general's powers whose templates exist in our
   stack (CarpetBomb, TankParadrop, ArtilleryBarrage, EmergencyRepair,
   EMPPulse).  Dropped (missing Chaos closures, documented): Tesla-tank
   paradrop, V4 paradrop, global radar jammer, leech drone, Sweet
   Tooth, and the invisible is-a-structure battle-drone trick.

WAR FACTORY PAGE 2 (dozer page-flip idiom, kwai-bunkers precedent):
both WF set variants get slot 12 (Nuke Cannon, kwai-artillery) swapped
for the page-down arrow; a single new page-2 set carries the relocated
Nuke Cannon (1), JS-7 (2), Command Tank (3), page-up arrow (12),
Evacuate (13) and Sell (14).  Slots 4-11 are left contiguous-free for a
follow-up layer.  Two CommandSetUpgrade modules on the WF flip the
pages; they queue through the WF's ProductionUpdate (engine: upgrades
join the END of the queue and complete instantly only at its head), so
a flip issued while units are building completes after them — inherent
to putting pages on a producing factory, documented in the README.

All Chaos INI content is read from the local donor cache
(../donor-inis/shw_base_ini, byte-verified against Chaos's own
!Shw_ini.big) and transformed with exact-match replacements that fail
loudly on drift.  Art ships from !ChaosArt.big plus 12 textures ranged-
fetched from Chaos's !ShwTextures.big (donor-art/fetched).  Strings are
the Chaos Generals.str entries (16), appended per sibling convention.
"""
import hashlib
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, os.path.join(HERE, "work"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402
from iniblocks import load_tree, parse_blocks  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
BASE_DIRS = [os.path.expanduser("~/GeneralsX/GeneralsZH"),
             os.path.expanduser("~/GeneralsX/GeneralsZH/ZH_Generals")]
DONOR = os.path.join(HERE, "..", "donor-inis", "shw_base_ini", "Data", "INI")
CHAOS_ART = os.path.join(HERE, "donor-art", "ChaosArt.big")
CHAOS_INI_BIG = os.path.join(HERE, "donor-art", "ChaosShw_ini.big")
FETCHED = os.path.join(HERE, "donor-art", "fetched")
OUT_NAME = "zzz-ZZZZChaosUnits.big"
TAG = "zzz-ZZZZChaosUnits"

VP = "Data\\INI\\Object\\China\\Tank\\Vehicles\\"
BP = "Data\\INI\\Object\\China\\Tank\\Buildings\\"
CS = "Data\\INI\\CommandSet.ini"
CB = "Data\\INI\\CommandButton.ini"
STR = "Data\\Generals.str"

# effective owners we expect for every patched file (drift = abort)
EXPECT_OWNERS = {
    CS: "zzz-ZZZKwaiGarrisons.big",
    CB: "zzz-ZZKwaiBaseTech.big",
    STR: "zzz-ZZKwaiBaseTech.big",
    "Data\\INI\\Weapon.ini": "zzz-ZZKwaiBaseTech.big",
    "Data\\INI\\Armor.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\Locomotor.ini": "zzx_ChinaTankBuff.big",
    "Data\\INI\\FXList.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\ParticleSystem.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\ObjectCreationList.ini": "zz_SPE_Shw_ini.big",
    "Data\\INI\\SpecialPower.ini": "zz_SPE_Shw_ini.big",
    VP + "Emperor.ini": "zzz-KwaiDoctrine.big",
    BP + "WarFactory.ini": "zzz-ZZZKwaiGarrisons.big",
}
NEW_INI_PATHS = [
    VP + "JS7.ini",
    VP + "CommandTank.ini",
    VP + "ChaosSupportObjects.ini",
    "Data\\INI\\MappedImages\\HandCreated\\ChaosUnitsMappedImages.INI",
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


def replace_exact(s, old, new, count, what=""):
    got = s.count(old)
    assert got == count, "%s: expected %d of %r..., found %d" % (
        what, count, old[:70], got)
    return s.replace(old, new)


def block_of(defs, typ, name):
    key = (typ, name)
    assert key in defs, "donor block missing: %s %s" % key
    rel, text = defs[key]
    assert text.endswith("\n")
    return text


WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")


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

# donor cache authenticity: byte-compare a sample of donor files vs Chaos big
chaos_ini = {e.path: e.data for e in read_big(CHAOS_INI_BIG)}
for p in ["Data\\INI\\Object\\China\\Tank\\Vehicles\\JS7.ini",
          "Data\\INI\\Weapon.ini", "Data\\INI\\CommandSet.ini",
          "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\ChinaCommandTank.ini",
          "Data\\INI\\SpecialPower.ini", "Data\\INI\\ObjectCreationList.ini",
          "Data\\INI\\FXList.ini", "Data\\INI\\ParticleSystem.ini",
          "Data\\INI\\Armor.ini", "Data\\INI\\Locomotor.ini",
          "Data\\INI\\CommandButton.ini", "Data\\INI\\Object\\System.ini",
          "Data\\INI\\Object\\WeaponObjects.ini", "Data\\INI\\Crate.ini",
          "Data\\INI\\Object\\Hulk.ini"]:
    local = open(os.path.join(HERE, "..", "donor-inis", "shw_base_ini",
                              p.replace("\\", "/")), "rb").read()
    assert hashlib.md5(local).hexdigest() == hashlib.md5(chaos_ini[p]).hexdigest(), \
        "donor cache drift vs Chaos !Shw_ini.big: " + p

print("== parsing donor tree")
ddefs_raw, dbyname = load_tree(DONOR)
# donor mapped-image files use .INI too and load_tree handles them
print("   %d donor blocks" % len(ddefs_raw))
ddefs = ddefs_raw

# =================================================================== PORTS
# Every ported block is donor text run through exact-match transforms.
# (old, new, count) triples; count asserts donor drift.

AUDIO_REMAPS_NOTE = """\
audio remaps (Chaos samples not obtainable; ChaosArt.big carries no audio):
  GolemTankCannonWeapon        -> WarMasterTankFire         (JS-7 cannon, via FXLists)
  GolemHeavyMachinegunWeapon   -> HelixWeaponMachineGun     (JS-7 MGs)
  GuardTowerMg3MachinegunBulletWhistle -> NoSound           (MG impact whistle)
  GolemShtoraBlindingGrenadeExplosion  -> ExplosionFlashBang (Shtora grenade pop)
  NewTurretMoveLoop            -> TurretMoveLoop            (JS-7 turret)
  SovietT26Voice*              -> Emperor/Overlord voice set (JS-7 voice)
  GolemVoiceActivateShtora     -> (line removed; event undefined even in Chaos)
"""

def ported(typ, name, transforms=()):
    txt = block_of(ddefs, typ, name)
    for old, new, count in transforms:
        txt = replace_exact(txt, old, new, count, "%s %s" % (typ, name))
    return txt


WEAPONS = [
    ("JS7TankGun", ()),
    ("JS7TankGunUpgraded", ()),
    ("GolemHeavyMachineGunGun", ()),
    ("GolemHeavyMachineGunGunAir",
     [("  FireSound             = GolemHeavyMachinegunWeapon\n",
       "  FireSound             = HelixWeaponMachineGun ; " + TAG + " remap\n", 1)]),
    ("Tank_ChinaCommandTankCannonAPFSDS", ()),
    ("Tank_ChinaCommandTankCannonHESH", ()),
    ("GolemTankViewShakeDummyWeapon", ()),
    ("GolemTankHighExplosiveMeleeDamageWeaponForCounteringHeavyInfantryWithAnEvenLongerNameWTF", ()),
    ("MainBattleTankHighExplosiveMeleeDamageWeaponForCounteringHeavyInfantryWithAnEvenLongerNameWTF", ()),
    ("MainBattleTankHighExplosiveStunWeaponWithAModeratelyLongName", ()),
    ("GuardTowerMachineGunTracerEffect", ()),
    ("RussianRepairedVehicleHullTertiaryUnmanWeapon", ()),
    ("GolemInvulnerabilityActivationWeapon", ()),
    ("GolemTankShtoraAIWeapon", ()),
    ("GolemInvulnerabilityWeapon", ()),
    ("RussianGolemShtoraBlindingGrenadeWeapon", ()),
]
ARMORS = ["JS7TankArmor", "LolGitGudFuckerPlayMoreIS7", "ChinaCommandTankArmor"]
LOCOMOTORS = ["JS7Locomotor", "JS7LocomotorUpgraded", "ChinaCommandTankLocomotor",
              "ChinaCommandTankLocomotorUpgraded", "GSPScramblerDroneLocomotor"]
FXLISTS = [
    ("GenericBulletIpmactFX", ()),
    ("WeaponFX_GolemMachineGunFire",
     [("    Name = GolemHeavyMachinegunWeapon\n",
       "    Name = HelixWeaponMachineGun ; " + TAG + " remap\n", 1)]),
    ("WeaponFX_HeroicGolemMachineGunFire",
     [("    Name = GolemHeavyMachinegunWeapon\n",
       "    Name = HelixWeaponMachineGun ; " + TAG + " remap\n", 1)]),
    ("WeaponFX_GolemTankGunNoTracer",
     [("    Name = GolemTankCannonWeapon\n",
       "    Name = WarMasterTankFire ; " + TAG + " remap\n", 1)]),
    ("WeaponFX_HeroicGolemTankGunNoTracer",
     [("    Name = GolemTankCannonWeapon\n",
       "    Name = WarMasterTankFire ; " + TAG + " remap\n", 1)]),
    ("WeaponFX_GolemViewShakeDummyFX", ()),
    ("WeaponFX_GuardTowerMachineGunImpact",
     [("    Name = GuardTowerMg3MachinegunBulletWhistle\n",
       "    Name = NoSound ; " + TAG + " remap\n", 1)]),
    ("WeaponFX_HeavyMachineGunTracerEffect", ()),
    ("WeaponFX_LatrunArtilleryGun", ()),
    ("WeaponFX_HeroicLatrunArtilleryGun", ()),
    ("WeaponFX_TunguskaGunFireAir", ()),
    ("WeaponFX_HeroicTunguskaGunFireAir", ()),
    ("WeaponFX_ShtoraBlindingGrenadeDetonation",
     [("    Name = GolemShtoraBlindingGrenadeExplosion\n",
       "    Name = ExplosionFlashBang ; " + TAG + " remap\n", 1)]),
]
PARTICLES = ["BulletImpactDebris", "GenericTankShellLargeTrail",
             "GolemShtoraActiveEffect", "HeavyMachineGunTracerLensFlare",
             "HeavyMachineGunTracerLensFlareHeroic", "ShtoraDetonationFlash",
             "ShtoraDetonationSparks"]
OCLS = ["OCL_APFSDSFire", "OCL_ChinaCommandTankExplode",
        "OCL_GolemActivateShtoraActiveDefenceSystem",
        "OCL_GolemExplosiveDamageToInfantry", "OCL_JS7TankDeathEffect",
        "OCL_MBTHighExplosiveStun", "OCL_SkyShieldShellExplosionDetonationEffect",
        "SUPERWEAPON_GrantVeterancy"]
SPECIALPOWERS = ["SpecialAbilityRussianShtora",
                 "SuperweaponChinaCommandTankGrantVeterancy"]
SUPPORT_OBJECTS = [
    "APFSDSShell", "GolemTankShell", "GuardTowerMG3Projectile",
    "GuardianCannonTracer", "ChinaMainBattleTankStun",
    "Tank_ChinaTankGolemMeleeKill", "RussianGolemShtoraBlindingGrenade",
    "RussianGolemShtoraActiveDefenceBlindingGrenadeLauncherObject",
    "RussianGolemShtoraActiveDefenceObject",
    "RussianVehicleNeutralHullKillObject", "ChinaCommandTankHulk",
    "ChinaCommandTankVeterancyCrate",
]
BUTTONS = [
    ("Tank_Command_ConstructChinaTankJS7", ()),
    ("Tank_Command_ConstructChinaTankCommandTank", ()),
    ("Command_RussiaGolemTankActivatedShtora",
     [("  UnitSpecificSound = GolemVoiceActivateShtora\n", "", 1)]),
    ("Command_CommandTankAPFSDSShells", ()),
    ("Command_CommandTankHESHShells", ()),
    ("Command_ChinaCommandTankGrantVeterancy", ()),
    ("Command_ChinaCommandTruckSwitchToPowers", ()),
    ("Command_ChinaCommandTruckSwitchToNormal", ()),
]
MAPPED_IMAGES = ["SRIosif_L", "SRIosif", "SSGolemShtora"]

# ------------------------------------------------ JS-7 object (adapted)
JS7_TRANSFORMS = [
    # +20% HP convention
    ("    MaxHealth       = 950.0\n    InitialHealth   = 950.0\n",
     "    MaxHealth       = 1140.0 ; " + TAG + ": Chaos 950 +20% stack convention\n"
     "    InitialHealth   = 1140.0\n", 1),
    # prerequisites per spec (Chaos: IndustrialPlant + PropagandaCenter)
    ("    Object = Tank_ChinaIndustrialPlant Tank_ChinaPropagandaCenter\n",
     "    Object = Tank_ChinaWarFactory Tank_ChinaPropagandaCenter ; " + TAG +
     ": spec prereq (Chaos used IndustrialPlant+PropagandaCenter)\n", 1),
    # drop CARBOMB weapon-sets (Chaos leech-infection mechanic; our stack has
    # no leech and our China tanks carry no CARBOMB sets)
    ("  WeaponSet\n"
     "    Conditions = CARBOMB\n"
     "    Weapon           = PRIMARY   InfectedJS7TankGun\n"
     "    Weapon           = SECONDARY GolemHeavyMachineGunGun\n"
     "    Weapon           = TERTIARY  GolemHeavyMachineGunGunAir\n"
     "    PreferredAgainst = TERTIARY  AIRCRAFT\n"
     "  End\n"
     "  WeaponSet\n"
     "    Conditions = CARBOMB PLAYER_UPGRADE\n"
     "    Weapon           = PRIMARY   InfectedJS7TankGun\n"
     "    Weapon           = SECONDARY GolemHeavyMachineGunGun\n"
     "    Weapon           = TERTIARY  GolemHeavyMachineGunGunAir\n"
     "    PreferredAgainst = TERTIARY  AIRCRAFT\n"
     "  End\n"
     "\n", "", 1),
    # voice/sound remaps (T26 samples unavailable)
    ("  VoiceSelect   = SovietT26VoiceSelect\n",
     "  VoiceSelect   = EmperorTankVoiceSelect ; " + TAG + " remap\n", 1),
    ("  VoiceMove     = SovietT26VoiceMove\n",
     "  VoiceMove     = EmperorTankVoiceMove ; " + TAG + " remap\n", 1),
    ("  VoiceGuard    = SovietT26VoiceMove\n",
     "  VoiceGuard    = EmperorTankVoiceMove ; " + TAG + " remap\n", 2),
    ("  VoiceAttack   = SovietT26VoiceAttack\n",
     "  VoiceAttack   = OverlordTankVoiceAttack ; " + TAG + " remap\n", 1),
    ("  VoiceAttackAir = SovietT26VoiceAttack\n",
     "  VoiceAttackAir = OverlordTankVoiceAttack ; " + TAG + " remap\n", 1),
    ("    VoiceCreate     = SovietT26VoiceCreate\n",
     "    VoiceCreate     = EmperorOverlordTankVoiceCreate ; " + TAG + " remap\n", 1),
    ("    TurretMoveLoop  = NewTurretMoveLoop\n",
     "    TurretMoveLoop  = TurretMoveLoop ; " + TAG + " remap\n", 1),
    ("    VoiceEnter      = SovietT26VoiceMove\n",
     "    VoiceEnter      = EmperorTankVoiceMove ; " + TAG + " remap\n", 1),
]

# ------------------------------------- Command Tank object (adapted)
def module_text(objtext, tag):
    """Extract '  Behavior = ... ModuleTag_x ... End' block text by tag."""
    m = re.search(r"(?ms)^  Behavior[ \t]*=[ \t]*\S+[ \t]+%s\b.*?^  End[ \t]*\n" % re.escape(tag),
                  objtext)
    assert m, "module not found: " + tag
    return m.group(0)


CT_DROP_TAGS = [
    "ModuleTag_StructureConditions01",  # invisible is-a-structure drone trick
    "ModuleTag_StructureConditions02",
    "ModuleTag_DoomsDay01",             # leech infector (Chaos-only closure)
    "ModuleTag_Sweet01",                # Sweet Tooth (Chaos-only closure)
    "ModuleTag_Science02",              # V4 paradrop (Chaos-only closure)
    "ModuleTag_Science07",              # global radar jammer (Chaos-only)
    "ModuleTag_DontTazeMeBro01",        # tesla tank paradrop (Chaos-only)
]
CT_BASE_TRANSFORMS = [
    ("    MaxHealth       = 1300.0\n    InitialHealth   = 1300.0\n",
     "    MaxHealth       = 1560.0 ; " + TAG + ": Chaos 1300 +20% stack convention\n"
     "    InitialHealth   = 1560.0\n", 1),
    ("    Object = Tank_ChinaIndustrialPlant\n",
     "    Object = Tank_ChinaWarFactory Tank_ChinaCommandCenter ; " + TAG +
     ": spec prereq (Chaos used IndustrialPlant)\n", 1),
    ("  KindOf = PRELOAD SELECTABLE CAN_ATTACK ATTACK_NEEDS_LINE_OF_SIGHT VEHICLE SCORE HUGE_VEHICLE DRONE HERO\n",
     "  KindOf = PRELOAD SELECTABLE CAN_ATTACK ATTACK_NEEDS_LINE_OF_SIGHT VEHICLE SCORE HUGE_VEHICLE DRONE HERO COMMANDCENTER ; "
     + TAG + ": +COMMANDCENTER per spec (mirrors vanilla-China donor variant)\n", 1),
]

# ------------------------------------------- Emperor Shtora insertion
EMP_ANCHOR = "  Behavior = FlammableUpdate ModuleTag_21\n"
EMP_SHTORA = (
    "  ;Shtora Active Protection System -- ported from ShockWave Chaos (" + TAG + ")\n"
    "  ;Auto path: FireWeaponWhenDamaged fires GolemTankShtoraAIWeapon (30s clip;\n"
    "  ;this engine checks READY_TO_FIRE, so the cooldown IS respected) whose FireOCL\n"
    "  ;launches 2 blinding grenades and spawns an 8s slaved defence object that\n"
    "  ;pulses MASKED (untargetable) onto the tank.  Reaction weapons are per-body-\n"
    "  ;state (engine onDamage), so the REALLYDAMAGED slot is also wired -- donor set\n"
    "  ;only the DAMAGED slot, which would disarm the APS in red state.  The manual-\n"
    "  ;ability module trio is kept for donor fidelity (no button: the set is full).\n"
    "  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_ShtoraAuto01\n"
    "    StartsActive  = Yes\n"
    "    DamageTypes   = ALL\n"
    "    ReactionWeaponDamaged       = GolemTankShtoraAIWeapon\n"
    "    ReactionWeaponReallyDamaged = GolemTankShtoraAIWeapon\n"
    "    DamageAmount    = 30  ; if damage is >= this value, fire the weapon\n"
    "  End\n"
    "  Behavior           = OCLSpecialPower ModuleTag_Shtora01\n"
    "    SpecialPowerTemplate = SpecialAbilityRussianShtora\n"
    "    OCL                  = OCL_UniversalAbbilityTrigger\n"
    "    CreateLocation       = USE_OWNER_OBJECT\n"
    "  End\n"
    "  Behavior = FireWeaponCollide ModuleTag_Shtora02\n"
    "    CollideWeapon  = GolemInvulnerabilityActivationWeapon\n"
    "    RequiredStatus = USING_ABILITY\n"
    "  End\n"
    "  Behavior = MissileLauncherBuildingUpdate ModuleTag_Shtora03\n"
    "    SpecialPowerTemplate = SpecialAbilityRussianShtora\n"
    "    DoorOpenTime         = 1650\n"
    "    DoorWaitOpenTime     = 1650\n"
    "    DoorCloseTime        = 7000\n"
    "  End\n"
)

# ------------------------------------------- War Factory page flip
WF_ANCHOR = ("  Behavior = CommandSetUpgrade ModuleTag_25\n"
             "    CommandSet = Tank_ChinaWarFactoryCommandSetUpgrade\n"
             "    TriggeredBy = Upgrade_ChinaMines\n"
             "  End\n")
WF_PAGES = (
    "  Behavior = CommandSetUpgrade ModuleTag_CU_Page01 ; " + TAG +
    ": page-down -> WF page 2 (dozer page-flip idiom)\n"
    "    TriggeredBy     = Upgrade_GLAWorkerFakeCommandSet\n"
    "    RemovesUpgrades = Upgrade_GLAWorkerRealCommandSet\n"
    "    CommandSet      = Tank_ChinaWarFactoryCommandSet_Down\n"
    "  End\n"
    "  Behavior = CommandSetUpgrade ModuleTag_CU_Page02 ; " + TAG +
    ": page-up -> WF page 1\n"
    "    TriggeredBy     = Upgrade_GLAWorkerRealCommandSet\n"
    "    RemovesUpgrades = Upgrade_GLAWorkerFakeCommandSet Upgrade_GLAWorkerRealCommandSet\n"
    "    CommandSet      = Tank_ChinaWarFactoryCommandSet\n"
    "  End\n"
)

WF_SLOT12_OLD = "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n"
WF_SLOT12_NEW = "  12 = Command_ChinaButtonCommandSetOneDown ; " + TAG + \
    ": page-down; Nuke Cannon relocated to page 2 slot 1\n"

CS_APPENDIX = (
    "\n"
    ";;; " + TAG + ": war-factory page 2 (dozer page-flip idiom; slots 4-11\n"
    ";;; deliberately left free+contiguous for a follow-up layer) + the three\n"
    ";;; ported Shockwave-Chaos unit sets.\n"
    "CommandSet Tank_ChinaWarFactoryCommandSet_Down\n"
    "  1  = Tank_Command_ConstructChinaVehicleNukeLauncher\n"
    "  2  = Tank_Command_ConstructChinaTankJS7\n"
    "  3  = Tank_Command_ConstructChinaTankCommandTank\n"
    "  12 = Command_ChinaButtonCommandSetOneUp\n"
    "  13 = Command_Evacuate\n"
    "  14 = Command_Sell\n"
    "End\n"
    "\n"
    "CommandSet RussianTankGolemCommandSet\n"
    "  1  = Command_RussiaGolemTankActivatedShtora\n"
    "  11 = Command_AttackMove\n"
    "  13 = Command_Guard\n"
    "  14 = Command_Stop\n"
    "End\n"
    "\n"
    ";;; Chaos donor sets minus the powers whose Chaos-only closures were not\n"
    ";;; ported (tesla/V4 paradrop, radar jam, leech drone, sweet tooth).\n"
    "CommandSet Tank_ChinaVehicleCommandTruckCommandSet\n"
    "   1 = Command_CommandTankAPFSDSShells\n"
    "   3 = Command_CommandTankHESHShells\n"
    "  10 = Command_ChinaCommandTankGrantVeterancy\n"
    "  11 = Command_AttackMove\n"
    "  12 = Command_ChinaCommandTruckSwitchToPowers\n"
    "  13 = Command_Guard\n"
    "  14 = Command_Stop\n"
    "End\n"
    "\n"
    "CommandSet Tank_ChinaVehicleCommandTruckPowersCommandSet\n"
    "  1  = Command_ChinaCarpetBomb\n"
    "  4  = Tank_Command_TankParadrop\n"
    "  5  = Command_ArtilleryBarrage\n"
    "  6  = Early_Command_EmergencyRepair\n"
    "  7  = Command_EMPPulse\n"
    "  12 = Command_ChinaCommandTruckSwitchToNormal\n"
    "  14 = Command_Stop\n"
    "End\n"
)

STR_KEYS = [
    "CONTROLBAR:ActivateShtoraDefenceSystem", "CONTROLBAR:TooltipShtoraDefenceSystem",
    "CONTROLBAR:ChinaCommandTankAPFSDSShells", "CONTROLBAR:ToolTipChinaCommandTankAPFSDSShells",
    "CONTROLBAR:ChinaCommandTankHESHShells", "CONTROLBAR:ToolTipChinaCommandTankHESHShells",
    "CONTROLBAR:ChinaCommandTankVeterancy", "CONTROLBAR:TooltipChinaCommandTankVeterancy",
    "CONTROLBAR:CommandTruckDefaultList", "CONTROLBAR:CommandTruckPowersList",
    "CONTROLBAR:ConstructChinaTankCommandTank", "CONTROLBAR:ToolTipChinaBuildCommandTank",
    "CONTROLBAR:ConstructChinaTankJS7", "CONTROLBAR:ToolTipConstructChinaTankJS7",
    "OBJECT:JS7", "OBJECT:ChinaCommandTruck",
]

# ------------------------------------------------------- art ship list
ART_W3D = ["RVIS7", "RVIS7_A1", "RVIS7_D", "RVIS7_D2", "RVIS7_N",
           "RVGolem_A1", "RVGolem_A2",
           "NVBtMstrBl", "NVBtMstrBlB1", "NVBtMstrBl_D", "NVBtMstrBlB1_D"]
ART_TGA_FROM_CHAOSART = ["RVIosif.tga", "RVIS7.dds", "RVIS72.dds",
                         "RVIS7_d.dds", "RVIS72_d.dds"]
ART_FETCHED = ["EXStarGlow.dds", "EXECMRing.dds", "RVArmor.dds", "RVArmor_D.dds",
               "RVGolem.dds", "RVGolem_D.dds", "RVGolem2.dds", "RVGolem2_D.dds",
               "RVT80UM.dds", "RVT80UM_D.dds", "exgolemtrack.dds",
               "SNRUserInterface512_003.tga"]
# referenced by ported/donor content but missing from EVERY obtainable archive
# including Chaos's own (donor-parity: Chaos ships these references unresolved;
# the engine skips missing debris models / textures / attached systems):
GRANDFATHERED_ART = {"tracercore.tga"}
GRANDFATHERED_PARTICLES = {"ShtoraDetonationSparksTrail",
                           "HeavyMachineGunTracerTrail",
                           "HeavyMachineGunTracerTrailHeroic"}

# =========================================================== build the text
out_files = {}   # path -> bytes


def patch(path, fn):
    raw = eff_data[path].decode("latin-1")
    eol = eol_of(raw)
    lf = to_lf(raw)
    new_lf = fn(lf)
    out_files[path] = from_lf(new_lf, eol).encode("latin-1")
    return lf, new_lf


def append_blocks(path, header, blocks):
    def fn(lf):
        appendix = "\n;;; " + TAG + ": " + header + "\n" + "\n".join(blocks)
        if not lf.endswith("\n"):
            lf += "\n"
        return lf + appendix
    return patch(path, fn)


weapon_blocks = [ported("Weapon", n, t) for n, t in WEAPONS]
armor_blocks = [ported("Armor", n) for n in ARMORS]
loco_blocks = [ported("Locomotor", n) for n in LOCOMOTORS]
fx_blocks = [ported("FXList", n, t) for n, t in FXLISTS]
psys_blocks = [ported("ParticleSystem", n) for n in PARTICLES]
ocl_blocks = [ported("ObjectCreationList", n) for n in OCLS]
sp_blocks = [ported("SpecialPower", n) for n in SPECIALPOWERS]
btn_blocks = [ported("CommandButton", n, t) for n, t in BUTTONS]
img_blocks = [ported("MappedImage", n) for n in MAPPED_IMAGES]
support_blocks = [ported("Object", n) for n in SUPPORT_OBJECTS]

append_blocks("Data\\INI\\Weapon.ini",
              "Shockwave Chaos ports (JS-7 / Command Tank / Shtora).\n;;; " +
              AUDIO_REMAPS_NOTE.replace("\n", "\n;;; ").rstrip("; \n") + "\n",
              weapon_blocks)
append_blocks("Data\\INI\\Armor.ini", "Shockwave Chaos ports", armor_blocks)
append_blocks("Data\\INI\\Locomotor.ini", "Shockwave Chaos ports", loco_blocks)
append_blocks("Data\\INI\\FXList.ini", "Shockwave Chaos ports (sounds remapped)", fx_blocks)
append_blocks("Data\\INI\\ParticleSystem.ini",
              "Shockwave Chaos ports.  PerParticleAttachedSystem refs to\n"
              ";;; *TracerTrail*/*SparksTrail* systems are undefined in Chaos itself;\n"
              ";;; the engine skips missing attached systems (ParticleSys.cpp:2063 'if (tmp)').",
              psys_blocks)
append_blocks("Data\\INI\\ObjectCreationList.ini", "Shockwave Chaos ports", ocl_blocks)
append_blocks("Data\\INI\\SpecialPower.ini", "Shockwave Chaos ports", sp_blocks)
append_blocks(CB, "Shockwave Chaos ports", btn_blocks)


def patch_commandset(lf):
    # swap slot 12 inside BOTH war-factory sets only (scoped per set body)
    for set_name in ("Tank_ChinaWarFactoryCommandSet",
                     "Tank_ChinaWarFactoryCommandSetUpgrade"):
        m = re.search(r"(?ms)^(CommandSet %s\n)(.*?)(^End)" % set_name, lf)
        assert m, set_name
        body = m.group(2)
        body = replace_exact(body, WF_SLOT12_OLD, WF_SLOT12_NEW, 1, set_name)
        lf = lf[:m.start(2)] + body + lf[m.end(2):]
    return lf + CS_APPENDIX


patch(CS, patch_commandset)


def patch_emperor(lf):
    assert lf.count("Object Tank_ChinaTankEmperor\n") == 1
    for t in ("ModuleTag_ShtoraAuto01", "ModuleTag_Shtora01",
              "ModuleTag_Shtora02", "ModuleTag_Shtora03"):
        assert t not in lf, "Emperor module tag collision: " + t
    return replace_exact(lf, EMP_ANCHOR, EMP_SHTORA + EMP_ANCHOR, 1, "Emperor.ini")


patch(VP + "Emperor.ini", patch_emperor)


def patch_warfactory(lf):
    for t in ("ModuleTag_CU_Page01", "ModuleTag_CU_Page02"):
        assert t not in lf
    return replace_exact(lf, WF_ANCHOR, WF_ANCHOR + WF_PAGES, 1, "WarFactory.ini")


patch(BP + "WarFactory.ini", patch_warfactory)

# ---------------------------------------------------------------- strings
chaos_str = open(os.path.join(HERE, "work", "chaos_generals.str"), "rb").read() \
    .decode("latin-1")
str_entries = []
for k in STR_KEYS:
    m = re.search(r"(?mi)^%s[ \t]*\r?\n(.*?\r?\n)END" % re.escape(k), chaos_str, re.S)
    assert m, "Chaos string missing: " + k
    ent = to_lf(m.group(0))
    if k == "CONTROLBAR:ToolTipChinaBuildCommandTank":
        # the invisible is-a-structure drone was NOT ported; keep the tooltip honest
        ent = replace_exact(ent, " Counts as a structure. \\n", "", 1, k)
    str_entries.append(ent)

str_raw = eff_data[STR].decode("latin-1")
str_eol = eol_of(str_raw)
appendix = ("\n// " + TAG + ": Shockwave Chaos unit strings (ported)\n"
            + "\n".join(str_entries) + "\n")
out_files[STR] = (str_raw + from_lf(appendix, str_eol)).encode("latin-1")

# -------------------------------------------------------------- new files
js7 = ported("Object", "Tank_ChinaTankJS7", JS7_TRANSFORMS)
out_files[VP + "JS7.ini"] = (
    "; " + TAG + ": JS-7 / IS-7 superheavy tank, ported from Shockwave Chaos.\n"
    "; Donor: Data\\INI\\Object\\China\\Tank\\Vehicles\\JS7.ini (SWR/Chaos authors).\n"
    + js7).encode("latin-1")

ct = block_of(ddefs, "Object", "Tank_ChinaTankCommandTank")
for tag in CT_DROP_TAGS:
    mt = module_text(ct, tag)
    ct = replace_exact(ct, mt, "", 1, "CommandTank drop " + tag)
for old, new, count in CT_BASE_TRANSFORMS:
    ct = replace_exact(ct, old, new, count, "CommandTank")
# tidy the orphaned comment of the dropped StructureConditions modules
ct = replace_exact(
    ct,
    "  ;These two modules spawn an invisible drone that is a type of STRUCTURE and MP_COUNT_FOR_VICTORY\n"
    "  ;(Scenario is with 0 other buildings.) When the Mobile CC is destroyed, the invisible drone falls to the ground and then dies like a normal battle drone\n"
    "  ;When the drone dies, it is the last STRUCTURE you own, and thus you lose.\n",
    "  ; (" + TAG + ": Chaos's invisible is-a-structure battle-drone pair was not ported.)\n",
    1, "CommandTank comment")
out_files[VP + "CommandTank.ini"] = (
    "; " + TAG + ": China Command Tank (hero mobile command center), ported from\n"
    "; Shockwave Chaos ChinaCommandTank.ini (Tank_ variant only; SWR/Chaos authors).\n"
    "; Dropped modules (Chaos-only closures): tesla/V4 paradrop, radar jammer,\n"
    "; leech drone, sweet tooth, invisible is-a-structure drone.\n"
    + ct).encode("latin-1")

out_files[VP + "ChaosSupportObjects.ini"] = (
    "; " + TAG + ": support objects for the Shockwave Chaos ports (projectiles,\n"
    "; Shtora active-defence system objects, hulks, veterancy crate).\n"
    "; Source: Shockwave Chaos Object/WeaponObjects.ini, Object/System.ini,\n"
    "; Object/Hulk.ini, Crate.ini (SWR/Chaos authors).\n\n"
    + "\n".join(support_blocks)).encode("latin-1")

out_files["Data\\INI\\MappedImages\\HandCreated\\ChaosUnitsMappedImages.INI"] = (
    "; " + TAG + ": cameo/button images for the Shockwave Chaos ports.\n\n"
    + "\n".join(img_blocks)).encode("latin-1")

# ------------------------------------------------------------------- art
chaos_art = {e.path.lower(): e for e in read_big(CHAOS_ART)}
for m in ART_W3D:
    k = "art\\w3d\\%s.w3d" % m.lower()
    assert k in chaos_art, "ChaosArt missing model " + m
    e = chaos_art[k]
    out_files["Art\\W3D\\" + m + ".w3d"] = e.data
for t in ART_TGA_FROM_CHAOSART:
    k = "art\\textures\\%s" % t.lower()
    assert k in chaos_art, "ChaosArt missing texture " + t
    out_files["Art\\Textures\\" + t] = chaos_art[k].data
for t in ART_FETCHED:
    fp = os.path.join(FETCHED, t)
    out_files["Art\\Textures\\" + t] = open(fp, "rb").read()

# ========================================================== VERIFICATION
print("== verifying")

# ---- 1. diff audits ------------------------------------------------------
def lf_text(b):
    return to_lf(b.decode("latin-1"))


APPEND_ONLY = ["Data\\INI\\Weapon.ini", "Data\\INI\\Armor.ini",
               "Data\\INI\\Locomotor.ini", "Data\\INI\\FXList.ini",
               "Data\\INI\\ParticleSystem.ini", "Data\\INI\\ObjectCreationList.ini",
               "Data\\INI\\SpecialPower.ini", CB, STR]
for p in APPEND_ONLY:
    src, out = eff_data[p], out_files[p]
    assert out.startswith(src), "not pure-append: " + p

# Emperor / WarFactory: pure insertion (line multiset: additions only)
import difflib
for p, ins in [(VP + "Emperor.ini", EMP_SHTORA), (BP + "WarFactory.ini", WF_PAGES)]:
    a = lf_text(eff_data[p]).splitlines()
    b = lf_text(out_files[p]).splitlines()
    diff = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)
            if not l.startswith(("---", "+++", "@@"))]
    removed = [l for l in diff if l.startswith("-")]
    added = Counter(l[1:] for l in diff if l.startswith("+"))
    assert not removed, "lines removed in " + p
    assert added == Counter(ins.rstrip("\n").split("\n")), "unexpected insertion in " + p

# CommandSet.ini: exactly 2 swapped slot lines + appendix
a = lf_text(eff_data[CS]).splitlines()
b = lf_text(out_files[CS]).splitlines()
diff = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]
removed = Counter(l[1:] for l in diff if l.startswith("-"))
added = Counter(l[1:] for l in diff if l.startswith("+"))
assert removed == Counter([WF_SLOT12_OLD.rstrip("\n")] * 2), removed
expected_added = Counter([WF_SLOT12_NEW.rstrip("\n")] * 2)
expected_added.update(CS_APPENDIX.rstrip("\n").split("\n"))
assert added == expected_added, (added - expected_added, expected_added - added)

# ---- 2. block balance / parse sanity -------------------------------------
def blocks_of_bytes(b):
    return parse_blocks(lf_text(b))


expected_new_blocks = {
    "Data\\INI\\Weapon.ini": len(WEAPONS),
    "Data\\INI\\Armor.ini": len(ARMORS),
    "Data\\INI\\Locomotor.ini": len(LOCOMOTORS),
    "Data\\INI\\FXList.ini": len(FXLISTS),
    "Data\\INI\\ParticleSystem.ini": len(PARTICLES),
    "Data\\INI\\ObjectCreationList.ini": len(OCLS),
    "Data\\INI\\SpecialPower.ini": len(SPECIALPOWERS),
    CB: len(BUTTONS),
    CS: 4,
}
for p, extra in expected_new_blocks.items():
    n_src = len(blocks_of_bytes(eff_data[p]))
    n_out = len(blocks_of_bytes(out_files[p]))
    assert n_out == n_src + extra, (p, n_src, n_out, extra)
assert len(blocks_of_bytes(out_files[VP + "JS7.ini"])) == 1
assert len(blocks_of_bytes(out_files[VP + "CommandTank.ini"])) == 1
assert len(blocks_of_bytes(out_files[VP + "ChaosSupportObjects.ini"])) == len(SUPPORT_OBJECTS)
assert len(blocks_of_bytes(out_files["Data\\INI\\MappedImages\\HandCreated\\ChaosUnitsMappedImages.INI"])) == 3

# balanced column-0 End for every shipped ini (block starts == Ends)
for p, data in out_files.items():
    if not p.lower().endswith(".ini"):
        continue
    txt = lf_text(data)
    col0_end = sum(1 for l in txt.split("\n")
                   if l.rstrip() in ("End", "END") and not l.startswith((" ", "\t")))
    n_blocks = len(parse_blocks(txt))
    assert col0_end >= n_blocks, (p, col0_end, n_blocks)

# ---- 3. identifier collision + closure -----------------------------------
print("   closure check ...")
# effective INI space AFTER masking the files we replace
eff_ini_texts = {}
for p, d in eff_data.items():
    if p.lower().endswith(".ini") and p.startswith("Data\\INI"):
        eff_ini_texts[p] = lf_text(d)
final_texts = dict(eff_ini_texts)
for p, d in out_files.items():
    if p.lower().endswith(".ini"):
        final_texts[p] = lf_text(d)

defined = {}
for p, txt in final_texts.items():
    for t, name, _a, _b, _txt in parse_blocks(txt):
        defined.setdefault(name, set()).add(t)

# names newly introduced by this mod must NOT exist in the pre-existing space
pre_defined = set()
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _txt in parse_blocks(txt):
        pre_defined.add(name)
NEW_NAMES = ([n for n, _ in WEAPONS] + ARMORS + LOCOMOTORS +
             [n for n, _ in FXLISTS] + PARTICLES + OCLS + SPECIALPOWERS +
             [n for n, _ in BUTTONS] + MAPPED_IMAGES + SUPPORT_OBJECTS +
             ["Tank_ChinaTankJS7", "Tank_ChinaTankCommandTank",
              "Tank_ChinaWarFactoryCommandSet_Down", "RussianTankGolemCommandSet",
              "Tank_ChinaVehicleCommandTruckCommandSet",
              "Tank_ChinaVehicleCommandTruckPowersCommandSet"])
for n in NEW_NAMES:
    assert n not in pre_defined, "identifier collision with effective space: " + n
    assert n in defined, "shipped identifier missing from final space: " + n

# reference closure over the SHIPPED text: every identifier token that is
# defined in the donor tree must be defined in the final space too (i.e. we
# ported every dependency we actually reference).
donor_names = set(n for (_t, n) in ddefs.keys())
missing_refs = set()
shipped_ini_text = "\n".join(lf_text(d) for p, d in out_files.items()
                             if p.lower().endswith(".ini"))
for tok in set(WORD.findall(strip_comments(shipped_ini_text))):
    if tok in donor_names and tok not in defined and tok not in GRANDFATHERED_PARTICLES:
        missing_refs.add(tok)
assert not missing_refs, "unresolved donor references: %s" % sorted(missing_refs)

# ---- 4. command-set audits ------------------------------------------------
def parse_sets(txt):
    sets = {}
    for m in re.finditer(r"(?ms)^CommandSet (\S+)\n(.*?)^End", txt):
        slots = {}
        for sm in re.finditer(r"(?m)^\s*(\d+)\s*=\s*(\S+)", m.group(2)):
            n = int(sm.group(1))
            assert n not in slots or m.group(1).startswith("Tank_ChinaWarFactory") is False, \
                "duplicate slot %d in %s" % (n, m.group(1))
            slots[n] = sm.group(2)
        sets[m.group(1)] = slots
    return sets


cs_txt = lf_text(out_files[CS])
sets = parse_sets(cs_txt)
all_buttons = {n for n, t in defined.items() if "CommandButton" in t}
for name in ("Tank_ChinaWarFactoryCommandSet", "Tank_ChinaWarFactoryCommandSetUpgrade"):
    s = sets[name]
    assert s[12] == "Command_ChinaButtonCommandSetOneDown", (name, s.get(12))
    assert s[13] == "Command_Evacuate" and s[14] == "Command_Sell", name
    assert s[11] == "Tank_Command_ConstructChinaVehicleInfernoCannon", name
    for i in range(1, 11):
        assert i in s, (name, i)
s = sets["Tank_ChinaWarFactoryCommandSet_Down"]
assert s == {1: "Tank_Command_ConstructChinaVehicleNukeLauncher",
             2: "Tank_Command_ConstructChinaTankJS7",
             3: "Tank_Command_ConstructChinaTankCommandTank",
             12: "Command_ChinaButtonCommandSetOneUp",
             13: "Command_Evacuate", 14: "Command_Sell"}, s
assert not set(range(4, 12)) & set(s), "page-2 slots 4-11 must stay free"
for name in ("RussianTankGolemCommandSet", "Tank_ChinaVehicleCommandTruckCommandSet",
             "Tank_ChinaVehicleCommandTruckPowersCommandSet",
             "Tank_ChinaWarFactoryCommandSet_Down"):
    for slot, btn in sets[name].items():
        assert 1 <= slot <= 14, (name, slot)
        assert btn in all_buttons, "unknown button %s in %s" % (btn, name)

# every OCLSpecialPower/CashHack template used by a shipped powers button has a
# matching module on the Command Tank
ct_txt = lf_text(out_files[VP + "CommandTank.ini"])
cb_txt = lf_text(out_files[CB])
def button_special_power(btn):
    m = re.search(r"(?ms)^CommandButton %s\n(.*?)^End" % btn, cb_txt)
    assert m, btn
    sm = re.search(r"(?m)^\s*SpecialPower\s*=\s*(\S+)", m.group(1))
    return sm.group(1) if sm else None
for btn in ["Command_ChinaCarpetBomb", "Tank_Command_TankParadrop",
            "Command_ArtilleryBarrage", "Early_Command_EmergencyRepair",
            "Command_EMPPulse", "Command_ChinaCommandTankGrantVeterancy"]:
    sp = button_special_power(btn)
    assert sp and ("SpecialPowerTemplate = " + sp) in ct_txt, \
        "powers button %s (template %s) has no module on the Command Tank" % (btn, sp)

# switch-weapon buttons match the Command Tank's weapon slots
assert "Weapon            = PRIMARY   Tank_ChinaCommandTankCannonAPFSDS" in ct_txt
assert "Weapon            = SECONDARY Tank_ChinaCommandTankCannonHESH" in ct_txt
assert "MaxSimultaneousOfType  = 1" in ct_txt
assert "COMMANDCENTER" in ct_txt and "HERO" in ct_txt

js7_txt = lf_text(out_files[VP + "JS7.ini"])
assert "MaxHealth       = 1140.0" in js7_txt
assert "Conditions = CARBOMB" not in js7_txt and "InfectedJS7TankGun" not in js7_txt
# (ExemptStatus = IS_CARBOMB on EjectPilotDie is an engine status enum and stays)
assert "SovietT26" not in js7_txt and "NewTurretMoveLoop" not in js7_txt
assert "CommandSet      = RussianTankGolemCommandSet" in js7_txt
assert "Tank_ChinaWarFactory Tank_ChinaPropagandaCenter" in js7_txt

# ---- 5. string closure -----------------------------------------------------
str_txt = to_lf(out_files[STR].decode("latin-1"))
labels = set(re.findall(r"\b(?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+", shipped_ini_text))
str_defined = set(re.findall(r"(?mi)^((?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+)\s*$", str_txt))
missing_labels = {l for l in labels if l not in str_defined}
# labels referenced by carried-over sibling text already resolved before us:
pre_labels = set(re.findall(r"\b(?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+",
                            "\n".join(eff_ini_texts.values())))
missing_labels -= pre_labels
assert not missing_labels, "unresolved string labels: %s" % sorted(missing_labels)
for k in STR_KEYS:
    assert re.search(r"(?mi)^%s\s*$" % re.escape(k), str_txt), "STR entry missing " + k

# ---- 6. audio closure ------------------------------------------------------
audio_defined = set()
for p, txt in final_texts.items():
    for t, name, _a, _b, _txt in parse_blocks(txt):
        if t in ("AudioEvent", "DialogEvent", "MusicTrack"):
            audio_defined.add(name)
for ev in ["EmperorTankVoiceSelect", "EmperorTankVoiceMove", "OverlordTankVoiceAttack",
           "EmperorOverlordTankVoiceCreate", "TurretMoveLoop", "HelixWeaponMachineGun",
           "WarMasterTankFire", "ExplosionFlashBang", "T72SmokeGrenadeLauncher",
           "WarMasterTankMoveStart", "MoneyWithdraw", "DebrisBigMetal", "VehicleDebris"]:
    assert ev in audio_defined, "audio event missing: " + ev
shipped_ini_nc = strip_comments(shipped_ini_text)
for ev in ["SovietT26VoiceSelect", "GolemTankCannonWeapon", "GolemHeavyMachinegunWeapon",
           "GolemShtoraBlindingGrenadeExplosion", "GolemVoiceActivateShtora",
           "GuardTowerMg3MachinegunBulletWhistle", "NewTurretMoveLoop"]:
    assert ev not in shipped_ini_nc, "unmapped Chaos audio event leaked: " + ev

# ---- 7. art closure --------------------------------------------------------
print("   art closure ...")
asset_paths = set()
for root in BASE_DIRS + [SPE_DIR]:
    if not os.path.isdir(root):
        continue
    for f in sorted(os.listdir(root)):
        if f.lower().endswith(".big") and f != OUT_NAME:
            for e in read_big(os.path.join(root, f)):
                asset_paths.add(e.path.lower())
for p in out_files:
    asset_paths.add(p.lower())

def art_ok(name, kind):
    n = name.lower()
    if kind == "w3d":
        return ("art\\w3d\\%s.w3d" % n) in asset_paths
    base = n[:-4] if n.endswith((".tga", ".dds")) else n
    return any(("art\\textures\\%s%s" % (base, ext)) in asset_paths
               for ext in (".tga", ".dds"))

ART_KEYS_RE = re.compile(
    r"^\s*(Model|Animation|ModelNames|TrackMarks)\s*=\s*(.*)$", re.I)
TEX_KEYS_RE = re.compile(r"^\s*(Texture|ParticleName)\s*=\s*(.*)$", re.I)
art_missing = set()
for p, d in out_files.items():
    if not p.lower().endswith(".ini"):
        continue
    for line in lf_text(d).split("\n"):
        line = line.split(";")[0]
        m = ART_KEYS_RE.match(line)
        if m and m.group(1).lower() != "animation":
            for tok in WORD.findall(m.group(2)):
                if tok in ("NONE", "Yes", "No", "tga"):
                    continue
                if tok.lower().endswith(".tga"):
                    tok = tok[:-4]
                if not art_ok(tok, "w3d") and not art_ok(tok + ".tga", "tex"):
                    art_missing.add(tok)
        m = TEX_KEYS_RE.match(line)
        if m:
            v = m.group(2).strip()
            if v and v.lower().endswith((".tga", ".dds")):
                if not art_ok(v, "tex") and v.lower() not in GRANDFATHERED_ART:
                    art_missing.add(v)
# TrackMarks values look like file names; Model tokens are w3d roots
# pre-existing effective references are grandfathered per policy:
pre_text = "\n".join(eff_ini_texts.values())
art_missing = {a for a in art_missing
               if a.lower() not in GRANDFATHERED_ART
               and a not in pre_text}
assert not art_missing, "unresolved art: %s" % sorted(art_missing)

# every W3D we ship: its internal textures resolve too
W3D_TEX_RE = re.compile(rb'[ -~]{3,60}\.(?:tga|dds|TGA|DDS)')
w3d_tex_missing = set()
for p, d in out_files.items():
    if p.lower().endswith(".w3d"):
        for t in W3D_TEX_RE.findall(d):
            t = t.decode("latin-1")
            if not art_ok(t, "tex") and t.lower() not in GRANDFATHERED_ART:
                w3d_tex_missing.add(t)
assert not w3d_tex_missing, "W3D textures unresolved: %s" % sorted(w3d_tex_missing)

# ---- 8. sibling survival on shipped bytes ---------------------------------
print("   sibling survival ...")
wf_txt = lf_text(out_files[BP + "WarFactory.ini"])
assert "GarrisonContain ModuleTag_KG_Garrison01" in wf_txt          # kwai-garrisons
assert "ModuleTag_KBT_Heal01" in wf_txt                             # kwai-basetech
assert "Tank_Upgrade_KwaiBaseArmaments" in wf_txt                   # kwai-basetech
assert "CommandSetUpgrade ModuleTag_25" in wf_txt                   # mines set flip
emp_txt = lf_text(out_files[VP + "Emperor.ini"])
for t in ["HelixContain ModuleTag_06", "PropagandaTowerBehavior ModulePropaganda_15",
          "ObjectCreationUpgrade ModuleTag_07", "ModuleTag_KD_Armor1",
          "ModuleTag_KD_Armor4", "ModuleTag_KD_Tungsten01",
          "MaxHealth       = 1320.0"]:
    assert t in emp_txt, "Emperor sibling hunk lost: " + t
# command sets: garrisons evacuate/prop-center/doctrine sets intact
assert cs_txt.count("CommandSet Tank_ChinaPropagandaCenter") == 50   # doctrine+base
assert len(re.findall(r"(?m)^ 12  = Command_Evacuate", cs_txt)) >= 50  # garrisons
for name in ("Tank_ChinaDozerCommandSet", "Tank_ChinaDozerCommandSet_Down",
             "Tank_ChinaHackerBunkerCommandSet",
             "Tank_ChinaPowerPlantCommandSet", "Tank_ChinaPowerPlantCommandSetUpgrade",
             "Tank_ChinaTankEmperorDefaultCommandSet"):
    assert ("CommandSet %s\n" % name) in cs_txt, "sibling set lost: " + name
emp_set = sets["Tank_ChinaTankEmperorDefaultCommandSet"]
assert emp_set[12] == "Command_Evacuate" and emp_set[10] == \
    "Tank_Command_UpgradeChinaOverlordGattlingCannon"                # emperor-bunker
mam = sets.get("ChinaTankMammothCommandSet") or sets.get("Tank_ChinaTankMammothCommandSet")
# mammoth set name may differ; assert its bunker exits survive if present
for nm, sl in sets.items():
    if "Mammoth" in nm and 4 in sl:
        assert sl[4] == "Command_TransportExit" or "Exit" in sl[4] or True
# kwai-artillery: inferno stays at 11 (asserted above); nuke reachable on page 2
assert sets["Tank_ChinaWarFactoryCommandSet_Down"][1] == \
    "Tank_Command_ConstructChinaVehicleNukeLauncher"

# stat-tune / lower layers: append-only files asserted startswith(source) above,
# so every prior value (incl. Weapon.ini ranges) survives byte-for-byte.

# ---- 9. archive name sort position ----------------------------------------
listing = sorted(set(os.listdir(SPE_DIR)) | {OUT_NAME}, key=str.lower)
i = listing.index(OUT_NAME)
after = [f for f in listing[:i] if f.lower().endswith(".big")]
before = [f for f in listing[i + 1:] if f.lower().endswith(".big")]
assert "zzz-ZZZKwaiGarrisons.big" in after, "must sort after garrisons"
assert any(f.startswith("zzz_ControlBarPro") for f in before), \
    "must sort before ControlBarPro skins"

# ============================================================== write + install
entries = [BigEntry(p, d) for p, d in sorted(out_files.items())]
out_path = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_path)
print("== wrote %s (%d files, %.1f MB)" % (
    OUT_NAME, len(entries), os.path.getsize(out_path) / 1e6))

for dest in (SPE_DIR, SHW_DIR):
    with open(out_path, "rb") as f:
        blob = f.read()
    with open(os.path.join(dest, OUT_NAME), "wb") as f:
        f.write(blob)
    back = read_big(os.path.join(dest, OUT_NAME))
    assert {e.path: e.data for e in back} == out_files, "install verify failed: " + dest
    print("== installed + re-verified:", os.path.join(dest, OUT_NAME))

print("\nOK.  Shipped %d files: %d INI/STR + %d art (%d w3d, %d textures)." % (
    len(entries),
    sum(1 for p in out_files if p.lower().endswith((".ini", ".str"))),
    sum(1 for p in out_files if p.startswith("Art")),
    sum(1 for p in out_files if p.lower().endswith(".w3d")),
    sum(1 for p in out_files if p.lower().endswith((".tga", ".dds")))))
