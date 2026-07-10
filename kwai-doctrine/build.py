#!/usr/bin/env python3
"""Build zzz-KwaiDoctrine.big — new purchasable upgrades at Kwai's (China
Tank General) Propaganda Center, for ShockWave under GeneralsX.

Roster (all researched at Tank_ChinaPropagandaCenter, player-wide):

  Composite Armor I-IV        1000/1500/2000/2500, 45s each
      +10% of base MaxHealth per tier (ADD_CURRENT_HEALTH_TOO) for ALL of
      Kwai's vehicles, aircraft and structures (absolute per-object deltas
      computed from the effective base health).  Sequential: each tier's
      button appears only after the previous tier is researched
      (CommandSetUpgrade chaining, see below).
  Infantry Conditioning I-IV  500/750/1000/1250, 30s each
      +15% of base MaxHealth per tier for the infantry Kwai fields
      (vanilla-shared ChinaInfantryRedguard/TankHunter/Hacker/BlackLotus —
      the Tank_ barracks stubs BuildVariations-redirect to these).  Modules
      are dormant for every other faction because only Kwai's Propaganda
      Center offers the research buttons.  Sequential like Composite Armor.
  Tungsten Shells             2000, 60s
      WeaponBonusUpgrade (PLAYER_UPGRADE weapon-bonus bit) on Battlemaster
      + Emperor.  Activates ShockWave's own dormant per-weapon
      'PLAYER_UPGRADE DAMAGE 125%' lines on Tank_BattleMasterTankGun[Upgraded]
      / Tank_OverlordTankGun and adds new 'PLAYER_UPGRADE RANGE 115%' lines
      to the same (Kwai-exclusive) weapons.  Net: +25% damage, +15% range.
  Advanced Infantry Doctrine  1500, 45s
      WeaponBonusUpgrade on ChinaInfantryRedguard + ChinaInfantryTankHunter
      (bit verified FREE on both: no other WeaponBonusUpgrade exists on any
      object using their weapons).  New per-weapon lines: +25% damage /
      +20% range on RedguardMachineGun + ChinaInfantryTankHunterMissile-
      Launcher, +20% range on RedguardStunBulletMachineGun.

Bonus task: Kwai's Hacker build stub (Tank_ChinaInfantryHacker) loses the
Propaganda Center prerequisite (Barracks kept) and BuildCost 625 -> 300.

Sequential-unlock mechanics (engine facts, GeneralsX GeneralsMD source):
  - UpgradeTemplate has NO prerequisite field (Upgrade.cpp:115-128, TODO at
    :456) and researched PLAYER_UPGRADE buttons stay VISIBLE-disabled
    (ControlBarCommand.cpp:1218-1242 -> COMMAND_CANT_AFFORD), so ladders
    must be compressed via command-set swaps.
  - CommandSetUpgrade sets a single per-object override string; LAST module
    to fire wins (CommandSetUpgrade.cpp:67-103, Object.cpp:6235).  The Prop
    Center already carries one such module (mines -> EMP-mines button swap,
    TriggeredBy the per-building OBJECT upgrade Upgrade_ChinaMines), so the
    full state space  mines{0,1} x CompArmor{0..4} x InfCond{0..4} = 50
    command sets is enumerated.  One CommandSetUpgrade module per non-initial
    state (49), TriggeredBy = exact upgrade set, RequiresAllTriggers = Yes
    (AND semantics, UpgradeModule.cpp:124-156; player+object upgrade masks
    are combined, Object.cpp:2510-2539).  Modules are emitted in ascending
    state-sum order: whenever an upgrade completes, every newly-satisfied
    state module fires in INI order and the maximal (= current) state has
    the strictly largest sum, so it fires last and wins.  Objects created
    later re-run all modules in the same order at spawn (Object.cpp:515),
    reproducing the correct set.
  - MaxHealthUpgrade modules stack: each is an independent one-shot delta
    (MaxHealthUpgrade.cpp:80-92); multiple modules per object are legal with
    unique tags and fire independently (Object.cpp:2510-2539), including on
    units built after research.

Why damage/range have ONE tier, not four (engine ceiling, verified):
  PLAYER_UPGRADE is the ONLY weapon-bonus condition bit settable by a
  permanent upgrade module, and WeaponBonusUpgrade/WeaponSetUpgrade/
  ArmorUpgrade are all parameterless single-flag modules (WeaponBonus-
  Upgrade.cpp:91, WeaponSetUpgrade.cpp:51, ArmorUpgrade.cpp:87).  Every
  other bit is hardwired to other subsystems.  Weapon-bonus VALUES are
  per-weapon (no global PLAYER_UPGRADE line in ShockWave's GameData.ini),
  keyed on that one bit — so per class there is at most ONE clean
  damage/range step, and only on objects where ShockWave hasn't already
  consumed the bit (taken: Gattling tank/Reaper/gattling towers via Chain
  Guns, WarMaster via Uranium Shells).

Packaging: zzz-KwaiDoctrine.big ('-' 0x2D < '_' 0x5F): sorts AFTER
zzyzzzzzz_EmperorBunker.big and BEFORE zzz_ControlBarPro*.big, so this
archive owns its files while the ControlBarPro UI skin keeps winning its
own (no shared paths anyway).  Installed to both mod dirs.
"""

import os
import re
import sys
import difflib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file, find_entry  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzz-KwaiDoctrine.big"

