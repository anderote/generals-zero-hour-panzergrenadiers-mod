# Kwai Fortress Bunker

Layer archive: **`zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big`** (21 Z's + `0Fortress` —
last data layer of the stack: above `zzz-ZZZZZZZZZZZZZZZZZZZZ0Flagship.big` [20 Z's],
below `zzz_ControlBarPro*` / `zzzz_FXEnhance`; verified against the real directory
listings of both mod dirs at build time).

Gives Kwai (China Tank General) a new dozer-buildable defensive structure on the
dozer's **page 2, slot 8** (the slot freed when the hotfix layer removed the Hacker
Bunker button): the **Fortress Bunker** (`Tank_ChinaFortressBunker`, **$800** / 8 s,
War Factory prerequisite) — a full clone of the effective `Tank_ChinaBunker`
(Rebalance copy: 1875 HP `HiveStructureBody`, `FireBaseArmor`, 1-vehicle fire-out
`GarrisonContain`, mines family, all four doctrine Composite-Armor tiers,
vehicle-repair aura) with its **own command bar** carrying three **per-bunker**
purchases (`Type = OBJECT` upgrades, slots 2–4; Evacuate/Stop/Mines/Sell kept):

| Purchase | Cost | Mechanism |
|---|---|---|
| **Composite Armor** | $500 | `MaxHealthUpgrade` **+937.5 HP** (+50% of base 1875, `ADD_CURRENT_HEALTH_TOO`) |
| **Point-Defense Laser** | $800 | `FireWeaponWhenDamagedBehavior` reactive anti-missile **LASER burst** (reuses `Tank_EmperorPDLWeapon`: 100 dmg, radius 30, `RadiusDamageAffects=ENEMIES`; triggers on hits ≥ 30 dmg) |
| **Propaganda Tower** | $500 | gated `AutoHealBehavior` **heal aura**: 20 HP/s per target, radius 150, allied `INFANTRY VEHICLE STRUCTURE` **including the bunker itself** |

Mines research swaps to `Tank_ChinaFortressBunkerCommandSetUpgrade` (EMP Mines at
13), same as the base Tank Bunker. Cameos/sounds reuse existing assets only
(`SNTankBunker`, `SSCompositeArmor`, `SNBlackSharkJammer`, `SSOLSpeaker`,
`SSSpySat`).

## Satellite Uplink (STAGE-ONLY until fork engine ≥ batch 3)

**`Tank_Upgrade_SatelliteUplink`** — a PLAYER research at Kwai's **Propaganda
Center** (**$2500 / 45 s**, `SSSpySat` cameo) that **permanently reveals the whole
map**, via the fork's new `Behavior = MapRevealUpgrade` UpgradeModule
(`ModuleTag_KF_Reveal01`, standard `TriggeredBy` parsing, no other fields) added
to `Tank_ChinaPropagandaCenter`.

> **WARNING**: `MapRevealUpgrade` does **not** exist in the currently deployed
> engine binary — an older binary **fails INI parse at startup** on this archive.
> Do **not** install this build until the batch-3 engine is deployed; the
> currently installed 5-file Fortress archive (no uplink) must stay in place
> until then. `python3 build.py --stage` only rebuilds the archive here.

**Command-set surgery**: the Kwai Propaganda Center has **no free UI slot** — all
**50** command-set variants (base + Upgrade + 48 `CS_M{0,1}V{0-4}I{0-4}`
kwai-doctrine ladder states) are 14/14 full, and every occupant is live for Kwai
(slots 1–5 vanilla researches — Nationalism is engine-hardcoded horde logic,
Neutron Bomb feeds the Tank command center; 6–11 doctrine/basetech; 12 Evacuate
serves the kwai-garrisons 10-man garrison; 14 Sell). The **slot-13 per-building
mines purchase** (`Command_UpgradeChinaMines`/`Command_UpgradeEMPMines`, the
least-value occupant — every other Kwai structure keeps its own) is **replaced by
the uplink button across all 50 variants**, with post-edit layout asserts that
only slot 13 changed in each set. The prop center's mines modules
(`GenerateMinefieldBehavior` + the M0↔M1 set dimension) stay defined but
dormant/unreachable; mines buttons everywhere else (incl. the Fortress Bunker's
own sets) are untouched.

## Engine-forced deviations (deployed branch `feature/veterancy-8-levels`, tip `0b3daa0c9`)

- **PDL is reactive, not a `PointDefenseLaserUpdate`**: the deployed module's
  field table is only `WeaponTemplate / *TargetTypes / ScanRate / ScanRange /
  PredictTargetVelocityFactor / VeterancyBoost / InterceptBallistics` — it has
  **no `StartsActive`/`TriggeredBy`**, so a purchasable (gated) true PDL would
  fail INI parse at startup. The gate-able reactive idiom is the same one the
  Emperor Defense Suite ships for its Hull PDL. (A rider-pod PDL needs a
  Helix/Overlord contain rider slot; the bunker keeps its `GarrisonContain`.)
- **Propaganda Tower is an `AutoHealBehavior` aura, not a
  `PropagandaTowerBehavior` / OCL rider**: `PropagandaTowerBehavior` cannot be
  OBJECT-gated (`effectLogic()` keys the heal rate off the **player** upgrade
  mask only; an OBJECT `UpgradeRequired` would heal at the base rate forever),
  and the battlemaster-proptower OCL-rider pattern requires a contain rider
  slot the bunker doesn't have. The gated aura heals structures natively — the
  fork's "prop towers heal structures" change is not required by this layer.
