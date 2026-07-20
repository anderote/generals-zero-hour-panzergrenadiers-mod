#!/usr/bin/env python3
"""kwai-arsenal -- Kwai "upgrade the hell out of everything" horde-defense pack
(ShockWave / GeneralsX).

Layer archive: zzz-ZZZZZZZZZZZZZZZZZZZZZZ0Arsenal.big (22 Z's + '0Arsenal':
sorts above zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big [21 Z's], below
zzz_ControlBarPro* / zzzz_FXEnhance). Whitelisted by the rebuilt Flagship's
guards. STAGE with --stage; the coordinator installs.

FEATURE 1 -- BATTLEMASTER FLEET RESEARCHES (per-tank purchases -> PLAYER
researches on War Factory page 3):
  * Fleet Speaker Towers $3000: the per-tank tower purchase
    (ObjectCreationUpgrade ModuleTag_PropTowerMount01 -> OCL_OverlordPropagandaTower,
    OBJECT Upgrade_ChinaOverlordPropagandaTower) is REPOINTED to the PLAYER
    research. Retrofit is engine-guaranteed: Player upgrade completion iterates
    every owned object and re-attempts all upgrade modules (Player.cpp:3250
    updateUpgradeModules loop), and new builds attempt at creation.
  * Fleet Point-Defense $3000: the per-tank PDL was a HelixContain RIDER pod
    (Tank_OCL_KwaiPDLPod -> Tank_ChinaPDLPod). RIDER-COEXISTENCE FINDING: the
    Battlemaster's HelixContain keeps exactly ONE portable-structure rider
    (HelixContain m_portableStructureID; the 3-way ERA/tower/pod exclusivity
    the kwai-pdl layer documents) -- there are no per-rider mount bones, so the
    tower and the pod can NEVER coexist as riders. Resolution: the tower keeps
    the rider slot (it is the visible one); the fleet PDL becomes a
    FireWeaponWhenDamagedBehavior reactive anti-missile LASER burst module ON
    the tank (the EDS-hull-PDL / kwai-fortress idiom, PLAYER-gated, reusing
    Tank_EmperorPDLWeapon). The pod machinery on the Battlemaster (mount OCU +
    2 exclusivity CommandSetUpgrades) is removed; the ERA plate OCU
    (ModuleTag_ArmorAddon02, cosmetic rider only -- the ERA stat modules
    ModuleTag_28/Armor_02 stay) is also removed so a researched fleet always
    gets its towers regardless of ERA order. Pod/tower/ERA machinery on OTHER
    units is untouched; the old per-tank buttons leave the Battlemaster sets
    (buttons/upgrades/OCLs/pod object stay defined -- dormant-stub discipline).
  * Expanded Crew Bays $2500: ContainCapacityUpgrade AddSlots=4 (bay 4 -> 8).

FEATURE 2 -- WAR FACTORY PAGE 3 (dozer page-flip idiom, new OBJECT tokens):
  page 2 slot 13 (was the kwai-fortress Expanded Battle Bunkers button) becomes
  the page-3 flip; page 3 = fleet researches 1-3, Expanded Battle Bunkers
  (moved) at 4, Gattling Doctrine II/III at 5-6, flip-up at 12, Evacuate
  (restored -- it serves the kwai-garrisons WF garrison) at 13, Sell at 14.
  Two new $0/0s OBJECT page tokens (GLA-worker token idiom) + two new flip
  buttons; 1<->2<->3 chaining via CommandSetUpgrade RemovesUpgrades resets.

FEATURE 3 -- GATTLING DOCTRINE II/III (HOSTED AT WF PAGE 3, NOT the prop
  center: all 50 prop-center doctrine-ladder sets are 14/14 full and slot 13
  is already the Satellite Uplink -- verified again this build). MECHANISM
  DEVIATION (engine fact): +25% DAMAGE tiers are impossible in pure data --
  WeaponBonusUpgrade can only set the single WEAPONBONUSCONDITION_PLAYER_UPGRADE
  bit (WeaponBonusUpgrade.cpp:91, no condition selector in the deployed fork)
  and that bit is already consumed on the whole gattling family by Chain Guns
  (kwai-doctrine README documents the same block for Tungsten Shells). The
  tiers instead use the doctrine ladders' own armor-tier idiom: each tier
  +25% of base HP (MaxHealthUpgrade, stacking on the 4 doctrine tiers) for
  Gattling Tank (350), Reaper (700, real object Tank_ChinaReaperTank_Real)
  and Gattling Cannon (1250); tier III also adds ExperienceScalarUpgrade
  AddXPScalar 1.0 (veterancy-driven damage -- the only data-legal stacking
  damage path). III requires II (RequiredUpgrade).

FEATURE 4 -- BARRACKS PAGE 2 (Kwai only): slot 11 was free on both Kwai
  barracks sets -> page-down there (reuses the shared GLA-worker OBJECT
  tokens + arrow buttons; they are per-object masks, so dozer/WF usage does
  not interfere). Page 2 hosts:
  * Body Armor I/II $1500/$3000 (II requires I): +20% of base HP each
    (doctrine armor-tier idiom) on the Kwai infantry family: Panzergrenadier,
    TankHunter, Hacker, Black Lotus (vanilla objects Kwai builds -- doctrine
    precedent), Sharpshooter, Shmel Trooper, Shock Trooper (_Var1).
    Excluded (documented): FlameThrower/MiniGunner/SiegeSoldier -- their real
    objects are other generals' units via BuildVariations stubs (Spec_/Infa_/
    vanilla), exactly the units kwai-doctrine's tiers also never covered.
  * Weapons Package I $2000: WeaponBonusUpgrade + per-weapon
    'WeaponBonus = PLAYER_UPGRADE DAMAGE 120% / RANGE 110%' lines -- ONLY for
    the three units whose PLAYER_UPGRADE bit is free (Sharpshooter, Shmel,
    Shock; Panzergrenadier and TankHunter already spend theirs on Advanced
    Infantry Doctrine). Cross-faction leak guard: build asserts no other
    effective object both references these weapons and carries a
    WeaponBonusUpgrade.
  * Weapons Package II $3500 (requires I): the same single-bit engine fact
    forbids a second stacked damage tier, so tier II is
    ExperienceScalarUpgrade AddXPScalar 1.0 on the five combat infantry
    (munitions training -> double veterancy rate -> real damage growth).
  Mines interaction: returning from page 2 is mines-aware (two return modules:
  ConflictsWith Upgrade_ChinaMines -> base set / RequiresAllTriggers with
  Upgrade_ChinaMines -> the EMP-mines set) so the EMP button state survives
  page flips.

FEATURE 5 (queued follow-up, FOLDED INTO THIS LAYER -- one build owns the top
  copies of the four shared files; extending kwai-fortress instead would force
  a fortress rebuild AND an arsenal rebuild for every change):
  KWAI BATTLE BUNKER -- dozer page 2 slot 10: Tank_ChinaBattleBunker, a clone
  of the China Infantry General's Infa_ChinaBunker ($800 / 8 s, 2200 HP,
  5-man GarrisonContain fire-out, mines family) adapted to Kwai: Side/prereq
  (Tank_ChinaBarracks)/command sets swapped, the four Kwai doctrine armor
  tiers added (+220 = 10% base each; the Infa original has no tier hooks),
  plus three per-bunker OBJECT purchases (kwai-fortress idiom):
    Reinforced Armor $600 (+50% = +1100 HP), PDL $800 (reactive LASER burst),
    Speaker Tower $500 (gated AutoHealBehavior aura 20 HP/s r150 incl. self).
  PROP-TOWER RE-INVESTIGATION (as asked): a REAL tower rider is still
  infeasible on a structure (one contain module per object; the bunker needs
  its GarrisonContain; riders need Helix/Overlord contains), and
  PropagandaTowerBehavior with an OBJECT UpgradeRequired still cannot gate the
  heal: doScan() reads the object mask ONLY for pulse-FX choice, while
  effectLogic() picks base-vs-upgraded heal rate via
  getControllingPlayer()->hasUpgradeComplete() -- the PLAYER mask, which never
  contains OBJECT upgrades -- so 'base 0% + upgraded 2%' heals 0% forever.
  The gated AutoHealBehavior aura is what actually works.

Usage: python3 build.py [--stage]   (--stage: write layer .big only, no install)
"""
import os, re, sys, hashlib, shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'hotkey-addon'))
import bigfile

ARCHIVE = 'zzz-' + 'Z' * 22 + '0Arsenal.big'
assert ARCHIVE == 'zzz-ZZZZZZZZZZZZZZZZZZZZZZ0Arsenal.big'
TAG = 'kwai-arsenal'
MODDIRS = [os.path.expanduser('~/GeneralsX/mods/ShockWaveSPE'),
           os.path.expanduser('~/GeneralsX/mods/ShockWave')]

# ---- tunable constants ----------------------------------------------------
COST_FLEET_TOWER, TIME_FLEET_TOWER = 3000, 45.0
COST_FLEET_PDL,   TIME_FLEET_PDL   = 3000, 45.0
COST_CREW_BAYS,   TIME_CREW_BAYS   = 2500, 40.0
COST_GATT2, TIME_GATT2 = 2500, 40.0
COST_GATT3, TIME_GATT3 = 4000, 60.0
COST_BA1, TIME_BA1 = 1500, 30.0
COST_BA2, TIME_BA2 = 3000, 45.0
COST_WP1, TIME_WP1 = 2000, 40.0
COST_WP2, TIME_WP2 = 3500, 45.0
COST_BB_ARMOR, COST_BB_PDL, COST_BB_SPEAKER = 600, 800, 500
COST_VA5, TIME_VA5 = 5000, 60.0   # Composite Armor V (standalone, requires IV)
COST_IA5, TIME_IA5 = 5000, 60.0   # Infantry Conditioning V (standalone, requires IV)
COST_DRAGON, TIME_DRAGON = 50000, 90.0   # Dragon Emperor super-heavy
DRAGON_HP_MULT   = 2       # MaxHealth/InitialHealth x2
DRAGON_GUN_MULT  = 1.5     # cannon damage x1.5
DRAGON_GUN_RANGE = 260     # was 240 (flagship long-barrel)
DRAGON_SCALE     = 1.15
DRAGON_MAX_SIMUL = 3
DRAGON_BAY_SLOTS = 12      # HelixContain 8 -> 12 (research adds +4 -> 16)
WM_BAY_SLOTS, JS7_BAY_SLOTS = 4, 6   # innate fire-out bays (BM parity kit)
BM_BAY_ADD       = 4       # Battlemaster HelixContain 4 -> 8
BM_PDL_TRIGGER   = 25      # min damage per hit triggering the fleet PDL burst
BB_PDL_TRIGGER   = 30      # battle-bunker burst trigger
GATT_TIER_RATIO  = 0.25    # per gattling tier: +25% of base HP
BA_TIER_RATIO    = 0.20    # per Body Armor tier: +20% of base HP
BB_ARMOR_RATIO   = 0.50    # battle-bunker Reinforced Armor: +50% of base HP
XP_SCALAR        = 1.0     # +100% experience (Gattling III / Weapons Package II)
WP1_DAMAGE, WP1_RANGE = '120%', '110%'
AURA_HEAL, AURA_DELAY, AURA_RADIUS = 20, 1000, 150

# ---- paths + expected effective owners ------------------------------------
OWN_FORT = 'zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big'
OWN_FLG  = 'zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big'
OWN_REB  = 'zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big'
OWN_THP  = 'zzz-ZZZZZZZZZZZZZZZZZZZ0TeslaHP.big'
OWN_SPE  = 'zz_SPE_Shw_ini.big'

P_CS  = 'Data\\INI\\CommandSet.ini'
P_CB  = 'Data\\INI\\CommandButton.ini'
P_UPG = 'Data\\INI\\Upgrade.ini'
P_STR = 'Data\\Generals.str'
P_WPN = 'Data\\INI\\Weapon.ini'
P_BM  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Battlemaster.ini'
P_WF  = 'Data\\INI\\Object\\China\\Tank\\Buildings\\WarFactory.ini'
P_BAR = 'Data\\INI\\Object\\China\\Tank\\Buildings\\Barracks.ini'
P_GT  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\GattlingTank.ini'
P_RP  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Reaper.ini'
P_GC  = 'Data\\INI\\Object\\China\\Tank\\Defences\\GattlingCannon.ini'
P_PG  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\Panzergrenadier.ini'
P_TH  = 'Data\\INI\\Object\\China\\Vanilla\\Infantry\\TankHunter.ini'
P_HK  = 'Data\\INI\\Object\\China\\Vanilla\\Infantry\\Hacker.ini'
P_BL  = 'Data\\INI\\Object\\China\\Vanilla\\Infantry\\BlackLotus.ini'
P_SS  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\Sharpshooter.ini'
P_SH  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShmelTrooper.ini'
P_ST  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShockTrooper.ini'
P_IB  = 'Data\\INI\\Object\\China\\Infantry\\Defences\\Bunker.ini'   # clone SOURCE only
P_BB  = 'Data\\INI\\Object\\China\\Tank\\Defences\\BattleBunker.ini' # NEW path
P_WM  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\WarMaster.ini'
P_JS  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\JS7.ini'
P_OV  = 'Data\\INI\\Object\\China\\Vanilla\\Vehicles\\Overlord.ini'
P_EMP = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\Emperor.ini'      # Dragon clone source (tier-V pass ships it)
P_DE  = 'Data\\INI\\Object\\China\\Tank\\Vehicles\\DragonEmperor.ini'  # NEW path
P_THS = 'Data\\INI\\Object\\China\\Tank\\Infantry\\TankHunter.ini'   # the Kwai STUB
P_PJ  = 'Data\\INI\\Object\\China\\Tank\\Infantry\\Panzerjager.ini'  # NEW path (clone)
OWN_KPDL = 'zzz-ZZZZZZZKwaiPDL.big'

EXPECT_OWNER = {P_CS: OWN_FORT, P_CB: OWN_FORT, P_UPG: OWN_FORT, P_STR: OWN_FORT,
                P_WPN: OWN_FLG, P_BM: OWN_FLG, P_PG: OWN_FLG, P_BAR: OWN_FLG,
                P_WF: OWN_REB, P_GT: OWN_REB, P_RP: OWN_REB, P_GC: OWN_REB,
                P_TH: OWN_REB, P_HK: OWN_REB, P_BL: OWN_REB, P_SS: OWN_REB,
                P_SH: OWN_REB, P_ST: OWN_THP, P_IB: OWN_SPE,
                P_WM: OWN_REB, P_JS: OWN_KPDL, P_OV: OWN_REB, P_EMP: OWN_FORT,
                P_THS: OWN_REB}
SHIPPED = [P_CS, P_CB, P_UPG, P_STR, P_WPN, P_BM, P_WF, P_BAR, P_GT, P_RP, P_GC,
           P_PG, P_TH, P_HK, P_BL, P_SS, P_SH, P_ST, P_BB, P_WM, P_JS, P_OV,
           P_EMP, P_DE, P_THS, P_PJ]