# ------------------------------------------------------------------ upgrades
VA = ["Tank_Upgrade_KwaiVehicleArmor%d" % n for n in (1, 2, 3, 4)]
IA = ["Tank_Upgrade_KwaiInfantryArmor%d" % n for n in (1, 2, 3, 4)]
TS = "Tank_Upgrade_KwaiTungstenShells"
ID = "Tank_Upgrade_KwaiInfantryDoctrine"
VA_BTN = ["Tank_Command_UpgradeKwaiVehicleArmor%d" % n for n in (1, 2, 3, 4)]
IA_BTN = ["Tank_Command_UpgradeKwaiInfantryArmor%d" % n for n in (1, 2, 3, 4)]
TS_BTN = "Tank_Command_UpgradeKwaiTungstenShells"
ID_BTN = "Tank_Command_UpgradeKwaiInfantryDoctrine"
VA_COST = [1000, 1500, 2000, 2500]
IA_COST = [500, 750, 1000, 1250]
ROMAN = ["I", "II", "III", "IV"]

DEFAULT_SET = "Tank_ChinaPropagandaCenterCommandSet"
UPGRADE_SET = "Tank_ChinaPropagandaCenterCommandSetUpgrade"


def set_name(m, v, i):
    if (m, v, i) == (0, 0, 0):
        return DEFAULT_SET
    if (m, v, i) == (1, 0, 0):
        return UPGRADE_SET
    return "Tank_ChinaPropagandaCenterCS_M%dV%dI%d" % (m, v, i)


# --------------------------------------------------- files & health ladders
# (archive path, expected owner archive, object name, exact MaxHealth string,
#  per-tier percent, upgrade name list, tag prefix, extra module text or None)
VEH = 0.10
INF = 0.15
P = "Data\\INI\\Object\\China\\"

WBU_TS = (
    "  Behavior = WeaponBonusUpgrade ModuleTag_KD_Tungsten01 ; zzz-KwaiDoctrine\n"
    "    TriggeredBy = %s\n"
    "  End\n" % TS)
WBU_ID = (
    "  Behavior = WeaponBonusUpgrade ModuleTag_KD_Doctrine01 ; zzz-KwaiDoctrine\n"
    "    TriggeredBy = %s\n"
    "  End\n" % ID)

HEALTH_TARGETS = [
    # ---- Kwai vehicles (Tank_-exclusive)
    (P + "Tank\\Vehicles\\BattleMaster.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaTankBattleMaster", "660.0", VEH, VA, WBU_TS),
    (P + "Tank\\Vehicles\\GattlingTank.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaTankGattling", "450.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\Emperor.ini", "zzyzzzzzz_EmperorBunker.big",
     "Tank_ChinaTankEmperor", "1320.0", VEH, VA, WBU_TS),
    (P + "Tank\\Vehicles\\WarMaster.ini", "zzx_ChinaTankBuff.big",
     "Tank_ChinaTankWarMaster", "696.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\DragonTank.ini", "zzx_ChinaTankBuff.big",
     "Tank_ChinaTankDragon", "336.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\ECMTank.ini", "zzx_ChinaTankBuff.big",
     "Tank_ChinaTankECM", "360.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\Reaper.ini", "zzx_ChinaTankBuff.big",
     "Tank_ChinaReaperTank_Real", "840.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\TroopCrawler.ini", "zzyy_ChinaBunkers.big",
     "Tank_ChinaVehicleTroopCrawler", "240.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\SupplyTruck.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaVehicleSupplyTruck", "350.0", VEH, VA, None),
    (P + "Tank\\Vehicles\\Dozer.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaVehicleDozer", "300.0", VEH, VA, None),
    (P + "Tank\\Aircraft\\Helix.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaVehicleHelix", "280.0", VEH, VA, None),
    (P + "Tank\\Aircraft\\Razor.ini", "zz_SPE_Shw_ini.big",
     "Tank_ChinaJetMIG", "160.0", VEH, VA, None),
    # ---- vanilla-shared artillery Kwai builds via kwai-artillery stubs
    (P + "Vanilla\\Vehicles\\InfernoCannon.ini", "zzyzzzz_StatTune.big",
     "ChinaVehicleInfernoCannon", "300.0", VEH, VA, None),
    (P + "Vanilla\\Vehicles\\NukeCannon.ini", "zz_SPE_Shw_ini.big",
     "ChinaVehicleNukeLauncher", "240.0", VEH, VA, None),
    # ---- Kwai structures
    (P + "Tank\\Buildings\\Airfield.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaAirfield", "3000", VEH, VA, None),
    (P + "Tank\\Buildings\\Barracks.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaBarracks", "2000", VEH, VA, None),
    (P + "Tank\\Buildings\\CommandCenter.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaCommandCenter", "10000", VEH, VA, None),
    (P + "Tank\\Buildings\\IndustrialPlant.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaIndustrialPlant", "3000", VEH, VA, None),
    (P + "Tank\\Buildings\\InternetCenter.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaInternetCenter", "20000", VEH, VA, None),
    (P + "Tank\\Buildings\\NuclearSilo.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaNuclearMissileLauncher", "8000", VEH, VA, None),
    (P + "Tank\\Buildings\\PowerPlant.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaPowerPlant", "3000", VEH, VA, None),
    (P + "Tank\\Buildings\\PropagandaCenter.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaPropagandaCenter", "3600", VEH, VA, None),
    (P + "Tank\\Buildings\\SupplyCenter.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaSupplyCenter", "4000", VEH, VA, None),
    (P + "Tank\\Buildings\\WarFactory.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaWarFactory", "4000", VEH, VA, None),
    (P + "Tank\\Defences\\Bunker.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaBunker", "3000", VEH, VA, None),
    (P + "Tank\\Defences\\GattlingCannon.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaGattlingCannon", "2000", VEH, VA, None),
    (P + "Tank\\Defences\\Ramjet Turret.ini", "zzyzzzz_StatTune.big",
     "Tank_ChinaSentryTower", "2400", VEH, VA, None),
    # ---- vanilla-shared infantry Kwai trains via barracks stubs
    (P + "Vanilla\\Infantry\\Redguard.ini", "zz_SPE_Shw_ini.big",
     "ChinaInfantryRedguard", "120.0", INF, IA, WBU_ID),
    (P + "Vanilla\\Infantry\\TankHunter.ini", "zz_SPE_Shw_ini.big",
     "ChinaInfantryTankHunter", "100.0", INF, IA, WBU_ID),
    (P + "Vanilla\\Infantry\\Hacker.ini", "zz_SPE_Shw_ini.big",
     "ChinaInfantryHacker", "100.0", INF, IA, None),
    (P + "Vanilla\\Infantry\\BlackLotus.ini", "zz_SPE_Shw_ini.big",
     "ChinaInfantryBlackLotus", "200.0", INF, IA, None),
]

