"""Block-editing helpers + the full port recipe (blocks, edits, remaps)
for the ROTR infantry port.  build.py drives this; integrate.py reuses the
fragment outputs.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))
from iniblocks import load_tree, parse_blocks  # noqa: E402
import portdefs  # noqa: E402

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")


def strip_comments_line(line):
    i = line.find(";")
    j = line.find("//")
    if i >= 0 and (j < 0 or i < j):
        return line[:i]
    if j >= 0:
        return line[:j]
    return line


# ---------------------------------------------------------------- editing
def strip_submodule(text, opener_re):
    """Remove a sub-block whose opener line matches opener_re (regex on the
    stripped line).  The block ends at the first following line that is
    'End' at the same indentation.  Returns (new_text, removed_count)."""
    lines = text.split("\n")
    out = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)" + opener_re, strip_comments_line(line).rstrip())
        if m:
            indent = m.group(1)
            j = i + 1
            end_re = re.compile(r"^" + re.escape(indent) + r"End\s*$")
            while j < len(lines):
                if end_re.match(strip_comments_line(lines[j]).rstrip()):
                    break
                j += 1
            if j >= len(lines):
                raise ValueError("unterminated sub-block for %r" % opener_re)
            removed += 1
            i = j + 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out), removed


def strip_module(text, tag):
    new, n = strip_submodule(
        text, r"Behavior\s*=\s*[A-Za-z0-9_]+\s+%s\b.*$" % re.escape(tag))
    if n != 1:
        raise ValueError("module strip %s: removed %d blocks (want 1)" % (tag, n))
    return new


def strip_lines(text, line_re):
    """Remove whole lines matching line_re (on comment-stripped content)."""
    rx = re.compile(line_re)
    out = []
    removed = 0
    for line in text.split("\n"):
        if rx.search(strip_comments_line(line)):
            removed += 1
            continue
        out.append(line)
    return "\n".join(out), removed


def retoken(text, mapping):
    """Word-boundary token replacement (also inside comments, harmless)."""
    if not mapping:
        return text
    rx = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?::[A-Za-z0-9_\-]+)?")

    def sub(m):
        return mapping.get(m.group(0), m.group(0))
    return rx.sub(sub, text)


# ---------------------------------------------------------------- recipe
# FX voice-wrapper remaps (donor FXLists that only wrap a ROTR death voice;
# FX_GIDie is the canonical vanilla infantry death FX):
FX_REMAP = {
    "FX_ShmelTrooperDie": "FX_GIDie",
    "FX_ShmelTrooperDieByFlame": "FX_GIDie",
    "FX_ShmelTrooperDieByToxin": "FX_GIDie",
    "FX_ShmelTrooperDieByTesla": "FX_GIDie",
    "FX_ShockTrooperDie": "FX_GIDie",
    "FX_ShockTrooperDieFire": "FX_GIDie",
    "FX_ShockTrooperDieToxin": "FX_GIDie",
    "FX_ShockTrooperDieTesla": "FX_GIDie",
}

# ROTR audio events -> base events (verified in base audio INI space by
# the build's audio scan; build fails loudly on any unmapped donor event).
AUDIO_REMAP = {
    # Shmel Trooper: China Tank Hunter (vanilla missile infantry)
    "ShmelTrooperVoiceSelect": "TankHunterVoiceSelect",
    "ShmelTrooperVoiceMove": "TankHunterVoiceMove",
    "ShmelTrooperVoiceAttack": "TankHunterVoiceAttack",
    "ShmelTrooperVoiceFear": "TankHunterVoiceFear",
    "ShmelTrooperVoiceCreate": "TankHunterVoiceCreate",
    "ShmelTrooperVoiceSmokeAttack": "TankHunterVoiceAttack",
    "ShmelTrooperVoiceAntiToxinAttack": "TankHunterVoiceAttack",
    "ShmelTrooperVoiceDie": "TankHunterVoiceDie",
    # Shock Trooper: ShockWave China Pyro (suited flame trooper)
    "ShockTrooperVoiceSelect": "PyroVoiceSelect",
    "ShockTrooperVoiceMove": "PyroVoiceMove",
    "ShockTrooperVoiceAttack": "PyroVoiceAttack",
    "ShockTrooperVoiceAttackTesla": "PyroVoiceAttack",
    "ShockTrooperVoiceFear": "PyroVoiceFear",
    "ShockTrooperVoiceCreate": "PyroVoiceCreate",
    "ShockTrooperVoiceGarrison": "PyroVoiceGarrison",
    "ShockTrooperVoiceModeRifle": "PyroVoiceMove",
    "ShockTrooperVoiceModeTeslaGun": "PyroVoiceMove",
    # weapon / FX sounds
    "ShmelRocketLauncherWeapon": "TankHunterWeapon",
    "ShmelRocketExplosion": "ExplosionFire",
    "ShockTrooperRifleWeapon": "RocketBuggyWeapon",
    "ShockTrooperTeslaWeaponSound": "AvengerPointDefenseLaserPulse",
    # sounds inside ported FXLists
    "ShockTrooperRocketElectricExplosion": "ExplosionPatriotEMP",
    "GenericAutoCannonDetonationImpact": "ExplosionRocketBuggyMissile",
    "InfantryTeslaDeathShock": "ExplosionPatriotEMP",
    "MoleBombDirstSound": "ExplosionDirt",
    "ShmelRocketAntiToxinActivated": "ExplosionFlashBang",
    "ShmelRocketAntiToxinDetonation": "ExplosionFlashBang",
}

PREREQ_REMAP = {
    "RussiaWarFactory": "Tank_ChinaWarFactory",
    "RussiaWeaponsBunker": "Tank_ChinaWarFactory",
}

# what ships where ------------------------------------------------------
OBJECT_FILES = {
    "Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShmelTrooper.ini": [
        ("Object", "RussianInfantryShmelTrooper"),
        ("Object", "ShmelTrooperRocket"),
        ("Object", "ShmelTrooperSmokeRocketProjectile"),
        ("ObjectReskin", "ShmelTrooperSmokeRocketHeroicProjectile"),
        ("Object", "ShmelTrooperAntiToxinRocketProjectile"),
        ("ObjectReskin", "ShmelTrooperAntiToxinRocketHeroicProjectile"),
        ("Object", "RussianShmelTrooperAntiToxinFoam"),
        ("Object", "RussianSmokeGrenadeSmokeScreen"),
        ("Object", "ShmellBurningEmbersFireField"),
        ("Object", "GenericHitScanProjectile"),
    ],
    "Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShockTrooper.ini": [
        ("Object", "RussiaInfantryShockTrooper"),
        ("Object", "RussiaInfantryShockTrooper_Var1"),
        ("ObjectReskin", "RussiaInfantryShockTrooper_Var2"),
        ("ObjectReskin", "RussiaInfantryShockTrooper_Var3"),
        ("Object", "ShockTrooperTeslaChainNode"),
        ("Object", "ShockTrooperTeslaChainNodeHeroic"),
        ("Object", "TeslaTrooperLaserBeam"),
    ] + [("Object", "TeslaTrooperElectricBolt%d" % i) for i in range(1, 9)] + [
        ("Object", "HeroicTeslaTrooperLaserBeam"),
    ] + [("Object", "HeroicTeslaTrooperElectricBolt%d" % i) for i in range(1, 9)] + [
        ("Object", "TeslaInfantry"),
    ],
}

SHARED_APPENDS = {
    "Weapon.ini": [
        "RussiaShmellTrooperMissileLauncher",
        "RussiaShmellTrooperSmokeMissileLauncher",
        "RussiaShmellTrooperSmokeMissileLauncherHeroic",
        "RussiaShmellTrooperAntiToxinMissileLauncher",
        "RussiaShmellTrooperAntiToxinMissileLauncherHeroic",
        "RussiaShmellTrooperSmokeMissilePellets",
        "RussiaShmellTrooperExtraDamageWithInfantryMunitionUpgrade",
        "RussianShmelTrooperAntiToxinSmokeWeapon",
        "RussianSmokeGrenadeSmokeScreenWeapon",
        "PyroFireWalFieldWeapon",
        "ShockTrooperTeslaWeapon",
        "ShockTrooperTeslaSubdualWeapon",
        "ShockTrooperTeslaArcWeapon",
        "HeroicShockTrooperTeslaWeapon",
        "HeroicShockTrooperTeslaSubdualWeapon",
        "HeroicShockTrooperTeslaArcWeapon",
        "ShockTrooperTeslaChainZap",
        "HeroicShockTrooperTeslaChainZap",
    ],
    "Armor.ini": ["ShockTrooperArmor", "InvulnerableArmorAll"],
    "Locomotor.ini": [
        "ShockTrooperLocomotor", "ShmelRocketLocomotor",
    ],
    "FXList.ini": [
        "FX_MoleBombEnterOrExitGround",
        "FX_ShmelTrooperAntiToxinRocketExplosion",
        "WeaponFX_ShmelRocketExplosion",
        "WeaponFX_ShmelRocketExplosionUpgraded",
        "WeaponFX_ShmelTrooperAntiToxinSmoke",
        "FX_ShockTrooperElectricRocketExplosion",
        "FX_IfantryTeslaDie",
    ],
    "ParticleSystem.ini": [
        "ShmelRocketExhaust", "HeroicShmelRocketExhaust", "ShmelRocketLenzflare",
        "ShmelExplosion", "ShmelDetonationDustWave",
        "ShmelAntiToxinRocketExhaust", "ShmelRocketAntiToxinDebris",
        "ShmelRocketAntiToxinDetonationCloud", "ShmelRocketAntiToxinExplosion",
        "ShmelRocketAntiToxinSmoke",
        "NapalmPoolSmoke", "ShmelPoolFire", "ShmelPoolFireMainRing",
        "ShockTrooperTeslaBlast",
        "TeslaTrooperFlare", "HeroicTeslaTrooperFlare",
    ],
    "ObjectCreationList.ini": [
        "OCL_RussiaExplodedDeath", "OCL_RussiaExplodedDeathShockTrooper",
        "OCL_ShmelTrooperSmokeScreen", "OCL_ShmelTrooperAntiToxinFoam",
        "OCL_ShmellRocketFire",
        "OCL_ShockTrooperTeslaChain", "OCL_ShockTrooperTeslaChainHeroic",
        "OCL_TeslaDeathInfantry", "OCL_ViralInfantryDeath",
    ],
}

MAPPED_IMAGES = [
    "SRShmelTrooper", "SRShmelTrooper_L", "SRShockTrooper", "SRShockTrooper_L",
    "SSRocketShmelSmoke", "SSRocketShmelAntiTox",
]

# extra death-module strips shared by both units (cryo chain dropped)
CRYO_TAG = "ModuleTag_03231"

# =====================================================================
# Shock Trooper tesla rework: authored blocks (override donor where the
# same name exists).  Design notes in README ("Shock Trooper rework").
# Armor math (effective Armor.ini): TankArmor MELEE 0% / AP 100% /
# FLAME 25%; HumanArmor AP 10% / FLAME 150%.  Hence AP beam for vehicles,
# FLAME arc for the infantry one-shot (110 * 1.5 = 165 post-armor).
# All weapons explicitly cannot target aircraft.
# =====================================================================
_ANTI_AIR_OFF = ("  AntiGround              = Yes\n"
                 "  AntiAirborneVehicle     = No\n"
                 "  AntiAirborneInfantry    = No\n")

_BONUS_LINES = (
    "  WeaponBonus             = GARRISONED RANGE  145%%\n"
    "  WeaponBonus             = GARRISONED DAMAGE 125%%\n"
    "  WeaponBonus             = PLAYER_UPGRADE RANGE  145%%\n"
    "  WeaponBonus             = PLAYER_UPGRADE DAMAGE 125%%\n")


def _tesla_beam(name, dmg, laser):
    return ("Weapon %s\n"
            "  ; tesla shock beam: the anti-vehicle component (AP because base\n"
            "  ; TankArmor takes 0%% MELEE damage -- the donor value was dead)\n"
            "  PrimaryDamage           = %s\n"
            "  PrimaryDamageRadius     = 5.0\n"
            "  AttackRange             = 140.0\n"
            "  DamageType              = ARMOR_PIERCING\n"
            "  DeathType               = POISONED_GAMMA ; tesla death animation\n"
            "  WeaponSpeed             = 99999\n"
            "  LaserName               = %s\n"
            "  LaserBoneName           = MUZZLE01\n"
            "  FireSound               = AvengerPointDefenseLaserPulse\n"
            "  DelayBetweenShots       = 1200\n" +
            _ANTI_AIR_OFF + _BONUS_LINES +
            "End\n") % (name, dmg, laser)


def _tesla_subdual(name, dmg, laser):
    return ("Weapon %s\n"
            "  ; subdual buildup rider: vehicles accumulate this until it\n"
            "  ; passes their MaxHealth -> DISABLED_SUBDUED for a few seconds\n"
            "  ; (decays at the target body's SubdualDamageHealRate/Amount)\n"
            "  PrimaryDamage           = %s\n"
            "  PrimaryDamageRadius     = 10.0\n"
            "  AttackRange             = 140.0\n"
            "  DamageType              = SUBDUAL_UNRESISTABLE\n"
            "  DeathType               = POISONED_GAMMA\n"
            "  WeaponSpeed             = 99999\n"
            "  LaserName               = %s\n"
            "  LaserBoneName           = MUZZLE01\n"
            "  DelayBetweenShots       = 1200\n"
            "  RadiusDamageAffects     = ENEMIES NEUTRALS\n" +
            _ANTI_AIR_OFF +
            "End\n") % (name, dmg, laser)


def _tesla_arc(name, dmg, ocl):
    return ("Weapon %s\n"
            "  ; anti-infantry fry + chain trigger: FLAME one-shots standard\n"
            "  ; infantry (<=%s*1.5 HP) and BURNED lights them up; the hitscan\n"
            "  ; projectile detonation spawns the chain-lightning node\n"
            "  PrimaryDamage           = %s\n"
            "  PrimaryDamageRadius     = 20.0\n"
            "  AttackRange             = 140.0\n"
            "  DamageType              = FLAME\n"
            "  DeathType               = BURNED\n"
            "  WeaponSpeed             = 99999\n"
            "  ProjectileObject        = GenericHitScanProjectile\n"
            "  ProjectileDetonationFX  = FX_ShockTrooperElectricRocketExplosion\n"
            "  ProjectileDetonationOCL = %s\n"
            "  DelayBetweenShots       = 1200\n"
            "  RadiusDamageAffects     = ENEMIES NEUTRALS\n" +
            _ANTI_AIR_OFF +
            "End\n") % (name, dmg, dmg, ocl)


def _chain_zap(name, dmg, laser):
    return ("Weapon %s\n"
            "  ; the chain-lightning arc fired by the spawned node\n"
            "  PrimaryDamage           = %s\n"
            "  PrimaryDamageRadius     = 12.0\n"
            "  AttackRange             = 90.0\n"
            "  DamageType              = FLAME\n"
            "  DeathType               = BURNED\n"
            "  WeaponSpeed             = 99999\n"
            "  LaserName               = %s\n"
            "  FireSound               = AvengerPointDefenseLaserPulse\n"
            "  DelayBetweenShots       = 500\n"
            "  RadiusDamageAffects     = ENEMIES NEUTRALS\n" +
            _ANTI_AIR_OFF +
            "End\n") % (name, dmg, laser)


def _chain_node(name, zap, minlife, maxlife):
    return """Object %s
  ; invisible short-lived arc source spawned at the tesla-arc impact point;
  ; auto-acquires a nearby ground enemy and zaps it (the chain lightning)
  EditorSorting = SYSTEM
  Side = ChinaTankGeneral
  KindOf = CAN_ATTACK NO_COLLIDE IMMOBILE UNATTACKABLE
  RadarPriority = NOT_ON_RADAR
  TransportSlotCount = 0

  Draw = W3DModelDraw ModuleTag_Draw01
    DefaultConditionState
      Model = NONE
    End
  End

  ArmorSet
    Conditions      = None
    Armor           = InvulnerableAllArmor
    DamageFX        = EmptyDamageFX
  End

  WeaponSet
    Conditions = None
    Weapon     = PRIMARY %s
  End

  VisionRange = 90
  ShroudClearingRange = 90

  Body = ActiveBody ModuleTag_Body01
    MaxHealth       = 50.0
    InitialHealth   = 50.0
  End

  Behavior = AIUpdateInterface ModuleTag_AI01
    Turret
      TurretTurnRate = 3600
      ControlledWeaponSlots = PRIMARY
    End
    AutoAcquireEnemiesWhenIdle = Yes
    MoodAttackCheckRate = 100
  End

  Behavior = LifetimeUpdate ModuleTag_Life01
    MinLifetime = %d
    MaxLifetime = %d
  End

  Behavior = DestroyDie ModuleTag_Die01
  End

  Geometry = CYLINDER
  GeometryMajorRadius = 1.0
  GeometryMinorRadius = 1.0
  GeometryHeight = 8.0
  GeometryIsSmall = Yes
