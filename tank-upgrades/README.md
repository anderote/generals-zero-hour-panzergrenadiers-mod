# Tank Upgrades — customizable Battlemaster field upgrades (ShockWave / GeneralsX)

`zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big` — the **top data layer** of the
Panzergrenadiers stack, for **Kwai (China Tank General)**. The rebalance layer cut
the Kwai Battlemaster (`Tank_ChinaTankBattleMaster`) to **stock** (MaxHealth 400);
this layer lets you make individual Battlemasters **elite by BUYING per-unit field
upgrades**, so power is *earned and customized per tank* — each Battlemaster can be
kitted differently.

**Pure data.** No engine, no new art (reused cameos), no touched map/tesla files.
Everything is **added**; every prior module and the rebalance stat cuts are preserved
byte-for-byte (build fails loudly on drift). Installed to both mod dirs, md5-identical.

## The three per-unit purchases (Battlemaster command bar, slots 6–8)

Same OBJECT-scoped **Upgrade + CommandButton + gated-module** idiom the Battlemaster
already uses for its Prop Tower / PDL / coax. Each is on **all four** Battlemaster
command sets (default / ERA / PDL / Tower) so it survives the tank's existing
`CommandSetUpgrade` swaps.

| # | Upgrade | Cost | Cameo | Mechanism | Magnitude |
|---|---|---|---|---|---|
| 6 | **Reactive Armor** | $800 | `SNTankTitaniumArmor` | `ArmorUpgrade` → reduced-damage `ArmorSet` | **−20%** vs AP / explosion / cannon |
| 7 | **Hull Reinforcement** | $600 | `SSCompositeArmor` | `MaxHealthUpgrade` (`ADD_CURRENT_HEALTH_TOO`) | **+160 HP** (+40% of stock 400) |
| 8 | **Projected Shield** | $1000 | `SSMammothShield` | `MaxHealthUpgrade` buffer + gated `AutoHealBehavior` | **+250 HP buffer, +15 HP/s** recharge |

All three **stack** with each other, with the tank's existing upgrades (KwaiDoctrine
armor tiers +66×4, Tungsten, Light Armor +115, Nuclear, AutoLoader, Prop Tower,
Kwai-PDL, coax), and with **veterancy** (they are additive `MaxHealthUpgrade` /
`ArmorUpgrade` modules; SagePatch veterancy HP multipliers apply on top). A fully
kitted Battlemaster: 400 → +160 hull → +250 shield ≈ **810 HP** with 15 HP/s regen
and 20% damage reduction, before doctrine/veterancy.

### Reactive Armor — the ArmorSet mechanism (documented engine constraint)

`ArmorUpgrade.cpp` only ever calls `setArmorSetFlag(ARMORSET_PLAYER_UPGRADE)` — there
is **no pure-data way to set a dedicated per-upgrade armorset bit** (VETERAN/ELITE/HERO
are rank-driven; `CRATE_UPGRADE_*` are salvage pickups; `PLAYER_UPGRADE` is the only
upgrade-settable flag). That single bit is already owned on this tank by the doctrine
`Upgrade_TankLightArmor`, whose `PLAYER_UPGRADE` armorset was **cosmetic only** (same
`TankArmor`, only a different `DamageFX`).

So this layer **repoints** that armorset to a real reduced-damage armor,
`Tank_BattleMasterReactiveArmor` (= `TankArmor`'s resistances plus `DEFAULT 80%`, i.e.
20% less from the otherwise-unlisted AP / explosion / cannon damage types that are the
meat of tank combat). Consequence (the spec's *"else document the mechanism"* fallback):
the reduced-damage armorset is granted by **either** the per-unit **Reactive Armor**
purchase **or** the doctrine **Light Armor** — both are "earned," and Reactive Armor
gives a tank the plating early / per-unit without the $2500 doctrine. The **only** edit
to an existing block is that one `Armor =` line (audited: −1 line); no module is removed.

### Projected Shield — scaled-down Emperor energy shield

The Emperor Defense Suite's energy shield is `MaxHealthUpgrade +2000` +
`AutoHealBehavior 40 HP/s`. This is the same idiom scaled to a Battlemaster:
`MaxHealthUpgrade +250` (absorption buffer, applied instantly, healed to new max) +
gated `AutoHealBehavior 15 HP/s` (`StartsActive = No`, `TriggeredBy` the shield upgrade).

## Overlord / Emperor — verified, not touched

The Emperor's kit is already rich (gattling, bunker, speaker, energy shield, ABM, innate
PDL). This layer does **not** ship or modify `Emperor.ini`; the build asserts it stays
owned by the rebalance layer and keeps its `MaxHealth 1100`, `ModuleTag_EDS_Shield01`,
Kwai-PDL mount and all buttons byte-for-byte. The optional "offer Reactive Armor/Hull on
the Overlord too" was **not taken** — it would require adding gating modules to the
already-crowded Emperor and coupling its own `PLAYER_UPGRADE` armorset; kept conservative
per spec.

