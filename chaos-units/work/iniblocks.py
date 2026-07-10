"""Top-level INI block parser for ZH INI files.

A top-level block starts at column 0 with "<Type> <Name>" (or "<Type> <Name> <junk>")
and ends at the matching column-0 "End" line.  Nested blocks/Ends are indented in
all ShockWave/Chaos files, so column-0 End terminates the block.
"""
import os
import re

BLOCK_TYPES = (
    "Object", "Weapon", "Armor", "Locomotor", "FXList", "ParticleSystem",
    "ObjectCreationList", "SpecialPower", "Upgrade", "Science", "CommandSet",
    "CommandButton", "AudioEvent", "DialogEvent", "MusicTrack", "MappedImage",
    "CrateData", "ObjectReskin", "WeaponBonusSet", "DamageFX", "FXParticleSystem",
)

_START = re.compile(r"^(%s)[ \t]+([A-Za-z0-9_\-]+)" % "|".join(BLOCK_TYPES))


def parse_blocks(text):
    """Yield (type, name, start_line_idx, end_line_idx_inclusive, text) over LF text."""
    lines = text.split("\n")
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        m = _START.match(lines[i])
        if m:
            t, name = m.group(1), m.group(2)
            j = i + 1
            while j < n:
                ls = lines[j]
                if ls == "End" or ls == "END" or ls.rstrip() == "End" and not ls.startswith((" ", "\t")):
                    break
                j += 1
            blocks.append((t, name, i, j, "\n".join(lines[i:j + 1]) + "\n"))
            i = j + 1
        else:
            i += 1
    return blocks


def load_tree(root):
    """Parse every .ini/.INI under root.  Returns:
    defs: dict (type,name) -> (relpath, blocktext)
    byname: dict name -> set of (type, relpath)
    """
    defs = {}
    byname = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith(".ini"):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, root)
            with open(fp, "rb") as f:
                raw = f.read()
            text = raw.decode("latin-1").replace("\r\n", "\n")
            for t, name, _a, _b, btext in parse_blocks(text):
                defs.setdefault((t, name), (rel, btext))
                byname.setdefault(name, set()).add((t, rel))
    return defs, byname


if __name__ == "__main__":
    import sys
    root, typ, name = sys.argv[1], sys.argv[2], sys.argv[3]
    defs, _ = load_tree(root)
    key = (typ, name)
    if key in defs:
        rel, btext = defs[key]
        sys.stdout.write("; from %s\n%s" % (rel, btext))
    else:
        print("NOT FOUND", key)
        sys.exit(1)
