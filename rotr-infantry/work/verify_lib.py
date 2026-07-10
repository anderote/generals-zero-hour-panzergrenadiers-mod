"""Static verification for the ROTR infantry archive.  Used by build.py
(and re-run by integrate.py after merge-day regeneration).

Everything is checked against BASE data = vanilla INIZH + the effective
ShockWaveSPE mod space (excluding our own archive), plus the archive's own
content: identifier closure, dropped-token absence, art presence (incl.
W3D-internal textures), audio events, string labels, append-only baking,
block balance, phase-1 invariants, BIG round-trip and sort position.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "hotkey-addon"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))

from bigfile import read_big, write_big  # noqa: E402
from iniblocks import load_tree, parse_blocks  # noqa: E402
import portdefs  # noqa: E402
import portlib  # noqa: E402
import resolve_art  # noqa: E402
import csf  # noqa: E402

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
LABEL = re.compile(r"\b(?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+")

MOD_DIRS = [os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
            os.path.expanduser("~/GeneralsX/mods/ShockWave")]
VANILLA_DIR = os.path.expanduser("~/GeneralsX/GeneralsZH")

errors = []


def err(msg):
    errors.append(msg)
    print("  ERROR:", msg)


def strip_comments(text):
    return "\n".join(portlib.strip_comments_line(l) for l in text.split("\n"))


def base_labels():
    labels = set()
    # effective Generals.str
    fp = os.path.join(HERE, "effective", "Data", "Generals.str")
    if os.path.exists(fp):
        raw = open(fp, "rb").read().decode("latin-1")
        labels |= {m.group(0).lower() for m in LABEL.finditer(raw)}
    # vanilla generals.csf
    for e in read_big(os.path.join(VANILLA_DIR, "EnglishZH.big")):
        if e.path.lower().endswith("generals.csf"):
            for lab in csf.parse(e.data).labels:
                labels.add(lab.name.decode("latin-1").lower())
    return labels


def verify_commandset_patch(archive_text, barracks_sets, slots):
    """Diff-audit the phase-2 CommandSet.ini: every effective block must be
    byte-identical except the barracks sets, which may differ only by our
    inserted slot lines (and must actually contain them)."""
    src = open(os.path.join(HERE, "effective", "Data", "INI",
                            "CommandSet.ini"), "rb").read().decode("latin-1")
    src_blocks = {n: bt for t, n, _a, _b, bt in parse_blocks(src)
                  if t == "CommandSet"}
    arc_blocks = {n: bt for t, n, _a, _b, bt in parse_blocks(archive_text)
                  if t == "CommandSet"}
    our_lines = {"  %-2d = %s ; rotr-infantry" % (slot, btn)
                 for slot, btn in slots}
    for n, bt in src_blocks.items():
        if n not in arc_blocks:
            err("CommandSet %s vanished from the patched CommandSet.ini" % n)
            continue
        if n in barracks_sets:
            arc_lines = arc_blocks[n].split("\n")
            extra = [l for l in arc_lines if l not in bt.split("\n")]
            if set(extra) != our_lines:
                err("barracks set %s: unexpected diff %r" % (n, extra))
            kept = [l for l in arc_lines if l not in our_lines]
            if kept != bt.split("\n"):
                err("barracks set %s: pre-existing lines were altered" % n)
        elif arc_blocks[n] != bt:
            err("CommandSet %s differs from the effective source" % n)
    print("  ok: CommandSet.ini diff-audit (barracks slots only + appends)")


def verify_all(archive_fp, frag_texts, dbyname, phase2=False,
               barracks_sets=None, slots=None):
    global errors
    errors = []
    entries = read_big(archive_fp)
    by_path = {e.path.lower(): e.data for e in entries}

    # ---- BIG round-trip
    if write_big(entries) != open(archive_fp, "rb").read():
        err("BIG round-trip mismatch")
    else:
        print("  ok: BIG round-trip byte-identical (%d entries)" % len(entries))

    # ---- phase invariants
    wiring = ("data\\ini\\commandset.ini", "data\\ini\\commandbutton.ini",
              "data\\generals.str")
    if not phase2:
        for banned in wiring:
            if banned in by_path:
                err("phase-1 violation: %s inside archive" % banned)
        print("  ok: no CommandSet.ini / CommandButton.ini / Generals.str shipped")
    else:
        for needed in wiring:
            if needed not in by_path:
                err("phase-2 violation: %s missing from archive" % needed)
        print("  ok: command wiring present (phase 2)")

    # ---- sort position vs the real mod dir listings
    name = os.path.basename(archive_fp)
    for d in MOD_DIRS:
        listing = [f for f in os.listdir(d) if f.lower().endswith(".big")]
        listing = sorted(set(listing) | {name}, key=str.lower)
        i = listing.index(name)
        # we bake full effective copies of the shared INI files, so we must
        # be the LAST layer except the ControlBarPro camera/UI archives
        stragglers = [f for f in listing[i + 1:]
                      if not f.lower().startswith("zzz_controlbarpro")]
        if stragglers:
            err("%s is not the last INI layer in %s (followed by %s)"
                % (name, d, stragglers))
        if not any("kwaiuav" in f.lower() for f in listing[:i]):
            err("%s does not sort after zzz-ZZZZZZKwaiUAV.big in %s" % (name, d))
        if not [f for f in listing[i + 1:] if f.lower().startswith("zzz_controlbarpro")]:
            err("%s does not sort before zzz_ControlBarPro* in %s" % (name, d))
    print("  ok: archive is the last INI layer (before ControlBarPro only) in both mod dirs")

    # ---- base INI space
    edefs, ebyname = load_tree(os.path.join(HERE, "effective", "Data", "INI"))
    vdefs, vbyname = load_tree(os.path.join(HERE, "vanilla_ini", "Data", "INI"))
    base_byname = dict(vbyname)
    for n, s in ebyname.items():
        base_byname.setdefault(n, set())
        base_byname[n] |= s

    # ---- append-only baking + collect our block space
    ours_byname = {}
    our_texts = {}     # tag -> our INI text (comment-stripped happens later)
    for e in entries:
        pl = e.path.lower()
        if pl == "data\\generals.str":
            src = open(os.path.join(HERE, "effective", "Data", "Generals.str"),
                       "rb").read()
            if not e.data.startswith(src):
                err("Generals.str: not append-only over the effective source")
            continue
        if not pl.endswith(".ini"):
            continue
        text = e.data.decode("latin-1")
        if pl == "data\\ini\\commandset.ini":
            # patched (barracks slots) + appended: diff-audited separately
            tail = text.split("appended by rotr-infantry", 1)[-1].split("\n", 1)[-1]
            our_texts[e.path] = tail
            verify_commandset_patch(text, barracks_sets or [], slots or [])
        elif pl.startswith("data\\ini\\") and pl.count("\\") == 2:
            fname = e.path.split("\\")[-1]
            src = open(os.path.join(HERE, "effective", "Data", "INI", fname), "rb").read()
            if not e.data.startswith(src):
                err("%s: baked file is not append-only over the effective source" % e.path)
            tail = e.data[len(src):].decode("latin-1")
            our_texts[e.path] = tail
        else:
            our_texts[e.path] = text
        for t, n, _a, _b, _bt in parse_blocks(our_texts[e.path]):
            ours_byname.setdefault(n, set()).add(t)
    for fname, text in frag_texts.items():
        if fname.endswith(".str") or fname == "Generals.str":
            continue
        our_texts["FRAGMENT:" + fname] = text
        for t, n, _a, _b, _bt in parse_blocks(text):
            ours_byname.setdefault(n, set()).add(t)
    print("  ok: baked shared files are append-only; %d new top-level blocks"
          % len(ours_byname))

    # ---- new-identifier collision check
    for n in sorted(ours_byname):
        if n in base_byname:
            err("identifier collision with base space: %s (%s)" % (n, ours_byname[n]))
    print("  ok: no identifier collisions with the base space")

    # ---- block balance: our chunks parse cleanly, nothing left over
    for tag, text in our_texts.items():
        blocks = parse_blocks(text)
        covered = set()
        for _t, _n, a, b, _bt in blocks:
            covered.update(range(a, b + 1))
        for i, line in enumerate(text.split("\n")):
            s = portlib.strip_comments_line(line).strip()
            if s and i not in covered:
                err("%s: stray content outside blocks at line %d: %r" % (tag, i + 1, s))
    print("  ok: block balance / no stray content in %d shipped chunks" % len(our_texts))

    # ---- closure: every donor-defined token must resolve; drops must be gone
    all_known = set(base_byname) | set(ours_byname)
    missing, dropped_seen = {}, {}
    for tag, text in our_texts.items():
        for tok in set(WORD.findall(strip_comments(text))):
            if tok in ("NONE", "None", "Nada"):
                continue
            if tok in portdefs.DROPS:
                dropped_seen.setdefault(tok, []).append(tag)
            elif tok in dbyname and tok not in all_known:
                missing.setdefault(tok, []).append(tag)
    for tok, tags in sorted(missing.items()):
        err("unresolved donor identifier %s (in %s)" % (tok, tags[:2]))
    for tok, tags in sorted(dropped_seen.items()):
        err("dropped identifier still referenced: %s (in %s)" % (tok, tags[:2]))
    print("  ok: identifier closure resolves; no dropped identifiers remain")

    # ---- string labels
    known_labels = base_labels()
    frag_str = frag_texts.get("Generals.str", "")
    known_labels |= {m.group(0).lower() for m in LABEL.finditer(frag_str)}
    for tag, text in our_texts.items():
        for lab in set(LABEL.findall(strip_comments(text))):
            if lab.lower() not in known_labels:
                err("unresolved string label %s (in %s)" % (lab, tag))
    print("  ok: all string labels resolve (fragment + base str + vanilla csf)")

    # ---- weapon enum sanity (DamageType/DeathType tokens known to base)
    base_weapon_text = open(os.path.join(HERE, "effective", "Data", "INI",
                                         "Weapon.ini"), "rb").read().decode("latin-1")
    base_enums = set(WORD.findall(base_weapon_text))
    for tag, text in our_texts.items():
        for m in re.finditer(r"^\s*(DamageType|DeathType)\s*=\s*([A-Z0-9_]+)", text, re.M):
            if m.group(2) not in base_enums:
                err("unknown %s token %s (in %s)" % (m.group(1), m.group(2), tag))
    print("  ok: damage/death type tokens all appear in the base Weapon.ini")

    # ---- art presence
    base_art = resolve_art.base_art_index()
    ship_files = {p.rsplit("\\", 1)[-1].lower() for p in by_path}

    def have_w3d(tok):
        f = tok.lower() + ".w3d"
        return f in ship_files or f in base_art

    def have_tex(tok):
        for ext in (".dds", ".tga"):
            f = tok.lower() + ext
            if f in ship_files or f in base_art:
                return True
        return False

    sys.path.insert(0, os.path.join(HERE, ".."))
    import build as build_mod  # for the shared token collectors
    shipped_ini = {p: d.decode("latin-1") for p, d in
                   ((e.path, e.data) for e in entries) if p.lower().endswith(".ini")}
    tokens = build_mod.collect_art_tokens(shipped_ini)
    for tok in tokens["models"]:
        if not have_w3d(tok):
            err("missing W3D for model/animation token %s" % tok)
    for tok in tokens["textures"]:
        if not have_tex(tok):
            err("missing texture %s" % tok)
    # W3D-internal textures of shipped W3Ds
    import tempfile
    for e in entries:
        if not e.path.lower().endswith(".w3d"):
            continue
        with tempfile.NamedTemporaryFile(suffix=".w3d") as tf:
            tf.write(e.data)
            tf.flush()
            for t in resolve_art.w3d_texture_names(tf.name):
                if not have_tex(t.rsplit(".", 1)[0]):
                    err("missing W3D-internal texture %s (of %s)" % (t, e.path))
    # mapped-image pages
    for m in re.finditer(r"^\s*Texture\s*=\s*([A-Za-z0-9_\-\.]+)", "\n".join(
            t for p, t in shipped_ini.items() if "mappedimages" in p.lower()), re.M):
        if not have_tex(m.group(1).rsplit(".", 1)[0]):
            err("missing mapped-image page %s" % m.group(1))
    print("  ok: every model / animation / texture / cameo page resolves")

    # ---- fragment cross-wiring
    cs = frag_texts["CommandSet.ini"]
    buttons_defined = {n for t, n, *_ in parse_blocks(frag_texts["CommandButton.ini"])}
    for m in re.finditer(r"^\s*\d+\s*=\s*([A-Za-z0-9_]+)", cs, re.M):
        b = m.group(1)
        if b not in buttons_defined and b not in base_byname:
            err("command set references unknown button %s" % b)
    for t, n, _a, _b, bt in parse_blocks(frag_texts["CommandButton.ini"]):
        mo = re.search(r"^\s*Object\s*=\s*([A-Za-z0-9_]+)", bt, re.M)
        if mo and mo.group(1) not in ours_byname:
            err("construct button %s: object %s not shipped" % (n, mo.group(1)))
    print("  ok: fragment command sets/buttons cross-wire correctly")

    if errors:
        raise SystemExit("VERIFICATION FAILED: %d errors" % len(errors))
    print("  verification passed with 0 errors")