# NOTE: the doctrine tier-V pass at the end dynamically extends the shipped set
# with a full copy of EVERY effective file carrying a tier-IV module (exact
# tier-IV coverage parity); those extra paths get the same above-claim guard.

# ---- new identifiers ------------------------------------------------------
UP_FTOWER = 'Tank_Upgrade_FleetSpeakerTowers'
UP_FPDL   = 'Tank_Upgrade_FleetPointDefense'
UP_BAYS   = 'Tank_Upgrade_ExpandedCrewBays'
UP_G2     = 'Tank_Upgrade_GattlingDoctrineII'
UP_G3     = 'Tank_Upgrade_GattlingDoctrineIII'
UP_BA1    = 'Tank_Upgrade_KwaiBodyArmorI'
UP_BA2    = 'Tank_Upgrade_KwaiBodyArmorII'
UP_WP1    = 'Tank_Upgrade_KwaiWeaponsPackageI'
UP_WP2    = 'Tank_Upgrade_KwaiWeaponsPackageII'
UP_T3D    = 'Tank_Upgrade_KwaiWFPageThree'       # $0 OBJECT page token
UP_T3U    = 'Tank_Upgrade_KwaiWFPageTwoReturn'   # $0 OBJECT page token
UP_BBARM  = 'Tank_Upgrade_BattleBunkerArmor'
UP_BBPDL  = 'Tank_Upgrade_BattleBunkerPDL'
UP_BBSPK  = 'Tank_Upgrade_BattleBunkerSpeaker'
CB_FTOWER = 'Tank_Command_UpgradeFleetSpeakerTowers'
CB_FPDL   = 'Tank_Command_UpgradeFleetPointDefense'
CB_BAYS   = 'Tank_Command_UpgradeExpandedCrewBays'
CB_G2     = 'Tank_Command_UpgradeGattlingDoctrineII'
CB_G3     = 'Tank_Command_UpgradeGattlingDoctrineIII'
CB_BA1    = 'Tank_Command_UpgradeKwaiBodyArmorI'
CB_BA2    = 'Tank_Command_UpgradeKwaiBodyArmorII'
CB_WP1    = 'Tank_Command_UpgradeKwaiWeaponsPackageI'
CB_WP2    = 'Tank_Command_UpgradeKwaiWeaponsPackageII'
CB_T3D    = 'Tank_Command_WarFactoryPageThree'
CB_T3U    = 'Tank_Command_WarFactoryPageTwoReturn'
CB_BBBLD  = 'Tank_Command_ConstructChinaBattleBunker'
CB_BBARM  = 'Tank_Command_UpgradeBattleBunkerArmor'
CB_BBPDL  = 'Tank_Command_UpgradeBattleBunkerPDL'
CB_BBSPK  = 'Tank_Command_UpgradeBattleBunkerSpeaker'
OBJ_BB    = 'Tank_ChinaBattleBunker'
CS_WF3    = 'Tank_ChinaWarFactoryCommandSet_Down2'
CS_BAR2   = 'Tank_ChinaBarracksCommandSet_Down'
CS_BBM    = 'Tank_ChinaBattleBunkerCommandSet'
CS_BBU    = 'Tank_ChinaBattleBunkerCommandSetUpgrade'
UP_VA5   = 'Tank_Upgrade_KwaiVehicleArmor5'
UP_IA5   = 'Tank_Upgrade_KwaiInfantryArmor5'
CB_VA5   = 'Tank_Command_UpgradeKwaiVehicleArmor5'
CB_IA5   = 'Tank_Command_UpgradeKwaiInfantryArmor5'
OBJ_DE   = 'Tank_ChinaDragonEmperor'
CB_DEBLD = 'Tank_Command_ConstructChinaDragonEmperor'
W_DEGUN  = 'Tank_DragonEmperorTankGun'
W_DEGUND = 'Tank_DragonEmperorTankGun_Dummy'
MODTAGS = ['ModuleTag_KA_PDL01', 'ModuleTag_KA_Bay01', 'ModuleTag_KA_Page01',
           'ModuleTag_KA_Page02', 'ModuleTag_KA_BPage01', 'ModuleTag_KA_BPage02',
           'ModuleTag_KA_BPage03', 'ModuleTag_KA_GD2', 'ModuleTag_KA_GD3',
           'ModuleTag_KA_GDXP', 'ModuleTag_KA_BA1', 'ModuleTag_KA_BA2',
           'ModuleTag_KA_WP1', 'ModuleTag_KA_WP2XP', 'ModuleTag_KA_BBArmor01',
           'ModuleTag_KA_BBPDL01', 'ModuleTag_KA_BBAura01',
           'ModuleTag_KA_VA5', 'ModuleTag_KA_IA5']
NEW_IDS = [UP_FTOWER, UP_FPDL, UP_BAYS, UP_G2, UP_G3, UP_BA1, UP_BA2, UP_WP1,
           UP_WP2, UP_T3D, UP_T3U, UP_BBARM, UP_BBPDL, UP_BBSPK,
           CB_FTOWER, CB_FPDL, CB_BAYS, CB_G2, CB_G3, CB_BA1, CB_BA2, CB_WP1,
           CB_WP2, CB_T3D, CB_T3U, CB_BBBLD, CB_BBARM, CB_BBPDL, CB_BBSPK,
           OBJ_BB, CS_WF3, CS_BAR2, CS_BBM, CS_BBU,
           UP_VA5, UP_IA5, CB_VA5, CB_IA5, OBJ_DE, CB_DEBLD, W_DEGUN, W_DEGUND,
           'Tank_ChinaInfantryPanzerjager', 'ModuleTag_KA_Horde01'] + MODTAGS
OBJ_PJ = 'Tank_ChinaInfantryPanzerjager'
LABEL_BASES = ['FleetSpeakerTowers', 'FleetPointDefense', 'ExpandedCrewBays',
               'GattlingDoctrineII', 'GattlingDoctrineIII', 'KwaiBodyArmorI',
               'KwaiBodyArmorII', 'KwaiWeaponsPackageI', 'KwaiWeaponsPackageII',
               'BattleBunkerArmor', 'BattleBunkerPDL', 'BattleBunkerSpeaker',
               'KwaiVehicleArmor5', 'KwaiInfantryArmor5']
NEW_LABELS = ['OBJECT:KwaiBattleBunker', 'CONTROLBAR:ConstructChinaBattleBunker',
              'CONTROLBAR:ToolTipChinaBuildBattleBunker',
              'OBJECT:DragonEmperor', 'CONTROLBAR:ConstructChinaDragonEmperor',
              'CONTROLBAR:ToolTipChinaBuildDragonEmperor']
for b in LABEL_BASES:
    NEW_LABELS += ['UPGRADE:' + b, 'CONTROLBAR:Upgrade' + b, 'CONTROLBAR:ToolTipUpgrade' + b]

# reused assets (drift-guarded)
W_PDL = 'Tank_EmperorPDLWeapon'
CAM = {'tower': 'SSOLSpeaker', 'pdl': 'SNBlackSharkJammer', 'bays': 'SNSuperBunk',
       'gatt': 'SNTankeGenGattlingTank', 'ba': 'SNTankTitaniumArmor',
       'wp': 'SSGattling', 'down': 'SSChinaCommandSetDown', 'up': 'SSChinaCommandSetUp',
       'bb': 'SNSuperBunk', 'bbarm': 'SSCompositeArmor', 'dragon': 'SNEmpTank',
       'va5': 'SNTankTitaniumArmor', 'ia5': 'SNTankTitaniumArmor'}
SND_RESEARCH, SND_OBJECT = 'ReaperVoiceUpgrade', 'OverlordExpansion'

def die(msg): print('BUILD FAILED:', msg); sys.exit(1)
def check(c, msg):
    if not c: die(msg)
def sorted_bigs(d):
    return sorted((f for f in os.listdir(d) if f.lower().endswith('.big')), key=str.lower)

# ---------------------------------------------------------------- sort order
for d in MODDIRS:
    probe = sorted(set(sorted_bigs(d)) | {ARCHIVE}, key=str.lower)
    i = probe.index(ARCHIVE); below = probe[:i]; above = probe[i+1:]
    for need in [OWN_FORT, OWN_FLG, OWN_REB, OWN_THP,
                 'zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big']:
        check(need in below, f'{d}: {need} must sort below us')
    for a in above:
        check(a.lower().startswith('zzz_controlbarpro') or a.lower().startswith('zzzz_'),
              f'{d}: unexpected archive above us: {a}')
    check(any(a.lower().startswith('zzz_controlbarpro') for a in above),
          f'{d}: ControlBarPro must sort above us')
print('sort position OK in both dirs (above Fortress [21Z], below ControlBarPro*/FXEnhance)')

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
for p, owner in EXPECT_OWNER.items():
    check(p.lower() in eff0, f'missing effective file {p}')
    check(eff0[p.lower()][0] == owner, f'{p}: owner is {eff0[p.lower()][0]} not {owner}')
    check(p.lower() in eff1 and eff0[p.lower()][1] == eff1[p.lower()][1],
          f'{p} differs between mod dirs')
for d in MODDIRS:
    for b in sorted_bigs(d):
        if b.lower() == ARCHIVE.lower():
            continue
        claimed = {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}
        for pnew in (P_BB, P_DE, P_PJ):
            check(pnew.lower() not in claimed, f'{d}/{b} already claims new path {pnew}')
        if b.lower() > ARCHIVE.lower():
            for p in SHIPPED:
                check(p.lower() not in claimed, f'{d}/{b} (above us) claims {p}')
print('effective sources OK (19 files; owners as expected; dirs byte-agree; '
      'new path unclaimed; nothing above claims shipped paths)')

SRC = {p: eff0[p.lower()][1].decode('latin-1') for p in SHIPPED if p not in (P_BB, P_DE, P_PJ)}
SRC[P_IB] = eff0[P_IB.lower()][1].decode('latin-1')

# ------------------------------------------ collision check
all_text = '\n'.join(data.decode('latin-1') for p, (b, data) in eff0.items()
                     if p.endswith('.ini') or p.endswith('.str'))
for ident in NEW_IDS + NEW_LABELS:
    check(not re.search(r'\b%s\b' % re.escape(ident), all_text),
          f'identifier collision: {ident} already exists in effective space')
print(f'new identifiers collision-free ({len(NEW_IDS)} ids, {len(NEW_LABELS)} labels)')

# ------------------------------------------ drift guards
mapped = '\n'.join(data.decode('latin-1') for p, (b, data) in eff0.items()
                   if '\\mappedimages\\' in p)
for img in sorted(set(CAM.values())):
    check(re.search(r'^MappedImage\s+%s\s*$' % re.escape(img), mapped, re.M),
          f'cameo MappedImage missing: {img}')
for snd in [SND_RESEARCH, SND_OBJECT, 'MoneyWithdraw']:
    check(re.search(r'^AudioEvent\s+%s\b' % snd, all_text, re.M), f'AudioEvent {snd} missing')
# engine-fact donors: EDS/fortress reactive-PDL idiom weapon (inside OUR Weapon.ini source)
wb = re.search(r'^Weapon %s\b(.*?)^End' % W_PDL, SRC[P_WPN], re.M | re.S)
check(wb and 'RadiusDamageAffects = ENEMIES' in wb.group(1), f'{W_PDL} idiom drifted')
# GLA-worker page-token idiom (we clone its shape for the WF page-3 tokens)
tok = re.search(r'^Upgrade Upgrade_GLAWorkerFakeCommandSet\b(.*?)^End', SRC[P_UPG], re.M | re.S)
check(tok and 'Type               = OBJECT' in tok.group(1) and 'BuildCost          = 0' in tok.group(1),
      'GLA-worker page-token idiom drifted')
for btn in ['Command_ChinaButtonCommandSetOneDown', 'Command_ChinaButtonCommandSetOneUp',
            'Command_BunkerExit', 'Command_Evacuate', 'Command_Stop', 'Command_Sell',
            'Command_UpgradeChinaMines', 'Command_UpgradeEMPMines',
            'Tank_Command_UpgradeExpandedBattleBunkers']:
    check(re.search(r'^CommandButton\s+%s\b' % btn, SRC[P_CB], re.M), f'button {btn} missing')
print('drift guards OK (cameos, sounds, PDL weapon, page-token idiom, reused buttons)')

# ---------------------------------------------------------------- helpers
def audit(label, old_text, new_text, exp_removed, exp_added):
    co = Counter(l.rstrip('\r') for l in old_text.split('\n'))
    cn = Counter(l.rstrip('\r') for l in new_text.split('\n'))
    removed = sorted((co - cn).elements()); added = sorted((cn - co).elements())
    # net the expectations against each other exactly like a multiset diff does
    # (e.g. removed '  End' lines partially cancel against added '  End' lines)
    er = Counter(x.rstrip('\r') for x in exp_removed)
    ea = Counter(x.rstrip('\r') for x in exp_added)
    exp_removed_net = sorted((er - ea).elements())
    exp_added_net = sorted((ea - er).elements())
    check(removed == exp_removed_net,
          f'{label}: removed-line audit mismatch:\n got {removed}\n exp {exp_removed_net}')
    check(added == exp_added_net,
          f'{label}: added-line audit mismatch:\n got {added}\n exp {exp_added_net}')
    print(f'{label}: diff audit OK (-{len(removed)}/+{len(added)} lines)')

def get_block(text, kind, name, label):
    m = re.search(r'^%s\s+%s\b[^\n]*\n(.*?)^End[ \t\r]*$' % (kind, re.escape(name)),
                  text, re.M | re.S)
    check(m, f'{label}: {kind} {name} missing'); return m

def remove_module(text, tag):
    """Remove the whole two-space-indented module block carrying `tag`.
    Returns (new_text, removed_lines)."""
    m = re.search(r'^ {2}Behavior = \w+ %s\b.*?^ {2}End[ \t\r]*$\r?\n?' % re.escape(tag),
                  text, re.M | re.S)
    check(m, f'module {tag} not found for removal')
    block = m.group(0)
    removed = [l for l in block.split('\n') if l.strip() != '']
    # also swallow ONE preceding blank line if present, keep audit exact
    return text[:m.start()] + text[m.end():], removed

def object_span(text, name):
    m = re.search(r'^Object %s\b.*?^End[ \t\r]*$' % re.escape(name), text, re.M | re.S)
    check(m, f'Object {name} not found')
    return m

def insert_after_body(text, obj_name, lines):
    """Insert module lines right after the object's Body block End."""
    om = object_span(text, obj_name)
    block = om.group(0)
    bm = re.search(r'^ {2}Body\s*=.*?^ {2}End[ \t\r]*$', block, re.M | re.S)
    check(bm, f'{obj_name}: Body block not found')
    ins = bm.end()
    new_block = block[:ins] + '\n' + '\n'.join(lines) + block[ins:]
    return text[:om.start()] + new_block + text[om.end():]

