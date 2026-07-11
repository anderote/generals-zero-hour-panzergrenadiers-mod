#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZInfantryScale.big - the INFANTRY-SCALE realism layer of
the Panzergrenadiers stack (ShockWave layers under GeneralsX / macOS).

WHAT IT DOES
  Shrinks every gameplay infantry model by ~10% for realistic human/vehicle
  proportions.  Two field edits per object, applied as pure top-layer file
  overrides (no lower layer is rebuilt):

    1. Scale = 0.95 added at the top level of each infantry Object.
       The engine DOUBLE-APPLIES Scale (it is baked into the W3D render
       prototype at load AND multiplied again per-frame), so the VISUAL size
       is ~= Scale**2.  0.95**2 = 0.9025 -> ~10% smaller on screen, matching
       ZH Reborn's effective infantry choice.  (The six CINE cheering units
       that already carry Scale = 0.8 are out of scope - see SCOPE below - so
       in practice every scaled object gains a fresh 0.95 line; the modify
       branch is kept only as a drift guard.)

    2. ShadowSizeX / ShadowSizeY multiplied by 0.90.  Shadow decals are sized
       from the template and do NOT inherit the model shrink, so they are
       scaled explicitly to match the ~0.90 visual footprint (every infantry
       shadow in the stack is 14 -> 12.6).  Objects with no ShadowSize fields
       are left alone (they use the engine default).

SCOPE (enumerated mechanically from the EFFECTIVE stack - the highest-priority
copy of each file across all installed archives sorting BELOW us):
  INCLUDE  every Object whose object-level KindOf line contains INFANTRY, all
           factions, every per-general clone, plus this stack's custom units
           (Tank_ChinaInfantryPanzergrenadier, the tesla Shock Trooper +
           _Var1, the Shmel Trooper, the Sharpshooter clone, TeslaInfantry).
           The visible angry-mob members and China-Infantry-general squad
           members ARE scaled (only their invisible nexus controllers are
           denied - see DENYLIST).  => 158 objects across 105 Object INI files.

  EXCLUDE from scope (NOT the gameplay roster, so left untouched):
     - CINE_* cinematic-only objects (mission intro/outro & challenge cutscene
       actors; never present in skirmish/MP, contribute nothing to the
       cross-faction realism goal).
     - maps\\ mission-embedded object definitions (e.g. maps\\md_gla11\\map.ini's
       scripted rebels; scenario config, not the roster, and scaling scripted
       mission units risks their spawn/scripting assumptions).
     These two categories are ALSO the only source of ShockWaveSPE vs
     ShockWave effective divergence (SPE overrides americacineunit.ini and
     adds the md_gla11 map); excluding them makes every shipped file
     byte-identical across both mod dirs, so ONE archive serves BOTH (verified
     in-build) - matching the sibling-layer single-artifact pattern.

DENYLIST (kept at Scale 1.0 on purpose, verified in-build):
     - HERO units, for battlefield readability: Black Lotus (x5 clones),
       Jarmen Kell (x5), Colonel Burton (x5) - matched by KindOf HERO.  The
       name match (Black Lotus / Jarmen Kell / Colonel Burton) additionally
       covers their non-HERO-tagged CINE clones, though those are already out
       of scope via the cinematic exclusion.  => 15 HERO objects denied.
     - MOB_NEXUS controller objects (the angry-mob & squad health-bar kluge -
       invisible controllers, not soldiers): GLAInfantryAngryMobNexus (Demo /
       Chem / vanilla - the CINE one is out of scope), the three
       Infa_ChinaInfantry{RedGuard,Minigunner,TankHunter}SquadNexus, and
       PlasmaBallOfDeathMaster.  => 7 MOB_NEXUS objects denied.
       (Denylist total as-applied: 22.  The visible angry-mob members and
       squad soldiers are NOT nexus objects and ARE scaled.)
     - The shared Parachute object (and every faction/vehicle parachute) is
       naturally out of scope: those are KindOf PARACHUTE, not INFANTRY, so
       they never enter the enumeration.  Documented, not specially handled.
     - No infantry "China Command Tank crew" object exists in the stack (the
       command-tank crew is not a KindOf INFANTRY object), so nothing to deny
       there.

