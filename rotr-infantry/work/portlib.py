"""Block-editing helpers + the full port recipe (blocks, edits, remaps)
for the ROTR infantry port.  build.py drives this; integrate.py reuses the
fragment outputs.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "chaos-units", "work"))
from iniblocks import load_tree, parse_blocks  # noqa: E402
import portdefs  # noqa: E402

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")


def strip_comments_line(line):
    i = line.find(";")
    j = line.find("//")
    if i >= 0 and (j < 0 or i < j):
        return line[:i]
    if j >= 0:
        return line[:j]
    return line


# ---------------------------------------------------------------- editing
def strip_submodule(text, opener_re):
    """Remove a sub-block whose opener line matches opener_re (regex on the
    stripped line).  The block ends at the first following line that is
    'End' at the same indentation.  Returns (new_text, removed_count)."""
    lines = text.split("\n")
    out = []
    removed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)" + opener_re, strip_comments_line(line).rstrip())
        if m:
            indent = m.group(1)
            j = i + 1
            end_re = re.compile(r"^" + re.escape(indent) + r"End\s*$")
            while j < len(lines):
                if end_re.match(strip_comments_line(lines[j]).rstrip()):
                    break
                j += 1
            if j >= len(lines):
                raise ValueError("unterminated sub-block for %r" % opener_re)
            removed += 1
            i = j + 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out), removed


def strip_module(text, tag):
    new, n = strip_submodule(
        text, r"Behavior\s*=\s*[A-Za-z0-9_]+\s+%s\b.*$" % re.escape(tag))
    if n != 1:
        raise ValueError("module strip %s: removed %d blocks (want 1)" % (tag, n))
    return new


def strip_lines(text, line_re):
    """Remove whole lines matching line_re (on comment-stripped content)."""
    rx = re.compile(line_re)
    out = []
    removed = 0
    for line in text.split("\n"):
        if rx.search(strip_comments_line(line)):
            removed += 1
            continue
        out.append(line)
    return "\n".join(out), removed


def retoken(text, mapping):
    """Word-boundary token replacement (also inside comments, harmless)."""
    if not mapping:
        return text
    rx = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?::[A-Za-z0-9_\-]+)?")

    def sub(m):
        return mapping.get(m.group(0), m.group(0))
    return rx.sub(sub, text)


# ---------------------------------------------------------------- recipe
# FX voice-wrapper remaps (donor FXLists that only wrap a ROTR death voice;
# FX_GIDie is the canonical vanilla infantry death FX):
FX_REMAP = {
    "FX_ShmelTrooperDie": "FX_GIDie",
    "FX_ShmelTrooperDieByFlame": "FX_GIDie",
    "FX_ShmelTrooperDieByToxin": "FX_GIDie",
    "FX_ShmelTrooperDieByTesla": "FX_GIDie",
    "FX_ShockTrooperDie": "FX_GIDie",
    "FX_ShockTrooperDieFire": "FX_GIDie",
    "FX_ShockTrooperDieToxin": "FX_GIDie",
    "FX_ShockTrooperDieTesla": "FX_GIDie",
}

# ROTR audio events -> base events (verified in base audio INI space by
# the build's audio scan; build fails loudly on any unmapped donor event).
AUDIO_REMAP = {
    # Shmel Trooper: China Tank Hunter (vanilla missile infantry)
    "ShmelTrooperVoiceSelect": "TankHunterVoiceSelect",
    "ShmelTrooperVoiceMove": "TankHunterVoiceMove",
    "ShmelTrooperVoiceAttack": "TankHunterVoiceAttack",
    "ShmelTrooperVoiceFear": "TankHunterVoiceFear",
    "ShmelTrooperVoiceCreate": "TankHunterVoiceCreate",
    "ShmelTrooperVoiceSmokeAttack": "TankHunterVoiceAttack",
    "ShmelTrooperVoiceAntiToxinAttack": "TankHunterVoiceAttack",
    "ShmelTrooperVoiceDie": "TankHunterVoiceDie",
    # Shock Trooper: ShockWave China Pyro (suited flame trooper)
    "ShockTrooperVoiceSelect": "PyroVoiceSelect",
    "ShockTrooperVoiceMove": "PyroVoiceMove",
    "ShockTrooperVoiceAttack": "PyroVoiceAttack",
    "ShockTrooperVoiceAttackTesla": "PyroVoiceAttack",
    "ShockTrooperVoiceFear": "PyroVoiceFear",
    "ShockTrooperVoiceCreate": "PyroVoiceCreate",
    "ShockTrooperVoiceGarrison": "PyroVoiceGarrison",
    "ShockTrooperVoiceModeRifle": "PyroVoiceMove",
    "ShockTrooperVoiceModeTeslaGun": "PyroVoiceMove",
    # weapon / FX sounds
    "ShmelRocketLauncherWeapon": "TankHunterWeapon",
    "ShmelRocketExplosion": "ExplosionFire",
    "ShockTrooperRifleWeapon": "RocketBuggyWeapon",
    "ShockTrooperTeslaWeaponSound": "AvengerPointDefenseLaserPulse",
    # sounds inside ported FXLists
    "GenericAutoCannonDetonationImpact": "ExplosionRocketBuggyMissile",
    "InfantryTeslaDeathShock": "ExplosionPatriotEMP",
    "MoleBombDirstSound": "ExplosionDirt",
    "ShmelRocketAntiToxinActivated": "ExplosionFlashBang",
    "ShmelRocketAntiToxinDetonation": "ExplosionFlashBang",
}

PREREQ_REMAP = {
    "RussiaWarFactory": "Tank_ChinaWarFactory",
    "RussiaWeaponsBunker": "Tank_ChinaWarFactory",
}

# what ships where ------------------------------------------------------
OBJECT_FILES = {
    "Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShmelTrooper.ini": [
        ("Object", "RussianInfantryShmelTrooper"),
        ("Object", "ShmelTrooperRocket"),
        ("Object", "ShmelTrooperSmokeRocketProjectile"),
        ("ObjectReskin", "ShmelTrooperSmokeRocketHeroicProjectile"),
        ("Object", "ShmelTrooperAntiToxinRocketProjectile"),
        ("ObjectReskin", "ShmelTrooperAntiToxinRocketHeroicProjectile"),
        ("Object", "RussianShmelTrooperAntiToxinFoam"),
        ("Object", "RussianSmokeGrenadeSmokeScreen"),
        ("Object", "ShmellBurningEmbersFireField"),
        ("Object", "GenericHitScanProjectile"),
    ],
    "Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShockTrooper.ini": [
        ("Object", "RussiaInfantryShockTrooper"),
        ("Object", "RussiaInfantryShockTrooper_Var1"),
        ("ObjectReskin", "RussiaInfantryShockTrooper_Var2"),
        ("ObjectReskin", "RussiaInfantryShockTrooper_Var3"),
        ("Object", "ShockTrooperGuidedMissile"),
        ("Object", "ShockTrooperRemoveUpgradeRocketRifleObject"),
        ("Object", "ShockTrooperRemoveUpgradeTeslaGunObject"),
        ("Object", "TeslaTrooperLaserBeam"),
    ] + [("Object", "TeslaTrooperElectricBolt%d" % i) for i in range(1, 9)] + [
        ("Object", "HeroicTeslaTrooperLaserBeam"),
    ] + [("Object", "HeroicTeslaTrooperElectricBolt%d" % i) for i in range(1, 9)] + [
        ("Object", "TeslaInfantry"),
    ],
}

SHARED_APPENDS = {
    "Weapon.ini": [
        "RussiaShmellTrooperMissileLauncher",
        "RussiaShmellTrooperSmokeMissileLauncher",
        "RussiaShmellTrooperSmokeMissileLauncherHeroic",
        "RussiaShmellTrooperAntiToxinMissileLauncher",
        "RussiaShmellTrooperAntiToxinMissileLauncherHeroic",
        "RussiaShmellTrooperSmokeMissilePellets",
        "RussiaShmellTrooperExtraDamageWithInfantryMunitionUpgrade",
        "RussianShmelTrooperAntiToxinSmokeWeapon",
        "RussianSmokeGrenadeSmokeScreenWeapon",
        "PyroFireWalFieldWeapon",
        "ShockTrooperRocketRifle",
        "ShockTrooperTeslaWeapon",
        "ShockTrooperTeslaSubdualWeapon",
        "HeroicShockTrooperTeslaWeapon",
        "HeroicShockTrooperTeslaSubdualWeapon",
        "ShockTrooperSwitchToRocketGunMode",
        "ShockTrooperSwitchToTeslaGunMode",
    ],
    "Armor.ini": ["ShockTrooperArmor", "InvulnerableArmorAll"],
    "Locomotor.ini": [
        "ShockTrooperLocomotor", "ShmelRocketLocomotor",
        "ShocktrooperRocketRifleLocomotor", "BerkutMissileDodgeJetLocomotor",
    ],
    "FXList.ini": [
        "FX_MoleBombEnterOrExitGround",
        "FX_ShmelTrooperAntiToxinRocketExplosion",
        "WeaponFX_ShmelRocketExplosion",
        "WeaponFX_ShmelRocketExplosionUpgraded",
        "WeaponFX_ShmelTrooperAntiToxinSmoke",
        "FX_ShockTrooperRocketExplosion",
        "WeaponFX_GenericShockTrooperRocketRifleFire",
        "WeaponFX_GenericShockTrooperRocketRifleFireWithRedTracers",
        "FX_IfantryTeslaDie",
    ],
    "ParticleSystem.ini": [
        "ShmelRocketExhaust", "HeroicShmelRocketExhaust", "ShmelRocketLenzflare",
        "ShmelExplosion", "ShmelDetonationDustWave",
        "ShmelAntiToxinRocketExhaust", "ShmelRocketAntiToxinDebris",
        "ShmelRocketAntiToxinDetonationCloud", "ShmelRocketAntiToxinExplosion",
        "ShmelRocketAntiToxinSmoke",
        "NapalmPoolSmoke", "ShmelPoolFire", "ShmelPoolFireMainRing",
        "EmptyShockRocketCassingsFalling",
        "TeslaTrooperFlare", "HeroicTeslaTrooperFlare",
    ],
    "ObjectCreationList.ini": [
        "OCL_RussiaExplodedDeath", "OCL_RussiaExplodedDeathShockTrooper",
        "OCL_ShmelTrooperSmokeScreen", "OCL_ShmelTrooperAntiToxinFoam",
        "OCL_ShmellRocketFire",
        "OCL_ShockTrooperRocketRifleModeTrigger", "OCL_GenericDummyRider2Trigger",
        "OCL_TeslaDeathInfantry", "OCL_ViralInfantryDeath",
    ],
}

MAPPED_IMAGES = [
    "SRShmelTrooper", "SRShmelTrooper_L", "SRShockTrooper", "SRShockTrooper_L",
    "SSRocketShmelSmoke", "SSRocketShmelAntiTox", "SSHEShockRocket",
    "SSElectricShockRocket",
]

# extra death-module strips shared by both units (cryo chain dropped)
CRYO_TAG = "ModuleTag_03231"


def load_donor():
    return load_tree(portdefs.DONOR_INI)


def edit_block(t, name, text):
    """Apply the per-block structural edits to a donor block (before the
    global token renames/remaps).  Returns final text."""
    for tag in portdefs.MODULE_STRIPS.get(name, []):
        text = strip_module(text, tag)
    if name in ("RussianInfantryShmelTrooper", "RussiaInfantryShockTrooper_Var1"):
        text = strip_module(text, CRYO_TAG)          # LASERED cryo death chain
        # catch-all death module owns LASERED and EXTRA_8 again:
        def fix_catchall(m):
            return m.group(0).replace(" -LASERED", "").replace(" -EXTRA_8", "")
        text, n = re.subn(r"^\s*DeathTypes\s*=\s*ALL[^\n]*$", fix_catchall,
                          text, count=1, flags=re.M)
        assert n == 1, "catch-all DeathTypes line not found in %s" % name
        # drop upgrade cameos of unreachable Russia upgrades
        text, _ = strip_lines(text, r"^\s*UpgradeCameo\d\s*=")
    if name == "RussianInfantryShmelTrooper":
        # PLAYER_UPGRADE weapon sets reference the dropped Upgraded weapons
        text, n = strip_player_upgrade_weaponsets(text)
        assert n == 2, "expected 2 PLAYER_UPGRADE weaponsets, removed %d" % n
    if name == "ShmelTrooperRocket":
        # thermobaric fire-field gate: Russia's Larger Clips -> Kwai-reachable
        # Black Napalm (re-side of the donor's upgrade gate; see README)
        text, n = re.subn(r"TriggeredBy\s*=\s*Upgrade_RussiaLargerClips",
                          "TriggeredBy  = Upgrade_ChinaBlackNapalm", text)
        assert n == 1, "fire-field TriggeredBy not found"
    if name in ("ShockTrooperRemoveUpgradeRocketRifleObject",
                "ShockTrooperRemoveUpgradeTeslaGunObject"):
        text = text.replace("Side                = Russia",
                            "Side                = ChinaTankGeneral")
    return text


def strip_player_upgrade_weaponsets(text):
    """Remove WeaponSet blocks whose Conditions include PLAYER_UPGRADE."""
    lines = text.split("\n")
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^(\s*)WeaponSet\s*$", strip_comments_line(line).rstrip()):
            indent = re.match(r"^(\s*)", line).group(1)
            j = i + 1
            end_re = re.compile(r"^" + re.escape(indent) + r"End\s*$")
            while j < len(lines) and not end_re.match(
                    strip_comments_line(lines[j]).rstrip()):
                j += 1
            body = "\n".join(lines[i:j + 1])
            if re.search(r"Conditions\s*=.*PLAYER_UPGRADE", body):
                removed += 1
                i = j + 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out), removed
