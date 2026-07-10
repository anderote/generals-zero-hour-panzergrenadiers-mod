#!/usr/bin/env python3
"""Build zzx_ChinaTankBuff.big for ShockWave (GeneralsX).

Buffs every Chinese tank: +20% MaxHealth, +10% weapon AttackRange,
+5% locomotor Speed.  Pure INI edits, packaged as a late-loading .big.

NOTE: ShockWave removed the TANK KindOf flag from every object in the mod
(zero occurrences archive-wide), so tanks are matched by a curated
file/object whitelist (main battle tanks, flame/gattling/ECM tanks,
Overlord/Emperor-class heavies and their general-specific variants).
"""

import os
import re
import sys
import copy

sys.path.insert(0, "/Users/andrewcote/Documents/software/generalsx-mods/hotkey-addon")
from bigfile import read_big, write_big_file, BigEntry, find_entry

SPE_BIG = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE/zz_SPE_Shw_ini.big")
OUT_NAME = "zzx_ChinaTankBuff.big"
OUT_DIRS = [
    os.path.expanduser("~/GeneralsX/mods/ShockWave"),
    os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE"),
]
HERE = os.path.dirname(os.path.abspath(__file__))

HEALTH_MULT = 1.2
RANGE_MULT = 1.1
SPEED_MULT = 1.05

# internal file path (lower) -> object names to buff in that file
MATCHED = {
    # Vanilla China
    r"data\ini\object\china\vanilla\vehicles\battlemaster.ini": ["ChinaTankBattleMaster_Var1"],
    r"data\ini\object\china\vanilla\vehicles\dragontank.ini": ["ChinaTankDragon"],
    r"data\ini\object\china\vanilla\vehicles\ecmtank.ini": ["ChinaTankECM"],
    r"data\ini\object\china\vanilla\vehicles\gattlingtank.ini": ["ChinaTankGattling"],
    r"data\ini\object\china\vanilla\vehicles\overlord.ini": ["ChinaTankOverlord"],
    # Infantry General (Fai)
    r"data\ini\object\china\infantry\vehicles\battlefortress.ini": ["Infa_ChinaTankOverlord"],
    r"data\ini\object\china\infantry\vehicles\gattlingapc.ini": ["Infa_ChinaTankGattling"],
    r"data\ini\object\china\infantry\vehicles\tigershark.ini": ["Infa_ChinaVehicleNukeLauncher"],
    # Nuke General (Tao)
    r"data\ini\object\china\nuke\vehicles\battlemaster.ini": ["Nuke_ChinaTankBattleMaster"],
    r"data\ini\object\china\nuke\vehicles\devastator.ini": ["Nuke_ChinaTankDevastator"],
    r"data\ini\object\china\nuke\vehicles\gattlingtank.ini": ["Nuke_ChinaTankGattling"],
    r"data\ini\object\china\nuke\vehicles\overlord.ini": ["Nuke_ChinaTankOverlord"],
    r"data\ini\object\china\nuke\vehicles\radtank.ini": ["Nuke_ChinaTankDragon"],
    # Special Weapons General (Leang)
    r"data\ini\object\china\specialweapons\vehicles\dragontank.ini": ["Spec_ChinaTankDragon"],
    r"data\ini\object\china\specialweapons\vehicles\gattlingtank.ini": ["Spec_ChinaTankGattling"],
    r"data\ini\object\china\specialweapons\vehicles\ravagetank.ini": ["Spec_ChinaTankBattleMaster"],
    r"data\ini\object\china\specialweapons\vehicles\seismictank.ini": ["Spec_ChinaVehicleSeismicTank"],
    # Tank General (Kwai)
    r"data\ini\object\china\tank\vehicles\battlemaster.ini": ["Tank_ChinaTankBattleMaster"],
    r"data\ini\object\china\tank\vehicles\dragontank.ini": ["Tank_ChinaTankDragon"],
    r"data\ini\object\china\tank\vehicles\ecmtank.ini": ["Tank_ChinaTankECM"],
    r"data\ini\object\china\tank\vehicles\emperor.ini": ["Tank_ChinaTankEmperor"],
    r"data\ini\object\china\tank\vehicles\gattlingtank.ini": ["Tank_ChinaTankGattling"],
    r"data\ini\object\china\tank\vehicles\reaper.ini": ["Tank_ChinaReaperTank_Real"],
    r"data\ini\object\china\tank\vehicles\warmaster.ini": ["Tank_ChinaTankWarMaster"],
}