- Both replacement mechanisms are already deployed OBJECT-gated in this stack
  (`Tank_Upgrade_BattleMasterHull`/`Shield` → `MaxHealthUpgrade` +
  `AutoHealBehavior` on `Tank_ChinaTankBattleMaster`).

## Files in the archive (6, full patched copies of the effective sources)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `…\Tank\Defences\FortressBunker.ini` | **new file** (clone of `Bunker.ini`, owner Rebalance) | 5 lines swapped + 3 purchase modules inserted |
| `…\Tank\Buildings\PropagandaCenter.ini` | `zzz-ZZZZZZZZZZZZZZZZZZ0Rebalance.big` | +`MapRevealUpgrade` module (3 lines) |
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big` | dozer page-2 slot 8 added; +2 fortress sets appended; prop-center slot 13 → uplink ×50 |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big` | +5 buttons appended (1 construct + 3 purchases + 1 research) |
| `Data\INI\Upgrade.ini` | `zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big` | +3 OBJECT + 1 PLAYER upgrades appended |
| `Data\Generals.str` | `zzz-ZZZZZZZZZZZZZZZZZZZ1TankUpgrades.big` | +15 string entries appended (append-only) |

`Weapon.ini` (owner Flagship) and `Emperor.ini` (owner Flagship) are **read but
not shipped** — the PDL burst reuses `Tank_EmperorPDLWeapon`, drift-guarded.

New identifiers (all definition-collision-checked word-boundary against the whole
effective INI/STR space): `Tank_ChinaFortressBunker`,
`Tank_ChinaFortressBunkerCommandSet[Upgrade]`,
`Tank_Command_ConstructChinaFortressBunker`,
`Tank_Upgrade_Fortress{CompositeArmor,PDL,PropTower}`,
`Tank_Command_UpgradeFortress{CompositeArmor,PDL,PropTower}`,
`Tank_Upgrade_SatelliteUplink`, `Tank_Command_UpgradeSatelliteUplink`,
`ModuleTag_KF_{Armor01,PDL01,Prop01,Reveal01}`, plus 15 `.str` labels.

## Build / install

```
python3 build.py --stage   # write layer archive here only (no install)
python3 build.py           # + install to both mod dirs (game must not be mid-session)
```

Verifies (fails loudly on any drift): sort position in both dirs; effective
ownership (Bunker.ini + PropagandaCenter.ini → Rebalance;
CommandSet/CommandButton/Upgrade/Generals.str → TankUpgrades; Weapon/Emperor →
Flagship); both mod dirs byte-agree; new INI path unclaimed by every other
archive in both dirs (self excluded — idempotent rebuild over an installed
copy); nothing above claims shipped paths;
identifier/label collision; donor-idiom drift guards (EDS PDL module, burst-weapon
LASER/ENEMIES idiom, armour table, cameo MappedImages, AudioEvents, reused
buttons/upgrades, BattleMasterHull OBJECT precedent); exact line-multiset diff
audits on the clone and CommandSet.ini; append-only asserts on the other three;
post-edit command-set layouts (dozer page 2, both fortress sets, all 50
prop-center sets with only slot 13 changed) + sibling survival; full closure
(construct→object→sets→buttons→upgrades→modules→weapon→labels, uplink
button→PLAYER upgrade→MapRevealUpgrade); BIG round-trip;
hash-idempotent rebuild; post-install effective-ownership audit + md5 match
(install mode only).

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big`

## Rebuild rule

Rebuild this layer whenever **any** lower layer that feeds its sources is rebuilt
(Rebalance for `Bunker.ini`; TankUpgrades for CommandSet/CommandButton/Upgrade/str;
Flagship for the reused `Tank_EmperorPDLWeapon`) — this layer embeds full copies
of the four shared files. Conversely, lower layers' builds must not see this
archive: delete it from both mod dirs first, rebuild the lower chain, then rerun
this build.

## Uninstall

Delete `zzz-ZZZZZZZZZZZZZZZZZZZZZ0Fortress.big` from both directories above. No
other files are touched. (Already-built Fortress Bunkers exist only in saves that
reference the object — saves crossing the install/uninstall boundary may not load.)

## Known limitations / balance

- The PDL is **reactive**: it pulses only when the bunker takes a hit ≥ 30 damage
  (1 s cooldown via the weapon's `DelayBetweenShots`) — saturation volleys still
  land; it does not pre-emptively sweep like an Avenger.
- The Propaganda Tower purchase has no tower model or pulse FX (pure aura); the
  ENTHUSIASTIC weapon-bonus of real prop towers is not granted.
- Composite Armor stacks with the four doctrine armor tiers (max 1875 + 1200 +
  937.5 ≈ 4012 HP).
- AI never builds or upgrades the Fortress Bunker (no AI build-list changes);
  player-facing only.
- **The staged 6-file archive (with Satellite Uplink) requires the fork engine
  ≥ batch 3** (`MapRevealUpgrade` INI key). The archive currently installed in
  the mod dirs is the earlier 5-file build without the uplink — do not
  overwrite it until the batch-3 binary is deployed.
- The Propaganda Center can no longer buy perimeter mines (slot-13 sacrifice);
  already-purchased mines on old saves keep working, and every other structure
  keeps its mines button.
- NOT verified in-game by this build (deliberately not launched); all
  verification is static against the installed bytes and the deployed engine
  source (`feature/veterancy-8-levels` worktree) — except `MapRevealUpgrade`,
  which is taken on faith from the batch-3 fork spec.