def mhu(tag, up, add, note):
    return [f'  Behavior = MaxHealthUpgrade {tag} ; {TAG}: {note}',
            f'    TriggeredBy   = {up}',
            f'    AddMaxHealth  = {add}',
            '    ChangeType    = ADD_CURRENT_HEALTH_TOO',
            '  End']

def fmt_hp(base, ratio):
    v = base * ratio
    s = ('%.1f' % v).rstrip('0').rstrip('.')
    return s if '.' in s else s + '.0'

def base_hp(text, obj_name):
    om = object_span(text, obj_name)
    m = re.search(r'MaxHealth\s*=\s*([\d.]+)', om.group(0))
    check(m, f'{obj_name}: MaxHealth not found')
    return float(m.group(1))

# ================================================ Battlemaster.ini (feature 1)
bm_src = SRC[P_BM]
t = bm_src
removed_all = []
for tag in ['ModuleTag_ArmorAddon02', 'ModuleTag_PropTowerCmdSet01',
            'ModuleTag_KPDL_Mount01', 'ModuleTag_KPDL_CmdSet01', 'ModuleTag_KPDL_CmdSet02']:
    t, rem = remove_module(t, tag)
    removed_all += rem
# repoint the tower mount to the PLAYER research; drop its ConflictsWith
old_trig = '    TriggeredBy   = Upgrade_ChinaOverlordPropagandaTower'
new_trig = f'    TriggeredBy   = {UP_FTOWER} ; {TAG}: fleet-wide PLAYER research (was per-tank OBJECT purchase)'
check(t.count(old_trig) == 1, 'tower mount TriggeredBy line not unique')
t = t.replace(old_trig, new_trig, 1)
m = re.search(r'^ {4}ConflictsWith = Upgrade_TankLightArmor Tank_Upgrade_KwaiPDL[^\n]*$', t, re.M)
check(m, 'tower mount ConflictsWith line not found')
conflict_line = m.group(0)
t = t[:m.start()] + t[m.end() + 1:] if t[m.end():m.end()+1] == '\n' else t[:m.start()] + t[m.end():]
BM_ADD = [
    f'  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_KA_PDL01 ; {TAG}: Fleet Point-Defense -- reactive anti-missile LASER burst (single HelixContain rider slot belongs to the speaker tower; pod idiom not coexistable)',
    '    StartsActive  = No',
    f'    TriggeredBy   = {UP_FPDL}',
    '    DamageTypes   = ALL',
    f'    ReactionWeaponPristine      = {W_PDL}',
    f'    ReactionWeaponDamaged       = {W_PDL}',
    f'    ReactionWeaponReallyDamaged = {W_PDL}',
    f'    DamageAmount    = {BM_PDL_TRIGGER}',
    '  End',
    f'  Behavior = ContainCapacityUpgrade ModuleTag_KA_Bay01 ; {TAG}: Expanded Crew Bays -- bunker bay 4 -> {4 + BM_BAY_ADD} (fork ContainCapacityUpgrade)',
    f'    TriggeredBy = {UP_BAYS}',
    f'    AddSlots    = {BM_BAY_ADD}',
    '  End',
]
anchor = re.search(r'^ {2}Behavior = ProductionUpdate ModuleTag_PropTowerProduction01\b.*?^ {2}End[ \t\r]*$',
                   t, re.M | re.S)
check(anchor, 'Battlemaster ProductionUpdate anchor missing')
t = t[:anchor.end()] + '\n' + '\n'.join(BM_ADD) + t[anchor.end():]
bm_new_text = t
audit('Battlemaster.ini (fleet conversion)', bm_src, bm_new_text,
      removed_all + [old_trig, conflict_line], BM_ADD + [new_trig])
for need in ['ModuleTag_ArmorAddon01', 'Slots                   = 4',
             'ModuleTag_PropTowerMount01', 'OCL_OverlordPropagandaTower',
             'ModuleTag_PropTowerProduction01', 'ModuleTag_TU_Reactive01',
             'ModuleTag_TU_Hull01', 'ModuleTag_TU_Shield01', 'ModuleTag_TU_Shield02',
             'ModuleTag_KD_Armor1', 'ModuleTag_KD_Tungsten01', 'ModuleTag_28',
             'ModuleTag_GP_Crew01']:
    check(need in bm_new_text, f'Battlemaster lost hunk: {need!r}')
for gone in ['ModuleTag_ArmorAddon02', 'ModuleTag_KPDL_Mount01', 'ModuleTag_KPDL_CmdSet01',
             'ModuleTag_KPDL_CmdSet02', 'ModuleTag_PropTowerCmdSet01', 'Tank_OCL_KwaiPDLPod',
             'OCL_BattleMasterArmorAddons', 'ConflictsWith = Upgrade_TankLightArmor']:
    check(gone not in bm_new_text, f'Battlemaster still contains removed hunk: {gone!r}')
check(f'TriggeredBy   = {UP_FTOWER}' in bm_new_text, 'tower mount not repointed')
bm_new = bm_new_text.encode('latin-1')
print('Battlemaster.ini: per-tank machinery removed, tower mount -> PLAYER research, '
      f'+fleet PDL burst, +bay {BM_BAY_ADD}')

# ================================= Warmaster / JS-7 / Overlord (2nd amendment)
# FINDINGS (effective data): the innate-coax and horde items of the parity kit
# are ALREADY present -- vehicle-kit gave the Warmaster the innate
# ShwBattleMasterCoaxMGWeapon TERTIARY (its WeaponSet carries the layer note),
# the JS-7 carries its own innate Golem HMGs (SECONDARY+TERTIARY), and BOTH
# already have HordeUpdate modules (the Battlemaster's ModuleTag_04 horde is
# also verified below). What remains is item 3: the fire-out infantry bay.
# Both tanks already own a HelixContain (the kwai-pdl pod SEAT, Slots=1
# PORTABLE_STRUCTURE): the rider slot is separate from the passenger list and
# bypasses the allow filter, so widening that same contain to the BM bay
# config gives bay + pod seat in one module -- exactly the BM's own layout.
def kit_bay(text, path_label, slots):
    old = ('    Slots                   = 1\n'
           '    DamagePercentToUnits    = 100%\n'
           '    AllowInsideKindOf       = PORTABLE_STRUCTURE\n'
           '    ForbidInsideKindOf      = AIRCRAFT BOAT\n'
           '    ExitDelay               = 100\n'
           '    NumberOfExitPaths       = 1\n'
           '    PassengersAllowedToFire = No')
    new = (f'    Slots                   = {slots} ; {TAG}: BM-parity fire-out bay (was 1: pod seat only; the pod rides the separate rider slot)\n'
           '    DamagePercentToUnits    = 25% ; PassengerSurvival parity\n'
           '    AllowInsideKindOf       = INFANTRY\n'
           '    ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT\n'
           '    EnterSound              = GarrisonEnter\n'
           '    ExitSound               = GarrisonExit\n'
           '    ExitDelay               = 100\n'
           '    NumberOfExitPaths       = 1\n'
           '    PassengersAllowedToFire = Yes')
    for eol in ('\r\n', '\n'):
        old_e = old.replace('\n', eol); new_e = new.replace('\n', eol)
        if text.count(old_e) == 1:
            return text.replace(old_e, new_e, 1), old.split('\n'), new.split('\n')
    die(f'{path_label}: pod-seat HelixContain block drifted')

def fleet_modules(pdl=True, bays=True):
    out = []
    if pdl:
        out += [f'  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_KA_PDL01 ; {TAG}: Fleet Point-Defense -- reactive anti-missile LASER burst',
                '    StartsActive  = No',
                f'    TriggeredBy   = {UP_FPDL}',
                '    DamageTypes   = ALL',
                f'    ReactionWeaponPristine      = {W_PDL}',
                f'    ReactionWeaponDamaged       = {W_PDL}',
                f'    ReactionWeaponReallyDamaged = {W_PDL}',
                f'    DamageAmount    = {BM_PDL_TRIGGER}',
                '  End']
    if bays:
        out += [f'  Behavior = ContainCapacityUpgrade ModuleTag_KA_Bay01 ; {TAG}: Expanded Crew Bays -- +4 seats (fork ContainCapacityUpgrade)',
                f'    TriggeredBy = {UP_BAYS}',
                f'    AddSlots    = {BM_BAY_ADD}',
                '  End']
    return out

hv_new = {}
for p, obj, slots in [(P_WM, 'Tank_ChinaTankWarMaster', WM_BAY_SLOTS),
                      (P_JS, 'Tank_ChinaTankJS7', JS7_BAY_SLOTS)]:
    src = SRC[p]
    check('HordeUpdate' in src, f'{p}: HordeUpdate missing (parity item 2 expected innate)')
    check(('ShwBattleMasterCoaxMGWeapon' in src) or ('GolemHeavyMachineGunGun' in src),
          f'{p}: innate coax/MG missing (parity item 1 expected innate)')
    t2, oldl, newl = kit_bay(src, p, slots)
    mods = fleet_modules(pdl=True, bays=True)
    m = re.search(r'^ {2}Behavior = ObjectCreationUpgrade ModuleTag_KPDL_Mount01\b.*?^ {2}End[ \t\r]*$',
                  t2, re.M | re.S)
    check(m, f'{p}: KPDL_Mount01 anchor missing')
    t2 = t2[:m.end()] + '\n' + '\n'.join(mods) + t2[m.end():]
    audit(f'{p.split(chr(92))[-1]} (parity bay + fleet modules)', src, t2, oldl, newl + mods)
    for need in ['ModuleTag_KPDL_Bay01', 'ModuleTag_KPDL_Mount01', 'HordeUpdate']:
        check(need in t2, f'{p} lost hunk: {need!r}')
    hv_new[p] = t2.encode('latin-1')
    print(f'{p.split(chr(92))[-1]}: bay widened to {slots} fire-out seats (+pod rider seat kept), '
          '+fleet PDL burst, +crew-bays module')
# Overlord: PDL burst only (own rider-choice system incl. its own tower purchase;
# its battle-bunker rider already gets +3 from the Fortress layer -- asserted)
ov_src = SRC[P_OV]
mods = fleet_modules(pdl=True, bays=False)
m = re.search(r'^ {2}Behavior = ProductionUpdate ModuleTag_10\b.*?^ {2}End[ \t\r]*$', ov_src, re.M | re.S)
check(m, 'Overlord ProductionUpdate anchor missing')
ov_new_text = ov_src[:m.end()] + '\n' + '\n'.join(mods) + ov_src[m.end():]
audit('Overlord.ini (+fleet PDL burst)', ov_src, ov_new_text, [], mods)
for need in ['Behavior = OverlordContain ModuleTag_06', 'ModuleTag_07', 'ModuleTag_08', 'ModuleTag_09']:
    check(need in ov_new_text, f'Overlord lost hunk: {need!r}')
misc_eff = eff0['data\\ini\\object\\china\\vanilla\\chinamisc.ini'][1].decode('latin-1')
check(misc_eff.count('Behavior = ContainCapacityUpgrade') == 1,
      'Overlord battle-bunker rider ContainCapacityUpgrade count drifted (Fortress +3 expected exactly once)')
ov_new = ov_new_text.encode('latin-1')
print('Overlord.ini: +fleet PDL burst (towers/bays excluded: own rider-choice system; '
      'rider bunker +3 comes from the Fortress layer)')

# ================================================ Dragon Emperor (super-heavy)
emp_src = SRC[P_EMP]
t = emp_src
DE_PATCHES = [
    ('Object Tank_ChinaTankEmperor',
     f'Object {OBJ_DE} ; {TAG}: Dragon Emperor super-heavy (clone of Tank_ChinaTankEmperor)'),
    ('  DisplayName         = OBJECT:Tank_Overlord',
     '  DisplayName         = OBJECT:DragonEmperor'),
    ('  BuildCost       = 19200   ; flagship-emperor: 8x flagship pricing (was 2400)',
     f'  BuildCost       = {COST_DRAGON}   ; {TAG}: super-heavy flagship pricing'),
    ('  BuildTime       = 20.0          ;in seconds    ',
     f'  BuildTime       = {TIME_DRAGON}          ; {TAG}: super-heavy build time'),
    ('    MaxHealth       = 1100',
     f'    MaxHealth       = {1100 * DRAGON_HP_MULT} ; {TAG}: x{DRAGON_HP_MULT}'),
    ('    InitialHealth   = 1100',
     f'    InitialHealth   = {1100 * DRAGON_HP_MULT} ; {TAG}: x{DRAGON_HP_MULT}'),
    ('    Slots                   = 8 ; zzz-ZZZZZZZKwaiPDL: was 10 - freed exit-cameo slot 9 for the PDL purchase button',
     f'    Slots                   = {DRAGON_BAY_SLOTS} ; {TAG}: super-heavy bay, was 8 (research adds +4 -> {DRAGON_BAY_SLOTS + BM_BAY_ADD})'),
]
for old, new in DE_PATCHES:
    check(t.count(old + '\n') == 1 or t.count(old + '\r\n') == 1,
          f'Dragon patch target not unique: {old[:50]!r}')
    if t.count(old + '\r\n') == 1:
        t = t.replace(old + '\r\n', new + '\r\n', 1)
    else:
        t = t.replace(old + '\n', new + '\n', 1)
de_removed = [o for o, n in DE_PATCHES]
de_added = [n for o, n in DE_PATCHES]
# cannon repoint: 2x PRIMARY dummy + 2x SECONDARY (both weapon-set variants)
t, n = re.subn(r'(PRIMARY Tank_EmperorTankGun_Dummy)\b', f'PRIMARY {W_DEGUND}', t)
check(n == 2, f'Dragon PRIMARY dummy repoint expected 2, got {n}')
t, n = re.subn(r'(SECONDARY Tank_EmperorTankGun)\b', f'SECONDARY {W_DEGUN}', t)
check(n == 2, f'Dragon SECONDARY repoint expected 2, got {n}')
# super-heavy template fields (precedents: MaxSimultaneousOfType on heroes,
# Scale on rotr units)
DE_FIELDS = [f'  Scale                = {DRAGON_SCALE} ; {TAG}: super-heavy silhouette',
             f'  MaxSimultaneousOfType = {DRAGON_MAX_SIMUL} ; {TAG}: flagship cap']
m = re.search(r'^ {2}Side\s+=\s+ChinaTankGeneral[^\n]*$', t, re.M)
check(m, 'Dragon Side anchor missing')
t = t[:m.end()] + '\n' + '\n'.join(DE_FIELDS) + t[m.end():]
de_new_text = t
# bay math: 12 + KF_Bay01's +4 = 16
check(f'Slots                   = {DRAGON_BAY_SLOTS}' in de_new_text
      and 'ModuleTag_KF_Bay01' in de_new_text
      and re.search(r'ModuleTag_KF_Bay01.*?AddSlots\s*=\s*4', de_new_text, re.S),
      f'Dragon bay math must land on {DRAGON_BAY_SLOTS}+4')
