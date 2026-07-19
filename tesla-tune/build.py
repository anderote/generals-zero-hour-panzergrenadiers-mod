#!/usr/bin/env python3
"""Build zzz-ZZZZZZZZZZZZZZZZ0TeslaTune.big - the "Tesla Tune" layer for Kwai
(China Tank General) Shock Trooper, ShockWave under GeneralsX (macOS).

TWO features, pure data, one layer that sorts ABOVE every data layer
(16 Z's + '0' sorts after the current top data layer
zzz-ZZZZZZZZZZZZZZZ0EmperorInnatePDL.big = 15 Z's) and, because
'-' (0x2D) < '_' (0x5F) < 'z' (0x7A), BELOW zzz_ControlBarPro* and
zzzz_FXEnhance.  It re-ships the effective Weapon.ini (owner TeslaFinish) and
the effective RotrShockTrooper.ini (owner InfantryScale), preserving every
other byte, and becomes the new effective owner of both.

TASK A - MAKE THE PRIMARY SHOT'S LIGHTNING VISIBLE
  Engine finding (GeneralsMD Weapon.cpp): a single Weapon canNOT both fire a
  ProjectileObject AND draw a LaserName beam.  fireWeaponTemplate (Weapon.cpp
  1015-1094) is an if/else: when the weapon has a ProjectileObject and this is
  the initial fire (isProjectileDetonation == false) it takes the `else` branch
  (line 1094) which spawns the projectile and NEVER calls createLaser().
  createLaser() - the only code that draws the LaserName bolt (line 1037/1043)
  - runs only when getProjectileTemplate()==nullptr (hitscan) OR
  isProjectileDetonation==true; at detonation the source passed in is the
  PROJECTILE itself (DumbProjectileBehavior.cpp:539 -> `obj`), so any laser
  there is a degenerate zero-length flash at the impact point, not a bolt from
  the trooper.  W3DLaserDraw on the projectile object is likewise non-viable:
  W3DLaserDraw::doDrawModule (W3DLaserDraw.cpp:258-262) hard-requires a
  ClientUpdate=LaserUpdate module, and LaserUpdate's endpoints are set ONLY by
  Weapon::createLaser -> initLaser (never runs for a projectile), so the beam
  would draw at the origin.
  => Because we MUST keep the projectile (its ProjectileDetonationOCL spawns the
  stun/chain node RELATIVE TO THE PROJECTILE so the chain fires even when the
  trooper is garrisoned inside a tank/building - Weapon.cpp:952), the fix is to
  make the PROJECTILE clearly visible: attach the tesla-coil family's own
  continuous spark system TeslaBoltSparks (SystemLifetime=0 -> emits for the
  whole flight, bright ADDITIVE EXFuzzyDot sparks, CRITICAL priority) to the
  projectile bone, ALONGSIDE the existing (1-frame) TeslaTrooperFlare puff.
  This paints a continuous crackling electric bolt-trail from the trooper to
  the target - visible even when firing from inside a container - and does NOT
  touch the projectile/OCL/detonation wiring, so garrisoned chain firing is
  preserved byte-for-byte.  (fx-enhance was rebuilt: TeslaBoltSparks,
  TeslaTrooperFlare, ShockTrooperTeslaBlast, FX_ShockTrooperElectricRocket
  Explosion all resolve in the effective ParticleSystem/FXList - no masking.)
  The dramatic hitscan bolt on the chain arcs (ShockTrooperTeslaChainZap uses
  LaserName=TeslaBoltRandom, WeaponSpeed=99999) is unchanged and still renders.

TASK B - NERF fire rate, range, damage on every Shock Trooper weapon variant
  PRIMARY ShockTrooperTeslaWeapon:  Damage 150->120 (-20%), Range 140->100,
    DelayBetweenShots 2400->3200 (~33% slower).
  Chain arc  ShockTrooperTeslaChainZap:        Damage 100->80, Range 90->65.
  Chain arc  HeroicShockTrooperTeslaChainZap:  Damage 120->96 (keeps the +20%
    heroic bump over the reduced 80 base), Range 90->65.
  Stun pulse ShockTrooperTeslaStunPulse:        Range 20->15 (~-25%).
  Stun pulse HeroicShockTrooperTeslaStunPulse:  Range 20->15 (~-25%).
  The chain/stun DelayBetweenShots (500 / 450) are the internal cadence of the
  SPAWNED NODE's own arcs (fired via FireWeaponUpdate on the node the primary's
  detonation OCL creates), NOT the trooper's own fire rate - so they are left
  unchanged (only the PRIMARY's DelayBetweenShots gates how fast the trooper
  shoots).  Stun subdual damage (220/280) is left alone (the task asked to cut
  stun RANGE only).  All WeaponBonus / DamageType / DeathType / OCL / projectile
  / anti-air lines are preserved verbatim.  There is no separate Heroic PRIMARY
  weapon (heroic-ness on the primary comes from VeterancyProjectileDetonationOCL
  = HEROIC OCL_ShockTrooperTeslaChainHeroic, not a HERO weapon set), so the
  primary is nerfed once.
"""

