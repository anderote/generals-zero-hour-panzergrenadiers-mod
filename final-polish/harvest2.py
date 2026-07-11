import re, json
from _eff import effective
import harvest  # reuse parsing
from harvest import csets, buttons, upgrades, strings, strval, resolve_upgrade_button, building_sets

# Map a command-set name to a canonical building label
def building_of(setname):
    s = setname[len('Tank_China'):]
    for suff in ['CommandSetUpgrade','CommandSetOneUpgrade','CommandSetTwoUpgrade',
                 'CommandSetOne','CommandSetTwo','CommandSet_Down','CommandSet']:
        if s.endswith(suff):
            s = s[:-len(suff)]; break
    s = re.sub(r'CS_M\dV\dI\d$','',s)  # propaganda doctrine states
    return s or setname

by_building = {}
for setname, slots in sorted(csets.items()):
    if not setname.startswith('Tank_China'): continue
    b = building_of(setname)
    for slot in sorted(slots):
        info = resolve_upgrade_button(slots[slot])
        if not info: continue
        key = info['upgrade'] or info['button']
        by_building.setdefault(b, {})
        if key not in by_building[b]:
            by_building[b][key] = info

# print compact
for b in sorted(by_building):
    print("\n### BUILDING:", b, "  (%d distinct upgrades)"%len(by_building[b]))
    for key, info in sorted(by_building[b].items(), key=lambda kv: (kv[1].get('cost') or '0', kv[0])):
        dn = info.get('displayname') or info.get('btn_text') or info['button']
        print("  - %-40s $%-5s %ss  [%s]  upg=%s"%(
            dn, info.get('cost','?'), info.get('time','?'), info.get('type','?'), info['upgrade']))