UPGRADE_PATH = "Data\\INI\\Upgrade.ini"
CS_PATH = "Data\\INI\\CommandSet.ini"
CB_PATH = "Data\\INI\\CommandButton.ini"
WEAPON_PATH = "Data\\INI\\Weapon.ini"
STR_PATH = "Data\\Generals.str"
PROP_PATH = P + "Tank\\Buildings\\PropagandaCenter.ini"
HACKERSTUB_PATH = P + "Tank\\Infantry\\Hacker.ini"

OWNERS = {
    UPGRADE_PATH: "zz_SPE_Shw_ini.big",
    CS_PATH: "zzyzzzzzz_EmperorBunker.big",
    CB_PATH: "zzyzzzzz_KwaiArtillery.big",
    WEAPON_PATH: "zzyzzzz_StatTune.big",
    STR_PATH: "zz_SPE_Shw_ini.big",
    HACKERSTUB_PATH: "zz_SPE_Shw_ini.big",
}
OWNERS.update({t[0]: t[1] for t in HEALTH_TARGETS})


# ------------------------------------------------------------------ helpers
def replace_once(s, old, new):
    assert s.count(old) == 1, "expected exactly 1 occurrence of %r..." % old[:80]
    return s.replace(old, new)


def eol_of(txt):
    return "\r\n" if "\r\n" in txt else "\n"


def with_eol(block_lf, eol):
    return block_lf.replace("\n", eol) if eol != "\n" else block_lf


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def body_span(txt, hp_str):
    """Span of the (unique) Body block whose MaxHealth equals hp_str,
    including the trailing newline of its End line."""
    spans = []
    for m in re.finditer(r"(?m)^([ \t]*)Body\s*=.*$", txt):
        ind = m.group(1)
        e = re.compile(r"(?m)^%sEnd[ \t]*\r?$" % re.escape(ind)).search(txt, m.end())
        assert e, "unterminated Body block"
        block = txt[m.start():e.end()]
        if re.search(r"MaxHealth\s*=\s*%s(?![\d.])" % re.escape(hp_str), block):
            spans.append((m.start(), e.end()))
    assert len(spans) == 1, "Body(MaxHealth=%s): %d matches" % (hp_str, len(spans))
    s, e = spans[0]
    while e < len(txt) and txt[e] in "\r\n":
        e += 1
        if txt[e - 1] == "\n":
            break
    return s, e


def health_modules(obj, hp_str, pct, upgrades, extra):
    base = float(hp_str)
    out = []
    for n, upg in enumerate(upgrades, 1):
        delta = base * pct
        out.append(
            "  Behavior = MaxHealthUpgrade ModuleTag_KD_Armor%d ; zzz-KwaiDoctrine:"
            " +%d%% of base %s for %s\n"
            "    TriggeredBy   = %s\n"
            "    AddMaxHealth  = %.1f\n"
            "    ChangeType    = ADD_CURRENT_HEALTH_TOO\n"
            "  End\n" % (n, int(pct * 100), hp_str, obj, upg, delta))
    if extra:
        out.append(extra)
    return "".join(out)


def patch_health(txt, obj, hp_str, pct, upgrades, extra):
    eol = eol_of(txt)
    ins = with_eol(health_modules(obj, hp_str, pct, upgrades, extra), eol)
    s, e = body_span(txt, hp_str)
    assert ("Object %s" % obj) in txt or ("Object  %s" % obj) in txt, obj
    return txt[:e] + ins + txt[e:], ins


