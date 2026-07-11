#!/usr/bin/env python3
"""Build zzz-ZZZZZZZVehicleKit.big - infantry fire-out bays + coaxial machine
guns for Kwai's (China Tank General) vehicle roster.  ShockWave under
GeneralsX.  Two features:

FEATURE 1 - 2-SEAT FIRE-OUT INFANTRY BAYS (china-bunkers BattleMaster bay
idiom: Slots 2, DamagePercentToUnits 0%, INFANTRY only, forbid
AIRCRAFT/VEHICLE/BOAT, garrison sounds, PassengersAllowedToFire Yes):
  - Tank_ChinaTankGattling (Kwai Gattling Tank)
  - Tank_ChinaVehicleScoutCar (kwai-roster clone; vision deliberately
    untouched - a queued economy layer owns that)
  - ALL artillery Kwai builds, on the SHARED donor objects (spillover to
    every owner of the same object, pre-approved like the kwai-pdl layer):
      ChinaVehicleNukeLauncher      (Nuke Cannon,   + vanilla China + CINE)
      ChinaVehicleInfernoCannon     (Inferno Cannon,+ vanilla China + CINE)
      Spec_ChinaVehicleNukeLauncher (Hammer Cannon, + Leang)
      Spec_ChinaVehicleInfernoCannon(Buratino/TOS,  + Leang)
  MERGE RULE: an object has ONE contain module.  kwai-pdl already gave the
  Gattling + all 4 artillery a minimal HelixContain PDL-pod rider seat
  (Slots 1, PORTABLE_STRUCTURE) - that module is EXTENDED in place, not
  duplicated.  The PDL pod mounts into HelixContain's dedicated
  PORTABLE_STRUCTURE rider slot (HelixContain.cpp addToContain /
  isValidContainerFor: bypasses AllowInsideKindOf, consumes no seats, never
  shows on exit buttons), so both infantry seats stay free and the $500 PDL
  purchase CO-EXISTS with garrisoned infantry - asserted below.
  Command sets gain 2 contiguous exit cameos (slots 7-8) + Evacuate (12; 10
  on the Gattling whose 12 is taken).  The Scout Car's vanilla-shared
  ChinaVehicleBullfrogCommandSet is CLONED (kwai-pdl Dragon/Reaper
  precedent) so vanilla China's scout sees no bay buttons.

FEATURE 2 - COAXIAL MACHINE GUNS, reusing the PROVEN HITSCAN
ShwBattleMasterCoaxMGWeapon (battlemaster-coax layer; the weapon carries NO
ProjectileObject - the earlier projectile version fired visible ballistic
arcs - drift-guarded below).  Scheme after per-unit re-verification of the
PLAYER_UPGRADE weapon-set flag and weapon-slot occupancy (engine truth:
WEAPONSLOT_COUNT == 3, WeaponSet.h; WeaponSetUpgrade.cpp:56 hard-codes
WEAPONSET_PLAYER_UPGRADE - no other upgrade-driven weapon-set flag exists):

  Emperor  (Tank_ChinaTankEmperor)  INNATE, 'None' set only.  Its
    PLAYER_UPGRADE set is FULL (PRIMARY targeting dummy, SECONDARY cannon,
    TERTIARY Tank_GattlingBuildingGunAirDummy for manual anti-air) - the
    spec's "add to BOTH sets" is impossible without sacrificing manual AA
    targeting of the mounted gattling turret; once the $1200 gattling rider
    is bought the coax is superseded by it (documented deviation).
  WarMaster (Tank_ChinaTankWarMaster)  INNATE fallback: flag TAKEN - ERA
    research (Upgrade_TankLightArmor -> WeaponSetUpgrade ModuleTag_Armor_02)
    flips PLAYER_UPGRADE for the armor-plate draw states.  Its single
    WeaponSet (Conditions = PLAYER_UPGRADE, always selected: best-effort
    matching, SparseMatchFinder.h findBestInfoSlow) gains the TERTIARY coax.
  Overlord (ChinaTankOverlord, vanilla-shared)  INNATE fallback: flag TAKEN
    by the per-unit gattling-turret purchase (WeaponSetUpgrade
    ModuleTag_WeaponSetUpgrade01, Upgrade_ChinaOverlordGattlingCannon).
    TERTIARY free in BOTH sets -> coax in both; survives all turret choices.
    Spillover to every ChinaTankOverlord owner (pre-approved).
  Dragon (Tank_ChinaTankDragon)  NO COAX: flag TAKEN (Black Napalm) AND all
    3 slots full in BOTH sets (flame / firewall / napalm-puddle) - the
    fallback ladder is exhausted.  File not shipped.
  Command Tank (Tank_ChinaTankCommandTank)  NO COAX: flag FREE and TERTIARY
    free, BUT its APFSDS/HESH switch set carries ShareWeaponReloadTime = Yes
    and the engine propagates EVERY weapon's next-shot frame + status to ALL
    slots in the set (Weapon.cpp reloadWithBonus ~:1994, privateFireWeapon
    ~:2753, onWeaponBonusChange ~:2057).  A 65 ms coax would stamp
    ready-in-65ms over the cannons' 10 s cycle (massive DPS exploit) and its
    5 s clip reload would randomly jam them; an INNATE coax is equally
    affected, so the unit is skipped with evidence (asserted still true at
    build time so drift re-opens the decision).
  JS-7  SKIPPED per spec (has its own MG).
  => NO unit qualifies for the $300 purchasable OBJECT_UPGRADE idiom; no
  Upgrade/CommandButton/Generals.str changes ship at all.

  PreferredAgainst mechanics: preferred weapons all tie at HUGE_DAMAGE and
  ties go to the LOWEST slot (WeaponSet.cpp chooseBestWeaponForTarget
  ~:842/930) - so the Emperor cannon's 'PreferredAgainst = SECONDARY
  INFANTRY' and the Overlord cannon's '... PRIMARY INFANTRY' are MOVED to
  the TERTIARY coax, otherwise the coax would never be selected.  Fire-FX
  bones: none of the three hosts declares TERTIARY bones - the tracer FX
  falls back to the hull position (battlemaster-coax precedent accepted).

COAX x PDL COEXISTENCE (user requirement): the coax is weapon-set text, the
PDL pod is a contain-rider OCL - different mechanisms; NO ConflictsWith is
added anywhere and the pod carries no weapon-set machinery (asserted).

PACKAGING: zzz-ZZZZZZZVehicleKit.big - case-insensitively sorts AFTER
zzz-ZZZZZZZTTeslaCoil.big ('v' > 't' at char 12), BEFORE
zzz-ZZZZZZZVetInsignia.big ('veh' < 'vet') and BEFORE zzz_ControlBarPro*
('-' 0x2D < '_' 0x5F).  Installed to both mod dirs.  This becomes the LAST
INI layer.
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
OUT_NAME = "zzz-ZZZZZZZVehicleKit.big"
TAG = "zzz-ZZZZZZZVehicleKit"
# CHANGELOG (kwai-infantry v2 chain rebuild): kwai-infantry removed its ZHE
# Sharpshooter port; Upgrade.ini reverted to zzz-ZZZZZZZKwaiPDL.big.  Sources
# are now read only from archives sorting strictly below this one; w-economy
# (rebuilt after us) may claim paths we ship.
REBUILT_AFTER = {"zzz-zzzzzzzweconomy.big"}

CS_PATH = "Data\\INI\\CommandSet.ini"
VEH = "Data\\INI\\Object\\China\\Tank\\Vehicles\\"
VAN = "Data\\INI\\Object\\China\\Vanilla\\Vehicles\\"
SPC = "Data\\INI\\Object\\China\\SpecialWeapons\\Vehicles\\"
EMP_PATH = VEH + "Emperor.ini"
WM_PATH = VEH + "WarMaster.ini"
GAT_PATH = VEH + "GattlingTank.ini"
SC_PATH = VEH + "ScoutCar.ini"
OVL_PATH = VAN + "Overlord.ini"
NUKE_PATH = VAN + "NukeCannon.ini"
INF_PATH = VAN + "InfernoCannon.ini"
HAM_PATH = SPC + "HammerCannon.ini"
BUR_PATH = SPC + "Buratino.ini"

OWNERS = {
    CS_PATH: "zzz-ZZZZZZZTTeslaCoil.big",
    EMP_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    WM_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    GAT_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    NUKE_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    INF_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    HAM_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    BUR_PATH: "zzz-ZZZZZZZKwaiPDL.big",
    SC_PATH: "zzz-ZZZZZKwaiRoster.big",
    OVL_PATH: "zzx_ChinaTankBuff.big",
}

COAX = "ShwBattleMasterCoaxMGWeapon"
SC_SET = "Tank_ChinaVehicleScoutCarCommandSet"   # the ONLY new identifier
NEW_NAMES = [SC_SET]

EXIT7 = "  7  = Command_TransportExit ; %s: infantry bay seat 1" % TAG
EXIT8 = "  8  = Command_TransportExit ; %s: infantry bay seat 2" % TAG
EVAC = "Command_Evacuate ; %s" % TAG


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


def insert_slot(block, slot, command_text):
    """Insert '  <slot> = <command_text>' before the first numbered line
    with a higher slot (or before End).  Asserts the slot is free."""
    lines = block.split("\n")
    slots_here = {}
    for i, line in enumerate(lines):
        lm = re.match(r"\s*(\d+)\s*=", line)
        if lm:
            slots_here[int(lm.group(1))] = i
    assert slot not in slots_here, "slot %d occupied in %r" % (slot,
                                                               lines[0])
    at = None
    for s in sorted(slots_here):
        if s > slot:
            at = slots_here[s]
            break
    if at is None:  # append before the final End line
        at = len(lines) - 1
        while not re.match(r"End[ \t]*$", lines[at]):
            at -= 1
    lines.insert(at, "  %-2d = %s" % (slot, command_text))
    return "\n".join(lines)


def top_object_block(lf, name):
    m = re.search(r"(?m)^Object[ \t]+%s[ \t]*(;[^\n]*)?$" % re.escape(name),
                  lf)
    assert m, "object not found: " + name
    m2 = re.search(r"(?m)^End[ \t]*$", lf[m.start():])
    assert m2
    return lf[m.start():m.start() + m2.end()]


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

# identifier collision check across the whole effective INI space
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
print("new identifiers collision-free (%d names, %d effective INI files)"
      % (len(NEW_NAMES), len(seen)))

# ================================================== 2. re-verification of
# the per-unit coax scheme (the decisions below are only valid while these
# facts hold - drift fails the build and re-opens the decisions)
WS_RE = r"(?ms)^  WeaponSet[ \t]*\n.*?^  End[ \t]*\n"

emp_lf = to_lf(sources[EMP_PATH])
emp_sets = re.findall(WS_RE, emp_lf)
assert len(emp_sets) == 2
assert "Conditions        = None" in emp_sets[0]
assert "Conditions        = PLAYER_UPGRADE" in emp_sets[1]
# PLAYER_UPGRADE set is FULL: dummy + cannon + manual-AA dummy on TERTIARY
assert "Weapon            = PRIMARY Tank_OverlordTankGun_Dummy" in emp_sets[1]
assert "Weapon            = SECONDARY Tank_OverlordTankGun" in emp_sets[1]
assert ("Weapon            = TERTIARY Tank_GattlingBuildingGunAirDummy"
        in emp_sets[1]), "Emperor PLAYER_UPGRADE TERTIARY freed - coax " \
    "could go in both sets now"
assert "TERTIARY" not in emp_sets[0], "Emperor None TERTIARY taken"

wm_lf = to_lf(sources[WM_PATH])
wm_sets = re.findall(WS_RE, wm_lf)
assert len(wm_sets) == 1, "WarMaster gained a weapon set"
assert "Conditions = PLAYER_UPGRADE" in wm_sets[0]
assert "TERTIARY" not in wm_sets[0]
assert re.search(r"(?ms)Behavior = WeaponSetUpgrade ModuleTag_Armor_02\n"
                 r"\s*TriggeredBy = Upgrade_TankLightArmor", wm_lf), \
    "WarMaster PLAYER_UPGRADE no longer taken by ERA - purchasable idiom " \
    "may be possible now"

ovl_lf = to_lf(sources[OVL_PATH])
ovl = top_object_block(ovl_lf, "ChinaTankOverlord")
ovl_sets = re.findall(WS_RE, ovl)
assert len(ovl_sets) == 2, "Overlord weapon-set count drift"
assert "Conditions" not in ovl_sets[0].split(";")[0].split("\n")[1], \
    "first Overlord set is no longer the None set"
assert "Conditions        = PLAYER_UPGRADE" in ovl_sets[1]
for s in ovl_sets:
    assert not re.search(r"(?m)^\s*Weapon\s+=\s*TERTIARY", s), \
        "Overlord TERTIARY taken"
assert re.search(
    r"(?ms)Behavior = WeaponSetUpgrade ModuleTag_WeaponSetUpgrade01\n"
    r"\s*TriggeredBy = Upgrade_ChinaOverlordGattlingCannon", ovl), \
    "Overlord PLAYER_UPGRADE no longer taken by the gattling purchase"

# Dragon: flag taken + both sets full -> NO COAX (file not shipped)
drg_lf = to_lf(EFFECTIVE(VEH + "DragonTank.ini"))
drg_sets = re.findall(WS_RE, drg_lf)
assert len(drg_sets) == 2
for s in drg_sets:
    for slot in ("PRIMARY", "SECONDARY", "TERTIARY"):
        assert re.search(r"(?m)^\s*Weapon\s*=\s*%s\s" % slot, s), \
            "Dragon %s freed - coax may be possible now" % slot
assert re.search(r"(?ms)Behavior = WeaponSetUpgrade ModuleTag_05\n"
                 r"\s*TriggeredBy = Upgrade_ChinaBlackNapalm", drg_lf)

# Command Tank: flag+slot free BUT ShareWeaponReloadTime -> NO COAX
ct_lf = to_lf(EFFECTIVE(VEH + "CommandTank.ini"))
ct_sets = re.findall(WS_RE, ct_lf)
assert len(ct_sets) == 1
assert "ShareWeaponReloadTime = Yes" in ct_sets[0], \
    "Command Tank no longer shares reload time - the purchasable coax " \
    "(PLAYER_UPGRADE clone) is viable now, re-open the decision"
assert "WeaponSetUpgrade" not in ct_lf   # flag itself is (still) free
assert "TERTIARY" not in ct_sets[0]
# the 10 s cannon cycle that the 65 ms coax would corrupt
wpn_lf = to_lf(EFFECTIVE("Data\\INI\\Weapon.ini"))
m = re.search(r"(?ms)^Weapon Tank_ChinaCommandTankCannonAPFSDS\s*\n.*?^End",
              wpn_lf)
assert m and re.search(r"(?m)^\s*ClipSize\s*=\s*1\b", m.group(0))
assert re.search(r"(?m)^\s*ClipReloadTime\s*=\s*10000", m.group(0))
print("coax scheme re-verification OK (Emperor PU set full; WarMaster flag "
      "taken by ERA; Overlord flag taken by gattling, TERTIARY free x2; "
      "Dragon full+taken; Command Tank shared-reload blocker)")

# ---- the reused coax weapon: drift guard (must stay the PROVEN HITSCAN)
m = re.search(r"(?ms)^Weapon %s\s*\n.*?^End" % COAX, wpn_lf)
assert m, "coax weapon missing from effective Weapon.ini"
coax_block = m.group(0)
for needle in ("PrimaryDamage           = 20.0",
               "AttackRange             = 165.0",
               "DamageType              = SMALL_ARMS",
               "WeaponSpeed             = 999999.0",
               "FireFX                  = WeaponFX_GenericMachineGunFire",
               "FireSound               = BattleMasterMachineGunFire",
               "DelayBetweenShots       = 65",
               "ClipSize                = 30",
               "ClipReloadTime          = 5000"):
    assert needle in coax_block, "coax weapon drift: " + needle
coax_code = "\n".join(l.split(";")[0] for l in coax_block.split("\n"))
assert "ProjectileObject" not in coax_code, \
    "coax weapon regained a ProjectileObject (ballistic-arc bug) - do not " \
    "reuse it until battlemaster-coax is hitscan again"
print("coax weapon drift guard OK (hitscan %s reused, not redefined)" % COAX)

# ---- PDL pod carries no weapon-set machinery (coax x PDL coexistence)
pod_lf = to_lf(EFFECTIVE(VEH + "PDLPod.ini"))
assert pod_lf and "Object Tank_ChinaPDLPod" in pod_lf
for forbidden in ("WeaponSetUpgrade", "GrantUpgradeCreate", "ConflictsWith"):
    assert forbidden not in pod_lf, "PDL pod gained " + forbidden
ocl_lf = to_lf(EFFECTIVE("Data\\INI\\ObjectCreationList.ini"))
m = re.search(r"(?ms)^ObjectCreationList Tank_OCL_KwaiPDLPod\s*\n.*?^End",
              ocl_lf)
assert m and "ContainInsideSourceObject = Yes" in m.group(0)
print("PDL pod has no weapon-set side effects (coax + pod stack cleanly)")

# ================================================== 3. patches
patched = {}

# ---------------------------------------------------- 3a. CommandSet.ini
cs_src = sources[CS_PATH]
cs_eol = eol_of(cs_src)
cs = to_lf(cs_src)

BAY_SET_PLANS = [
    # (set name, pre-occupancy, evacuate slot)
    ("Tank_ChinaVehicleGattlingTankCommandSet",
     [9, 11, 12, 13, 14], 10),   # 12 = Command_GuardFlyingUnitsOnly
    ("ChinaVehicleNukeCannonCommandSet",
     [1, 2, 4, 6, 9, 11, 13, 14], 12),
    ("ChinaVehicleInfernoCannonCommandSet",
     [1, 2, 4, 9, 11, 13, 14], 12),
    ("ChinaVehicleInfernoCannonUpgradedCommandSet",
     [1, 2, 4, 9, 11, 13, 14], 12),
    ("ChinaVehicleHammerCannonCommandSet",
     [1, 2, 4, 6, 9, 11, 13, 14], 12),
    ("ChinaVehicleTOSCommandSet",
     [1, 2, 4, 9, 11, 13, 14], 12),
]
pre_sets = parse_sets(cs)
for name, occ, evac_slot in BAY_SET_PLANS:
    assert sorted(pre_sets[name]) == occ, \
        "occupancy drift in %s: %r" % (name, sorted(pre_sets[name]))
    old = get_set_block(cs, name)
    new = insert_slot(old, 7, EXIT7.split("= ", 1)[1])
    new = insert_slot(new, 8, EXIT8.split("= ", 1)[1])
    new = insert_slot(new, evac_slot, EVAC)
    cs = replace_exact(cs, old, new)

# the Bullfrog set is untouched (vanilla-shared); the Kwai Scout Car gets a
# clone with the bay buttons (kwai-pdl Dragon/Reaper clone precedent)
bull = pre_sets["ChinaVehicleBullfrogCommandSet"]
assert bull == {1: "Command_ChinaScoutCarAreaScan",
                2: "Command_ScoutCarTaunt",
                14: "Command_Stop"}, bull
SC_SET_APPENDIX = (
    "\n;;; %(tag)s: Kwai Scout Car set - clone of the vanilla-shared\n"
    ";;; ChinaVehicleBullfrogCommandSet (also used by vanilla China's scout,"
    " which has no\n"
    ";;; bay) + 2 bay exit cameos + Evacuate for the new 2-seat infantry"
    " bay.\n"
    "CommandSet %(set)s\n"
    "  1 = Command_ChinaScoutCarAreaScan\n"
    "  2 = Command_ScoutCarTaunt\n"
    "%(e7)s\n"
    "%(e8)s\n"
    "  12 = %(evac)s\n"
    "  14 = Command_Stop\n"
    "End\n" % {"tag": TAG, "set": SC_SET, "e7": EXIT7, "e8": EXIT8,
               "evac": EVAC})
cs = cs + SC_SET_APPENDIX
patched[CS_PATH] = from_lf(cs, cs_eol)

# ---------------------------------------------------- 3b. bay merges (5x)
BAY_OLD = (
    "  Behavior = HelixContain ModuleTag_KPDL_Bay01 ; zzz-ZZZZZZZKwaiPDL:"
    " rider seat for the PDL pod (BlackShark ECM-jammer idiom)\n"
    "    Slots                   = 1\n"
    "    DamagePercentToUnits    = 100%\n"
    "    AllowInsideKindOf       = PORTABLE_STRUCTURE\n"
    "    ForbidInsideKindOf      = AIRCRAFT BOAT\n"
    "    ExitDelay               = 100\n"
    "    NumberOfExitPaths       = 1\n"
    "    PassengersAllowedToFire = No\n"
    "  End\n")
BAY_NEW = (
    "  ; " + TAG + ": the kwai-pdl PDL rider seat below is EXTENDED into a"
    " 2-seat\n"
    "  ; fire-out infantry bay (china-bunkers BattleMaster bay idiom).  An"
    " object has\n"
    "  ; ONE contain module, so the pod seat and the infantry bay share it:"
    " the PDL pod\n"
    "  ; mounts into HelixContain's dedicated PORTABLE_STRUCTURE rider slot\n"
    "  ; (HelixContain.cpp addToContain/isValidContainerFor - bypasses"
    " AllowInsideKindOf\n"
    "  ; and the Slots count, never shows on exit buttons), so both seats"
    " stay free for\n"
    "  ; infantry and the $500 PDL purchase co-exists with garrisoned"
    " passengers.\n"
    "  Behavior = HelixContain ModuleTag_KPDL_Bay01 ; zzz-ZZZZZZZKwaiPDL:"
    " rider seat for the PDL pod (BlackShark ECM-jammer idiom)\n"
    "    Slots                   = 2 ; " + TAG + ": was 1\n"
    "    DamagePercentToUnits    = 0% ; " + TAG + ": was 100%\n"
    "    AllowInsideKindOf       = INFANTRY ; " + TAG + ": was"
    " PORTABLE_STRUCTURE (the pod uses the rider slot, not a seat)\n"
    "    ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT ; " + TAG + ":"
    " +VEHICLE (china-bunkers bay convention)\n"
    "    EnterSound              = GarrisonEnter ; " + TAG + "\n"
    "    ExitSound               = GarrisonExit ; " + TAG + "\n"
    "    ExitDelay               = 100\n"
    "    NumberOfExitPaths       = 1\n"
    "    PassengersAllowedToFire = Yes ; " + TAG + ": fire-out bay (was No)\n"
    "  End\n")

for path in (GAT_PATH, NUKE_PATH, INF_PATH, HAM_PATH, BUR_PATH):
    src = sources[path]
    eol = eol_of(src)
    lf = replace_exact(to_lf(src), BAY_OLD, BAY_NEW)
    patched[path] = from_lf(lf, eol)

# ---------------------------------------------------- 3c. Scout Car
sc_src = sources[SC_PATH]
sc_eol = eol_of(sc_src)
sc = to_lf(sc_src)
sc = replace_exact(
    sc, "  CommandSet = ChinaVehicleBullfrogCommandSet",
    "  CommandSet = " + SC_SET + " ; " + TAG + ": clone with bay exit"
    " buttons (the vanilla set is shared with vanilla China's scout)")
SC_BAY = (
    "\n  Behavior = HelixContain ModuleTag_VKitBay01 ; " + TAG + ": 2-seat"
    " fire-out infantry bay (china-bunkers BattleMaster bay idiom)\n"
    "    Slots                   = 2\n"
    "    DamagePercentToUnits    = 0%\n"
    "    AllowInsideKindOf       = INFANTRY\n"
    "    ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT\n"
    "    EnterSound              = GarrisonEnter\n"
    "    ExitSound               = GarrisonExit\n"
    "    ExitDelay               = 100\n"
    "    NumberOfExitPaths       = 1\n"
    "    PassengersAllowedToFire = Yes\n"
    "  End\n")
SC_ANCHOR = ("  Behavior = PhysicsBehavior ModuleTag_05\n"
             "    Mass = 30.0\n"
             "  End\n")
sc = replace_exact(sc, SC_ANCHOR, SC_ANCHOR + SC_BAY)
# vision must NOT change (queued economy layer owns it)
assert "VisionRange     = 450" in sc and "ShroudClearingRange = 500" in sc
patched[SC_PATH] = from_lf(sc, sc_eol)

# ---------------------------------------------------- 3d. Emperor coax
emp_eol = eol_of(sources[EMP_PATH])
EMP_NONE_OLD = (
    "  WeaponSet\n"
    "    Conditions        = None\n"
    "    \n"
    "    Weapon            = PRIMARY Tank_OverlordTankGun_Dummy\n"
    "    AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    PreferredAgainst  = PRIMARY UNATTACKABLE\n"
    "\n"
    "    Weapon            = SECONDARY Tank_OverlordTankGun\n"
    "    AutoChooseSources = SECONDARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    PreferredAgainst  = SECONDARY INFANTRY\n"
    "  End\n")
EMP_NONE_NEW = (
    "  WeaponSet\n"
    "    Conditions        = None\n"
    "    \n"
    "    Weapon            = PRIMARY Tank_OverlordTankGun_Dummy\n"
    "    AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    PreferredAgainst  = PRIMARY UNATTACKABLE\n"
    "\n"
    "    Weapon            = SECONDARY Tank_OverlordTankGun\n"
    "    AutoChooseSources = SECONDARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    ; " + TAG + ": the cannon's 'PreferredAgainst = SECONDARY INFANTRY'"
    " moved to the\n"
    "    ; TERTIARY coax - preferred weapons all tie at HUGE_DAMAGE and the"
    " tie goes to\n"
    "    ; the lowest slot (WeaponSet.cpp chooseBestWeaponForTarget), so"
    " keeping it on\n"
    "    ; the cannon would leave the coax permanently unselected.\n"
    "\n"
    "    Weapon            = TERTIARY " + COAX + " ; " + TAG + ": innate"
    " coaxial MG (battlemaster-coax hitscan weapon, reused).  NOT in the"
    " PLAYER_UPGRADE set: that set's TERTIARY is the manual anti-air dummy"
    " for the mounted gattling turret (all 3 slots full) - once the gattling"
    " rider is bought it supersedes the coax as the anti-infantry weapon.\n"
    "    PreferredAgainst  = TERTIARY INFANTRY\n"
    "  End\n")
patched[EMP_PATH] = from_lf(replace_exact(emp_lf, EMP_NONE_OLD, EMP_NONE_NEW),
                            emp_eol)

# ---------------------------------------------------- 3e. WarMaster coax
wm_eol = eol_of(sources[WM_PATH])
WM_OLD = (
    "  WeaponSet\n"
    "    Conditions = PLAYER_UPGRADE \n"
    "    Weapon = PRIMARY Tank_WarMasterTankGun\n"
    "    Weapon = SECONDARY Tank_NapalmRocketPod\n"
    "  End\n")
WM_NEW = (
    "  WeaponSet\n"
    "    Conditions = PLAYER_UPGRADE \n"
    "    Weapon = PRIMARY Tank_WarMasterTankGun\n"
    "    Weapon = SECONDARY Tank_NapalmRocketPod\n"
    "    ; " + TAG + ": INNATE coaxial MG (battlemaster-coax hitscan weapon,"
    " reused).\n"
    "    ; The $300 purchasable idiom needs the PLAYER_UPGRADE weapon-set"
    " flag, but on\n"
    "    ; the WarMaster it is TAKEN: ERA research (Upgrade_TankLightArmor"
    " ->\n"
    "    ; WeaponSetUpgrade ModuleTag_Armor_02) flips it for the"
    " WEAPONSET_PLAYER_UPGRADE\n"
    "    ; armor-plate draw states.  This is the object's ONLY WeaponSet -"
    " best-effort\n"
    "    ; set matching selects it whether or not the flag is set, so the"
    " coax works\n"
    "    ; from build time.\n"
    "    Weapon = TERTIARY " + COAX + " ; " + TAG + "\n"
    "    PreferredAgainst = TERTIARY INFANTRY ; " + TAG + ": auto-selected"
    " vs infantry\n"
    "  End\n")
patched[WM_PATH] = from_lf(replace_exact(wm_lf, WM_OLD, WM_NEW), wm_eol)

# ---------------------------------------------------- 3f. Overlord coax
ovl_eol = eol_of(sources[OVL_PATH])
OVL_NONE_OLD = (
    "  WeaponSet\n"
    "  \n"
    "    ; Weapon            = PRIMARY OverlordTankGun_Dummy\n"
    "    ; AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    ; PreferredAgainst  = PRIMARY INFANTRY\n"
    "\n"
    "    Weapon            = PRIMARY OverlordTankGun\n"
    "    AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    PreferredAgainst  = PRIMARY INFANTRY\n"
    "    \n"
    "  End\n")
OVL_MOVED_COMMENT = (
    "    ; " + TAG + ": 'PreferredAgainst = PRIMARY INFANTRY' moved to the"
    " TERTIARY coax\n"
    "    ; (preferred weapons tie at HUGE_DAMAGE; the tie goes to the lowest"
    " slot, which\n"
    "    ; would leave the coax permanently unselected).\n")
OVL_COAX_LINES = (
    "    Weapon            = TERTIARY " + COAX + " ; " + TAG + ": innate"
    " coaxial MG (battlemaster-coax hitscan weapon, reused).  INNATE because"
    " the PLAYER_UPGRADE flag is taken by the per-unit gattling-turret"
    " purchase; vanilla-shared object - spillover to every ChinaTankOverlord"
    " owner, pre-approved.\n"
    "    PreferredAgainst  = TERTIARY INFANTRY\n")
OVL_NONE_NEW = (
    "  WeaponSet\n"
    "  \n"
    "    ; Weapon            = PRIMARY OverlordTankGun_Dummy\n"
    "    ; AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    ; PreferredAgainst  = PRIMARY INFANTRY\n"
    "\n"
    "    Weapon            = PRIMARY OverlordTankGun\n"
    "    AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    + OVL_MOVED_COMMENT +
    "\n"
    + OVL_COAX_LINES +
    "    \n"
    "  End\n")
OVL_PU_OLD = (
    "  WeaponSet  \n"
    "    Conditions        = PLAYER_UPGRADE\n"
    "    \n"
    "    ; Weapon            = PRIMARY OverlordTankGun_Dummy\n"
    "    ; AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    ; PreferredAgainst  = PRIMARY INFANTRY\n"
    "\n"
    "    Weapon            = PRIMARY OverlordTankGun\n"
    "    AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    PreferredAgainst  = PRIMARY INFANTRY\n"
    "\n"
    "    Weapon            = SECONDARY GattlingBuildingGunAirDummy ;Dummy"
    " weapon that allows manual targeting of air units outside range\n"
    "    PreferredAgainst  = SECONDARY AIRCRAFT\n"
    "\n"
    "  End\n")
OVL_PU_NEW = (
    "  WeaponSet  \n"
    "    Conditions        = PLAYER_UPGRADE\n"
    "    \n"
    "    ; Weapon            = PRIMARY OverlordTankGun_Dummy\n"
    "    ; AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    "    ; PreferredAgainst  = PRIMARY INFANTRY\n"
    "\n"
    "    Weapon            = PRIMARY OverlordTankGun\n"
    "    AutoChooseSources = PRIMARY FROM_PLAYER FROM_AI FROM_SCRIPT\n"
    + OVL_MOVED_COMMENT +
    "\n"
    "    Weapon            = SECONDARY GattlingBuildingGunAirDummy ;Dummy"
    " weapon that allows manual targeting of air units outside range\n"
    "    PreferredAgainst  = SECONDARY AIRCRAFT\n"
    "\n"
    + OVL_COAX_LINES +
    "\n"
    "  End\n")
ovl_new = replace_exact(ovl_lf, OVL_NONE_OLD, OVL_NONE_NEW)
ovl_new = replace_exact(ovl_new, OVL_PU_OLD, OVL_PU_NEW)
patched[OVL_PATH] = from_lf(ovl_new, ovl_eol)

# ================================================== 4. verification
# ---- CommandSet.ini diff audit: exactly 18 inserted lines + 1 appended set
tail_i = patched[CS_PATH].index(from_lf(";;; " + TAG, cs_eol))
base_region = to_lf(patched[CS_PATH][:tail_i])
diff = unified(to_lf(cs_src), base_region)
added = Counter(l[1:] for l in diff if l.startswith("+"))
removed = Counter(l[1:] for l in diff if l.startswith("-"))
assert removed == Counter(), removed
expect = Counter({EXIT7: 6, EXIT8: 6, "  12 = " + EVAC: 5,
                  "  10 = " + EVAC: 1, "": 1})
assert added == expect, (added, expect)
tail = to_lf(patched[CS_PATH][tail_i:])
assert tail.count("\nCommandSet ") == 1 and ("CommandSet %s\n" % SC_SET) in tail
print("CommandSet.ini diff audit OK (6 sets x [exits 7-8 + Evacuate], "
      "1 cloned set appended, nothing removed)")

# ---- per-file diff audits (exact added/removed line multisets = the
#      strongest sibling-survival guarantee for the object files)
def audit(path, exp_removed, exp_added):
    d = unified(to_lf(sources[path]), to_lf(patched[path]))
    a = Counter(l[1:] for l in d if l.startswith("+"))
    r = Counter(l[1:] for l in d if l.startswith("-"))
    assert r == Counter(exp_removed), (path, r.items())
    assert a == Counter(exp_added), (path, a.items())


def expected_delta(old, new):
    o, n = Counter(old.split("\n")[:-1]), Counter(new.split("\n")[:-1])
    return +(o - n), +(n - o)   # (removed, added)


bay_removed, bay_added = expected_delta(BAY_OLD, BAY_NEW)
for path in (GAT_PATH, NUKE_PATH, INF_PATH, HAM_PATH, BUR_PATH):
    audit(path, bay_removed, bay_added)
audit(EMP_PATH, *expected_delta(EMP_NONE_OLD, EMP_NONE_NEW))
audit(WM_PATH, *expected_delta(WM_OLD, WM_NEW))
ovl_rm = Counter(OVL_NONE_OLD.split("\n")[:-1]) \
    + Counter(OVL_PU_OLD.split("\n")[:-1]) \
    - Counter(OVL_NONE_NEW.split("\n")[:-1]) \
    - Counter(OVL_PU_NEW.split("\n")[:-1])
ovl_ad = Counter(OVL_NONE_NEW.split("\n")[:-1]) \
    + Counter(OVL_PU_NEW.split("\n")[:-1]) \
    - Counter(OVL_NONE_OLD.split("\n")[:-1]) \
    - Counter(OVL_PU_OLD.split("\n")[:-1])
audit(OVL_PATH, +ovl_rm, +ovl_ad)
audit(SC_PATH,
      ["  CommandSet = ChinaVehicleBullfrogCommandSet"],
      ["  CommandSet = " + SC_SET + " ; " + TAG + ": clone with bay exit"
       " buttons (the vanilla set is shared with vanilla China's scout)"]
      + SC_BAY.split("\n")[:-1])
print("object-file diff audits OK (every added/removed line accounted for; "
      "all sibling hunks byte-survive)")

# ---- no ConflictsWith anywhere in our additions (coax x PDL coexistence)
for path in patched:
    d = unified(to_lf(sources.get(path, "")), to_lf(patched[path]))
    for l in d:
        if l.startswith("+"):
            assert "ConflictsWith" not in l, (path, l)
print("no ConflictsWith added anywhere (coax + PDL pod are co-purchasable)")

# ---- block-balance deltas
for path, delta in ((CS_PATH, 1), (GAT_PATH, 0), (NUKE_PATH, 0),
                    (INF_PATH, 0), (HAM_PATH, 0), (BUR_PATH, 0),
                    (EMP_PATH, 0), (WM_PATH, 0), (OVL_PATH, 0),
                    (SC_PATH, 1)):
    d = end_lines(to_lf(patched[path])) - end_lines(to_lf(sources[path]))
    assert d == delta, (path, d, delta)
print("block-balance deltas OK")

# ---- content asserts on the patched texts
for path in (GAT_PATH, NUKE_PATH, INF_PATH, HAM_PATH, BUR_PATH, SC_PATH):
    lf = to_lf(patched[path])
    m = re.search(r"(?ms)^  Behavior = HelixContain.*?^  End", lf)
    assert m, path
    bay = m.group(0)
    for needle in ("Slots                   = 2",
                   "DamagePercentToUnits    = 0%",
                   "AllowInsideKindOf       = INFANTRY",
                   "ForbidInsideKindOf      = AIRCRAFT VEHICLE BOAT",
                   "EnterSound              = GarrisonEnter",
                   "ExitSound               = GarrisonExit",
                   "PassengersAllowedToFire = Yes"):
        assert needle in bay, (path, needle)
    assert lf.count("Behavior = HelixContain") == 1, path  # ONE contain
    if path != SC_PATH:  # PDL mount survives next to the merged bay
        assert "UpgradeObject = Tank_OCL_KwaiPDLPod" in lf, path
for path, n_coax in ((EMP_PATH, 1), (WM_PATH, 1), (OVL_PATH, 2)):
    lf = to_lf(patched[path])
    hits = re.findall(r"(?m)^\s*Weapon\s*=\s*TERTIARY\s+%s\b" % COAX, lf)
    assert len(hits) == n_coax, (path, hits)
    prefs = re.findall(r"(?m)^\s*PreferredAgainst\s*=\s*TERTIARY\s+INFANTRY",
                       lf)
    assert len(prefs) == n_coax, (path, prefs)
    # the moved preference is GONE from the cannons (uncommented lines only)
    code = "\n".join(l.split(";")[0] for l in lf.split("\n"))
    if path == EMP_PATH:
        none_set = re.findall(WS_RE, lf)[0]
        none_code = "\n".join(l.split(";")[0] for l in none_set.split("\n"))
        assert "Conditions        = None" in none_set
        assert "PreferredAgainst  = SECONDARY INFANTRY" not in none_code
        # PLAYER_UPGRADE set byte-identical (air dummy + its INFANTRY
        # preference intact - that set has no coax)
        assert emp_sets[1] in lf
    if path == OVL_PATH:
        assert not re.search(r"(?m)^\s*PreferredAgainst\s*=\s*PRIMARY"
                             r"\s+INFANTRY", code)
        assert "PreferredAgainst  = SECONDARY AIRCRAFT" in lf
# Emperor bay untouched at 8 seats, Shtora + prop + PDL exclusivity intact
emp_new = to_lf(patched[EMP_PATH])
for needle in ("Slots                   = 8",
               "Behavior = FireWeaponWhenDamagedBehavior ModuleTag_ShtoraAuto01",
               "Behavior        = PropagandaTowerBehavior ModulePropaganda_15",
               "ConflictsWith = Tank_Upgrade_KwaiPDL",
               "ConflictsWith = Upgrade_ChinaOverlordGattlingCannon",
               "CommandSet  = Tank_ChinaTankEmperorPDLCommandSet",
               "CommandSet  = Tank_ChinaTankEmperorGattlingCommandSet"):
    assert needle in emp_new, needle
print("patched-content asserts OK (bays merged 1-per-object, PDL mounts "
      "survive, coax slots + moved preferences, Emperor modules intact)")

# ---- cross-reference closure (referenced identifiers resolve effectively)
cb_lf = to_lf(EFFECTIVE("Data\\INI\\CommandButton.ini"))
snd_lf = to_lf(EFFECTIVE("Data\\INI\\SoundEffects.ini"))
new_sets = parse_sets(to_lf(patched[CS_PATH]))
for name, _, _ in BAY_SET_PLANS:
    for slot, btn in new_sets[name].items():
        assert re.search(r"(?m)^CommandButton\s+%s\b" % re.escape(btn),
                         cb_lf), (name, slot, btn)
for slot, btn in new_sets[SC_SET].items():
    assert re.search(r"(?m)^CommandButton\s+%s\b" % re.escape(btn), cb_lf), \
        (SC_SET, slot, btn)
for ev in ("GarrisonEnter", "GarrisonExit"):
    assert re.search(r"(?m)^AudioEvent\s+%s\s*$" % ev, snd_lf), ev
# hosts reference sets that exist; coax weapon exists (asserted above)
assert SC_SET in new_sets
print("cross-reference closure OK (every slot of every touched set resolves "
      "to a CommandButton; garrison sounds + coax weapon exist)")


# ---- sibling survival on the shipped CommandSet.ini (and installed later)
def verify_survival(cs_text, label=""):
    lf = to_lf(cs_text)
    sets = parse_sets(lf)
    dz1 = sets["Tank_ChinaDozerCommandSet"]
    assert dz1[9] == "Tank_Command_ConstructChinaGattlingCannon"
    assert dz1[13] == "Command_ChinaButtonCommandSetOneDown"      # kwai-bunkers
    dz2 = sets["Tank_ChinaDozerCommandSet_Down"]
    assert dz2 == {1: "Tank_Command_ConstructChinaIndustrialPlant",
                   7: "Tank_Command_ConstructChinaBunker",
                   8: "Tank_Command_ConstructChinaHackerBunker",
                   9: "Tank_Command_ConstructChinaTeslaCoil",     # tesla-coil
                   13: "Command_ChinaButtonCommandSetOneUp",
                   14: "Command_DisarmMinesAtPosition"}, dz2
    assert sets["Tank_ChinaTeslaCoilCommandSet"] == \
        {12: "Command_Stop", 14: "Command_Sell"}                  # tesla-coil
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
    assert emp[12] == "Command_Evacuate"
    assert sets["Tank_ChinaTankEmperorPDLCommandSet"][11] == \
        "Command_AttackMove"                                      # kwai-pdl
    assert 10 not in sets["Tank_ChinaTankEmperorPDLCommandSet"]
    assert 9 not in sets["Tank_ChinaTankEmperorGattlingCommandSet"]
    for n in ("Tank_ChinaTankDragonCommandSet",
              "Tank_ChinaTankDragonUpgradedCommandSet"):          # kwai-pdl
        assert sets[n][9] == "Tank_Command_UpgradeKwaiPDL"
        assert 7 not in sets[n] and 8 not in sets[n]  # Dragon has NO bay
    ct = sets["Tank_ChinaVehicleCommandTruckCommandSet"]          # chaos
    assert ct[1] == "Command_CommandTankAPFSDSShells"
    assert ct[3] == "Command_CommandTankHESHShells"
    assert ct[9] == "Tank_Command_UpgradeKwaiPDL"
    assert 7 not in ct and 8 not in ct            # Command Tank has NO bay
    pc_sets = {n for n in sets if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc_sets) == 50, len(pc_sets)                       # doctrine+
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):          # kwai-uav
        ic = sets["Tank_ChinaInternetCenterCommandSet" + v]
        assert ic[7] == "Tank_Command_UpgradeKwaiUAVProgram"
        assert ic[8] == "Tank_Command_KwaiUAVDeploy"
    assert "Tank_ChinaHackerBunkerCommandSet" in sets             # kwai-bunkers
    gat_def = sets["Tank_ChinaGattlingCannonCommandSet"]
    assert gat_def == {12: "Command_Stop", 13: "Command_UpgradeChinaMines",
                       14: "Command_Sell"}, gat_def
    assert lf.count("= Command_Evacuate") >= 60                   # garrisons
    # untouched vanilla-shared sets stay byte-frozen
    assert sets["ChinaVehicleBullfrogCommandSet"] == \
        {1: "Command_ChinaScoutCarAreaScan", 2: "Command_ScoutCarTaunt",
         14: "Command_Stop"}
    for n in ("ChinaTankDragonCommandSet", "GenericCommandSet",
              "ChinaTankOverlordDefaultCommandSet",
              "Nuke_ChinaVehicleNukeCannonCommandSet"):
        assert n in sets, n
        assert "Command_TransportExit" not in sets[n].values(), n
        assert "Command_Evacuate" not in sets[n].values(), n
    # our modified sets: exact expected layouts
    assert new_sets_expected == {n: sets[n] for n in new_sets_expected}, \
        "modified-set layout drift"
    print("  sibling survival OK" + (" (%s)" % label if label else ""))


new_sets_expected = {
    "Tank_ChinaVehicleGattlingTankCommandSet": {
        7: "Command_TransportExit", 8: "Command_TransportExit",
        9: "Tank_Command_UpgradeKwaiPDL", 10: "Command_Evacuate",
        11: "Command_AttackMove", 12: "Command_GuardFlyingUnitsOnly",
        13: "Command_Guard", 14: "Command_Stop"},
    "ChinaVehicleNukeCannonCommandSet": {
        1: "Command_FireNukeCannon", 2: "Command_ChinaNukeWarhead",
        4: "Command_ChinaNeutronWarhead", 6: "Command_NukeCannonHoldFireMode",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        9: "Tank_Command_UpgradeKwaiPDL", 11: "Command_AttackMove",
        12: "Command_Evacuate", 13: "Command_Guard", 14: "Command_Stop"},
    "ChinaVehicleInfernoCannonCommandSet": {
        1: "Command_ChinaInfernoCannonGroundAttack",
        2: "Command_ChinaIfernoNapalmWarhead",
        4: "Command_ChinaIfernoHEWarhead",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        9: "Tank_Command_UpgradeKwaiPDL", 11: "Command_AttackMove",
        12: "Command_Evacuate", 13: "Command_Guard", 14: "Command_Stop"},
    "ChinaVehicleInfernoCannonUpgradedCommandSet": {
        1: "Command_ChinaInfernoCannonGroundAttack",
        2: "Command_ChinaIfernoBlackNapalmWarhead",
        4: "Command_ChinaIfernoHEWarhead",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        9: "Tank_Command_UpgradeKwaiPDL", 11: "Command_AttackMove",
        12: "Command_Evacuate", 13: "Command_Guard", 14: "Command_Stop"},
    "ChinaVehicleHammerCannonCommandSet": {
        1: "Command_HammerCannonGroundAttack",
        2: "Command_ChinaHammerCannonHEShells",
        4: "Command_ChinaHammerCannonSeismicShells",
        6: "Command_NukeCannonHoldFireMode",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        9: "Tank_Command_UpgradeKwaiPDL", 11: "Command_AttackMove",
        12: "Command_Evacuate", 13: "Command_Guard", 14: "Command_Stop"},
    "ChinaVehicleTOSCommandSet": {
        1: "Command_ChinaTOSGroundAttack",
        2: "Command_GenericArtilleryFreeFireMode",
        4: "Command_GenericArtilleryFreeHoldMode",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        9: "Tank_Command_UpgradeKwaiPDL", 11: "Command_AttackMove",
        12: "Command_Evacuate", 13: "Command_Guard", 14: "Command_Stop"},
    SC_SET: {
        1: "Command_ChinaScoutCarAreaScan", 2: "Command_ScoutCarTaunt",
        7: "Command_TransportExit", 8: "Command_TransportExit",
        12: "Command_Evacuate", 14: "Command_Stop"},
}
verify_survival(patched[CS_PATH], "shipped")

# ================================================== 5. package + install
SHIPPED = sorted(patched)
entries = [BigEntry(p, patched[p].encode("latin-1")) for p in SHIPPED]
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
    assert listing[i - 1].lower() == "zzz-zzzzzzztteslacoil.big", listing
    assert listing[i + 1].lower() == "zzz-zzzzzzzvetinsignia.big", listing
    # nothing that sorts after us may claim any path we ship
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        if later.lower() in REBUILT_AFTER:
            continue  # documented: rebuilt after us, may claim shared files
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, (d, later, e.path)
    cbp = [f for f in listing if f.lower().startswith("zzz_controlbarpro")]
    assert cbp and all(listing.index(c) > i for c in cbp), listing
    print("sort order OK in %s: %s < %s < %s (later archives claim none of "
          "our paths, incl. VetInsignia)" % (d, listing[i - 1], OUT_NAME,
                                             listing[i + 1]))

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
                    "installed " + d)
    for p, needle in ((EMP_PATH, "Weapon            = TERTIARY " + COAX),
                      (WM_PATH, "Weapon = TERTIARY " + COAX),
                      (OVL_PATH, "Weapon            = TERTIARY " + COAX),
                      (GAT_PATH, "PassengersAllowedToFire = Yes"),
                      (SC_PATH, "ModuleTag_VKitBay01")):
        assert needle in find_entry(back, p).data.decode("latin-1"), (d, p)
    print("installed + re-read OK:", dst)

# ---- post-install effective-space audit (both dirs): our archive owns all
# 10 shipped paths; the sibling-owned paths we did NOT touch keep their
# owners; the skipped units' files are untouched
for d in (SPE_DIR, SHW_DIR):
    # REBUILT_AFTER layers may hold stale copies of our shared files until
    # their own rebuild (next in the chain) - audit the space below them
    arcs = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")
                   and f.lower() not in REBUILT_AFTER),
                  key=str.lower, reverse=True)
    def eff2(path, _arcs=arcs, _d=d):
        want = path.lower()
        for a in _arcs:
            for e in read_big(os.path.join(_d, a)):
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        return None, None
    for p in SHIPPED:
        data, got = eff2(p)
        assert got == OUT_NAME, (d, p, got)
        assert data == patched[p], (d, p, "content mismatch")
    for p, want_owner_prefix in (
            (VEH + "DragonTank.ini", "zzz-ZZZZZZZKwaiPDL"),
            (VEH + "CommandTank.ini", "zzz-ZZZZZZZKwaiPDL"),
            (VEH + "PDLPod.ini", "zzz-ZZZZZZZKwaiPDL"),
            ("Data\\INI\\CommandButton.ini", "zzz-ZZZZZZZTTeslaCoil"),
            ("Data\\INI\\Weapon.ini", "zzz-ZZZZZZZTTeslaCoil"),
            ("Data\\Generals.str", "zzz-ZZZZZZZTTeslaCoil"),
            ("Data\\INI\\Upgrade.ini", "zzz-ZZZZZZZKwaiPDL"),  # kwai-infantry v2: ZHE port removed
            (VAN + "ScoutCar.ini", None)):  # vanilla scout: any lower layer
        data, got = eff2(p)
        assert data is not None, (d, p)
        if want_owner_prefix:
            assert got.startswith(want_owner_prefix), (d, p, got)
        assert got != OUT_NAME, (d, p)
    # skipped units really untouched + vanilla scout still on Bullfrog set
    ct_eff = eff2(VEH + "CommandTank.ini")[0]
    assert COAX not in ct_eff and "ShareWeaponReloadTime = Yes" in ct_eff
    drg_eff = eff2(VEH + "DragonTank.ini")[0]
    assert COAX not in drg_eff
    van_sc = eff2(VAN + "ScoutCar.ini")[0]
    assert "ChinaVehicleBullfrogCommandSet" in van_sc
    assert "HelixContain" not in van_sc
    print("post-install effective-space audit OK:", d)

print("DONE")
