#!/usr/bin/env python3
"""Trace the INI-identifier closure of the three ported units from the Chaos
donor tree against our effective INI space.

Outputs work/closure_report.txt listing, per needed donor block: type, name,
donor file — and whether it exists in the effective space (reuse) or must be
ported.  Also collects art asset names (models, textures, particles handled as
blocks), audio event names, and string labels referenced by ported blocks.
"""
import os
import re
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from iniblocks import load_tree, parse_blocks  # noqa: E402

DONOR = os.path.join(HERE, "..", "..", "donor-inis", "shw_base_ini", "Data", "INI")
EFFECTIVE = os.path.join(HERE, "effective", "Data", "INI")

print("parsing donor tree ...")
ddefs, dbyname = load_tree(DONOR)
print("  %d donor blocks" % len(ddefs))
print("parsing effective tree ...")
edefs, ebyname = load_tree(EFFECTIVE)
print("  %d effective blocks" % len(edefs))

json.dump(sorted("%s\t%s" % k for k in edefs),
          open(os.path.join(HERE, "effective_defs.json"), "w"))

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
LABEL = re.compile(r"\b(?:CONTROLBAR|OBJECT|TOOLTIP|GUI|INI|SCRIPT|UPGRADE|SIDE):[A-Za-z0-9_\-]+")

# lines whose values are ART asset names (w3d model roots / textures)
ART_KEYS = re.compile(
    r"^\s*(Model|Animation|IdleAnimation|ModelNames|TrackMarks|Texture|Image|"
    r"ParticleName|ExtraBounceFXList)\s*=\s*(.*)$", re.I)
AUDIO_KEYS = re.compile(
    r"^\s*(VoiceSelect|VoiceMove|VoiceGuard|VoiceAttack|VoiceAttackAir|VoiceFear|"
    r"VoiceCreate|VoiceEnter|VoiceCrush|TurretMoveStart|TurretMoveLoop|"
    r"SoundMoveStart|SoundMoveStartDamaged|FireSound|EnterSound|ExitSound|"
    r"UnitSpecificSound|BounceSound|Sound|DeathSound|Sounds|Attack|Decay)\s*=\s*(.*)$", re.I)


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        i = line.find(";")
        j = line.find("//")
        if i >= 0 and (j < 0 or i < j):
            line = line[:i]
        elif j >= 0:
            line = line[:j]
        out.append(line)
    return "\n".join(out)


def refs_of(text):
    return set(WORD.findall(strip_comments(text)))


# ---------------------------------------------------------------- seeds
SEEDS = [
    ("Object", "Tank_ChinaTankJS7"),
    ("Object", "Tank_ChinaTankCommandTank"),
    # Shtora machinery grafted onto our Emperor (donor modules):
    ("Weapon", "GolemTankShtoraAIWeapon"),
    ("Weapon", "GolemInvulnerabilityActivationWeapon"),
    ("SpecialPower", "SpecialAbilityRussianShtora"),
    ("ObjectCreationList", "OCL_UniversalAbbilityTrigger"),
    # buttons we plan to ship:
    ("CommandButton", "Tank_Command_ConstructChinaTankJS7"),
    ("CommandButton", "Tank_Command_ConstructChinaTankCommandTank"),
    ("CommandButton", "Command_RussiaGolemTankActivatedShtora"),
    ("CommandButton", "Command_CommandTankAPFSDSShells"),
    ("CommandButton", "Command_CommandTankHESHShells"),
    ("CommandButton", "Command_ChinaCommandTankGrantVeterancy"),
    ("CommandButton", "Command_ChinaCommandTruckSwitchToPowers"),
    ("CommandButton", "Command_ChinaCommandTruckSwitchToNormal"),
    ("CommandSet", "RussianTankGolemCommandSet"),
]

