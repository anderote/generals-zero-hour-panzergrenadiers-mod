#!/usr/bin/env python3
"""Build zzyz_GattlingBuff.big for ShockWave (GeneralsX).

Buffs China's gattling TANKS (vanilla, Nuke, Spec/Leang, Tank/Kwai gattling
tanks + Infantry general's Gattling APC), multiplicatively on top of the
already-installed zzx_ChinaTankBuff layer:

  - MaxHealth / InitialHealth  x1.15  (on top of tank-buff's x1.2 -> 1.38x vanilla)
  - weapon AttackRange         x1.2   (on top of tank-buff's x1.1 -> 1.32x vanilla)
  - weapon PrimaryDamage       x1.2
  - weapon DelayBetweenShots   /1.1   (rounded to integer ms)

All weapon *stages* are scaled uniformly (normal / PLAYER_UPGRADE "Advanced"
/ HERO variants, ground + air guns), so the ContinuousFire spin-up
progression (RATE_OF_FIRE 200%/300% WeaponBonus) stays coherent -- the
bonuses are percentages of the base delay and scale automatically.

Dummy handling: Spec_ChinaTankGattling's hull carries the near-zero-damage
Spec_GattlingTankAirDummy (STATUS, 0.0001 dmg) as its AA acquisition
weapon; the real AA gun (Spec_GattlingTankGunAir) sits on the independent
rider turret Spec_ChinaTankGattlingTurret. The dummy's range must track the
real gun's range or the hull's AA engagement envelope stays at the old
value. The dummy template is SHARED with Infa_ChinaVehicleHelix and
Spec_ChinaGattlingCannon (Sentinel), whose real guns we do NOT buff, so
instead of scaling the shared template we clone it as
Spec_GattlingTankAirDummyBuffed (range 420) and repoint only the Spec
gattling tank's WeaponSets at the clone. Helix/Sentinel keep the original
350 dummy.

Effective-file rule: every file we ship is extracted from the
highest-priority archive that contains it -- verified to be
zzx_ChinaTankBuff.big for all six files (zzyy_ChinaBunkers.big and
zzy_MammothBunker.big contain no gattling/Weapon.ini entries).
"""

import hashlib
import os
import re
import sys

sys.path.insert(0, "/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon")
from bigfile import read_big, write_big_file, BigEntry, find_entry

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "zzyz_GattlingBuff.big"
OUT_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
]
SRC_BIG_SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zzx_ChinaTankBuff.big")
SRC_BIG_SHW = os.path.expanduser("~/GeneralsX/mods/ShockWave/zzx_ChinaTankBuff.big")

HEALTH_MULT = 1.15
RANGE_MULT = 1.2
DAMAGE_MULT = 1.2
ROF_DIV = 1.1

VANILLA = {  # true vanilla (pre-any-mod) values, for vs-vanilla reporting
    "health": {
        "ChinaTankGattling": 300.0,
        "Nuke_ChinaTankGattling": 300.0,
        "Spec_ChinaTankGattling": 300.0,
        "Tank_ChinaTankGattling": 350.0,
        "Infa_ChinaTankGattling": 220.0,
    },
    "range": {  # weapon -> vanilla AttackRange
        "GattlingTankGun": 150.0, "GattlingTankGunHeroic": 150.0, "GattlingTankGunAir": 350.0,
        "AdvancedGattlingTankGun": 150.0, "AdvancedGattlingTankGunHeroic": 150.0, "AdvancedGattlingTankGunAir": 350.0,
        "NukeGattlingTankGun": 150.0, "NukeGattlingTankGunHeroic": 150.0, "NukeGattlingTankGunAir": 350.0,
        "NukeAdvancedGattlingTankGun": 150.0, "NukeAdvancedGattlingTankGunHeroic": 150.0, "NukeAdvancedGattlingTankGunAir": 350.0,
        "Spec_GattlingTankGun": 150.0, "Spec_GattlingTankGunHeroic": 150.0, "Spec_GattlingTankGunAir": 350.0,
        "GattlingAPCGun": 150.0, "GattlingAPCGunHeroic": 150.0, "GattlingAPCGunAir": 230.0,
        "UpgradedGattlingAPCGun": 150.0, "UpgradedGattlingAPCGunHeroic": 150.0, "UpgradedGattlingAPCGunAir": 230.0,
    },
}

