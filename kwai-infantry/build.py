#!/usr/bin/env python3
"""Build zzz-ZZZZZZZLKwaiInfantry.big — THREE new Barracks infantry for Kwai
(China Tank General), ShockWave under GeneralsX.  **v2 — ZHE port removed.**

  Barracks slot 6  FLAME TROOPER   Tank_ChinaInfantryFlameThrower
     build stub -> Spec_ChinaInfantryFlameThrower (Leang, $350 / 8 s,
     donor prereqs Spec_ChinaBarracks + Spec_ChinaWarFactory translated to
     Tank_ChinaBarracks + Tank_ChinaWarFactory).
  Barracks slot 7  MINIGUNNER      Tank_ChinaInfantryMiniGunner
     build stub -> Infa_ChinaInfantryMiniGunner (Fai, $550 / 14 s, donor
     prereq Infa_ChinaBarracks translated to Tank_ChinaBarracks).
  Barracks slot 8  SHARPSHOOTER    Tank_ChinaInfantrySharpshooter
     SIMPLE SNIPER: full CLONE of the effective vanilla-USA Pathfinder
     (AmericaInfantryPathfinder, zz_SPE_Shw_ini.big) — stock stealth-sniper
     mechanics only — re-sided to Kwai, RedGuard voice set, Pathfinder cameo,
     $1200 / 30 s, prereq Tank_ChinaBarracks + Tank_ChinaPropagandaCenter.
     (v1 ported Zero Hour Enhanced's ChinaInfantrySharpshooter with its full
     closure — 176 INI blocks, 47 W3D, 33 textures, 101 wavs, 28 audio
     events, 18 strings.  REMOVED after two mid-skirmish crashes with the
     port as prime suspect; zero ZHE machinery remains in this layer.)

Stubs follow the kwai-artillery/kwai-roster BuildVariations idiom; the
sniper follows kwai-roster's Scout Car full-clone idiom (exact line-diff
audited).  Effective-file rule: this layer sorts case-insensitively AFTER
zzz-ZZZZZZZKwaiPDL.big ('k' < 'l' at char 11) and BEFORE
zzz-ZZZZZZZTTeslaCoil.big / zzz-ZZZZZZZVehicleKit.big /
zzz-ZZZZZZZWEconomy.big (which embed files derived from ours and are
REBUILT AFTER us — rebuild chain in README).  Sources are read ONLY from
archives sorting strictly below this one.
"""
import difflib
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
sys.path.insert(0, os.path.join(HERE, "..", "chaos-units", "work"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402
from iniblocks import parse_blocks  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")
OUT_NAME = "zzz-ZZZZZZZLKwaiInfantry.big"
TAG = "zzz-ZZZZZZZLKwaiInfantry"

CS = "Data\\INI\\CommandSet.ini"
CB = "Data\\INI\\CommandButton.ini"
STR = "Data\\Generals.str"
IP = "Data\\INI\\Object\\China\\Tank\\Infantry\\"
PATH_DONOR = "Data\\INI\\Object\\USA\\Vanilla\\Infantry\\Pathfinder.ini"

EXPECT_OWNERS = {
    CS: "zzz-ZZZZZZZKwaiPDL.big", CB: "zzz-ZZZZZZZKwaiPDL.big",
    STR: "zzz-ZZZZZZZKwaiPDL.big",
    # donor files (read-only, drift guards)
    "Data\\INI\\Object\\China\\SpecialWeapons\\Infantry\\FlameThrower.ini":
        "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Infantry\\Infantry\\MiniGunner.ini":
        "zz_SPE_Shw_ini.big",
    PATH_DONOR: "zz_SPE_Shw_ini.big",
    "Data\\INI\\Object\\China\\Vanilla\\Infantry\\Redguard.ini":
        "zzz-KwaiDoctrine.big",
    IP + "SiegeSoldier.ini": "zzz-ZZZZZKwaiRoster.big",
}
NEW_INI_PATHS = [IP + "FlameTrooper.ini", IP + "MiniGunner.ini",
                 IP + "Sharpshooter.ini"]
NEW_IDENTIFIERS = [
    "Tank_ChinaInfantryFlameThrower", "Tank_ChinaInfantryMiniGunner",
    "Tank_ChinaInfantrySharpshooter",
    "Tank_Command_ConstructChinaInfantryFlameThrower",
    "Tank_Command_ConstructChinaInfantryMiniGunner",
    "Tank_Command_ConstructChinaInfantrySharpshooter",
]
NEW_LABELS = ["OBJECT:KwaiSharpshooter",
              "CONTROLBAR:ConstructKwaiSharpshooter",
              "CONTROLBAR:ToolTipKwaiBuildSharpshooter"]

# v1 ZHE residue guard: none of these may appear in anything we ship
ZHE_MARKERS = [
    "ChinaInfantrySharpshooterVariation", "ChinaInfantrySharpshooter_Wounded",
    "Type79SniperRifle", "Type86Grenade", "Type66Claymore",
    "UpgradeViaRiderSwitch", "IngeniousInfantry", "AreaReconnaissance",
    "SharpshooterVoice", "KwaiZheSNN", "KwaiZheSNS", "NIMRKMN", "CISPINF",
    "SNSharpshooter", "OBJECT:Sharpshooter",
    "CONTROLBAR:ConstructChinaInfantrySharpshooter",
]


# ---------------------------------------------------------------- helpers
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(s):
    return s.replace("\r\n", "\n")


def from_lf(s, eol):
    return s.replace("\n", eol) if eol != "\n" else s


def lf_text(b):
    return to_lf(b.decode("latin-1"))


def replace_exact(s, old, new, count, what=""):
    got = s.count(old)
    assert got == count, "%s: expected %d of %r..., found %d" % (
        what, count, old[:80], got)
    return s.replace(old, new)


WORD = re.compile(r"[0-9A-Za-z_][A-Za-z0-9_\-]*")


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


# ------------------------------------------------------------ load sources
# ONLY archives sorting strictly below this one are sources: the layers
# above (tesla-coil / vehicle-kit / w-economy / fx-enhance / ControlBarPro /
# VetInsignia) embed files derived from OURS and are rebuilt after us.
print("== reading effective sources from", SPE_DIR)
bigs = sorted([f for f in os.listdir(SPE_DIR) if f.lower().endswith(".big")
               and f.lower() < OUT_NAME.lower()], key=str.lower)
assert "zzz-ZZZZZZZKwaiPDL.big" in bigs and OUT_NAME not in bigs
eff_data, eff_owner = {}, {}
for b in bigs:
    for e in read_big(os.path.join(SPE_DIR, b)):
        eff_data[e.path] = e.data
        eff_owner[e.path] = b
for p, owner in EXPECT_OWNERS.items():
    assert eff_owner.get(p) == owner, \
        "ownership drift: %s owned by %s (expected %s)" % (p, eff_owner.get(p), owner)
for p in NEW_INI_PATHS:
    assert p not in eff_data, "new path already claimed: " + p

eff_ini_texts = {p: lf_text(d) for p, d in eff_data.items()
                 if p.lower().endswith(".ini") and p.startswith("Data\\INI")}
eff_all_text = "\n".join(eff_ini_texts.values())
eff_words = set(WORD.findall(eff_all_text))
eff_defined = {}
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _txt in parse_blocks(txt):
        eff_defined.setdefault(name, set()).add(t)

for n in NEW_IDENTIFIERS:
    assert n not in eff_words, "identifier collision: " + n

# ---------------------------------------------- donor drift sanity asserts
print("== donor sanity")


def eff_block(path, typ, name):
    for t, n, _a, _b, btext in parse_blocks(eff_ini_texts[path]):
        if (t, n) == (typ, name):
            return btext
    raise AssertionError("block missing: %s %s in %s" % (typ, name, path))


DONOR_EXPECT = [
    ("Spec_ChinaInfantryFlameThrower", 350, "8.0",
     ["Spec_ChinaBarracks", "Spec_ChinaWarFactory"],
     "Data\\INI\\Object\\China\\SpecialWeapons\\Infantry\\FlameThrower.ini"),
    ("Infa_ChinaInfantryMiniGunner", 550, "14.0",
     ["Infa_ChinaBarracks"],
     "Data\\INI\\Object\\China\\Infantry\\Infantry\\MiniGunner.ini"),
    ("AmericaInfantryPathfinder", 600, "10.0",
     ["AmericaBarracks"], PATH_DONOR),   # + Science = SCIENCE_Pathfinder (dropped)
]
for name, cost, btime, prereqs, path in DONOR_EXPECT:
    blk = eff_block(path, "Object", name)
    m = re.search(r"(?m)^\s*BuildCost\s*=\s*(\d+)", blk)
    assert m and int(m.group(1)) == cost, (name, "cost", m and m.group(1))
    m = re.search(r"(?m)^\s*BuildTime\s*=\s*(\S+)", blk)
    assert m and m.group(1) == btime, (name, "time", m and m.group(1))
    pm = re.search(r"(?ms)^\s*Prerequisites\s*\n(.*?)^\s*End", blk)
    got = [t for line in re.findall(r"(?m)^\s*Object\s*=\s*(.+?)\s*$", pm.group(1))
           for t in line.split()]
    assert got == prereqs, (name, "prereqs", got)
pf_donor = eff_block(PATH_DONOR, "Object", "AmericaInfantryPathfinder")
assert "Science = SCIENCE_Pathfinder" in pf_donor          # the gate we drop
# Kwai cannot buy SCIENCE_Pathfinder (drop is mandatory, artillery precedent)
for rank in ("Rank1", "Rank3", "Rank8"):
    assert "SCIENCE_Pathfinder" not in eff_block(
        CS, "CommandSet", "Tank_SCIENCE_CHINA_CommandSet" + rank), rank
# prereq targets we translate TO all exist
for n in ("Tank_ChinaBarracks", "Tank_ChinaWarFactory", "Tank_ChinaPropagandaCenter"):
    assert "Object" in eff_defined.get(n, set()), "missing Kwai building: " + n
# RedGuard voice events all defined (mod Voice.ini)
REDGUARD_VOICES = ["RedGuardVoiceSelect", "RedGuardVoiceMove",
                   "RedGuardVoiceAttack", "RedGuardVoiceFear",
                   "RedGuardVoiceCreate", "RedGuardVoiceGarrison"]
eff_audio = set()
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _tx in parse_blocks(txt):
        if t in ("AudioEvent", "DialogEvent", "MusicTrack"):
            eff_audio.add(name)
for ev in REDGUARD_VOICES + ["StealthOn", "StealthOff", "MoneyWithdraw"]:
    assert ev in eff_audio, "audio event missing: " + ev
# Redguard really uses this voice set (drift guard for the remap)
rg = eff_block("Data\\INI\\Object\\China\\Vanilla\\Infantry\\Redguard.ini",
               "Object", "ChinaInfantryRedguard")
for ev in REDGUARD_VOICES:
    assert ev in rg, "Redguard donor drift: " + ev
# cameo mapped images exist (engine lookups are case-insensitive; the SA
# page spells it SAPathFinder1)
mapped_images_lc = set()
for p, txt in eff_ini_texts.items():
    for t, name, _a, _b, _tx in parse_blocks(txt):
        if t == "MappedImage":
            mapped_images_lc.add(name.lower())
for img in ("SAPathfinder1", "SAPathfinder1_L", "SNFlameTrooper",
            "SNFlameTrooper_L", "SNMiniGunner", "SNMiniGunner_L"):
    assert img.lower() in mapped_images_lc, "mapped image missing: " + img


# ---------------------------------------------------------------- stubs
def stub(name, comment, portrait, image, model, cost, btime, prereqs, variation,
         kindof):
    return ("; %s: build stub letting China's Tank General (Kwai) produce\n"
            "; %s\n"
            "; Same BuildVariations idiom ShockWave uses for Tank_ChinaVehicleHackerVan\n"
            "; and AirF_AmericaInfantryPathfinder (kwai-roster/kwai-artillery pattern).\n"
            "\n"
            "Object %s\n"
            "\n"
            "  ; *** ART Parameters ***\n"
            "  SelectPortrait         = %s\n"
            "  ButtonImage            = %s\n"
            "\n"
            "  Draw = W3DModelDraw ModuleTag_01\n"
            "    OkToChangeModelColor  = Yes\n"
            "    DefaultConditionState\n"
            "      Model               = %s\n"
            "    End\n"
            "  End\n"
            "\n"
            "  ; set cost and time fields here or else they won't work\n"
            "  BuildCost       = %d\n"
            "  BuildTime       = %s          ;in seconds\n"
            "\n"
            "  Prerequisites\n%s"
            "  End\n"
            "\n"
            "  Side = ChinaTankGeneral\n"
            "  EditorSorting = INFANTRY\n"
            "  BuildVariations = %s\n"
            "\n"
            "  KindOf = %s\n"
            "\nEnd\n" % (TAG, comment, name, portrait, image, model, cost,
                         btime, "".join("    Object = %s\n" % p for p in prereqs),
                         variation, kindof))


STUBS = {
    IP + "FlameTrooper.ini": stub(
        "Tank_ChinaInfantryFlameThrower",
        "Leang's Flame Trooper (Spec_ChinaInfantryFlameThrower; donor prereqs\n"
        "; Spec_ChinaBarracks + Spec_ChinaWarFactory translated to Tank_).",
        "SNFlameTrooper_L", "SNFlameTrooper", "NIPYRO_SKN",
        350, "8.0", ["Tank_ChinaBarracks", "Tank_ChinaWarFactory"],
        "Spec_ChinaInfantryFlameThrower",
        "PRELOAD SELECTABLE CAN_ATTACK CAN_CAST_REFLECTIONS INFANTRY SCORE"),
    IP + "MiniGunner.ini": stub(
        "Tank_ChinaInfantryMiniGunner",
        "Fai's Minigunner (Infa_ChinaInfantryMiniGunner; donor prereq\n"
        "; Infa_ChinaBarracks translated to Tank_ChinaBarracks).",
        "SNMiniGunner_L", "SNMiniGunner", "NICNSCI_SKN",
        550, "14.0", ["Tank_ChinaBarracks"],
        "Infa_ChinaInfantryMiniGunner",
        "PRELOAD SELECTABLE CAN_ATTACK ATTACK_NEEDS_LINE_OF_SIGHT "
        "CAN_CAST_REFLECTIONS INFANTRY SCORE PARACHUTABLE"),
}

# ------------------------------------------------- Sharpshooter CLONE
# Full clone of the effective vanilla-USA Pathfinder (kwai-roster Scout Car
# idiom): stock stealth-sniper mechanics, nothing else.  Documented edits:
SS_TRANSFORMS = [
    ("Object AmericaInfantryPathfinder\n",
     "Object Tank_ChinaInfantrySharpshooter ; " + TAG +
     ": clone of the effective vanilla-USA Pathfinder\n", 1),
    # USA-only upgrade cameo hints dropped (the ArmorUpgrade /
    # ExperienceScalarUpgrade modules stay - inert, Kwai can't research them)
    ("  UpgradeCameo1 = Upgrade_AmericaAdvancedTraining\n",
     "  ;UpgradeCameo1 = NONE ; " + TAG + ": donor Upgrade_AmericaAdvancedTraining"
     " (USA-only research, cameo hint dropped)\n", 1),
    ("  UpgradeCameo2 = Upgrade_AmericaChemicalSuits\n",
     "  ;UpgradeCameo2 = NONE ; " + TAG + ": donor Upgrade_AmericaChemicalSuits"
     " (USA-only research, cameo hint dropped)\n", 1),
    ("  DisplayName      = OBJECT:Pathfinder\n",
     "  DisplayName      = OBJECT:KwaiSharpshooter ; " + TAG + "\n", 1),
    ("  Side = America\n",
     "  Side = ChinaTankGeneral ; " + TAG + " (donor: America)\n", 1),
    ("  Prerequisites\n"
     "    Object = AmericaBarracks\n"
     "    Science = SCIENCE_Pathfinder\n"
     "  End\n",
     "  Prerequisites\n"
     "    Object = Tank_ChinaBarracks ; " + TAG + " (donor: AmericaBarracks)\n"
     "    Object = Tank_ChinaPropagandaCenter ; " + TAG +
     ": tech gate per spec (donor science\n"
     "    ; SCIENCE_Pathfinder dropped - Kwai's promotion tree cannot buy it;\n"
     "    ; kwai-artillery Nuke Cannon precedent)\n"
     "  End\n", 1),
    ("  BuildCost = 600\n",
     "  BuildCost = 1200 ; " + TAG + ": spec cost (donor 600)\n", 1),
    ("  BuildTime = 10.0          ;in seconds  \n",
     "  BuildTime = 30.0          ;in seconds ; " + TAG + ": spec (donor 10.0)\n", 1),
    # RedGuard voice set (China-ish voices per spec; donor events stay defined
    # and in use by the real Pathfinders)
    ("  VoiceSelect = PathfinderVoiceSelect\n",
     "  VoiceSelect = RedGuardVoiceSelect ; " + TAG + ": RedGuard voice set\n", 1),
    ("  VoiceMove = PathfinderVoiceMove\n",
     "  VoiceMove = RedGuardVoiceMove ; " + TAG + "\n", 1),
    ("  VoiceGuard = PathfinderVoiceMove\n",
     "  VoiceGuard = RedGuardVoiceMove ; " + TAG + "\n", 1),
    ("  VoiceAttack = PathfinderVoiceAttack\n",
     "  VoiceAttack = RedGuardVoiceAttack ; " + TAG + "\n", 1),
    ("  VoiceFear = PathfinderVoiceFear\n  SoundStealthOn = StealthOn\n",
     "  VoiceFear = RedGuardVoiceFear ; " + TAG + "\n  SoundStealthOn = StealthOn\n", 1),
    ("  VoiceFear = PathfinderVoiceFear\n  \n",
     "  VoiceFear = RedGuardVoiceFear ; " + TAG + " (donor duplicates the line)\n  \n", 1),
    ("    VoiceCreate          = PathfinderVoiceCreate\n",
     "    VoiceCreate          = RedGuardVoiceCreate ; " + TAG + "\n", 1),
    ("    VoiceGarrison = PathfinderVoiceGarrison\n",
     "    VoiceGarrison = RedGuardVoiceGarrison ; " + TAG + "\n", 1),
    ("    VoiceEnter = PathfinderVoiceMove\n",
     "    VoiceEnter = RedGuardVoiceMove ; " + TAG + "\n", 1),
    ("    VoiceEnterHostile =  PathfinderVoiceMove\n",
     "    VoiceEnterHostile =  RedGuardVoiceMove ; " + TAG + "\n", 1),
    ("    VoiceGetHealed      = PathfinderVoiceMove\n",
     "    VoiceGetHealed      = RedGuardVoiceMove ; " + TAG + "\n", 1),
]
SS_HEADER = (
    "; " + TAG + " (v2): Kwai's Sharpshooter -- a full CLONE of the effective\n"
    "; vanilla-USA Pathfinder (AmericaInfantryPathfinder, zz_SPE_Shw_ini.big):\n"
    "; stock stealth-sniper mechanics (innate stealth while stationary, sniper\n"
    "; rifle, stealth detection), NOTHING exotic.  Documented edits only:\n"
    "; renamed / re-sided to ChinaTankGeneral / Kwai prereqs (science gate\n"
    "; dropped) / $1200 / 30 s per spec / RedGuard voice set / USA upgrade\n"
    "; cameo hints dropped.  Donor art (AIPFDR/ASPFDR models, SAPathfinder1\n"
    "; cameo), weapon (USAPathfinderSniperRifle), armor and locomotor are live\n"
    "; references into the effective space -- no new assets.\n"
    "; (v1 was a Zero Hour Enhanced port; removed -- see README.)\n"
    "\n")


def build_sniper_clone():
    raw = eff_data[PATH_DONOR].decode("latin-1")
    eol = eol_of(raw)
    lf = to_lf(raw)
    out = lf
    for old, new, count in SS_TRANSFORMS:
        out = replace_exact(out, old, new, count, "sniper clone")
    out = SS_HEADER + out
    # exact line-multiset audit (alignment-independent): the clone's line
    # multiset differs from the donor's by EXACTLY the transform swaps + header
    before, after = Counter(lf.split("\n")), Counter(out.split("\n"))
    exp_removed, exp_added = Counter(), Counter()
    for old, new, _c in SS_TRANSFORMS:
        exp_removed.update(old.rstrip("\n").split("\n"))
        exp_added.update(new.rstrip("\n").split("\n"))
    exp_added.update(SS_HEADER.split("\n")[:-1])
    assert before - after == exp_removed - exp_added, \
        ((before - after) - (exp_removed - exp_added),
         (exp_removed - exp_added) - (before - after))
    assert after - before == exp_added - exp_removed, \
        ((after - before) - (exp_added - exp_removed),
         (exp_added - exp_removed) - (after - before))
    return from_lf(out, eol).encode("latin-1"), out


# =========================================================== CommandSet.ini
BAR_ANCHOR = "  5 = Tank_Command_ConstructChinaInfantrySiegeSoldier ; zzz-ZZZZZKwaiRoster\n"
BAR_ADD = (
    "  6 = Tank_Command_ConstructChinaInfantryFlameThrower ; " + TAG + "\n"
    "  7 = Tank_Command_ConstructChinaInfantryMiniGunner ; " + TAG + "\n"
    "  8 = Tank_Command_ConstructChinaInfantrySharpshooter ; " + TAG + "\n")


def patch_commandset(lf):
    assert lf.count(BAR_ANCHOR) == 2  # both Barracks set variants
    return replace_exact(lf, BAR_ANCHOR, BAR_ANCHOR + BAR_ADD, 2, "Barracks 6-8")


# ========================================================= CommandButton.ini
BTN_APPENDIX = "".join("""\
CommandButton Tank_Command_Construct%s
  Command       = UNIT_BUILD
  UnitSpecificSound = MoneyWithdraw
  Object        = %s
  TextLabel     = CONTROLBAR:%s
  ButtonImage   = %s
  ButtonBorderType        = BUILD ; Identifier for the User as to what kind of button this is
  DescriptLabel           = CONTROLBAR:%s
End

""" % row for row in [
    ("ChinaInfantryFlameThrower", "Tank_ChinaInfantryFlameThrower",
     "ConstructChinaInfantryFlameTrooper", "SNFlameTrooper",
     "ToolTipChinaBuildFlameTrooper"),
    ("ChinaInfantryMiniGunner", "Tank_ChinaInfantryMiniGunner",
     "ConstructChinaInfantryMiniGunner", "SNMiniGunner",
     "ToolTipChinaBuildMiniGunner"),
    ("ChinaInfantrySharpshooter", "Tank_ChinaInfantrySharpshooter",
     "ConstructKwaiSharpshooter", "SAPathfinder1",
     "ToolTipKwaiBuildSharpshooter"),
])


def patch_commandbutton(lf):
    if not lf.endswith("\n"):
        lf += "\n"
    return (lf + "\n;;; " + TAG + ": construct buttons (Flame Trooper / "
            "Minigunner reuse donor art+labels; the Sharpshooter is a "
            "Pathfinder clone using its cameo + this layer's own labels)\n"
            + BTN_APPENDIX)


# ============================================================== Generals.str
STR_APPENDIX = (
    "// " + TAG + ": Kwai Sharpshooter strings (authored by this layer;\n"
    "// v1's Zero Hour Enhanced string entries were removed)\n"
    "\n"
    "OBJECT:KwaiSharpshooter\n"
    "\"Sharpshooter\"\n"
    "END\n"
    "\n"
    "CONTROLBAR:ConstructKwaiSharpshooter\n"
    "\"&Sharpshooter\"\n"
    "END\n"
    "\n"
    "CONTROLBAR:ToolTipKwaiBuildSharpshooter\n"
    "\"Stealthy sniper infantry.\\n Invisible while stationary; detects "
    "nearby stealth.\\n\\n Strong vs Infantry\\n Weak vs Vehicles, "
    "Aircraft\"\n"
    "END\n")


def patch_str(lf):
    for lab in NEW_LABELS:
        assert not re.search(r"(?mi)^%s[ \t]*$" % re.escape(lab), lf), \
            "label already present: " + lab
    if not lf.endswith("\n"):
        lf += "\n"
    return lf + "\n" + STR_APPENDIX


# =========================================================== build the text
print("== composing")
sources = {}
for p in (CS, CB, STR):
    raw = eff_data[p].decode("latin-1")
    sources[p] = (to_lf(raw), eol_of(raw))

cs_new = patch_commandset(sources[CS][0])
cb_new = patch_commandbutton(sources[CB][0])
str_new = patch_str(sources[STR][0])
sniper_bytes, sniper_lf = build_sniper_clone()

new_texts = {CS: cs_new, CB: cb_new, STR: str_new,
             IP + "FlameTrooper.ini": STUBS[IP + "FlameTrooper.ini"],
             IP + "MiniGunner.ini": STUBS[IP + "MiniGunner.ini"],
             IP + "Sharpshooter.ini": sniper_lf}
out_files = {}
for p, txt in new_texts.items():
    if p in sources:
        out_files[p] = from_lf(txt, sources[p][1]).encode("latin-1")
    elif p == IP + "Sharpshooter.ini":
        out_files[p] = sniper_bytes
    else:
        out_files[p] = txt.encode("latin-1")

# ========================================================== VERIFICATION
print("== verifying")

# ---- 0. ZERO ZHE residue in anything we ship
shipped_all = "\n".join(new_texts.values())
for marker in ZHE_MARKERS:
    assert marker not in shipped_all, "ZHE residue in shipped text: " + marker
assert len(out_files) == 6, sorted(out_files)
for p in out_files:
    assert not p.lower().endswith((".w3d", ".tga", ".dds", ".wav")), p

# ---- 1. diff audits ---------------------------------------------------
for p in (CB, STR):
    assert out_files[p].startswith(eff_data[p].rstrip(b"\r\n")), \
        "not append-only: " + p
cs_diff = [l for l in difflib.unified_diff(
    sources[CS][0].split("\n"), cs_new.split("\n"), lineterm="", n=0)
    if not l.startswith(("---", "+++", "@@"))]
removed = [l for l in cs_diff if l.startswith("-")]
added = Counter(l[1:] for l in cs_diff if l.startswith("+"))
assert not removed, removed[:5]
assert added == Counter(BAR_ADD.rstrip("\n").split("\n") * 2), added
print("   CommandSet diff: +6 lines, -0, as intended")

# ---- 2. block balance ---------------------------------------------------
assert len(parse_blocks(cs_new)) == len(parse_blocks(sources[CS][0]))
assert len(parse_blocks(cb_new)) == len(parse_blocks(sources[CB][0])) + 3
for p in NEW_INI_PATHS:
    blocks = parse_blocks(new_texts[p])
    assert len(blocks) == 1 and blocks[0][0] == "Object", p
    col0 = sum(1 for l in new_texts[p].split("\n")
               if l.rstrip() == "End" and not l.startswith((" ", "\t")))
    assert col0 == 1, (p, col0)
new_names = {parse_blocks(new_texts[p])[0][1] for p in NEW_INI_PATHS}
assert new_names == set(NEW_IDENTIFIERS[:3]), new_names

# ---- 3. stub + clone closure -------------------------------------------
print("   closure ...")
final_defined = dict(eff_defined)
for n in NEW_IDENTIFIERS[:3]:
    final_defined.setdefault(n, set()).add("Object")
for path, objname, target in (
        (IP + "FlameTrooper.ini", "Tank_ChinaInfantryFlameThrower",
         "Spec_ChinaInfantryFlameThrower"),
        (IP + "MiniGunner.ini", "Tank_ChinaInfantryMiniGunner",
         "Infa_ChinaInfantryMiniGunner"),
        (IP + "Sharpshooter.ini", "Tank_ChinaInfantrySharpshooter", None)):
    txt = strip_comments(new_texts[path])
    if target:
        m = re.search(r"(?m)^\s*BuildVariations\s*=\s*(\S+)\s*$", txt)
        assert m and m.group(1) == target, (path, m and m.group(1))
        assert "Object" in eff_defined.get(target, set()), target
    for pr in re.findall(r"(?m)^\s*Object\s*=\s*(\S+)\s*$", txt):
        assert "Object" in final_defined.get(pr, set()), (path, pr)

# sniper clone: every identifier it references resolves in the effective
# space (clone-of-effective => live by construction, asserted anyway;
# kwai-roster Scout Car precedent)
sniper_nc = strip_comments(sniper_lf)
assert "BuildVariations" not in sniper_nc          # a real clone, not a stub
assert "  BuildCost = 1200" in sniper_lf
assert "  BuildTime = 30.0" in sniper_lf
assert "Side = ChinaTankGeneral" in sniper_nc
assert "SCIENCE_Pathfinder" not in sniper_nc       # science gate dropped
for key, want in ((r"Weapon = PRIMARY (\S+)", "Weapon"),
                  (r"Armor\s+= (\S+)", "Armor"),
                  (r"Locomotor = SET_NORMAL (\S+)", "Locomotor"),
                  (r"CommandSet\s+= (\S+)", "CommandSet")):
    hits = list(re.finditer(r"(?m)^\s*" + key, sniper_nc))
    assert hits, key
    for m in hits:
        tok = m.group(1)
        assert want in eff_defined.get(tok, set()), (want, tok)
donor_nc = strip_comments(lf_text(eff_data[PATH_DONOR]))
dangling = set()
for m in re.finditer(r"(?m)^\s*(?:FX|OCL)\s*=\s*(?:INITIAL|FINAL)\s+(\S+)",
                     sniper_nc):
    tok = m.group(1)
    if eff_defined.get(tok, set()) & {"FXList", "ObjectCreationList"}:
        continue
    # ShockWave's OWN donor text carries a few dangling death-FX refs
    # (e.g. FX_IfantryTeslaDie on dozens of stock USA infantry) - donor
    # parity: allowed iff the unmodified donor already references it
    assert tok in donor_nc, "sniper clone unresolved (not donor-parity): " + tok
    dangling.add(tok)
print("   donor-parity dangling FX/OCL refs (ShockWave ships these): %s"
      % (sorted(dangling) or "none"))
for tok in set(WORD.findall(sniper_nc)):
    if tok.startswith(("FX_", "OCL_", "Upgrade_")):
        assert tok in eff_words, "sniper clone unresolved reference: " + tok
# voice remap complete: no Pathfinder voice event remains; RedGuard's in use
assert "PathfinderVoice" not in sniper_nc
for ev in REDGUARD_VOICES:
    assert ev in sniper_nc, "voice remap missing: " + ev
# cameo art resolves (case-insensitive, engine behavior)
for m in re.finditer(r"(?m)^\s*(?:SelectPortrait|ButtonImage)\s*=\s*(\S+)",
                     strip_comments(shipped_all)):
    assert m.group(1).lower() in mapped_images_lc, m.group(1)
# donor vanilla Pathfinder untouched (we ship a copy, not a patch)
assert "Object AmericaInfantryPathfinder\n" in lf_text(eff_data[PATH_DONOR])

# buttons/labels resolve
str_defined = set(re.findall(
    r"(?mi)^((?:CONTROLBAR|OBJECT|UPGRADE|SCIENCE|TOOLTIP|GUI):[A-Za-z0-9_\-]+)[ \t]*$",
    str_new))
for lab in re.findall(r"\b(?:CONTROLBAR|OBJECT):[A-Za-z0-9_\-]+",
                      strip_comments(BTN_APPENDIX + "\n" + sniper_nc)):
    assert lab in str_defined, "label unresolved: " + lab
for lab in NEW_LABELS:
    assert lab in str_defined, lab

# costs per spec
for path, name, cost in ((IP + "FlameTrooper.ini", "Tank_ChinaInfantryFlameThrower", 350),
                         (IP + "MiniGunner.ini", "Tank_ChinaInfantryMiniGunner", 550),
                         (IP + "Sharpshooter.ini", "Tank_ChinaInfantrySharpshooter", 1200)):
    btext = parse_blocks(new_texts[path])[0][4]
    c = int(re.search(r"(?m)^\s*BuildCost\s*=\s*(\d+)", btext).group(1))
    assert c == cost, (name, c)
# w-economy (rebuilt above us) halves the sniper to 600/15 via override -
# its patcher requires exactly one BuildCost + one BuildTime line per block:
ss_block = parse_blocks(sniper_lf)[0][4]
assert len(re.findall(r"(?m)^[ \t]*BuildCost[ \t]*=", ss_block)) == 1
assert len(re.findall(r"(?m)^[ \t]*BuildTime[ \t]*=", ss_block)) == 1

# ---- 4. sibling survival --------------------------------------------------
print("   sibling survival ...")


def parse_sets(txt):
    sets = {}
    for t, name, _a, _b, btext in parse_blocks(txt):
        if t != "CommandSet":
            continue
        slots = {}
        for sm in re.finditer(r"(?m)^\s*(\d+)\s*=\s*(\S+)", btext):
            slots[int(sm.group(1))] = sm.group(2)
        sets[name] = slots
    return sets


def verify_survival(cs_txt, installed=False):
    lf = to_lf(cs_txt)
    s = parse_sets(lf)
    for n in ("Tank_ChinaBarracksCommandSet", "Tank_ChinaBarracksCommandSetUpgrade"):
        b = s[n]
        assert b[5] == "Tank_Command_ConstructChinaInfantrySiegeSoldier", n
        assert b[6] == "Tank_Command_ConstructChinaInfantryFlameThrower", n
        assert b[7] == "Tank_Command_ConstructChinaInfantryMiniGunner", n
        assert b[8] == "Tank_Command_ConstructChinaInfantrySharpshooter", n
        assert b[12] == "Command_UpgradeChinaRedguardCaptureBuilding", n
        assert b[13] in ("Command_UpgradeChinaMines", "Command_UpgradeEMPMines"), n
        assert b[14] == "Command_Sell", n
        assert set(b) == {1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14}, (n, sorted(b))
    assert lf.count("Tank_Command_UpgradeKwaiPDL ;") == 17          # PDL
    for n in ("Tank_ChinaVehicleBattleMasterCommandSetTower",
              "Tank_ChinaVehicleBattleMasterCommandSetPDL",
              "Tank_ChinaTankEmperorGattlingCommandSet",
              "Tank_ChinaTankEmperorPDLCommandSet",
              "Tank_ChinaTankDragonCommandSet",
              "Tank_ChinaTankDragonUpgradedCommandSet",
              "Tank_ChinaReaperCommandSet"):
        assert n in s, "PDL set lost: " + n
    wf = s["Tank_ChinaWarFactoryCommandSet_Down"]                    # roster
    assert wf[4] == "Tank_Command_ConstructChinaTankOverlord"
    assert wf[7] == "Tank_Command_ConstructChinaVehicleScoutCar"
    for i in (8, 9, 10, 11):
        assert i not in wf
    for n in ("Tank_ChinaAirfieldCommandSet", "Tank_ChinaAirfieldCommandSetUpgrade"):
        a = s[n]
        assert a[3] == "Tank_Command_ConstructChinaJetMIGFighter"
        assert a[4] == "Tank_Command_ConstructChinaJetMIGBomber"
        for i in (5, 6, 7, 8, 9):
            assert a[i] == "Command_StructureExit", (n, i)
        assert a[10] == "Command_Evacuate"
    for v in ("One", "OneUpgrade", "Two", "TwoUpgrade"):             # kwai-uav
        ic = s["Tank_ChinaInternetCenterCommandSet" + v]
        assert ic[7] == "Tank_Command_UpgradeKwaiUAVProgram" \
            and ic[8] == "Tank_Command_KwaiUAVDeploy" \
            and ic[9] == "Command_Evacuate", (v, ic)
    pc = {n: b for n, b in s.items() if n.startswith("Tank_ChinaPropagandaCenter")}
    assert len(pc) == 50, len(pc)                                    # doctrine
    for n in ("Tank_ChinaWarFactoryCommandSet", "Tank_ChinaWarFactoryCommandSetUpgrade"):
        assert s[n][11] == "Tank_Command_ConstructChinaVehicleInfernoCannon", n
        assert s[n][12] == "Command_ChinaButtonCommandSetOneDown", n
    stem = ("  3  = Command_ConstructAmericaVehicleHellfireDrone\n"
            "  4  = Command_TransportExit\n"
            "  5  = Command_TransportExit\n"
            "  6  = Command_TransportExit\n"
            "  7  = Command_TransportExit\n")
    assert lf.count(stem + "  8  = Command_Evacuate\n") == 1         # mammoth
    assert lf.count(stem + "  8  = Command_Evacuate \n") == 4
    assert s["Tank_ChinaDozerCommandSet"][13] == "Command_ChinaButtonCommandSetOneDown"
    dz2 = s["Tank_ChinaDozerCommandSet_Down"]
    assert dz2[7] == "Tank_Command_ConstructChinaBunker"
    assert dz2[8] == "Tank_Command_ConstructChinaHackerBunker"
    for n in ("Tank_ChinaHackerBunkerCommandSet", "Tank_ChinaPowerPlantCommandSet",
              "Tank_ChinaPowerPlantCommandSetUpgrade", "GlobalHawkCommandSet"):
        assert n in s, "sibling set lost: " + n
    emp = s["Tank_ChinaTankEmperorDefaultCommandSet"]                # emperor
    assert emp[10] == "Tank_Command_UpgradeChinaOverlordGattlingCannon"
    assert emp[12] == "Command_Evacuate"
    assert lf.count("Command_Evacuate") >= 60                        # garrisons
    assert "CommandSet Tank_ChinaVehicleBattleMasterCommandSetERA\n" in lf
    vpc = s["ChinaPropagandaCenterCommandSet"]
    assert vpc[1] == "Command_UpgradeChinaNationalism" and 10 not in vpc
    # v1 ZHE command sets must be GONE
    assert "ChinaInfantrySharpshooterCommandSet" not in lf
    print("   commandset survival OK%s" % (" (installed)" if installed else ""))


verify_survival(cs_new)
for bn in ("Tank_Command_UpgradeKwaiPDL", "Tank_Command_KwaiUAVDeploy",
           "Tank_Command_ConstructChinaTankJS7",
           "Tank_Command_ConstructChinaInfantrySiegeSoldier",
           "Tank_Command_ConstructChinaVehicleInfernoCannon"):
    assert ("CommandButton %s\n" % bn) in cb_new, bn

# ---- 5. archive name sort position (both real dirs) -----------------------
for d in (SPE_DIR, SHW_DIR):
    listing = sorted(set(os.listdir(d)) | {OUT_NAME, "zzz-ZZZZZZZRotrProbe.big"},
                     key=str.lower)
    i = listing.index(OUT_NAME)
    after = [f for f in listing[:i] if f.lower().endswith(".big")]
    before = [f for f in listing[i + 1:] if f.lower().endswith(".big")]
    assert "zzz-ZZZZZZZKwaiPDL.big" in after, d + ": must sort after PDL"
    assert "zzz-ZZZZZZZRotrProbe.big" in before, d + ": must sort before R*"
    assert any(f.startswith("zzz_ControlBarPro") for f in before), \
        d + ": must sort before ControlBarPro skins"
print("   sort order OK in both mod dirs")

# ============================================================ write + install
entries = [BigEntry(p, data) for p, data in sorted(out_files.items())]
out_path = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_path)
print("== wrote %s (%d files, %.1f KB)" % (
    OUT_NAME, len(entries), os.path.getsize(out_path) / 1e3))

with open(out_path, "rb") as f:
    blob = f.read()
for dest in (SPE_DIR, SHW_DIR):
    dst = os.path.join(dest, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob)
    back = read_big(dst)
    assert {e.path: e.data for e in back} == out_files, "install verify: " + dst
    verify_survival(next(e.data for e in back if e.path == CS).decode("latin-1"),
                    installed=True)
    print("== installed + re-verified:", dst)

print("\nOK (v2).  Barracks 6 Flame Trooper ($350) / 7 Minigunner ($550) / "
      "8 Sharpshooter ($1200, Pathfinder clone).")
print("REMINDER: rebuild the layers above in order: tesla-coil -> vehicle-kit"
      " -> w-economy (they embed files derived from this layer).")
