#!/usr/bin/env python3
"""Build the FX-enhancement data mod for C&C Generals Zero Hour (GeneralsX port).

Two archives are produced from surgically-transformed copies of the shipped
INIs (ParticleSystem.ini + FXList.ini):

  * zzzz_FXEnhance.big  -> ShockWave / ShockWaveSPE mod dirs (later-alpha wins)
  * 000_FXEnhanceZH.big -> GeneralsZH game dir            (earlier-alpha wins)

The transform is VISUAL-ONLY and byte-preserving: it never touches a byte it
does not intentionally change (line endings, comments, spacing all preserved).
The port's INI parser hard-crashes on malformed lines, so every generated line
is validated against the engine parse tables and against real shipped data.

What it changes (see README.md for the full spec):
  * FXList.ini : injects a warm LightPulse nugget into every "explosion" FXList
                 (one that already screen-shakes via a ViewShake nugget) that
                 does not already have a LightPulse.
  * ParticleSystem.ini : scales BurstCount / Size (and Lifetime for smoke) of
                 the particle systems those explosions spawn, within hard
                 safety caps derived from the engine's 2048/system render
                 ceiling and 10000 global particle cap.

Idempotent: a "; FXEnhance v1" marker is prepended to each transformed file and
a re-run of the transform on its own output refuses to double-apply.

Usage:
  python3 build.py                       # guard + build + install (default)
  python3 build.py --no-install          # build to ./build only, do not deploy
  python3 build.py --allow-layer-conflict # proceed past the step-1 layer guard
"""

import argparse
import difflib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hotkey-addon"))
from bigfile import read_big, write_big_file, BigEntry  # noqa: E402

# ----------------------------------------------------------------------------
# configuration
# ----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
GAME_DIR = Path.home() / "GeneralsX/GeneralsZH"
MOD_DIRS = [Path.home() / "GeneralsX/mods/ShockWave",
            Path.home() / "GeneralsX/mods/ShockWaveSPE"]
# The mod source is resolved from the ShockWaveSPE dir (its INIs are byte
# identical to ShockWave's), then the built archive is installed to BOTH.
MOD_SRC_DIR = Path.home() / "GeneralsX/mods/ShockWaveSPE"

TARGETS = ["Data\\INI\\ParticleSystem.ini", "Data\\INI\\FXList.ini"]

MOD_BIG_NAME = "zzzz_FXEnhance.big"
VANILLA_BIG_NAME = "000_FXEnhanceZH.big"

MARKER = "; FXEnhance v1"

# transform tunables (from the brief) -----------------------------------------
BURST_MULT = 1.75
BURST_CAP = 120           # per keyframe value
SIZE_MULT = 1.25
LIFETIME_MULT = 1.3       # smoke systems only
SAFETY_ESTIMATE_CAP = 2000   # peak concurrent particles per system

SMOKE_RE = re.compile(r"smoke", re.I)
SLAVE_EXPLOSION_RE = re.compile(r"explosion|fireball|flame", re.I)

# LightPulse nugget to inject. Field spelling/order copied from a REAL shipped
# LightPulse nugget in FXList.ini (Color/Radius/IncreaseTime/DecreaseTime);
# RadiusAsPercentOfObjectSize is in the FXList.cpp parse table but is absent
# from real data so it is dropped, per the brief. Values are the brief's warm
# orange flash. 2-space nugget indent / 4-space field indent matches the file.
LIGHTPULSE_BLOCK = [
    "  LightPulse",
    "    Color = R:255 G:156 B:64",
    "    Radius = 80",
    "    IncreaseTime = 80",
    "    DecreaseTime = 600",
    "  End",
]
_LP_LINE_RE = re.compile(
    r"^\s*(LightPulse|Color\s*=|Radius\s*=|IncreaseTime\s*=|DecreaseTime\s*=|End)\s*",
    re.I)


