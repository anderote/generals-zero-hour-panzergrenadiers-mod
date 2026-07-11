#!/usr/bin/env python3
"""Trace the INI-identifier closure of the two ROTR infantry units against
our effective INI space (vanilla INIZH as bottom layer, ShockWaveSPE mods
effective on top).

Per referenced donor name: PORT (missing everywhere -> ship from donor),
REUSE (already defined in base), DROP (decision table).  Also collects art
asset tokens, audio event references (with base-presence classification)
and string labels.  Writes work/closure_report.txt.
"""
import os
import re
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))
from iniblocks import load_tree  # noqa: E402
import portdefs  # noqa: E402

print("parsing donor tree ...")
ddefs, dbyname = load_tree(portdefs.DONOR_INI)
print("  %d donor blocks" % len(ddefs))
print("parsing effective tree ...")
edefs, ebyname = load_tree(portdefs.EFFECTIVE_INI)
print("  %d effective blocks" % len(edefs))
print("parsing vanilla tree ...")
vdefs, vbyname = load_tree(portdefs.VANILLA_INI)
print("  %d vanilla blocks" % len(vdefs))

# base = vanilla overlaid by mods-effective
base_byname = dict(vbyname)
for n, s in ebyname.items():
    base_byname.setdefault(n, set())
    base_byname[n] |= s

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
LABEL = re.compile(r"\b(?:CONTROLBAR|OBJECT|TOOLTIP|GUI|INI|SCRIPT|UPGRADE|SIDE):[A-Za-z0-9_\-]+")

ART_KEYS = re.compile(
    r"^\s*(Model|Animation|IdleAnimation|ModelNames|AnimationSet|TrackMarks|Texture|Image|"
    r"ButtonImage|SelectPortrait|ShadowTexture|ParticleName|ExtraBounceFXList)\s*=\s*(.*)$", re.I)
AUDIO_KEYS = re.compile(
    r"^\s*(VoiceSelect|VoiceMove|VoiceGuard|VoiceAttack|VoiceAttackAir|VoiceFear|"
    r"VoiceCreate|VoiceEnter|VoiceEnterHostile|VoiceGarrison|VoiceGetHealed|VoiceCrush|"
    r"VoiceFlameLocation|VoicePoisonLocation|VoiceSubdue|TurretMoveStart|TurretMoveLoop|"
    r"SoundMoveStart|SoundMoveStartDamaged|FireSound|EnterSound|ExitSound|"
    r"UnitSpecificSound|BounceSound|Sound|DeathSound|Sounds)\s*=\s*(.*)$", re.I)


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


pending = list(portdefs.SEEDS)
seen = set()
port = []
reuse = []
unresolved = []
art_names = set()
audio_refs = {}    # name -> set of donor blocks referencing it
labels = set()
port_edges = {}    # name -> set of referencing port block names

while pending:
    key = pending.pop()
    if key in seen:
        continue
    seen.add(key)
    t, name = key
    if name in portdefs.DROPS:
        continue
    if key not in ddefs:
        alts = dbyname.get(name)
        if not alts:
            unresolved.append(key)
            continue
        t = sorted(alts)[0][0]
        key = (t, name)
        if key in seen:
            continue
        seen.add(key)
    # audio events are never ported (remap policy) - classify separately
    if key[0] in ("AudioEvent", "DialogEvent"):
        continue
    if name in base_byname and key not in portdefs.SEEDS:
        reuse.append((t, name, sorted(base_byname[name])[0][1]))
        continue
    rel, btext = ddefs[key]
    port.append((t, name, rel))
    labels.update(LABEL.findall(btext))
    for line in btext.split("\n"):
        line_nc = line.split(";")[0]
        m = ART_KEYS.match(line_nc)
        if m:
            for tok in WORD.findall(m.group(2)):
                art_names.add(tok)
        m = AUDIO_KEYS.match(line_nc)
        if m:
            for tok in WORD.findall(m.group(2)):
                audio_refs.setdefault(tok, set()).add(name)
    for tok in refs_of(btext):
        if tok == name or tok in portdefs.DROPS:
            continue
        if tok in dbyname:
            port_edges.setdefault(tok, set()).add(name)
            for (tt, _rel) in dbyname[tok]:
                pending.append((tt, tok))

audio_report = []
for a in sorted(audio_refs):
    if a in ("NONE", "None", "NoSound"):
        continue
    in_base = a in base_byname and any(
        t in ("AudioEvent", "DialogEvent") for t, _ in base_byname[a])
    in_donor = a in dbyname and any(
        t in ("AudioEvent", "DialogEvent") for t, _ in dbyname[a])
    if not (in_base or in_donor):
        continue  # not an audio event token (false positive)
    st = "base" if in_base else "DONOR-ONLY (remap!)"
    audio_report.append((a, st, sorted(audio_refs[a])))

with open(os.path.join(HERE, "closure_report.txt"), "w") as f:
    f.write("=== PORT (missing from base space; ship from donor) ===\n")
    for t, name, rel in sorted(port):
        via = ",".join(sorted(port_edges.get(name, ["seed"]))[:3])
        f.write("  %-20s %-55s %-40s via %s\n" % (t, name, rel, via))
    f.write("\n=== REUSE (already in base/effective space) ===\n")
    for t, name, rel in sorted(set(reuse)):
        f.write("  %-20s %-55s %s\n" % (t, name, rel))
    f.write("\n=== UNRESOLVED tokens queued as defs but defined nowhere ===\n")
    for t, name in sorted(set(unresolved)):
        f.write("  %-20s %s\n" % (t, name))
    f.write("\n=== ART name tokens referenced by ported blocks ===\n")
    for a in sorted(art_names):
        f.write("  %s\n" % a)
    f.write("\n=== AUDIO events referenced by ported blocks ===\n")
    for a, st, via in audio_report:
        f.write("  %-45s %-22s via %s\n" % (a, st, ",".join(via[:3])))
    f.write("\n=== STRING labels referenced by ported blocks ===\n")
    for s in sorted(labels):
        f.write("  %s\n" % s)

print("port=%d reuse=%d unresolved=%d art=%d audio=%d labels=%d" % (
    len(port), len(set(reuse)), len(set(unresolved)), len(art_names),
    len(audio_report), len(labels)))
