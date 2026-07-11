#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZDefenseVet.big - give EVERY combat base-defense
STRUCTURE (all factions, all ShockWave per-general variants) the ability to
earn veterancy from its own kills.  ShockWave under GeneralsX/macOS.

MECHANISM (proven by the Tesla Coil layer):  vanilla/stack base defenses
carry an ExperienceValue but never rank up because they lack the trainable
flag - the engine gates XP accrual on IsTrainable (ExperienceTracker.cpp:176)
and credits a kill to the firing object's tracker (Object.cpp:3565).  The fix
per structure is two top-level Object fields, inserted right after the
existing ExperienceValue line (exactly what tesla-coil did):

    ExperienceRequired  = 0 120 300 500   ; rank tiers V/E/H
    IsTrainable         = Yes

Once a defense can rank, the stack's GLOBAL veterancy bonuses apply to it
automatically - GameData.ini defines WeaponBonus = VETERAN/ELITE/HERO
DAMAGE/RATE_OF_FIRE (keyed on rank status, not per-object), so ranked
defenses fire faster / hit harder with NO per-structure bonus work.  This
layer therefore ONLY adds the two gate fields; it defines no new identifiers,
ships no art/audio, and touches no weapon numbers.

ExperienceRequired = 0 120 300 500 : deliberately heavier than the Tesla
Coil's 0 80 200 300 - defenses are stationary force-multipliers and should
rank SLOWER than mobile units.  ExperienceValue (XP GIVEN when the structure
dies) is left exactly as each structure already had it.

SCOPE - only STRUCTURES that fire their OWN weapon and thus get kill credit
on the STRUCTURE's tracker.  A structure qualifies iff its KindOf has
FS_BASE_DEFENSE + STRUCTURE, it has an AIUpdateInterface, and its WeaponSet
names a real damaging weapon (PrimaryDamage>0, DamageType != STATUS, name not
*DUMMY / *NotARealWeapon).  Deliberately EXCLUDED (documented in README):
  - Garrison containers (all Bunkers, Speaker Towers, Hacker Bunker, Module
    Bunker, Machine-Gun Site): no own weapon - the OCCUPANTS fire and get the
    XP, so IsTrainable on the shell is inert.
  - Pure spawners (Mortar Pit, most Stinger Sites): SPAWNS_ARE_THE_WEAPONS -
    the spawned soldiers fire and rank, not the site.  (The Salvage general's
    Stinger/Hornet Site DOES have its own HornetRocketLauncherWeapon turret,
    so it IS included.)
  - Detection turrets (Listening Post, Gazer Turret): weapons are
    DamageType = STATUS (target-marking, non-lethal) - cannot get kills.
  - Demo Traps / Mine Traps: one-shot, not repeating base-defense turrets.
  - Base-Armaments-armed ECONOMY buildings (barracks, war factory, command
    center, power plant...): armed by the kwai-basetech upgrade but NOT
    FS_BASE_DEFENSE dedicated defenses - kept out to keep this layer clean.
  - Tesla Coil: already IsTrainable (tesla-coil layer) - verified, skipped.

PACKAGING: zzz-ZZZZZZZZZDefenseVet.big sorts (case-insensitive) AFTER every
INI layer that defines these files (Panzergrenadier and below) so its whole-
file overrides win, and BEFORE zzz_ControlBarPro* / zzzz_FXEnhance.  It sorts
before the concurrently-built zzz-ZZZZZZZZZInfantryScale ('D' < 'I' at
char 14) - harmless: the two layers ship DISJOINT object files (structures vs
infantry).  Installed to both mod dirs.  The game is deliberately NOT
launched.
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
OUT_NAME = "zzz-ZZZZZZZZZDefenseVet.big"
TAG = "zzz-ZZZZZZZZZDefenseVet"
EXREQ = "0 120 300 500"

# archive immediately below us in the real listings (drift guard on sort pos)
PREV = "zzz-ZZZZZZZZPanzergrenadier.big"
# archives that legitimately sort ABOVE us; none may claim a path we ship.
# (the concurrently-built zzz-ZZZZZZZZZInfantryScale.big also sorts above us
#  but ships DISJOINT infantry object files - it may not be installed yet.)
ALLOWED_ABOVE_TO_SKIP = set()   # none are rebuilt-after-us here

