#!/usr/bin/env python3
"""Build zzz-ZZKwaiBaseTech.big — two researchable Propaganda Center
upgrades for Kwai (China Tank General), ShockWave under GeneralsX.

1. AUTOMATED REPAIR SYSTEMS (Tank_Upgrade_KwaiAutoRepair, $1500 / 45 s,
   Propaganda Center slot 10).  Every Kwai structure gains one
   AutoHealBehavior module (StartsActive = No, TriggeredBy the upgrade)
   that heals the building itself — Radius omitted = 0 = self-only, the
   exact GLA Junk Repair idiom (Scorpion.ini: HealingAmount/HealingDelay/
   TriggeredBy; engine AutoHealBehavior.cpp radius==0 self path).
   RATE: 1% of that building's effective base MaxHealth per second
   (HealingAmount = MaxHealth/100, HealingDelay = 1000 ms), computed
   per building from the effective INI at build time.  A flat rate would
   be negligible on the 20000 HP Internet Center and strong on a 2000 HP
   Barracks; 1%/s gives every structure the same ~100 s empty-to-full
   repair (up to ~140 s with all four kwai-doctrine armor tiers, whose
   MaxHealthUpgrade additions are deliberately not counted).  2%/s
   (IC 400/s) was judged too strong.  Covered: the 13 doctrine-covered
   Kwai structures + the kwai-bunkers Hacker Bunker (14 files).  The
   vanilla-shared Speaker Tower stays out (doctrine's shared-file rule).

2. BASE ARMAMENTS (Tank_Upgrade_KwaiBaseArmaments, $2000 / 60 s, slot 11).
   Kwai's seven MAIN buildings — Command Center, Barracks, War Factory,
   Supply Center, Internet Center, Propaganda Center, Power Plant — gain
   an upgrade-gated defensive machine gun:
     - WeaponSet Conditions = None, EMPTY (unarmed by default; empty-set
       precedent: GLA Salvage MI8Gunship, ChinaMisc "no weapons").
     - WeaponSet Conditions = PLAYER_UPGRADE carrying the new weapon.
     - Behavior = WeaponSetUpgrade TriggeredBy the upgrade (sets the
       per-object WEAPONSET_PLAYER_UPGRADE flag — same mechanism as the
       Gattling Cannon's Chain Guns set swap, GattlingCannon.ini
       ModuleTag_16).  Verified free: none of the seven buildings has any
       WeaponSet or WeaponSetUpgrade today (asserted at build time).
     - Behavior = AIUpdateInterface with a logical Turret
       (ControlledWeaponSlots = PRIMARY, 360-degree idle scan) +
       AutoAcquireEnemiesWhenIdle = Yes + MoodAttackCheckRate — the
       minimal acquisition set mirrored from Tank_ChinaGattlingCannon
       ModuleTag_06.  IMMOBILE structures need the turret to aim
       (engine TurretAI is pure logic; no turret bone in the art means
       no visible rotation — the gun fires from the structure origin,
       cosmetic only).  ProductionUpdate + AIUpdateInterface coexist
       (AmericaStrategyCenter, TechWarFortress_Real precedents).
     - KindOf deliberately NOT given CAN_ATTACK: Object.cpp
       isAbleToAttack returns true for "AI + any weapon in the current
       set", so the buildings only register as armed after the research
       flips the weapon set; CAN_ATTACK would make weaponless buildings
       claim attack ability (the Internet Center already carries
       CAN_ATTACK from ShockWave — left untouched, harmless).
   WEAPON: new template Tank_KwaiBaseArmamentsGun appended to Weapon.ini
   — a toned-down clone of Tank_GattlingBuildingGun (12 vs 20 damage,
   175 vs 225 range so it stays inside every armed building's 200 vision
   radius, no anti-air, no Chain-Guns PLAYER_UPGRADE damage line;
   continuous-fire rate bonuses kept — the FiringTracker sets those bits
   per object automatically).  Reusing the base-defense gun verbatim
   would have out-ranged the buildings' own vision and duplicated a
   full Gattling Cannon on every structure.
   Skipped (documented): Airfield (JetAI parking interactions untested),
   Nuclear Silo (superweapon), Industrial Plant (outside the requested
   main-building set), defenses (already armed / spawn-armed).

3. BUTTONS: Propaganda Center slots 10 + 11 in ALL 50 Kwai prop-center
   command sets (2 base + kwai-doctrine's 48 enumerated Mines x CompArmor
   x InfCond state sets).  NO new CommandSetUpgrade anywhere — both
   upgrades are plain one-shot PLAYER upgrades whose buttons the engine
   natively disables once researched, so the doctrine state machine is
   untouched.  Slots 10-12 verified free in every prop-center set.
   Cameos reuse mapped images: SNRepairPad (China repair pad) and
   SNTankGatTower (Kwai gattling tower).  Strings append-only.

4. AI: no AI wiring (player-facing only).

Packaging: zzz-ZZKwaiBaseTech.big.  Case-insensitively 'zzz-zk...' <
'zzz-zz...' puts it AFTER zzz-ZKwaiBunkers.big (whose CommandSet.ini /
CommandButton.ini / Generals.str / HackerBunker.ini it layers on) and
'-' (0x2D) < '_' (0x5F) puts it BEFORE zzz_ControlBarPro*.big — verified
against the real directory listings at build time.  Installed to both
mod dirs.

Rebuild order: this is now the LAST INI layer.  If any lower layer
(kwai-bunkers, kwai-doctrine, stat-tune, ...) is rebuilt, rebuild this
archive afterwards.  Conversely kwai-bunkers' own build must not see
this archive (its ownership asserts would fail): delete
zzz-ZZKwaiBaseTech.big from both mod dirs first, rebuild kwai-bunkers,
then rerun this build.  (And kwai-doctrine requires BOTH bunkers and
this archive removed first.)
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
OUT_NAME = "zzz-ZZKwaiBaseTech.big"
TAG = "zzz-ZZKwaiBaseTech"

P = "Data\\INI\\Object\\China\\Tank\\"
CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
STR_PATH = "Data\\Generals.str"
UPG_PATH = "Data\\INI\\Upgrade.ini"
WPN_PATH = "Data\\INI\\Weapon.ini"

OWNER_BUNKERS = "zzz-ZKwaiBunkers.big"
OWNER_DOCTRINE = "zzz-KwaiDoctrine.big"

# (path, object name, armed?) — armed = gets the Base Armaments weapon
BUILDINGS = [
    (P + "Buildings\\Airfield.ini",         "Tank_ChinaAirfield",              False),
    (P + "Buildings\\Barracks.ini",         "Tank_ChinaBarracks",              True),
    (P + "Buildings\\CommandCenter.ini",    "Tank_ChinaCommandCenter",         True),
    (P + "Buildings\\IndustrialPlant.ini",  "Tank_ChinaIndustrialPlant",       False),
    (P + "Buildings\\InternetCenter.ini",   "Tank_ChinaInternetCenter",        True),
    (P + "Buildings\\NuclearSilo.ini",      "Tank_ChinaNuclearMissileLauncher", False),
    (P + "Buildings\\PowerPlant.ini",       "Tank_ChinaPowerPlant",            True),
    (P + "Buildings\\PropagandaCenter.ini", "Tank_ChinaPropagandaCenter",      True),
    (P + "Buildings\\SupplyCenter.ini",     "Tank_ChinaSupplyCenter",          True),
    (P + "Buildings\\WarFactory.ini",       "Tank_ChinaWarFactory",            True),
    (P + "Defences\\Bunker.ini",            "Tank_ChinaBunker",                False),
    (P + "Defences\\GattlingCannon.ini",    "Tank_ChinaGattlingCannon",        False),
    (P + "Defences\\Ramjet Turret.ini",     "Tank_ChinaSentryTower",           False),
    (P + "Defences\\HackerBunker.ini",      "Tank_ChinaHackerBunker",          False),
]

OWNERS = {
    CS_PATH: OWNER_BUNKERS,
    CB_PATH: OWNER_BUNKERS,
    STR_PATH: OWNER_BUNKERS,
    UPG_PATH: OWNER_DOCTRINE,
    WPN_PATH: OWNER_DOCTRINE,
}
for path, _, _ in BUILDINGS:
    OWNERS[path] = OWNER_BUNKERS if path.endswith("HackerBunker.ini") else OWNER_DOCTRINE

SHIPPED = [CS_PATH, CB_PATH, STR_PATH, UPG_PATH, WPN_PATH] + [p for p, _, _ in BUILDINGS]

UPG_REPAIR = "Tank_Upgrade_KwaiAutoRepair"
UPG_ARM = "Tank_Upgrade_KwaiBaseArmaments"
BTN_REPAIR = "Tank_Command_UpgradeKwaiAutoRepair"
BTN_ARM = "Tank_Command_UpgradeKwaiBaseArmaments"
NEW_WEAPON = "Tank_KwaiBaseArmamentsGun"
NEW_NAMES = (UPG_REPAIR, UPG_ARM, BTN_REPAIR, BTN_ARM, NEW_WEAPON,
             "ModuleTag_KBT_Heal01", "ModuleTag_KBT_Arm01", "ModuleTag_KBT_AI01",
             "UPGRADE:KwaiAutoRepair", "UPGRADE:KwaiBaseArmaments")


# ------------------------------------------------------------------ helpers
def eol_of(raw):
    """Assert the file uses a single uniform EOL style; return it."""
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(raw):
    return raw.replace("\r\n", "\n")


def from_lf(lf_text, eol):
    return lf_text.replace("\n", eol) if eol != "\n" else lf_text


def replace_exact(s, old, new, count):
    assert s.count(old) == count, \
        "expected %d occurrences of %r, found %d" % (count, old[:80], s.count(old))
    return s.replace(old, new)


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def added_only(src_lf, out_lf, label):
    """Assert the diff is pure insertion; return the added-line multiset."""
    d = unified(src_lf, out_lf)
    rem = [l for l in d if l.startswith("-")]
    assert not rem, "%s: unexpected removals %r" % (label, rem[:5])
    return Counter(l[1:] for l in d if l.startswith("+"))


# ------------------------------------------------------- generated INI text
UPGRADE_APPENDIX = """
;;; zzz-ZZKwaiBaseTech: Kwai base-tech upgrades (researched at the Propaganda Center)
Upgrade Tank_Upgrade_KwaiAutoRepair
  DisplayName        = UPGRADE:KwaiAutoRepair
  Type               = PLAYER
  BuildTime          = 45.0
  BuildCost          = 1500
  ButtonImage        = SNRepairPad
  ResearchSound      = ReaperVoiceUpgrade