check('Tank_EmperorTankGun' not in re.sub(r'\bTank_DragonEmperorTankGun(_Dummy)?\b', '', de_new_text),
      'stale Emperor cannon reference in Dragon')
de_rm = [l for l in emp_src.split('\n')
         if re.search(r'PRIMARY Tank_EmperorTankGun_Dummy\b', l)
         or re.search(r'SECONDARY Tank_EmperorTankGun\b', l)]
check(len(de_rm) == 4, f'expected 4 cannon lines in clone source, got {len(de_rm)}')
de_ad = [re.sub(r'PRIMARY Tank_EmperorTankGun_Dummy\b', f'PRIMARY {W_DEGUND}',
         re.sub(r'SECONDARY Tank_EmperorTankGun\b', f'SECONDARY {W_DEGUN}', l)) for l in de_rm]
audit('DragonEmperor.ini (clone of Emperor)', emp_src, de_new_text,
      de_removed + de_rm, de_added + de_ad + DE_FIELDS)
for need in ['ModuleTag_EDS_PDL01', 'ModuleTag_EmperorInnatePDL', 'ModuleTag_KD_Armor4',
             'ModuleTag_KF_Bay01', 'Behavior = HelixContain ModuleTag_06',
             'CommandSet = Tank_ChinaTankEmperorDefaultCommandSet']:
    check(need in de_new_text, f'Dragon lost clone hunk: {need!r}')
print(f'DragonEmperor.ini built ({OBJ_DE}: ${COST_DRAGON}/{TIME_DRAGON}s, HP x{DRAGON_HP_MULT}, '
      f'guns x{DRAGON_GUN_MULT} @ {DRAGON_GUN_RANGE}, bay {DRAGON_BAY_SLOTS}+4, '
      f'scale {DRAGON_SCALE}, cap {DRAGON_MAX_SIMUL})')

# ================================================ WarFactory.ini (page 3 flips)
wf_src = SRC[P_WF]
WF_ADD = [
    f'  Behavior = CommandSetUpgrade ModuleTag_KA_Page01 ; {TAG}: page-down -> WF page 3 (dozer page-flip idiom, own tokens)',
    f'    TriggeredBy     = {UP_T3D}',
    f'    RemovesUpgrades = {UP_T3U}',
    f'    CommandSet      = {CS_WF3}',
    '  End',
    f'  Behavior = CommandSetUpgrade ModuleTag_KA_Page02 ; {TAG}: page-up -> WF page 2',
    f'    TriggeredBy     = {UP_T3U}',
    f'    RemovesUpgrades = {UP_T3D} {UP_T3U}',
    '    CommandSet      = Tank_ChinaWarFactoryCommandSet_Down',
    '  End',
]
m = re.search(r'^ {2}Behavior = CommandSetUpgrade ModuleTag_CU_Page02\b.*?^ {2}End[ \t\r]*$',
              wf_src, re.M | re.S)
check(m, 'WarFactory ChaosUnits page-flip anchor missing')
wf_new_text = wf_src[:m.end()] + '\n' + '\n'.join(WF_ADD) + wf_src[m.end():]
# Tank pairs: QuantityModifier inside the WF ProductionUpdate (stub/concrete
# names matched at queue time, same engine evidence as the barracks pairs).
WF_QM = [f'    QuantityModifier = Tank_ChinaTankBattleMaster   2 ; {TAG}: Battlemaster pairs, two per click',
         f'    QuantityModifier = Tank_ChinaTankGattling   2 ; {TAG}: Gattling Tank pairs, two per click']
pm = re.search(r'^( {2}Behavior = ProductionUpdate ModuleTag_12[^\n]*\n)', wf_new_text, re.M)
check(pm, 'WarFactory ProductionUpdate anchor missing')
wf_new_text = wf_new_text[:pm.end()] + '\n'.join(WF_QM) + '\n' + wf_new_text[pm.end():]
audit('WarFactory.ini (+page-3 flip modules, +tank pairs)', wf_src, wf_new_text, [], WF_ADD + WF_QM)
for need in ['ModuleTag_CU_Page01', 'ModuleTag_KG_Garrison01', 'Behavior = ProductionUpdate ModuleTag_12',
             'QuantityModifier = Tank_ChinaTankBattleMaster   2',
             'QuantityModifier = Tank_ChinaTankGattling   2']:
    check(need in wf_new_text, f'WarFactory lost hunk: {need!r}')
wf_new = wf_new_text.encode('latin-1')
print('WarFactory.ini: +2 page-3 flip modules (chain 1<->2<->3), +Battlemaster/Gattling x2')

# ================================================ Barracks.ini (page flips)
bar_src = SRC[P_BAR]
BAR_ADD = [
    f'  Behavior = CommandSetUpgrade ModuleTag_KA_BPage01 ; {TAG}: page-down -> barracks page 2 (shared GLA-worker tokens; OBJECT masks are per-object)',
    '    TriggeredBy     = Upgrade_GLAWorkerFakeCommandSet',
    '    RemovesUpgrades = Upgrade_GLAWorkerRealCommandSet',
    f'    CommandSet      = {CS_BAR2}',
    '  End',
    f'  Behavior = CommandSetUpgrade ModuleTag_KA_BPage02 ; {TAG}: page-up -> page 1 (no mines yet)',
    '    TriggeredBy     = Upgrade_GLAWorkerRealCommandSet',
    '    ConflictsWith   = Upgrade_ChinaMines',
    '    RemovesUpgrades = Upgrade_GLAWorkerFakeCommandSet Upgrade_GLAWorkerRealCommandSet',
    '    CommandSet      = Tank_ChinaBarracksCommandSet',
    '  End',
    f'  Behavior = CommandSetUpgrade ModuleTag_KA_BPage03 ; {TAG}: page-up -> page 1 EMP-mines variant (mines-aware return)',
    '    TriggeredBy     = Upgrade_GLAWorkerRealCommandSet Upgrade_ChinaMines',
    '    RequiresAllTriggers = Yes',
    '    RemovesUpgrades = Upgrade_GLAWorkerFakeCommandSet Upgrade_GLAWorkerRealCommandSet',
    '    CommandSet      = Tank_ChinaBarracksCommandSetUpgrade',
    '  End',
]
m = re.search(r'^ {2}Behavior = CommandSetUpgrade ModuleTag_25\b.*?^ {2}End[ \t\r]*$',
              bar_src, re.M | re.S)
check(m, 'Barracks mines CommandSetUpgrade anchor missing')
bar_new_text = bar_src[:m.end()] + '\n' + '\n'.join(BAR_ADD) + bar_src[m.end():]
# Panzerjaeger pairs: QuantityModifier referencing the STUB name -- correct
# because matching happens at QUEUE time against the queued template
# (ProductionUpdate.cpp queueCreateUnit: isEquivalentTo(unitType), the button's
# Object), while BuildVariations only resolves later per spawned unit inside
# ThingFactory::newObject (ProductionUpdate.cpp:815); isEquivalentTo covers
# identity/override/reskin only (ThingTemplate.cpp:1547), never BuildVariations.
# Same pattern as Flagship's stub-named Redguard modifier.
QM_ANCHOR = '  QuantityModifier = Tank_ChinaInfantryPanzergrenadier   2 ; flagship-emperor: PG squads, two per click'
QM_LINE = (f'  QuantityModifier = Tank_ChinaInfantryTankHunter   2 ; {TAG}: Panzerjaeger pairs '
           '(stub name -- matched at queue time, pre-BuildVariations; ProductionUpdate.cpp)')
QM_HACKER = f'  QuantityModifier = Tank_ChinaInfantryHacker   4 ; {TAG}: hacker cells, four per click (stub name, queue-time match)'
check(bar_new_text.count(QM_ANCHOR + '\n') == 1, 'Barracks PG QuantityModifier anchor missing')
bar_new_text = bar_new_text.replace(QM_ANCHOR + '\n', QM_ANCHOR + '\n' + QM_LINE + '\n' + QM_HACKER + '\n', 1)
audit('Barracks.ini (+3 page-flip modules, +TankHunter x2, +Hacker x4)', bar_src, bar_new_text,
      [], BAR_ADD + [QM_LINE, QM_HACKER])
for need in ['QuantityModifier = Tank_ChinaInfantryPanzergrenadier   2',
             'QuantityModifier = Tank_ChinaInfantryHacker   4',
             'Behavior = ProductionUpdate ModuleTag_10', 'Tank_ChinaBarracksCommandSetUpgrade']:
    check(need in bar_new_text, f'Barracks lost hunk: {need!r}')
bar_new = bar_new_text.encode('latin-1')
print('Barracks.ini: +3 page-flip modules (mines-aware return)')

# ================================================ gattling family (feature 3)
GATT = [(P_GT, 'Tank_ChinaTankGattling', 350.0),
        (P_RP, 'Tank_ChinaReaperTank_Real', 700.0),
        (P_GC, 'Tank_ChinaGattlingCannon', 1250.0)]
gatt_new = {}
for p, obj, hp_expect in GATT:
    src = SRC[p]
    hp = base_hp(src, obj)
    check(hp == hp_expect, f'{obj}: base MaxHealth drifted: {hp} (expected {hp_expect})')
    check('ModuleTag_KD_Armor1' in object_span(src, obj).group(0), f'{obj}: doctrine tiers missing')
    lines = (mhu('ModuleTag_KA_GD2', UP_G2, fmt_hp(hp, GATT_TIER_RATIO),
                 f'Gattling Doctrine II -- +{int(GATT_TIER_RATIO*100)}% of base {int(hp)}')
             + mhu('ModuleTag_KA_GD3', UP_G3, fmt_hp(hp, GATT_TIER_RATIO),
                   f'Gattling Doctrine III -- +{int(GATT_TIER_RATIO*100)}% of base {int(hp)}')
             + [f'  Behavior = ExperienceScalarUpgrade ModuleTag_KA_GDXP ; {TAG}: Gattling Doctrine III -- veteranize 2x (the only data-legal stacking damage path; PLAYER_UPGRADE weapon-bonus bit is consumed by Chain Guns)',
                f'    TriggeredBy = {UP_G3}',
                f'    AddXPScalar = {XP_SCALAR}',
                '  End'])
    new = insert_after_body(src, obj, lines)
    audit(f'{p.split(chr(92))[-1]} (+gattling tiers on {obj})', src, new, [], lines)
    gatt_new[p] = new.encode('latin-1')
print('gattling family: +2 HP tiers (+XP on III) on GattlingTank/Reaper_Real/GattlingCannon')

# ================================================ infantry family (feature 4)
INF = [(P_PG, 'Tank_ChinaInfantryPanzergrenadier', 72.0,  True,  False),
       (P_TH, 'ChinaInfantryTankHunter',           50.0,  True,  False),
       (P_HK, 'ChinaInfantryHacker',               100.0, False, False),
       (P_BL, 'ChinaInfantryBlackLotus',           200.0, False, False),
       (P_SS, 'Tank_ChinaInfantrySharpshooter',    60.0,  True,  True),
       (P_SH, 'Tank_ChinaInfantryShmelTrooper',    50.0,  True,  True),
       (P_ST, 'Tank_ChinaInfantryShockTrooper_Var1', 125.0, True, True)]
inf_new = {}
for p, obj, hp_expect, combat, wp1 in INF:
    src = SRC[p]
    hp = base_hp(src, obj)
    check(hp == hp_expect, f'{obj}: base MaxHealth drifted: {hp} (expected {hp_expect})')
    if wp1:
        check('WeaponBonusUpgrade' not in object_span(src, obj).group(0),
              f'{obj}: PLAYER_UPGRADE weapon-bonus bit unexpectedly taken')
    lines = (mhu('ModuleTag_KA_BA1', UP_BA1, fmt_hp(hp, BA_TIER_RATIO),
                 f'Body Armor I -- +{int(BA_TIER_RATIO*100)}% of base {int(hp)}')
             + mhu('ModuleTag_KA_BA2', UP_BA2, fmt_hp(hp, BA_TIER_RATIO),
                   f'Body Armor II -- +{int(BA_TIER_RATIO*100)}% of base {int(hp)}'))
    if wp1:
        lines += [f'  Behavior = WeaponBonusUpgrade ModuleTag_KA_WP1 ; {TAG}: Weapons Package I -- sets PLAYER_UPGRADE (weapon carries DAMAGE {WP1_DAMAGE} / RANGE {WP1_RANGE} lines)',
                  f'    TriggeredBy = {UP_WP1}',
                  '  End']
    if combat:
        lines += [f'  Behavior = ExperienceScalarUpgrade ModuleTag_KA_WP2XP ; {TAG}: Weapons Package II -- veteranize 2x (second stacked damage tier is data-impossible: single PLAYER_UPGRADE bonus bit)',
                  f'    TriggeredBy = {UP_WP2}',
                  f'    AddXPScalar = {XP_SCALAR}',
                  '  End']
    new = insert_after_body(src, obj, lines)
    audit(f'{p.split(chr(92))[-1]} (+infantry researches on {obj})', src, new, [], lines)
    inf_new[p] = new.encode('latin-1')
print('infantry family: Body Armor tiers x7, WP1 bit x3, WP2 XP x5')

# ================================================ Weapon.ini (WP1 lines)
# FINDING: the rotr weapons ALREADY carry dormant 'WeaponBonus = PLAYER_UPGRADE
# DAMAGE 125% / RANGE 133-145%' lines (rotr-infantry authored them so container
# flags could grant garrison bonuses). No unit-side WeaponBonusUpgrade ever set
# the bit -- our Weapons Package I module IS the missing activator; only the
# Sharpshooter's (shared) rifle needs new lines.
WP1_WEAPONS = ['USAPathfinderSniperRifle', 'RussiaShmellTrooperMissileLauncher',
               'ShockTrooperTeslaWeapon']
WP1_NEW_LINE_WEAPONS = ['USAPathfinderSniperRifle']
wpn_src = SRC[P_WPN]
t = wpn_src
wpn_added = []
for w in WP1_NEW_LINE_WEAPONS:
    m = re.search(r'^Weapon %s\b[^\n]*\n.*?^End[ \t\r]*$' % re.escape(w), t, re.M | re.S)
    check(m, f'weapon block missing: {w}')
    block = m.group(0)
    check('PLAYER_UPGRADE' not in block, f'{w}: already has PLAYER_UPGRADE bonus lines')
    endm = re.search(r'^End[ \t\r]*$', block, re.M)
    add = [f'  WeaponBonus = PLAYER_UPGRADE DAMAGE {WP1_DAMAGE} ; {TAG}: Weapons Package I',
           f'  WeaponBonus = PLAYER_UPGRADE RANGE {WP1_RANGE} ; {TAG}: Weapons Package I']
    block_new = block[:endm.start()] + '\n'.join(add) + '\n' + block[endm.start():]
    t = t[:m.start()] + block_new + t[m.end():]
    wpn_added += add