# ----------------------------------------------------------------------------
# lossless, EOL-preserving line handling
# ----------------------------------------------------------------------------
# Line-ending convention varies per file/source: vanilla uses \r\n for both
# INIs; ShockWave's FXList.ini is pure \n while its ParticleSystem.ini is \r\n.
# We detect the file's single convention and split/join on exactly that, which
# is byte-lossless for a uniformly-terminated file.
def detect_eol(text):
    return "\r\n" if "\r\n" in text else "\n"


def assert_uniform_eol(text, label):
    b = text.encode("latin-1")
    crlf = b.count(b"\r\n")
    lone_n = b.count(b"\n") - crlf
    if crlf and lone_n:
        raise AssertionError(f"[{label}] mixed line endings (crlf={crlf}, lone_n={lone_n}); "
                             "refusing to transform")


def split_lines(text, eol):
    return text.split(eol)


def join_lines(lines, eol):
    return eol.join(lines)


def has_marker(text):
    # first physical line, tolerating either convention
    return text.split("\n", 1)[0].rstrip("\r").strip() == MARKER


def add_marker(text, eol):
    return MARKER + eol + text


def fmt_like(orig_tok, newval):
    """Format newval to match the decimal style of orig_tok."""
    if "." in orig_tok:
        decimals = len(orig_tok.split(".", 1)[1])
        return f"{newval:.{decimals}f}"
    return str(int(round(newval)))


# ----------------------------------------------------------------------------
# FXList.ini transform
# ----------------------------------------------------------------------------
def _fxlist_blocks(lines):
    """Yield (name, start, end_exclusive) for each depth-0 FXList block.

    end_exclusive is one past the block's terminating column-0 `End`.
    Nesting is tracked by: a non-comment, non-empty, non-`End` line with no
    `=` opens a nested nugget block; `End` closes the innermost.
    """
    n = len(lines)
    i = 0
    while i < n:
        m = re.match(r"^FXList\s+(\S+)", lines[i])
        if m:
            start = i
            depth = 1
            i += 1
            while i < n and depth > 0:
                code = lines[i].split(";", 1)[0].strip()
                if not code:
                    i += 1
                    continue
                if re.match(r"^End\b", code):
                    depth -= 1
                elif "=" not in code:
                    depth += 1
                i += 1
            yield (m.group(1), start, i)
        else:
            i += 1


def _block_has_nugget(lines, start, end, keyword):
    pat = re.compile(r"^\s*" + keyword + r"\b", re.I)
    for j in range(start, end):
        code = lines[j].split(";", 1)[0]
        if pat.match(code):
            return True
    return False


def _collect_particle_names(lines, start, end):
    """Names referenced by `ParticleSystem`/`AttachedSystem` nuggets in a block.

    DEVIATION FROM BRIEF: shipped FXList.ini has no `ParticleSystem = <name>`
    form; systems are named by a `Name = <sys>` field inside a `ParticleSystem`
    (or `AttachedParticleSystem`) nugget. We collect those Name values.
    """
    names = set()
    j = start
    while j < end:
        code = lines[j].split(";", 1)[0].strip()
        if re.match(r"^(ParticleSystem|AttachedParticleSystem|AttachedSystem)\b",
                    code, re.I) and "=" not in code:
            k = j + 1
            depth = 1
            while k < end and depth > 0:
                c = lines[k].split(";", 1)[0].strip()
                if re.match(r"^End\b", c):
                    depth -= 1
                elif c and "=" not in c:
                    depth += 1
                elif depth == 1:
                    nm = re.match(r"^Name\s*=\s*(\S+)", c, re.I)
                    if nm:
                        names.add(nm.group(1))
                k += 1
        j += 1
    return names