# ------------------------------------------------------- generated INI text
def upgrades_ini_block():
    out = ["\n;;; zzz-KwaiDoctrine: Kwai Propaganda Center doctrine upgrades\n"]
    for n in range(4):
        out.append(
            "Upgrade %s\n"
            "  DisplayName        = UPGRADE:KwaiVehicleArmor%d\n"
            "  Type               = PLAYER\n"
            "  BuildTime          = 45.0\n"
            "  BuildCost          = %d\n"
            "  ButtonImage        = SNTankTitaniumArmor\n"
            "  ResearchSound      = ReaperVoiceUpgrade\n"
            "End\n\n" % (VA[n], n + 1, VA_COST[n]))
    for n in range(4):
        out.append(
            "Upgrade %s\n"
            "  DisplayName        = UPGRADE:KwaiInfantryArmor%d\n"
            "  Type               = PLAYER\n"
            "  BuildTime          = 30.0\n"
            "  BuildCost          = %d\n"
            "  ButtonImage        = SNChemsuit\n"
            "  ResearchSound      = ChineRedGuardUpgradeChemSuits\n"
            "End\n\n" % (IA[n], n + 1, IA_COST[n]))
    out.append(
        "Upgrade %s\n"
        "  DisplayName        = UPGRADE:KwaiTungstenShells\n"
        "  Type               = PLAYER\n"
        "  BuildTime          = 60.0\n"
        "  BuildCost          = 2000\n"
        "  ButtonImage        = SNUrShells\n"
        "  ResearchSound      = BattleMasterTankVoiceUpgradeWeaponsGrade\n"
        "End\n\n" % TS)
    out.append(
        "Upgrade %s\n"
        "  DisplayName        = UPGRADE:KwaiInfantryDoctrine\n"
        "  Type               = PLAYER\n"
        "  BuildTime          = 45.0\n"
        "  BuildCost          = 1500\n"
        "  ButtonImage        = Infa_SNPatriotism\n"
        "  ResearchSound      = RedGuardVoiceUpgradePatriotism\n"
        "End\n" % ID)
    return "".join(out)


def button(name, upg, label_stub):
    return (
        "CommandButton %s\n"
        "  Command       = PLAYER_UPGRADE\n"
        "  Upgrade       = %s\n"
        "  TextLabel     = CONTROLBAR:%s\n"
        "  ButtonImage   = %s\n"
        "  ButtonBorderType        = UPGRADE ; Identifier for the User as to what kind of button this is\n"
        "  DescriptLabel           = CONTROLBAR:Tooltip%s\n"
        "  PurchasedLabel          = CONTROLBAR:Tooltip%s\n"
        "  UnitSpecificSound = MoneyWithdraw\n"
        "End\n\n" % (name, upg, label_stub,
                     BTN_IMAGE[name], label_stub, label_stub))


BTN_IMAGE = {}
for n in range(4):
    BTN_IMAGE[VA_BTN[n]] = "SNTankTitaniumArmor"
    BTN_IMAGE[IA_BTN[n]] = "SNChemsuit"
BTN_IMAGE[TS_BTN] = "SNUrShells"
BTN_IMAGE[ID_BTN] = "Infa_SNPatriotism"


def buttons_ini_block():
    out = ["\n;;; zzz-KwaiDoctrine: Kwai Propaganda Center doctrine buttons\n"]
    for n in range(4):
        out.append(button(VA_BTN[n], VA[n], "UpgradeKwaiVehicleArmor%d" % (n + 1)))
    for n in range(4):
        out.append(button(IA_BTN[n], IA[n], "UpgradeKwaiInfantryArmor%d" % (n + 1)))
    out.append(button(TS_BTN, TS, "UpgradeKwaiTungstenShells"))
    out.append(button(ID_BTN, ID, "UpgradeKwaiInfantryDoctrine"))
    return "".join(out)


def prop_set_block(m, v, i):
    return (
        "CommandSet %s\n"
        "  1  = Command_UpgradeChinaNationalism\n"
        "  2  = Command_UpgradeChinaSubliminalMessaging\n"
        "  3  = Command_UpgradeChinaNeutronBomb\n"
        "  4  = Command_UpgradeChinaChainGuns\n"
        "  5  = Command_UpgradeChinaBlackNapalm\n"
        "  6  = %s\n"
        "  7  = %s\n"
        "  8  = %s\n"
        "  9  = %s\n"
        " 13  = %s\n"
        " 14  = Command_Sell  \n"
        "End\n\n" % (
            set_name(m, v, i),
            VA_BTN[min(v, 3)], IA_BTN[min(i, 3)], TS_BTN, ID_BTN,
            "Command_UpgradeEMPMines" if m else "Command_UpgradeChinaMines"))


def all_states():
    sts = [(m, v, i) for m in (0, 1) for v in range(5) for i in range(5)]
    sts.sort(key=lambda s: (sum(s), s))
    return sts


def commandsets_appendix():
    out = ["\n; zzz-KwaiDoctrine: Propaganda Center ladder state sets\n"
           "; (mines x CompositeArmor x InfantryConditioning; the two base\n"
           ";  states reuse the original set names, edited in place above)\n\n"]
    for (m, v, i) in all_states():
        if (m, v, i) in ((0, 0, 0), (1, 0, 0)):
            continue
        out.append(prop_set_block(m, v, i))
    return "".join(out)