for w in ['RussiaShmellTrooperMissileLauncher', 'ShockTrooperTeslaWeapon']:
    m = re.search(r'^Weapon %s\b[^\n]*\n.*?^End[ \t\r]*$' % re.escape(w), t, re.M | re.S)
    check(m, f'weapon block missing: {w}')
    check(re.search(r'WeaponBonus\s*=\s*PLAYER_UPGRADE DAMAGE', m.group(0)),
          f'{w}: dormant PLAYER_UPGRADE DAMAGE line missing (rotr idiom drifted)')
# cross-faction leak guard: no OTHER effective object references these weapons
# while carrying a WeaponBonusUpgrade
covered = {'Tank_ChinaInfantrySharpshooter', 'Tank_ChinaInfantryShmelTrooper',
           'Tank_ChinaInfantryShockTrooper_Var1'}
for p, (b, data) in eff0.items():
    if '\\object\\' not in p or not p.endswith('.ini'):
        continue
    txt = data.decode('latin-1')
    for om in re.finditer(r'^Object\s+(\S+)(.*?)^End\s*$', txt, re.M | re.S):
        if om.group(1) in covered:
            continue
        body = om.group(2)
        if any(re.search(r'\b%s\b' % w, body) for w in WP1_WEAPONS):
            check('WeaponBonusUpgrade' not in body,
                  f'WP1 leak: {om.group(1)} ({p}) uses a WP1 weapon AND WeaponBonusUpgrade')
wp1_text = t
audit('Weapon.ini (+WP1 bonus lines)', wpn_src, wp1_text, [], wpn_added)
# Dragon Emperor cannon clones (flagship clone idiom): damage x1.5, range 260
dragon_guns = []
for src_name, new_name in [('Tank_EmperorTankGun', W_DEGUN),
                           ('Tank_EmperorTankGun_Dummy', W_DEGUND)]:
    check(not re.search(r'\b%s\b' % new_name, t), f'{new_name} already exists')
    m = re.search(r'^Weapon %s\b.*?^End' % re.escape(src_name), t, re.M | re.S)
    check(m, f'donor weapon missing: {src_name}')
    blk = m.group(0)
    blk = re.sub(r'^Weapon %s\b' % re.escape(src_name), 'Weapon ' + new_name, blk, count=1)
    def scale_dmg(mm):
        val = float(mm.group(2)) * DRAGON_GUN_MULT
        s = ('%.1f' % val).rstrip('0').rstrip('.')
        if '.' not in s: s += '.0'
        return mm.group(1) + s + f'   ; {TAG}: x{DRAGON_GUN_MULT} (was {mm.group(2)})'
    blk, k = re.subn(r'^(\s*(?:Primary|Secondary)Damage\s*=\s*)([0-9.]+)\b[^\n]*', scale_dmg, blk, flags=re.M)
    check(k >= 1, f'{new_name}: no damage lines scaled')
    blk, r = re.subn(r'^(\s*AttackRange\s*=\s*)240(\.0)?\b[^\n]*',
                     r'\g<1>%s.0   ; %s: dragon long-barrel (was 240)' % (DRAGON_GUN_RANGE, TAG),
                     blk, flags=re.M)
    check(r == 1, f'{new_name}: AttackRange 240 not found exactly once (got {r})')
    dragon_guns.append('\n; ' + '-' * 76 + f'\n; {TAG}: Dragon-Emperor-only clone of {src_name} '
                       f'(damage x{DRAGON_GUN_MULT}, range {DRAGON_GUN_RANGE}).\n' + blk + '\n')
t = wp1_text + ''.join(dragon_guns)
check(t.startswith(wp1_text), 'Weapon.ini gun clones not append-only')
check(''.join(dragon_guns).count('\nWeapon ') == 2, 'dragon gun append balance')
# donors untouched
for src_name in ['Tank_EmperorTankGun', 'Tank_EmperorTankGun_Dummy']:
    check(re.search(r'^Weapon %s\b.*?^End' % re.escape(src_name), t, re.M | re.S).group(0)
          == re.search(r'^Weapon %s\b.*?^End' % re.escape(src_name), wpn_src, re.M | re.S).group(0),
          f'donor weapon {src_name} was modified')
wpn_new_text = t
wpn_new = wpn_new_text.encode('latin-1')
print('Weapon.ini: +2 PLAYER_UPGRADE lines (sniper rifle; rotr weapons already carry '
      'dormant lines, asserted) + 2 Dragon cannon clones appended')

# ================================================ BattleBunker.ini (feature 5)
ib_src = SRC[P_IB]
check('\r\n' in ib_src, 'Infa Bunker.ini expected CRLF line endings')
BB_PATCHES = [
    ('Object Infa_ChinaBunker',
     f'Object {OBJ_BB} ; {TAG}: Kwai battle bunker (clone of Infa_ChinaBunker)'),
    ('  DisplayName      = OBJECT:Infa_Bunker',
     '  DisplayName      = OBJECT:KwaiBattleBunker'),
    ('  Side = ChinaInfantryGeneral',
     '  Side = ChinaTankGeneral'),
    ('    Object = Infa_ChinaBarracks',
     '    Object = Tank_ChinaBarracks'),
    ('  CommandSet       = Infa_ChinaBunkerCommandSet ;Upgrade',
     f'  CommandSet       = {CS_BBM}'),
    ('    CommandSet = Infa_ChinaBunkerCommandSetUpgrade',
     f'    CommandSet = {CS_BBU}'),
]
t = ib_src
for old, new in BB_PATCHES:
    n = t.count(old + '\r\n')
    check(n == 1, f'BattleBunker patch target not unique ({n}): {old[:50]!r}')
    t = t.replace(old + '\r\n', new + '\r\n', 1)
bb_hp = base_hp(t, OBJ_BB)
check(bb_hp == 2200.0, f'Infa bunker base MaxHealth drifted: {bb_hp}')
BB_MODS = (
    [f'  ; {TAG}: Kwai doctrine armor-tier hooks (the Infa original has none)']
    + mhu('ModuleTag_KD_Armor1', 'Tank_Upgrade_KwaiVehicleArmor1', fmt_hp(bb_hp, 0.10), '+10% of base 2200')
    + mhu('ModuleTag_KD_Armor2', 'Tank_Upgrade_KwaiVehicleArmor2', fmt_hp(bb_hp, 0.10), '+10% of base 2200')
    + mhu('ModuleTag_KD_Armor3', 'Tank_Upgrade_KwaiVehicleArmor3', fmt_hp(bb_hp, 0.10), '+10% of base 2200')
    + mhu('ModuleTag_KD_Armor4', 'Tank_Upgrade_KwaiVehicleArmor4', fmt_hp(bb_hp, 0.10), '+10% of base 2200')
    + [f'  ; {TAG}: three per-bunker purchases (kwai-fortress idiom; OBJECT upgrades)']
    + mhu('ModuleTag_KA_BBArmor01', UP_BBARM, fmt_hp(bb_hp, BB_ARMOR_RATIO),
          f'Reinforced Armor -- +{int(BB_ARMOR_RATIO*100)}% of base {int(bb_hp)}')
    + [f'  Behavior = FireWeaponWhenDamagedBehavior ModuleTag_KA_BBPDL01 ; {TAG}: Point-Defense Laser -- reactive anti-missile LASER burst',
       '    StartsActive  = No',
       f'    TriggeredBy   = {UP_BBPDL}',
       '    DamageTypes   = ALL',
       f'    ReactionWeaponPristine      = {W_PDL}',
       f'    ReactionWeaponDamaged       = {W_PDL}',
       f'    ReactionWeaponReallyDamaged = {W_PDL}',
       f'    DamageAmount    = {BB_PDL_TRIGGER}',
       '  End',
       f'  Behavior = AutoHealBehavior ModuleTag_KA_BBAura01 ; {TAG}: Speaker Tower -- heal aura (real tower rider infeasible: one contain per object, GarrisonContain needed; PropagandaTowerBehavior heal rate cannot be OBJECT-gated -- effectLogic reads the PLAYER mask only)',
       '    StartsActive  = No',
       f'    TriggeredBy   = {UP_BBSPK}',
       f'    HealingAmount = {AURA_HEAL}',
       f'    HealingDelay  = {AURA_DELAY} ; msec',
       f'    Radius        = {AURA_RADIUS}',
       '    KindOf        = INFANTRY VEHICLE STRUCTURE',
       '    SkipSelfForHealing = No',
       '  End'])
m = re.search(r'^ {2}Behavior = CommandSetUpgrade ModuleTag_25\b.*?^ {2}End[ \t\r]*$', t, re.M | re.S)
check(m, 'BattleBunker mines CommandSetUpgrade anchor missing')
t = t[:m.end()] + '\n' + '\n'.join(BB_MODS) + t[m.end():]
bb_new_text = t
audit('BattleBunker.ini (clone + tiers + purchases)', ib_src, bb_new_text,
      [o for o, n in BB_PATCHES], [n for o, n in BB_PATCHES] + BB_MODS)
for need in ['Behavior = GarrisonContain ModuleTag_08', 'ContainMax                    = 5',
             'Behavior = ProductionUpdate ModuleTag_10', 'GenerateMinefieldBehavior',
             'BuildCost         = 800']:
    check(need in bb_new_text, f'BattleBunker lost clone hunk: {need!r}')
code_only = '\n'.join(l.split(';', 1)[0] for l in bb_new_text.split('\n'))
check(not re.search(r'\bInfa_', code_only), 'stale Infa_ reference in BattleBunker (non-comment)')
bb_new = bb_new_text.encode('latin-1')
print(f'BattleBunker.ini built ({OBJ_BB}: $800, 2200 HP, 5-man garrison, '
      '4 doctrine tiers + 3 purchases)')

# ================================================ CommandSet.ini
cs_src = SRC[P_CS]
t = cs_src
cs_removed, cs_added = [], []

def edit_set(text, name, remove_lines=(), insert_after=None, insert_lines=()):
    m = get_block(text, 'CommandSet', name, 'CS')
    block = m.group(0)
    for rl in remove_lines:
        check(block.count(rl + '\n') == 1, f'{name}: line not unique: {rl!r}')
        block = block.replace(rl + '\n', '', 1)
        cs_removed.append(rl)
    if insert_after is not None:
        am = re.search(r'^%s$' % re.escape(insert_after), block, re.M)
        check(am, f'{name}: insert anchor missing: {insert_after!r}')
        block = block[:am.end()] + '\n' + '\n'.join(insert_lines) + block[am.end():]
        cs_added.extend(insert_lines)
    return text[:m.start()] + block + text[m.end():]

# feature 1: strip per-tank purchase buttons from the Battlemaster sets
L9  = '  9  = Tank_Command_UpgradeKwaiPDL ; zzz-ZZZZZZZKwaiPDL'
L10 = '  10 = Command_UpgradeChinaOverlordPropagandaTower'
t = edit_set(t, 'Tank_ChinaVehicleBattleMasterCommandSet', remove_lines=[L9, L10])
t = edit_set(t, 'Tank_ChinaVehicleBattleMasterCommandSetPDL', remove_lines=[L9])
t = edit_set(t, 'Tank_ChinaVehicleBattleMasterCommandSetTower', remove_lines=[L10])
# 2nd amendment: exit/evacuate buttons for the new Warmaster/JS-7 fire-out bays
for name, anchor1, nexits in [('Tank_ChinaVehicleWarMasterCommandSet',
                               '  1  = Command_ChinaWarMasterFireRockets', WM_BAY_SLOTS),
                              ('RussianTankGolemCommandSet',
                               '  1  = Command_RussiaGolemTankActivatedShtora', JS7_BAY_SLOTS)]:
    lines = [f'  {i}  = Command_TransportExit ; {TAG}: parity-bay seat' for i in range(2, 2 + nexits)]
    lines.append(f'  {2 + nexits}  = Command_Evacuate ; {TAG}')
    t = edit_set(t, name, insert_after=anchor1, insert_lines=lines)
# feature 2: WF page 2 slot 13 -> page-3 flip (BB research moves to page 3)
WF2 = 'Tank_ChinaWarFactoryCommandSet_Down'
OLD13 = '  13 = Tank_Command_UpgradeExpandedBattleBunkers ; kwai-fortress: Expanded Battle Bunkers (page-1 Evacuate keeps serving the garrison)'
NEW13 = f'  13 = {CB_T3D} ; {TAG}: page down -> WF page 3 (Expanded Battle Bunkers moved there)'
m = get_block(t, 'CommandSet', WF2, 'CS')
check(m.group(0).count(OLD13 + '\n') == 1, 'WF2 slot-13 BB line missing (kwai-fortress 8-file build must be installed)')
t = t[:m.start()] + m.group(0).replace(OLD13 + '\n', NEW13 + '\n', 1) + t[m.end():]
cs_removed.append(OLD13); cs_added.append(NEW13)
# feature 4: barracks page-down on both page-1 variants (slot 11 is free)
BAR_DOWN = f' 11 = Command_ChinaButtonCommandSetOneDown ; {TAG}: page down -> infantry researches'
for name in ['Tank_ChinaBarracksCommandSet', 'Tank_ChinaBarracksCommandSetUpgrade']:
    t = edit_set(t, name,
                 insert_after='  10 = Tank_Command_ConstructChinaInfantryShockTrooper ; rotr-infantry',
                 insert_lines=[BAR_DOWN])
# feature 5: dozer page 2 slot 10 construct button
t = edit_set(t, 'Tank_ChinaDozerCommandSet_Down',
             insert_after='  9  = Tank_Command_ConstructChinaTeslaCoil ; zzz-ZZZZZZZTTeslaCoil',
             insert_lines=[f'  10 = {CB_BBBLD} ; {TAG}'])
