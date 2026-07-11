#!/usr/bin/env python3
import re
from eff import effective, all_paths, arc

space = {}
for lp, (p, a) in all_paths((".ini",)).items():
    for e in arc(a):
        if e.path.lower() == lp:
            space[lp] = (e.data.decode("latin-1").replace("\r\n","\n"), a, p); break

def field(block, name):
    m = re.search(r"(?mi)^\s*%s\s*=\s*([^;\n]+)" % name, block)
    return m.group(1).strip() if m else None

cs_text = effective("Data\\INI\\CommandSet.ini")[0].replace("\r\n","\n")
sets = {}
for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End", cs_text):
    slots = {}
    for line in m.group(2).splitlines():
        lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
        if lm: slots[int(lm.group(1))] = lm.group(2)
    sets[m.group(1)] = slots

# find all objects whose KindOf includes COMMANDCENTER
print("===== COMMANDCENTER objects =====")
ccs = []
for lp,(t,a,p) in sorted(space.items()):
    for m in re.finditer(r"(?m)^Object[ \t]+(\S+)", t):
        name = m.group(1)
        m2 = re.search(r"(?mi)^End[ \t]*(;[^\n]*)?$", t[m.start():])
        if m2 is None: continue
        block = t[m.start():m.start()+m2.end()]
        kind = ""
        for km in re.finditer(r"(?mi)^\s*KindOf\s*=\s*([^;\n]+)", block):
            kind += " " + km.group(1)
        if "COMMANDCENTER" in kind.split():
            side = field(block,"Side"); cset = field(block,"CommandSet")
            csu = re.findall(r"(?mi)^\s*CommandSet(?:Alt)?\s*=\s*(\S+)", block)
            ccs.append((side,name,cset,p,a,block))
for side,name,cset,p,a,block in ccs:
    print("%-30s %-38s set=%-42s %s [%s]" % (side,name,cset,p.split('INI\\')[-1],a))
    # any CommandSetUpgrade modules?
    for m in re.finditer(r"(?ms)^  Behavior\s*=\s*CommandSetUpgrade.*?^  End", block):
        print("      CSU:", " | ".join(re.findall(r"(?m)^\s*(CommandSet(?:Alt)?|TriggeredBy)\s*=\s*([^\n;]+)", m.group(0))[0]) if False else re.sub(r"\s+"," ",m.group(0))[:200])

print("\n===== CC command set occupancies =====")
seen=set()
for side,name,cset,p,a,block in ccs:
    for sn in set([cset] + re.findall(r"(?mi)^\s*CommandSet(?:Alt)?\s*=\s*(\S+)", block)):
        if sn and sn in sets and sn not in seen:
            seen.add(sn)
            print("%-46s (obj %s)" % (sn, name))
            for sl in sorted(sets[sn]): print("   %2d = %s" % (sl, sets[sn][sl]))

print("\n===== Kwai production buildings: ProductionUpdate =====")
for path, objname in (("Data\\INI\\Object\\China\\Tank\\Buildings\\Barracks.ini","Tank_ChinaBarracks"),
                      ("Data\\INI\\Object\\China\\Tank\\Buildings\\WarFactory.ini","Tank_ChinaWarFactory"),
                      ("Data\\INI\\Object\\China\\Tank\\Buildings\\Airfield.ini","Tank_ChinaAirfield")):
    t, a = effective(path)
    t = t.replace("\r\n","\n")
    print("--", path, "[owner %s]" % a)
    for m in re.finditer(r"(?ms)^  Behavior\s*=\s*ProductionUpdate.*?^  End", t):
        print(re.sub(r"\n"," | ", m.group(0))[:400])