End

Upgrade Tank_Upgrade_KwaiBaseArmaments
  DisplayName        = UPGRADE:KwaiBaseArmaments
  Type               = PLAYER
  BuildTime          = 60.0
  BuildCost          = 2000
  ButtonImage        = SNTankGatTower
  ResearchSound      = GattlingTankVoiceUpgrade
End
"""

WEAPON_APPENDIX = """
;;; zzz-ZZKwaiBaseTech: Base Armaments building machine gun - a toned-down
;;; derivative of Tank_GattlingBuildingGun (12 vs 20 damage, 175 vs 225
;;; range, ground-only, no Chain-Guns PLAYER_UPGRADE damage line).
Weapon Tank_KwaiBaseArmamentsGun
  PrimaryDamage         = 12.0
  PrimaryDamageRadius   = 1.0       ; 0 primary radius means "hits only intended victim"
  ScatterRadius         = 0.01
  AttackRange           = 175.0
  DamageType            = GATTLING
  DeathType             = NORMAL
  WeaponSpeed           = 9999.0          ; dist/sec (huge value == effectively instant)
  ProjectileObject      = GenericMachinegunProjectile
  FireFX                = WeaponFX_NormalGattlingCannonMachineGunFire
  FireSound             = GattlingCannonBarrelSpinning
  FireSoundLoopTime     = 300
  RadiusDamageAffects   = ALLIES ENEMIES NEUTRALS
  DelayBetweenShots     = 250               ; time between shots, msec
  ClipSize              = 0                    ; how many shots in a Clip (0 == infinite)
  ClipReloadTime        = 0              ; how long to reload a Clip, msec
  ContinuousFireOne     = 1 ; How many shots at the same target constitute "Continuous Fire"
  ContinuousFireTwo     = 4 ; How many shots at the same target constitute "Continuous Fire Two"
  ContinuousFireCoast   = 700 ; msec we can coast without firing before we lose Continuous Fire
  WeaponBonus           = CONTINUOUS_FIRE_MEAN RATE_OF_FIRE 150%
  WeaponBonus           = CONTINUOUS_FIRE_FAST RATE_OF_FIRE 200%
  AntiAirborneVehicle   = No
  AntiAirborneInfantry  = No
  AntiSmallMissile      = No
  AntiBallisticMissile  = No
  AntiGround            = Yes
  ProjectileDetonationFX = WeaponFX_GenericBulletImpact