# appended sets
CS_APPEND_LINES = [
    f';;; {TAG}: War Factory page 3 (fleet researches + gattling doctrine + battle bunkers)',
    f'CommandSet {CS_WF3}',
    f'  1  = {CB_FTOWER}',
    f'  2  = {CB_FPDL}',
    f'  3  = {CB_BAYS}',
    '  4  = Tank_Command_UpgradeExpandedBattleBunkers',
    f'  5  = {CB_G2}',
    f'  6  = {CB_G3}',
    f'  7  = {CB_VA5}',
    f'  8  = {CB_DEBLD}',
    f' 12 = {CB_T3U}',
    ' 13 = Command_Evacuate',
    ' 14 = Command_Sell',
    'End',
    '',
    f';;; {TAG}: Barracks page 2 (infantry researches)',
    f'CommandSet {CS_BAR2}',
    f'  1  = {CB_BA1}',
    f'  2  = {CB_BA2}',
    f'  3  = {CB_WP1}',
    f'  4  = {CB_WP2}',
    f'  5  = {CB_IA5}',
    ' 11 = Command_ChinaButtonCommandSetOneUp',
    ' 14 = Command_Sell',
    'End',
    '',
    f';;; {TAG}: Battle Bunker command bars (per-bunker purchases at 7-9)',
    f'CommandSet {CS_BBM}',
    '  1  = Command_BunkerExit',
    '  2  = Command_BunkerExit',
    '  3  = Command_BunkerExit',
    '  4  = Command_BunkerExit',
    '  5  = Command_BunkerExit',
    '  6  = Command_Evacuate',
    f'  7  = {CB_BBARM}',
    f'  8  = {CB_BBPDL}',
    f'  9  = {CB_BBSPK}',
    ' 12 = Command_Stop',
    ' 13 = Command_UpgradeChinaMines',
    ' 14 = Command_Sell',
    'End',
    '',
    f'CommandSet {CS_BBU}',
    '  1  = Command_BunkerExit',
    '  2  = Command_BunkerExit',
    '  3  = Command_BunkerExit',
    '  4  = Command_BunkerExit',
    '  5  = Command_BunkerExit',
    '  6  = Command_Evacuate',
    f'  7  = {CB_BBARM}',
    f'  8  = {CB_BBPDL}',
    f'  9  = {CB_BBSPK}',
    ' 12 = Command_Stop',
    ' 13 = Command_UpgradeEMPMines',
    ' 14 = Command_Sell',
    'End',
]
check(t.endswith('\n'), 'CommandSet.ini must end with newline')
t = t + '\n' + '\n'.join(CS_APPEND_LINES) + '\n'
cs_new_text = t
audit('CommandSet.ini (arsenal surgery)', cs_src, cs_new_text,
      cs_removed, cs_added + CS_APPEND_LINES + [''])
# post-edit layouts
def slots_of(name):
    return dict(re.findall(r'^\s*(\d+)\s*=\s*(\S+)',
                get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), re.M))
for name in ['Tank_ChinaVehicleBattleMasterCommandSet', 'Tank_ChinaVehicleBattleMasterCommandSetERA',
             'Tank_ChinaVehicleBattleMasterCommandSetPDL', 'Tank_ChinaVehicleBattleMasterCommandSetTower']:
    sl = slots_of(name)
    check(sl == {'1': 'Command_TransportExit', '2': 'Command_TransportExit', '3': 'Command_TransportExit',
                 '4': 'Command_TransportExit', '5': 'Command_Evacuate',
                 '6': 'Tank_Command_UpgradeBattleMasterReactiveArmor',
                 '7': 'Tank_Command_UpgradeBattleMasterHull', '8': 'Tank_Command_UpgradeBattleMasterShield',
                 '11': 'Command_AttackMove', '13': 'Command_Guard', '14': 'Command_Stop'},
          f'{name} post-edit layout wrong: {sl}')
sl = slots_of(WF2)
check(sl['13'] == CB_T3D and sl['8'] == 'Tank_Command_UpgradeEmperorPDL'
      and sl['12'] == 'Command_ChinaButtonCommandSetOneUp', f'{WF2} layout wrong: {sl}')
check(slots_of(CS_WF3) == {'1': CB_FTOWER, '2': CB_FPDL, '3': CB_BAYS,
                           '4': 'Tank_Command_UpgradeExpandedBattleBunkers', '5': CB_G2, '6': CB_G3,
                           '7': CB_VA5, '8': CB_DEBLD,
                           '12': CB_T3U, '13': 'Command_Evacuate', '14': 'Command_Sell'},
      'WF page 3 layout wrong')
sl = slots_of('Tank_ChinaVehicleWarMasterCommandSet')
check(sl == {'1': 'Command_ChinaWarMasterFireRockets', '2': 'Command_TransportExit',
             '3': 'Command_TransportExit', '4': 'Command_TransportExit', '5': 'Command_TransportExit',
             '6': 'Command_Evacuate', '9': 'Tank_Command_UpgradeKwaiPDL', '11': 'Command_AttackMove',
             '13': 'Command_Guard', '14': 'Command_Stop'}, f'WarMaster set layout wrong: {sl}')
sl = slots_of('RussianTankGolemCommandSet')
check(sl == {'1': 'Command_RussiaGolemTankActivatedShtora', '2': 'Command_TransportExit',
             '3': 'Command_TransportExit', '4': 'Command_TransportExit', '5': 'Command_TransportExit',
             '6': 'Command_TransportExit', '7': 'Command_TransportExit', '8': 'Command_Evacuate',
             '9': 'Tank_Command_UpgradeKwaiPDL', '11': 'Command_AttackMove',
             '13': 'Command_Guard', '14': 'Command_Stop'}, f'JS-7 (Golem) set layout wrong: {sl}')
for name, thirteen in [('Tank_ChinaBarracksCommandSet', 'Command_UpgradeChinaMines'),
                       ('Tank_ChinaBarracksCommandSetUpgrade', 'Command_UpgradeEMPMines')]:
    sl = slots_of(name)
    check(sl['11'] == 'Command_ChinaButtonCommandSetOneDown' and sl['13'] == thirteen
          and sl['1'] == 'Tank_Command_ConstructChinaInfantryPanzergrenadier'
          and sl['10'] == 'Tank_Command_ConstructChinaInfantryShockTrooper',
          f'{name} layout wrong: {sl}')
check(slots_of(CS_BAR2) == {'1': CB_BA1, '2': CB_BA2, '3': CB_WP1, '4': CB_WP2, '5': CB_IA5,
                            '11': 'Command_ChinaButtonCommandSetOneUp', '14': 'Command_Sell'},
      'Barracks page 2 layout wrong')
sl = slots_of('Tank_ChinaDozerCommandSet_Down')
check(sl == {'1': 'Tank_Command_ConstructChinaIndustrialPlant', '7': 'Tank_Command_ConstructChinaBunker',
             '8': 'Tank_Command_ConstructChinaFortressBunker', '9': 'Tank_Command_ConstructChinaTeslaCoil',
             '10': CB_BBBLD, '13': 'Command_ChinaButtonCommandSetOneUp',
             '14': 'Command_DisarmMinesAtPosition'}, f'dozer page 2 layout wrong: {sl}')
for name, thirteen in [(CS_BBM, 'Command_UpgradeChinaMines'), (CS_BBU, 'Command_UpgradeEMPMines')]:
    sl = slots_of(name)
    check(sl['7'] == CB_BBARM and sl['8'] == CB_BBPDL and sl['9'] == CB_BBSPK
          and sl['13'] == thirteen, f'{name} layout wrong: {sl}')
# sibling survival
for name, need in [('Tank_ChinaFortressBunkerCommandSet', 'Tank_Command_UpgradeFortressCompositeArmor'),
                   ('Tank_ChinaPropagandaCenterCommandSet', 'Tank_Command_UpgradeSatelliteUplink'),
                   ('Tank_ChinaWarFactoryCommandSet', 'Tank_Command_ConstructChinaTankEmperor'),
                   ('Infa_ChinaBunkerCommandSet', 'Command_BunkerExit')]:
    check(need in get_block(cs_new_text, 'CommandSet', name, 'CS').group(1),
          f'survival: {name} lost {need}')
cs_new = cs_new_text.encode('latin-1')
print('CommandSet.ini patched (BM strip, WF2 slot13, +WF3/Barracks2/BattleBunker sets, '
      'barracks slot 11, dozer slot 10)')

# ================================================ CommandButton.ini (append)
def upg_button(name, upgrade, base, cameo, command='PLAYER_UPGRADE', opts='OK_FOR_MULTI_SELECT'):
    return '\n'.join([
        f'CommandButton {name}', f'  Command       = {command}',
        f'  Upgrade       = {upgrade}', f'  Options       = {opts}',
        f'  TextLabel     = CONTROLBAR:Upgrade{base}', f'  ButtonImage   = {cameo}',
        '  ButtonBorderType        = UPGRADE',
        f'  DescriptLabel           = CONTROLBAR:ToolTipUpgrade{base}',
        f'  PurchasedLabel          = CONTROLBAR:ToolTipUpgrade{base}',
        '  UnitSpecificSound = MoneyWithdraw', 'End'])
def flip_button(name, upgrade, textlabel, cameo):
    return '\n'.join([
        f'CommandButton {name} ; {TAG}: WF page-3 flip (GLA-worker arrow idiom, own token)',
        '  Command       = OBJECT_UPGRADE', f'  Upgrade       = {upgrade}',
        f'  TextLabel     = {textlabel}', f'  ButtonImage   = {cameo}',
        '  ButtonBorderType        = UPGRADE', '  DescriptLabel           = Nada', 'End'])
CB_APPEND = ('\n; ' + '-' * 76 + f'\n; {TAG}: fleet/gattling/infantry researches, WF page-3 flips, battle bunker.\n' +
    '\n\n'.join([
        upg_button(CB_FTOWER, UP_FTOWER, 'FleetSpeakerTowers', CAM['tower']),
        upg_button(CB_FPDL, UP_FPDL, 'FleetPointDefense', CAM['pdl']),
        upg_button(CB_BAYS, UP_BAYS, 'ExpandedCrewBays', CAM['bays']),
        upg_button(CB_G2, UP_G2, 'GattlingDoctrineII', CAM['gatt']),
        upg_button(CB_G3, UP_G3, 'GattlingDoctrineIII', CAM['gatt']),
        upg_button(CB_BA1, UP_BA1, 'KwaiBodyArmorI', CAM['ba']),
        upg_button(CB_BA2, UP_BA2, 'KwaiBodyArmorII', CAM['ba']),
        upg_button(CB_WP1, UP_WP1, 'KwaiWeaponsPackageI', CAM['wp']),
        upg_button(CB_WP2, UP_WP2, 'KwaiWeaponsPackageII', CAM['wp']),
        flip_button(CB_T3D, UP_T3D, 'CONTROLBAR:OneDown', CAM['down']),
        flip_button(CB_T3U, UP_T3U, 'CONTROLBAR:OneUp', CAM['up']),
        '\n'.join([f'CommandButton {CB_BBBLD}', '  Command       = DOZER_CONSTRUCT',
                   '  UnitSpecificSound = MoneyWithdraw', f'  Object        = {OBJ_BB}',
                   '  TextLabel     = CONTROLBAR:ConstructChinaBattleBunker',
                   f'  ButtonImage   = {CAM["bb"]}', '  ButtonBorderType        = BUILD',
                   '  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildBattleBunker', 'End']),
        upg_button(CB_BBARM, UP_BBARM, 'BattleBunkerArmor', CAM['bbarm'],
                   command='OBJECT_UPGRADE', opts='OK_FOR_MULTI_SELECT NOT_QUEUEABLE'),
        upg_button(CB_BBPDL, UP_BBPDL, 'BattleBunkerPDL', CAM['pdl'],
                   command='OBJECT_UPGRADE', opts='OK_FOR_MULTI_SELECT NOT_QUEUEABLE'),
        upg_button(CB_BBSPK, UP_BBSPK, 'BattleBunkerSpeaker', CAM['tower'],
                   command='OBJECT_UPGRADE', opts='OK_FOR_MULTI_SELECT NOT_QUEUEABLE'),
        upg_button(CB_VA5, UP_VA5, 'KwaiVehicleArmor5', CAM['va5']),
        upg_button(CB_IA5, UP_IA5, 'KwaiInfantryArmor5', CAM['ia5']),
        '\n'.join([f'CommandButton {CB_DEBLD} ; {TAG}: Dragon Emperor super-heavy (WF page 3)',
                   '  Command       = UNIT_BUILD',
                   '  UnitSpecificSound = MoneyWithdraw', f'  Object        = {OBJ_DE}',
                   '  TextLabel     = CONTROLBAR:ConstructChinaDragonEmperor',
                   f'  ButtonImage   = {CAM["dragon"]}', '  ButtonBorderType        = BUILD',
                   '  DescriptLabel           = CONTROLBAR:ToolTipChinaBuildDragonEmperor', 'End']),
    ]) + '\n')
cb_src_b = SRC[P_CB].encode('latin-1')
check(cb_src_b.endswith(b'\n'), 'CommandButton.ini must end with newline')
cb_new = cb_src_b + CB_APPEND.encode('latin-1')
check(cb_new.startswith(cb_src_b), 'CommandButton.ini not append-only')
check(CB_APPEND.count('\nCommandButton ') == 18, 'CB append balance')
print('CommandButton.ini: +18 buttons appended (11 researches, 2 flips, 2 constructs, 3 purchases)')

# ================================================ Upgrade.ini (append)
def upg(name, base, typ, cost, time, cameo, snd, req=None, note=''):
    out = [f'Upgrade {name}' + (f' ; {TAG}: {note}' if note else ''),
           f'  DisplayName        = UPGRADE:{base}', f'  Type               = {typ}',
           f'  BuildTime          = {time}', f'  BuildCost          = {cost}',
           f'  ButtonImage        = {cameo}', f'  ResearchSound      = {snd}']
    if req:
        out.append(f'  RequiredUpgrade    = {req} ; {TAG}: tier prereq')
    out.append('End')
    return '\n'.join(out)
def token(name, note):
    return '\n'.join([f'Upgrade {name} ; {TAG}: {note}', '  Type               = OBJECT',
                      '  BuildTime          = 0.0', '  BuildCost          = 0',
                      f'  ButtonImage        = {CAM["down"]}', 'End'])
UPG_APPEND = ('\n; ' + '-' * 76 + f'\n; {TAG}: fleet/gattling/infantry researches + WF page tokens + bunker purchases.\n' +
    '\n\n'.join([
        upg(UP_FTOWER, 'FleetSpeakerTowers', 'PLAYER', COST_FLEET_TOWER, TIME_FLEET_TOWER, CAM['tower'], SND_RESEARCH),
        upg(UP_FPDL, 'FleetPointDefense', 'PLAYER', COST_FLEET_PDL, TIME_FLEET_PDL, CAM['pdl'], SND_RESEARCH),
        upg(UP_BAYS, 'ExpandedCrewBays', 'PLAYER', COST_CREW_BAYS, TIME_CREW_BAYS, CAM['bays'], SND_RESEARCH),
        upg(UP_G2, 'GattlingDoctrineII', 'PLAYER', COST_GATT2, TIME_GATT2, CAM['gatt'], SND_RESEARCH),
        upg(UP_G3, 'GattlingDoctrineIII', 'PLAYER', COST_GATT3, TIME_GATT3, CAM['gatt'], SND_RESEARCH, req=UP_G2),
        upg(UP_BA1, 'KwaiBodyArmorI', 'PLAYER', COST_BA1, TIME_BA1, CAM['ba'], SND_RESEARCH),
        upg(UP_BA2, 'KwaiBodyArmorII', 'PLAYER', COST_BA2, TIME_BA2, CAM['ba'], SND_RESEARCH, req=UP_BA1),
        upg(UP_WP1, 'KwaiWeaponsPackageI', 'PLAYER', COST_WP1, TIME_WP1, CAM['wp'], SND_RESEARCH),
        upg(UP_WP2, 'KwaiWeaponsPackageII', 'PLAYER', COST_WP2, TIME_WP2, CAM['wp'], SND_RESEARCH, req=UP_WP1),
        token(UP_T3D, 'WF page-3 down token ($0 instant, GLA-worker idiom)'),
        token(UP_T3U, 'WF page-3 up token ($0 instant, GLA-worker idiom)'),
        upg(UP_BBARM, 'BattleBunkerArmor', 'OBJECT', COST_BB_ARMOR, 10.0, CAM['bbarm'], SND_OBJECT),
        upg(UP_BBPDL, 'BattleBunkerPDL', 'OBJECT', COST_BB_PDL, 10.0, CAM['pdl'], SND_OBJECT),
        upg(UP_BBSPK, 'BattleBunkerSpeaker', 'OBJECT', COST_BB_SPEAKER, 10.0, CAM['tower'], SND_OBJECT),
        upg(UP_VA5, 'KwaiVehicleArmor5', 'PLAYER', COST_VA5, TIME_VA5, CAM['va5'], SND_RESEARCH,
            req='Tank_Upgrade_KwaiVehicleArmor4',
            note='Composite Armor V -- standalone tier (the 50-set doctrine ladder is not extended)'),
        upg(UP_IA5, 'KwaiInfantryArmor5', 'PLAYER', COST_IA5, TIME_IA5, CAM['ia5'], SND_RESEARCH,
            req='Tank_Upgrade_KwaiInfantryArmor4',
            note='Infantry Conditioning V -- standalone tier (ditto)'),
    ]) + '\n')
