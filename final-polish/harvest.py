import re, json
from _eff import effective

cs_txt,_   = effective(r"Data\INI\CommandSet.ini")
cb_txt,_   = effective(r"Data\INI\CommandButton.ini")
up_txt,_   = effective(r"Data\INI\Upgrade.ini")
str_txt,_  = effective(r"Data\Generals.str")

# ---- parse STR (name -> value). Format: LABEL \n "text" \n END
strings = {}
for m in re.finditer(r'(?ms)^\s*([A-Za-z0-9_:]+)\s*\n\s*"(.*?)"\s*\n\s*END\b', str_txt):
    strings[m.group(1).upper()] = m.group(2)

# ---- parse Upgrade blocks
upgrades = {}
for m in re.finditer(r'(?ms)^Upgrade\s+(\S+)\s*\n(.*?)^End\b', up_txt):
    name, body = m.group(1), m.group(2)
    d = {}
    for lm in re.finditer(r'(?m)^\s*(\w+)\s*=\s*(.+?)\s*$', body):
        d[lm.group(1)] = lm.group(2).split(';')[0].strip()
    upgrades[name] = d

# ---- parse CommandButton blocks
buttons = {}
for m in re.finditer(r'(?ms)^CommandButton\s+(\S+)\s*\n(.*?)^End\b', cb_txt):
    name, body = m.group(1), m.group(2)
    d = {}
    for lm in re.finditer(r'(?m)^\s*(\w+)\s*=\s*(.+?)\s*$', body):
        d[lm.group(1)] = lm.group(2).split(';')[0].strip()
    buttons[name] = d

# ---- parse CommandSet blocks
csets = {}
for m in re.finditer(r'(?ms)^CommandSet\s+(\S+)\s*\n(.*?)^End\b', cs_txt):
    name, body = m.group(1), m.group(2)
    slots = {}
    for lm in re.finditer(r'(?m)^\s*(\d+)\s*=\s*(\S+)', body):
        slots[int(lm.group(1))] = lm.group(2)
    csets[name] = slots

def strval(label):
    if not label: return None
    return strings.get(label.upper())

def resolve_upgrade_button(bname):
    b = buttons.get(bname)
    if not b: return None
    cmd = b.get('Command','')
    if cmd not in ('OBJECT_UPGRADE','PLAYER_UPGRADE'): return None
    up = b.get('Upgrade')
    info = {'button': bname, 'command': cmd, 'upgrade': up}
    if up and up in upgrades:
        u = upgrades[up]
        info['cost'] = u.get('BuildCost')
        info['time'] = u.get('BuildTime')
        info['type'] = u.get('Type','PLAYER')
        info['displayname'] = strval(u.get('DisplayName'))
        info['displayname_label'] = u.get('DisplayName')
    info['btn_text'] = strval(b.get('TextLabel'))
    info['btn_tip']  = strval(b.get('DescriptLabel'))
    return info

# Kwai building command sets of interest
building_sets = {k:v for k,v in csets.items()
                 if k.startswith('Tank_China') and 'CommandSet' in k}

out = {}
for setname, slots in sorted(building_sets.items()):
    ups = []
    for slot in sorted(slots):
        info = resolve_upgrade_button(slots[slot])
        if info:
            info['slot'] = slot
            ups.append(info)
    if ups:
        out[setname] = ups

if __name__ == "__main__":
    print(json.dumps(out, indent=1))