# --------------------------------------------------------------- the targets
# (object name, effective object-INI path).  1 target object per file.
# Every structure below fires its OWN real weapon via an AIUpdateInterface and
# is FS_BASE_DEFENSE + STRUCTURE - enumerated & damage-verified from the live
# effective ShockWave INI space (see README for the full audit).
TARGETS = [
    # ---- CHINA (8) ----
    ("Infa_ChinaGattlingCannon", "China\\Infantry\\Defences\\GattlingCannon.ini"),
    ("Nuke_ChinaGattlingCannon", "China\\Nuke\\Defences\\GattlingCannon.ini"),
    ("Spec_ChinaHellStorm", "China\\SpecialWeapons\\Defences\\HellStorm.ini"),
    ("Spec_ChinaGattlingCannon", "China\\SpecialWeapons\\Defences\\Sentinel.ini"),
    ("Tank_ChinaGattlingCannon", "China\\Tank\\Defences\\GattlingCannon.ini"),
    ("Tank_ChinaSentryTower", "China\\Tank\\Defences\\Ramjet Turret.ini"),
    ("ChinaFlameTower", "China\\Vanilla\\Defences\\FlameTower.ini"),
    ("ChinaGattlingCannon", "China\\Vanilla\\Defences\\GattlingCannon.ini"),
    # ---- GLA (8) ----
    ("Demo_GLATunnelNetwork", "GLA\\Demo\\Defences\\TunnelNetwork.ini"),
    ("Salv_SA2Samsite", "GLA\\Salvage\\Defences\\SA2Samsite.ini"),
    ("Salv_GLAStingerSite", "GLA\\Salvage\\Defences\\StingerSiteHornetSite.ini"),
    ("Salv_GLATunnelNetwork", "GLA\\Salvage\\Defences\\TunnelNetwork.ini"),
    ("Slth_GLATunnelNetwork", "GLA\\Stealth\\Defences\\TunnelNetwork.ini"),
    ("Chem_GLATunnelNetwork", "GLA\\Toxin\\Defences\\TunnelNetwork.ini"),
    ("GLATunnelNetwork", "GLA\\Vanilla\\Defences\\TunnelNetwork.ini"),
    ("GLATunnelNetworkNoSpawn", "GLA\\Vanilla\\GLAMisc.ini"),
    # ---- USA (14) ----
    ("AirF_AmericaFireBase", "USA\\Airforce\\Defences\\FireBase.ini"),
    ("AirF_AmericaPatriotBattery", "USA\\Airforce\\Defences\\Patriot.ini"),
    ("Armor_AmericaGuardianDefenceTurret",
     "USA\\Armor\\Defences\\GuardianDefenceTurret.ini"),
    ("Armor_AmericaPatriotBattery", "USA\\Armor\\Defences\\PatriotPhalanx.ini"),
    ("Armor_AmericaVulcanTurret", "USA\\Armor\\Defences\\VulcanTurret.ini"),
    ("Lazr_AmericaFireBase", "USA\\Laser\\Defences\\LaserFireBase.ini"),
    ("Lazr_AmericaPatriotBattery", "USA\\Laser\\Defences\\LaserPatriot.ini"),
    ("SupW_AmericaPatriotBattery", "USA\\SuperWeapon\\Defences\\EMPPatriot.ini"),
    ("SupW_AmericaFireBase", "USA\\SuperWeapon\\Defences\\FireBase.ini"),
    ("Supw_AmericaPopUpPatriotBattery",
     "USA\\SuperWeapon\\Defences\\PopUpPatriot.ini"),
    ("SupW_AmericaParaDropPopTurret",
     "USA\\SuperWeapon\\SuperWeaponGeneralMisc.ini"),
    ("AmericaFireBase", "USA\\Vanilla\\Defences\\FireBase.ini"),
    ("AmericaPatriotBattery", "USA\\Vanilla\\Defences\\PatriotMissileBattery.ini"),
    ("AmericaPillbox", "USA\\Vanilla\\Defences\\Pillbox.ini"),
]
PREFIX = "Data\\INI\\Object\\"


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


def object_region(lf_lines, obj):
    """Return (start, end) line indices for the top-level `Object obj` block.
    Top-level objects are delimited by column-0 `Object NAME`; ShockWave uses
    column-0 `End` for MODULE blocks too, so `End` is NOT a safe delimiter -
    the next column-0 `Object` (or EOF) is."""
    starts = [i for i, l in enumerate(lf_lines) if re.match(r"^Object\s+\S", l)]
    hit = [i for i in starts
           if re.match(r"^Object\s+" + re.escape(obj) + r"\b", lf_lines[i])]
    assert len(hit) == 1, "%s: expected 1 object header, found %d" % (obj,
                                                                      len(hit))
    s = hit[0]
    after = [i for i in starts if i > s]
    return s, (after[0] if after else len(lf_lines))


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


