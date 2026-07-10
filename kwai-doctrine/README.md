# Kwai Doctrine (ShockWave / GeneralsX)

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. Adds **ten
researchable upgrades** to Kwai's (China Tank General) **Propaganda Center**
— two sequential four-tier armor ladders plus two weapon doctrines — and
makes his **Hacker** cheap and available without a Propaganda Center.

Output archive: **`zzz-KwaiDoctrine.big`** (installed to both mod dirs).
The `-` (0x2D) sorts before `_` (0x5F), so the name lands **after**
`zzyzzzzzz_EmperorBunker.big` (whose CommandSet.ini/Emperor.ini it layers
on) and **before** `zzz_ControlBarPro*.big` — verified case-insensitively
against the real directory listings at build time.

## The upgrades

All researched at the Propaganda Center, all player-wide (`Type = PLAYER`).

| Slot | Upgrade | Cost / time | Effect |
|---|---|---|---|
| 6 | **Composite Armor I–IV** | 1000/1500/2000/2500, 45 s | Each tier: **+10% of base max health** for **all** of Kwai's vehicles, aircraft and structures (list below). Sequential — tier N+1's button replaces tier N's when it completes. |
| 7 | **Infantry Conditioning I–IV** | 500/750/1000/1250, 30 s | Each tier: **+15% of base max health** for the infantry Kwai fields (Red Guard, Tank Hunter, Hacker, Black Lotus). Sequential. |
| 8 | **Tungsten Shells** | 2000, 60 s | **+25% damage, +15% range** for Battlemaster and Emperor main guns. |
| 9 | **Advanced Infantry Doctrine** | 1500, 45 s | **+25% damage, +20% range** for Red Guard rifles and Tank Hunter missiles. |