# object -> (file internal path, expected current MaxHealth from zzx layer)
OBJECTS = {
    "ChinaTankGattling": (r"Data\INI\Object\China\Vanilla\Vehicles\GattlingTank.ini", 360.0),
    "Nuke_ChinaTankGattling": (r"Data\INI\Object\China\Nuke\Vehicles\GattlingTank.ini", 360.0),
    "Spec_ChinaTankGattling": (r"Data\INI\Object\China\SpecialWeapons\Vehicles\GattlingTank.ini", 360.0),
    "Tank_ChinaTankGattling": (r"Data\INI\Object\China\Tank\Vehicles\GattlingTank.ini", 420.0),
    "Infa_ChinaTankGattling": (r"Data\INI\Object\China\Infantry\Vehicles\GattlingAPC.ini", 264.0),
}

# weapon -> (expected current AttackRange, PrimaryDamage, DelayBetweenShots) in zzx layer
WEAPONS = {
    "GattlingTankGun": (165.0, 15.0, 400),
    "GattlingTankGunHeroic": (165.0, 15.0, 400),
    "GattlingTankGunAir": (385.0, 12.0, 400),
    "AdvancedGattlingTankGun": (165.0, 15.0, 400),
    "AdvancedGattlingTankGunHeroic": (165.0, 15.0, 400),
    "AdvancedGattlingTankGunAir": (385.0, 12.0, 400),
    "NukeGattlingTankGun": (165.0, 15.0, 400),
    "NukeGattlingTankGunHeroic": (165.0, 15.0, 400),
    "NukeGattlingTankGunAir": (385.0, 12.0, 400),
    "NukeAdvancedGattlingTankGun": (165.0, 15.0, 400),
    "NukeAdvancedGattlingTankGunHeroic": (165.0, 15.0, 400),
    "NukeAdvancedGattlingTankGunAir": (385.0, 12.0, 400),
    "Spec_GattlingTankGun": (165.0, 18.75, 400),
    "Spec_GattlingTankGunHeroic": (165.0, 18.75, 400),
    "Spec_GattlingTankGunAir": (350.0, 10.0, 400),  # rider turret gun; tank-buff missed it
    "GattlingAPCGun": (165.0, 10.0, 400),
    "GattlingAPCGunHeroic": (165.0, 10.0, 400),
    "GattlingAPCGunAir": (253.0, 8.0, 400),
    "UpgradedGattlingAPCGun": (165.0, 10.0, 400),
    "UpgradedGattlingAPCGunHeroic": (165.0, 10.0, 400),
    "UpgradedGattlingAPCGunAir": (253.0, 8.0, 400),
}

DUMMY_SRC = "Spec_GattlingTankAirDummy"
DUMMY_NEW = "Spec_GattlingTankAirDummyBuffed"
DUMMY_NEW_RANGE = 420.0  # must equal Spec_GattlingTankGunAir's new range

# prior-layer (china-tank-buff) values that must survive in our Weapon.ini copy
PRIOR_LAYER_SPOT_CHECKS = {
    "BattleMasterTankGun": 165.0,
    "OverlordTankGun": 192.5,
    "ChainGun55mmslugeatingWeaponwithalongname": 192.5,
    "Tank_WarMasterTankGun": 176.0,
}

MAXHP_RE = re.compile(r"^(\s*MaxHealth\s*=\s*)([\d.]+)(.*)$")
INITHP_RE = re.compile(r"^(\s*InitialHealth\s*=\s*)([\d.]+)(.*)$")
RANGE_RE = re.compile(r"^(\s*AttackRange\s*=\s*)([\d.]+)(.*)$")
PDMG_RE = re.compile(r"^(\s*PrimaryDamage\s*=\s*)([\d.]+)(.*)$")
SDMG_RE = re.compile(r"^(\s*SecondaryDamage\s*=\s*)([\d.]+)(.*)$")
DELAY_RE = re.compile(r"^(\s*DelayBetweenShots\s*=\s*)(\d+)(.*)$")
WEAPON_DEF_RE = re.compile(r"^[ \t]*Weapon[ \t]+([\w-]+)[ \t]*(?:;.*|//.*)?$")


