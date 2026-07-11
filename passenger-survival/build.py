#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZPassengerSurvival.big — passenger-survival data layer
for the Panzergrenadiers ShockWave stack on GeneralsX/macOS.

WHAT THIS LAYER DOES
--------------------
When a troop-carrying vehicle/bay is DESTROYED, its infantry should MOSTLY
SURVIVE (spilling onto the field, hurt) instead of all dying.  The only knob
this layer touches is `DamagePercentToUnits` inside the vehicles' contain
modules.

ENGINE SEMANTICS (verified in GeneralsMD OpenContain.cpp)
--------------------------------------------------------
`DamagePercentToUnits` is parsed by INI::parsePercentToReal ("25%" -> 0.25f)
into OpenContainModuleData::m_damagePercentageToUnits.  It is used in EXACTLY
ONE place: OpenContain::onDie() (line ~912):

    if ( getDamagePercentageToUnits() > 0 )
        processDamageToContained( getDamagePercentageToUnits() );
    ...
    removeAllContained();           // survivors spill out ALIVE

processDamageToContained -> processDamageToContainedInternal (line ~1492):

    Real damage = object->getBodyModule()->getMaxHealth() * percentDamage;
    damageInfo.in.m_damageType = DAMAGE_UNRESISTABLE;
    object->attemptDamage(&damageInfo);
    if ( !object->isEffectivelyDead() && percentDamage == 1.0f )
        object->kill();             // 100% is a hard kill (even flame-proof)

So the field is a DEATH-SPILL knob ONLY, never continuous-while-riding damage
(the only other processDamageToContained caller is BattleBusSlowDeathBehavior,
which uses its OWN separate field `PercentDamageToPassengers`).  The math:

  * damage dealt to EACH rider = percent x that rider's OWN MaxHealth,
    as UNRESISTABLE damage, once, at the moment the transport dies.
  * 0%   -> onDie skips the block entirely: every rider survives UNHARMED.
  * 100% -> every rider takes full max-health damage AND is hard-killed:
            guaranteed total wipe (this is the special == 1.0f case).
  * 0<p<1 -> a rider survives iff its current health > p x maxHealth.
            A FULL-HEALTH rider ALWAYS survives (p x max < max), left at
            (1-p) health; riders already below the p threshold die.
            Survivors are then ejected alive by removeAllContained().

Therefore a MODERATE percentage is exactly the "survive with damage" knob the
design wants: healthy loads spill out hurt (0-2 casualties, only those already
below the threshold), already-battered loads lose more.  No engine limitation:
the knob natively expresses the goal.  (The recently-fixed onDisabledEdge null
deref in the processDamageToContained -> onRemoving path is guarded upstream,
so ejecting damaged-but-alive survivors is safe.)

SURVIVAL POLICY (tiered by how well the hull shields its riders)
---------------------------------------------------------------
  PROTECTED (15%) : super-heavy / fully-enclosed transports — Emperor,
                    Mammoth, Overlord Battle Bunker, Battle Fortress.
  STANDARD  (25%) : medium armored transports — Battlemaster bunker bays,
                    all Troop Crawlers, Gattling Tank bay, artillery fire-out
                    bays (Buratino/Hammer/Inferno/Nuke).
  LIGHT     (35%) : light/open vehicles — Scout Car, Gattling APC.

Full-health infantry survive every tier; the tier only changes how hurt the
survivors are and how damaged a rider must already be to die.

OUT OF SCOPE (intentionally NOT touched)
----------------------------------------
The KPDL/ArmorAddon "bays" on WarMaster, CommandTank, DragonTank, ECMTank,
JS7 and Reaper are `AllowInsideKindOf = PORTABLE_STRUCTURE` pod/addon holders
(Slots=1, PassengersAllowedToFire=No) — NOT infantry bays.  Their 100% is
correct: the pod/addon dies with its host.  Lowering it would eject a loose
structure.  Helix (aircraft) passengers stay at vanilla 100% — they cannot
"spill onto the field" from altitude.

EFFECTIVE-FILE RULE
-------------------
Each object file is sourced from its CURRENT highest-priority (last-loaded)
copy below this layer, then re-emitted whole with ONLY the DamagePercentToUnits
value changed.  Because this archive sorts last (10 Z's, after
InfantryScale/DefenseVet, before zzz_ControlBarPro/zzzz_FXEnhance) it wins.