End
"""

CB_APPENDIX = """
;;; zzz-ZZKwaiBaseTech: Kwai base-tech research buttons (Propaganda Center slots 10-11)

CommandButton Tank_Command_UpgradeKwaiAutoRepair
  Command       = PLAYER_UPGRADE
  Upgrade       = Tank_Upgrade_KwaiAutoRepair
  TextLabel     = CONTROLBAR:UpgradeKwaiAutoRepair
  ButtonImage   = SNRepairPad
  ButtonBorderType        = UPGRADE ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:TooltipUpgradeKwaiAutoRepair
  PurchasedLabel          = CONTROLBAR:TooltipUpgradeKwaiAutoRepair
  UnitSpecificSound = MoneyWithdraw
End

CommandButton Tank_Command_UpgradeKwaiBaseArmaments
  Command       = PLAYER_UPGRADE
  Upgrade       = Tank_Upgrade_KwaiBaseArmaments
  TextLabel     = CONTROLBAR:UpgradeKwaiBaseArmaments
  ButtonImage   = SNTankGatTower
  ButtonBorderType        = UPGRADE ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:TooltipUpgradeKwaiBaseArmaments
  PurchasedLabel          = CONTROLBAR:TooltipUpgradeKwaiBaseArmaments
  UnitSpecificSound = MoneyWithdraw
