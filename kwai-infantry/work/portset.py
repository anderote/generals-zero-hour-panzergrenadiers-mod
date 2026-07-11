#!/usr/bin/env python3
"""Compute the exact ZHE->our-stack port set for the Sharpshooter.

Precise per-field reference extraction (no word sweeps).  Starting from the
curated roots, walk references; anything defined in OUR effective space is
REUSED (walk stops there); anything only in ZHE joins the PORT set and is
walked further.  Also accumulates audio events, models/anims, mapped images
and string labels.
"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))
from iniblocks import load_tree

zdefs, zby = load_tree(os.path.join(HERE, "zhe"))
edefs, eby = load_tree(os.path.join(HERE, "effective"))

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

# (regex with one capture group possibly containing several whitespace-split
#  names, category)  category: block = INI block ref; audio; image; string;
#  model; psys (particle system block ref); texture
LINE_RULES = [
    (r"^\s*ProjectileObject\s*=\s*(\S+)", "block"),
    (r"^\s*ObjectNames\s*=\s*(.+?)\s*$", "block"),
    (r"^\s*SpawnTemplateName\s*=\s*(\S+)", "block"),
    (r"^\s*BuildVariations\s*=\s*(.+?)\s*$", "block"),
    (r"^\s*Object\s*=\s*([A-Za-z0-9_ \t]+?)\s*$", "block"),      # prerequisites
    (r"^\s*Weapon\s*=\s*(?:PRIMARY|SECONDARY|TERTIARY|INITIAL|MIDPOINT|FINAL)\s+(\S+)", "block"),
    (r"^\s*Weapon\s*=\s*(\S+)\s*$", "block"),                    # FireWeaponUpdate / death Weapon
    (r"^\s*CollideWeapon\s*=\s*(\S+)", "block"),
    (r"^\s*ReactionWeapon\w*\s*=\s*(\S+)", "block"),
    (r"^\s*WeaponTemplate\s*=\s*(\S+)", "block"),
    (r"^\s*DetonationWeapon\s*=\s*(\S+)", "block"),
    (r"^\s*Armor\s*=\s*(\S+)", "block"),
    (r"^\s*DamageFX\s*=\s*(\S+)", "block"),
    (r"^\s*Locomotor\s*=\s*SET_\w+\s+(.+?)\s*$", "block"),
    (r"^\s*FX\s*=\s*(?:INITIAL|MIDPOINT|FINAL)\s+(\S+)", "block"),
    (r"^\s*FX\s*=\s*(\S+)\s*$", "block"),
    (r"^\s*FireFX\s*=\s*(\S+)", "block"),
    (r"^\s*VeterancyFireFX\s*=\s*HEROIC\s+(\S+)", "block"),
    (r"^\s*ProjectileDetonationFX\s*=\s*(\S+)", "block"),
    (r"^\s*ProjectileDetonationOCL\s*=\s*(\S+)", "block"),
    (r"^\s*FireOCL\s*=\s*(\S+)", "block"),
    (r"^\s*OCL\s*=\s*(?:INITIAL|MIDPOINT|FINAL)\s+(\S+)", "block"),
    (r"^\s*OCL\s*=\s*(\S+)\s*$", "block"),
    (r"^\s*UpgradeObject\s*=\s*(\S+)", "block"),
    (r"^\s*SpecialPowerTemplate\s*=\s*(\S+)", "block"),
    (r"^\s*SpecialPower\s*=\s*(\S+)", "block"),
    (r"^\s*CommandSet\s*=\s*(\S+)", "block"),
    (r"^\s*Upgrade\s*=\s*(\S+)", "block"),                       # button upgrade
    (r"^\s*TriggeredBy\s*=\s*(.+?)\s*$", "block"),
    (r"^\s*ConflictsWith\s*=\s*(.+?)\s*$", "block"),
    (r"^\s*RemovesUpgrades\s*=\s*(.+?)\s*$", "block"),
    (r"^\s*Rider\d\s*=\s*(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)", "block2"),
    (r"^\s*Science\s*=\s*(.+?)\s*$", "block"),
    (r"^\s*\d+\s*=\s*(\S+)", "block"),                           # CommandSet slots
    (r"^\s*Name\s*=\s*(\S+)", "block"),                          # FXList nested ParticleSystem/Sound Name
    (r"^\s*AttachedSystem\s*=\s*(\S+)", "block"),
    (r"^\s*SlaveSystem\s*=\s*(\S+)", "block"),
    (r"^\s*PerParticleAttachedSystem\s*=\s*(\S+)", "block"),
    (r"^\s*ParticleSysBone\s*=\s*\S+\s+(\S+)", "block"),
    (r"^\s*ProjectileExhaust\s*=\s*(\S+)", "block"),
    (r"^\s*VeterancyProjectileExhaust\s*=\s*HEROIC\s+(\S+)", "block"),
    (r"^\s*LaserName\s*=\s*(\S+)", "block"),
    (r"^\s*(?:Voice\w+|SoundMoveStart\w*|SoundOnDamaged|SoundOnReallyDamaged|SoundAmbient\w*|SoundStealthOn|SoundStealthOff|SoundCreated|UnitSpecificSound|InitiateSound|FireSound|ProjectileSound|SoundFX)\s*=\s*(\S+)", "audio"),
    (r"^\s*(?:SelectPortrait|ButtonImage|UpgradeCameo\d)\s*=\s*(\S+)", "image"),
    (r"^\s*(?:TextLabel|DescriptLabel|PurchasedLabel|ConflictingLabel|DisplayName)\s*=\s*(\S+)", "string"),
    (r"^\s*Model\s*=\s*(\S+)", "model"),
    (r"^\s*(?:Idle)?Animation\s*=\s*(\S+)", "anim"),
    (r"^\s*ParticleName\s*=\s*(\S+)", "texture"),
]
RULES = [(re.compile(p, re.I), c) for p, c in LINE_RULES]
SKIP = {"NONE", "None", "Yes", "No", "PRIMARY", "SECONDARY", "TERTIARY"}

ROOT_NAMES = [
    "ChinaInfantrySharpshooter",
    "ChinaInfantrySharpshooterVariation1",
    "ChinaInfantrySharpshooterVariation2",
    "ChinaInfantrySharpshooterVariation3",
    "ChinaInfantrySharpshooterVariation4",
    "ChinaInfantrySharpshooter_Wounded",
    "ChinaInfantrySharpshooter_WoundedVariation1",
    "ChinaInfantrySharpshooter_WoundedVariation2",
    "ChinaInfantrySharpshooter_WoundedVariation3",
    "ChinaInfantrySharpshooter_WoundedVariation4",
    "ChinaInfantrySharpshooter_PronedWounded",
    "ChinaInfantrySharpshooter_PronedWoundedVariation1",
    "ChinaInfantrySharpshooter_PronedWoundedVariation2",
    "ChinaInfantrySharpshooter_PronedWoundedVariation3",
    "ChinaInfantrySharpshooter_PronedWoundedVariation4",
    "ChinaInfantrySharpshooterCommandSet",
    "ChinaInfantrySharpshooterPronedCommandSet",
    "ChinaInfantrySharpshooterAPUpgradedCommandSet",
    "ChinaInfantrySharpshooterAPUpgradedPronedCommandSet",
]

port = {}          # (type,name) -> relpath
reuse = {}         # name -> [(type, relpath in eff)]
unresolved = set()
audio, images, strings, models, anims, textures = set(), set(), set(), set(), set(), set()
seen = set()
queue = list(ROOT_NAMES)

def visit_name(name):
    if name in SKIP or not re.match(r"^[A-Za-z0-9_][A-Za-z0-9_\-]*$", name) or name.isdigit():
        return
    if name in seen:
        return
    seen.add(name)
    zhits = zby.get(name)
    ehits = eby.get(name)
    if ehits and name not in ROOT_NAMES:
        reuse[name] = sorted(ehits)
        return
    if not zhits:
        unresolved.add(name)
        return
    for (t, rel) in sorted(zhits):
        port[(t, name)] = rel
        walk_block(t, name)

def walk_block(t, name):
    entry = zdefs.get((t, name))
    if not entry:
        # load_tree keeps first def only per (type,name); fine
        return
    rel, txt = entry
    nc = strip_comments(txt)
    for line in nc.split("\n"):
        for rx, cat in RULES:
            m = rx.match(line)
            if not m:
                continue
            if cat == "block":
                for tok in m.group(1).split():
                    queue.append(tok)
            elif cat == "block2":
                queue.append(m.group(1)); queue.append(m.group(2))
            elif cat == "audio":
                v = m.group(1)
                if v not in ("NoSound",):
                    audio.add(v)
            elif cat == "image":
                images.add(m.group(1))
            elif cat == "string":
                v = m.group(1)
                if ":" in v:
                    strings.add(v)
            elif cat == "model":
                if m.group(1) not in ("None", "NONE"):
                    models.add(m.group(1))
            elif cat == "anim":
                v = m.group(1)
                if "." in v:
                    models.add(v.split(".")[0]); anims.add(v)
            elif cat == "texture":
                textures.add(m.group(1))
            break

while queue:
    visit_name(queue.pop())

print("=== PORT set (%d blocks):" % len(port))
byfile = {}
for (t, n), rel in sorted(port.items(), key=lambda kv: (kv[1], kv[0])):
    byfile.setdefault(rel, []).append((t, n))
for rel in sorted(byfile):
    print(" %s" % rel)
    for t, n in byfile[rel]:
        print("    %-20s %s" % (t, n))
print("\n=== REUSE from effective (%d):" % len(reuse))
for n in sorted(reuse):
    print("  %-50s %s" % (n, ",".join("%s(%s)" % (t, r.split("/")[-1]) for t, r in reuse[n])))
print("\n=== UNRESOLVED names (neither space):", sorted(unresolved))
print("\n=== audio (%d): %s" % (len(audio), " ".join(sorted(audio))))
print("\n=== models (%d): %s" % (len(models), " ".join(sorted(models))))
print("\n=== images (%d): %s" % (len(images), " ".join(sorted(images))))
print("\n=== strings (%d): %s" % (len(strings), " ".join(sorted(strings))))
print("\n=== psys textures (%d): %s" % (len(textures), " ".join(sorted(textures))))
json.dump({"port": [[t, n, rel] for (t, n), rel in sorted(port.items())],
           "reuse": {n: [[t, r] for t, r in v] for n, v in reuse.items()},
           "unresolved": sorted(unresolved),
           "audio": sorted(audio), "models": sorted(models),
           "anims": sorted(anims), "images": sorted(images),
           "strings": sorted(strings), "textures": sorted(textures)},
          open(os.path.join(HERE, "portset.json"), "w"), indent=1)
