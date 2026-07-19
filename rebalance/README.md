# Rebalance — harder Kwai (ShockWave / GeneralsX)

`zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big` — the **balance** top layer of the
Panzergrenadiers stack. The faction had drifted heavily overpowered (skirmish
vs 7 Hard AI was trivial). This layer pulls the inflated **player base buffs
back toward genuine STOCK** and makes the **7 Hard AI relentless via its
economy**, so power is now *earned* through veterancy (combat) and upgrades
(economy) rather than baked into the base stats.

**Pure data.** No engine, no art, no new identifiers — only numeric stat lines
change. Every file is re-shipped from the **winning (highest-priority) copy**
beneath us, so all prior structural work (bays, coax, PDL, the Emperor / tesla
/ drop changes, garrison, doctrine, …) is preserved **byte-for-byte** except
the exact lines listed below. Anchor values are read **live from the base
archive** (`zz_SPE_Shw_ini.big` / `!Shw_ini.big`) so the stock anchor can't
drift. 76 files, ~4.0 MB, installed to both mod dirs (md5-identical).

Rebuild: `python3 build.py` — self-verifying (sort position, effective
ownership, prior-layer survival, BIG round-trip byte-identity, SPE/SW source
parity, both-dir install audit). Idempotent.

**Load order** — `zzz-` + **18 `Z`** + `0Rebalance` sorts (case-insensitively)
*after* every existing data layer (highest is `…ZZZ0EmperorTweaks`, 17 `Z`;
our 18th char `Z` `0x7A` > its `0` `0x30`) and *before*
`zzz_ControlBarPro*` / `zzzz_FXEnhance` (`-` `0x2D` < `_`/`z`). It is the **last
data layer**. Verified against both real dir listings at build time.

**Not touched** (owned by concurrent sessions): the shellmap map files,
`ShellEmperorElite.ini`, `EmperorFullDrop.ini`, `RotrShockTrooper.ini`,
`SagePatch.ini` (veterancy — deliberately left strong; the base cuts make it
*relatively* more impactful).

> **First-pass balance — expect playtest iteration.** See "Things to watch."

---

## A. Player base buffs → stock

### A1+A2 · 24 China tanks: HP → stock, weapon ranges → stock; **+5% speed kept**
Reverts china-tank-buff (+20 % HP / +10 % range), gattling-buff (+15 % HP /
+20 % range) and stat-tune (absolute HP / ranges) — **all the way to stock**.
Locomotor.ini is *not* touched, so china-tank-buff's **+5 % speeds stay**
(mobility feel retained).

| Tank (object) | HP was → now | Tank | HP was → now |
|---|---|---|---|
| Battlemaster (vanilla/Nuke/Tank) | 660 → **400** | Emperor (Kwai) | 1320 → **1100** |
| Battlemaster (Leang) | 576 → **480** | Overlord (all) | 1320 → **1100** |
| Gattling tank (van/Nuke/Spec) | 450 → **300** | Devastator | 960 → **800** |
| Gattling tank (Kwai) | 450 → **350** | Reaper | 840 → **700** |
| Gattling APC (Fai) | 304 → **220** | WarMaster | 696 → **580** |
| Dragon / ECM / Rad / Seismic / Tiger Shark | → **stock** | | |

Key weapon ranges (64 range lines total → stock):

| Weapon | was → now | | Weapon | was → now |
|---|---|---|---|---|
| BattleMasterTankGun (all) | 198 → **150** | | GattlingTankGun (ground, all) | 250 → **150** |
| GattlingTankGunAir (AA, all) | 462 → **350** | | Spec_GattlingTankGunAir | 420 → **350** |
| OverlordTankGun / Ravage / Dragon / Rad / ECM … | → **stock** | | (Devastator, Leang flame, chaingun…) | → **stock** |