def transform_fxlist(text):
    """Return (new_text, stats, collected_system_names)."""
    stats = {"explosion": 0, "already_lp": 0, "injected": 0}
    if has_marker(text):
        stats["already_enhanced"] = True
        return text, stats, set()

    assert_uniform_eol(text, "FXList")
    eol = detect_eol(text)
    lines = split_lines(text, eol)
    collected = set()
    insertions = []  # (index_to_insert_before, [lines])

    for name, start, end in _fxlist_blocks(lines):
        if not _block_has_nugget(lines, start, end, "ViewShake"):
            continue
        stats["explosion"] += 1
        collected |= _collect_particle_names(lines, start, end)
        if _block_has_nugget(lines, start, end, "LightPulse"):
            stats["already_lp"] += 1
            continue
        # insert before the block's terminating column-0 End (index end-1)
        insertions.append((end - 1, list(LIGHTPULSE_BLOCK)))
        stats["injected"] += 1

    for idx, block in sorted(insertions, key=lambda t: t[0], reverse=True):
        lines[idx:idx] = block

    new_text = add_marker(join_lines(lines, eol), eol)
    return new_text, stats, collected


# ----------------------------------------------------------------------------
# ParticleSystem.ini transform
# ----------------------------------------------------------------------------
def _ps_blocks(lines):
    """Return dict name -> (start, end_exclusive) for each ParticleSystem block."""
    blocks = {}
    n = len(lines)
    i = 0
    while i < n:
        m = re.match(r"^ParticleSystem\s+(\S+)", lines[i])
        if m:
            start = i
            i += 1
            while i < n and not re.match(r"^End\b", lines[i]):
                i += 1
            # i now points at the column-0 End; end_exclusive = i+1
            blocks[m.group(1)] = (start, min(i + 1, n))
            i += 1
        else:
            i += 1
    return blocks


def _field_value(lines, start, end, key):
    pat = re.compile(r"^\s*" + key + r"\s*=\s*(.*?)\s*$", re.I)
    for j in range(start, end):
        code = lines[j].split(";", 1)[0]
        m = pat.match(code)
        if m:
            return m.group(1)
    return None


def _floats(s):
    return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", s)]


def _slave_names(lines, start, end):
    out = []
    for j in range(start, end):
        code = lines[j].split(";", 1)[0]
        m = re.match(r"^\s*SlaveSystem\s*=\s*(\S+)", code, re.I)
        if m:
            out.append(m.group(1))
    return out