Health is applied `ADD_CURRENT_HEALTH_TOO` (units heal by the added amount,
same style as ShockWave's own Reactive Armor). Tiers stack additively on
the base value: all four Composite Armor tiers = +40% of base; all four
Conditioning tiers = +60% of base. Units built later still get every
researched tier (engine re-runs upgrade modules at spawn).

### Exact per-object numbers (+X health per tier, from the effective base)

Vehicles/aircraft (+10%/tier): Battlemaster 660 (+66), Gattling Tank 450
(+45), Emperor 1320 (+132), WarMaster 696 (+69.6), Dragon 336 (+33.6),
ECM 360 (+36), Reaper 840 (+84), Troop Crawler 240 (+24), Supply Truck 350
(+35), Dozer 300 (+30), Helix 280 (+28), MiG (Razor) 160 (+16), Inferno
Cannon 300 (+30), Nuke Cannon 240 (+24).

Structures (+10%/tier): Airfield 3000 (+300), Barracks 2000 (+200), Command
Center 10000 (+1000), Industrial Plant 3000 (+300), Internet Center 8000
(+800), Nuclear Silo 8000 (+800), Power Plant 3000 (+300), Propaganda
Center 3600 (+360), Supply Center 4000 (+400), War Factory 4000 (+400),
Bunker 3000 (+300), Gattling Cannon 2000 (+200), Sentry (Ramjet) Turret
2400 (+240).

Infantry (+15%/tier): Red Guard 120 (+18), Tank Hunter 100 (+15), Hacker
100 (+15), Black Lotus 200 (+30).

Not covered (documented choices): the ERA/prop-tower/gattling **rider
addon objects**, the vanilla-shared Speaker Tower / Hacker Van / Listening
Outpost stub targets (negligible combat value, keeps the shared-file
footprint down).

### Hacker change

Kwai's Hacker build stub (`Tank_ChinaInfantryHacker`): **BuildCost 625 →
300** and the **Propaganda Center prerequisite is removed** (Barracks
kept). Kwai-only — other generals' hackers are separate objects/stubs.

## Mechanisms (engine-source verified, GeneralsX GeneralsMD tree)

- **Health tiers** — one `MaxHealthUpgrade` module per tier per object
  (unique `ModuleTag_KD_Armor1..4`, `TriggeredBy` that tier's upgrade).
  Multiple modules per object are legal and fire independently
  (`Object::updateUpgradeModules`, Object.cpp:2510); each is a one-shot
  absolute delta (MaxHealthUpgrade.cpp:80).
- **Sequential unlock** — the engine has **no upgrade prerequisites**
  (UpgradeTemplate field table Upgrade.cpp:115-128; `canAffordUpgrade`
  checks money only, with a `@todo` at :456) and researched buttons stay
  visible-disabled, so ladders are compressed with **CommandSetUpgrade
  chaining**. `CommandSetUpgrade` writes a single per-object command-set
  override string, last-fired-module-wins (CommandSetUpgrade.cpp:67,
  Object.cpp:6235). The Propaganda Center already used one such module
  (per-building Mines → EMP-Mines button swap on slot 13), so the **full
  state space is enumerated**: mines{0,1} × CompArmor{0..4} ×
  InfCond{0..4} = **50 command sets** and **49 CommandSetUpgrade modules**
  (one per non-initial state, `TriggeredBy` = the exact upgrade set,
  `RequiresAllTriggers = Yes` for AND semantics; player + object upgrade
  masks are combined, Object.cpp:2525). Modules are emitted in ascending
  state-sum order, so whenever an upgrade completes, all newly-satisfied
  state modules fire in INI order and the maximal (= current) state fires
  last and wins. Buildings placed later re-derive the correct set at spawn.
- **Weapon doctrines** — `WeaponBonusUpgrade` modules set the per-object
  `PLAYER_UPGRADE` weapon-bonus condition bit; the *values* live per-weapon
  (`WeaponBonus = PLAYER_UPGRADE <FIELD> <pct>` lines inside the Weapon
  templates — ShockWave defines **no global** PLAYER_UPGRADE bonus in
  GameData.ini). Tungsten Shells activates ShockWave's own **dormant**
  `DAMAGE 125% ; UraniumShells` lines already present on
  `Tank_BattleMasterTankGun[Upgraded]`/`Tank_OverlordTankGun` (neither tank
  had any module setting the bit) and adds new `RANGE 115%` lines to those
  same Kwai-exclusive weapons. Advanced Infantry Doctrine adds the bit to
  the vanilla-shared `ChinaInfantryRedguard`/`ChinaInfantryTankHunter`
  (verified: **no other object using their weapons has any
  WeaponBonusUpgrade**, so the new per-weapon lines can only ever activate
  via this upgrade) with new `DAMAGE 125%` + `RANGE 120%` lines on
  `RedguardMachineGun`, `RedguardStunBulletMachineGun` (range only) and
  `ChinaInfantryTankHunterMissileLauncher`.
- **Scoping on shared objects** — the infantry and the two artillery
  pieces are vanilla-China objects (Kwai trains them through
  `BuildVariations` stubs). The added modules are **dormant for every
  other faction**: only Kwai's Propaganda Center offers the research
  buttons, and upgrade modules only fire for the owning player's completed
  upgrades. (Bonus: if Kwai captures a vanilla China barracks, those Red
  Guards benefit too — correct semantics.)

## Why damage/range are single upgrades, not 4-tier ladders (the honest ceiling)

`PLAYER_UPGRADE` is the **only** weapon-bonus condition bit settable by a
permanent upgrade-triggered module; `WeaponBonusUpgrade`,
`WeaponSetUpgrade` and `ArmorUpgrade` are all **parameterless single-flag
modules** (WeaponBonusUpgrade.cpp:91, WeaponSetUpgrade.cpp:51,
ArmorUpgrade.cpp:87). Every other bit is hardwired elsewhere (garrison,
horde/nationalism, veterancy, propaganda, battle plans, firing tracker,
salvage crates…; `WeaponBonusUpdate` can set any bit but only
*temporarily*). One bit = one on/off step per object, and the bit is
already **consumed** by ShockWave on: Gattling Tank + Reaper + gattling
towers (Chain Guns), WarMaster (Uranium Shells — Kwai researches that at
his Nuclear Silo, slot 11). Hence:

- Vehicle damage/range: ONE step, scoped to Battlemaster + Emperor (free
  bit + Kwai-exclusive weapons). Gattling/Reaper get theirs from Chain
  Guns; WarMaster from Uranium Shells; Dragon/Troop Crawler weapons are
  cross-faction-shared, so buffing them would leak.
- Infantry damage/range: ONE step (bit verified free on the infantry).
- **Engine feature requests that would unlock true tiers**: a
  `BonusConditionType`-style parameter on `WeaponBonusUpgrade` (the
  *temporary* `WeaponBonusUpdate` already parses exactly that field —
  `TheWeaponBonusNames`) plus a handful of generic spare condition bits
  (e.g. `PLAYER_UPGRADE_2..4`) in `WeaponBonusConditionType`; or
  per-upgrade weapon-bonus values. Also nice-to-have: a `RequiredUpgrade`
  field on `UpgradeTemplate` (the engine TODO at Upgrade.cpp:456) — that
  would eliminate the 50-set state machine entirely.

## Propaganda Center slot layout (all 50 state sets)

1 Nationalism · 2 Subliminal Messaging · 3 Neutron Bomb · 4 Chain Guns ·
5 Black Napalm (4-5 are kwai-artillery's relocations — preserved) ·
**6 Composite Armor (current tier)** · **7 Infantry Conditioning (current
tier)** · **8 Tungsten Shells** · **9 Advanced Infantry Doctrine** ·
13 Mines / EMP Mines (per-building state, preserved) · 14 Sell.

## Files in the archive (37, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\Upgrade.ini` | `zz_SPE_Shw_ini.big` | +10 Upgrade blocks appended |
| `Data\INI\CommandButton.ini` | `zzyzzzzz_KwaiArtillery.big` | +10 PLAYER_UPGRADE buttons appended |
| `Data\INI\CommandSet.ini` | `zzyzzzzzz_EmperorBunker.big` | 2 prop-center sets gain slots 6-9; +48 state sets appended |
| `Data\INI\Weapon.ini` | `zzyzzzz_StatTune.big` | +8 per-weapon `WeaponBonus = PLAYER_UPGRADE …` lines |
| `Data\Generals.str` | `zz_SPE_Shw_ini.big` | +30 string entries appended (ShockWave uses the STR file, not generals.csf — the engine prefers `Data\Generals.str` when present, GameText.cpp:318; GeneralsX falls back to the CSF for labels missing from it) |
| `…\Tank\Buildings\PropagandaCenter.ini` | `zzyzzzz_StatTune.big` | mines CommandSetUpgrade replaced by the 49-state family; +4 MaxHealthUpgrade |
| `…\Tank\Vehicles\*.ini` (10), `…\Tank\Aircraft\*.ini` (2) | stat-tune / emperor-bunker / china-tank-buff / china-bunkers / zz_SPE (per file) | +4 MaxHealthUpgrade each; Battlemaster & Emperor also +WeaponBonusUpgrade |
| `…\Tank\Buildings\*.ini` (9 more), `…\Tank\Defences\*.ini` (3) | `zzyzzzz_StatTune.big` | +4 MaxHealthUpgrade each |
| `…\Vanilla\Vehicles\InfernoCannon.ini`, `NukeCannon.ini` | stat-tune / zz_SPE | +4 MaxHealthUpgrade each |
| `…\Vanilla\Infantry\{Redguard,TankHunter,Hacker,BlackLotus}.ini` | `zz_SPE_Shw_ini.big` | +4 MaxHealthUpgrade each; Red Guard & Tank Hunter also +WeaponBonusUpgrade |
| `…\Tank\Infantry\Hacker.ini` | `zz_SPE_Shw_ini.big` | BuildCost 300, Propaganda Center prerequisite removed |

Button art reuses existing mapped images (`SNTankTitaniumArmor`,
`SNChemsuit`, `SNUrShells`, `Infa_SNPatriotism`) and existing research
sounds — no new assets.

## Build-time verification (all enforced, build fails loudly otherwise)

- Effective-file ownership asserted per file (drift = abort).
- Full diff audit: every hunk in every shipped file is an expected one
  (net multiset compare); append-only files asserted `startswith(source)`
  — the STR base bytes are byte-identical, only new entries follow.
- Cross-reference closure: every state set ↔ exactly one CSU module;
  every button ↔ upgrade ↔ string label exists.
- Sibling survival re-asserted on the shipped/installed bytes:
  emperor-bunker contain + Emperor command set (exits 2-9/gattling 10/
  evacuate 12) + MaxHealth 1320; kwai-artillery factory slots 11-12 and
  prop-center slots 4-5 (now in all 50 sets); mammoth-bunker slots 4-8;
  china-bunkers/prop-towers Battlemaster exits + ERA set; battlemaster
  stack (coax secondary, ERA HelixContain/OCL/set-swap, prop-tower mount,
  660 HP); stat-tune AttackRange values compared source-vs-shipped
  (value-agnostic, since stat-tune is actively re-tuned).
- Archive sort position checked against the real directory listings;
  installed archives re-read and re-verified byte-for-byte.

## Rebuild

```
python3 build.py
```

Reads the effective sources from `~/GeneralsX/mods/ShockWaveSPE/`
(excluding its own archive — idempotent), patches, verifies, writes
`zzz-KwaiDoctrine.big` here and installs to both mod dirs. Depends on
`../hotkey-addon/bigfile.py`. **Rebuild-order note**: this is the last
INI layer; if any lower layer (stat-tune, emperor-bunker, kwai-artillery,
…) is rebuilt, rebuild this archive afterwards — it embeds full copies of
their files and would otherwise mask their newer versions.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-KwaiDoctrine.big`
- `~/GeneralsX/mods/ShockWave/zzz-KwaiDoctrine.big`

## Uninstall

Delete `zzz-KwaiDoctrine.big` from both directories above. No other files
are touched.

## Known limitations / risks

- **Save games**: many objects gained modules — saves crossing an
  install/uninstall boundary may not load. Start fresh games.
- The `Generals.str` copy shipped into the plain-ShockWave dir is based on
  the SPE-effective one (same convention as every sibling INI); the SPE
  string additions are inert there.
- The two ladders' buttons stay on their state-machine sets; if a future
  sibling mod adds *another* CommandSetUpgrade to the Propaganda Center,
  the state space must be re-enumerated (build asserts would catch the
  ownership shift).
- Tier-IV buttons remain visible (dimmed full-color) after completion —
  standard already-researched presentation.
- Tungsten Shells intentionally excludes Gattling Tank/Reaper (Chain Guns
  owns their bonus bit) and WarMaster (Uranium Shells owns it) — those
  units have their own damage upgrades.
- AI never researches any of these (no AI script/build-list changes);
  player-facing only.
- Balance: fully laddered Kwai (+40% vehicle/building HP, +60% infantry
  HP, both weapon doctrines) is substantially stronger — intentional, and
  priced at 13 750 total.
