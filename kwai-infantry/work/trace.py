#!/usr/bin/env python3
"""Trace the ZHE ChinaInfantrySharpshooter closure against OUR effective space.

For every identifier reachable from the sharpshooter roots in the ZHE INI
tree, report whether it's defined in our effective space (reuse) or only in
ZHE (must port).
"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))
from iniblocks import parse_blocks, load_tree

ZHE = os.path.join(HERE, "zhe")
EFF = os.path.join(HERE, "effective")

print("loading ZHE tree ...")
zhe_defs, zhe_byname = load_tree(ZHE)
print(len(zhe_defs), "ZHE blocks")
print("loading effective tree ...")
eff_defs, eff_byname = load_tree(EFF)
print(len(eff_defs), "effective blocks")

def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i, j = line.find(";"), line.find("//")
        if i >= 0 and (j < 0 or i < j):
            line = line[:i]
        elif j >= 0:
            line = line[:j]
        out.append(line)
    return "\n".join(out)

# reference-extraction: keyed fields -> target block type
REF_KEYS = {
    "Weapon": [
        (r"^\s*Weapon\s*=\s*\w+\s+(\S+)", None),
        (r"^\s*CollideWeapon\s*=\s*(\S+)", None),
        (r"^\s*ReactionWeapon\w*\s*=\s*(\S+)", None),
        (r"^\s*WeaponTemplate\s*=\s*(\S+)", None),
        (r"^\s*WeaponName\s*=\s*(\S+)", None),
    ],
    "Armor": [(r"^\s*Armor\s*=\s*(\S+)", None)],
    "Locomotor": [(r"^\s*Locomotor\s*=\s*\w+\s+(.+)$", "multi")],
    "FXList": [(r"^\s*FX\s*=\s*\w+\s+(\S+)", None),
               (r"^\s*FireFX\s*=\s*(\S+)", None),
               (r"^\s*VeterancyFireFX\s*=\s*HEROIC\s+(\S+)", None),
               (r"^\s*ProjectileDetonationFX\s*=\s*(\S+)", None),
               (r"^\s*FireOCL\s*=\s*(\S+)", None),  # actually OCL, handled below
               (r"^\s*DamageFX\s*=\s*(\S+)", None)],
    "ObjectCreationList": [(r"^\s*OCL\s*=\s*(?:INITIAL|FINAL|MIDPOINT)?\s*(\S+)", None),
                           (r"^\s*OCL\s*=\s*(\S+)", None),
                           (r"^\s*ProjectileDetonationOCL\s*=\s*(\S+)", None),
                           (r"^\s*DeliverPayload.*", None)],
    "Object": [(r"^\s*SpawnTemplateName\s*=\s*(\S+)", None),
               (r"^\s*ProjectileObject\s*=\s*(\S+)", None),
               (r"^\s*BuildVariations\s*=\s*(.+)$", "multi"),
               (r"^\s*Object\s*=\s*(.+)$", "multi"),   # prerequisites
               (r"^\s*CreateObject\s*=\s*(.+)$", "multi"),
               (r"^\s*Rider\d\s*=\s*(\S+)", None)],
    "Upgrade": [(r"^\s*TriggeredBy\s*=\s*(.+)$", "multi"),
                (r"^\s*ConflictsWith\s*=\s*(.+)$", "multi"),
                (r"^\s*UpgradeToGrant\s*=\s*(\S+)", None),
                (r"^\s*UpgradeCameo\d\s*=\s*(\S+)", None),
                (r"^\s*RemovesUpgrades\s*=\s*(.+)$", "multi")],
    "SpecialPower": [(r"^\s*SpecialPowerTemplate\s*=\s*(\S+)", None),
                     (r"^\s*SpecialPower\s*=\s*(\S+)", None)],
    "CommandSet": [(r"^\s*CommandSet\s*=\s*(\S+)", None),
                   (r"^\s*Rider\d\s*=\s*\S+\s+\S+\s+\S+\s+\S+\s+(\S+)", None)],
    "CommandButton": [(r"^\s*\d+\s*=\s*(\S+)", None)],
    "Science": [(r"^\s*Science\s*=\s*(.+)$", "multi"),
                (r"^\s*NeededScience\s*=\s*(\S+)", None)],
}
AUDIO_RE = re.compile(
    r"^\s*(Voice\w+|Sound\w*|UnitSpecificSound|InitiateSound|FireSound|"
    r"WeaponBonus.*|AudioLoop\w*)\s*=\s*(\S+)\s*$", re.I)

MODEL_RE = re.compile(r"^\s*(?:Model|WeaponLaunchBone)\s*=\s*(\S+)", re.I)
ANIM_RE = re.compile(r"^\s*(?:Idle)?Animation\s*=\s*([\w\-]+)\.([\w\-]+)", re.I)

# roots
ROOTS = [
    ("Object", "ChinaInfantrySharpshooter"),
    ("Object", "ChinaInfantrySharpshooterVariation1"),
    ("ObjectReskin", "ChinaInfantrySharpshooterVariation2"),
    ("ObjectReskin", "ChinaInfantrySharpshooterVariation3"),
    ("ObjectReskin", "ChinaInfantrySharpshooterVariation4"),
    ("Object", "ChinaInfantrySharpshooter_Wounded"),
    ("Object", "ChinaInfantrySharpshooter_WoundedVariation1"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_WoundedVariation2"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_WoundedVariation3"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_WoundedVariation4"),
    ("Object", "ChinaInfantrySharpshooter_PronedWounded"),
    ("Object", "ChinaInfantrySharpshooter_PronedWoundedVariation1"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_PronedWoundedVariation2"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_PronedWoundedVariation3"),
    ("ObjectReskin", "ChinaInfantrySharpshooter_PronedWoundedVariation4"),
    ("CommandSet", "ChinaInfantrySharpshooterCommandSet"),
    ("CommandSet", "ChinaInfantrySharpshooterPronedCommandSet"),
    ("CommandSet", "ChinaInfantrySharpshooterAPUpgradedCommandSet"),
    ("CommandSet", "ChinaInfantrySharpshooterAPUpgradedPronedCommandSet"),
]

def find_def(name):
    """Return list of (type, relpath) for name in ZHE."""
    return sorted(zhe_byname.get(name, ()))

def block_text(typ, name):
    v = zhe_defs.get((typ, name))
    return v[1] if v else None

TYPE_ORDER = ["Object", "ObjectReskin", "Weapon", "Armor", "Locomotor",
              "FXList", "ParticleSystem", "ObjectCreationList", "Upgrade",
              "SpecialPower", "CommandSet", "CommandButton", "Science",
              "AudioEvent", "CrateData", "WeaponBonusSet", "DamageFX",
              "MappedImage", "FXParticleSystem"]

visited = set()
queue = list(ROOTS)
refs_audio, refs_models, refs_anims, refs_strings, refs_images = set(), set(), set(), set(), set()
missing = []

def enqueue(name, hinttypes=None):
    if not name or name in ("NONE", "None", "No", "Yes"):
        return
    cands = find_def(name)
    if not cands:
        return  # not a ZHE block; may be image/string/bone/etc.
    for t, _rel in cands:
        if (t, name) not in visited:
            queue.append((t, name))

while queue:
    t, name = queue.pop()
    if (t, name) in visited:
        continue
    visited.add((t, name))
    txt = block_text(t, name)
    if txt is None:
        missing.append((t, name))
        continue
    nc = strip_comments(txt)
    for line in nc.split("\n"):
        # audio
        m = AUDIO_RE.match(line)
        if m and m.group(2) not in ("NoSound",):
            refs_audio.add(m.group(2))
        m = MODEL_RE.match(line)
        if m:
            refs_models.add(m.group(1))
        m = ANIM_RE.match(line)
        if m:
            refs_anims.add((m.group(1), m.group(2)))
        for lab in re.findall(r"\b(?:CONTROLBAR|OBJECT|TOOLTIP|GUI|SCIENCE|UPGRADE):[A-Za-z0-9_\-]+", line):
            refs_strings.add(lab)
        for key in ("SelectPortrait", "ButtonImage", "UpgradeCameo1",
                    "UpgradeCameo2", "UpgradeCameo3", "UpgradeCameo4",
                    "UpgradeCameo5", "RadiusCursorType"):
            m2 = re.match(r"^\s*%s\s*=\s*(\S+)" % key, line)
            if m2:
                refs_images.add(m2.group(1))
        # block refs
        for _typ, pats in REF_KEYS.items():
            for pat, mode in pats:
                m2 = re.match(pat, line)
                if not m2 or not m2.groups():
                    continue
                val = m2.group(1)
                if mode == "multi":
                    for tok in val.split():
                        enqueue(tok.strip())
                else:
                    enqueue(val.strip())
        # particle systems in FXLists / weapons
        for m2 in re.finditer(r"^\s*(?:ParticleSystem|AttachedSystem|SlavedSystem)\s*(?:Name)?\s*=?\s*(\S+)?", line):
            pass
    # FXList / OCL / ParticleSystem blocks: sweep every word for known defs
    if t in ("FXList", "ObjectCreationList", "ParticleSystem", "Weapon",
             "Upgrade", "SpecialPower", "CommandButton", "ObjectCreationList"):
        for tok in set(re.findall(r"[A-Za-z_][A-Za-z0-9_\-]*", nc)):
            if tok in zhe_byname:
                enqueue(tok)

report = {}
for (t, name) in sorted(visited):
    ineff = sorted(eff_byname.get(name, ()))
    zrel = find_def(name)
    report.setdefault(t, []).append({
        "name": name,
        "zhe": [r for _t, r in zrel],
        "eff": ["%s:%s" % (tt, r) for tt, r in ineff],
    })

out = {"blocks": report,
       "audio": sorted(refs_audio),
       "models": sorted(refs_models),
       "anims": sorted("%s.%s" % a for a in refs_anims),
       "strings": sorted(refs_strings),
       "images": sorted(refs_images)}
json.dump(out, open(os.path.join(HERE, "closure_raw.json"), "w"), indent=1)

for t in TYPE_ORDER:
    for e in report.get(t, []):
        tag = "REUSE(eff)" if e["eff"] else "PORT"
        print("%-22s %-55s %s" % (t, e["name"], tag))
print("audio:", len(refs_audio), "models:", len(refs_models),
      "anims:", len(refs_anims), "strings:", len(refs_strings),
      "images:", len(refs_images))