def unified(a, b):
    return [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(),
                                            lineterm="", n=0)
            if not l.startswith(("---", "+++", "@@"))]


# ================================================== 1. effective sources
archives = sorted((f for f in os.listdir(SPE_DIR)
                   if f.lower().endswith(".big")
                   and f.lower() < OUT_NAME.lower()),
                  key=str.lower, reverse=True)
cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}


def effective_entry(path):
    """Highest-priority (last-sorting-below-us) entry for a path, cased."""
    want = path.lower()
    for a in archives:
        for e in cache[a]:
            if e.path.lower() == want:
                return e, a
    return None, None


sources = {}    # cased_path -> (lf_text, eol, owner)
owners = {}
for obj, rel in TARGETS:
    full = PREFIX + rel
    e, owner = effective_entry(full)
    assert e is not None, "effective source not found: " + full
    raw = e.data.decode("latin-1")
    sources[full] = (to_lf(raw), eol_of(raw), owner, e.path)
    owners[full] = owner
print("effective sources resolved for %d target files (owners: %s)" % (
    len(sources), ", ".join(sorted(set(owners.values())))))

# per-file targets (defensive: allow >1 object per file even though it's 1:1)
by_file = {}
for obj, rel in TARGETS:
    by_file.setdefault(PREFIX + rel, []).append(obj)

# ================================================== 2. patch each file
INS = ("%sExperienceRequired  = " + EXREQ + " ; " + TAG + ": base defense"
       " ranks up from kills (heavier tiers than mobile units)\n"
       "%sIsTrainable         = Yes ; " + TAG + ": XP accrual is gated on"
       " this (ExperienceTracker.cpp:176)")

patched = {}          # cased_path -> shipped bytes-text (original EOL)
patched_lf = {}       # cased_path -> lf text (for audits)
for full, objs in by_file.items():
    lf, eol, owner, cased = sources[full]
    lines = lf.split("\n")
    # patch objects back-to-front so earlier indices stay valid
    plan = []
    for obj in objs:
        s, en = object_region(lines, obj)
        ev = [i for i in range(s, en)
              if re.match(r"^\s*ExperienceValue\s*=", lines[i])]
        assert len(ev) == 1, "%s: expected 1 ExperienceValue, found %d" % (
            obj, len(ev))
        i = ev[0]
        region = lines[s:en]
        assert not any(re.match(r"^\s*IsTrainable\s*=\s*Yes", l)
                       for l in region), obj + " already IsTrainable"
        assert not any(re.match(r"^\s*ExperienceRequired\s*=", l)
                       for l in region), obj + " already has ExperienceRequired"
        indent = re.match(r"^(\s*)", lines[i]).group(1)
        plan.append((i, indent, obj))
    for i, indent, obj in sorted(plan, reverse=True):
        lines.insert(i + 1, INS % (indent, indent))
    new_lf = "\n".join(lines)
    patched_lf[full] = new_lf
    patched[full] = from_lf(new_lf, eol)

# ================================================== 3. verification
# ---- per-file diff audit: ONLY our 2 lines inserted per target, nothing else
added_total = 0
for full, objs in by_file.items():
    src_lf = sources[full][0]
    diff = unified(src_lf, patched_lf[full])
    removed = [l[1:] for l in diff if l.startswith("-")]
    added = [l[1:] for l in diff if l.startswith("+")]
    assert removed == [], (full, "unexpected removals", removed)
    # exactly 2 added lines per object in this file, and they are OURS
    assert len(added) == 2 * len(objs), (full, len(added), 2 * len(objs))
    for a in added:
        assert (("ExperienceRequired  = " + EXREQ) in a
                or "IsTrainable         = Yes" in a), (full, "foreign add", a)
    added_total += len(added)
    # block balance: no End added/removed (we only added top-level fields)
    assert end_lines(patched_lf[full]) == end_lines(src_lf), (full, "End drift")
    # line balance
    assert (len(patched_lf[full].split("\n"))
            - len(src_lf.split("\n"))) == 2 * len(objs), (full, "line drift")
