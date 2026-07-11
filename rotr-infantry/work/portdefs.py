"""Shared decision tables for the ROTR infantry port (Shmel Trooper +
Shock Trooper -> Kwai).  Used by trace_closure.py, build.py and
integrate.py so every stage agrees on what ships, what is renamed,
what is remapped and what is dropped.
"""

# ---------------------------------------------------------------- paths
import os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DONOR_INI = os.path.join(REPO, "..", "generalsx-mods", "donor-inis",
                         "rotr_ini", "Data", "INI")
# fall back to a donor tree inside this worktree if the main worktree moves
if not os.path.isdir(DONOR_INI):
    DONOR_INI = os.path.join(REPO, "donor-inis", "rotr_ini", "Data", "INI")
EFFECTIVE_INI = os.path.join(HERE, "effective", "Data", "INI")
VANILLA_INI = os.path.join(HERE, "vanilla_ini", "Data", "INI")

ARCHIVE_NAME = "zzz-ZZZZZZZRotrInfantry.big"

# ---------------------------------------------------------------- seeds
# Donor-named roots of the closure.  The two buildable units, their
# variation/system objects and the unit-ability buttons/sets.
SEEDS = [
    ("Object", "RussianInfantryShmelTrooper"),
    ("Object", "RussiaInfantryShockTrooper"),
    ("CommandSet", "RussianInfantryShmelTrooperCommandSet"),
    ("CommandSet", "RussianInfantryShockTrooperCommandSet"),
    ("CommandButton", "Command_RussiaShmellTrooperSmokeRocket"),
    ("CommandButton", "Command_RussiaShmellTrooperAntiToxinRocket"),
]

# ---------------------------------------------------------------- renames
# Donor identifier -> our identifier.  The unit family is re-sided for
# Kwai (Tank_ prefix mirrors every other Kwai-owned object in the stack).
RENAMES = {
    "RussianInfantryShmelTrooper": "Tank_ChinaInfantryShmelTrooper",
    "RussiaInfantryShockTrooper": "Tank_ChinaInfantryShockTrooper",
    "RussiaInfantryShockTrooper_Var1": "Tank_ChinaInfantryShockTrooper_Var1",
    "RussiaInfantryShockTrooper_Var2": "Tank_ChinaInfantryShockTrooper_Var2",
    "RussiaInfantryShockTrooper_Var3": "Tank_ChinaInfantryShockTrooper_Var3",
    "RussianInfantryShmelTrooperCommandSet": "Tank_ChinaInfantryShmelTrooperCommandSet",
    "RussianInfantryShockTrooperCommandSet": "Tank_ChinaInfantryShockTrooperCommandSet",
    "Command_RussiaShmellTrooperSmokeRocket": "Tank_Command_ShmelTrooperSmokeRocket",
    "Command_RussiaShmellTrooperAntiToxinRocket": "Tank_Command_ShmelTrooperAntiToxinRocket",
    # string labels: donor keys live in ROTR's generals.csf; we ship our
    # own Generals.str entries under fresh keys (collision-safe).
    "OBJECT:ShmelTrooper": "OBJECT:TankShmelTrooper",
    "OBJECT:ShockTrooper": "OBJECT:TankShockTrooper",
}