import os
import re
import sys
import difflib
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hotkey-addon"))
from bigfile import BigEntry, read_big, write_big_file  # noqa: E402

SPE_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWaveSPE")
SHW_DIR = os.path.expanduser("~/GeneralsX/mods/ShockWave")

OUT_NAME = "zzz-ZZZZZZZZZZZZZZZZ0TeslaTune.big"
TAG = "tesla-tune"

WPN_PATH = "Data\\INI\\Weapon.ini"
OBJ_PATH = "Data\\INI\\Object\\China\\Tank\\Infantry\\RotrShockTrooper.ini"
PS_PATH = "Data\\INI\\ParticleSystem.ini"

# expected effective owners of the two files we re-ship (verified at build time)
WPN_OWNER = "zzz-ZZZZZZZZZZZZZ0TeslaFinish.big"
OBJ_OWNER = "zzz-ZZZZZZZZZInfantryScale.big"
OWNERS = {WPN_PATH: WPN_OWNER, OBJ_PATH: OBJ_OWNER}

# archives that legitimately sort ABOVE us (they must claim NONE of our paths)
ABOVE_OK = {"zzzz_fxenhance.big", "zzz_controlbarprozh.big",
            "zzz_controlbarpro2160zh.big"}

# the new visible-trail particle system (must resolve in effective data)
TRAIL_PS = "TeslaBoltSparks"

# ---- per-block field edits for Task B (weapon -> [(old_line, new_line), ...])
def nerf(oldval, newval, note):
    return note  # placeholder; edits are built inline below

WEAPON_EDITS = {
    "ShockTrooperTeslaWeapon": [
        ("  PrimaryDamage           = 150.0",
         "  PrimaryDamage           = 120.0 ; %s nerf: was 150.0 (-20%%)" % TAG),
        ("  AttackRange             = 140.0",
         "  AttackRange             = 100.0 ; %s nerf: was 140.0 (shorter range)" % TAG),
        ("  DelayBetweenShots       = 2400",
         "  DelayBetweenShots       = 3200 ; %s nerf: was 2400 (~33%% slower fire rate)" % TAG),
    ],
    "ShockTrooperTeslaChainZap": [
        ("  PrimaryDamage           = 100.0",
         "  PrimaryDamage           = 80.0 ; %s nerf: was 100.0 (-20%%)" % TAG),
        ("  AttackRange             = 90.0",
         "  AttackRange             = 65.0 ; %s nerf: was 90.0 (shorter chain reach)" % TAG),
    ],
    "HeroicShockTrooperTeslaChainZap": [
        ("  PrimaryDamage           = 120.0",
         "  PrimaryDamage           = 96.0 ; %s nerf: was 120.0 (keeps +20%% heroic bump over new 80 base)" % TAG),
        ("  AttackRange             = 90.0",
         "  AttackRange             = 65.0 ; %s nerf: was 90.0 (shorter chain reach)" % TAG),
    ],
    "ShockTrooperTeslaStunPulse": [
        ("  AttackRange             = 20.0",
         "  AttackRange             = 15.0 ; %s nerf: was 20.0 (~-25%% stun reach)" % TAG),
    ],
    "HeroicShockTrooperTeslaStunPulse": [
        ("  AttackRange             = 20.0",
         "  AttackRange             = 15.0 ; %s nerf: was 20.0 (~-25%% stun reach)" % TAG),
    ],
}
# fields that must survive verbatim in the primary block (spot-check)
PRIMARY_KEEP = ["ProjectileObject        = ShockTrooperTeslaBoltProjectile",
                "ProjectileDetonationOCL = OCL_ShockTrooperTeslaChain",
                "VeterancyProjectileDetonationOCL = HEROIC OCL_ShockTrooperTeslaChainHeroic",
                "ProjectileDetonationFX  = FX_ShockTrooperElectricRocketExplosion",
                "WeaponBonus             = GARRISONED RANGE  145%",
                "WeaponBonus             = GARRISONED DAMAGE 125%",
                "WeaponBonus             = PLAYER_UPGRADE RANGE  145%",
                "WeaponBonus             = PLAYER_UPGRADE DAMAGE 125%",
                "DamageType              = EXPLOSION",
                "DeathType               = BURNED",
                "PrimaryDamageRadius     = 20.0",
                "WeaponSpeed             = 400"]