**Artillery ranges** — Nuke Cannon family → stock (reverts stat-tune's 800):
`NukeCannonGun` / `Nuke_NukeCannonGun` 800 → **450**, `…NeutronWeapon` 729 →
**410**, `Nuke_…SSNRWeapon` 622 → **350**. *Kept as intentional nerfs:*
`HowitzerGun` 250 (Ironside), `InfernoCannonGun` 350.

### Kwai Tank buildings: 2× → **~1.25× stock HP** (13 structures)

| Building | was → now | Building | was → now |
|---|---|---|---|
| Command Center | 10000 → **6250** | Power Plant | 3000 → **1875** |
| Internet Center | 20000 → **5000** ⚠ | Barracks | 2000 → **1250** |
| War Factory | 4000 → **2500** | Airfield | 3000 → **1875** |
| Supply Center | 4000 → **2500** | Industrial Plant | 3000 → **1875** |
| Propaganda Center | 3600 → **2250** | Bunker | 3000 → **1875** |
| Nuclear Silo | 8000 → **5000** | Gattling Cannon | 2000 → **1250** |
| Sentry (Ramjet) Turret | 2400 → **1500** | | |

⚠ The Internet Center was 5× stock (20 000); pulled to 1.25× like the rest.
Auto-repair + Base Armaments still protect it — flag for playtest.

**Inferno Cannon HP** 300 → **210** (toward stock 195, tiny edge).

### A3 · China infantry cost/build: w-economy's 50 %/2× → **~15 % cheaper / 1.25× speed**
All 32 buildable China-infantry objects: `BuildCost = 0.85 × stock` (rounded to
$5), `BuildTime = 0.80 × stock` (1.25× build). Examples: Red Guard **255 / 8 s**
(was 150/5), Tank Hunter **255 / 4 s**, Minigunner **470 / 11.2 s**, Flame
Trooper **300 / 6.4 s**, Sharpshooter **1020 / 24 s**. Spam is no longer
trivial.

---

## B. China infantry: **combat HP −50 %** (useless on foot, valuable garrisoned/in-tank)

19 combat-infantry objects halved (they keep the SagePatch 140 % garrison range
bonus and are protected inside tank bays / bunkers — on foot they die fast):

| Unit | HP | Unit | HP |
|---|---|---|---|
| Red Guard (all 4 generals) | 120 → **60** | Minigunner (Fai ×2) | 120 → **60** |
| Red Guard squad member | 120 → **60** | Flame Trooper (Leang) | 100 → **50** |
| Tank Hunter (all 4) | 100 → **50** | **Panzergrenadier (Kwai)** | 144 → **72** |
| Tank Hunter squad member | 120 → **60** | **Shmel Trooper (Kwai)** | 100 → **50** |
| Siege Soldier (van/Fai/Nuke) | 100 → **50** | **Sharpshooter (Kwai)** | 120 → **60** |

**Exempt** (documented): Black Lotus (HERO ×5 — cost still cut, HP untouched);
hackers & other non-combat (Officer/Agent/Ambassador/Secret Police/Parade);
squad-nexus controllers (99999 invisible); the Mortar-Pit emplacement crew;
and the tesla **Shock Trooper / TeslaInfantry** — their file
(`RotrShockTrooper.ini`) is owned by a concurrent session and must not be
touched (so those two combat units keep full HP this pass).

## C. Veterancy — untouched

`SagePatch.ini` is owned by the main session and left as-is (Heroic 247 % HP,
lvl 8 400 % HP). Because the base is now modest, a *fresh* tank is stock and a
*Heroic* one is a monster — veterancy is the earned power source.

## D. AI economy — relentless 7 Hard AI

1. **Inexhaustible supplies** (global): every persistent supply source's
   `StartingBoxes` → **100000** (× $90/box ≈ bottomless): `SupplyWarehouse`,
   `SupplyDock`+`_Var1/2/3`, `SupplyPile`, `SupplyPileSmall`, `ToxinRepository`.
   The AI (bad at expanding) keeps its few gatherers earning forever and never
   stalls for cash. Helps the player too — accepted; the challenge is surviving.
2. **AI-only build/attack levers** (`AIData.ini`, `AIData` block — affects AI
   behaviour only): `Wealthy` 12000 → **6000**, `Poor` 3000 → **1500**,
   `StructuresWealthyRate` 2 → **3**, `TeamsWealthyRate` 2 → **3**,
   `TeamSeconds` 10 → **5**. With bottomless money the Hard AI stays *wealthy*
   and so builds structures + attack teams far more often and forms new attack
   teams twice as fast → constant pressure.
3. **Global supply value**: `ValuePerSupplyBox` 75 → **90** (+20 %) so both
   sides can afford constant production. *This one is global* (no data lever
   gives the AI a private cash multiplier in this stack); the differential AI
   advantage comes from lever #2 + inexhaustible piles.
   **AI superweapons stay OFF** (`NoAISuperweapons` untouched — not restored).

---

## Things to watch (first-pass; likely needs tuning)

- **Internet Center 20000 → 5000** is the biggest single cut (was 5× stock).
  If the hacker economy gets sniped too easily, raise it (~1.5–2×).
- **Base-defence HP** (Bunker / Gattling Cannon / Sentry) cut to 1.25× while
  the AI is now relentless — defences may feel thin; nudge up if bases fold.
- **Infantry at 50–72 HP** may be *too* fragile even garrisoned; if garrison
  play feels bad, soften to −40 %.
- **Nuke Cannon 800 → 450**: large siege-range cut; verify Kwai artillery still
  feels useful behind escorts.
- **ValuePerSupplyBox +20 %** is global — if the player out-economies the AI,
  drop it back to 75 and lean entirely on the AIData levers.
- Shmel / Shock Trooper HP not cut this pass (file locked by another session) —
  revisit once `RotrShockTrooper.ini` is free.

## Uninstall

Delete `zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big` from both
`~/GeneralsX/mods/ShockWaveSPE/` and `~/GeneralsX/mods/ShockWave/`. Nothing
else is modified.