print("diff audit OK: %d files, %d lines inserted (2 per structure), zero "
      "removals, zero foreign edits, End-count stable" % (len(by_file),
                                                          added_total))

# ---- every targeted object now carries both fields, in its own region
for full, objs in by_file.items():
    lines = patched_lf[full].split("\n")
    for obj in objs:
        s, en = object_region(lines, obj)
        region = "\n".join(lines[s:en])
        assert ("ExperienceRequired  = " + EXREQ) in region, (obj, "no ExReq")
        assert re.search(r"(?m)^\s*IsTrainable\s*=\s*Yes", region), (obj, "no IsTrainable")
        # ExperienceValue still present and unchanged in this region
        assert re.search(r"(?m)^\s*ExperienceValue\s*=", region), (obj, "lost EV")
print("all %d target structures carry IsTrainable=Yes + ExperienceRequired=%s"
      % (len(TARGETS), EXREQ))

# ---- no NON-target object anywhere in the shipped files gained the flag.
# (the diff audit already proves only our 2 lines/obj were added, but assert
#  the total IsTrainable=Yes count per file rose by exactly len(objs).)
for full, objs in by_file.items():
    src_n = len(re.findall(r"(?mi)^\s*IsTrainable\s*=\s*Yes", sources[full][0]))
    new_n = len(re.findall(r"(?mi)^\s*IsTrainable\s*=\s*Yes", patched_lf[full]))
    assert new_n - src_n == len(objs), (full, src_n, new_n)
print("no non-target object was made trainable (per-file IsTrainable delta "
      "== target count)")

# ---- this layer defines/renames NO identifiers and ships only object INIs
assert all(p.lower().startswith("data\\ini\\object\\") for p in patched)

# ================================================== 4. package
SHIPPED = sorted(patched)
entries = [BigEntry(sources[p][3], patched[p].encode("latin-1"))
           for p in SHIPPED]
out_local = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_local)
print("wrote %s (%d files, %d bytes)" % (out_local, len(entries),
                                         os.path.getsize(out_local)))

# ================================================== 5. sort order + install
shipped_lc = {sources[p][3].lower() for p in SHIPPED}
for d in (SPE_DIR, SHW_DIR):
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    below = listing[i - 1]
    assert below.lower() == PREV.lower(), \
        "expected %s directly below us, got %s" % (PREV, below)
    # nothing sorting ABOVE us may claim a path we ship (else it overrides us)
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        if later.lower() in ALLOWED_ABOVE_TO_SKIP:
            continue
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, \
                    "%s (sorts above us) claims our path %s" % (later, e.path)
    # still below the ControlBarPro skins + FXEnhance
    for tail in ("zzz_controlbarpro", "zzzz_fxenhance"):
        t = [f for f in listing if f.lower().startswith(tail)]
        assert all(listing.index(c) > i for c in t), (tail, listing)
    # probe: sorts before the concurrently-built infantry-scale layer
    probe = sorted(listing + ["zzz-ZZZZZZZZZInfantryScale.big"], key=str.lower)
    assert probe.index("zzz-ZZZZZZZZZInfantryScale.big") > probe.index(OUT_NAME)
    print("sort order OK in %s: %s < %s < %s (no later archive claims our "
          "paths; before ControlBarPro/FXEnhance/InfantryScale)"
          % (d, below, OUT_NAME, listing[i + 1]))

# ---- install + re-read + byte-compare + re-assert the two fields survive
blob = open(out_local, "rb").read()
for d in (SPE_DIR, SHW_DIR):
    dst = os.path.join(d, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob)
    back = read_big(dst)
    assert [e.path for e in back] == [e.path for e in entries], dst
    for x, y in zip(back, entries):
        assert x.data == y.data, x.path
    # spot re-check every target in the INSTALLED bytes
    for obj, rel in TARGETS:
        cased = sources[PREFIX + rel][3]
        txt = to_lf(find_entry(back, cased).data.decode("latin-1"))
        lines = txt.split("\n")
        s, en = object_region(lines, obj)
        region = "\n".join(lines[s:en])
        assert ("ExperienceRequired  = " + EXREQ) in region and \
            re.search(r"(?m)^\s*IsTrainable\s*=\s*Yes", region), (dst, obj)
    print("installed + re-read + re-verified all %d structures: %s"
          % (len(TARGETS), dst))

print("DONE - %d base defenses across all factions can now earn veterancy."
      % len(TARGETS))