def prop_center_csu_modules():
    out = []
    for (m, v, i) in all_states():
        if (m, v, i) == (0, 0, 0):
            continue
        trig = ([u for u in ["Upgrade_ChinaMines"] if m]
                + VA[:v] + IA[:i])
        out.append(
            "  Behavior = CommandSetUpgrade ModuleTag_KD_CS_M%dV%dI%d ; zzz-KwaiDoctrine ladder state\n"
            "    CommandSet = %s\n"
            "    TriggeredBy = %s\n"
            "    RequiresAllTriggers = Yes\n"
            "  End\n" % (m, v, i, set_name(m, v, i), " ".join(trig)))
    return "".join(out)


def strings_appendix():
    ent = []
    for n in range(4):
        nxt = (" \\n Unlocks Composite Armor %s." % ROMAN[n + 1]) if n < 3 else ""
        ent += [
            ("UPGRADE:KwaiVehicleArmor%d" % (n + 1),
             "Composite Armor %s" % ROMAN[n]),
            ("CONTROLBAR:UpgradeKwaiVehicleArmor%d" % (n + 1),
             "Composite Armor %s" % ROMAN[n]),
            ("CONTROLBAR:TooltipUpgradeKwaiVehicleArmor%d" % (n + 1),
             "Layered composite plating for Kwai's war machine. "
             "\\n +10% maximum health for all vehicles, aircraft and structures."
             + nxt),
        ]
    for n in range(4):
        nxt = (" \\n Unlocks Infantry Conditioning %s." % ROMAN[n + 1]) if n < 3 else ""
        ent += [
            ("UPGRADE:KwaiInfantryArmor%d" % (n + 1),
             "Infantry Conditioning %s" % ROMAN[n]),
            ("CONTROLBAR:UpgradeKwaiInfantryArmor%d" % (n + 1),
             "Infantry Conditioning %s" % ROMAN[n]),
            ("CONTROLBAR:TooltipUpgradeKwaiInfantryArmor%d" % (n + 1),
             "Hardened field training for Kwai's infantry. "
             "\\n +15% maximum health for Red Guard, Tank Hunters, Hackers and Black Lotus."
             + nxt),
        ]
    ent += [
        ("UPGRADE:KwaiTungstenShells", "Tungsten Shells"),
        ("CONTROLBAR:UpgradeKwaiTungstenShells", "Tungsten Shells"),
        ("CONTROLBAR:TooltipUpgradeKwaiTungstenShells",
         "Tungsten-cored ammunition for Kwai's cannon platforms. "
         "\\n +25% damage and +15% range for Battlemaster and Emperor main guns."),
        ("UPGRADE:KwaiInfantryDoctrine", "Advanced Infantry Doctrine"),
        ("CONTROLBAR:UpgradeKwaiInfantryDoctrine", "Advanced Infantry Doctrine"),
        ("CONTROLBAR:TooltipUpgradeKwaiInfantryDoctrine",
         "Live-fire assault doctrine for Kwai's infantry. "
         "\\n +25% damage and +20% range for Red Guard rifles and Tank Hunter missiles."),
    ]
    return "".join("\n\n%s\n\"%s\"\nEND" % (label, text) for label, text in ent)


# ------------------------------------------------------------- file patches
def patch_commandset(txt):
    add = ("  6  = %s\n  7  = %s\n  8  = %s\n  9  = %s\n"
           % (VA_BTN[0], IA_BTN[0], TS_BTN, ID_BTN))
    old_def = (
        "CommandSet %s\n"
        "  1  = Command_UpgradeChinaNationalism\n"
        "  2  = Command_UpgradeChinaSubliminalMessaging\n"
        "  3  = Command_UpgradeChinaNeutronBomb\n"
        "  4  = Command_UpgradeChinaChainGuns\n"
        "  5  = Command_UpgradeChinaBlackNapalm\n"
        " 13  = Command_UpgradeChinaMines\n" % DEFAULT_SET)
    new_def = old_def.replace(" 13  =", add + " 13  =", 1)
    txt = replace_once(txt, old_def, new_def)
    old_upg = (
        "CommandSet %s\n"
        "  1  = Command_UpgradeChinaNationalism\n"
        "  2  = Command_UpgradeChinaSubliminalMessaging\n"
        "  3  = Command_UpgradeChinaNeutronBomb\n"
        "  4  = Command_UpgradeChinaChainGuns\n"
        "  5  = Command_UpgradeChinaBlackNapalm\n"
        " 13  = Command_UpgradeEMPMines\n" % UPGRADE_SET)
    new_upg = old_upg.replace(" 13  =", add + " 13  =", 1)
    txt = replace_once(txt, old_upg, new_upg)
    return txt + commandsets_appendix()


def patch_prop_center(txt):
    eol = eol_of(txt)
    old = with_eol(
        "  Behavior = CommandSetUpgrade ModuleTag_25\n"
        "    CommandSet = Tank_ChinaPropagandaCenterCommandSetUpgrade\n"
        "    TriggeredBy = Upgrade_ChinaMines\n"
        "  End\n", eol)
    return replace_once(txt, old, with_eol(prop_center_csu_modules(), eol))