def transform_particlesystem(text, collected):
    """Return (new_text, stats). `collected` = names referenced by explosion FXLists."""
    stats = {"scaled": 0, "skips": []}
    if has_marker(text):
        stats["already_enhanced"] = True
        return text, stats

    assert_uniform_eol(text, "ParticleSystem")
    eol = detect_eol(text)
    lines = split_lines(text, eol)
    blocks = _ps_blocks(lines)

    # scale set: collected systems present + their explosion-ish slaves
    scale_set = set()
    for name in collected:
        if name in blocks:
            scale_set.add(name)
    for name in list(scale_set):
        s, e = blocks[name]
        for sl in _slave_names(lines, s, e):
            if sl in blocks and SLAVE_EXPLOSION_RE.search(sl):
                scale_set.add(sl)

    for name in sorted(collected):
        if name not in blocks:
            stats["skips"].append(f"{name}: referenced by FX but no ParticleSystem block")

    for name in sorted(scale_set):
        s, e = blocks[name]
        priority = (_field_value(lines, s, e, "Priority") or "").strip()
        ptype = (_field_value(lines, s, e, "Type") or "").strip()
        is_oneshot = (_field_value(lines, s, e, "IsOneShot") or "").strip().lower() in ("yes", "true", "1")
        pname = (_field_value(lines, s, e, "ParticleName") or "")

        if ptype.upper() == "VOLUME_PARTICLE":
            stats["skips"].append(f"{name}: skipped (Type=VOLUME_PARTICLE, 6x fill cost)")
            continue
        if priority.upper() == "WEAPON_TRAIL":
            stats["skips"].append(f"{name}: skipped (Priority=WEAPON_TRAIL, continuous emitter)")
            continue

        is_smoke = bool(SMOKE_RE.search(pname) or SMOKE_RE.search(name))

        burst_raw = _field_value(lines, s, e, "BurstCount")
        life_raw = _field_value(lines, s, e, "Lifetime")
        bd_raw = _field_value(lines, s, e, "BurstDelay")

        burst_vals = _floats(burst_raw) if (burst_raw and "%" not in burst_raw) else []
        life_vals = _floats(life_raw) if (life_raw and "%" not in life_raw) else []
        bd_vals = _floats(bd_raw) if (bd_raw and "%" not in bd_raw) else []

        # ---- safety cap: peak concurrent particle estimate ----
        burst_factor = 1.0
        if burst_vals:
            burst_scaled_max = max(min(round(v * BURST_MULT), BURST_CAP) for v in burst_vals)
            life_max_scaled = 0.0
            if life_vals:
                life_max_scaled = max(life_vals) * (LIFETIME_MULT if is_smoke else 1.0)
            if is_oneshot:
                estimate = burst_scaled_max  # single generation
            else:
                # BurstDelay and Lifetime are in frames; the shortest meaningful
                # emission interval is one frame, so floor BurstDelay at 1.0.
                bd_min = min(bd_vals) if bd_vals else 1.0
                bd_min = max(bd_min, 1.0)
                estimate = burst_scaled_max * (life_max_scaled / bd_min) if life_max_scaled else burst_scaled_max
            if estimate > SAFETY_ESTIMATE_CAP:
                burst_factor = SAFETY_ESTIMATE_CAP / estimate
                stats["skips"].append(
                    f"{name}: BurstCount multiplier reduced x{burst_factor:.3f} "
                    f"(peak estimate {estimate:.0f} > {SAFETY_ESTIMATE_CAP})")

        changed = False
        for j in range(s, e):
            raw = lines[j]
            code, sep, comment = raw.partition(";")
            m = re.match(r"^(\s*)(BurstCount|Size|Lifetime)(\s*=\s*)(.*)$", code, re.I)
            if not m:
                continue
            key = m.group(2)
            keyl = key.lower()
            if keyl == "lifetime" and not is_smoke:
                continue  # lifetime only scaled for smoke systems
            valpart = m.group(4)
            if "%" in valpart:
                stats["skips"].append(f"{name}.{key}: skipped (contains %)")
                continue
            if not re.search(r"\d", valpart):
                stats["skips"].append(f"{name}.{key}: skipped (no numeric value)")
                continue

            if keyl == "burstcount":
                def repl(mm):
                    v = float(mm.group(0))
                    nv = min(round(v * BURST_MULT * burst_factor), BURST_CAP)
                    return fmt_like(mm.group(0), nv)
            elif keyl == "size":
                def repl(mm):
                    return fmt_like(mm.group(0), float(mm.group(0)) * SIZE_MULT)
            else:  # lifetime
                def repl(mm):
                    return fmt_like(mm.group(0), float(mm.group(0)) * LIFETIME_MULT)

            try:
                new_val = re.sub(r"[-+]?\d*\.?\d+", repl, valpart)
            except ValueError:
                stats["skips"].append(f"{name}.{key}: skipped (float parse failed)")
                continue
            new_code = m.group(1) + m.group(2) + m.group(3) + new_val
            # reattach the original inline comment verbatim if the line had one
            lines[j] = new_code + sep + comment
            changed = True
        if changed:
            stats["scaled"] += 1

    new_text = add_marker(join_lines(lines, eol), eol)
    return new_text, stats