# ------------------------------------------------------------------ helpers
def eol_of(raw):
    crlf = raw.count("\r\n")
    lf = raw.count("\n") - crlf
    assert raw.count("\r") == crlf, "stray CR"
    assert crlf == 0 or lf == 0, "mixed EOLs"
    return "\r\n" if crlf else "\n"


def to_lf(raw):
    return raw.replace("\r\n", "\n")


def from_lf(lf_text, eol):
    return lf_text.replace("\n", eol) if eol != "\n" else lf_text


def replace_exact(s, old, new, count=1):
    assert s.count(old) == count, \
        "expected %d occurrences of %r, found %d" % (count, old[:80], s.count(old))
    return s.replace(old, new)


def weapon_block(lf, name):
    m = re.search(r"(?ms)^Weapon[ \t]+%s[ \t]*\n.*?^End[ \t]*$" % re.escape(name), lf)
    assert m, "weapon block not found: " + name
    return m.group(0)


def unified(a, b):
    return [l for l in difflib.unified_diff(
        a.splitlines(), b.splitlines(), lineterm="", n=0)
        if not l.startswith(("---", "+++", "@@"))]


def end_lines(lf):
    return len(re.findall(r"(?mi)^\s*End\s*$", lf))


# ================================================== 1. effective sources
archives = sorted((f for f in os.listdir(SPE_DIR)
                   if f.lower().endswith(".big") and f.lower() < OUT_NAME.lower()),
                  key=str.lower, reverse=True)
cache = {a: read_big(os.path.join(SPE_DIR, a)) for a in archives}


def effective(path):
    want = path.lower()
    for a in archives:
        for e in cache[a]:
            if e.path.lower() == want:
                return e.data.decode("latin-1"), a
    return None, None


sources = {}
for path, owner in OWNERS.items():
    data, got = effective(path)
    assert data is not None, "effective source not found: " + path
    assert got == owner, "ownership drift for %s: %s (expected %s)" % (path, got, owner)
    sources[path] = data
print("effective-file ownership verified: Weapon.ini <- %s, RotrShockTrooper.ini <- %s"
      % (WPN_OWNER, OBJ_OWNER))

# closure blob over the whole effective INI space (below us)
seen = set()
ini_blob = []
for a in archives:
    for e in cache[a]:
        lp = e.path.lower()
        if lp in seen or not lp.endswith(".ini"):
            continue
        seen.add(lp)
        ini_blob.append(to_lf(e.data.decode("latin-1")))
blob = "\n".join(ini_blob)

for kw, name in (("Object", "TeslaBoltRandom"),
                 ("ParticleSystem", TRAIL_PS),
                 ("ParticleSystem", "TeslaTrooperFlare"),
                 ("ObjectCreationList", "OCL_ShockTrooperTeslaChain"),
                 ("ObjectCreationList", "OCL_ShockTrooperTeslaChainHeroic"),
                 ("FXList", "FX_ShockTrooperElectricRocketExplosion"),
                 ("AudioEvent", "TeslaCoilWeapon")):
    assert re.search(r"(?m)^%s\s+%s\b" % (kw, re.escape(name)), blob), \
        "unresolved reference: %s %s" % (kw, name)
print("closure OK: trail system %s + TeslaBoltRandom/OCLs/detonation-FX/sound all resolve"
      % TRAIL_PS)

# ================================================== 2. Task B - Weapon.ini
def patch_weapon(src_lf):
    out = src_lf
    for wname, edits in WEAPON_EDITS.items():
        blk = weapon_block(out, wname)
        newblk = blk
        for old, new in edits:
            newblk = replace_exact(newblk, old, new)
        out = replace_exact(out, blk, newblk)
    return out


# ================================================== 3. Task A - projectile trail
PROJ_ANCHOR = "      ParticleSysBone = None TeslaTrooperFlare\n"
PROJ_INSERT = (PROJ_ANCHOR +
               "      ParticleSysBone = None %s ; %s: continuous bright"
               " tesla-family spark trail (SystemLifetime=0) so the flying"
               " bolt is VISIBLE, incl. from inside a container\n" % (TRAIL_PS, TAG))


def patch_object(src_lf):
    # the anchor line must be unique to the projectile object
    assert src_lf.count(PROJ_ANCHOR) == 1, \
        "projectile trail anchor not unique: %d" % src_lf.count(PROJ_ANCHOR)
    return replace_exact(src_lf, PROJ_ANCHOR, PROJ_INSERT)


