#!/usr/bin/env python3
"""dump.py [--eff] NAME [NAME...] — print ZHE (or effective) blocks by name."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))
from iniblocks import load_tree

args = sys.argv[1:]
root = "zhe"
if args and args[0] == "--eff":
    root = "effective"
    args = args[1:]
defs, byname = load_tree(os.path.join(HERE, root))
for name in args:
    hits = byname.get(name)
    if not hits:
        print("=== %s: NOT DEFINED in %s" % (name, root))
        continue
    for t, rel in sorted(hits):
        print("=== %s %s  [%s :: %s]" % (t, name, root, rel))
        print(defs[(t, name)][1] if defs.get((t, name)) and defs[(t, name)][0] == rel
              else [v for k, v in defs.items() if k == (t, name)][0][1])