# ----------------------------------------------------------------------------
# verification
# ----------------------------------------------------------------------------
def verify_diff(orig_text, new_text, expect_injections, label):
    """Assert every changed line matches an allowed pattern. Raises on violation."""
    if not has_marker(new_text):
        raise AssertionError(f"[{label}] output missing marker comment")
    eol = detect_eol(orig_text)
    # strip the marker line for a fair body diff
    new_body = new_text.split(eol, 1)[1]
    a = split_lines(orig_text, eol)
    b = split_lines(new_body, eol)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    scale_key_re = re.compile(r"^\s*(BurstCount|Size|Lifetime)\s*=", re.I)
    injected = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            raise AssertionError(f"[{label}] disallowed deletion at line {i1}: {a[i1:i2]!r}")
        if tag == "replace":
            if (i2 - i1) != (j2 - j1):
                raise AssertionError(f"[{label}] replace changed line count at {i1}: {a[i1:i2]!r} -> {b[j1:j2]!r}")
            for oa, ob in zip(a[i1:i2], b[j1:j2]):
                if not (scale_key_re.match(oa) and scale_key_re.match(ob)):
                    raise AssertionError(f"[{label}] disallowed change: {oa!r} -> {ob!r}")
                ka = scale_key_re.match(oa).group(1).lower()
                kb = scale_key_re.match(ob).group(1).lower()
                if ka != kb:
                    raise AssertionError(f"[{label}] key mutated: {oa!r} -> {ob!r}")
        elif tag == "insert":
            for ln in b[j1:j2]:
                if not _LP_LINE_RE.match(ln):
                    raise AssertionError(f"[{label}] disallowed inserted line: {ln!r}")
                if re.match(r"^\s*LightPulse\s*$", ln):
                    injected += 1
    if injected != expect_injections:
        raise AssertionError(f"[{label}] LightPulse insert count {injected} != expected {expect_injections}")
    return injected


def verify_line_endings(orig_text, new_text, added_lines, label):
    """Convention must be preserved exactly; EOL count grows by added_lines only."""
    ob = orig_text.encode("latin-1")
    nb = new_text.encode("latin-1")
    o_crlf, n_crlf = ob.count(b"\r\n"), nb.count(b"\r\n")
    o_lone, n_lone = ob.count(b"\n") - o_crlf, nb.count(b"\n") - n_crlf
    if "\r\n" in orig_text:  # CRLF file
        if n_lone != 0:
            raise AssertionError(f"[{label}] introduced lone \\n into a CRLF file")
        if n_crlf != o_crlf + added_lines:
            raise AssertionError(f"[{label}] CRLF count {n_crlf} != {o_crlf}+{added_lines}")
    else:  # LF file
        if n_crlf != 0:
            raise AssertionError(f"[{label}] introduced \\r\\n into an LF file")
        if n_lone != o_lone + added_lines:
            raise AssertionError(f"[{label}] LF count {n_lone} != {o_lone}+{added_lines}")
    return n_crlf or n_lone


def verify_block_counts(orig_text, new_text, injected, is_fxlist, label):
    eol = detect_eol(orig_text)
    a = split_lines(orig_text, eol)
    # skip marker line in new
    b = split_lines(new_text.split(eol, 1)[1], eol)
    col0_a = sum(1 for L in a if re.match(r"^End\b", L))
    col0_b = sum(1 for L in b if re.match(r"^End\b", L))
    if col0_a != col0_b:
        raise AssertionError(f"[{label}] column-0 End (top-level block) count changed {col0_a} -> {col0_b}")
    end_a = sum(1 for L in a if re.match(r"^\s*End\b", L))
    end_b = sum(1 for L in b if re.match(r"^\s*End\b", L))
    expected = end_a + (injected if is_fxlist else 0)
    if end_b != expected:
        raise AssertionError(f"[{label}] total End count {end_b} != {end_a}+{injected}={expected}")
    return col0_a, end_b


def verify_roundtrip(new_fx, new_ps):
    """Second pass on our own output must refuse to double-apply."""
    fx2, s1, c1 = transform_fxlist(new_fx)
    ps2, s2 = transform_particlesystem(new_ps, set())
    if not s1.get("already_enhanced") or fx2 != new_fx:
        raise AssertionError("FXList round-trip: transform re-applied (not idempotent)")
    if not s2.get("already_enhanced") or ps2 != new_ps:
        raise AssertionError("ParticleSystem round-trip: transform re-applied (not idempotent)")


