#!/usr/bin/env python3
import re
from eff import effective

cs_text = effective("Data\\INI\\CommandSet.ini")[0].replace("\r\n","\n")
sets = {}
for m in re.finditer(r"(?ms)^CommandSet[ \t]+(\S+)[ \t]*\n(.*?)^End", cs_text):
    slots = {}
    for line in m.group(2).splitlines():
        lm = re.match(r"\s*(\d+)\s*=\s*(\S+)", line)
        if lm: slots[int(lm.group(1))] = lm.group(2)
    sets[m.group(1)] = slots

MAIN = ["AmericaCommandCenterCommandSet","AirF_AmericaCommandCenterCommandSet",
        "Lazr_AmericaCommandCenterCommandSet","SupW_AmericaCommandCenterCommandSet",
        "Armor_AmericaCommandCenterCommandSet",
        "ChinaCommandCenterCommandSet","ChinaCommandCenterCommandSetUpgrade",
        "Tank_ChinaCommandCenterCommandSet","Tank_ChinaCommandCenterCommandSetUpgrade",
        "Infa_ChinaCommandCenterCommandSet","Infa_ChinaCommandCenterCommandSetUpgrade",
        "Nuke_ChinaCommandCenterCommandSet","Nuke_ChinaCommandCenterCommandSetUpgrade",
        "Spec_ChinaCommandCenterCommandSet","Spec_ChinaCommandCenterCommandSetUpgrade",
        "GLACommandCenterCommandSet","Chem_GLACommandCenterCommandSet",
        "Demo_GLACommandCenterCommandSet","Slth_GLACommandCenterCommandSet",
        "Salv_GLACommandCenterCommandSet"]
for n in MAIN:
    if n not in sets:
        print("!! MISSING:", n); continue
    s = sets[n]
    free = [i for i in range(1,15) if i not in s]
    print("== %s   FREE(1-14): %s" % (n, free))
    for sl in sorted(s): print("   %2d = %s" % (sl, s[sl]))
# any USA/GLA CC mines-style upgrade variants I missed?
for n in sorted(sets):
    if "CommandCenter" in n and n not in MAIN and "Taunt" not in n:
        print("OTHER CC SET:", n, sorted(sets[n].items()))