Run:  python3 build.py
"""
import os
import glob
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402

OUT_NAME = "zzz-ZZZZZZZZZZPassengerSurvival.big"

# Scan this dir for the current effective copies (last-loaded wins).
SCAN_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
INSTALL_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
]

PROTECTED, STANDARD, LIGHT = 15, 25, 35
P = r"Data\INI"

# Simple single-DPU-line targets: (internal_path, expected_old_pct, new_pct).
# The DamagePercentToUnits line is unique within each of these files.
SIMPLE = [
    # --- Battlemaster bunker bays (STANDARD) ---
    (P + r"\Object\China\Vanilla\Vehicles\BattleMaster.ini",        0, STANDARD),
    (P + r"\Object\China\Nuke\Vehicles\BattleMaster.ini",           0, STANDARD),
    (P + r"\Object\China\Tank\Vehicles\BattleMaster.ini",           0, STANDARD),
    (P + r"\Object\China\SpecialWeapons\Vehicles\RavageTank.ini",   0, STANDARD),
    # --- Troop Crawlers (STANDARD) ---
    (P + r"\Object\China\Vanilla\Vehicles\TroopCrawler.ini",       10, STANDARD),
    (P + r"\Object\China\Nuke\Vehicles\TroopCrawler.ini",          10, STANDARD),
    (P + r"\Object\China\Tank\Vehicles\TroopCrawler.ini",          10, STANDARD),
    (P + r"\Object\China\SpecialWeapons\Vehicles\SupportCrawler.ini", 10, STANDARD),
    (P + r"\Object\China\Infantry\Vehicles\TroopCrawler.ini",      10, STANDARD),
    # --- Gattling Tank bay + artillery fire-out bays (STANDARD) ---
    (P + r"\Object\China\Tank\Vehicles\GattlingTank.ini",           0, STANDARD),
    (P + r"\Object\China\SpecialWeapons\Vehicles\Buratino.ini",     0, STANDARD),
    (P + r"\Object\China\SpecialWeapons\Vehicles\HammerCannon.ini", 0, STANDARD),
    (P + r"\Object\China\Vanilla\Vehicles\InfernoCannon.ini",       0, STANDARD),
    (P + r"\Object\China\Vanilla\Vehicles\NukeCannon.ini",          0, STANDARD),
    # --- Protected transports (PROTECTED) ---
    (P + r"\Object\China\Tank\Vehicles\Emperor.ini",                0, PROTECTED),
    (P + r"\Object\China\Infantry\Vehicles\BattleFortress.ini",    80, PROTECTED),
    (P + r"\Object\USA\Armor\Vehicles\Mammoth.ini",                 0, PROTECTED),
    # --- Light/open vehicles (LIGHT) ---
    (P + r"\Object\China\Tank\Vehicles\ScoutCar.ini",               0, LIGHT),
    (P + r"\Object\China\Infantry\Vehicles\GattlingAPC.ini",        0, LIGHT),
]

# ChinaMisc.ini holds several bays; two share an identical "= 10%" line, so it
# needs block-context anchors.  Blocks patched:
#   - ChinaTankOverlordBattleBunker (Overlord infantry bunker, 0% -> PROTECTED)
#   - the buildable empty Troop Crawler (Slots=8, 10% -> STANDARD)
# Left untouched:
#   - OverlordContain PORTABLE_STRUCTURE addon slot (100%)
#   - the CINE prop crawler (Slots=10, cinematic-only)
CHINAMISC = P + r"\Object\China\Vanilla\ChinaMisc.ini"
CHINAMISC_PATCHES = [
    # Overlord Battle Bunker — unique "  = 0%" line.
    ("    DamagePercentToUnits  = 0%\n",
     "    DamagePercentToUnits  = " + str(PROTECTED) + "% ; PassengerSurvival (was 0%)\n"),
    # Buildable empty crawler — anchor on its Slots=8 block to disambiguate
    # from the Slots=10 CINE prop that carries the same "= 10%" line.
    ("    Slots = 8\n"
     "    HealthRegen%PerSec = 10\n"
     "    DamagePercentToUnits = 10%\n",
     "    Slots = 8\n"
     "    HealthRegen%PerSec = 10\n"
     "    DamagePercentToUnits = " + str(STANDARD) + "% ; PassengerSurvival (was 10%)\n"),
]


def load_effective():
    """Return {internal_path_lower: (archive_name, path, data)} using the
    last-loaded copy strictly BELOW our output layer."""
    bigs = sorted(glob.glob(os.path.join(SCAN_DIR, "*.big")),
                  key=lambda p: os.path.basename(p).lower())
    eff = {}
    for b in bigs:
        name = os.path.basename(b)
        if name.lower() >= OUT_NAME.lower():
            continue  # never source from our own layer or anything above it
        try:
            entries = read_big(b)
        except Exception:
            continue
        for e in entries:
            eff[e.path.lower()] = (name, e.path, e.data)
    return eff


def apply_line(data: bytes, old: str, new: str) -> bytes:
    """Replace `old` (written with \\n) exactly once, matching CRLF or LF."""
    for eol in ("\r\n", "\n"):
        ob = old.replace("\n", eol).encode("latin-1")
        nb = new.replace("\n", eol).encode("latin-1")
        c = data.count(ob)
        if c == 1:
            return data.replace(ob, nb)
        if c > 1:
            raise ValueError(f"anchor found {c}x (must be 1): {old!r}")
    raise ValueError(f"anchor not found: {old!r}")


def count_ends(data: bytes) -> int:
    return data.decode("latin-1").count("\nEnd")


def simple_pair(data: bytes, old_pct: int, new_pct: int):
    """Locate the single DamagePercentToUnits line, verify its value, and
    return (old_line, new_line) preserving the file's own name-alignment."""
    marker = b"DamagePercentToUnits"
    idxs = [i for i in range(len(data)) if data.startswith(marker, i)]
    if len(idxs) != 1:
        raise ValueError(f"expected 1 DamagePercentToUnits, found {len(idxs)}")
    i = idxs[0]
    # back up to start of line
    ls = data.rfind(b"\n", 0, i) + 1
    le = data.find(b"\r", i)
    le2 = data.find(b"\n", i)
    le = min(x for x in (le, le2) if x != -1)
    old_line = data[ls:le].decode("latin-1")
    if f"{old_pct}%" not in old_line:
        raise ValueError(f"expected old value {old_pct}% in {old_line!r}")
    # prefix up to and including '= '
    head = old_line.split("=", 1)[0]  # "    DamagePercentToUnits    "
    new_line = f"{head}= {new_pct}% ; PassengerSurvival (was {old_pct}%)"
    return old_line, new_line