# ----------------------------------------------------------------------------
# source resolution + layer guard
# ----------------------------------------------------------------------------
OWN_BIGS = {MOD_BIG_NAME, VANILLA_BIG_NAME}


def _is_base_big(name):
    return name.startswith("!") or name.startswith("zz_SPE_")


def effective_ini_mod(target):
    """Inside a mod dir, LATER-alphabetical archive wins; skip our own output."""
    winner = None
    for big in sorted(MOD_SRC_DIR.glob("*.big")):
        if big.name in OWN_BIGS:
            continue
        for e in read_big(big):
            if e.path.lower() == target.lower():
                winner = (big.name, e.data)
    if winner is None:
        raise FileNotFoundError(f"{target} not found in {MOD_SRC_DIR}")
    return winner


def effective_ini_vanilla(target):
    """In the game dir, EARLIER-alphabetical wins; skip our own output."""
    for big in sorted(GAME_DIR.glob("*.big")):
        if big.name in OWN_BIGS:
            continue
        for e in read_big(big):
            if e.path.lower() == target.lower():
                return (big.name, e.data)
    raise FileNotFoundError(f"{target} not found in {GAME_DIR}")


def layer_conflicts():
    """Custom (non-base, non-own) mod layers already containing a target INI."""
    tset = {t.lower() for t in TARGETS}
    conflicts = []
    for md in MOD_DIRS:
        for big in sorted(md.glob("*.big")):
            if _is_base_big(big.name) or big.name in OWN_BIGS:
                continue
            try:
                hits = [e.path for e in read_big(big) if e.path.lower() in tset]
            except Exception as ex:  # noqa: BLE001
                hits = [f"<read error: {ex}>"]
            if hits:
                conflicts.append((md.name, big.name, hits))
    return conflicts


# ----------------------------------------------------------------------------
# build a variant
# ----------------------------------------------------------------------------
def build_variant(label, ps_src, fx_src):
    """ps_src / fx_src are (archive_name, bytes). Returns (entries, report)."""
    fx_text = fx_src[1].decode("latin-1")
    ps_text = ps_src[1].decode("latin-1")

    new_fx, fx_stats, collected = transform_fxlist(fx_text)
    new_ps, ps_stats = transform_particlesystem(ps_text, collected)

    # ---- verification ----
    injected = verify_diff(fx_text, new_fx, fx_stats["injected"], f"{label}/FXList")
    verify_diff(ps_text, new_ps, 0, f"{label}/ParticleSystem")
    # added EOLs = 1 marker line + one per injected LightPulse-block line
    verify_line_endings(fx_text, new_fx, 1 + len(LIGHTPULSE_BLOCK) * injected, f"{label}/FXList")
    verify_line_endings(ps_text, new_ps, 1, f"{label}/ParticleSystem")
    fx_blocks = verify_block_counts(fx_text, new_fx, injected, True, f"{label}/FXList")
    ps_blocks = verify_block_counts(ps_text, new_ps, 0, False, f"{label}/ParticleSystem")
    verify_roundtrip(new_fx, new_ps)

    entries = [
        BigEntry("Data\\INI\\ParticleSystem.ini", new_ps.encode("latin-1")),
        BigEntry("Data\\INI\\FXList.ini", new_fx.encode("latin-1")),
    ]
    report = {
        "label": label,
        "fx_src": fx_src[0], "ps_src": ps_src[0],
        "fx_src_size": len(fx_src[1]), "ps_src_size": len(ps_src[1]),
        "fx_stats": fx_stats, "ps_stats": ps_stats,
        "collected": len(collected),
        "fx_blocks": fx_blocks, "ps_blocks": ps_blocks,
    }
    return entries, report


