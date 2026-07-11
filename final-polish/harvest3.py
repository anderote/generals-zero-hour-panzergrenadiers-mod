import re
from harvest import csets, buttons, upgrades, strings, strval, resolve_upgrade_button

# collect every distinct upgrade referenced by any Tank_China* command set
seen = {}
for setname, slots in csets.items():
    if not setname.startswith('Tank_China'): continue
    for slot, btn in slots.items():
        info = resolve_upgrade_button(btn)
        if not info: continue
        up = info['upgrade']
        if up and up not in seen:
            seen[up] = info

# filter out the fake command-swap "upgrades"
FAKE = {'Upgrade_GLAWorkerFakeCommandSet','Upgrade_GLAWorkerRealCommandSet'}
for up in sorted(seen):
    if up in FAKE: continue
    info = seen[up]
    dn = info.get('displayname') or info.get('btn_text') or ''
    tip = (info.get('btn_tip') or '').replace('\\n',' ')
    print("%-42s | $%-5s %-5ss | %-7s | %s"%(dn, info.get('cost','?'), info.get('time','?'), info.get('type','?'), tip[:160]))