def main():
    eff = load_effective()
    entries = []
    audit = []

    # --- simple single-line targets ---
    for path, old_pct, new_pct in SIMPLE:
        key = path.lower()
        if key not in eff:
            raise KeyError(f"effective copy not found: {path}")
        arc, real, data = eff[key]
        before = count_ends(data)
        old_line, new_line = simple_pair(data, old_pct, new_pct)
        patched = apply_line(data, old_line + "\n", new_line + "\n")
        after = count_ends(patched)
        assert before == after, f"{path}: End-count changed {before}->{after}"
        # only the DPU line differs
        _assert_only_dpu_changed(data, patched, path)
        entries.append(BigEntry(real, patched))
        audit.append((path, arc, old_pct, new_pct))

    # --- ChinaMisc.ini (multi-block) ---
    key = CHINAMISC.lower()
    arc, real, data = eff[key]
    before = count_ends(data)
    patched = data
    for old, new in CHINAMISC_PATCHES:
        patched = apply_line(patched, old, new)
    after = count_ends(patched)
    assert before == after, f"ChinaMisc: End-count changed {before}->{after}"
    _assert_only_dpu_changed(data, patched, CHINAMISC)
    entries.append(BigEntry(real, patched))
    audit.append((CHINAMISC + " (OverlordBunker)", arc, 0, PROTECTED))
    audit.append((CHINAMISC + " (EmptyCrawler)", arc, 10, STANDARD))

    # --- write + install ---
    out_path = os.path.join(HERE, OUT_NAME)
    write_big_file(entries, out_path)
    print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes, "
          f"{len(entries)} files)\n")

    # round-trip re-read
    reread = {e.path.lower(): e.data for e in read_big(out_path)}
    for e in entries:
        assert reread[e.path.lower()] == e.data, f"round-trip mismatch {e.path}"

    for d in INSTALL_DIRS:
        shutil.copyfile(out_path, os.path.join(d, OUT_NAME))
        print(f"installed {os.path.join(d, OUT_NAME)}")

    # --- audit report ---
    print("\n=== survival policy applied (DamagePercentToUnits) ===")
    tier_name = {PROTECTED: "PROTECTED", STANDARD: "STANDARD", LIGHT: "LIGHT"}
    for path, arc, old_pct, new_pct in audit:
        short = path.replace(P + "\\", "")
        print(f"  {old_pct:>3}% -> {new_pct:>3}% [{tier_name[new_pct]:<9}] "
              f"{short}  (source: {arc})")

    # --- installed re-read verification ---
    print("\n=== installed re-read verification ===")
    _verify_installed()


def _assert_only_dpu_changed(a: bytes, b: bytes, path: str):
    la = a.split(b"\n")
    lb = b.split(b"\n")
    assert len(la) == len(lb), f"{path}: line count changed"
    for x, y in zip(la, lb):
        if x != y:
            assert b"DamagePercentToUnits" in x and b"DamagePercentToUnits" in y, \
                f"{path}: non-DPU line changed:\n  {x!r}\n  {y!r}"


def _verify_installed():
    inst = os.path.join(INSTALL_DIRS[0], OUT_NAME)
    ents = {e.path.lower(): e.data for e in read_big(inst)}
    expect = {p.lower(): n for p, _o, n in SIMPLE}
    ok = 0
    for path, exp in expect.items():
        data = ents[path]
        need = f"DamagePercentToUnits".encode()
        line = next(l for l in data.split(b"\r\n") if need in l)
        assert f"= {exp}%".encode() in line, f"{path}: {line!r} != {exp}%"
        ok += 1
    # ChinaMisc: both patched values present, pod slot still 100%
    cm = ents[CHINAMISC.lower()].decode("latin-1")
    assert f"= {PROTECTED}% ; PassengerSurvival (was 0%)" in cm
    assert f"= {STANDARD}% ; PassengerSurvival (was 10%)" in cm
    assert "DamagePercentToUnits        = 100%" in cm, "pod addon slot must stay 100%"
    print(f"  {ok} simple bays verified at intended values; "
          f"ChinaMisc bunker+crawler patched, pod slot still 100%")
    print(f"  archive holds {len(ents)} files, all present in "
          f"{os.path.basename(inst)}")


if __name__ == "__main__":
    main()