def patch_weapon(txt):
    """Block-scoped weapon edits (LF file)."""
    def block(name):
        m = re.search(r"(?m)^Weapon %s\s*$" % re.escape(name), txt)
        assert m, "weapon not found: " + name
        e = re.search(r"(?m)^End\s*$", txt[m.end():])
        assert e
        return m.start(), m.end() + e.end()

    def insert_in_block(t, name, anchor_re, addition):
        s, e = block(name)
        seg = t[s:e]
        am = list(re.finditer(anchor_re, seg))
        assert len(am) == 1, (name, anchor_re, len(am))
        p = am[0].end()
        while seg[p - 1] != "\n":
            p += 1
        return t[:s] + seg[:p] + addition + seg[p:] + t[e:]

    ts_note = " ; zzz-KwaiDoctrine Tungsten Shells\n"
    id_note = " ; zzz-KwaiDoctrine Advanced Infantry Doctrine\n"
    for w in ("Tank_BattleMasterTankGun", "Tank_BattleMasterTankGunUpgraded",
              "Tank_OverlordTankGun"):
        txt = insert_in_block(
            txt, w,
            r"(?m)^\s*WeaponBonus\s*=\s*PLAYER_UPGRADE DAMAGE 125% ; UraniumShells\s*$",
            "  WeaponBonus             = PLAYER_UPGRADE RANGE 115%" + ts_note)
    txt = insert_in_block(
        txt, "RedguardMachineGun",
        r"(?m)^  AttackRange           = 110\.0\s*$",
        "  WeaponBonus           = PLAYER_UPGRADE DAMAGE 125%" + id_note
        + "  WeaponBonus           = PLAYER_UPGRADE RANGE 120%" + id_note)
    txt = insert_in_block(
        txt, "RedguardStunBulletMachineGun",
        r"(?m)^  AttackRange            = 120\.0\s*$",
        "  WeaponBonus            = PLAYER_UPGRADE RANGE 120%" + id_note)
    txt = insert_in_block(
        txt, "ChinaInfantryTankHunterMissileLauncher",
        r"(?m)^  AttackRange = 175\.0\s*$",
        "  WeaponBonus = PLAYER_UPGRADE DAMAGE 125%" + id_note
        + "  WeaponBonus = PLAYER_UPGRADE RANGE 120%" + id_note)
    return txt


def patch_hacker_stub(txt):
    eol = eol_of(txt)
    txt = replace_once(txt, "  BuildCost = 625" + eol,
                       "  BuildCost = 300 ; zzz-KwaiDoctrine (was 625)" + eol)
    txt = replace_once(
        txt,
        "  Prerequisites" + eol
        + "    Object = Tank_ChinaBarracks" + eol
        + "    Object = Tank_ChinaPropagandaCenter" + eol,
        "  Prerequisites" + eol
        + "    Object = Tank_ChinaBarracks" + eol
        + "    ; zzz-KwaiDoctrine: Propaganda Center prerequisite removed" + eol)
    return txt


# -------------------------------------------------------------- verification
def verify_commandset_survival(cs):
    checks = {
        ("Kwai artillery factory slots 11-12 (both variants)", 2):
            "  11 = Tank_Command_ConstructChinaVehicleInfernoCannon\n"
            "  12 = Tank_Command_ConstructChinaVehicleNukeLauncher\n",
        # chain guns + napalm now live in all 50 prop-center state sets
        ("prop-center slots 4-5 (2 base + 48 state sets)", 50):
            "  4  = Command_UpgradeChinaChainGuns\n"
            "  5  = Command_UpgradeChinaBlackNapalm\n",
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
        ("vanilla Battlemaster exits", 1):
            "CommandSet ChinaVehicleBattleMasterCommandSet\n"
            "  1  = Command_TransportExit\n",
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
        # my ladder buttons present in both original prop-center sets
        ("doctrine slots 6-9 (2 base + 48 state sets)", 50):
            "  8  = %s\n  9  = %s\n" % (TS_BTN, ID_BTN),
    }
    for (label, count), needle in checks.items():
        assert cs.count(needle) == count, \
            "CS SURVIVAL FAILED: %s (found %d)" % (label, cs.count(needle))
        print("  commandset OK:", label)


def verify_weapon_survival(w, src=None):
    """Structural presence + (when the effective source is at hand) that the
    stat-tune-owned AttackRange values were carried through unchanged.
    Values are compared source-vs-patched rather than hardcoded because the
    stat-tune layer is actively re-tuned (its numbers drifted 420->350 for
    the Inferno during this build's development)."""
    assert "Weapon ShwBattleMasterCoaxMGWeapon\n" in w, \
        "WEAPON SURVIVAL FAILED: coax weapon present"

    def rng_of(text, wname):
        m = re.search(r"(?m)^Weapon %s\s*$" % wname, text)
        assert m, "WEAPON SURVIVAL FAILED: missing " + wname
        seg = text[m.start():m.start() + 1200]
        r = re.search(r"AttackRange\s*=\s*([\d.]+)", seg)
        assert r, "WEAPON SURVIVAL FAILED: no AttackRange in " + wname
        return r.group(1)

    for wname in ("GattlingTankGun", "InfernoCannonGun", "NukeCannonGun",
                  "Tank_BattleMasterTankGun", "RedguardMachineGun",
                  "ChinaInfantryTankHunterMissileLauncher"):
        got = rng_of(w, wname)
        if src is not None:
            want = rng_of(src, wname)
            assert got == want, \
                "WEAPON SURVIVAL FAILED: %s range %s != source %s" % (
                    wname, got, want)
        print("  weapon OK: %s AttackRange %s" % (wname, got))


