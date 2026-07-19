#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big  --  the REBALANCE (harder Kwai)
top layer of the Panzergrenadiers stack (ShockWave under GeneralsX / macOS).

Design goal (user-approved): Kwai's tanks + infantry start MODEST; power is
EARNED through veterancy (combat) and upgrades (economy).  This layer pulls
the inflated player buffs back toward STOCK and makes the 7 Hard AI relentless
via its economy.  Pure data; no engine, no art, no new identifiers.

It is the LAST data layer: `zzz-` + 18 'Z' + `0Rebalance` sorts (case-
insensitively) AFTER every existing data layer (the highest is
zzz-ZZZZZZZZZZZZZZZZZ0EmperorTweaks = 17 'Z') because at char 18 our 'Z'
(0x7A) > EmperorTweaks' '0' (0x30); and BEFORE zzz_ControlBarPro*/zzzz_
FXEnhance because '-' (0x2D) < '_' (0x5F) and '-' < 'z'.  Verified against the
real listings of BOTH mod dirs at build time.

Every file is re-shipped from the WINNING (highest-priority) copy beneath us,
so all prior structural edits (bays, coax, PDL, Emperor/tesla/drop changes,
garrison, doctrine, ...) are preserved BYTE-FOR-BYTE except the specific
numeric stat lines this layer intentionally changes.  Values are anchored to
the genuine STOCK ShockWave-SPE base (read live from the base archive) so the
anchor cannot drift.

FORBIDDEN (owned by concurrent sessions; NOT touched): the shellmap map files,
ShellEmperorElite.ini, EmperorFullDrop.ini, RotrShockTrooper.ini, SagePatch.ini.