PACKAGING: zzz-ZZZZZZZZZInfantryScale.big case-insensitively sorts:
     AFTER  zzz-ZZZZZZZZPanzergrenadier.big  (equal through 'zzz-zzzzzzzz',
            then char 13 'z' > 'p') -> we are the LAST Object-INI layer;
     BEFORE zzz_ControlBarPro*.big  ('-' 0x2D < '_' 0x5F at char 4) and
            zzzz_FXEnhance.big       ('-' < 'z' at char 4).
  Verified against the real directory listings of both mod dirs.  We touch
  ONLY Object INI files - never fx-enhance's FXList / ParticleSystem files -
  and never source from any archive sorting at or above us.

Depends on ../hotkey-addon/bigfile.py.  No git commits, no game launch.
"""
import os, re, sys, shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big, find_entry  # noqa: E402

ARCHIVE = "zzz-ZZZZZZZZZInfantryScale.big"
TAG = "zzz-ZZZZZZZZZInfantryScale"
SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW = os.path.expanduser("~/GeneralsX/mods/ShockWave")
MODDIRS = [SPE, SHW]
PRIMARY = SPE

SCALE_MULT = 0.95      # per-object Scale factor (visual ~= factor**2 due to engine double-apply)
SHADOW_MULT = 0.90     # shadow-decal factor (matches ~0.90 visual footprint)
SCALE_DEFAULT = "0.95"

# ---- drift guards (this build's decisions are valid only while these hold) ---
EXP_SCALED = 158
EXP_FILES = 105
# Denylist as it APPLIES to in-scope objects.  (The CINE_* hero clones -
# CINE_AmericaInfantryColonelBurton / CINE_ChinaInfantryBlackLotus /
# CINE_GLAInfantryJarmenKell - and CINE_GLAInfantryAngryMobNexus are removed
# by the cinematic exclusion BEFORE the denylist runs, so they are out of
# scope rather than denied; net effect identical - all stay Scale 1.0.)
EXP_DENIED = {"HERO": 15, "MOB_NEXUS": 7}

HERO_NAME_KEYS = ("blacklotus", "jarmenkell", "colonelburton")


def die(msg):
    print("BUILD FAILED:", msg)
    sys.exit(1)


def check(cond, msg):
    if not cond:
        die(msg)


# ------------------------------------------------------------------ EOL utils
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    check(raw.count("\r") == crlf, "stray CR")
    check(crlf == 0 or lf == 0, "mixed EOLs")
    return "\r\n" if crlf else "\n"


def to_lf(raw):
    return raw.replace("\r\n", "\n")


def from_lf(lf_text, eol):
    return lf_text.replace("\n", eol) if eol != "\n" else lf_text


def fmt(x):
    r = round(x, 4)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    return ("%.4f" % r).rstrip("0").rstrip(".")


# --------------------------------------------------------- object parsing (LF)
OBJ_HDR = re.compile(r"(?m)^Object[ \t]+(\S+)[ \t]*(?:;[^\n]*)?$")
END_TOP = re.compile(r"(?m)^End[ \t]*(?:;[^\n]*)?$")


def iter_blocks(lf):
    """Yield (name, block, start, end) for every top-level Object..End.
    Top-level End is at column 0; nested module Ends are indented, so END_TOP
    (anchored ^End) never matches them."""
    for m in OBJ_HDR.finditer(lf):
        m2 = END_TOP.search(lf, m.start())
        if not m2:
            continue
        yield m.group(1), lf[m.start():m2.end()], m.start(), m2.end()


def obj_field(block, name):
    m = re.search(r"(?mi)^[ \t]*%s[ \t]*=[ \t]*([^;\n]*)" % name, block)
    return m.group(1).strip() if m else None


def end_count(lf):
    return len(re.findall(r"(?mi)^End[ \t]*(?:;[^\n]*)?$", lf))


# ================================================== 1. effective stack (PRIMARY)
def load_effective(moddir):
    """lowerpath -> (archive, bytes, origpath), highest-priority (per-file)
    copy, from archives sorting strictly BELOW us (never ourselves/higher)."""
    arcs = sorted((f for f in os.listdir(moddir) if f.lower().endswith(".big")
                   and f.lower() < ARCHIVE.lower()),
                  key=str.lower, reverse=True)
    eff = {}
    for a in arcs:
        for e in read_big(os.path.join(moddir, a)):
            eff.setdefault(e.path.lower(), (a, e.data, e.path))
    return eff, arcs


eff, arcs = load_effective(PRIMARY)
print("effective stack loaded from %s (%d archives below us, %d files)"
      % (os.path.basename(PRIMARY), len(arcs), len(eff)))


# ================================================== 2. enumerate + classify
def deny_reason(name, kind):
    ks = kind.split()
    if "HERO" in ks:
        return "HERO"
    if "MOB_NEXUS" in ks:
        return "MOB_NEXUS"
    if any(h in name.lower() for h in HERO_NAME_KEYS):
        return "HERO_NAME"
    return None


targets = {}          # lowerpath -> [objname, ...]  (scaled)
denied = []           # (name, reason)
all_inf = 0
for p, (a, data, _op) in eff.items():
    if not p.endswith(".ini"):
        continue
    if p.startswith("maps\\"):          # scenario-embedded, out of scope
        continue
    lf = to_lf(data.decode("latin-1"))
    for name, block, _s, _e in iter_blocks(lf):
        kind = obj_field(block, "KindOf") or ""
        if "INFANTRY" not in kind.split():
            continue
        if name.upper().startswith("CINE_"):   # cinematic-only, out of scope
            continue
        all_inf += 1
        r = deny_reason(name, kind)
        if r:
            denied.append((name, r))
        else:
            check(p.startswith("data\\ini\\object\\"),
                  "scaled infantry outside Object tree: " + p)
            targets.setdefault(p, []).append(name)

scaled_count = sum(len(v) for v in targets.values())
den_counter = Counter(r for _n, r in denied)
print("infantry in scope: %d  (scaled %d in %d files, denied %d %s)"
      % (all_inf, scaled_count, len(targets), len(denied), dict(den_counter)))
check(scaled_count == EXP_SCALED, "scaled count drift: %d != %d" % (scaled_count, EXP_SCALED))
check(len(targets) == EXP_FILES, "file count drift: %d != %d" % (len(targets), EXP_FILES))
check(dict(den_counter) == EXP_DENIED, "denylist drift: %s != %s" % (dict(den_counter), EXP_DENIED))
# every custom unit is actually in the scaled set
for cu in ("Tank_ChinaInfantryPanzergrenadier", "Tank_ChinaInfantryShockTrooper",
           "Tank_ChinaInfantryShmelTrooper", "Tank_ChinaInfantrySharpshooter"):
    check(any(cu in names for names in targets.values()), "custom unit not scaled: " + cu)
print("drift guards OK (158 scaled / 105 files / deny 15 HERO + 7 MOB_NEXUS; "
      "CINE hero/nexus clones out of scope via cinematic exclusion)")

# both dirs must agree byte-for-byte on every file we ship (so one archive
# serves both) - the scope exclusions above are exactly what guarantees this
eff_shw, _ = load_effective(SHW)
for p in targets:
    check(p in eff_shw, "shipped file absent from ShockWave dir: " + p)
    check(eff_shw[p][1] == eff[p][1],
          "shipped file differs between mod dirs (needs per-dir build): " + p)
print("cross-dir source parity OK (all %d shipped files byte-identical in both mod dirs)"
      % len(targets))


# ================================================== 3. patch each file
def edit_block(block, name):
    """Return (new_block, changes) where changes is [(old_line|None, new_line)]."""
    changes = []
    # --- Scale (modify existing top-level Scale, else insert after header) ---
    sc = re.search(r"(?m)^([ \t]*)Scale([ \t]*=[ \t]*)([0-9.]+)[ \t]*(;[^\n]*)?$",
                   block)
    if sc:
        oldval = sc.group(3)
        newval = fmt(round(float(oldval) * SCALE_MULT, 4))
        old_line = sc.group(0)
        new_line = ("%sScale%s%s ; %s: was %s (x%s; engine double-applies Scale "
                    "-> ~10%% visual shrink)"
                    % (sc.group(1), sc.group(2), newval, TAG, oldval,
                       fmt(SCALE_MULT)))
        block = block[:sc.start()] + new_line + block[sc.end():]
        changes.append((old_line, new_line))
    else:
        nl = block.index("\n")
        scale_line = ("  Scale = %s ; %s: infantry realism ~10%% shrink "
                      "(engine double-applies Scale -> visual ~0.90)"
                      % (SCALE_DEFAULT, TAG))
        block = block[:nl] + "\n" + scale_line + block[nl:]
        changes.append((None, scale_line))
    # --- ShadowSizeX / ShadowSizeY (multiply if present) ---
    for axis in ("X", "Y"):
        m = re.search(r"(?m)^([ \t]*ShadowSize%s[ \t]*=[ \t]*)([0-9.]+)[ \t]*(;[^\n]*)?$"
                      % axis, block)
        if not m:
            continue
        old_comment = (m.group(3) or "").lstrip(";").strip()
        check(old_comment == "", "unexpected non-empty ShadowSize%s comment on %s: %r"
              % (axis, name, old_comment))
        oldval = m.group(2)
        newval = fmt(round(float(oldval) * SHADOW_MULT, 4))
        old_line = m.group(0)
        new_line = "%s%s ; %s: was %s (shadow x%s)" % (m.group(1), newval, TAG,
                                                       oldval, fmt(SHADOW_MULT))
        block = block[:m.start()] + new_line + block[m.end():]
        changes.append((old_line, new_line))
    return block, changes


patched = {}          # lowerpath -> patched bytes (native EOL)
orig_path = {}        # lowerpath -> original-cased path (for the BIG index)
n_scale_ins = n_scale_mod = n_shadow = 0

for p in sorted(targets):
    a, data, opath = eff[p]
    orig_path[p] = opath
    raw = data.decode("latin-1")
    eol = eol_of(raw)
    lf = to_lf(raw)
    tset = set(targets[p])

    # apply edits object-by-object (each block is a unique substring in lf)
    exp_removed, exp_added = Counter(), Counter()
    new_lf = lf
    for name in targets[p]:
        # re-locate the block in the (possibly already edited) text
        blk = None
        for nm, block, _s, _e in iter_blocks(new_lf):
            if nm == name:
                blk = block
                break
        check(blk is not None, "lost object %s in %s" % (name, p))
        newblk, changes = edit_block(blk, name)
        check(new_lf.count(blk) == 1, "non-unique block for %s in %s" % (name, p))
        new_lf = new_lf.replace(blk, newblk, 1)
        for old, new in changes:
            if old is not None:
                exp_removed[old] += 1
            exp_added[new] += 1
            if old is None:
                n_scale_ins += 1
            elif "Scale" in new and "shadow" not in new:
                n_scale_mod += 1
            else:
                n_shadow += 1

    # --- per-file line-multiset audit: only the recorded lines changed ----
    # (order-independent Counter difference - robust for files with many
    # edits and abundant repeated lines like blanks / "End")
    old_c, new_c = Counter(lf.split("\n")), Counter(new_lf.split("\n"))
    got_added = new_c - old_c
    got_removed = old_c - new_c
    check(got_added == exp_added, "%s: added-line audit mismatch: %r"
          % (p, (got_added - exp_added, exp_added - got_added)))
    check(got_removed == exp_removed, "%s: removed-line audit mismatch: %r"
          % (p, (got_removed - exp_removed, exp_removed - got_removed)))

    # --- block-balance: no End added/removed (pure field edits) -----------
    check(end_count(new_lf) == end_count(lf), "%s: End count changed" % p)

    # --- non-target objects byte-identical; target objects gained Scale ----
    src_blocks = {nm: block for nm, block, _s, _e in iter_blocks(lf)}
    new_blocks = {nm: block for nm, block, _s, _e in iter_blocks(new_lf)}
    check(set(src_blocks) == set(new_blocks), "%s: object set changed" % p)
    for nm in src_blocks:
        if nm in tset:
            check(src_blocks[nm] != new_blocks[nm], "%s: target %s unchanged" % (p, nm))
            check(re.search(r"(?m)^[ \t]*Scale[ \t]*=", new_blocks[nm]),
                  "%s: %s missing Scale after edit" % (p, nm))
        else:
            check(src_blocks[nm] == new_blocks[nm],
                  "%s: NON-TARGET %s was modified!" % (p, nm))

    # --- text OUTSIDE all object blocks byte-identical ---------------------
    def outside(text):
        spans, pos, out = [], 0, []
        for _nm, _b, s, e in iter_blocks(text):
            out.append(text[pos:s]); pos = e
        out.append(text[pos:])
        return "".join(out)
    check(outside(lf) == outside(new_lf), "%s: inter-object text changed" % p)

    patched[p] = from_lf(new_lf, eol).encode("latin-1")

check(len(patched) == EXP_FILES, "patched file count")
print("patched %d files: +%d Scale inserts, %d Scale modifies, %d shadow edits"
      % (len(patched), n_scale_ins, n_scale_mod, n_shadow))
print("per-file audits OK (line-multiset diff, End-balance, non-target byte-survival, "
      "inter-object byte-survival)")


# ================================================== 4. package
entries = [BigEntry(orig_path[p], patched[p]) for p in sorted(patched)]
blob = write_big(entries)
rt = read_big(blob)
check([(e.path, e.data) for e in rt] == [(e.path, e.data) for e in entries],
      "BIG round-trip mismatch")
out_path = os.path.join(HERE, ARCHIVE)
prev = open(out_path, "rb").read() if os.path.exists(out_path) else None
open(out_path, "wb").write(blob)
print("wrote %s (%d files, %d bytes)%s" % (out_path, len(entries), len(blob),
      " [hash-idempotent]" if prev == blob else ""))

shipped_lc = {e.path.lower() for e in entries}


# ================================================== 5. sort order (both dirs)
for d in MODDIRS:
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {ARCHIVE}, key=str.lower)
    i = listing.index(ARCHIVE)
    below, above = listing[:i], listing[i + 1:]
    check(any(b.lower() == "zzz-zzzzzzzzpanzergrenadier.big" for b in below),
          "%s: Panzergrenadier must sort below us" % d)
    check(listing[i - 1].lower() == "zzz-zzzzzzzzpanzergrenadier.big",
          "%s: expected Panzergrenadier immediately below us, got %s" % (d, listing[i - 1]))
    for a in above:
        check(a.lower().startswith("zzz_controlbarpro") or a.lower().startswith("zzzz_"),
              "%s: unexpected archive above us: %s" % (d, a))
    check(any(a.lower().startswith("zzz_controlbarpro") for a in above),
          "%s: ControlBarPro must sort above us" % d)
    check(any(a.lower().startswith("zzzz_fxenhance") for a in above),
          "%s: FXEnhance must sort above us" % d)
    # no higher-sorting archive may claim any path we ship
    for later in above:
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                check(e.path.lower() not in shipped_lc,
                      "%s/%s (sorts above us) claims %s" % (d, later, e.path))
    print("sort order OK in %s: ...%s < %s < %s... (no higher archive claims our paths)"
          % (os.path.basename(d), listing[i - 1], ARCHIVE, listing[i + 1]))


# ================================================== 6. install + re-read
for d in MODDIRS:
    dst = os.path.join(d, ARCHIVE)
    shutil.copyfile(out_path, dst)
    back = read_big(dst)
    check([e.path for e in back] == [e.path for e in entries], "install path mismatch: " + d)
    for x, y in zip(back, entries):
        check(x.data == y.data, "install byte mismatch %s in %s" % (x.path, d))
    print("installed + re-read OK:", dst)


# ================================================== 7. post-install audit (both)
def enumerate_scaled(eff_map):
    out = {}
    for p, (a, data) in eff_map.items():
        if not p.endswith(".ini") or p.startswith("maps\\"):
            continue
        lf = to_lf(data.decode("latin-1"))
        for name, block, _s, _e in iter_blocks(lf):
            kind = obj_field(block, "KindOf") or ""
            if "INFANTRY" not in kind.split() or name.upper().startswith("CINE_"):
                continue
            if deny_reason(name, kind):
                continue
            out[name] = obj_field(block, "Scale")
    return out


for d in MODDIRS:
    arcs2 = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")),
                   key=str.lower, reverse=True)
    cache = {a: read_big(os.path.join(d, a)) for a in arcs2}

    def eff2(path):
        want = path.lower()
        for a in arcs2:
            for e in cache[a]:
                if e.path.lower() == want:
                    return e.data.decode("latin-1"), a
        return None, None

    # every shipped path is now owned by us with our exact bytes
    for e in entries:
        data, got = eff2(e.path)
        check(got == ARCHIVE, "%s: %s effective owner is %s" % (d, e.path, got))
        check(data.encode("latin-1") == e.data, "%s: %s bytes differ" % (d, e.path))

    # effective-space re-enumeration: exactly 158 scaled, each now Scale 0.95;
    # denied heroes/nexus still have NO Scale (untouched at default 1.0)
    eff_post = {}
    for a in arcs2:
        for x in cache[a]:
            eff_post.setdefault(x.path.lower(), (a, x.data))
    scaled_post = enumerate_scaled(eff_post)
    check(len(scaled_post) == EXP_SCALED, "%s: post-install scaled count %d"
          % (d, len(scaled_post)))
    for nm, sv in scaled_post.items():
        check(sv is not None, "%s: %s has no Scale post-install" % (d, nm))
        check(abs(float(sv) - float(SCALE_DEFAULT)) < 1e-9
              or abs(float(sv) - round(0.8 * SCALE_MULT, 4)) < 1e-9,
              "%s: %s unexpected Scale %s" % (d, nm, sv))
    # denied objects untouched (no Scale line, still 1.0)
    for dn, reason in denied:
        blk = None
        for a in arcs2:
            for x in cache[a]:
                if not x.path.lower().endswith(".ini"):
                    continue
                lf = to_lf(x.data.decode("latin-1"))
                for name, block, _s, _e in iter_blocks(lf):
                    if name == dn:
                        blk = block
                        break
                if blk:
                    break
            if blk:
                break
        check(blk is not None, "%s: denied %s vanished" % (d, dn))
        check(not re.search(r"(?m)^[ \t]*Scale[ \t]*=", blk),
              "%s: denied %s (%s) gained a Scale line!" % (d, dn, reason))
    print("post-install effective audit OK in %s (158 scaled @0.95, %d denied @1.0)"
          % (os.path.basename(d), len(denied)))

print("ALL CHECKS PASSED")