# ---------------------------------------------------------------- drops
# Donor identifiers we deliberately do NOT port; references to them are
# stripped (module-level or line-level) by build.py.  Rationale in README.
DROPS = {
    # Russia general-power hook granted per-infantry (out of scope; would
    # pull the Grizon transport plane + paradrop closure):
    "SpecialAbilityRussianGrizonReinforcements", "SUPERWEAPON_GrizonAirDrop",
    "Command_RussiaCallinGrizonAirdrop",
    # Russia tech-tree upgrades Kwai can never research (their modules,
    # cameos and PLAYER_UPGRADE weaponsets go too):
    "Upgrade_RussiaMedPack", "Upgrade_RussiaLargerClips",
    "Upgrade_RussiaAdvancedMissileEngines",
    "RussianInfantryShmelTrooperUpgradedCommandSet",
    "RussiaShmellTrooperMissileLauncherUpgraded",
    "RussiaShmellTrooperSmokeMissileLauncherUpgraded",
    "RussiaShmellTrooperAntiToxinMissileLauncherUpgraded",
    "RussiaShmellTrooperSmokeMissileLauncherHeroicUpgraded",
    "RussiaShmellTrooperAntiToxinMissileLauncherHeroicUpgraded",
    # ROTR POW/surrender + suicide theatre (nothing in base ShockWave
    # inflicts the EXTRA_8 surrender death; the crate chain drags in the
    # CIA-intel / capture-science system):
    "RussiaInfantryShmelTrooperSurrenderCrate",
    "OCL_ShmelTrooperSurrendering", "FX_ShmelTrooperSurrender",
    "OCL_SurrenderedShmelTrooperRevive",
    "RussiaInfantryShockTrooperCommitingSuicide",
    "OCL_ShockTrooperTrooperSurrendering",
    "FX_ShockTrooperSuicide", "FX_ShockTrooperSuicideHeadExplosion",
    # ROTR "berserker on death" flavor system (spawns a rage-aura object
    # tied to ROTR-wide mechanics):
    "OCL_InfantryBeserkerObject", "IfantryBezerker_Object",
    # ROTR science gate on the tesla mode switch (Kwai can't buy it):
    "SCIENCE_TeslaTech",
    # prerequisite buildings: remapped to Tank_ChinaWarFactory by build.py
    # (porting them would pull the whole Russia faction closure):
    "RussiaWarFactory", "RussiaWeaponsBunker",
    # === Shock Trooper tesla rework: the rocket-rifle mode and the whole
    # RiderChangeContain switch machinery are dropped (see README) ===
    "ShockTrooperRocketRifle", "ShockTrooperGuidedMissile",
    "ShocktrooperRocketRifleLocomotor",
    "FX_ShockTrooperRocketExplosion",
    "WeaponFX_GenericShockTrooperRocketRifleFire",
    "WeaponFX_GenericShockTrooperRocketRifleFireWithRedTracers",
    "EmptyShockRocketCassingsFalling",
    "ShockTrooperSwitchToRocketGunMode", "ShockTrooperSwitchToTeslaGunMode",
    "OCL_ShockTrooperRocketRifleModeTrigger", "OCL_GenericDummyRider2Trigger",
    "ShockTrooperRemoveUpgradeRocketRifleObject",
    "ShockTrooperRemoveUpgradeTeslaGunObject",
    "BerkutMissileDodgeJetLocomotor",
    "Command_RussiaShockTrooperSwitchToRockets",
    "Command_RussiaShockTrooperSwitchToTeslaGun",
}

# ---------------------------------------------------------------- module strips
# (object-name, module-tag) pairs removed verbatim by build.py.  Kept in
# sync with DROPS above; build.py asserts each strip removes >=1 module
# and that afterwards no dropped identifier is referenced.
MODULE_STRIPS = {
    "RussianInfantryShmelTrooper": [
        # (ModuleTag_Death06 / POISONED_BETA is KEPT: OCL_ToxicInfantryBeta
        # exists in base; stripping it left that death type uncovered)
        "ModuleTag_Medkit01",       # AutoHeal on Upgrade_RussiaMedPack
        "ModuleTag_RussiaInfantryBeserker01",
        "ModuleTag_MissileRangeUpgrade01",
        "ModuleTag_19",             # SubObjectsUpgrade (LargerClips launcher art)
        "ModuleTag_021",            # CommandSetUpgrade (LargerClips)
        "ModuleTag_GrizonAirDrop01",
        "ModuleTag_Surrender_Death",
    ],
    "RussiaInfantryShockTrooper_Var1": [
        "ModuleTag_Medkit01",
        "ModuleTag_GrizonAirDrop01",
        "ModuleTag_0324114256",     # EXTRA_8 suicide death
        # tesla-only rework: the whole rider/transformation block goes
        "ModuleTag_Transform01",    # RiderChangeContain
        "ModuleTag_Transform02",    # GrantUpgradeCreate
        "ModuleTag_Transform03",    # ProductionUpdate (switch queue)
        "ModuleTag_Transform04",    # FireWeaponCollide (rocket trigger)
        "ModuleTag_Transform05",    # ObjectCreationUpgrade
        "ModuleTag_Transform06",    # StatusBitsUpgrade
        "ModuleTag_Transform07",    # FireWeaponCollide (tesla trigger)
        "ModuleTag_Transform08",    # ObjectCreationUpgrade
        "ModuleTag_Transform09",    # StatusBitsUpgrade
    ],
}

# ---------------------------------------------------------------- audio remap
# ROTR audio events -> base-ShockWave/vanilla events (all verified present
# in the effective audio INI space by trace_closure.py).  Chosen for
# flavor: Shmel = China Tank Hunter (missile infantry), Shock Trooper =
# ShockWave heavy infantry-ish; weapon sounds get closest base analogue.
AUDIO_REMAP = {}   # filled after the trace report; see build.py

# ---------------------------------------------------------------- misc
# (6-8 were taken by the zzz-ZZZZZZZLKwaiInfantry stubs layer that landed
# mid-branch; integrate.py aborts loudly if these are occupied by merge day)
BARRACKS_SLOT_DEFAULT_SHMEL = 9
BARRACKS_SLOT_DEFAULT_SHOCK = 10