End
""" % (name, zap, minlife, maxlife)


AUTHORED = {
    "ShockTrooperTeslaWeapon": _tesla_beam(
        "ShockTrooperTeslaWeapon", "60.0", "TeslaTrooperLaserBeam"),
    "HeroicShockTrooperTeslaWeapon": _tesla_beam(
        "HeroicShockTrooperTeslaWeapon", "80.0", "HeroicTeslaTrooperLaserBeam"),
    "ShockTrooperTeslaSubdualWeapon": _tesla_subdual(
        "ShockTrooperTeslaSubdualWeapon", "250.0", "TeslaTrooperLaserBeam"),
    "HeroicShockTrooperTeslaSubdualWeapon": _tesla_subdual(
        "HeroicShockTrooperTeslaSubdualWeapon", "325.0",
        "HeroicTeslaTrooperLaserBeam"),
    "ShockTrooperTeslaArcWeapon": _tesla_arc(
        "ShockTrooperTeslaArcWeapon", "110.0", "OCL_ShockTrooperTeslaChain"),
    "HeroicShockTrooperTeslaArcWeapon": _tesla_arc(
        "HeroicShockTrooperTeslaArcWeapon", "140.0",
        "OCL_ShockTrooperTeslaChainHeroic"),
    "ShockTrooperTeslaChainZap": _chain_zap(
        "ShockTrooperTeslaChainZap", "100.0", "TeslaTrooperLaserBeam"),
    "HeroicShockTrooperTeslaChainZap": _chain_zap(
        "HeroicShockTrooperTeslaChainZap", "120.0",
        "HeroicTeslaTrooperLaserBeam"),
    "ShockTrooperTeslaChainNode": _chain_node(
        "ShockTrooperTeslaChainNode", "ShockTrooperTeslaChainZap", 1100, 1300),
    "ShockTrooperTeslaChainNodeHeroic": _chain_node(
        "ShockTrooperTeslaChainNodeHeroic", "HeroicShockTrooperTeslaChainZap",
        1400, 1600),
    "OCL_ShockTrooperTeslaChain": """ObjectCreationList OCL_ShockTrooperTeslaChain
  CreateObject
    ObjectNames = ShockTrooperTeslaChainNode
    Count       = 1
    Disposition = ON_GROUND_ALIGNED
    IgnorePrimaryObstacle = Yes
  End
