#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZZZZZZZ0TeslaHP.big  --  the "Tesla HP" top layer for
Kwai (China Tank General) tesla/shock infantry, ShockWave under GeneralsX
(macOS).  Pure data; no engine, no art, no new identifiers.

WHY THIS LAYER EXISTS
  The recent Rebalance pass (zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big, 18 'Z') cut
  every China infantry unit's HP ~50% (Red Guard 120->60, Panzergrenadier
  144->72, ...) but had to SKIP the tesla Shock Trooper + tesla infantry because
  their file, RotrShockTrooper.ini, was locked by the tesla-tune session at the
  time.  This layer applies the same ~50% HP cut to those units so they match.

EFFECTIVE SOURCE (winning copy, preserved byte-for-byte except HP)
  RotrShockTrooper.ini's effective owner is the tesla-tune layer
  zzz-ZZZZZZZZZZZZZZZZ0TeslaTune.big (16 'Z') -- verified live at build time.
  We re-ship RotrShockTrooper.ini based on THAT winning copy, changing ONLY the
  MaxHealth/InitialHealth lines of the two HP-bearing tesla infantry objects.
  Everything else survives verbatim: the tesla FX trail on the flying bolt
  (ParticleSysBone = None TeslaBoltSparks on ShockTrooperTeslaBoltProjectile),
  the nerfed weapon references (ShockTrooperTeslaWeapon), the chain/detonation
  wiring, the projectile's own HP (100, a PROJECTILE -- LEFT alone), etc.

HP CUTS (~50%, both MaxHealth AND InitialHealth)
  Tank_ChinaInfantryShockTrooper_Var1 : 250 -> 125
      (the actual buildable Shock Trooper.  The base object
       Tank_ChinaInfantryShockTrooper is a BuildVariations *selector* with no
       Body/HP of its own; only the _Var1 variant carries HP.  No _Var2/_Var3
       objects exist -- BuildVariations falls back to _Var1 -- and there is no
       separate Heroic/veteran ShockTrooper object; heroism comes from a weapon
       OCL, not a distinct unit.)
  TeslaInfantry                       :  50 ->  25  (the tesla infantry object)

NOT TOUCHED (documented)
  ShockTrooperTeslaBoltProjectile (HP 100) -- a KindOf=PROJECTILE object, not a
    unit; left at 100 exactly as required.
  ShockTrooperTeslaChainNode / ...Heroic (HP 50 each) -- KindOf CAN_ATTACK
    NO_COLLIDE IMMOBILE UNATTACKABLE weapon-delivery nodes spawned by the
    projectile's detonation OCL; they are the tesla-chain mechanism itself
    (part of the FX/chain wiring this layer must preserve), are UNATTACKABLE so
    their HP is functionally irrelevant, and are neither infantry nor squad
    members.  Left untouched, same reasoning as the projectile.
  Shmel Trooper (Tank_ChinaInfantryShmelTrooper) lives in a SEPARATE file,
    RotrShmelTrooper.ini, and was already cut by the Rebalance pass -- not in
    this file, so not re-shipped here.  (Noted, deferred: nothing to do.)

SORT POSITION
  Name = "zzz-" + 19 'Z' + "0TeslaHP".  At the 19th 'Z' our 'Z' (case-folded
  'z' 0x7A) beats Rebalance's '0' (0x30) at the same offset, so we sort AFTER
  every existing DATA layer (highest is Rebalance = 18 'Z').  Because '-'
  (0x2D) < '_' (0x5F) < 'z' (0x7A), we sort BEFORE zzz_ControlBarPro* and
  zzzz_FXEnhance.  Both facts are asserted against the real listings of BOTH
  mod dirs at build time.