def verify_emperor_survival(t):
    for label, needle in {
        "china-tank-buff MaxHealth 1320":
            "    MaxHealth       = 1320.0\r\n",
        "HelixContain bunker bay": "  Behavior = HelixContain ModuleTag_06",
        "10 passenger slots": "    Slots                   = 10\r\n",
        "propaganda tower behavior":
            "  Behavior        = PropagandaTowerBehavior ModulePropaganda_15\r\n",
        "gattling upgrade chain":
            "    UpgradeObject = OCL_Tank_OverlordGattlingCannon\r\n",
    }.items():
        assert needle in t, "EMPEROR SURVIVAL FAILED: " + label
        print("  emperor OK:", label)


def verify_battlemaster_survival(t):
    for label, needle in {
        "stat-tune MaxHealth 660": "MaxHealth       = 660.0",
        "coax secondary weapon": "Weapon = SECONDARY ShwBattleMasterCoaxMGWeapon",
        "ERA HelixContain": "Behavior = HelixContain ModuleTag_ArmorAddon01",
        "ERA rider OCL": "UpgradeObject = OCL_BattleMasterArmorAddons",
        "ERA command-set swap":
            "CommandSet  = Tank_ChinaVehicleBattleMasterCommandSetERA",
        "prop tower mount": "UpgradeObject = OCL_OverlordPropagandaTower",
    }.items():
        assert needle in t.replace("\r\n", "\n"), "BM SURVIVAL FAILED: " + label
        print("  battlemaster OK:", label)


def block_balance(old, new, opener="Behavior", extra_blocks=0):
    o = sum(1 for l in old.splitlines() if l.strip().startswith(opener + " "))
    n = sum(1 for l in new.splitlines() if l.strip().startswith(opener + " "))
    return n - o


