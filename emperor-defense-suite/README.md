# Emperor Defense Suite (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX (macOS), for
**Kwai (China Tank General)**. Adds **four researchable, RequiredUpgrade-chained
defensive systems** to Kwai's **Emperor Overlord** tank
(`Tank_ChinaTankEmperor`), layered on top of the grenadier package's crewed
Emperor. Everything is **added**; every prior-layer module (grenadier crew,
Shtora APS, propaganda tower, gattling/kwai-PDL riders, doctrine armor tiers,
1320 HP) is preserved byte-for-byte.

Output archive: **`zzz-ZZZZZZZZZZZZ0EmperorDefense.big`** (6 files, INI + STR —
all art/FX/sounds are live references; no new assets). 12 Z's + `0` sorts
**after** the grenadier package's 11-Z layers
(`zzz-ZZZZZZZZZZZ0GrenadierResearch`, `zzz-ZZZZZZZZZZZ1DropLadder`) and — because
`-` (0x2D) < `_` (0x5F) < `z` (0x7A) — **before** `zzz_ControlBarPro*` and
`zzzz_FXEnhance`. Verified against the real listings of both mod dirs at build
time. This is now the **last INI layer of the stack**.

## The four systems (War Factory page 2, slots 8–11)

| # | System | Cost / time | Prereq | Cameo (reused) |
|---|---|---|---|---|
| 1 | **Hull Point-Defense Laser (PDL)** | $1500 / 40 s | — | `SNBlackSharkJammer` |
| 2 | **ABM Interceptor Array** | $2500 / 60 s | PDL | `SARocketAvenger` |
| 3 | **Projected Energy Shield** | $2500 / 50 s | — | `SSMammothShield` |
| 4 | **Fleet Shield Projection** | $2000 / 45 s | Shield | `SAPopupPatriot` |

Two chains via the **deployed engine's `RequiredUpgrade`** field (GeneralsMD
`Upgrade.cpp` `canAffordUpgrade` prereq gate — verified present): **PDL → ABM**
and **Shield → Fleet**. Chain buttons grey out until their prerequisite is owned
(engine QoL feature #6). All four are `Type = PLAYER` upgrades (researched once,
apply to every Emperor), mirroring the grenadier-research idiom.

## Engine idioms (evidence-backed, pure data)

### 1 & 2 — PDL / ABM: gated reactive point-defense laser burst
`FireWeaponWhenDamagedBehavior` is a full **`UpgradeMux`** (engine:
`FireWeaponWhenDamagedBehavior.h` inherits `UpgradeMux`), so
`StartsActive = No` + `TriggeredBy` is a clean **off→on research gate** — the
same module the Emperor's own **Shtora APS** already uses. Its reaction weapon
is fired via `forceFireWeapon( obj, obj->getPosition() )`
(`FireWeaponWhenDamagedBehavior.cpp` `onDamage`) — a **burst centred on the
Emperor** in every body state (`ReactionWeaponPristine/Damaged/ReallyDamaged`
all wired, unlike the donor Shtora which left Pristine unset).

The burst weapon (`Tank_EmperorPDLWeapon` / `Tank_EmperorABMWeapon`) is
`DamageType = LASER` with `RadiusDamageAffects = ENEMIES`:

- **`LASER` vs `TankArmor` = 0%** (`Armor.ini`, comment *"lasers are
  anti-personel and anti-projectile only (for point defense laser)"*) → the
  Emperor is **never hurt** by its own burst.
- **`LASER` vs `ProjectileArmor` = 100%** → incoming rockets/missiles in the
  radius are **destroyed**. (`BallisticMissileArmor` = 50%; ABM adds
  `AntiBallisticMissile = Yes` so SCUD-class ordnance is intercepted too.)
- **`RadiusDamageAffects = ENEMIES`** (`Weapon.cpp` `WEAPON_AFFECTS_ENEMIES`) →
  **no self- and no friendly-fire**; only hostile projectiles/units are hit.

Reuses the Avenger PDL fire FX (`WeaponFX_AvengerPointDefenseLaser`). PDL: 100
dmg, radius 30, 1 s cadence, triggers on hits ≥ 40. ABM: 250 dmg, radius 70,
0.8 s cadence, triggers on hits ≥ 25 (wider coverage, faster, anti-ballistic).

**This is a *reactive* point-defense** (fires when the Emperor is struck,
clearing follow-up ordnance in the area) — an honest approximation, chosen
deliberately. See *Why not proactive `PointDefenseLaserUpdate`* below.

### 3 — Projected Energy Shield: absorption buffer + recharge
The ShockWave **Mammoth "Energy Shield"** idiom
(`Upgrade_AmericaEnergyShieldGenerator` → `ArmorUpgrade` + `MaxHealthUpgrade`
`+200` + shield `DamageFX` + shield-visual OCL). This layer takes the
load-bearing part — the `MaxHealthUpgrade` — and scales it up:

- `MaxHealthUpgrade ModuleTag_EDS_Shield01`: **`AddMaxHealth = 2000`**,
  `ChangeType = ADD_CURRENT_HEALTH_TOO` (Emperor hull 1320 → **3320**+; a large
  damage-absorbing buffer that applies instantly on research).
- `AutoHealBehavior ModuleTag_EDS_Shield02` (gated): **40 HP/s recharge** (the
  Industrial Plant's Automated-Repair idiom) — the shield "recharges".

**Mechanism/magnitude:** implemented as a **+2000 HP absorption buffer with
40 HP/s regeneration**, not an armor multiplier (see *Why not an ArmorSet
shield* below). This matches how ShockWave's own Energy Shield actually works
(extra HP + cosmetic shield FX; the armor values are unchanged).

### 4 — Fleet Shield Projection: gated regen aura to the fleet
A **second `PropagandaTowerBehavior`** — the Overlord speaker-tower heal-aura
template the spec names as cleanest — gated by `UpgradeRequired` with the base
rate set to **0%** so it is fully off until researched:

- `Radius = 200`, `HealPercentEachSecond = 0%` (off),
  `UpgradedHealPercentEachSecond = 2%`,
  `UpgradeRequired = Tank_Upgrade_EmperorFleetShield`, `AffectsSelf = No`.
- Once researched, the Emperor projects a **2%/s regenerative shield field** to
  nearby friendlies (regen = sustained damage mitigation = "a weaker version of
  the shield").

**Mechanism/magnitude:** a **gated 2%/s regeneration aura, radius 200**. The
engine has **no pure-data module that grants armor/damage-reduction to nearby
units** (only heal — `PropagandaTowerBehavior` — and stealth — `GrantStealth` —
auras exist), so per the spec's "or the propaganda-heal aura is the cleanest
template" this is a regen field. Caveats: it affects **all** nearby friendlies
(the module has no `KindOf` filter, so VEHICLE-only isn't achievable in data);
and it partially **overlaps the Emperor's innate propaganda tower** (radius 150,
1–2%/s) — `attemptHealingFromSoleBenefactor` is non-stacking, so the net effect
is the higher rate within 150 and an **extended 150→200 heal envelope** for the
fleet. The propaganda `ENTHUSIASTIC` weapon-bonus it also applies is redundant
with the innate tower (same boolean condition) — no new leak.

## Why the mounting choices (engine constraints)

- **Why not proactive `PointDefenseLaserUpdate`** (the true Avenger scanning
  interceptor): the module has **no upgrade field and no disabled check**
  (`PointDefenseLaserUpdate.cpp` `update()` only tests `isEffectivelyDead`), so
  directly-mounted it is **always-on and cannot be research-gated in pure
  data**. Gating it would require a rider pod via `ObjectCreationUpgrade` → OCL
  → `HelixContain`, but the Emperor's **single portable-structure rider slot is
  already contested** by the gattling cannon **and** the existing kwai-PDL pod
  (`HelixContain.cpp` keeps exactly one `m_portableStructureID`; a second
  portable is rejected), and `getContain()` returns only the first bay so a
  second contain can't receive an OCL pod. Adding a fourth mutually-exclusive
  rider would **contest**, not add. Hence PDL/ABM use the gate-able **reactive**
  idiom instead. (The engine's `VeterancyBoost` opt-in on
  `PointDefenseLaserUpdate` is deployed but only rank-scales an existing PDL —
  it is not a research gate; and `WeaponBonusUpgrade` only sets the **shared**
  `PLAYER_UPGRADE` weapon-bonus condition, which the Emperor's Tungsten-Shells
  upgrade already owns, so it can't independently gate a PDL weapon.)
- **Why not an ArmorSet damage-reduction shield:** `ArmorUpgrade` only ever sets
  `ARMORSET_PLAYER_UPGRADE` (`ArmorUpgrade.cpp`; no flag selector), and the
  Emperor's `PLAYER_UPGRADE` ArmorSet is **already owned by
  `Upgrade_TankLightArmor`**. Repointing it to a reduced-damage shield armor
  would hand the shield to anyone who buys the cheap Light Armor upgrade —
  breaking the research gate. So the shield is a MaxHealthUpgrade buffer (the
  Mammoth Energy-Shield mechanism) instead.
- **Why the War Factory page 2, not the Propaganda Center / Industrial Plant:**
  both named structures are **full** in the current stack — the Propaganda
  Center is 14/14 across **58** research-state variants (kwai-doctrine), and the
  Industrial Plant has only **3** free garrison-exit slots for **4** buttons
  (its slots 1–5 = armor/autoloader/grenadier researches, 9–11 = drop powers,
  12–14 = Evacuate/Mines/Sell). The War Factory's **advanced-vehicle page 2**
  (`Tank_ChinaWarFactoryCommandSet_Down`) has **exactly 4 contiguous free
  slots** (8–11), a `ProductionUpdate` for upgrade buttons, and is thematically
  the vehicle-tech panel. Documented deviation.

## Files in the archive (6, full patched copies of the effective sources)

| File | Effective source (owner) | Change |
|---|---|---|
| `…\China\Tank\Vehicles\Emperor.ini` | `zzz-ZZZZZZZZZZZ0GrenadierResearch.big` | **+5 modules** before `Geometry = BOX` (2× FireWeaponWhenDamaged, MaxHealth+AutoHeal shield, PropagandaTower fleet aura) |
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZZZZZ1DropLadder.big` | +4 slot lines (WF page-2 8–11) |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZZZZZZZ1DropLadder.big` | +4 buttons appended |
| `Data\INI\Upgrade.ini` | `zzz-ZZZZZZZZZZZ0GrenadierResearch.big` | +4 PLAYER upgrades (2 chained via RequiredUpgrade) |
| `Data\INI\Weapon.ini` | `zzz-ZZZZZZZZPanzergrenadier.big` | +2 LASER burst weapons appended |
| `Data\Generals.str` | `zzz-ZZZZZZZZZZZ1DropLadder.big` | +12 entries appended (append-only) |

New identifiers (all word-boundary collision-checked against the whole
effective INI/STR space): 4 upgrades, 4 buttons, 2 weapons, 5 module tags, 12
string labels.

## Build-time verification (all enforced; build fails loudly otherwise)

- Sort position + effective ownership of all 6 sourced files (both dirs); no
  higher-sorting archive claims any shipped path.
- **Donor-idiom drift guards**: Avenger PDL weapon (LASER + AntiSmallMissile),
  `TankArmor` LASER = 0% / `ProjectileArmor` LASER = 100%, ShockWave energy-shield
  upgrade, propaganda + Avenger FX, all 4 cameos + 2 sounds resolve.
- **Exact line-multiset diff audits**: Emperor +5 modules / +42 lines (removes
  nothing); CommandSet +4 lines; Weapon/Upgrade/CommandButton/Generals.str
  append-only with block/entry-count balance.
- **Prior-layer survival** on shipped + installed bytes: Emperor 1320 HP,
  HelixContain 8-seat bay, propaganda tower, Shtora APS, gattling + kwai-PDL
  rider modules, doctrine armor tiers, grenadier `GP_Crew01/03` all survive; WF
  page-2 siblings (roster construct buttons, page-flip, Evacuate, Sell), the
  grenadier IP researches + drop buttons, and the Emperor's kwai-PDL button all
  intact; DropLadder still owns SpecialPower/OCL/IndustrialPlant.
- **Combined-stack closure** (separate `work/audit.py`): every WF-page-2 button
  → CommandButton; button → upgrade → cameo; RequiredUpgrade prereqs; Emperor
  module → upgrade/weapon; weapon → FX/armor; every string label resolves —
  recomputed over the whole effective space **including** this archive.
- BIG round-trip byte-identity; hash-idempotent rebuild; installed archives
  re-read and byte-compared; **both archives md5-match across the two mod dirs**;
  post-install effective audit in both dirs. **The game was deliberately not
  launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (everything sorting
below this archive), patches, verifies, writes
`zzz-ZZZZZZZZZZZZ0EmperorDefense.big` here and installs to both mod dirs. Depends
on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is the **last INI layer**. If any lower layer is
rebuilt (grenadier package, kwai-*, chaos-units, panzergrenadier, …), rebuild
this archive afterwards — it embeds full copies of Emperor.ini / CommandSet.ini /
CommandButton.ini / Upgrade.ini / Weapon.ini / Generals.str. Conversely, lower
layers' builds must not see this archive: delete it from both mod dirs first,
rebuild the lower chain in its documented order, then rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZZZZZZ0EmperorDefense.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZZZZZZ0EmperorDefense.big`

## Uninstall

Delete `zzz-ZZZZZZZZZZZZ0EmperorDefense.big` from both directories. No other
files are touched.

## Known limitations / balance

- **PDL/ABM are reactive**, not proactive-scanning (engine constraint above):
  they fire when the Emperor is struck, destroying *other* incoming ordnance in
  the burst radius — they don't pre-emptively shoot down the first missile.
  Proactive interception already exists on the Emperor as the separate per-unit
  **kwai-PDL pod** (contested rider slot); this suite adds a gate-able layer on
  top rather than clobbering it.
- **Fleet Shield is a regen aura**, not literal armor projection, and heals all
  nearby friendlies (not VEHICLE-only) — the engine has no pure-data
  grant-armor-to-nearby module; it partially overlaps the Emperor's innate
  propaganda heal (non-stacking) and effectively extends its radius to 200.
- The **Energy Shield is a +2000 HP buffer** (with 40 HP/s recharge), not a
  per-hit damage multiplier — the ShockWave Energy-Shield mechanism; an ArmorSet
  multiplier would leak through the shared `PLAYER_UPGRADE` ArmorSet owned by
  Light Armor.
- Researches are hosted on the **War Factory page 2** (both named tech buildings
  are full); flip to page 2 to buy them.
- The PDL burst is `RadiusDamageAffects = ENEMIES`, so contained crew, the
  Emperor itself, and friendly escorts are safe; enemy aircraft are immune to
  LASER (`AirplaneArmor` LASER 0%) — the burst is anti-projectile/anti-personnel
  by design.
- Save games crossing an install/uninstall boundary may not load (the Emperor's
  module list changed). Start fresh.
- AI never researches these (player-only upgrades; no AI/build-list changes).
- **NOT verified in-game** (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX GeneralsMD engine source.