--------------------------------------------------------------------------
A. CUT PLAYER BASE BUFFS TOWARD STOCK
   1+2. All 24 china-tank-buff tanks: MaxHealth/InitialHealth -> STOCK
        (reverts china-tank-buff +20% HP, gattling-buff +15%, stat-tune
        absolutes).  All china-tank-buff weapon ranges -> STOCK (reverts +10%
        / gattling +20% / stat-tune BM 198 & gattling 250/462).  Nuke Cannon
        family range -> STOCK (reverts stat-tune 800).  +5% locomotor SPEED is
        KEPT (Locomotor.ini is not touched, so china-tank-buff's speeds stay
        effective).  Howitzer (250) and Inferno range (350) are intentional
        nerfs and are LEFT alone.
   Kwai Tank buildings: 2x -> ~1.25x STOCK HP (13 structures).
   Inferno Cannon HP: 300 -> 210 (toward stock 195, tiny edge).
   3. China infantry cost/build (w-economy's 50%/2x): re-toned to ~15% cheaper
      + ~1.25x build speed (0.85x stock cost, 0.8x stock time; 32 objects).
B. China infantry combat HP -50% (near-useless on foot; still valuable
   garrisoned @140% range / inside tank bays).  Heroes, hackers, non-combat,
   squad-nexus controllers, the mortar-pit emplacement crew, and the FORBIDDEN
   RotrShockTrooper.ini units are EXEMPT (documented).
C. Veterancy untouched (SagePatch.ini owned by the main session).
D. AI economy:
   1. Inexhaustible supplies: every persistent supply source's StartingBoxes
      -> 100000 (x $ValuePerSupplyBox = effectively bottomless).  Global.
   2. AI-specific relentlessness (AIData.ini, AI-only fields): Wealthy 12000
      ->6000, Poor 3000->1500, StructuresWealthyRate 2->3, TeamsWealthyRate
      2->3, TeamSeconds 10->5  -- with bottomless money the Hard AI stays
      "wealthy" and builds structures + attack teams far more often.  Plus a
      modest GLOBAL ValuePerSupplyBox 75->90 so both sides can afford constant
      production (helps the player too -- accepted; the challenge is surviving
      the assault).  AI superweapons stay OFF (not restored).
"""
import os, re, sys, hashlib, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import read_big, write_big_file, BigEntry  # noqa: E402

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SW = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big"   # 18 'Z'
TAG = "Rebalance"
BASE_ARCHIVES = ["zz_SPE_Shw_ini.big", "!Shw_ini.big"]
# archives that sort ABOVE us (their copies must NOT be overridden by us, and
# they must not claim any path we ship):
ABOVE = {"zzz_controlbarpro2160zh.big", "zzz_controlbarprozh.big", "zzzz_fxenhance.big"}

# --------------------------------------------------------------------------
# archive plumbing
# --------------------------------------------------------------------------
def sorted_bigs(d):
    return sorted([f for f in os.listdir(d) if f.lower().endswith(".big")], key=str.lower)

_arch_cache = {}
def arch_files(d, arch):
    key = (d, arch)
    if key not in _arch_cache:
        _arch_cache[key] = {e.path: e.data for e in read_big(os.path.join(d, arch))}
    return _arch_cache[key]

def build_owner(d):
    """path.lower() -> (arch, realpath) winner among archives sorting BELOW us."""
    owner = {}
    for arch in sorted_bigs(d):
        if arch.lower() in ABOVE or arch == OUT_NAME:
            continue
        for e in read_big(os.path.join(d, arch)):
            owner[e.path.lower()] = (arch, e.path)
    return owner

def base_file(d, relpath):
    for a in BASE_ARCHIVES:
        if not os.path.exists(os.path.join(d, a)):
            continue
        fs = arch_files(d, a)
        if relpath in fs:
            return fs[relpath].decode("latin-1"), a
    raise SystemExit(f"base copy not found: {relpath}")

# --------------------------------------------------------------------------
# region-scoped, line-precise editing
# --------------------------------------------------------------------------
def _block_region(txt, kw, name):
    hdrs = list(re.finditer(r"(?mi)^%s\s+(\S+)" % kw, txt))
    for i, m in enumerate(hdrs):
        if m.group(1) == name:
            s = m.end()
            e = hdrs[i + 1].start() if i + 1 < len(hdrs) else len(txt)
            return s, e
    raise SystemExit(f"{kw} {name}: not found")

def set_field(txt, kw, name, field, newval, must=1):
    """Set every `field = X` within the `kw name` block to newval (formatted).
    Returns (txt, n_changed).  Asserts at least `must` lines change."""
    s, e = _block_region(txt, kw, name)
    region = txt[s:e]
    nv = ("%g" % newval) if isinstance(newval, float) else str(newval)
    pat = re.compile(r"(?mi)^(?P<lead>\s*%s\s*=\s*)(?P<val>[0-9]+(?:\.[0-9]+)?)" % re.escape(field))
    cnt = [0]
    def repl(mm):
        cnt[0] += 1
        return mm.group("lead") + nv
    region2 = pat.sub(repl, region)
    assert cnt[0] >= must, f"{kw} {name}: expected >={must} '{field}' lines, got {cnt[0]}"
    return txt[:s] + region2 + txt[e:], cnt[0]

def get_field(txt, kw, name, field):
    s, e = _block_region(txt, kw, name)
    m = re.search(r"(?mi)^\s*%s\s*=\s*([0-9]+(?:\.[0-9]+)?)" % re.escape(field), txt[s:e])
    return float(m.group(1)) if m else None

def round5(x):
    return int(round(x / 5.0) * 5)

# --------------------------------------------------------------------------
# 24 china-tank-buff tanks -> file (resolved) ; STOCK HP read from base
# --------------------------------------------------------------------------
TANK_FILES = {
 "ChinaTankBattleMaster_Var1": r"Data\INI\Object\China\Vanilla\Vehicles\BattleMaster.ini",
 "ChinaTankDragon": r"Data\INI\Object\China\Vanilla\Vehicles\DragonTank.ini",
 "ChinaTankECM": r"Data\INI\Object\China\Vanilla\Vehicles\ECMTank.ini",
 "ChinaTankGattling": r"Data\INI\Object\China\Vanilla\Vehicles\GattlingTank.ini",
 "ChinaTankOverlord": r"Data\INI\Object\China\Vanilla\Vehicles\Overlord.ini",
 "Infa_ChinaTankOverlord": r"Data\INI\Object\China\Infantry\Vehicles\BattleFortress.ini",
 "Infa_ChinaTankGattling": r"Data\INI\Object\China\Infantry\Vehicles\GattlingAPC.ini",
 "Infa_ChinaVehicleNukeLauncher": r"Data\INI\Object\China\Infantry\Vehicles\TigerShark.ini",
 "Nuke_ChinaTankBattleMaster": r"Data\INI\Object\China\Nuke\Vehicles\BattleMaster.ini",
 "Nuke_ChinaTankDevastator": r"Data\INI\Object\China\Nuke\Vehicles\Devastator.ini",
 "Nuke_ChinaTankGattling": r"Data\INI\Object\China\Nuke\Vehicles\GattlingTank.ini",
 "Nuke_ChinaTankOverlord": r"Data\INI\Object\China\Nuke\Vehicles\Overlord.ini",
 "Nuke_ChinaTankDragon": r"Data\INI\Object\China\Nuke\Vehicles\RADTank.ini",
 "Spec_ChinaTankDragon": r"Data\INI\Object\China\SpecialWeapons\Vehicles\DragonTank.ini",
 "Spec_ChinaTankGattling": r"Data\INI\Object\China\SpecialWeapons\Vehicles\GattlingTank.ini",
 "Spec_ChinaTankBattleMaster": r"Data\INI\Object\China\SpecialWeapons\Vehicles\RavageTank.ini",
 "Spec_ChinaVehicleSeismicTank": r"Data\INI\Object\China\SpecialWeapons\Vehicles\SeismicTank.ini",
 "Tank_ChinaTankBattleMaster": r"Data\INI\Object\China\Tank\Vehicles\BattleMaster.ini",
 "Tank_ChinaTankDragon": r"Data\INI\Object\China\Tank\Vehicles\DragonTank.ini",
 "Tank_ChinaTankECM": r"Data\INI\Object\China\Tank\Vehicles\ECMTank.ini",
 "Tank_ChinaTankEmperor": r"Data\INI\Object\China\Tank\Vehicles\Emperor.ini",
 "Tank_ChinaTankGattling": r"Data\INI\Object\China\Tank\Vehicles\GattlingTank.ini",
 "Tank_ChinaReaperTank_Real": r"Data\INI\Object\China\Tank\Vehicles\Reaper.ini",
 "Tank_ChinaTankWarMaster": r"Data\INI\Object\China\Tank\Vehicles\WarMaster.ini",
}

# --------------------------------------------------------------------------
# Kwai Tank buildings -> 1.25x STOCK HP
# --------------------------------------------------------------------------
BUILDINGS = {
 "Tank_ChinaAirfield": r"Data\INI\Object\China\Tank\Buildings\Airfield.ini",
 "Tank_ChinaBarracks": r"Data\INI\Object\China\Tank\Buildings\Barracks.ini",
 "Tank_ChinaCommandCenter": r"Data\INI\Object\China\Tank\Buildings\CommandCenter.ini",
 "Tank_ChinaIndustrialPlant": r"Data\INI\Object\China\Tank\Buildings\IndustrialPlant.ini",
 "Tank_ChinaInternetCenter": r"Data\INI\Object\China\Tank\Buildings\InternetCenter.ini",
 "Tank_ChinaNuclearMissileLauncher": r"Data\INI\Object\China\Tank\Buildings\NuclearSilo.ini",
 "Tank_ChinaPowerPlant": r"Data\INI\Object\China\Tank\Buildings\PowerPlant.ini",
 "Tank_ChinaPropagandaCenter": r"Data\INI\Object\China\Tank\Buildings\PropagandaCenter.ini",
 "Tank_ChinaSupplyCenter": r"Data\INI\Object\China\Tank\Buildings\SupplyCenter.ini",
 "Tank_ChinaWarFactory": r"Data\INI\Object\China\Tank\Buildings\WarFactory.ini",
 "Tank_ChinaBunker": r"Data\INI\Object\China\Tank\Defences\Bunker.ini",
 "Tank_ChinaGattlingCannon": r"Data\INI\Object\China\Tank\Defences\GattlingCannon.ini",
 "Tank_ChinaSentryTower": r"Data\INI\Object\China\Tank\Defences\Ramjet Turret.ini",
}
BUILDING_FACTOR = 1.25

# --------------------------------------------------------------------------
# B. combat infantry -> -50% HP (name -> file).  Current HP read live; halved.
# --------------------------------------------------------------------------
INFANTRY_HP = {
 "ChinaInfantryRedguard": r"Data\INI\Object\China\Vanilla\Infantry\Redguard.ini",
 "ChinaInfantryTankHunter": r"Data\INI\Object\China\Vanilla\Infantry\TankHunter.ini",
 "ChinaInfantrySiegeSoldier": r"Data\INI\Object\China\Vanilla\Infantry\SiegeSoldier.ini",
 "Infa_ChinaInfantryRedguard": r"Data\INI\Object\China\Infantry\Infantry\RedGuard.ini",
 "Infa_ChinaInfantryTankHunter": r"Data\INI\Object\China\Infantry\Infantry\TankHunter.ini",
 "Infa_ChinaInfantrySiegeSoldier": r"Data\INI\Object\China\Infantry\Infantry\SiegeSoldier.ini",
 "Infa_ChinaInfantryMiniGunner": r"Data\INI\Object\China\Infantry\Infantry\MiniGunner.ini",
 "Squad_Infa_ChinaInfantryRedGuard": r"Data\INI\Object\China\Infantry\Infantry\RedGuardSquad.ini",
 "Squad_Infa_ChinaInfantryTankHunter": r"Data\INI\Object\China\Infantry\Infantry\TankHunterSquad.ini",
 "Squad_Infa_ChinaInfantryMiniGunner": r"Data\INI\Object\China\Infantry\Infantry\MinigunnerSquad.ini",
 "Nuke_ChinaInfantryRedguard": r"Data\INI\Object\China\Nuke\Infantry\RedGuard.ini",
 "Nuke_ChinaInfantryTankHunter": r"Data\INI\Object\China\Nuke\Infantry\TankHunter.ini",
 "Nuke_ChinaInfantrySiegeSoldier": r"Data\INI\Object\China\Nuke\Infantry\SiegeSoldier.ini",
 "Spec_ChinaInfantryRedguard": r"Data\INI\Object\China\SpecialWeapons\Infantry\RedGuard.ini",
 "Spec_ChinaInfantryTankHunter": r"Data\INI\Object\China\SpecialWeapons\Infantry\TankHunter.ini",
 "Spec_ChinaInfantryFlameThrower": r"Data\INI\Object\China\SpecialWeapons\Infantry\FlameThrower.ini",
 "Tank_ChinaInfantryPanzergrenadier": r"Data\INI\Object\China\Tank\Infantry\Panzergrenadier.ini",
 "Tank_ChinaInfantryShmelTrooper": r"Data\INI\Object\China\Tank\Infantry\RotrShmelTrooper.ini",
 "Tank_ChinaInfantrySharpshooter": r"Data\INI\Object\China\Tank\Infantry\Sharpshooter.ini",
}
INFANTRY_HP_FACTOR = 0.5

# --------------------------------------------------------------------------
# A3. w-economy's 32 China infantry cost/build objects (STOCK cost/time),
#     re-toned to 0.85x cost (round to $5) + 0.8x time (1.25x build speed).
#     (file, object, stock_cost, stock_time)  -- files carry current halved
#     values; we set absolute new values from stock so the anchor is exact.
# --------------------------------------------------------------------------
O = "Data\\INI\\Object\\"
INF_COST = [
 (O+r"China\Vanilla\Infantry\Redguard.ini", "ChinaInfantryRedguard", 300, 10.0),
 (O+r"China\Vanilla\Infantry\TankHunter.ini", "ChinaInfantryTankHunter", 300, 5.0),
 (O+r"China\Vanilla\Infantry\SiegeSoldier.ini", "ChinaInfantrySiegeSoldier", 600, 8.0),
 (O+r"China\Vanilla\Infantry\Hacker.ini", "ChinaInfantryHacker", 600, 13.0),
 (O+r"China\Vanilla\Infantry\BlackLotus.ini", "ChinaInfantryBlackLotus", 1500, 20.0),
 (O+r"China\Nuke\Infantry\RedGuard.ini", "Nuke_ChinaInfantryRedguard", 300, 12.0),
 (O+r"China\Nuke\Infantry\TankHunter.ini", "Nuke_ChinaInfantryTankHunter", 350, 7.0),
 (O+r"China\Nuke\Infantry\SiegeSoldier.ini", "Nuke_ChinaInfantrySiegeSoldier", 600, 8.0),
 (O+r"China\Nuke\Infantry\Hacker.ini", "Nuke_ChinaInfantryHacker", 600, 13.0),
 (O+r"China\Nuke\Infantry\BlackLotus.ini", "Nuke_ChinaInfantryBlackLotus", 1500, 20.0),
 (O+r"China\Infantry\Infantry\RedGuard.ini", "Infa_ChinaInfantryRedguard", 450, 14.0),
 (O+r"China\Infantry\Infantry\TankHunter.ini", "Infa_ChinaInfantryTankHunter", 350, 6.0),
 (O+r"China\Infantry\Infantry\MiniGunner.ini", "Infa_ChinaInfantryMiniGunner", 550, 14.0),
 (O+r"China\Infantry\Infantry\SiegeSoldier.ini", "Infa_ChinaInfantrySiegeSoldier", 600, 8.0),
 (O+r"China\Infantry\Infantry\Hacker.ini", "Infa_ChinaInfantryHacker", 700, 13.0),
 (O+r"China\Infantry\Infantry\BlackLotus.ini", "Infa_ChinaInfantryBlackLotus", 1500, 20.0),
 (O+r"China\Infantry\Infantry\RedGuardSquad.ini", "Infa_ChinaInfantryRedGuardSquadNexus", 2000, 25.0),
 (O+r"China\Infantry\Infantry\MinigunnerSquad.ini", "Infa_ChinaInfantryMinigunnerSquadNexus", 2000, 25.0),
 (O+r"China\Infantry\Infantry\TankHunterSquad.ini", "Infa_ChinaInfantryTankHunterSquadNexus", 2000, 25.0),
 (O+r"China\SpecialWeapons\Infantry\RedGuard.ini", "Spec_ChinaInfantryRedguard", 325, 10.0),
 (O+r"China\SpecialWeapons\Infantry\TankHunter.ini", "Spec_ChinaInfantryTankHunter", 300, 5.0),
 (O+r"China\SpecialWeapons\Infantry\FlameThrower.ini", "Spec_ChinaInfantryFlameThrower", 350, 8.0),
 (O+r"China\SpecialWeapons\Infantry\Hacker.ini", "Spec_ChinaInfantryHacker", 600, 13.0),
 (O+r"China\SpecialWeapons\Infantry\BlackLotus.ini", "Spec_ChinaInfantryBlackLotus", 1500, 20.0),
 (O+r"China\Tank\Infantry\RedGuard.ini", "Tank_ChinaInfantryRedguard", 400, 12.0),
 (O+r"China\Tank\Infantry\TankHunter.ini", "Tank_ChinaInfantryTankHunter", 375, 10.0),
 (O+r"China\Tank\Infantry\Hacker.ini", "Tank_ChinaInfantryHacker", 300, 13.0),
 (O+r"China\Tank\Infantry\BlackLotus.ini", "Tank_ChinaInfantryBlackLotus", 1500, 20.0),
 (O+r"China\Tank\Infantry\SiegeSoldier.ini", "Tank_ChinaInfantrySiegeSoldier", 600, 8.0),
 (O+r"China\Tank\Infantry\FlameTrooper.ini", "Tank_ChinaInfantryFlameThrower", 350, 8.0),
 (O+r"China\Tank\Infantry\MiniGunner.ini", "Tank_ChinaInfantryMiniGunner", 550, 14.0),
 (O+r"China\Tank\Infantry\Sharpshooter.ini", "Tank_ChinaInfantrySharpshooter", 1200, 30.0),
]
COST_FACTOR = 0.85     # 15% cheaper
TIME_FACTOR = 0.80     # 1.25x build speed

# Inferno Cannon HP -> toward stock (195); tiny functional edge
INFERNO = (O+r"China\Vanilla\Vehicles\InfernoCannon.ini", "ChinaVehicleInfernoCannon", 210)

# Extra weapon ranges reset to STOCK beyond china-tank-buff's set (derived at
# build time): Spec gattling AA (gattling-buff missed by ctb) + Nuke Cannon
# family (stat-tune inflated to 800). Values are read from base.
EXTRA_RANGE_WEAPONS = [
 "Spec_GattlingTankGunAir",
 "NukeCannonGun", "Nuke_NukeCannonGun",
 "NukeCannonNeutronWeapon", "Nuke_NukeCannonNeutronWeapon",
 "Nuke_NukeCannonSSNRWeapon",
]

WEAPON_INI = r"Data\INI\Weapon.ini"
CIVIL = r"Data\INI\Object\CivilianBuilding.ini"
GAMEDATA = r"Data\INI\GameData.ini"
AIDATA = r"Data\INI\Default\AIData.ini"

SUPPLY_OBJECTS = ["SupplyWarehouse", "SupplyDock", "SupplyDock_Var1",
                  "SupplyDock_Var2", "SupplyDock_Var3", "SupplyPile",
                  "SupplyPileSmall", "ToxinRepository"]
SUPPLY_BOXES = 100000

AIDATA_FIELDS = [  # (field, newval)  -- top-level AIData block, one each
 ("TeamSeconds", 5),
 ("Wealthy", 6000),
 ("Poor", 1500),
 ("StructuresWealthyRate", 3.0),
 ("TeamsWealthyRate", 3.0),
]


# --------------------------------------------------------------------------
def main():
    report = []
    owner = build_owner(SPE)

    # sort-position assertions -----------------------------------------------
    for d, dn in [(SPE, "SPE"), (SW, "SW")]:
        s = sorted(set(sorted_bigs(d)) | {OUT_NAME}, key=str.lower)
        i = s.index(OUT_NAME)
        assert i == len(s) - 1 or s[i + 1].lower() in ABOVE, \
            f"[{dn}] Rebalance not above all data layers: after us -> {s[i+1:]}"
        # must sort AFTER the highest data layer (EmperorTweaks) and BEFORE UI
        below_us = [x for x in s[:i] if x != OUT_NAME]
        assert below_us[-1].startswith("zzz-ZZZZZZZZZZZZZZZZZ0EmperorTweaks"), \
            f"[{dn}] unexpected top data layer: {below_us[-1]}"
        assert all(x.lower() in ABOVE for x in s[i + 1:]), f"[{dn}] non-UI above us"
    report.append("sort-position: Rebalance is the last DATA layer in both dirs "
                  "(above EmperorTweaks, below ControlBarPro/FXEnhance). OK")

    # collect edits per file --------------------------------------------------
    edits = {}   # relpath -> list of (kind, ...) applied later, for reporting
    files = {}   # relpath -> (source_text, source_arch)
    changes = {} # relpath -> list of human strings

    def load(relpath, from_base=False):
        if relpath in files:
            return files[relpath][0]
        if from_base:
            txt, a = base_file(SPE, relpath)
        else:
            key = relpath.lower()
            assert key in owner, f"no owner for {relpath}"
            a, rp = owner[key]
            txt = arch_files(SPE, a)[rp].decode("latin-1")
        files[relpath] = [txt, a]
        changes[relpath] = []
        return txt

    def store(relpath, txt):
        files[relpath][0] = txt

    # ---- A1/A2: tank HP -> stock -------------------------------------------
    for name, rel in TANK_FILES.items():
        txt = load(rel)
        bt, _ = base_file(SPE, rel)
        hp = get_field(bt, "Object", name, "MaxHealth")
        ih = get_field(bt, "Object", name, "InitialHealth")
        assert hp is not None
        cur = get_field(txt, "Object", name, "MaxHealth")
        txt, _ = set_field(txt, "Object", name, "MaxHealth", hp)
        if ih is not None:
            txt, _ = set_field(txt, "Object", name, "InitialHealth", ih)
        store(rel, txt)
        changes[rel].append(f"{name} HP {cur:g}->{hp:g}")

    # ---- A1/A2: weapon ranges -> stock -------------------------------------
    # derive china-tank-buff's touched-range weapon set = ctb Weapon.ini vs base
    ctb = arch_files(SPE, "zzx_ChinaTankBuff.big")[WEAPON_INI].decode("latin-1")
    basew, _ = base_file(SPE, WEAPON_INI)
    def wrange(txt, wn):
        try:
            s, e = _block_region(txt, "Weapon", wn)
        except SystemExit:
            return None
        m = re.search(r"(?mi)^\s*AttackRange\s*=\s*([0-9]+(?:\.[0-9]+)?)", txt[s:e])
        return float(m.group(1)) if m else None
    ctb_weapons = []
    for m in re.finditer(r"(?mi)^Weapon\s+(\S+)", ctb):
        wn = m.group(1)
        rb, rc = wrange(basew, wn), wrange(ctb, wn)
        if rb is not None and rc is not None and rb != rc:
            ctb_weapons.append(wn)
    reset_weapons = sorted(set(ctb_weapons) | set(EXTRA_RANGE_WEAPONS))
    assert len(ctb_weapons) >= 55, f"china-tank-buff weapon set too small: {len(ctb_weapons)}"
    # sanity: intentional nerfs must NOT be in the reset set
    for forbidden in ("HowitzerGun", "InfernoCannonGun", "InfernoCannonGunUpgraded",
                      "HEInfernoCannonGun"):
        assert forbidden not in reset_weapons, f"{forbidden} must stay nerfed"

    wtxt = load(WEAPON_INI)
    nrw = 0
    for wn in reset_weapons:
        stock = wrange(basew, wn)
        assert stock is not None, f"no base range for {wn}"
        cur = wrange(wtxt, wn)
        if cur is None:      # weapon not present in effective Weapon.ini
            continue
        if cur == stock:
            continue
        wtxt, _ = set_field(wtxt, "Weapon", wn, "AttackRange", stock, must=1)
        nrw += 1
        changes[WEAPON_INI].append(f"{wn} range {cur:g}->{stock:g}")
    store(WEAPON_INI, wtxt)
    report.append(f"weapon ranges reset to stock: {nrw} weapons "
                  f"({len(ctb_weapons)} china-tank-buff + {len(EXTRA_RANGE_WEAPONS)} artillery/AA)")

    # ---- A2: Kwai buildings 2x -> 1.25x stock ------------------------------
    for name, rel in BUILDINGS.items():
        txt = load(rel)
        bt, _ = base_file(SPE, rel)
        stock = get_field(bt, "Object", name, "MaxHealth")
        assert stock is not None
        new = int(round(stock * BUILDING_FACTOR))
        cur = get_field(txt, "Object", name, "MaxHealth")
        txt, _ = set_field(txt, "Object", name, "MaxHealth", new)
        if get_field(bt, "Object", name, "InitialHealth") is not None:
            txt, _ = set_field(txt, "Object", name, "InitialHealth", new)
        store(rel, txt)
        changes[rel].append(f"{name} HP {cur:g}->{new} (stock {stock:g} x1.25)")

    # ---- A2: Inferno Cannon HP --------------------------------------------
    rel, name, newhp = INFERNO
    txt = load(rel)
    cur = get_field(txt, "Object", name, "MaxHealth")
    txt, _ = set_field(txt, "Object", name, "MaxHealth", newhp)
    if get_field(txt, "Object", name, "InitialHealth") is not None:
        txt, _ = set_field(txt, "Object", name, "InitialHealth", newhp)
    store(rel, txt)
    changes[rel].append(f"{name} HP {cur:g}->{newhp}")

    # ---- B: infantry HP -50% ----------------------------------------------
    for name, rel in INFANTRY_HP.items():
        txt = load(rel)
        cur = get_field(txt, "Object", name, "MaxHealth")
        assert cur is not None, f"{name}: no MaxHealth (stub?)"
        new = int(round(cur * INFANTRY_HP_FACTOR))
        txt, _ = set_field(txt, "Object", name, "MaxHealth", new)
        if get_field(txt, "Object", name, "InitialHealth") is not None:
            txt, _ = set_field(txt, "Object", name, "InitialHealth", new)
        store(rel, txt)
        changes[rel].append(f"{name} HP {cur:g}->{new}")

    # ---- A3: infantry cost/build re-tone -----------------------------------
    for rel, name, sc, st in INF_COST:
        txt = load(rel)
        newc = round5(sc * COST_FACTOR)
        newt = round(st * TIME_FACTOR, 4)
        curc = get_field(txt, "Object", name, "BuildCost")
        txt, _ = set_field(txt, "Object", name, "BuildCost", newc)
        # BuildTime may be float; format compactly
        curt = get_field(txt, "Object", name, "BuildTime")
        txt, _ = set_field(txt, "Object", name, "BuildTime", float(newt))
        store(rel, txt)
        changes[rel].append(f"{name} cost {curc:g}->{newc}, time {curt:g}->{newt:g}")

    # ---- D1: inexhaustible supplies ----------------------------------------
    txt = load(CIVIL, from_base=True)
    for name in SUPPLY_OBJECTS:
        cur = get_field(txt, "Object", name, "StartingBoxes")
        txt, _ = set_field(txt, "Object", name, "StartingBoxes", SUPPLY_BOXES)
        changes[CIVIL].append(f"{name} StartingBoxes {cur:g}->{SUPPLY_BOXES}")
    store(CIVIL, txt)

    # ---- D2: global supply value + AI-only build/attack levers --------------
    txt = load(GAMEDATA, from_base=True)
    m = re.search(r"(?mi)^(\s*ValuePerSupplyBox\s*=\s*)(\d+)", txt)
    assert m and m.group(2) == "75"
    txt = txt[:m.start()] + m.group(1) + "90" + txt[m.end():]
    store(GAMEDATA, txt)
    changes[GAMEDATA].append("ValuePerSupplyBox 75->90 (global +20%)")

    txt = load(AIDATA)  # owner: zzyzy_NoAISuperweapons.big (superweapons stay off)
    for field, newv in AIDATA_FIELDS:
        nv = ("%g" % newv) if isinstance(newv, float) else str(newv)
        pat = re.compile(r"(?mi)^(\s*%s\s*=\s*)([0-9]+(?:\.[0-9]+)?)" % re.escape(field))
        cnt = [0]
        def repl(mm, nv=nv):
            cnt[0] += 1
            return mm.group(1) + nv
        txt = pat.sub(repl, txt, count=1)
        assert cnt[0] == 1, f"AIData {field}: {cnt[0]} matches"
        changes[AIDATA].append(f"{field} -> {nv}")
    store(AIDATA, txt)

    # ------------------------------------------------------------------------
    # SURVIVAL VERIFICATION: every shipped file differs from its winning source
    # ONLY on lines whose stripped key is an allowed stat field.
    # ------------------------------------------------------------------------
    ALLOWED = {"MaxHealth", "InitialHealth", "AttackRange", "BuildCost",
               "BuildTime", "StartingBoxes", "ValuePerSupplyBox", "TeamSeconds",
               "Wealthy", "Poor", "StructuresWealthyRate", "TeamsWealthyRate"}
    entries = []
    for rel, (txt, src_arch) in files.items():
        # original source bytes
        if src_arch in BASE_ARCHIVES:
            orig = base_file(SPE, rel)[0]
        else:
            a, rp = owner[rel.lower()]
            orig = arch_files(SPE, a)[rp].decode("latin-1")
        ol, nl = orig.split("\n"), txt.split("\n")
        assert len(ol) == len(nl), f"{rel}: line count changed {len(ol)}->{len(nl)}"
        diffs = [(i, ol[i], nl[i]) for i in range(len(ol)) if ol[i] != nl[i]]
        for i, a, b in diffs:
            key = a.strip().split("=")[0].strip()
            assert key in ALLOWED, f"{rel}:{i+1}: unexpected change on '{key}': {a!r}->{b!r}"
        assert diffs, f"{rel}: no changes (bug)"
        report.append(f"  {rel.split(chr(92))[-1]:32s} {len(diffs):3d} stat line(s) "
                      f"[src {src_arch}]  survival OK")
        entries.append(BigEntry(rel, txt.encode("latin-1")))

    # closure: no shipped edit renames/removes any identifier; ranges/HP that
    # go to stock still resolve (objects/weapons already existed). Assert the
    # weapons we reset still exist post-edit (round-trip check below covers it).

    # ------------------------------------------------------------------------
    # package + BIG round-trip byte-identity
    # ------------------------------------------------------------------------
    out_path = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_path)
    rt = {e.path: e.data for e in read_big(out_path)}
    for e in entries:
        assert rt[e.path] == e.data, f"round-trip mismatch: {e.path}"
    assert len(rt) == len(entries)
    report.append(f"BIG round-trip byte-identical: {len(entries)} files, "
                  f"{os.path.getsize(out_path)} bytes")

    # ------------------------------------------------------------------------
    # both-dir source parity: the file we based on is identical in the SW stack
    # ------------------------------------------------------------------------
    owner_sw = build_owner(SW)
    for rel, (txt, src_arch) in files.items():
        key = rel.lower()
        if src_arch in BASE_ARCHIVES:
            sw_src = base_file(SW, rel)[0]
            spe_src = base_file(SPE, rel)[0]
        else:
            assert key in owner_sw, f"[SW] no owner for {rel}"
            a, rp = owner_sw[key]
            sw_src = arch_files(SW, a)[rp].decode("latin-1")
            oa, orp = owner[key]
            spe_src = arch_files(SPE, oa)[orp].decode("latin-1")
        assert sw_src == spe_src, f"SPE/SW source divergence on {rel}; needs per-dir archive"
    report.append("SPE/SW source parity: every based-on file identical in both stacks; "
                  "one archive serves both dirs")

    # ------------------------------------------------------------------------
    # install to both dirs + post-install audit + md5 match
    # ------------------------------------------------------------------------
    md5 = hashlib.md5(open(out_path, "rb").read()).hexdigest()
    for d in (SPE, SW):
        shutil.copy2(out_path, os.path.join(d, OUT_NAME))
    for d in (SPE, SW):
        dp = os.path.join(d, OUT_NAME)
        assert os.path.exists(dp)
        assert hashlib.md5(open(dp, "rb").read()).hexdigest() == md5
        # post-install: our archive is the winner for every path it ships
        own2 = build_owner(d)   # excludes us & UI
        # rebuild including us to confirm nothing above claims our paths
        full = sorted([f for f in os.listdir(d) if f.lower().endswith(".big")], key=str.lower)
        for e in entries:
            claimants = [a for a in full if a.lower() not in ABOVE and a != OUT_NAME
                         and e.path in arch_files(d, a)]
            # ok as long as none sorting ABOVE us claims it
            above_claim = [a for a in full if a.lower() in ABOVE and e.path in arch_files(d, a)]
            assert not above_claim, f"[{os.path.basename(d)}] {e.path} claimed above us by {above_claim}"
    report.append(f"installed to BOTH mod dirs; md5={md5}; both dirs match; "
                  f"no archive above us claims any shipped path")

    # ------------------------------------------------------------------------
    print("=" * 78)
    print(f"BUILT {OUT_NAME}  ({len(entries)} files)")
    print("=" * 78)
    for r in report:
        print(r)
    print("\n---- CHANGE DETAIL (old->new) ----")
    for rel in sorted(changes):
        print(f"\n### {rel}")
        for c in changes[rel]:
            print(f"   {c}")


if __name__ == "__main__":
    main()