DECL_RE = re.compile(
    r"^(Object|ChildObject|ObjectReskin)[ \t]+([\w-]+)(?:[ \t]+([\w-]+))?[ \t]*(?:;.*|//.*)?$"
)
WEAPON_SLOT_RE = re.compile(r"^\s*Weapon\s*=\s*(\w+)\s+([\w-]+)")
LOCO_SET_RE = re.compile(r"^\s*Locomotor\s*=\s*(\w+)\s+([\w \t-]+?)\s*(?:;.*|//.*)?$")
MAXHP_RE = re.compile(r"^(\s*MaxHealth\s*=\s*)([\d.]+)(.*)$")
INITHP_RE = re.compile(r"^(\s*InitialHealth\s*=\s*)([\d.]+)(.*)$")
ATTACKRANGE_RE = re.compile(r"^(\s*AttackRange\s*=\s*)([\d.]+)(.*)$")
SPEED_RE = re.compile(r"^(\s*Speed\s*=\s*)([\d.]+)(.*)$")
# NB: some ShockWave templates are declared with leading whitespace
WEAPON_DEF_RE = re.compile(r"^[ \t]*Weapon[ \t]+([\w-]+)[ \t]*(?:;.*|//.*)?$")
LOCO_DEF_RE = re.compile(r"^[ \t]*Locomotor[ \t]+([\w-]+)[ \t]*(?:;.*|//.*)?$")


def fmt(value: float, orig: str) -> str:
    """Format new value roughly matching original style."""
    if abs(value - round(value)) < 1e-9:
        iv = int(round(value))
        return f"{iv}.0" if "." in orig else str(iv)
    return ("%.4f" % value).rstrip("0").rstrip(".")


def object_extents(lines):
    """Yield (kind, name, parent, start, end) for column-0 declarations."""
    decls = []
    for i, line in enumerate(lines):
        m = DECL_RE.match(line.rstrip("\r\n"))
        if m:
            decls.append((i, m.group(1), m.group(2), m.group(3)))
    out = []
    for idx, (i, kind, name, parent) in enumerate(decls):
        end = decls[idx + 1][0] if idx + 1 < len(decls) else len(lines)
        out.append((kind, name, parent, i, end))
    return out