# ================================================== 4. build shipped texts
patched = {}
patched[WPN_PATH] = from_lf(patch_weapon(to_lf(sources[WPN_PATH])),
                            eol_of(sources[WPN_PATH]))
patched[OBJ_PATH] = from_lf(patch_object(to_lf(sources[OBJ_PATH])),
                            eol_of(sources[OBJ_PATH]))

# ================================================== 5. verification
# ---- Weapon.ini diff audit: exactly the intended field lines changed
wdiff = unified(to_lf(sources[WPN_PATH]), to_lf(patched[WPN_PATH]))
wrem = [l[1:] for l in wdiff if l.startswith("-")]
wadd = [l[1:] for l in wdiff if l.startswith("+")]
exp_rem = [o for edits in WEAPON_EDITS.values() for (o, _) in edits]
exp_add = [n for edits in WEAPON_EDITS.values() for (_, n) in edits]
assert sorted(wrem) == sorted(exp_rem), ("weapon rem drift", wrem)
assert sorted(wadd) == sorted(exp_add), ("weapon add drift", wadd)
assert len(wrem) == 9 and len(wadd) == 9, (len(wrem), len(wadd))
# block count unchanged (no weapon added/removed) + only within our 5 weapons
assert end_lines(to_lf(patched[WPN_PATH])) == end_lines(to_lf(sources[WPN_PATH]))
print("Weapon.ini diff audit OK: exactly 9 field lines changed across the 5 "
      "Shock Trooper weapons; every other byte identical")

# ---- primary keep-verbatim spot-check + numeric proof
prim = weapon_block(to_lf(patched[WPN_PATH]), "ShockTrooperTeslaWeapon")
for keep in PRIMARY_KEEP:
    assert keep in prim, "primary lost a preserved line: " + keep
assert "PrimaryDamage           = 120.0 ;" in prim
assert "AttackRange             = 100.0 ;" in prim
assert "DelayBetweenShots       = 3200 ;" in prim
# chain / stun new values present, delays untouched
wl = to_lf(patched[WPN_PATH])
cz = weapon_block(wl, "ShockTrooperTeslaChainZap")
assert "PrimaryDamage           = 80.0 ;" in cz and "AttackRange             = 65.0 ;" in cz
assert "DelayBetweenShots       = 500" in cz, "chain-node cadence must be untouched"
hcz = weapon_block(wl, "HeroicShockTrooperTeslaChainZap")
assert "PrimaryDamage           = 96.0 ;" in hcz and "AttackRange             = 65.0 ;" in hcz
assert "DelayBetweenShots       = 500" in hcz
for sn in ("ShockTrooperTeslaStunPulse", "HeroicShockTrooperTeslaStunPulse"):
    sb = weapon_block(wl, sn)
    assert "AttackRange             = 15.0 ;" in sb
    assert "DelayBetweenShots       = 450" in sb, "stun-node cadence must be untouched"
    assert "DamageType              = SUBDUAL_UNRESISTABLE" in sb
print("weapon doctrine preserved OK (projectile/OCL/WeaponBonus/DamageType intact; "
      "node cadences 500/450 untouched; stun subdual damage untouched)")

# ---- RotrShockTrooper.ini diff audit: exactly the one trail line inserted
odiff = unified(to_lf(sources[OBJ_PATH]), to_lf(patched[OBJ_PATH]))
orem = [l[1:] for l in odiff if l.startswith("-")]
oadd = [l[1:] for l in odiff if l.startswith("+")]
assert orem == [] and len(oadd) == 1, (orem, oadd)
assert oadd[0].strip().startswith("ParticleSysBone = None %s" % TRAIL_PS)
# projectile + garrison-critical detonation wiring untouched
proj = re.search(r"(?ms)^Object\s+ShockTrooperTeslaBoltProjectile\s*\n.*?^End\s*$",
                 to_lf(patched[OBJ_PATH])).group(0)
for keep in ("Model = NONE", "ParticleSysBone = None TeslaTrooperFlare",
             "DumbProjectileBehavior", "KindOf = PROJECTILE"):
    assert keep in proj, "projectile lost: " + keep
assert end_lines(to_lf(patched[OBJ_PATH])) == end_lines(to_lf(sources[OBJ_PATH]))
print("RotrShockTrooper.ini diff audit OK: exactly 1 ParticleSysBone trail line "
      "added to the projectile; projectile flight/detonation wiring unchanged")