upg_src_b = SRC[P_UPG].encode('latin-1')
check(upg_src_b.endswith(b'\n'), 'Upgrade.ini must end with newline')
upg_new = upg_src_b + UPG_APPEND.encode('latin-1')
check(upg_new.startswith(upg_src_b), 'Upgrade.ini not append-only')
check(UPG_APPEND.count('\nUpgrade ') == 16
      and UPG_APPEND.count('Type               = PLAYER') == 11
      and UPG_APPEND.count('Type               = OBJECT') == 5
      and UPG_APPEND.count('RequiredUpgrade') == 5, 'Upgrade append balance')
# tier-IV prereqs must exist in the effective upgrade space
for req in ['Tank_Upgrade_KwaiVehicleArmor4', 'Tank_Upgrade_KwaiInfantryArmor4']:
    check(re.search(r'^Upgrade\s+%s\b' % req, SRC[P_UPG], re.M), f'tier-IV prereq {req} missing')
print('Upgrade.ini: +16 upgrades appended (11 PLAYER, 2 tokens, 3 OBJECT; 5 tier chains)')

# ================================================ Generals.str (append)
def s(label, val):
    return f'{label}\n"{val}"\nEND\n'
STR_ITEMS = [
    ('OBJECT:KwaiBattleBunker', 'Battle Bunker'),
    ('CONTROLBAR:ConstructChinaBattleBunker', '&Battle Bunker'),
    ('CONTROLBAR:ToolTipChinaBuildBattleBunker',
     'Fortified bunker garrisoning up to five infantry, who fire out.\\n'
     ' Can be individually fitted with Reinforced Armor, a Point-Defense Laser\\n'
     ' and a Speaker Tower.'),
    ('UPGRADE:FleetSpeakerTowers', 'Fleet Speaker Towers'),
    ('CONTROLBAR:UpgradeFleetSpeakerTowers', 'Fleet &Speaker Towers'),
    ('CONTROLBAR:ToolTipUpgradeFleetSpeakerTowers',
     'Mounts a propaganda speaker tower on every Battlemaster, current and\\n'
     ' future: heals and inspires nearby friendly forces.'),
    ('UPGRADE:FleetPointDefense', 'Fleet Point-Defense'),
    ('CONTROLBAR:UpgradeFleetPointDefense', 'Fleet &Point-Defense'),
    ('CONTROLBAR:ToolTipUpgradeFleetPointDefense',
     'Fits every Battlemaster with a reactive point-defense laser: when\\n'
     ' struck, it pulses an anti-missile LASER burst that destroys incoming\\n'
     ' rockets and missiles.'),
    ('UPGRADE:ExpandedCrewBays', 'Expanded Crew Bays'),
    ('CONTROLBAR:UpgradeExpandedCrewBays', 'Expanded &Crew Bays'),
    ('CONTROLBAR:ToolTipUpgradeExpandedCrewBays',
     'Enlarges every Battlemaster bunker bay from 4 to 8 soldiers.'),
    ('UPGRADE:GattlingDoctrineII', 'Gattling Doctrine II'),
    ('CONTROLBAR:UpgradeGattlingDoctrineII', 'Gattling Doctrine &II'),
    ('CONTROLBAR:ToolTipUpgradeGattlingDoctrineII',
     'Hardens the gattling arsenal: Gattling Tanks, Reapers and Gattling\\n'
     ' Cannons gain 25% more hit points.'),
    ('UPGRADE:GattlingDoctrineIII', 'Gattling Doctrine III'),
    ('CONTROLBAR:UpgradeGattlingDoctrineIII', 'Gattling Doctrine I&II'),
    ('CONTROLBAR:ToolTipUpgradeGattlingDoctrineIII',
     'Requires Gattling Doctrine II. Another 25% hit points for the gattling\\n'
     ' arsenal, and its crews earn veterancy twice as fast.'),
    ('UPGRADE:KwaiBodyArmorI', 'Body Armor I'),
    ('CONTROLBAR:UpgradeKwaiBodyArmorI', 'Body &Armor I'),
    ('CONTROLBAR:ToolTipUpgradeKwaiBodyArmorI',
     'Issues composite body armor to Kwai\'s infantry: +20% hit points.'),
    ('UPGRADE:KwaiBodyArmorII', 'Body Armor II'),
    ('CONTROLBAR:UpgradeKwaiBodyArmorII', 'Body Armor &II'),
    ('CONTROLBAR:ToolTipUpgradeKwaiBodyArmorII',
     'Requires Body Armor I. Another +20% hit points for Kwai\'s infantry.'),
    ('UPGRADE:KwaiWeaponsPackageI', 'Weapons Package I'),
    ('CONTROLBAR:UpgradeKwaiWeaponsPackageI', '&Weapons Package I'),
    ('CONTROLBAR:ToolTipUpgradeKwaiWeaponsPackageI',
     'Upgunned small arms for Sharpshooters, Shmel and Shock Troopers:\\n'
     ' 20-25% more damage and extended range.'),
    ('UPGRADE:KwaiWeaponsPackageII', 'Weapons Package II'),
    ('CONTROLBAR:UpgradeKwaiWeaponsPackageII', 'Weapons Package &II'),
    ('CONTROLBAR:ToolTipUpgradeKwaiWeaponsPackageII',
     'Requires Weapons Package I. Advanced munitions training: combat\\n'
     ' infantry earn veterancy twice as fast.'),
    ('UPGRADE:BattleBunkerArmor', 'Reinforced Armor'),
    ('CONTROLBAR:UpgradeBattleBunkerArmor', '&Reinforced Armor'),
    ('CONTROLBAR:ToolTipUpgradeBattleBunkerArmor',
     'Reinforce this bunker: permanently adds 50% more hit points (and heals\\n'
     ' it by the added amount).'),
    ('UPGRADE:BattleBunkerPDL', 'Point-Defense Laser'),
    ('CONTROLBAR:UpgradeBattleBunkerPDL', '&Point-Defense Laser'),
    ('CONTROLBAR:ToolTipUpgradeBattleBunkerPDL',
     'Fit this bunker with a point-defense laser: when struck, it pulses an\\n'
     ' anti-missile LASER burst that destroys incoming rockets and missiles.'),
    ('UPGRADE:BattleBunkerSpeaker', 'Speaker Tower'),
    ('CONTROLBAR:UpgradeBattleBunkerSpeaker', '&Speaker Tower'),
    ('CONTROLBAR:ToolTipUpgradeBattleBunkerSpeaker',
     'Mount propaganda speakers on this bunker: a healing aura that\\n'
     ' continuously repairs nearby friendly troops, vehicles and structures\\n'
     ' (including the bunker itself).'),
    ('UPGRADE:KwaiVehicleArmor5', 'Composite Armor V'),
    ('CONTROLBAR:UpgradeKwaiVehicleArmor5', 'Composite Armor &V'),
    ('CONTROLBAR:ToolTipUpgradeKwaiVehicleArmor5',
     'Requires Composite Armor IV. A fifth armor tier: every vehicle and\\n'
     ' structure the doctrine covers gains another 10% of its base hit points.'),
    ('UPGRADE:KwaiInfantryArmor5', 'Infantry Conditioning V'),
    ('CONTROLBAR:UpgradeKwaiInfantryArmor5', 'Infantry Conditioning &V'),
    ('CONTROLBAR:ToolTipUpgradeKwaiInfantryArmor5',
     'Requires Infantry Conditioning IV. A fifth conditioning tier: covered\\n'
     ' infantry gain another 10% of their base hit points.'),
    ('OBJECT:DragonEmperor', 'Dragon Emperor'),
    ('CONTROLBAR:ConstructChinaDragonEmperor', '&Dragon Emperor'),
    ('CONTROLBAR:ToolTipChinaBuildDragonEmperor',
     'The Dragon Emperor super-heavy: a doubled-hull Emperor with x1.5\\n'
     ' long-barrel cannons and a 12-man bunker bay. Limited to 3 in the field.'),
]
STR_APPEND = '\n' + '\n'.join(s(a, b) for a, b in STR_ITEMS)
str_src_b = SRC[P_STR].encode('latin-1')
check(str_src_b.endswith(b'\n'), 'Generals.str must end with newline')
str_new = str_src_b + STR_APPEND.encode('latin-1')
check(str_new.startswith(str_src_b), 'Generals.str not append-only')
check(len(STR_ITEMS) == 48, f'expected 48 str entries, got {len(STR_ITEMS)}')
check(str_new.decode('latin-1').count('\nEND\n') == str_src_b.decode('latin-1').count('\nEND\n') + 48,
      'str append entry count (want +48)')
print('Generals.str: +48 entries appended')

# ================================================ doctrine tier V (dynamic pass)
# Exact tier-IV coverage parity: EVERY effective object carrying a tier-IV
# MaxHealthUpgrade gets a tier-V clone of that module (same AddMaxHealth --
# tier IV adds exactly 10% of base, so tier V does too), triggered by the new
# standalone research. Files not already shipped are pulled in as full copies.
shipped_texts = {P_BM: bm_new_text, P_WF: wf_new_text, P_BAR: bar_new_text,
                 P_BB: bb_new_text, P_WPN: wpn_new_text, P_WM: hv_new[P_WM].decode('latin-1'),
                 P_JS: hv_new[P_JS].decode('latin-1'), P_OV: ov_new_text,
                 P_EMP: emp_src, P_DE: de_new_text}
for p in gatt_new:  shipped_texts[p] = gatt_new[p].decode('latin-1')
for p in inf_new:   shipped_texts[p] = inf_new[p].decode('latin-1')

TIER4 = [('Tank_Upgrade_KwaiVehicleArmor4', UP_VA5, 'ModuleTag_KA_VA5'),
         ('Tank_Upgrade_KwaiInfantryArmor4', UP_IA5, 'ModuleTag_KA_IA5')]
MHU_RX = re.compile(r'^ {2}Behavior = MaxHealthUpgrade \S+[^\n]*\n.*?^ {2}End[ \t\r]*$', re.M | re.S)

def tier5_pass(text, label):
    """Clone every tier-IV MaxHealthUpgrade block as a tier-V module."""
    added = []
    out, last = [], 0
    for m in MHU_RX.finditer(text):
        blk = m.group(0)
        hit = None
        for trig4, up5, tag5 in TIER4:
            if re.search(r'TriggeredBy\s*=\s*%s\b' % trig4, blk):
                hit = (trig4, up5, tag5); break
        out.append(text[last:m.end()]); last = m.end()
        if hit:
            trig4, up5, tag5 = hit
            v = re.search(r'AddMaxHealth\s*=\s*([\d.]+)', blk)
            check(v, f'{label}: tier-IV module without AddMaxHealth')
            clone = [f'  Behavior = MaxHealthUpgrade {tag5} ; {TAG}: tier V -- same magnitude as tier IV',
                     f'    TriggeredBy   = {up5}',
                     f'    AddMaxHealth  = {v.group(1)}',
                     '    ChangeType    = ADD_CURRENT_HEALTH_TOO',
                     '  End']
            out.append('\n' + '\n'.join(clone))
            added += clone
    out.append(text[last:])
    return ''.join(out), added

# canonical (display-case) path map, from the highest-priority source of each
canon_map = {}
for b in sorted_bigs(MODDIRS[0]):
    if b.lower() >= ARCHIVE.lower():
        continue
    for e in bigfile.read_big(os.path.join(MODDIRS[0], b)):
        canon_map[e.path.lower()] = e.path
# archives above us (for the dynamic-file claim guard)
above_claims = set()
for d in MODDIRS:
    for b in sorted_bigs(d):
        if b.lower() > ARCHIVE.lower():
            above_claims |= {e.path.lower() for e in bigfile.read_big(os.path.join(d, b))}

tier5_files = 0; tier5_mods = 0
tier5_dynamic = []
for p_low, (owner, data) in sorted(eff0.items()):
    if not p_low.endswith('.ini') or '\\object\\' not in p_low:
        continue
    txt = data.decode('latin-1')
    if not any(re.search(r'TriggeredBy\s*=\s*%s\b' % t4, txt) for t4, _, _ in TIER4):
        continue
    canon = next((p for p in shipped_texts if p.lower() == p_low), None)
    base_text = shipped_texts[canon] if canon else txt
    if canon is None:
        check(p_low not in above_claims, f'an archive above us claims tier-V file {p_low}')
        canon = canon_map[p_low]
        tier5_dynamic.append(canon)
    new_text, added = tier5_pass(base_text, canon)
    check(added, f'{canon}: tier-IV trigger found but no module cloned')
    audit(f'tier-V: {canon.split(chr(92))[-1]}', base_text, new_text, [], added)
    shipped_texts[canon] = new_text
    tier5_files += 1; tier5_mods += len(added) // 5
# ============================================ Panzerjaeger clone (post-passes)
# Kwai-scoped concrete clone of the vanilla ChinaInfantryTankHunter so a
# HordeUpdate can be added without touching the shared unit. Built from OUR
# fully-patched vanilla text (so it inherits doctrine tiers, InfantryDoctrine
# hook, Body Armor I/II, WP2 XP -- and tier V via the pass below). The Kwai
# stub's BuildVariations is repointed; every external reference (construct
# button, QuantityModifier, command sets) keeps the STUB name.
th_text = shipped_texts[P_TH]
om = object_span(th_text, 'ChinaInfantryTankHunter')
pj = om.group(0)
n_beh_src = len(re.findall(r'^\s*Behavior\s*=', pj, re.M))
pj = re.sub(r'^Object ChinaInfantryTankHunter\b',
            f'Object {OBJ_PJ} ; {TAG}: Kwai Panzerjaeger (clone of ChinaInfantryTankHunter + horde discipline)',
            pj, count=1)