End
"""

STR_APPENDIX = (
    "\n\nUPGRADE:KwaiAutoRepair\n"
    "\"Automated Repair Systems\"\nEND"
    "\n\nCONTROLBAR:UpgradeKwaiAutoRepair\n"
    "\"Automated Repair Systems\"\nEND"
    "\n\nCONTROLBAR:TooltipUpgradeKwaiAutoRepair\n"
    "\"Automated repair systems for Kwai's structures. \\n All of Kwai's"
    " buildings slowly repair themselves - about 1% of their base maximum"
    " health per second.\"\nEND"
    "\n\nUPGRADE:KwaiBaseArmaments\n"
    "\"Base Armaments\"\nEND"
    "\n\nCONTROLBAR:UpgradeKwaiBaseArmaments\n"
    "\"Base Armaments\"\nEND"
    "\n\nCONTROLBAR:TooltipUpgradeKwaiBaseArmaments\n"
    "\"Defensive machine guns for Kwai's key structures. \\n Command Center,"
    " Barracks, War Factory, Supply Center, Internet Center, Propaganda"
    " Center and Power Plant gain an anti-infantry machine gun.\"\nEND"
)

CS_SLOT9 = "  9  = Tank_Command_UpgradeKwaiInfantryDoctrine\n"
CS_NEW = (" 10  = Tank_Command_UpgradeKwaiAutoRepair\n"
          " 11  = Tank_Command_UpgradeKwaiBaseArmaments\n")

HEAL_MODULE = (
    "  Behavior = AutoHealBehavior ModuleTag_KBT_Heal01 ; %s: Automated Repair Systems, 1%%/s of base %d\n"
    "    StartsActive  = No\n"
    "    HealingAmount = %d\n"
    "    HealingDelay  = 1000 ; msec\n"
    "    TriggeredBy   = Tank_Upgrade_KwaiAutoRepair\n"
    "  End\n"
)

ARM_MODULES = (
    "  Behavior = WeaponSetUpgrade ModuleTag_KBT_Arm01 ; " + TAG + ": Base Armaments - flips to the PLAYER_UPGRADE weapon set\n"
    "    TriggeredBy = Tank_Upgrade_KwaiBaseArmaments\n"
    "  End\n"
    "  Behavior = AIUpdateInterface ModuleTag_KBT_AI01 ; " + TAG + ": Base Armaments target acquisition (logical turret, no art)\n"
    "    Turret\n"
    "      ControlledWeaponSlots = PRIMARY\n"
    "      TurretTurnRate      = 180   ; turn rate, in degrees per sec\n"
    "      TurretPitchRate     = 180\n"
    "      AllowsPitch         = Yes\n"
    "      FiresWhileTurning   = Yes\n"
    "      MinIdleScanInterval   = 250    ; in milliseconds\n"
    "      MaxIdleScanInterval   = 250    ; in milliseconds\n"
    "      MinIdleScanAngle      = 0      ; in degrees off the natural turret angle\n"
    "      MaxIdleScanAngle      = 360    ; in degrees off the natural turret angle\n"
    "    End\n"
    "    AutoAcquireEnemiesWhenIdle = Yes ; defensive weapon\n"
    "    MoodAttackCheckRate        = 250\n"
    "  End\n"
)

WEAPONSET_BLOCKS = (
    "  ; " + TAG + ": Base Armaments - unarmed by default; researching\n"
    "  ; Tank_Upgrade_KwaiBaseArmaments sets WEAPONSET_PLAYER_UPGRADE (module below)\n"
    "  WeaponSet\n"
    "    Conditions          = None\n"
    "  End\n"
    "  WeaponSet\n"
    "    Conditions          = PLAYER_UPGRADE\n"
    "    Weapon              = PRIMARY Tank_KwaiBaseArmamentsGun\n"
    "    AutoChooseSources   = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    PreferredAgainst    = PRIMARY INFANTRY\n"
    "  End\n"
)


# ------------------------------------------------------------- file patches
def patch_commandset(src):
    out = replace_exact(src, CS_SLOT9, CS_SLOT9 + CS_NEW, 50)
    return out


def parse_max_health(lf, path):
    vals = re.findall(r"(?m)^\s*MaxHealth\s*=\s*([0-9.]+)", lf)
    assert len(vals) == 1, "%s: MaxHealth count %d" % (path, len(vals))
    return int(float(vals[0]))


def patch_building(raw, path, obj_name, armed):
    eol = eol_of(raw)
    lf = to_lf(raw)
    assert re.search(r"(?m)^Object %s\b" % re.escape(obj_name), lf), \
        "%s: object %s not found" % (path, obj_name)
    assert len(re.findall(r"(?m)^Object ", lf)) == 1, path

    max_health = parse_max_health(lf, path)
    heal = int(round(max_health / 100.0))
    heal_block = HEAL_MODULE % (TAG, max_health, heal)

    # insert behaviors right after the (single) Body block's End
    body = re.search(r"(?m)^  Body\s*=", lf)
    assert body and len(re.findall(r"(?m)^  Body\s*=", lf)) == 1, path
    end = re.compile(r"(?m)^  End[ \t]*$").search(lf, body.end())
    assert end, path
    at = lf.index("\n", end.end()) + 1
    insertion = heal_block + (ARM_MODULES if armed else "")
    lf = lf[:at] + insertion + lf[at:]

    if armed:
        # weapon sets go right after the single object-scope KindOf line
        # (freedom of the PLAYER_UPGRADE weapon-set flag is asserted on the
        #  SOURCE text in main() before this runs)
        kinds = list(re.finditer(r"(?m)^  KindOf\s*=.*$", lf))
        assert len(kinds) == 1, "%s: KindOf count %d" % (path, len(kinds))
        at = kinds[0].end() + 1
        lf = lf[:at] + WEAPONSET_BLOCKS + lf[at:]

    return from_lf(lf, eol), max_health, heal


# -------------------------------------------------------------- verification
def verify_cs_survival(cs):
    """kwai-doctrine + kwai-bunkers + older siblings must survive intact."""
    checks = {
        ("Kwai artillery factory slots 11-12 (both variants)", 2):
            "  11 = Tank_Command_ConstructChinaVehicleInfernoCannon\n"
            "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n",
        ("prop-center artillery slots 4-5 (50 sets)", 50):
            "  4  = Command_UpgradeChinaChainGuns\n"
            "  5  = Command_UpgradeChinaBlackNapalm\n",
        ("doctrine slots 8-9 + new slots 10-11 (50 sets)", 50):
            "  8  = Tank_Command_UpgradeKwaiTungstenShells\n"
            "  9  = Tank_Command_UpgradeKwaiInfantryDoctrine\n"
            " 10  = Tank_Command_UpgradeKwaiAutoRepair\n"
            " 11  = Tank_Command_UpgradeKwaiBaseArmaments\n",
        ("doctrine 48 appended state sets", 48):
            "CommandSet Tank_ChinaPropagandaCenterCS_M",
        ("Mammoth slots 4-8", 1):
            "  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n"
            "  8  = Command_Evacuate\n",
        ("Tank Battlemaster exit/prop-tower", 1):
            "CommandSet Tank_ChinaVehicleBattleMasterCommandSet\n"
            "  1  = Command_TransportExit\n"
            "  2  = Command_TransportExit\n"
            "  3  = Command_TransportExit\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_Evacuate\n"
            "  10 = Command_UpgradeChinaOverlordPropagandaTower\n",
        ("Tank Battlemaster ERA set", 1):
            "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n",
        ("Emperor bunker set (exits 2-9, gattling 10, evacuate 12)", 1):
            "CommandSet Tank_ChinaTankEmperorDefaultCommandSet\n"
            "  1  = Command_OverlordTaunt\n"
            "  2  = Command_TransportExit\n"
            "  3  = Command_TransportExit\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n"
            "  8  = Command_TransportExit\n"
            "  9  = Command_TransportExit\n"
            "  10 = Tank_Command_UpgradeChinaOverlordGattlingCannon\n"
            "  11 = Command_AttackMove\n"
            "  12 = Command_Evacuate\n"
            "  13 = Command_Guard\n"
            "  14 = Command_Stop\n"
            "End\n",
        ("Kwai dozer page 1 (bunkers page-flip) intact", 1):
            "CommandSet Tank_ChinaDozerCommandSet\n"
            "  1  = Tank_Command_ConstructChinaPowerPlant\n"
            "  2  = Tank_Command_ConstructChinaInternetCenter\n"
            "  3  = Tank_Command_ConstructChinaBarracks\n"
            "  4  = Tank_Command_ConstructChinaAirfield\n"
            "  5  = Tank_Command_ConstructChinaSupplyCenter\n"
            "  6  = Tank_Command_ConstructChinaPropagandaCenter\n"
            "  7  = Tank_Command_ConstructChinaSentryTower\n"
            "  8  = Tank_Command_ConstructChinaSpeakerTower\n"
            "  9  = Tank_Command_ConstructChinaGattlingCannon\n"
            " 10  = Tank_Command_ConstructChinaNuclearMissileLauncher\n"
            " 11  = Tank_Command_ConstructChinaWarFactory\n"
            " 12  = Tank_Command_ConstructChinaCommandCenter\n"
            " 13  = Command_ChinaButtonCommandSetOneDown\n"
            " 14  = Command_DisarmMinesAtPosition\nEnd\n",
        ("Kwai dozer page 2 (bunkers)", 1):
            "CommandSet Tank_ChinaDozerCommandSet_Down\n"
            "  1  = Tank_Command_ConstructChinaIndustrialPlant\n"
            "  7  = Tank_Command_ConstructChinaBunker\n"
            "  8  = Tank_Command_ConstructChinaHackerBunker\n",
        ("Hacker Bunker set (bunkers)", 1):
            "CommandSet Tank_ChinaHackerBunkerCommandSet\n",
        ("vanilla China dozer pages untouched", 1):
            "CommandSet ChinaDozerCommandSet_Down\n",
        ("vanilla prop-center sets untouched (no slot 10)", 1):
            "CommandSet ChinaPropagandaCenterCommandSet\n"
            "  1  = Command_UpgradeChinaNationalism\n"
            "  2  = Command_UpgradeChinaAutoLoader\n",
    }
    for (label, count), needle in checks.items():
        assert cs.count(needle) == count, \
            "CS SURVIVAL FAILED: %s (found %d, want %d)" % (
                label, cs.count(needle), count)
        print("  commandset OK:", label)
    # the new buttons appear exactly 50 times each, nowhere else
    assert cs.count(BTN_REPAIR) == 50 and cs.count(BTN_ARM) == 50


def verify_building(shipped, path, obj_name, armed, heal, max_health):
    lf = to_lf(shipped)
    assert lf.count("ModuleTag_KBT_Heal01") == 1, path
    assert ("HealingAmount = %d\n" % heal) in lf, path
    assert "TriggeredBy   = Tank_Upgrade_KwaiAutoRepair\n" in lf, path
    assert "StartsActive  = No\n" in lf, path
    # doctrine armor tiers survive with their triggers
    for i in (1, 2, 3, 4):
        assert ("ModuleTag_KD_Armor%d" % i) in lf, (path, i)
        assert ("Tank_Upgrade_KwaiVehicleArmor%d" % i) in lf, (path, i)
    if armed:
        assert lf.count("ModuleTag_KBT_Arm01") == 1, path
        assert lf.count("ModuleTag_KBT_AI01") == 1, path
        assert lf.count("  WeaponSet\n") == 2, path
        assert lf.count("Weapon              = PRIMARY Tank_KwaiBaseArmamentsGun\n") == 1
        assert lf.count("    Conditions          = None\n") == 1
        assert lf.count("    Conditions          = PLAYER_UPGRADE\n") == 1
        assert "AutoAcquireEnemiesWhenIdle = Yes" in lf
        assert "ControlledWeaponSlots = PRIMARY" in lf
    else:
        assert "ModuleTag_KBT_Arm01" not in lf and "ModuleTag_KBT_AI01" not in lf
        assert NEW_WEAPON not in lf
    # per-file specials
    if "InternetCenter" in path:
        assert max_health == 20000, "stat-tune IC 20000 lost"
        assert re.search(r"(?m)^\s*Slots\s*=\s*30\b", lf), "stat-tune IC 30 slots lost"
    if "HackerBunker" in path:
        assert "Behavior = InternetHackContain ModuleTag_KB_Hack01" in lf, \
            "bunkers hacker-contain lost"
        assert re.search(r"(?m)^\s*Slots\s*=\s*4\b", lf)
    if path.endswith("Defences\\Bunker.ini"):
        # the bunker keeps its own vehicle-repair aura next to our module
        assert "AutoHealBehavior ModuleTag_Repair01" in lf


def verify_cross_refs(cb, s, upg, wpn):
    for b, u in ((BTN_REPAIR, UPG_REPAIR), (BTN_ARM, UPG_ARM)):
        m = re.search(r"(?ms)^CommandButton %s\s*$.*?^End" % b, cb)
        assert m, "button missing: " + b
        assert ("Upgrade       = %s\n" % u) in m.group(0)
        assert "Command       = PLAYER_UPGRADE" in m.group(0)
    for u, cost, time in ((UPG_REPAIR, 1500, 45.0), (UPG_ARM, 2000, 60.0)):
        m = re.search(r"(?ms)^Upgrade %s\s*$.*?^End" % u, to_lf(upg))
        assert m, "upgrade missing: " + u
        assert "Type               = PLAYER" in m.group(0)
        assert ("BuildCost          = %d" % cost) in m.group(0)
        assert ("BuildTime          = %.1f" % time) in m.group(0)
    # weapon exists exactly once and references only existing assets
    assert len(re.findall(r"(?m)^Weapon %s\b" % NEW_WEAPON, wpn)) == 1
    for asset in ("GenericMachinegunProjectile",
                  "WeaponFX_NormalGattlingCannonMachineGunFire",
                  "GattlingCannonBarrelSpinning",
                  "WeaponFX_GenericBulletImpact"):
        assert wpn.count(asset) >= 2, "asset only in our block: " + asset
    # cameos are mapped (already used by other buttons/upgrades in the sources)
    for img in ("SNRepairPad", "SNTankGatTower"):
        assert cb.count(img) >= 2, "cameo not pre-existing: " + img
    # research sounds pre-existing
    for snd in ("ReaperVoiceUpgrade", "GattlingTankVoiceUpgrade"):
        assert to_lf(upg).count(snd) >= 2, "sound not pre-existing: " + snd
    # strings for every new label
    for lbl in ("UPGRADE:KwaiAutoRepair", "CONTROLBAR:UpgradeKwaiAutoRepair",
                "CONTROLBAR:TooltipUpgradeKwaiAutoRepair",
                "UPGRADE:KwaiBaseArmaments", "CONTROLBAR:UpgradeKwaiBaseArmaments",
                "CONTROLBAR:TooltipUpgradeKwaiBaseArmaments"):
        assert ("\n%s\n" % lbl) in s, "missing string: " + lbl
    print("  cross-reference closure OK (buttons<->upgrades<->strings<->weapon<->assets)")


def verify_sibling_appendices(cb, s):
    # doctrine's 10 buttons / 30 strings + bunkers' button / 3 strings survive
    assert cb.count("CommandButton Tank_Command_UpgradeKwai") == 12  # 10 doctrine + our 2
    assert re.search(r"(?m)^CommandButton Tank_Command_ConstructChinaHackerBunker\s*$", cb)
    assert s.count("\nUPGRADE:Kwai") == 12  # 10 doctrine + our 2
    assert s.count("\nCONTROLBAR:TooltipUpgradeKwai") == 12
    assert ("\nOBJECT:TankHackerBunker\n") in s
    print("  sibling appendices OK in CommandButton.ini / Generals.str")


# ---------------------------------------------------------------------- main
def main():
    archives = sorted((f for f in os.listdir(SPE_DIR)
                       if f.lower().endswith(".big")
                       and f.lower() != OUT_NAME.lower()),  # never self-source
                      key=str.lower, reverse=True)
    cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}

    def effective(path):
        want = path.lower()
        for a in archives:
            for e in cache[a]:
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        return None, None

    sources = {}
    for path, owner in OWNERS.items():
        data, got = effective(path)
        assert data is not None, "effective source not found: " + path
        assert got == owner, "ownership drift for %s: %s (expected %s)" % (
            path, got, owner)
        sources[path] = data
    print("effective-file ownership verified (%d files)" % len(sources))

    # new identifiers must be unused across every effective source we touch
    # and across the whole archive chain's INI space for the global names
    for name in NEW_NAMES:
        for path in SHIPPED:
            assert name not in sources[path], (name, path)
    print("new identifiers are collision-free in all sources")

    # the PLAYER_UPGRADE weapon-set flag must be free on every armed building
    for path, obj, armed in BUILDINGS:
        if armed:
            lf = to_lf(sources[path])
            assert "WeaponSet" not in lf, path + ": already has weapon machinery"
            assert "WeaponSetUpgrade" not in lf, path
            assert not re.search(r"(?m)^\s*Behavior\s*=\s*AIUpdateInterface\b", lf), path
    print("WEAPONSET_PLAYER_UPGRADE flag free on all 7 armed buildings "
          "(no WeaponSet / WeaponSetUpgrade / active AIUpdateInterface)")

    # prop-center slots 10-12 must be free in every prop-center set
    cs_lf = sources[CS_PATH]
    for m in re.finditer(r"(?ms)^CommandSet (\S*PropagandaCenter\S*)\n(.*?)^End", cs_lf):
        for slot in (10, 11, 12):
            assert not re.search(r"(?m)^\s*%d\s*=" % slot, m.group(2)), \
                "slot %d taken in %s" % (slot, m.group(1))
    print("slots 10-12 free in every Propaganda Center command set")

    # ---- build the shipped files
    patched = {
        CS_PATH: patch_commandset(sources[CS_PATH]),
        CB_PATH: sources[CB_PATH] + from_lf(CB_APPENDIX, eol_of(sources[CB_PATH])),
        STR_PATH: sources[STR_PATH] + from_lf(STR_APPENDIX, eol_of(sources[STR_PATH])),
        UPG_PATH: sources[UPG_PATH] + from_lf(UPGRADE_APPENDIX, eol_of(sources[UPG_PATH])),
        WPN_PATH: sources[WPN_PATH] + from_lf(WEAPON_APPENDIX, eol_of(sources[WPN_PATH])),
    }
    stats = {}
    for path, obj, armed in BUILDINGS:
        patched[path], max_health, heal = patch_building(sources[path], path, obj, armed)
        stats[path] = (obj, armed, max_health, heal)
        print("  %-28s MaxHealth %6d -> heal %3d/s %s" % (
            obj, max_health, heal, "+ MG" if armed else ""))

    # ---- append-only files: base bytes identical
    for path in (CB_PATH, STR_PATH, UPG_PATH, WPN_PATH):
        assert patched[path].startswith(sources[path]), path
    print("append-only base-byte identity OK (CommandButton, Generals.str, Upgrade, Weapon)")

    # ---- CommandSet.ini diff audit: exactly 100 inserted lines, none removed
    add = added_only(sources[CS_PATH], patched[CS_PATH], "CommandSet.ini")
    assert add == Counter({" 10  = " + BTN_REPAIR: 50,
                           " 11  = " + BTN_ARM: 50}), add
    print("CommandSet.ini diff audit OK (2 x 50 slot lines inserted, nothing removed)")

    # ---- object-file diff audits: pure insertion of exactly our blocks
    for path, obj, armed in BUILDINGS:
        _, _, max_health, heal = stats[path]
        exp = (HEAL_MODULE % (TAG, max_health, heal)) + (ARM_MODULES if armed else "") \
            + (WEAPONSET_BLOCKS if armed else "")
        expected = Counter(exp.rstrip("\n").split("\n"))
        got = added_only(to_lf(sources[path]), to_lf(patched[path]), path)
        assert got == expected, (path, got - expected, expected - got)
    print("object-file diff audits OK (14 files, insertions only, exact blocks)")

    # ---- content + survival verification on final text
    verify_cs_survival(patched[CS_PATH])
    for path, obj, armed in BUILDINGS:
        _, _, max_health, heal = stats[path]
        verify_building(patched[path], path, obj, armed, heal, max_health)
    print("  building content OK (heal modules, weapon sets, doctrine tiers, IC 20000/30)")
    verify_cross_refs(patched[CB_PATH], patched[STR_PATH],
                      patched[UPG_PATH], patched[WPN_PATH])
    verify_sibling_appendices(patched[CB_PATH], patched[STR_PATH])

    # ---- package
    entries = [BigEntry(path, patched[path].encode("latin-1"))
               for path in sorted(SHIPPED)]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_local)
    print("wrote %s (%d files, %d bytes)"
          % (out_local, len(entries), os.path.getsize(out_local)))

    # ---- sort-order verification against the real directory listings
    for d in (SPE_DIR, SHW_DIR):
        listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                         | {OUT_NAME}, key=str.lower)
        i = listing.index(OUT_NAME)
        after = listing[i - 1]
        before = listing[i + 1] if i + 1 < len(listing) else None
        assert after.lower() == "zzz-zkwaibunkers.big", listing
        assert before and before.lower().startswith("zzz_controlbarpro"), listing
        print("sort order OK in %s: %s < %s < %s" % (d, after, OUT_NAME, before))

    # ---- install + re-read verification
    blob = open(out_local, "rb").read()
    for d in (SPE_DIR, SHW_DIR):
        dst = os.path.join(d, OUT_NAME)
        with open(dst, "wb") as f:
            f.write(blob)
        back = read_big(dst)
        assert [e.path for e in back] == [e.path for e in entries]
        for x, y in zip(back, entries):
            assert x.data == y.data, x.path
        verify_cs_survival(find_entry(back, CS_PATH).data.decode("latin-1"))
        for path, obj, armed in BUILDINGS:
            _, _, max_health, heal = stats[path]
            verify_building(find_entry(back, path).data.decode("latin-1"),
                            path, obj, armed, heal, max_health)
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
