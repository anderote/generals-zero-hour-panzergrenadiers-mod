# Battlemaster Coaxial Machine Gun — mini-mod for ShockWave (GeneralsX/macOS)

Every China Battlemaster tank variant gets a **coaxial machine gun** as a
SECONDARY weapon that is automatically selected against infantry (the cannon
is still used against everything else). The design is ported from the Zero
Hour Enhanced (ZHE) mod's `Type67CoaxialMachineGunWeapon`, with every
FX/sound/projectile reference replaced by a ShockWave-native equivalent.

Output archive: **`zzyzzz_CoaxMG.big`** — sorts after `zzyzz_PropTowers.big`
and the (in-progress) `zzyzy_NoAISuperweapons.big`, and before the
`zzz_ControlBarPro*.big` UI skins, so it is currently the **last gameplay
layer** in the stack.

## The weapon: `ShwBattleMasterCoaxMGWeapon`

Stats are ZHE's Type67 coax as-is, except where ShockWave forced a change:

| Field | Value | ZHE original / note |
|---|---|---|
| PrimaryDamage / radius | 20.0 / 1.0 | same |
| SecondaryDamage / radius | 10.0 / 2.0 | same |
| ScatterRadius | 30.0 | same (suppressive spray — many shots land near, not on, the target) |
| AttackRange | **165.0** | ZHE 200 — **capped at the Battlemaster cannon's buffed 165** |
| MinimumAttackRange | 20.0 | same (point-blank infantry is handled by the cannon/crushing) |
| DamageType | SMALL_ARMS | same — 100 % vs infantry (HumanArmor has no SMALL_ARMS entry), 25 % vs TankArmor |
| DelayBetweenShots / ClipSize / ClipReloadTime | 65 ms / 30 / 5000 ms | same |
| PreAttack | 2000 ms PER_CLIP | same |
| WeaponSpeed | 600 | same |
| ProjectileObject | GenericMachinegunProjectile | ZHE `GenericBullet` — not in ShockWave; this is the Gattling tank's tracer |
| ProjectileDetonationFX | WeaponFX_GenericBulletImpact | ZHE `FX_BulletHit` — not in ShockWave |
| ProjectileDetonationOCL | *(dropped)* | ZHE `OCL_GenericBulletWaterChecker_VeryWeakSuppressive` — no such OCL (or suppression system) in ShockWave |
| FireFX / heroic | WeaponFX_GenericMachineGunFire / …WithRedTracers | ZHE `FX_Type67Fire(WithRedTracers)` — not in ShockWave |
| FireSound | BattleMasterMachineGunFire | ZHE `PKMMachineGun` — not in ShockWave; this is the sound ShockWave's own (unused) `BattleMasterMachineGun` template uses |

Every substituted asset was verified to exist in the effective ShockWave
data (FXList.ini, SoundEffects.ini, WeaponTracerObjects.ini) at build time.

## Per-variant WeaponSet changes

Each listed WeaponSet gains
`Weapon = SECONDARY ShwBattleMasterCoaxMGWeapon` and
`PreferredAgainst = SECONDARY INFANTRY` (deterministic anti-infantry
selection; damage estimation would pick it anyway since the cannons'
ARMOR_PIERCING is 10 % vs HumanArmor):

| Object | WeaponSets patched |
|---|---|
| `ChinaTankBattleMaster_Var1` (vanilla China) | `None` + `PLAYER_UPGRADE` (autoloader). Var2–4 are `ObjectReskin`s of Var1 with **no WeaponSet redefinition** — verified, they inherit. |
| `Nuke_ChinaTankBattleMaster` (Tao) | `None` + `PLAYER_UPGRADE` |
| `Tank_ChinaTankBattleMaster` (Kwai) | `None` + `PLAYER_UPGRADE` |
| `Spec_ChinaTankBattleMaster` (Ravage) | its single `None` set — SECONDARY was **free** (ShockWave ships a commented-out `;Weapon = SECONDARY RavageMasterMachineGun` / `;PreferredAgainst = SECONDARY INFANTRY` right there; the Ramjet lives on TERTIARY with `AutoChooseSources = TERTIARY NONE`, untouched). |

`AutoChooseSources` for SECONDARY is left at its default (all sources), so
both the player-AI and computer players auto-fire it.

## Fire FX bones — no compromise needed

The Battlemaster models turn out to have a **dedicated coax bone**,
`WEAPONA01`, and the shipped INIs already bind it:

- `NVBtMstr` (vanilla), `NVT80` (Ravage): every relevant draw ConditionState
  already has `WeaponFireFXBone/WeaponLaunchBone = SECONDARY WeaponA` —
  dormant until now because no SECONDARY weapon existed.