def print_report(r):
    print(f"\n=== {r['label']} variant ===")
    print(f"  source FXList.ini        : {r['fx_src']} ({r['fx_src_size']} bytes)")
    print(f"  source ParticleSystem.ini: {r['ps_src']} ({r['ps_src_size']} bytes)")
    fx = r["fx_stats"]
    print(f"  explosion FXLists        : {fx['explosion']} "
          f"(already had LightPulse: {fx['already_lp']})")
    print(f"  LightPulses injected     : {fx['injected']}")
    print(f"  particle systems referenced: {r['collected']}")
    print(f"  particle systems scaled  : {r['ps_stats']['scaled']}")
    print(f"  FXList blocks (col0 End / total End): {r['fx_blocks']}")
    print(f"  ParticleSystem blocks (col0 End / total End): {r['ps_blocks']}")
    skips = r["ps_stats"]["skips"]
    print(f"  skips / caps ({len(skips)}):")
    for s in skips:
        print(f"      - {s}")


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-install", action="store_true",
                    help="build to ./build only; do not copy into game/mod dirs")
    ap.add_argument("--allow-layer-conflict", action="store_true",
                    help="proceed even though other custom layers modify the target INIs")
    args = ap.parse_args()

    build_dir = HERE / "build"
    build_dir.mkdir(exist_ok=True)

    # ---- Step 1 guard: other custom layers already own these INIs? ----
    conflicts = layer_conflicts()
    if conflicts:
        print("LAYER-ORDERING CONFLICT: existing custom layers already contain the "
              "target INIs.\nA whole-file .big replacement by this mod would sit on "
              "top of / be overridden against them:")
        for md, big, hits in conflicts:
            print(f"  {md}/{big}: {', '.join(hits)}")
        if not args.allow_layer_conflict:
            print("\nSTOPPING (a layer-ordering decision is needed). "
                  "Re-run with --allow-layer-conflict to proceed once resolved.")
            return 2
        print("\n--allow-layer-conflict set: proceeding.\n")

    # ---- resolve sources ----
    mod_ps = effective_ini_mod("Data\\INI\\ParticleSystem.ini")
    mod_fx = effective_ini_mod("Data\\INI\\FXList.ini")
    van_ps = effective_ini_vanilla("Data\\INI\\ParticleSystem.ini")
    van_fx = effective_ini_vanilla("Data\\INI\\FXList.ini")

    for lbl, src in (("ShockWave(mod) FXList", mod_fx), ("ShockWave(mod) PS", mod_ps),
                     ("vanilla FXList", van_fx), ("vanilla PS", van_ps)):
        if len(src[1]) < 100 * 1024:
            print(f"WARNING: {lbl} source {src[0]} is only {len(src[1])} bytes (<100KB)")

    # ---- build + verify both variants ----
    mod_entries, mod_report = build_variant("ShockWave(mod)", mod_ps, mod_fx)
    van_entries, van_report = build_variant("vanilla", van_ps, van_fx)
    print_report(mod_report)
    print_report(van_report)

    # ---- package ----
    mod_big = build_dir / MOD_BIG_NAME
    van_big = build_dir / VANILLA_BIG_NAME
    write_big_file(mod_entries, str(mod_big))
    write_big_file(van_entries, str(van_big))
    print(f"\nbuilt {mod_big} ({mod_big.stat().st_size} bytes)")
    print(f"built {van_big} ({van_big.stat().st_size} bytes)")

    # ---- install ----
    if args.no_install:
        print("\n--no-install: skipping deployment.")
        return 0
    print("\ninstalling:")
    for d in MOD_DIRS:
        dest = d / MOD_BIG_NAME
        dest.write_bytes(mod_big.read_bytes())
        print(f"  {dest} ({dest.stat().st_size} bytes)")
    van_dest = GAME_DIR / VANILLA_BIG_NAME
    van_dest.write_bytes(van_big.read_bytes())
    print(f"  {van_dest} ({van_dest.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
