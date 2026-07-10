# Kwai Base Tech (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Adds **two
researchable upgrades** to Kwai's (China Tank General) **Propaganda Center**:

| Slot | Upgrade | Cost / time | Effect |
|---|---|---|---|
| 10 | **Automated Repair Systems** | 1500 / 45 s | All of Kwai's structures slowly self-repair: **1% of base max health per second** each. |
| 11 | **Base Armaments** | 2000 / 60 s | Kwai's seven **main buildings** gain a defensive anti-infantry **machine gun** (range 175, auto-acquires nearby ground enemies). |

Both are plain one-shot `Type = PLAYER` upgrades — **no new
CommandSetUpgrade anywhere**, so kwai-doctrine's 50-set Propaganda-Center
state machine is untouched; the engine natively greys the buttons out once
researched. The two buttons are added at the free slots 10–11 of **all 50**
Kwai prop-center command sets (2 base + 48 doctrine state sets).

Output archive: **`zzz-ZZKwaiBaseTech.big`** (installed to both mod dirs).
Case-insensitively `zzz-zk…` < `zzz-zz…` puts it **after**
`zzz-ZKwaiBunkers.big` (whose CommandSet.ini / CommandButton.ini /
Generals.str / HackerBunker.ini it layers on) and `-` (0x2D) < `_` (0x5F)
puts it **before** `zzz_ControlBarPro*.big` — verified against the real
directory listings at build time.

## Automated Repair Systems

One `AutoHealBehavior` module per structure (`ModuleTag_KBT_Heal01`,
`StartsActive = No`, `TriggeredBy = Tank_Upgrade_KwaiAutoRepair`, no
`Radius` = self-only) — the exact GLA **Junk Repair** idiom
(`Scorpion.ini ModuleTag_05`; engine `AutoHealBehavior.cpp` radius==0
self-heal path verified in the GeneralsX GeneralsMD tree).