def fmt(value, orig):
    if abs(value - round(value)) < 1e-9:
        iv = int(round(value))
        return f"{iv}.0" if "." in orig else str(iv)
    return ("%.4f" % value).rstrip("0").rstrip(".")


def weapon_extents(lines):
    decls = []
    for i, line in enumerate(lines):
        m = WEAPON_DEF_RE.match(line.rstrip("\r\n"))
        if m:
            decls.append((i, m.group(1)))
    ext = {}
    for idx, (i, name) in enumerate(decls):
        end = decls[idx + 1][0] if idx + 1 < len(decls) else len(lines)
        assert name not in ext, f"duplicate weapon template {name}"
        ext[name] = (i, end)
    return ext


def main():
    # ---- sanity: the two installed zzx copies are identical ----
    h_spe = hashlib.md5(open(SRC_BIG_SPE, "rb").read()).hexdigest()
    h_shw = hashlib.md5(open(SRC_BIG_SHW, "rb").read()).hexdigest()
    assert h_spe == h_shw, "zzx_ChinaTankBuff.big differs between mod dirs!"

    src = read_big(SRC_BIG_SPE)
    modified = {}          # internal path -> new text
    originals = {}         # internal path -> original text
    rep_health, rep_weap = [], []

    # ---- object files: health x1.15 (+ Spec dummy repoint) ----
    for obj, (path, expect_hp) in OBJECTS.items():
        entry = find_entry(src, path)
        text = entry.data.decode("latin-1")
        originals[entry.path] = text
        lines = text.splitlines(keepends=True)
        n_hp = 0
        for i, raw in enumerate(lines):
            body = raw.rstrip("\r\n")
            eol = raw[len(body):]
            m = MAXHP_RE.match(body) or INITHP_RE.match(body)
            if m:
                old = float(m.group(2))
                assert abs(old - expect_hp) < 1e-6, \
                    f"{obj}: expected health {expect_hp}, found {old} (upstream drift?)"
                new = fmt(round(old * HEALTH_MULT), m.group(2))
                lines[i] = m.group(1) + new + m.group(3) + eol
                if "MaxHealth" in m.group(1):
                    rep_health.append((obj, old, float(new)))
                n_hp += 1
        assert n_hp == 2, f"{obj}: expected MaxHealth+InitialHealth, changed {n_hp} lines"
        new_text = "".join(lines)
        if obj == "Spec_ChinaTankGattling":
            pat = re.compile(r"(Weapon\s*=\s*SECONDARY\s+)" + DUMMY_SRC + r"(?![\w-])")
            new_text, n_sub = pat.subn(r"\g<1>" + DUMMY_NEW, new_text)
            assert n_sub == 2, f"expected 2 dummy WeaponSet refs in Spec file, got {n_sub}"
        modified[entry.path] = new_text

    # ---- Weapon.ini: range/damage/delay on 21 real weapons + dummy clone ----
    wentry = find_entry(src, r"Data\INI\Weapon.ini")
    wtext = wentry.data.decode("latin-1")
    originals[wentry.path] = wtext
    wlines = wtext.splitlines(keepends=True)
    ext = weapon_extents(wlines)

    for wname, (exp_r, exp_d, exp_delay) in sorted(WEAPONS.items()):
        s, e = ext[wname]
        got = {"range": 0, "dmg": 0, "delay": 0}
        entry_rep = {"name": wname}
        for i in range(s, e):
            raw = wlines[i]
            body = raw.rstrip("\r\n")
            eol = raw[len(body):]
            m = RANGE_RE.match(body)
            if m:
                old = float(m.group(2))
                assert abs(old - exp_r) < 1e-6, f"{wname} AttackRange {old} != expected {exp_r}"
                new = fmt(old * RANGE_MULT, m.group(2))
                wlines[i] = m.group(1) + new + m.group(3) + eol
                entry_rep["range"] = (old, float(new))
                got["range"] += 1
                continue
            m = PDMG_RE.match(body)
            if m:
                old = float(m.group(2))
                assert abs(old - exp_d) < 1e-6, f"{wname} PrimaryDamage {old} != expected {exp_d}"
                new = fmt(old * DAMAGE_MULT, m.group(2))
                wlines[i] = m.group(1) + new + m.group(3) + eol
                entry_rep["dmg"] = (old, float(new))
                got["dmg"] += 1
                continue
            assert not SDMG_RE.match(body), f"{wname} has SecondaryDamage (unhandled)"
            m = DELAY_RE.match(body)
            if m:
                old = int(m.group(2))
                assert old == exp_delay, f"{wname} DelayBetweenShots {old} != expected {exp_delay}"
                new = str(round(old / ROF_DIV))
                wlines[i] = m.group(1) + new + m.group(3) + eol
                entry_rep["delay"] = (old, int(new))
                got["delay"] += 1
        assert got == {"range": 1, "dmg": 1, "delay": 1}, f"{wname}: matched lines {got}"
        rep_weap.append(entry_rep)

    # dummy clone: copy Spec_GattlingTankAirDummy block, rename, set range 420
    s, e = ext[DUMMY_SRC]
    block = wlines[s:e]
    # trim trailing blank lines off the copied block
    while block and block[-1].strip() == "":
        block.pop()
    assert block[-1].strip() == "End", "dummy block does not end with End"
    clone = []
    clone.append(";------------------------------------------------------------------------------\n")
    clone.append("; Added by zzyz_GattlingBuff: private copy of " + DUMMY_SRC + " for\n")
    clone.append("; Spec_ChinaTankGattling only, so its hull AA acquisition envelope tracks the\n")
    clone.append("; buffed rider-turret gun (Spec_GattlingTankGunAir) without touching the\n")
    clone.append("; Helix / Sentinel gattling cannon, which share the original dummy.\n")
    n_range = 0
    for raw in block:
        body = raw.rstrip("\r\n")
        eol = raw[len(body):] or "\n"
        m = re.match(r"^([ \t]*Weapon[ \t]+)" + DUMMY_SRC + r"([ \t]*.*)$", body)
        if m:
            clone.append(m.group(1) + DUMMY_NEW + m.group(2) + eol)
            continue
        m = RANGE_RE.match(body)
        if m:
            assert abs(float(m.group(2)) - 350.0) < 1e-6, "dummy range drifted"
            clone.append(m.group(1) + fmt(DUMMY_NEW_RANGE, m.group(2)) + m.group(3) + eol)
            n_range += 1
            continue
        clone.append(body + eol)
    assert n_range == 1
    clone.append("\n")
    wlines[e:e] = clone  # insert right after the original dummy block
    modified[wentry.path] = "".join(wlines)

    # ---- verification: prior-layer values survive in shipped Weapon.ini ----
    final_ext = weapon_extents(modified[wentry.path].splitlines(keepends=True))
    flines = modified[wentry.path].splitlines()
    for wname, want_range in PRIOR_LAYER_SPOT_CHECKS.items():
        s, e = final_ext[wname]
        vals = [float(m.group(2)) for L in flines[s:e] if (m := RANGE_RE.match(L))]
        assert vals and abs(vals[0] - want_range) < 1e-6, \
            f"prior-layer check failed: {wname} AttackRange {vals} != {want_range}"
    assert DUMMY_NEW in final_ext and DUMMY_SRC in final_ext

    # ---- verification: diff hunks only where intended ----
    diff_summary = {}
    for path, new_text in modified.items():
        old_lines = originals[path].splitlines()
        new_lines = new_text.splitlines()
        if path.lower().endswith("weapon.ini"):
            inserted = len(new_lines) - len(old_lines)
            assert inserted == len(clone), f"unexpected insertion size in {path}"
            # compare with clone spliced out
            e0 = None
            # find insertion point again by locating the clone comment
            idx = new_lines.index("; Added by zzyz_GattlingBuff: private copy of " + DUMMY_SRC + " for") - 1
            spliced = new_lines[:idx] + new_lines[idx + len(clone):]
            changed = [i for i, (a, b) in enumerate(zip(old_lines, spliced)) if a != b]
            assert len(spliced) == len(old_lines)
            exp = len(WEAPONS) * 3
            assert len(changed) == exp, f"{path}: {len(changed)} changed lines, expected {exp}"
            for i in changed:
                assert re.match(r"\s*(AttackRange|PrimaryDamage|DelayBetweenShots)\s*=", old_lines[i]), \
                    f"unintended change at {path}:{i + 1}: {old_lines[i]!r}"
            diff_summary[path] = f"{len(changed)} stat lines changed + {len(clone)}-line dummy clone inserted"
        else:
            assert len(old_lines) == len(new_lines)
            changed = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
            exp = 4 if "SpecialWeapons" in path else 2
            assert len(changed) == exp, f"{path}: {len(changed)} changed lines, expected {exp}"
            for i in changed:
                assert re.match(r"\s*(MaxHealth|InitialHealth|Weapon)\s*=", old_lines[i]), \
                    f"unintended change at {path}:{i + 1}: {old_lines[i]!r}"
            diff_summary[path] = f"{len(changed)} lines changed"

    # ---- block balance: 'End' count per file (+1 for Weapon.ini clone) ----
    for path, new_text in modified.items():
        n_old = len(re.findall(r"^\s*End\s*(?:;.*)?$", originals[path], re.M | re.I))
        n_new = len(re.findall(r"^\s*End\s*(?:;.*)?$", new_text, re.M | re.I))
        want = n_old + (1 if path.lower().endswith("weapon.ini") else 0)
        assert n_new == want, f"{path}: End count {n_old} -> {n_new}, expected {want}"

    # ---- package & install ----
    out_entries = [BigEntry(p, t.encode("latin-1")) for p, t in sorted(modified.items())]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(out_entries, out_local)
    for d in OUT_DIRS:
        with open(out_local, "rb") as fi, open(os.path.join(d, OUT_NAME), "wb") as fo:
            fo.write(fi.read())

    # ---- verify installed archives round-trip ----
    local_bytes = open(out_local, "rb").read()
    for d in OUT_DIRS:
        p = os.path.join(d, OUT_NAME)
        assert open(p, "rb").read() == local_bytes, f"install mismatch: {p}"
        back = read_big(p)
        assert {e.path: e.data for e in back} == {e.path: e.data for e in out_entries}, p

    # sort-order sanity inside the mod dirs (case-insensitive)
    for d in OUT_DIRS:
        bigs = sorted((f.lower() for f in os.listdir(d) if f.lower().endswith(".big")))
        i = bigs.index(OUT_NAME.lower())
        after = [b for b in bigs[:i] if b.startswith("zz")]
        assert "zzx_chinatankbuff.big" in after and \
               ("zzyy_chinabunkers.big" in after), f"sort order broken in {d}: {bigs}"
        assert all(not b.startswith("zzz_") for b in after), d

    # ---- report ----
    print("HEALTH (x1.15 on current; vanilla -> tank-buff -> now):")
    for obj, old, new in rep_health:
        van = VANILLA["health"][obj]
        print(f"  {obj:28s} {old:7.1f} -> {new:7.1f}   (vanilla {van:.0f}, total x{new / van:.3f})")
    print("\nWEAPONS (range x1.2, damage x1.2, delay /1.1):")
    for r in rep_weap:
        van = VANILLA["range"][r["name"]]
        ro, rn = r["range"]
        do, dn = r["dmg"]
        yo, yn = r["delay"]
        print(f"  {r['name']:36s} range {ro:6.1f}->{rn:6.1f} (van {van:.0f}, x{rn / van:.2f})"
              f"  dmg {do:5.2f}->{dn:5.2f}  delay {yo}->{yn}")
    print(f"\nDUMMY: {DUMMY_SRC} kept at 350 (shared with Helix/Sentinel);")
    print(f"       new {DUMMY_NEW} @ {DUMMY_NEW_RANGE:.0f} used by Spec_ChinaTankGattling only.")
    print("\nDIFF SUMMARY:")
    for p, s in sorted(diff_summary.items()):
        print(f"  {p}: {s}")
    print("\nFILES IN ARCHIVE (%d):" % len(out_entries))
    for e in out_entries:
        print(f"  {len(e.data):>9}  {e.path}")
    print("\nINSTALLED:")
    for d in OUT_DIRS:
        print("  ", os.path.join(d, OUT_NAME))
    print("\nALL VERIFICATIONS PASSED")


if __name__ == "__main__":
    main()