# ---------------------------------------------------------------------- main
def main():
    # effective-file map from the SPE mod dir (later-alphabetical wins)
    archives = sorted((f for f in os.listdir(SPE_DIR)
                       if f.lower().endswith(".big")
                       and f.lower() != OUT_NAME.lower()),  # rebuild-safe:
                      key=str.lower, reverse=True)          # never self-source
    cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}

    def effective(path):
        want = path.lower()
        for a in archives:
            for e in cache[a]:
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        raise SystemExit("effective source not found: " + path)

    sources = {}
    for path, owner in OWNERS.items():
        data, got = effective(path)
        assert got == owner, "ownership drift for %s: %s (expected %s)" % (
            path, got, owner)
        sources[path] = data
    print("effective-file ownership verified for %d files" % len(sources))

    patched = {}
    audit = []

    # ---- object files: health ladders (+ weapon-bonus modules)
    for path, owner, obj, hp, pct, upgrades, extra in HEALTH_TARGETS:
        txt = patched.get(path, sources[path])
        new, ins = patch_health(txt, obj, hp, pct, upgrades, extra)
        added = ins.replace("\r\n", "\n").rstrip("\n").split("\n")
        audit.append((path, added, []))
        patched[path] = new

    # ---- Propaganda Center: replace mines CSU with the 49-state family
    prop = patch_prop_center(patched[PROP_PATH])
    audit.append((PROP_PATH,
                  prop_center_csu_modules().rstrip("\n").split("\n"),
                  ["  Behavior = CommandSetUpgrade ModuleTag_25",
                   "    CommandSet = Tank_ChinaPropagandaCenterCommandSetUpgrade",
                   "    TriggeredBy = Upgrade_ChinaMines",
                   "  End"]))
    patched[PROP_PATH] = prop

    # ---- Hacker stub
    patched[HACKERSTUB_PATH] = patch_hacker_stub(sources[HACKERSTUB_PATH])

    # ---- Upgrade.ini / CommandButton.ini / Generals.str: append-only
    for path, appendix in ((UPGRADE_PATH, upgrades_ini_block()),
                           (CB_PATH, buttons_ini_block()),
                           (STR_PATH, strings_appendix())):
        src = sources[path]
        eol = eol_of(src)
        patched[path] = src + with_eol(appendix, eol)
        assert patched[path].startswith(src)

    # ---- CommandSet.ini
    patched[CS_PATH] = patch_commandset(sources[CS_PATH])

    # ---- Weapon.ini
    patched[WEAPON_PATH] = patch_weapon(sources[WEAPON_PATH])

    # -------------------------------------------------------- audit & checks
    merged = {}
    for path, added_expected, removed_expected in audit:
        a, r = merged.setdefault(path, ([], []))
        a.extend(added_expected)
        r.extend(removed_expected)
    for path, (added_expected, removed_expected) in merged.items():
        diff = unified(sources[path].replace("\r\n", "\n"),
                       patched[path].replace("\r\n", "\n"))
        add = [l[1:] for l in diff if l.startswith("+")]
        rem = [l[1:] for l in diff if l.startswith("-")]
        # difflib may rotate insertions around shared lines ("End", and the
        # removed mines-CSU block matches lines inside the generated family),
        # so compare NET multisets: added-minus-removed both ways.
        from collections import Counter
        ca, cr = Counter(add), Counter(rem)
        ea, er = Counter(added_expected), Counter(removed_expected)
        assert ca - cr == ea - er, "diff drift (net added) in " + path
        assert cr - ca == er - ea, "diff drift (net removed) in " + path
    print("object-file diff audit OK (%d files)" % len(merged))

    # hacker stub diff
    hdiff = unified(sources[HACKERSTUB_PATH].replace("\r\n", "\n"),
                    patched[HACKERSTUB_PATH].replace("\r\n", "\n"))
    assert sorted(hdiff) == sorted([
        "-  BuildCost = 625",
        "+  BuildCost = 300 ; zzz-KwaiDoctrine (was 625)",
        "-    Object = Tank_ChinaPropagandaCenter",
        "+    ; zzz-KwaiDoctrine: Propaganda Center prerequisite removed",
    ]), hdiff
    print("hacker stub diff OK:", hdiff)

    # weapon diff: 8 added WeaponBonus lines, nothing removed
    wdiff = unified(sources[WEAPON_PATH], patched[WEAPON_PATH])
    wadd = [l for l in wdiff if l.startswith("+")]
    wrem = [l for l in wdiff if l.startswith("-")]
    assert not wrem and len(wadd) == 8 and \
        all("PLAYER_UPGRADE" in l and "zzz-KwaiDoctrine" in l for l in wadd), wdiff
    print("Weapon.ini diff OK (8 added WeaponBonus lines)")

    # commandset diff: 8 inserted slot lines + appendix, nothing removed
    cdiff = unified(sources[CS_PATH], patched[CS_PATH])
    crem = [l for l in cdiff if l.startswith("-")]
    assert not crem, crem
    cadd = [l[1:] for l in cdiff if l.startswith("+")]
    slot_inserts = [l for l in cadd if l.startswith(("  6  =", "  7  =",
                                                     "  8  =", "  9  ="))]
    assert len(slot_inserts) == 8 + 48 * 4, len(slot_inserts)
    new_sets = [l for l in cadd if l.startswith("CommandSet ")]
    assert len(new_sets) == 48 and len(set(new_sets)) == 48
    print("CommandSet.ini diff OK (48 new sets, 2 sets extended)")

    # block balance
    for path in patched:
        old, new = sources[path], patched[path]
        eo = old.count("End"); en = new.count("End")
        assert en >= eo, path
    cs_new = patched[CS_PATH]
    assert (sum(1 for l in cs_new.splitlines() if l.startswith("CommandSet "))
            - sum(1 for l in sources[CS_PATH].splitlines()
                  if l.startswith("CommandSet "))) == 48
    assert block_balance(sources[PROP_PATH], patched[PROP_PATH]) == 49 - 1 + 4
    print("block balance OK")

    # every generated set referenced by exactly one module and vice versa
    mods = re.findall(r"CommandSet = (\S+)", prop_center_csu_modules())
    assert len(mods) == 49 and len(set(mods)) == 49
    for s in mods:
        assert ("CommandSet %s\n" % s) in cs_new, "set missing: " + s
    # ladder buttons exist for every command referenced
    cb_new = patched[CB_PATH]
    for b in VA_BTN + IA_BTN + [TS_BTN, ID_BTN]:
        assert ("CommandButton %s\n" % b) in cb_new, b
        assert ("  6  = %s\n" % b) in cs_new or ("  7  = %s\n" % b) in cs_new \
            or ("  8  = %s\n" % b) in cs_new or ("  9  = %s\n" % b) in cs_new
    # upgrades defined for every button
    up_new = patched[UPGRADE_PATH].replace("\r\n", "\n")
    for u in VA + IA + [TS, ID]:
        assert ("Upgrade %s\n" % u) in up_new, u
    # strings defined for every label referenced by the new buttons
    str_new = patched[STR_PATH].replace("\r\n", "\n")
    for lbl in re.findall(r"CONTROLBAR:\S+|UPGRADE:\S+",
                          buttons_ini_block() + upgrades_ini_block()):
        if "Kwai" in lbl:
            assert ("\n%s\n" % lbl) in str_new, "missing string: " + lbl
    print("cross-reference closure OK (sets<->modules<->buttons<->upgrades<->strings)")

    # sibling survival on the final text
    verify_commandset_survival(cs_new)
    verify_weapon_survival(patched[WEAPON_PATH], sources[WEAPON_PATH])
    verify_emperor_survival(patched[P + "Tank\\Vehicles\\Emperor.ini"])
    verify_battlemaster_survival(patched[P + "Tank\\Vehicles\\BattleMaster.ini"])

    # ---- package
    entries = [BigEntry(path, patched[path].encode("latin-1"))
               for path in sorted(patched)]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_local)
    print("wrote %s (%d files, %d bytes)"
          % (out_local, len(entries), os.path.getsize(out_local)))

    # ---- sort-order verification against the real directory listing
    for d in (SPE_DIR, SHW_DIR):
        listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                         | {OUT_NAME}, key=str.lower)
        i = listing.index(OUT_NAME)
        after = listing[i - 1]
        before = listing[i + 1] if i + 1 < len(listing) else None
        assert after.lower() == "zzyzzzzzz_emperorbunker.big", listing
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
        for a, b in zip(back, entries):
            assert a.data == b.data, a.path
        verify_commandset_survival(find_entry(back, CS_PATH).data.decode("latin-1"))
        verify_weapon_survival(find_entry(back, WEAPON_PATH).data.decode("latin-1"),
                               sources[WEAPON_PATH])
        verify_emperor_survival(
            find_entry(back, P + "Tank\\Vehicles\\Emperor.ini").data.decode("latin-1"))
        print("installed + re-read OK:", dst)

    print("DONE")


if __name__ == "__main__":
    main()