**Rate choice (documented):** `HealingAmount` = 1% of that building's
effective base `MaxHealth`, `HealingDelay = 1000 ms`, computed per building
from the effective INI at build time. A flat 20–30 HP/s would be
negligible on the 20 000 HP Internet Center yet meaningful on a 2 000 HP
Barracks; 1%/s gives *every* structure the same ~100 s empty-to-full
repair (up to ~140 s with all four doctrine Composite Armor tiers, whose
`MaxHealthUpgrade` additions deliberately don't raise the rate). 2%/s
(400/s on the IC) was judged too strong.

Covered (14 files — the 13 doctrine-covered Kwai structures + the
kwai-bunkers Hacker Bunker):

| Structure | Base HP | Heal/s | | Structure | Base HP | Heal/s |
|---|---|---|---|---|---|---|
| Command Center | 10000 | 100 | | Airfield | 3000 | 30 |
| Internet Center | 20000 | 200 | | Industrial Plant | 3000 | 30 |
| War Factory | 4000 | 40 | | Nuclear Silo | 8000 | 80 |
| Supply Center | 4000 | 40 | | Tank Bunker | 3000 | 30 |
| Propaganda Center | 3600 | 36 | | Gattling Cannon | 2000 | 20 |
| Power Plant | 3000 | 30 | | Sentry (Ramjet) Turret | 2400 | 24 |
| Barracks | 2000 | 20 | | Hacker Bunker | 3000 | 30 |

Not covered: the vanilla-shared Speaker Tower (doctrine's shared-file
rule — a module there would leak to other China generals' files).

## Base Armaments

Armed set (7): **Command Center, Barracks, War Factory, Supply Center,
Internet Center, Propaganda Center, Power Plant**. Skipped (documented):
Airfield (JetAI parking/runway interactions untested), Nuclear Silo
(superweapon plumbing), Industrial Plant (outside the main-building set),
defenses (already armed or spawn-armed).

Mechanism per building (engine-source verified, mirrored from shipping
precedents):

- **Two `WeaponSet` blocks**: `Conditions = None` **empty** (unarmed by
  default — empty-set precedent: GLA Salvage `MI8Gunship`, `ChinaMisc`
  "no weapons") and `Conditions = PLAYER_UPGRADE` carrying the gun.
  SparseMatchFinder scoring (SparseMatchFinder.h `findBestInfoSlow`)
  picks the None set pre-research (fewest extraneous bits) and the
  PLAYER_UPGRADE set after.
- **`WeaponSetUpgrade ModuleTag_KBT_Arm01`** `TriggeredBy =
  Tank_Upgrade_KwaiBaseArmaments` — sets the per-object
  `WEAPONSET_PLAYER_UPGRADE` flag, the same mechanism as the Gattling
  Cannon's Chain-Guns set swap. **Verified free**: none of the seven
  buildings had any `WeaponSet` / `WeaponSetUpgrade` / active
  `AIUpdateInterface` before this mod (asserted at build time).
- **`AIUpdateInterface ModuleTag_KBT_AI01`** with a logical `Turret`
  (`ControlledWeaponSlots = PRIMARY`, 360° idle scan, 180°/s) +
  `AutoAcquireEnemiesWhenIdle = Yes` + `MoodAttackCheckRate = 250` — the
  minimal acquisition module set of `Tank_ChinaGattlingCannon`
  (ModuleTag_06). IMMOBILE structures need the turret to aim; TurretAI
  is pure logic, so no turret bone is required. ProductionUpdate +
  AIUpdateInterface coexist (`AmericaStrategyCenter`,
  `TechWarFortress_Real` precedents).
- **KindOf deliberately NOT given `CAN_ATTACK`**: `Object.cpp
  isAbleToAttack` returns true for "has AI + any weapon in the current
  set", so the buildings only register as armed once the research flips
  the set; `CAN_ATTACK` would make them claim attack ability while
  weaponless. (The Internet Center already carries `CAN_ATTACK` from
  ShockWave — left as-is.)
- **Weapon**: new template **`Tank_KwaiBaseArmamentsGun`** appended to
  `Weapon.ini` — a toned-down clone of the Gattling Cannon's
  `Tank_GattlingBuildingGun`: **12** damage (vs 20) every 250 ms,
  GATTLING type, **range 175** (vs 225 — stays inside every armed
  building's 200 vision/acquisition radius), ground-only (no anti-air),
  continuous-fire rate bonuses kept (FiringTracker sets those bits per
  object automatically), the Chain-Guns `PLAYER_UPGRADE DAMAGE 125%`
  bonus line dropped. All FX/sounds/projectiles reuse existing assets.
  Reusing the base-defense gun verbatim would have put a full Gattling
  Cannon on every structure and out-ranged the buildings' vision.

**Cosmetics (known):** no turret model — the gun fires its tracers from
the structure's origin/center bone with the vanilla gattling FX and
barrel-spin sound. Purely visual oddity.

Buttons reuse mapped cameos `SNRepairPad` (repair) and `SNTankGatTower`
(armaments), research sounds `ReaperVoiceUpgrade` /
`GattlingTankVoiceUpgrade` — no new assets. 6 string entries appended to
`Data\Generals.str` (append-only, base bytes byte-identical).

## Files in the archive (19, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZKwaiBunkers.big` | slots 10–11 inserted into all 50 Kwai prop-center sets (100 lines, insertions only) |
| `Data\INI\CommandButton.ini` | `zzz-ZKwaiBunkers.big` | +2 PLAYER_UPGRADE buttons appended |
| `Data\Generals.str` | `zzz-ZKwaiBunkers.big` | +6 string entries appended |
| `Data\INI\Upgrade.ini` | `zzz-KwaiDoctrine.big` | +2 Upgrade blocks appended |
| `Data\INI\Weapon.ini` | `zzz-KwaiDoctrine.big` | +1 Weapon template appended |
| `…\Tank\Buildings\*.ini` (10) | `zzz-KwaiDoctrine.big` | +AutoHealBehavior each; the armed ones also +2 WeaponSets +WeaponSetUpgrade +AIUpdateInterface |
| `…\Tank\Defences\{Bunker,GattlingCannon,Ramjet Turret}.ini` | `zzz-KwaiDoctrine.big` | +AutoHealBehavior each |
| `…\Tank\Defences\HackerBunker.ini` | `zzz-ZKwaiBunkers.big` | +AutoHealBehavior |

## Build-time verification (all enforced, build fails loudly otherwise)

- Effective-file ownership asserted per file (drift = abort); new
  identifiers collision-checked across all sources; prop-center slots
  10–12 asserted free in *every* prop-center set (all generals);
  WEAPONSET_PLAYER_UPGRADE asserted free on all 7 armed buildings.
- Diff audits: CommandSet.ini = exactly 100 inserted slot lines, zero
  removed; every object file = pure insertion of exactly the expected
  blocks; CommandButton.ini / Generals.str / Upgrade.ini / Weapon.ini
  asserted `startswith(source)` (append-only, base bytes identical).
- Cross-reference closure: buttons ↔ upgrades ↔ strings ↔ weapon;
  cameos/sounds/FX/projectile asserted pre-existing in the sources.
- **Sibling survival re-asserted on the shipped and installed bytes**:
  doctrine's 48 state sets + slots 4–9 in all 50 sets + its 10 buttons /
  30 strings + all four `MaxHealthUpgrade` armor tiers (with triggers) in
  every shipped object file; kwai-bunkers' dozer page flip (both pages),
  Hacker Bunker set/button/strings and `InternetHackContain`; stat-tune's
  Internet Center **20000 HP / 30 hacker slots**; kwai-artillery factory
  slots 11–12; emperor-bunker's Emperor set; mammoth-bunker slots 4–8;
  vanilla (non-Kwai) prop-center sets and China dozer pages untouched.
- Archive sort position checked against the real directory listings;
  installed archives re-read and re-verified byte-for-byte; rebuild is
  idempotent (self-archive excluded from sourcing, hash-stable).

## Rebuild

```
python3 build.py
```

Reads the effective sources from `~/GeneralsX/mods/ShockWaveSPE/`
(excluding its own archive), patches, verifies, writes
`zzz-ZZKwaiBaseTech.big` here and installs to both mod dirs. Depends on
`../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer** (directly
before the `zzz_ControlBarPro*` skins). If **any** lower layer is rebuilt
(kwai-bunkers, kwai-doctrine, stat-tune, emperor-bunker, kwai-artillery,
…), rebuild this archive afterwards — it embeds full copies of their
files and would otherwise mask their newer versions. Conversely the
lower layers' own builds must not see this archive:

1. rebuilding **kwai-bunkers** → delete `zzz-ZZKwaiBaseTech.big` from
   both mod dirs first, rebuild it, then rerun this build;
2. rebuilding **kwai-doctrine** → delete **both** `zzz-ZZKwaiBaseTech.big`
   and `zzz-ZKwaiBunkers.big` first, rebuild doctrine, rebuild
   kwai-bunkers, then rerun this build.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZKwaiBaseTech.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZKwaiBaseTech.big`

## Uninstall

Delete `zzz-ZZKwaiBaseTech.big` from both directories above. No other
files are touched.

## Known limitations / risks

- **Save games**: 14 structures gained modules — saves crossing an
  install/uninstall boundary may not load. Start fresh games.
- The building guns fire from the structure origin with no turret art
  (cosmetic); they keep firing during low power (the buildings are not
  `POWERED`) and their acquisition radius is the building's vision range
  (200–300), slightly above the 175 weapon range.
- Structures firing while *under construction* / *being sold* is
  untested; the engine's UNDER_CONSTRUCTION status normally suppresses
  combat modules.
- If a building is captured, upgrade modules re-evaluate for the new
  owner: an enemy without the research gets no gun/repair — correct
  semantics, same as captured Gattling Cannons and Chain Guns.
- The repair rate is 1% of *base* max health; with all four doctrine
  armor tiers the effective pool is +40% so a full repair takes ~140 s.
- Auto-repair on the Tank Bunker sits alongside its existing
  vehicle-repair aura (`ModuleTag_Repair01`) — two independent
  AutoHealBehavior modules, the JunkBunker shipping pattern.
- AI never researches either upgrade (no AI script changes);
  player-facing only.
- Balance: both upgrades together cost 3500 and make a fully teched Kwai
  base very hard to raid with infantry — intentional; the MG plinks
  vehicles (GATTLING damage) and cannot touch aircraft.
- NOT verified in-game (the game was deliberately not launched); all
  verification is static against the engine source and installed bytes.