# donor names we deliberately do NOT port (documented drops); their subtrees
# are pruned from the closure.
DROPS = {
    # Command Tank powers whose SpecialPower templates don't exist here and
    # whose closures are out of scope:
    "SuperweaponSpawnLeechInfector", "SUPERWEAPON_LeechInfectorDrone",
    "SuperweaponSummonSweetTooth", "SUPERWEAPON_SweetTooth",
    "SuperweaponV4Paradrop", "SUPERWEAPON_V4Paradrop1", "SUPERWEAPON_V4Paradrop2",
    "SuperweaponChinaGlobalJammer", "SUPERWEAPON_ChinaRadarJammer",
    "SuperweaponTeslaTankDrop", "SUPERWEAPON_ChinaCommandTankTeslaTankParadrop",
    "Command_ChinaCommandTankTeslaTankParadrop",
    # invisible is-a-structure drone trick (victory-condition side effects):
    "OCL_AmericaCommandTankIsStructure",
    # infection/carbomb chain kept only if closure demands (see report)
}

pending = list(SEEDS)
seen = set()
port = []          # (type, name, donorfile) blocks that must ship
reuse = []         # (type, name) resolved by effective space
unresolved = []    # donor-referenced names defined nowhere (usually harmless tokens)

art_names = set()
audio_names = set()
labels = set()

while pending:
    key = pending.pop()
    if key in seen:
        continue
    seen.add(key)
    t, name = key
    if name in DROPS:
        continue
    if key not in ddefs:
        # maybe defined under another type name in donor
        alts = dbyname.get(name)
        if not alts:
            unresolved.append(key)
            continue
        t = sorted(alts)[0][0]
        key = (t, name)
        if key in seen:
            continue
        seen.add(key)
    # if the effective space already defines this name (any type), reuse it
    if name in ebyname and key not in SEEDS:
        reuse.append((t, name, sorted(ebyname[name])[0][1]))
        continue
    rel, btext = ddefs[(t, name)]
    port.append((t, name, rel))
    # collect labels / art / audio from this block
    labels.update(LABEL.findall(btext))
    for line in btext.split("\n"):
        line_nc = line.split(";")[0]
        m = ART_KEYS.match(line_nc)
        if m:
            for tok in WORD.findall(m.group(2)):
                art_names.add(tok)
        m = AUDIO_KEYS.match(line_nc)
        if m and t in ("Object", "CommandButton", "AudioEvent", "Weapon", "FXList"):
            for tok in WORD.findall(m.group(2)):
                audio_names.add(tok)
    # recurse over identifier references
    for tok in refs_of(btext):
        if tok == name:
            continue
        if tok in DROPS:
            continue
        if tok in dbyname:
            for (tt, _rel) in dbyname[tok]:
                pending.append((tt, tok))

# classify audio references: defined AudioEvents get handled via closure;
# remaining are raw tokens
audio_report = []
for a in sorted(audio_names):
    in_eff = a in ebyname
    in_donor = a in dbyname
    audio_report.append((a, "effective" if in_eff else ("donor-only" if in_donor else "raw/none")))

with open(os.path.join(HERE, "closure_report.txt"), "w") as f:
    f.write("=== PORT (missing from effective space; ship from donor) ===\n")
    for t, name, rel in sorted(port):
        f.write("  %-20s %-55s %s\n" % (t, name, rel))
    f.write("\n=== REUSE (already in effective space) ===\n")
    for t, name, rel in sorted(set(reuse)):
        f.write("  %-20s %-55s %s\n" % (t, name, rel))
    f.write("\n=== UNRESOLVED tokens queued as defs but defined nowhere ===\n")
    for t, name in sorted(set(unresolved)):
        f.write("  %-20s %s\n" % (t, name))
    f.write("\n=== ART name tokens referenced by ported blocks ===\n")
    for a in sorted(art_names):
        f.write("  %s\n" % a)
    f.write("\n=== AUDIO tokens referenced by ported blocks ===\n")
    for a, st in audio_report:
        f.write("  %-45s %s\n" % (a, st))
    f.write("\n=== STRING labels referenced by ported blocks ===\n")
    for s in sorted(labels):
        f.write("  %s\n" % s)

print("port=%d reuse=%d unresolved=%d art=%d audio=%d labels=%d" % (
    len(port), len(set(reuse)), len(set(unresolved)), len(art_names),
    len(audio_names), len(labels)))
print("report: closure_report.txt")
