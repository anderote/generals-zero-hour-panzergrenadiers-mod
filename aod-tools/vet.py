#!/usr/bin/env python3
"""Phase 2: vet harvested maps' template references against the EFFECTIVE
ShockWaveSPE+layers INI space (mod dir overrides base GeneralsZH dir per file
path; within each dir, later-alphabetical archive wins)."""
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon")
import mapscript
from bigfile import read_big

SPE = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
ZH  = os.path.expanduser("~/GeneralsX/GeneralsZH")

def effective_roster():
    objs, seen = set(), set()
    for d in (SPE, ZH):                       # mod dir first: wins per path
        arcs = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")),
                      key=str.lower, reverse=True)
        for a in arcs:
            try:
                ents = read_big(os.path.join(d, a))
            except Exception:
                continue
            for e in ents:
                lp = e.path.lower().replace("/", "\\")
                if not lp.endswith(".ini") or lp in seen:
                    continue
                seen.add(lp)
                for m in re.finditer(rb"(?mi)^\s*Object\s+([A-Za-z0-9_]+)", e.data):
                    objs.add(m.group(1).decode("latin-1"))
    return objs

def main():
    roster = effective_roster()
    print("effective roster: %d object templates (SPE mod dir > base GeneralsZH, per-path)" % len(roster))
    results = {}
    for f in sorted(os.listdir(os.path.join(HERE, "harvest"))):
        if not f.endswith(".map") or f == "aod_pasha.map":
            continue
        info = mapscript.analyze(os.path.join(HERE, "harvest", f))
        refs = mapscript.referenced_templates(info)
        missing = {t: sorted(w) for t, w in sorted(refs.items()) if t not in roster}
        # placed scenery misses are cosmetic; team/script misses hit the wave engine
        hard = {t: w for t, w in missing.items() if set(w) & {"team", "script"}}
        soft = {t: w for t, w in missing.items() if t not in hard}
        results[f] = dict(total=len(refs), missing=len(missing), hard=len(hard))
        print("\n== %s: %d refs, %d missing (%d wave-critical)" %
              (f, len(refs), len(missing), len(hard)))
        for t, w in sorted(hard.items()):
            print("   HARD %-42s %s" % (t, ",".join(w)))
        for t, w in sorted(soft.items())[:12]:
            print("   soft %-42s %s" % (t, ",".join(w)))
        if len(soft) > 12:
            print("   ... +%d more soft (placed scenery/buildlist)" % (len(soft) - 12))
    json.dump(results, open(os.path.join(HERE, "vet_results.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