- Kwai: the hull model `NVBtmstr_TG` has no coax bone, but the separate
  `ModuleTag_Gun01` draw module (model `NVBGun_TG`, which contains
  `WEAPONA01`) declares the SECONDARY bones — a cut coax MG model that this
  layer effectively re-activates.
- Nuke (`NVBtMstrNG`): dedicated `USING_WEAPON_B` condition states bind
  SECONDARY to `Muzzle`/`MUZZLEUP` (the cannon muzzle) — cosmetically the MG
  fires from the main barrel on this variant only. Left as shipped.

No draw modules were modified.

## Balance notes

- Range capped at 165 so the MG never out-ranges the cannon (which already
  carries the +10 % china-tank-buff; the ZHE MG's 200 would have out-ranged
  it).
- The MG stats are otherwise pure ZHE and do **not** inherit any layer buff
  (the gattling-buff +20 % range / ROF applied to gattling weapons only; the
  tank buff applied to the cannons only).
- 30-unit scatter + small splash means it shreds groups slowly and
  suppression-style rather than deleting single soldiers; burst DPS vs a
  direct hit is high (30 rounds × 20 in ~2 s) but the 2 s pre-aim and 5 s
  reload gate it.

## Files in the archive (full patched copies, original internal paths)

| File | Effective source layer | Change |
|---|---|---|
| `Data\INI\Weapon.ini` | `zzyz_GattlingBuff.big` | +1 weapon template (inserted after `BattleMasterMachineGun`) |
| `Data\INI\Object\China\Vanilla\Vehicles\BattleMaster.ini` | `zzyzz_PropTowers.big` | +4 lines (2 WeaponSets) |
| `Data\INI\Object\China\Nuke\Vehicles\BattleMaster.ini` | `zzyzz_PropTowers.big` | +4 lines |
| `Data\INI\Object\China\Tank\Vehicles\BattleMaster.ini` | `zzyzz_PropTowers.big` | +4 lines |
| `Data\INI\Object\China\SpecialWeapons\Vehicles\RavageTank.ini` | `zzyzz_PropTowers.big` | +2 lines |

`CommandSet.ini` is untouched — a passive auto-selected weapon needs no
button.

Prior layers are preserved and verified at build time (build fails if they
drift): prop-tower blocks + HelixContain bunker bays in all four object
INIs, china-tank-buff health (480/576) and cannon ranges (165), gattling
buff values in Weapon.ini (GattlingTankGun range 198 / damage 18).

## Rebuild

```
python3 build.py
```

Reads the effective source of each file from the highest-priority archive
containing it (zzyzy_NoAISuperweapons → zzyzz_PropTowers →
zzyz_GattlingBuff → zzyy_ChinaBunkers → zzy_MammothBunker →
zzx_ChinaTankBuff → zz_SPE_Shw_ini → !Shw_ini), applies exact-text patches
(fails loudly on upstream drift), verifies survivals / referenced assets /
block balance, writes `zzyzzz_CoaxMG.big` here, round-trips it and installs
into both mod dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild order note**: this archive embeds full copies of files from
earlier layers, and being later-alphabetical it masks them. If any of
china-tank-buff, mammoth-bunker, china-bunkers, gattling-buff or
battlemaster-proptower is rebuilt with different content, rebuild this one
afterwards. Full order: china-tank-buff → mammoth-bunker → china-bunkers →
gattling-buff → battlemaster-proptower → (no-ai-superweapons) →
**battlemaster-coax**. (no-ai-superweapons currently ships only
AIData/skirmish-script files, no overlap — but the build re-checks its
archive on every run in case that changes.)

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzyzzz_CoaxMG.big`
- `~/GeneralsX/mods/ShockWave/zzyzzz_CoaxMG.big`

## Uninstall

Delete `zzyzzz_CoaxMG.big` from both directories above. (WeaponSet-only
changes — save games are less likely to break than with module-list changes,
but crossing an install/uninstall boundary with saves is still not
recommended.)

## Known limitations / risks

- **MinimumAttackRange 20** (ZHE value kept): against infantry closer than
  20 the tank will nudge back to open range or simply crush them; the
  forced `PreferredAgainst = SECONDARY INFANTRY` means it won't switch back
  to the cannon for point-blank infantry.
- On the **Nuke** Battlemaster the MG muzzle flash/tracers come from the
  main cannon barrel (its shipped SECONDARY bones point at `Muzzle`) —
  cosmetic only.
- The MG benefits from generic weapon bonuses (veterancy, horde,
  propaganda ROF) like any weapon; it deliberately gets no layer buffs.
- ZHE's bullet-splash/suppression OCL was dropped (system absent in
  ShockWave): no water-splash decal when strafing water, slightly less
  feedback than in ZHE.
- Ravage keeps its Ramjet on TERTIARY exactly as before; the MG takes the
  designed-but-disabled SECONDARY slot.