# ================================================== 6. package + install
entries = [BigEntry(p, patched[p].encode("latin-1")) for p in sorted(patched)]
out_local = os.path.join(HERE, OUT_NAME)
write_big_file(entries, out_local)
print("wrote %s (%d files, %d bytes)" % (out_local, len(entries),
                                         os.path.getsize(out_local)))

# ---- BIG round-trip byte identity
rt = read_big(out_local)
assert [e.path for e in rt] == [e.path for e in entries]
for x, y in zip(rt, entries):
    assert x.data == y.data, x.path
print("BIG round-trip byte-identical")

# ---- sort order + no-masking invariant against the real listings
shipped_lc = {p.lower() for p in patched}
for d in (SPE_DIR, SHW_DIR):
    listing = sorted({f for f in os.listdir(d) if f.lower().endswith(".big")}
                     | {OUT_NAME}, key=str.lower)
    i = listing.index(OUT_NAME)
    for later in listing[i + 1:]:
        assert later.lower() > OUT_NAME.lower()
        assert later.lower() in ABOVE_OK, \
            "an unexpected archive sorts above us: " + later
        lp = os.path.join(d, later)
        if os.path.exists(lp):
            for e in read_big(lp):
                assert e.path.lower() not in shipped_lc, \
                    "MASKED: %s claims our %s" % (later, e.path)
    cbp = [f for f in listing if f.lower().startswith("zzz_controlbarpro")]
    assert cbp and all(listing.index(c) > i for c in cbp), listing
    fx = [f for f in listing if f.lower() == "zzzz_fxenhance.big"]
    assert fx and listing.index(fx[0]) > i, "fx-enhance must sort after us"
    # everything else (all data layers) sorts BELOW us
    below = listing[:i]
    assert any(f.lower() == WPN_OWNER.lower() for f in below)
    assert any(f.lower() == OBJ_OWNER.lower() for f in below)
    print("sort order OK in %s: all data layers < %s < %s (nothing above masks "
          "our paths)" % (d, OUT_NAME, ", ".join(listing[i + 1:])))

# ---- install + re-read + effective-ownership audit in both dirs
blob_bytes = open(out_local, "rb").read()
md5s = {}
for d in (SPE_DIR, SHW_DIR):
    dst = os.path.join(d, OUT_NAME)
    with open(dst, "wb") as f:
        f.write(blob_bytes)
    md5s[d] = hashlib.md5(open(dst, "rb").read()).hexdigest()
    back = read_big(dst)
    assert [e.path for e in back] == [e.path for e in entries]
    for x, y in zip(back, entries):
        assert x.data == y.data, x.path
    arts = sorted((f for f in os.listdir(d) if f.lower().endswith(".big")),
                  key=str.lower, reverse=True)
    ca = {a: read_big(os.path.join(d, a)) for a in arts}

    def eff2(path):
        w = path.lower()
        for a in arts:
            for e in ca[a]:
                if e.path.lower() == w:
                    return e.data.decode("latin-1"), a
        return None, None
    for p in (WPN_PATH, OBJ_PATH):
        _, own = eff2(p)
        assert own == OUT_NAME, "post-install owner drift %s: %s" % (p, own)
    # installed-byte proof of both tasks
    wi, _ = eff2(WPN_PATH)
    pb = weapon_block(to_lf(wi), "ShockTrooperTeslaWeapon")
    assert "PrimaryDamage           = 120.0 ;" in pb
    assert "AttackRange             = 100.0 ;" in pb
    assert "DelayBetweenShots       = 3200 ;" in pb
    assert "ProjectileObject        = ShockTrooperTeslaBoltProjectile" in pb
    oi, _ = eff2(OBJ_PATH)
    assert ("ParticleSysBone = None %s" % TRAIL_PS) in to_lf(oi)
    # ParticleSystem.ini still owned by fx-enhance (we did NOT touch it) and the
    # trail system resolves there
    ps_i, ps_own = eff2(PS_PATH)
    assert ps_own.lower() == "zzzz_fxenhance.big", "ParticleSystem owner drift: " + str(ps_own)
    assert re.search(r"(?m)^ParticleSystem\s+%s\b" % TRAIL_PS, to_lf(ps_i))
    print("installed + audited OK in %s (owner=us for Weapon.ini + "
          "RotrShockTrooper.ini; primary 120/100/3200; trail=%s; ParticleSystem "
          "still fx-enhance's and resolves %s)" % (dst, TRAIL_PS, TRAIL_PS))

assert md5s[SPE_DIR] == md5s[SHW_DIR], "archives differ across mod dirs"
print("both installed archives md5-match: %s" % md5s[SPE_DIR])
print("DONE")
