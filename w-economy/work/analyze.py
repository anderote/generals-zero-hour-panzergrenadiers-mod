#!/usr/bin/env python3
import re, sys
from eff import effective, all_paths, arc, archives
import os

# Build the effective INI space: path(lower) -> (text, owner)
space = {}
for lp, (p, a) in all_paths((".ini",)).items():
    data, owner = None, a
    for e in arc(a):
        if e.path.lower() == lp:
            data = e.data.decode("latin-1"); break
    space[lp] = (data.replace("\r\n", "\n"), a, p)

blob_parts = []
for lp,(t,a,p) in space.items():
    blob_parts.append(t)
blob = "\n".join(blob_parts)

# ---- parse all top-level Object blocks
objects = {}   # name -> (block, path, owner)
obj_re = re.compile(r"(?m)^Object[ \t]+(\S+)")
for lp,(t,a,p) in space.items():
    for m in obj_re.finditer(t):
        name = m.group(1)
        m2 = re.search(r"(?m)^End[ \t]*$", t[m.start():])
        block = t[m.start():m.start()+m2.end()] if m2 else ""
        # objects can be redefined? assume unique; last wins if dup
        if name not in objects:
            objects[name] = (block, p, a)

def field(block, name):
    m = re.search(r"(?mi)^\s*%s\s*=\s*([^;\n]+)" % name, block)
    return m.group(1).strip() if m else None

# ---- parse all CommandSets (effective CommandSet.ini) + all CommandButtons
cs_text, cs_owner = effective("Data\\INI\\CommandSet.ini")
cs_text = cs_text.replace("\r\n","\n")
cb_text, cb_owner = effective("Data\\INI\\CommandButton.ini")
cb_text = cb_text.replace("\r\n","\n")
print("CommandSet.ini owner:", cs_owner, "| CommandButton.ini owner:", cb_owner)

sets = {}
for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End", cs_text):
    slots = {}
    for line in m.group(2).splitlines():
        lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
        if lm: slots[int(lm.group(1))] = lm.group(2)
    sets[m.group(1)] = slots

buttons = {}
for m in re.finditer(r"(?ms)^CommandButton[ \t]+(\S+)[ \t]*\n(.*?)^End", cb_text):
    buttons[m.group(1)] = m.group(2)

# ---- China sides
sides = ["China","ChinaTankGeneral","ChinaInfantryGeneral","ChinaNukeGeneral","ChinaSpecialWeaponsGeneral"]

# all China-side objects with INFANTRY kindof and a BuildCost
print("\n===== China-side objects: KindOf INFANTRY with BuildCost =====")
inf = []
for name,(block,p,a) in sorted(objects.items()):
    side = field(block,"Side")
    if side not in sides: continue
    kind = field(block,"KindOf") or ""
    cost = field(block,"BuildCost"); time = field(block,"BuildTime")
    if cost is None: continue
    if "INFANTRY" not in kind.split(): continue
    bv = field(block,"BuildVariations")
    inf.append((side,name,cost,time,bv,p,a))
for row in inf:
    print("%-28s %-42s cost=%-6s time=%-5s bv=%-40s %s [%s]" % row[:5] + (row[5].split("\\")[-1],) + (row[6],)) if False else None
for side,name,cost,time,bv,p,a in inf:
    print("%-28s %-44s cost=%-6s time=%-6s bv=%-42s %s  [%s]" % (side,name,cost,time,bv,p.split("Object\\")[-1],a))

# which are referenced by a UNIT_BUILD command button that sits in some command set?
print("\n===== construct buttons referencing them (and which sets carry the button) =====")
btn_by_obj = {}
for bn, bb in buttons.items():
    if re.search(r"(?m)^\s*Command\s*=\s*UNIT_BUILD", bb):
        o = field(bb,"Object")
        if o: btn_by_obj.setdefault(o, []).append(bn)
for side,name,cost,time,bv,p,a in inf:
    bns = btn_by_obj.get(name, [])
    carrying = []
    for bn in bns:
        for sn, slots in sets.items():
            for sl, cmd in slots.items():
                if cmd == bn: carrying.append("%s:%d" % (sn,sl))
    print("%-44s buttons=%-60s sets=%s" % (name, ",".join(bns) or "-", "; ".join(carrying) or "-"))