def main():
    spe = read_big(SPE_BIG)
    by_lower = {e.path.lower(): e for e in spe}

    report = {"health": [], "range": [], "speed": [], "skipped_dummy": set(),
              "weapon_users": {}, "loco_users": {}, "warnings": []}

    modified = {}  # internal path (original spelling) -> new text
    tank_weapons = {}   # weapon name -> set(tank object names using it)
    tank_locos = {}     # loco name -> set((tank, condition))
    matched_objects = set()

    # ---- pass 1: vehicle files: health + collect weapon/loco refs ----
    for path_l, names in MATCHED.items():
        entry = by_lower[path_l]
        text = entry.data.decode("latin-1")
        lines = text.splitlines(keepends=True)
        extents = {n: (s, e) for k, n, p, s, e in object_extents(lines)}
        changed = False
        for name in names:
            if name not in extents:
                report["warnings"].append(f"object {name} not found in {entry.path}")
                continue
            matched_objects.add(name)
            s, e = extents[name]
            # find MaxHealth value first
            max_vals = []
            for i in range(s, e):
                m = MAXHP_RE.match(lines[i].rstrip("\r\n"))
                if m:
                    max_vals.append(float(m.group(2)))
            for i in range(s, e):
                raw = lines[i]
                eol = raw[len(raw.rstrip("\r\n")):]
                body = raw.rstrip("\r\n")
                m = MAXHP_RE.match(body)
                if m:
                    old = float(m.group(2))
                    new = fmt(round(old * HEALTH_MULT), m.group(2))
                    lines[i] = m.group(1) + new + m.group(3) + eol
                    report["health"].append((name, m.group(2), new))
                    changed = True
                    continue
                m = INITHP_RE.match(body)
                if m and max_vals and abs(float(m.group(2)) - max_vals[0]) < 1e-6:
                    new = fmt(round(float(m.group(2)) * HEALTH_MULT), m.group(2))
                    lines[i] = m.group(1) + new + m.group(3) + eol
                    changed = True
                    continue
                mw = WEAPON_SLOT_RE.match(body.split(";")[0])
                if mw:
                    wname = mw.group(2)
                    if wname.lower() == "none":
                        pass
                    elif "dummy" in wname.lower():
                        report["skipped_dummy"].add(wname)
                    else:
                        tank_weapons.setdefault(wname, set()).add(name)
                ml = LOCO_SET_RE.match(body.split(";")[0])
                if ml:
                    for ln in ml.group(2).split():
                        tank_locos.setdefault(ln, set()).add((name, ml.group(1)))
        if changed:
            modified[entry.path] = "".join(lines)

    # ---- pass 2: Weapon.ini AttackRange ----
    wentry = find_entry(spe, r"data\ini\weapon.ini")
    wlines = wentry.data.decode("latin-1").splitlines(keepends=True)
    wdecls = []
    for i, line in enumerate(wlines):
        m = WEAPON_DEF_RE.match(line.rstrip("\r\n"))
        if m:
            wdecls.append((i, m.group(1)))
    wext = {}
    for idx, (i, name) in enumerate(wdecls):
        end = wdecls[idx + 1][0] if idx + 1 < len(wdecls) else len(wlines)
        if name in wext:
            report["warnings"].append(f"duplicate weapon template {name} in Weapon.ini")
        wext[name] = (i, end)
    for wname in sorted(tank_weapons):
        if wname not in wext:
            report["warnings"].append(f"weapon template {wname} NOT FOUND in Weapon.ini")
            continue
        s, e = wext[wname]
        hit = False
        for i in range(s, e):
            raw = wlines[i]
            eol = raw[len(raw.rstrip("\r\n")):]
            m = ATTACKRANGE_RE.match(raw.rstrip("\r\n"))
            if m:
                old = float(m.group(2))
                new = fmt(old * RANGE_MULT, m.group(2))
                wlines[i] = m.group(1) + new + m.group(3) + eol
                report["range"].append((wname, m.group(2), new))
                hit = True
        if not hit:
            report["warnings"].append(f"weapon {wname}: no AttackRange line (inherits/contact weapon?)")
    modified[wentry.path] = "".join(wlines)

    # ---- pass 3: Locomotor.ini Speed ----
    lentry = find_entry(spe, r"data\ini\locomotor.ini")
    llines = lentry.data.decode("latin-1").splitlines(keepends=True)
    ldecls = []
    for i, line in enumerate(llines):
        m = LOCO_DEF_RE.match(line.rstrip("\r\n"))
        if m:
            ldecls.append((i, m.group(1)))
    lext = {}
    for idx, (i, name) in enumerate(ldecls):
        end = ldecls[idx + 1][0] if idx + 1 < len(ldecls) else len(llines)
        lext[name] = (i, end)
    for lname in sorted(tank_locos):
        if lname not in lext:
            report["warnings"].append(f"locomotor template {lname} NOT FOUND in Locomotor.ini")
            continue
        s, e = lext[lname]
        hit = False
        for i in range(s, e):
            raw = llines[i]
            eol = raw[len(raw.rstrip("\r\n")):]
            m = SPEED_RE.match(raw.rstrip("\r\n"))
            if m:
                old = float(m.group(2))
                new = fmt(old * SPEED_MULT, m.group(2))
                llines[i] = m.group(1) + new + m.group(3) + eol
                report["speed"].append((lname, m.group(2), new))
                hit = True
        if not hit:
            report["warnings"].append(f"locomotor {lname}: no Speed line found")
    modified[lentry.path] = "".join(llines)

    # ---- pass 4: shared-usage audit across all object INIs ----
    wnames = {w: re.compile(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])") for w in tank_weapons}
    lnames = {l: re.compile(r"(?<![\w-])" + re.escape(l) + r"(?![\w-])") for l in tank_locos}
    for e in spe:
        p = e.path.lower()
        if not p.endswith(".ini") or not p.startswith(r"data\ini\object"):
            continue
        text = e.data.decode("latin-1")
        lines = text.splitlines()
        for kind, name, parent, s, en in object_extents(lines):
            block = "\n".join(L.split(";")[0] for L in lines[s:en])
            for w, rx in wnames.items():
                if rx.search(block):
                    report["weapon_users"].setdefault(w, set()).add(name)
            for l, rx in lnames.items():
                if rx.search(block):
                    report["loco_users"].setdefault(l, set()).add(name)

    # ---- pass 5: build archive ----
    out_entries = [BigEntry(p, t.encode("latin-1")) for p, t in sorted(modified.items())]
    out_local = os.path.join(HERE, OUT_NAME)
    write_big_file(out_entries, out_local)
    for d in OUT_DIRS:
        dst = os.path.join(d, OUT_NAME)
        with open(out_local, "rb") as fi, open(dst, "wb") as fo:
            fo.write(fi.read())

    # ---- report ----
    print("MATCHED TANK OBJECTS (%d):" % len(matched_objects))
    for n in sorted(matched_objects):
        print("  ", n)
    print("\nHEALTH (MaxHealth x1.2):")
    for n, o, w in report["health"]:
        print(f"  {n:42s} {o:>8s} -> {w}")
    print("\nATTACK RANGE (x1.1):")
    for n, o, w in report["range"]:
        print(f"  {n:52s} {o:>8s} -> {w}")
    print("\nLOCOMOTOR SPEED (x1.05):")
    for n, o, w in report["speed"]:
        print(f"  {n:42s} {o:>8s} -> {w}")
    print("\nSKIPPED DUMMY WEAPONS:", ", ".join(sorted(report["skipped_dummy"])) or "none")
    print("\nWEAPON SPILLOVER (users that are NOT matched tanks):")
    for w in sorted(report["weapon_users"]):
        others = report["weapon_users"][w] - matched_objects
        if others:
            print(f"  {w}: {', '.join(sorted(others))}")
    print("\nLOCOMOTOR SPILLOVER (users that are NOT matched tanks):")
    for l in sorted(report["loco_users"]):
        others = report["loco_users"][l] - matched_objects
        if others:
            print(f"  {l}: {', '.join(sorted(others))}")
    print("\nLOCOMOTOR CONDITIONS SEEN:")
    for l in sorted(tank_locos):
        conds = sorted({c for _, c in tank_locos[l]})
        print(f"  {l}: {', '.join(conds)}")
    print("\nWARNINGS:")
    for w in report["warnings"]:
        print("  !", w)
    if not report["warnings"]:
        print("   none")
    print("\nFILES IN ARCHIVE (%d):" % len(out_entries))
    for e in out_entries:
        print(f"  {len(e.data):>9}  {e.path}")
    print("\nINSTALLED:")
    for d in OUT_DIRS:
        print("  ", os.path.join(d, OUT_NAME))


if __name__ == "__main__":
    main()