check(pj.count('  DisplayName      = OBJECT:TankHunter') == 1, 'clone DisplayName anchor')
pj = pj.replace('  DisplayName      = OBJECT:TankHunter',
                f'  DisplayName      = OBJECT:TankPanzerjager ; {TAG}: selected units read Panzerjaeger', 1)
sm = re.search(r'^ {2}Side\s*=\s*China[ \t\r]*$', pj, re.M)
check(sm, 'clone Side anchor')
pj = pj[:sm.start()] + f'  Side = ChinaTankGeneral ; {TAG}: Kwai-scoped (was China)' + pj[sm.end():]
PJ_HORDE = [f'  Behavior = HordeUpdate ModuleTag_KA_Horde01 ; {TAG}: Panzerjaeger horde discipline (Panzergrenadier config)',
            '    RubOffRadius = 60',
            '    UpdateRate = 1000',
            '    Radius = 30',
            '    KindOf = INFANTRY',
            '    AlliesOnly = Yes',
            '    ExactMatch = No',
            '    Count = 5',
            '    Action = HORDE',
            '  End']
bm2 = re.search(r'^ {2}Body\s*=.*?^ {2}End[ \t\r]*$', pj, re.M | re.S)
check(bm2, 'clone Body block missing')
pj = pj[:bm2.end()] + '\n' + '\n'.join(PJ_HORDE) + pj[bm2.end():]
check(len(re.findall(r'^\s*Behavior\s*=', pj, re.M)) == n_beh_src + 1,
      'clone module census != source + 1 (HordeUpdate)')
# label exists since the panzergrenadier layer (drift guard)
check(re.search(r'^OBJECT:TankPanzerjager\s*$',
                eff0[P_STR.lower()][1].decode('latin-1'), re.M),
      'OBJECT:TankPanzerjager label missing from effective str')
pj_file = (f'; {TAG}: Kwai Panzerjaeger -- concrete clone of the effective vanilla\n'
           f'; ChinaInfantryTankHunter (incl. all arsenal/doctrine hooks) + HordeUpdate.\n'
           f'; The Kwai stub Tank_ChinaInfantryTankHunter BuildVariations-resolves here.\n\n'
           + pj + '\n')
shipped_texts[P_PJ] = pj_file
print(f'Panzerjager.ini built ({OBJ_PJ}: clone census {n_beh_src}+1 modules, horde discipline)')
# stub repoint
ths_src = SRC[P_THS]
OLD_BV = '  BuildVariations = ChinaInfantryTankHunter'
NEW_BV = f'  BuildVariations = {OBJ_PJ} ; {TAG}: was ChinaInfantryTankHunter (shared vanilla unit untouched)'
check(ths_src.count(OLD_BV + '\r\n') == 1, 'stub BuildVariations line drifted')
ths_new_text = ths_src.replace(OLD_BV + '\r\n', NEW_BV + '\r\n', 1)
audit('TankHunter.ini stub (BuildVariations repoint)', ths_src, ths_new_text, [OLD_BV], [NEW_BV])
for need in ['Scale = 0.95', 'DisplayName            = OBJECT:TankPanzerjager',
             'Side = ChinaTankGeneral', 'BuildCost             = 320']:
    check(need in ths_new_text, f'stub lost override hunk: {need!r}')
shipped_texts[P_THS] = ths_new_text
print('TankHunter.ini stub: BuildVariations -> Panzerjaeger clone (art/scale/name overrides kept)')

# the NEW objects (BattleBunker, Dragon, Panzerjaeger) are not in eff0 -- pass them too
for p in [P_BB, P_DE]:
    new_text, added = tier5_pass(shipped_texts[p], p)
    check(added, f'{p}: expected tier-V coverage on the new object')
    audit(f'tier-V: {p.split(chr(92))[-1]}', shipped_texts[p], new_text, [], added)
    shipped_texts[p] = new_text
    tier5_files += 1; tier5_mods += len(added) // 5
print(f'doctrine tier V: {tier5_mods} modules cloned across {tier5_files} files '
      f'({len(tier5_dynamic)} pulled in dynamically: '
      + ', '.join(sorted(p.split(chr(92))[-1] for p in tier5_dynamic)) + ')')
check(tier5_mods >= 40, f'tier-V coverage suspiciously small: {tier5_mods}')
# both new bunkers + the Dragon carry doctrine tiers -> tier V must cover them
for p in [P_BB, P_DE, P_BM, P_EMP]:
    check('ModuleTag_KA_VA5' in shipped_texts[p], f'{p}: tier-V module missing')

# ================================================ global closure
cb_f = cb_new.decode('latin-1'); upg_f = upg_new.decode('latin-1')
str_f = str_new.decode('latin-1')
# every research button -> upgrade -> at least one module wired to it
CHAINS = [(CB_FTOWER, UP_FTOWER, 'PLAYER', [P_BM]),
          (CB_FPDL, UP_FPDL, 'PLAYER', [P_BM, P_WM, P_JS, P_OV]),
          (CB_BAYS, UP_BAYS, 'PLAYER', [P_BM, P_WM, P_JS]),
          (CB_G2, UP_G2, 'PLAYER', [P_GT, P_RP, P_GC]), (CB_G3, UP_G3, 'PLAYER', [P_GT, P_RP, P_GC]),
          (CB_BA1, UP_BA1, 'PLAYER', [P_PG, P_TH, P_HK, P_BL, P_SS, P_SH, P_ST]),
          (CB_BA2, UP_BA2, 'PLAYER', [P_PG, P_TH, P_HK, P_BL, P_SS, P_SH, P_ST]),
          (CB_WP1, UP_WP1, 'PLAYER', [P_SS, P_SH, P_ST]),
          (CB_WP2, UP_WP2, 'PLAYER', [P_PG, P_TH, P_SS, P_SH, P_ST]),
          (CB_T3D, UP_T3D, 'OBJECT', [P_WF]), (CB_T3U, UP_T3U, 'OBJECT', [P_WF]),
          (CB_BBARM, UP_BBARM, 'OBJECT', [P_BB]), (CB_BBPDL, UP_BBPDL, 'OBJECT', [P_BB]),
          (CB_BBSPK, UP_BBSPK, 'OBJECT', [P_BB]),
          (CB_VA5, UP_VA5, 'PLAYER', [P_BM, P_EMP, P_DE, P_BB, P_GT]),
          (CB_IA5, UP_IA5, 'PLAYER', [P_PG, P_TH, P_HK, P_BL])]
for cb, up, typ, paths in CHAINS:
    b = get_block(cb_f, 'CommandButton', cb, 'CB').group(1)
    check(f'Upgrade       = {up}' in b, f'{cb} upgrade ref')
    ub = get_block(upg_f, 'Upgrade', up, 'UPG').group(1)
    check(f'Type               = {typ}' in ub, f'{up} wrong Type')
    for p in paths:
        check(re.search(r'TriggeredBy\s*=.*\b%s\b' % up, shipped_texts[p]),
              f'{up}: no module wired in {p}')
# RequiredUpgrade chains resolve
for req in [UP_G2, UP_BA1, UP_WP1]:
    check(re.search(r'^Upgrade\s+%s\b' % req, upg_f, re.M), f'prereq {req} undefined')
# construct chain
b = get_block(cb_f, 'CommandButton', CB_BBBLD, 'CB').group(1)
check(f'Object        = {OBJ_BB}' in b, 'construct button object ref')
check(re.search(r'^Object %s\b' % OBJ_BB, bb_new_text, re.M), f'{OBJ_BB} undefined')
check(f'CommandSet       = {CS_BBM}' in bb_new_text and f'CommandSet = {CS_BBU}' in bb_new_text,
      'battle bunker command-set refs')
check(re.search(r'^\s*Object = Tank_ChinaBarracks\s*$', bb_new_text, re.M), 'BB prereq not Kwai barracks')
check(re.search(r'^Object\s+Tank_ChinaBarracks\b', bar_new_text, re.M), 'Tank_ChinaBarracks undefined')
# Dragon Emperor chain: button -> object -> cloned cannons defined in our Weapon.ini
b = get_block(cb_f, 'CommandButton', CB_DEBLD, 'CB').group(1)
check(f'Object        = {OBJ_DE}' in b, 'Dragon construct button object ref')
check(re.search(r'^Object %s\b' % OBJ_DE, shipped_texts[P_DE], re.M), f'{OBJ_DE} undefined')
for w in [W_DEGUN, W_DEGUND]:
    check(re.search(r'^Weapon %s\b' % w, shipped_texts[P_WPN], re.M), f'{w} not defined')
    check(w in shipped_texts[P_DE], f'Dragon does not reference {w}')
check(f'MaxSimultaneousOfType = {DRAGON_MAX_SIMUL}' in shipped_texts[P_DE], 'Dragon cap missing')
# Panzerjaeger chain: stub -> clone; QuantityModifier -> stub; clone hooks intact
check(re.search(r'^\s*BuildVariations = %s\b' % OBJ_PJ, shipped_texts[P_THS], re.M),
      'stub does not resolve to the Panzerjaeger clone')
check(re.search(r'^Object %s\b' % OBJ_PJ, shipped_texts[P_PJ], re.M), f'{OBJ_PJ} undefined')
check(re.search(r'QuantityModifier = Tank_ChinaInfantryTankHunter\s+2\b', bar_new_text),
      'TankHunter QuantityModifier missing from Barracks')
check(re.search(r'^Object Tank_ChinaInfantryTankHunter\b', shipped_texts[P_THS], re.M),
      'QuantityModifier target (the stub) undefined')
for hook in ['ModuleTag_KD_Armor4', 'ModuleTag_KD_Doctrine01', 'ModuleTag_KA_BA1',
             'ModuleTag_KA_BA2', 'ModuleTag_KA_WP2XP', 'ModuleTag_KA_IA5',
             'ModuleTag_KA_Horde01']:
    check(hook in shipped_texts[P_PJ], f'Panzerjaeger clone lost hook: {hook}')
# word-boundary: the shared ChinaInfantryTankHunterMissileLauncher weapon and
# ChinaInfantryTankHunterCommandSet are deliberate reuse, not staleness
check(not re.search(r'\bChinaInfantryTankHunter\b',
                    '\n'.join(l.split(';', 1)[0] for l in shipped_texts[P_PJ].split('\n'))),
      'stale vanilla object reference in Panzerjaeger clone (non-comment)')
# page-3/page-2 reachability: sets referenced by WF modules exist; flip buttons on the right pages
check(f'CommandSet      = {CS_WF3}' in wf_new_text, 'WF module does not open page 3')
check('CommandSet      = Tank_ChinaWarFactoryCommandSet_Down' in wf_new_text, 'WF page-3 return target')
check(f'CommandSet      = {CS_BAR2}' in bar_new_text, 'Barracks module does not open page 2')
# every slot of every new/edited set resolves to a defined button
for name in [CS_WF3, CS_BAR2, CS_BBM, CS_BBU, WF2, 'Tank_ChinaBarracksCommandSet',
             'Tank_ChinaBarracksCommandSetUpgrade', 'Tank_ChinaDozerCommandSet_Down',
             'Tank_ChinaVehicleBattleMasterCommandSet']:
    for _, btn in re.findall(r'^\s*(\d+)\s*=\s*(\S+)',
                             get_block(cs_new_text, 'CommandSet', name, 'CS').group(1), re.M):
        check(re.search(r'^CommandButton\s+%s\b' % re.escape(btn), cb_f, re.M),
              f'{name}: slot button {btn} undefined')
# labels resolve (new in our str; reused arrow labels in effective str)
for lab in NEW_LABELS:
    check(re.search(r'^%s$' % re.escape(lab), str_f, re.M), f'label {lab} missing from str')
for lab in ['CONTROLBAR:OneDown', 'CONTROLBAR:OneUp']:
    check(re.search(r'^%s$' % re.escape(lab), str_f, re.M), f'reused label {lab} missing')
# WP1 weapon lines present (new on the sniper rifle, pre-existing rotr lines on the rest)
for w in WP1_WEAPONS:
    blk = re.search(r'^Weapon %s\b.*?^End' % re.escape(w), wpn_new_text, re.M | re.S).group(0)
    check(re.search(r'WeaponBonus\s*=\s*PLAYER_UPGRADE DAMAGE', blk), f'{w}: DAMAGE line missing')
print(f'closure OK ({len(CHAINS)} button->upgrade->module chains, prereqs, construct chains, '
      'page reachability, slot resolution, labels, weapon lines)')

# ------------------------------------------------------------------ write big
ship_bytes = {P_CS: cs_new, P_CB: cb_new, P_UPG: upg_new, P_STR: str_new}
for p, txt in shipped_texts.items():
    ship_bytes[p] = txt.encode('latin-1')
entries = [bigfile.BigEntry(p, ship_bytes[p]) for p in sorted(ship_bytes)]
check(len(entries) == 26 + len(tier5_dynamic),
      f'entry count: {len(entries)} != 26 + {len(tier5_dynamic)} dynamic tier-V files')
blob = bigfile.write_big(entries)
rt = bigfile.read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries], 'BIG round-trip mismatch')
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, 'rb').read() if os.path.exists(out_path) else None
with open(out_path, 'wb') as f:
    f.write(blob)
print(f'wrote {out_path} ({len(blob)} bytes, {len(entries)} files)'
      + (' [hash-idempotent]' if prev == blob else ''))

if '--stage' in sys.argv:
    print('STAGED ONLY (no install) -- run without --stage to install to both mod dirs')
    print('ALL CHECKS PASSED (kwai-arsenal, staged)')
    sys.exit(0)

# -------------------------------------------------------------------- install
md5s = []
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    shutil.copyfile(out_path, dst)
    data = open(dst, 'rb').read()
    check(data == blob, f'install verify failed: {dst}')
    md5s.append(hashlib.md5(data).hexdigest())
    posteff = {}
    for b_ in sorted_bigs(d):
        for e in bigfile.read_big(os.path.join(d, b_)):
            posteff[e.path.lower()] = (b_, e.data)
    for e in entries:
        check(posteff[e.path.lower()] == (ARCHIVE, e.data),
              f'{d}: {e.path} not effectively ours post-install')
    # Emperor.ini is now legitimately OURS post-install: the dynamic tier-V
    # machinery ships a full copy (Fortress-derived, +ModuleTag_KA_VA5). The
    # entries loop above already asserts our copy is the effective winner.
    # (Stale Fortress-ownership assert removed -- it predated the tier-V pull.)
    print(f'installed + post-install effective audit OK: {dst}')
check(md5s[0] == md5s[1], f'archives differ across mod dirs: {md5s}')
print('both archives md5-match:', md5s[0])
print('ALL CHECKS PASSED (kwai-arsenal)')