End
""",
    "OCL_ShockTrooperTeslaChainHeroic": """ObjectCreationList OCL_ShockTrooperTeslaChainHeroic
  ; heroic Shock Troopers chain from TWO nodes (more arcs, longer-lived)
  CreateObject
    ObjectNames = ShockTrooperTeslaChainNodeHeroic
    Count       = 1
    Disposition = ON_GROUND_ALIGNED
    IgnorePrimaryObstacle = Yes
  End
  CreateObject
    ObjectNames = ShockTrooperTeslaChainNodeHeroic
    Count       = 1
    Offset      = X:14.0 Y:10.0 Z:0.0
    Disposition = ON_GROUND_ALIGNED
    IgnorePrimaryObstacle = Yes
  End
End
""",
}


# ---- tesla-only draw (replaces the donor RIDER1/RIDER2 dual-mode draw) ----
def shock_tesla_draw(skin):
    """skin: '' | '2' | '3' -> RITslTrp[skin]_SKN.  Donor RIDER2 states with
    the rider condition stripped; FIRING_B/C aliases cover the subdual and
    arc weapon slots."""
    m = "RITslTrp%s_SKN" % skin
    return """  Draw = W3DModelDraw ModuleTag_01

    OkToChangeModelColor = Yes

    ; ---- standing (tesla gun is the only armament now)
    DefaultConditionState
      Model = %(m)s
      IdleAnimation = NIGATT_SKL.NIGATT_IDC 0 35
      IdleAnimation = NIGATT_SKL.NIGATT_IDA
      IdleAnimation = NIGATT_SKL.NIGATT_IDB
      IdleAnimation = NIGATT_SKL.NIGATT_STA
      AnimationMode = ONCE
      TransitionKey = TRANS_STANDING_TESLA
    End

    ; ---- attack
    ConditionState = FIRING_A
      Animation = NIGATT_SKL.NIGATT_ATA1
      AnimationMode = LOOP
      TransitionKey = None
    End
    AliasConditionState = BETWEEN_FIRING_SHOTS_A
    AliasConditionState = RELOADING_A
    AliasConditionState = FIRING_B
    AliasConditionState = BETWEEN_FIRING_SHOTS_B
    AliasConditionState = RELOADING_B
    AliasConditionState = FIRING_C
    AliasConditionState = BETWEEN_FIRING_SHOTS_C
    AliasConditionState = RELOADING_C

    ConditionState = MOVING FIRING_A
      Animation = NIGATT_SKL.NIGATT_ATB1 20
      AnimationMode = LOOP
      Flags = RANDOMSTART
      TransitionKey = None
      ParticleSysBone = None InfantryDustTrails
    End
    AliasConditionState = MOVING BETWEEN_FIRING_SHOTS_A
    AliasConditionState = MOVING RELOADING_A
    AliasConditionState = MOVING FIRING_B
    AliasConditionState = MOVING BETWEEN_FIRING_SHOTS_B
    AliasConditionState = MOVING RELOADING_B
    AliasConditionState = MOVING FIRING_C
    AliasConditionState = MOVING BETWEEN_FIRING_SHOTS_C
    AliasConditionState = MOVING RELOADING_C

    ; ---- moving
    ConditionState = MOVING
      Animation = NIGATT_SKL.NIGATT_WKA 20
      AnimationMode = LOOP
      Flags = RANDOMSTART
      TransitionKey = None
      ParticleSysBone  = None InfantryDustTrails
    End
    AliasConditionState = ATTACKING MOVING

    ; ---- dying
    ConditionState      = DYING
      Model             = %(m)s
      Animation         = NIGATT_SKL.NIGATT_DTA
      Animation         = NIGATT_SKL.NIGATT_DTB
      AnimationMode     = ONCE
      TransitionKey     = TRANS_TESLA_DYING
    End

    TransitionState     = TRANS_TESLA_DYING TRANS_TESLA_FLAILING
      Model             = %(m)s
      Animation         = NIGATT_SKL.NIGATT_ADTD1
      AnimationMode     = ONCE
    End

    ConditionState      = DYING EXPLODED_FLAILING
      Model             = %(m)s
      Animation         = NIGATT_SKL.NIGATT_ADTD2
      AnimationMode     = LOOP
      TransitionKey     = TRANS_TESLA_FLAILING
    End

    ConditionState      = DYING EXPLODED_BOUNCING
      Model             = %(m)s
      Animation         = NIGATT_SKL.NIGATT_ADTD3
      AnimationMode     = ONCE
      TransitionKey     = None
    End

  End

  Draw = W3DModelDraw ModuleTag_LaunchBone01
    DefaultConditionState
      Model               = RIShkTrp_B
      WeaponFireFXBone    = PRIMARY Muzzle
      WeaponLaunchBone    = PRIMARY Muzzle
      WeaponFireFXBone    = TERTIARY Muzzle
      WeaponLaunchBone    = TERTIARY Muzzle
    End
  End