## Autoloader (optional global research) — skipped

`Tank_Upgrade_ChinaTankAutoLoader` **already exists** on this tank (a `WeaponSetUpgrade`
to the upgraded gun). A second global RATE_OF_FIRE "autoloader" would be
redundant/confusing, so it was skipped to keep the menu focused (per spec).

## Load order

`zzz-` + **19 `Z`** + `1TankUpgrades` sorts (case-insensitively) **after** every data
layer — the highest is the rebalance's `…ZZ0Rebalance` (18 `Z` + `0`; our 19th char `Z`
`0x7A` > its `0` `0x30`) — and **before** `zzz_ControlBarPro*` / `zzzz_FXEnhance`
(`-` `0x2D` < `_`/`z`). It is now the **last data layer**. Verified against both real
mod-dir listings at build time.

## Files in the archive (6, full patched copies of the winning sources)

| File | Effective source (owner) | Change |
|---|---|---|
| `…\China\Tank\Vehicles\BattleMaster.ini` | `…ZZ0Rebalance.big` | +4 modules before `Geometry=BOX`; PLAYER_UPGRADE armorset repointed to reactive armor |
| `Data\INI\CommandSet.ini` | `…Z0EmperorTweaks.big` | +3 slot lines (6–8) on each of the 4 Battlemaster command sets |
| `Data\INI\CommandButton.ini` | `…Z0TeslaFinish.big` | +3 OBJECT_UPGRADE buttons appended |
| `Data\INI\Upgrade.ini` | `…Z0EmperorDefense.big` | +3 `Type=OBJECT` upgrades appended |
| `Data\INI\Armor.ini` | `…RotrInfantry.big` | +1 reduced-damage armor appended |
| `Data\Generals.str` | `…Z0EmperorTweaks.big` | +9 entries appended (append-only) |

New identifiers (all collision-checked): 3 upgrades, 3 buttons, 1 armor, 4 module tags,
9 string labels. Concurrent sessions' files (shellmap, `RotrShockTrooper.ini`) are
untouched and disjoint.

## Build-time verification (all enforced; build fails loudly otherwise)

Sort position + effective ownership in both dirs; no higher archive claims any shipped
path (or `Emperor.ini`); identifier collision-freedom; donor-idiom drift guards (cameos,
`TankArmor`, MaxHealth/Armor/AutoHeal modules, OBJECT_UPGRADE button, `MoneyWithdraw`);
exact line-multiset diff audits (BattleMaster −1/+22, CommandSet −0/+12, appends
balance-checked); prior-layer survival on shipped **and** installed bytes (rebalance
`MaxHealth 400`, all prior Battlemaster modules, Emperor `1100`+kit); closure
(button→upgrade→module, armorset→armor→def, buttons on all 4 sets, labels, cameos); BIG
round-trip byte-identity; hash-idempotent rebuild; both archives md5-match across dirs;
post-install effective audit. A separate `work/audit.py` re-checks **combined-stack
closure** over the whole effective space *including* this archive. **The game was
deliberately not launched.**

## Rebuild

```
python3 build.py       # then optionally: python3 work/audit.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (everything sorting below
this archive), patches, verifies, writes the archive here and installs to both mod dirs.
Depends on `../hotkey-addon/bigfile.py`. **This is the last data layer** — if any lower
layer is rebuilt, rebuild this afterwards (it embeds full copies of the six files).

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big`

## Known limitations / balance

- **Reactive Armor shares the `PLAYER_UPGRADE` armorset bit with the Light Armor
  doctrine** (engine constraint above): researching Light Armor also grants the 20%
  reduction fleet-wide, making the per-unit purchase redundant on that tank. Documented,
  on-theme (both earned).
- The three upgrades are **once-per-tank, non-refundable** (same as the existing
  Prop Tower / PDL). After purchase the button shows as produced.
- **AI never buys them** (player-facing; no AI scripting added).
- Save games crossing an install/uninstall boundary may not load (the Battlemaster's
  module list changed). Start fresh.
- **NOT verified in-game** (deliberately not launched); all verification is static
  against the installed bytes and the GeneralsX GeneralsMD engine source.

## Uninstall

Delete `zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big` from both mod dirs. Nothing else is
modified.