"""

import os
import re
import sys
import difflib
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")

OUT_NAME = "zzz-" + "Z" * 19 + "0TeslaHP.big"   # 19 'Z'
TAG = "tesla-hp"

OBJ_PATH = "Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShockTrooper.ini"
PS_PATH = "Data\\INI\\ParticleSystem.ini"

# expected effective owner of the file we re-ship (verified at build time)
OBJ_OWNER = "zzz-ZZZZZZZZZZZZZZZZ0TeslaTune.big"   # tesla-tune, 16 'Z'

# archives that legitimately sort ABOVE us (must claim NONE of our paths)
ABOVE_OK = {"zzzz_fxenhance.big", "zzz_controlbarprozh.big",
            "zzz_controlbarpro2160zh.big"}

# the tesla FX trail on the projectile (must survive byte-for-byte)
TRAIL_LINE = "      ParticleSysBone = None TeslaBoltSparks"
TRAIL_PS = "TeslaBoltSparks"

# ~50% HP cut: object -> (old_max, new_max, old_init, new_init) formatted strings
HP_CUTS = {
    "Tank_ChinaInfantryShockTrooper_Var1": ("250.0", "125.0", "250.0", "125.0"),
    "TeslaInfantry":                        ("50.0",  "25.0",  "50.0",  "25.0"),
}

# non-HP content that MUST survive verbatim (spot-checks after edit)
PRESERVE = [
    TRAIL_LINE,                                          # tesla FX bolt trail
    "    Weapon            = PRIMARY ShockTrooperTeslaWeapon",     # weapon ref
]


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


def object_block(lf, name):
    """Return (start, end) span of `Object <name> ... End`, exact-name match."""
    hdrs = list(re.finditer(r"(?mi)^Object[ \t]+(\S+)[ \t]*$", lf))
    for i, m in enumerate(hdrs):
        if m.group(1) == name:
            s = m.end()
            e = hdrs[i + 1].start() if i + 1 < len(hdrs) else len(lf)
            return s, e
    raise AssertionError("object block not found: " + name)


def set_health(lf, name, field, oldval, newval):
    """Set the single `field = oldval` line inside `Object name` to newval."""
    s, e = object_block(lf, name)
    region = lf[s:e]
    pat = re.compile(r"(?m)^(?P<lead>[ \t]*%s[ \t]*=[ \t]*)%s[ \t]*$"
                     % (re.escape(field), re.escape(oldval)))
    cnt = [0]

    def repl(mm):
        cnt[0] += 1
        return mm.group("lead") + newval

    region2 = pat.sub(repl, region)
    assert cnt[0] == 1, "%s.%s: expected exactly 1 '%s' line, changed %d" \
        % (name, field, oldval, cnt[0])
    return lf[:s] + region2 + lf[e:]


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


# ================================================== 1. effective source
archives = sorted((f for f in os.listdir(SPE_DIR)
                   if f.lower().endswith(".big") and f.lower() < OUT_NAME.lower()),
                  key=str.lower, reverse=True)
cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}


def effective(path):
    want = path.lower()
    for a in archives:                       # archives are high->low priority
        for e in cache[a]:
            if e.path.lower() == want:
                return e.data.decode("latin-1"), a
    return None, None


src_raw, got = effective(OBJ_PATH)
assert src_raw is not None, "effective source not found: " + OBJ_PATH
assert got == OBJ_OWNER, "ownership drift for RotrShockTrooper.ini: %s (expected %s)" \
    % (got, OBJ_OWNER)
print("effective-file ownership verified: RotrShockTrooper.ini <- %s" % OBJ_OWNER)

# closure blob over the whole effective INI space below us (for reference checks)
seen = set()
ini_blob = []
for a in archives:
    for e in cache[a]:
        lp = e.path.lower()
        if lp in seen or not lp.endswith(".ini"):
            continue
        seen.add(lp)
        ini_blob.append(to_lf(e.data.decode("latin-1")))
blob = "\n".join(ini_blob)

# ================================================== 2. apply HP cuts
eol = eol_of(src_raw)
src_lf = to_lf(src_raw)
out_lf = src_lf
report_rows = []
for name, (om, nm, oi, ni) in HP_CUTS.items():
    out_lf = set_health(out_lf, name, "MaxHealth", om, nm)
    out_lf = set_health(out_lf, name, "InitialHealth", oi, ni)
    report_rows.append((name, om, nm))
patched_raw = from_lf(out_lf, eol)

# ================================================== 3. verification
# ---- diff audit: EXACTLY the 4 HP lines changed (2 objects x 2 fields) -----
diff = unified(src_lf, out_lf)
rem = [l[1:] for l in diff if l.startswith("-")]
add = [l[1:] for l in diff if l.startswith("+")]
assert len(rem) == 4 and len(add) == 4, ("expected 4 changed lines", rem, add)
for line in rem + add:
    key = line.strip().split("=")[0].strip()
    assert key in ("MaxHealth", "InitialHealth"), "non-HP line changed: " + repr(line)
# line count unchanged, End-block count unchanged (nothing added/removed)
assert len(src_lf.split("\n")) == len(out_lf.split("\n")), "line count changed"
assert end_lines(out_lf) == end_lines(src_lf), "End-block count changed"
print("diff audit OK: exactly 4 lines changed, all MaxHealth/InitialHealth; "
      "line count + End-block count unchanged")

# ---- new HP values present in the right objects ----------------------------
for name, om, nm in report_rows:
    s, e = object_block(out_lf, name)
    reg = out_lf[s:e]
    assert re.search(r"(?m)^[ \t]*MaxHealth[ \t]*=[ \t]*%s[ \t]*$" % re.escape(nm), reg)
    assert re.search(r"(?m)^[ \t]*InitialHealth[ \t]*=[ \t]*%s[ \t]*$" % re.escape(nm), reg)

# ---- tesla FX trail + weapon refs + non-touched HP survive verbatim --------
for keep in PRESERVE:
    assert src_lf.count(keep) == 1 and out_lf.count(keep) == 1, \
        "preserved content drift: " + keep
# projectile HP stays 100 (untouched); chain nodes stay 50 (untouched)
def hp_of(lf, name, field="MaxHealth"):
    s, e = object_block(lf, name)
    m = re.search(r"(?m)^[ \t]*%s[ \t]*=[ \t]*([0-9.]+)" % field, lf[s:e])
    return m.group(1) if m else None
assert hp_of(out_lf, "ShockTrooperTeslaBoltProjectile") == "100.0", "projectile HP moved"
assert hp_of(out_lf, "ShockTrooperTeslaChainNode") == "50.0", "chain node HP moved"
assert hp_of(out_lf, "ShockTrooperTeslaChainNodeHeroic") == "50.0", "heroic chain node HP moved"
print("survival OK: tesla FX trail (%s) + weapon ref intact; projectile HP=100 & "
      "chain-node HP=50 untouched" % TRAIL_PS)

# ---- closure: every identifier the edited objects reference still resolves --
# (we only changed numbers, so no reference could have changed; assert the key
#  referenced identifiers exist in the effective INI space below us.)
assert re.search(r"(?m)^ParticleSystem\s+%s\b" % re.escape(TRAIL_PS), blob), \
    "unresolved: ParticleSystem " + TRAIL_PS
assert re.search(r"(?m)^Weapon\s+ShockTrooperTeslaWeapon\b", blob), \
    "unresolved: Weapon ShockTrooperTeslaWeapon"
# the projectile object referenced by the weapon is defined in THIS file
assert re.search(r"(?m)^Object\s+ShockTrooperTeslaBoltProjectile\b", out_lf)
print("closure OK: TeslaBoltSparks (ParticleSystem) + ShockTrooperTeslaWeapon "
      "resolve; projectile object still defined")

# ================================================== 4. package + round-trip
entries = [BigEntry(OBJ_PATH, patched_raw.encode("latin-1"))]
out_local = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_local)
print("wrote %s (%d files, %d bytes)"
      % (out_local, len(entries), os.path.getsize(out_local)))

rt = read_big(out_local)
assert [e.path for e in rt] == [e.path for e in entries]
for x, y in zip(rt, entries):
    assert x.data == y.data, x.path
print("BIG round-trip byte-identical")

# ================================================== 5. sort order + no-masking
shipped_lc = {e.path.lower() for e in entries}
for d in (SPE_DIR, SHW_DIR):
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    # everything after us must be UI (ControlBarPro / FXEnhance) and claim none
    # of our paths
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        assert later.lower() in ABOVE_OK, "unexpected archive sorts above us: " + later
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, \
                    "MASKED: %s claims our %s" % (later, e.path)
    # the last DATA layer below us must be Rebalance (18 'Z'); tesla-tune present
    below = listing[:i]
    assert below[-1].startswith("zzz-" + "Z" * 18 + "0Rebalance"), \
        "top data layer below us is not Rebalance: " + below[-1]
    assert any(f.lower() == OBJ_OWNER.lower() for f in below), "tesla-tune not below us"
    cbp = [f for f in listing if f.lower().startswith("zzz_controlbarpro")]
    assert cbp and all(listing.index(c) > i for c in cbp), listing
    fx = [f for f in listing if f.lower() == "zzzz_fxenhance.big"]
    assert fx and listing.index(fx[0]) > i, "fx-enhance must sort after us"
    print("sort order OK in %s: all data layers (top=%s) < %s < %s"
          % (os.path.basename(d), below[-1], OUT_NAME, ", ".join(listing[i + 1:])))

# ================================================== 6. install + audit + md5
blob_bytes = open(out_local, "rb").read()
md5s = {}
for d in (SPE_DIR, SHW_DIR):
    dst = os.path.join(d, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob_bytes)
    md5s[d] = hashlib.md5(open(dst, "rb").read()).hexdigest()
    back = read_big(dst)
    assert [e.path for e in back] == [e.path for e in entries]
    for x, y in zip(back, entries):
        assert x.data == y.data, x.path
    # post-install effective-ownership audit: we own RotrShockTrooper.ini now
    arts = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")),
                  key=str.lower, reverse=True)
    ca = {a: read_big(os.path.join(d, a)) for a in arts}

    def eff2(path):
        w = path.lower()
        for a in arts:
            for e in ca[a]:
                if e.path.lower() == w:
                    return e.data.decode("latin-1"), a
        return None, None

    oi, own = eff2(OBJ_PATH)
    assert own == OUT_NAME, "post-install owner drift %s: %s" % (OBJ_PATH, own)
    oi_lf = to_lf(oi)
    # installed-byte proof of the cuts + survival
    for name, om, nm in report_rows:
        s, e = object_block(oi_lf, name)
        assert re.search(r"(?m)^[ \t]*MaxHealth[ \t]*=[ \t]*%s[ \t]*$" % re.escape(nm),
                         oi_lf[s:e]), "installed cut missing: " + name
    assert TRAIL_LINE in oi_lf, "installed trail missing"
    assert hp_of(oi_lf, "ShockTrooperTeslaBoltProjectile") == "100.0"
    # ParticleSystem.ini still owned by fx-enhance and TeslaBoltSparks resolves
    ps_i, ps_own = eff2(PS_PATH)
    assert ps_own.lower() == "zzzz_fxenhance.big", "ParticleSystem owner drift: " + str(ps_own)
    assert re.search(r"(?m)^ParticleSystem\s+%s\b" % re.escape(TRAIL_PS), to_lf(ps_i))
    print("installed + audited OK in %s (owner=us for RotrShockTrooper.ini; cuts "
          "present; trail intact; projectile HP=100; ParticleSystem still fx-enhance)"
          % dst)

assert md5s[SPE_DIR] == md5s[SHW_DIR], "archives differ across mod dirs"
print("both installed archives md5-match: %s" % md5s[SPE_DIR])

# ================================================== 7. report
print("\n" + "=" * 66)
print("TESLA/SHOCK INFANTRY HP CUTS (~50%)")
print("=" * 66)
for name, om, nm in report_rows:
    print("  %-38s %s -> %s (Max+Initial)" % (name, om, nm))
print("  %-38s %s (PROJECTILE, left)" % ("ShockTrooperTeslaBoltProjectile", "100.0"))
print("  %-38s %s (chain nodes, UNATTACKABLE, left)" % ("ShockTrooperTeslaChainNode(+Heroic)", "50.0"))
print("  Shmel Trooper: separate file RotrShmelTrooper.ini (Rebalance handled it)")
print("DONE")