""" % {"m": m}


SHOCK_WEAPONSETS = """  WeaponSet
    Conditions        = None
    Weapon            = PRIMARY   ShockTrooperTeslaWeapon
    Weapon            = SECONDARY ShockTrooperTeslaSubdualWeapon
    Weapon            = TERTIARY  ShockTrooperTeslaArcWeapon
    ShareWeaponReloadTime = Yes
  End

  WeaponSet
    Conditions        = HERO
    Weapon            = PRIMARY   HeroicShockTrooperTeslaWeapon
    Weapon            = SECONDARY HeroicShockTrooperTeslaSubdualWeapon
    Weapon            = TERTIARY  HeroicShockTrooperTeslaArcWeapon
    ShareWeaponReloadTime = Yes
  End
"""

SHOCK_COST = ("800", "10.0")   # donor 450 / 7.0 -- elite repricing


def load_donor():
    return load_tree(portdefs.DONOR_INI)


def edit_block(t, name, text):
    """Apply the per-block structural edits to a donor block (before the
    global token renames/remaps).  Returns final text."""
    for tag in portdefs.MODULE_STRIPS.get(name, []):
        text = strip_module(text, tag)
    if name in ("RussianInfantryShmelTrooper", "RussiaInfantryShockTrooper_Var1"):
        text = strip_module(text, CRYO_TAG)          # LASERED cryo death chain
        # catch-all death module owns LASERED and EXTRA_8 again:
        def fix_catchall(m):
            return m.group(0).replace(" -LASERED", "").replace(" -EXTRA_8", "")
        text, n = re.subn(r"^\s*DeathTypes\s*=\s*ALL[^\n]*$", fix_catchall,
                          text, count=1, flags=re.M)
        assert n == 1, "catch-all DeathTypes line not found in %s" % name
        # drop upgrade cameos of unreachable Russia upgrades
        text, _ = strip_lines(text, r"^\s*UpgradeCameo\d\s*=")
    if name == "RussianInfantryShmelTrooper":
        # PLAYER_UPGRADE weapon sets reference the dropped Upgraded weapons
        text, n = strip_player_upgrade_weaponsets(text)
        assert n == 2, "expected 2 PLAYER_UPGRADE weaponsets, removed %d" % n
    if name == "ShmelTrooperRocket":
        # thermobaric fire-field gate: Russia's Larger Clips -> Kwai-reachable
        # Black Napalm (re-side of the donor's upgrade gate; see README)
        text, n = re.subn(r"TriggeredBy\s*=\s*Upgrade_RussiaLargerClips",
                          "TriggeredBy  = Upgrade_ChinaBlackNapalm", text)
        assert n == 1, "fire-field TriggeredBy not found"

    # ---- Shock Trooper tesla rework ------------------------------------
    if name == "RussiaInfantryShockTrooper":
        # the buildable shell still carried the rocket-trooper preview draw;
        # swap it to the tesla model so the RIShkTrp skin/anims can drop
        text, n = strip_submodule(
            text, r"Draw\s*=\s*W3DModelDraw\s+ModuleTag_01\b.*$")
        assert n == 1, "shell draw not found"
        marker = "  ; set cost and time fields"
        assert marker in text
        text = text.replace(marker, (
            "  Draw = W3DModelDraw ModuleTag_01\n"
            "    DefaultConditionState\n"
            "      Model               = RITslTrp_SKN\n"
            "      IdleAnimation       = NIGATT_SKL.NIGATT_IDC 0 35\n"
            "      IdleAnimation       = NIGATT_SKL.NIGATT_IDA\n"
            "      IdleAnimation       = NIGATT_SKL.NIGATT_IDB\n"
            "      AnimationMode       = ONCE\n"
            "      TransitionKey       = TRANS_Standing\n"
            "    End\n"
            "  End\n\n" + marker), 1)
    if name in ("RussiaInfantryShockTrooper", "RussiaInfantryShockTrooper_Var1"):
        # elite repricing (donor 450 / 7.0)
        text, n = re.subn(r"BuildCost\s*=\s*450", "BuildCost = %s" % SHOCK_COST[0],
                          text)
        assert n >= 1, "BuildCost not found in %s" % name
        text, n = re.subn(r"BuildTime\s*=\s*7\.0", "BuildTime = %s" % SHOCK_COST[1],
                          text)
        assert n >= 1, "BuildTime not found in %s" % name
    if name == "RussiaInfantryShockTrooper_Var1":
        # 1. dual-mode draw -> tesla-only draw (donor RIDER2 states)
        text, n = strip_submodule(
            text, r"Draw\s*=\s*W3DModelDraw\s+ModuleTag_01\b.*$")
        assert n == 1, "Var1 main draw not found"
        text, n = strip_submodule(
            text, r"Draw\s*=\s*W3DModelDraw\s+ModuleTag_LaunchBone01\b.*$")
        assert n == 1, "Var1 launch-bone draw not found"
        marker = "  ; ***DESIGN parameters ***"
        assert marker in text
        text = text.replace(marker, shock_tesla_draw("") + "\n" + marker, 1)
        # 2. the four rider weaponsets -> two tesla sets (3 slots each)
        text, n = strip_submodule(text, r"WeaponSet\s*$")
        assert n == 4, "expected 4 donor weaponsets, removed %d" % n
        amarker = "  ArmorSet"
        assert amarker in text
        text = text.replace(amarker, SHOCK_WEAPONSETS + "\n" + amarker, 1)
        # 3. turret also drives the arc weapon (TERTIARY)
        text, n = re.subn(r"ControlledWeaponSlots\s*=\s*SECONDARY\s*$",
                          "ControlledWeaponSlots = SECONDARY TERTIARY",
                          text, flags=re.M)
        assert n == 1, "turret ControlledWeaponSlots not found"
    if name in ("RussiaInfantryShockTrooper_Var2",
                "RussiaInfantryShockTrooper_Var3"):
        skin = name[-1]   # '2' | '3'
        text = ("ObjectReskin %s RussiaInfantryShockTrooper_Var1\n\n"
                % name) + shock_tesla_draw(skin) + "\nEnd\n"
    return text


def strip_player_upgrade_weaponsets(text):
    """Remove WeaponSet blocks whose Conditions include PLAYER_UPGRADE."""
    lines = text.split("\n")
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^(\s*)WeaponSet\s*$", strip_comments_line(line).rstrip()):
            indent = re.match(r"^(\s*)", line).group(1)
            j = i + 1
            end_re = re.compile(r"^" + re.escape(indent) + r"End\s*$")
            while j < len(lines) and not end_re.match(
                    strip_comments_line(lines[j]).rstrip()):
                j += 1
            body = "\n".join(lines[i:j + 1])
            if re.search(r"Conditions\s*=.*PLAYER_UPGRADE", body):
                removed += 1
                i = j + 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out), removed
