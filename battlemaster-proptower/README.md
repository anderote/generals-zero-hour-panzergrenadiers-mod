# Battlemaster Propaganda Towers — mini-mod for ShockWave (GeneralsX/macOS)

Every China Battlemaster tank variant can buy a per-tank **Propaganda Tower**
add-on ($500, 10 s — the Overlord's own speaker tower: heals friendly units
and boosts their fire rate in a 150 radius, upgradable by Subliminal
Messaging where available). The tower rides in a dedicated HelixContain
rider slot, so the 4-man bunker bay from `zzyy_ChinaBunkers` is untouched.

Output archive: **`zzyzz_PropTowers.big`** — the name is deliberate: inside a
`-mod` directory, later-alphabetical archives take priority, so it must sort
after `zzyz_GattlingBuff.big` and `zzyy_ChinaBunkers.big` (whose files it
layers on) but before `zzz_ControlBarPro*.big` (UI skin).

## Design

The Overlord's shared per-object upgrade and button are reused as-is — no
new upgrades, art or CSF strings:

- `Upgrade_ChinaOverlordPropagandaTower` (Type = OBJECT, BuildCost 500,
  SSOLSpeaker button image, existing `CONTROLBAR:UpgradeChinaOverlord…`
  labels), bound via the existing
  `Command_UpgradeChinaOverlordPropagandaTower` button at **slot 10** (the
  same slot the Overlord family uses) of each Battlemaster command set.

Per tank, an `ObjectCreationUpgrade` fires an existing OCL that spawns the
tower rider with `ContainInsideSourceObject = Yes`, plus a `ProductionUpdate`
(`MaxQueueEntries = 1`) because OBJECT_UPGRADE purchases run through the
unit's own production queue (same as Overlord/Helix).

| Object | General | Rider object (via OCL) |
|---|---|---|
| `ChinaTankBattleMaster_Var1` (Var2-4 reskins inherit the behaviors) | vanilla China | `ChinaTankOverlordPropagandaTower` (`OCL_OverlordPropagandaTower`) |
| `Nuke_ChinaTankBattleMaster` | Nuke (Tao) | `ChinaTankOverlordPropagandaTower_Nuke` (`OCL_OverlordPropagandaTower_Nuke`) |
| `Tank_ChinaTankBattleMaster` | Tank (Kwai) | `ChinaTankOverlordPropagandaTower` (vanilla — see below) |
| `Spec_ChinaTankBattleMaster` (Ravage) | Special Weapons | `ChinaTankOverlordPropagandaTower` (vanilla — no Spec tower exists) |

**Kwai rider note**: ShockWave defines `Tank_OCL_OverlordPropagandaTower`,
but it references `Tank_ChinaTankOverlordPropagandaTower`, an object that is
**not defined anywhere** — a dead OCL. The vanilla rider is used instead;
retail precedent for cross-general reuse: the Nuke and Infantry generals'
Helixes mount the `Side = China` `ChinaHelixPropagandaTower`. All ShockWave
tower riders share identical stats (radius 150, 1 %/s heal, 2 %/s with
Subliminal Messaging).

### Contain / mounting (engine-source verified)

- Vanilla/Nuke/Spec: the china-bunkers `TransportContain ModuleTag_BunkerBay01`
  becomes **`HelixContain`** with identical fields (4 infantry slots,
  fire ports, garrison sounds). `HelixContain.cpp`: the first
  PORTABLE_STRUCTURE goes into a dedicated rider slot **outside** the
  passenger list — `isValidContainerFor` returns TRUE for it regardless of
  `AllowInsideKindOf`, it consumes no seats, never appears on exit buttons,
  and is position-synced to the tank every frame.
- Kwai already had HelixContain (ERA rider). Its passenger allow-list is
  narrowed from `INFANTRY PORTABLE_STRUCTURE` to `INFANTRY`: HelixContain
  has **no rider replacement** (first portable wins; a second would fall
  through into a passenger seat), and an OCL payload the contain refuses is
  cleanly destroyed (`ObjectCreationList.cpp` ContainInsideSourceObject
  path), so overflow portables can no longer steal infantry seats.

### Tower visibility

The rider draws itself with `W3DDependencyModelDraw`, which only renders
after the **container's** draw module calls
`notifyDrawableDependencyCleared()` — only the `W3DOverlord*Draw` family
does. `W3DOverlordTankDraw` is a strict drop-in extension of `W3DTankDraw`
(no extra INI fields; Kwai's Battlemaster already uses it), so one
`W3DTankDraw` per drawable is converted:

- vanilla `_Var1` `ModuleTag_01`, `_Var2`/`_Var3` `ModuleTag_Chassis01`,
  `_Var4` `ModuleTag_Turret01` (reskins own their draw sets — engine
  clears inherited draw modules when a reskin defines its own),
- Nuke and Ravage `ModuleTag_01`.

The tower attaches to bone `FIREPOINT01`; the Battlemaster models don't
have it, so the engine falls back to the hull origin (verified fallback in
`W3DDependencyModelDraw::adjustTransformMtx`) — the tower sits centered on
the hull.

### Kwai: tower vs ERA armor (mutually exclusive)

The HelixContain rider slot holds exactly one portable structure, so the
tower and the ERA plate rider (`ChinaTankArmorUpgradeAddon_BattleMaster`,
spawned per-tank when the player-level `Upgrade_TankLightArmor` completes)
are made mutually exclusive:

- the tower's `ObjectCreationUpgrade` has
  `ConflictsWith = Upgrade_TankLightArmor` (player + object upgrade masks
  are OR'd when modules are tested), and
- a `CommandSetUpgrade` swaps Kwai Battlemasters to
  `Tank_ChinaVehicleBattleMasterCommandSetERA` (identical set minus the
  tower button) when ERA completes — the button disappears instead of
  letting the player waste $500 on a tower that can no longer mount.
- **Reverse order** (tower bought before ERA is researched): the tank keeps
  its tower and still receives ERA's stat boost (+115 HP and the upgraded
  armor set are modules on the tank itself); only the cosmetic ERA plate
  rider is skipped on that tank.

## Files in the archive (full patched copies, original internal paths)

All five effective sources came from `zzyy_ChinaBunkers.big` (the sibling
`zzyz_GattlingBuff.big` exists but contains only gattling files + Weapon.ini
— no overlap; the build checks it first anyway):

| File | Changes |
|---|---|
| `Data\INI\Object\China\Vanilla\Vehicles\BattleMaster.ini` | contain→Helix, tower OCU + ProductionUpdate, 4 draw conversions (Var1-4) |
| `Data\INI\Object\China\Nuke\Vehicles\BattleMaster.ini` | contain→Helix, tower OCU (Nuke OCL) + ProductionUpdate, draw conversion |
| `Data\INI\Object\China\Tank\Vehicles\BattleMaster.ini` | allow-list narrowed, tower OCU (+ConflictsWith), CommandSetUpgrade, ProductionUpdate |
| `Data\INI\Object\China\SpecialWeapons\Vehicles\RavageTank.ini` | contain→Helix, tower OCU + ProductionUpdate, draw conversion |
| `Data\INI\CommandSet.ini` | `10 = Command_UpgradeChinaOverlordPropagandaTower` on all four Battlemaster sets; new `Tank_ChinaVehicleBattleMasterCommandSetERA` |

Prior layers are preserved and verified at build time (build fails if they
drift): Battlemaster `MaxHealth 480` / Ravage `576` (china-tank-buff),
4-slot bunker bays + exit buttons (china-bunkers), and the Mammoth's
`Armor_AmericaTankPaladinCommandSet` hunk (mammoth-bunker).

## Rebuild

```
python3 build.py
```

Reads the effective sources (zzyz_GattlingBuff → zzyy_ChinaBunkers →
zzy_MammothBunker → zzx_ChinaTankBuff → zz_SPE_Shw_ini → !Shw_ini),
re-applies exact-text patches (fails loudly on upstream drift), verifies
prior-layer survival and block balance, writes `zzyzz_PropTowers.big` here,
re-reads it for round-trip integrity and installs into both mod dirs.
Depends on `../hotkey-addon/bigfile.py`.

**Rebuild order note**: if any earlier layer (`zzx_ChinaTankBuff`,
`zzy_MammothBunker`, `zzyy_ChinaBunkers`, `zzyz_GattlingBuff`) is rebuilt
with different content, rebuild this archive too — it embeds full copies of
their files and, being later-alphabetical, would silently mask their newer
versions. Correct rebuild order: china-tank-buff → mammoth-bunker →
china-bunkers → gattling-buff → **battlemaster-proptower**.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzyzz_PropTowers.big`
- `~/GeneralsX/mods/ShockWave/zzyzz_PropTowers.big`

## Uninstall

Delete `zzyzz_PropTowers.big` from both directories above.

## Known limitations / risks

- **Save games**: module lists changed for all Battlemasters — saves that
  cross an install/uninstall boundary may fail to load. Start fresh
  missions/skirmishes.
- The tower renders at the hull center (no FIREPOINT01 bone in the
  Battlemaster models) and may intersect the turret slightly; the
  propaganda pulse FX and healing radius are unaffected.
- The upgrade is once-per-tank and not refundable/removable (same as the
  Overlord's). After purchase the button shows as already-produced.
- On Kwai tanks the tower button disappears for ALL Battlemasters once ERA
  armor is researched (player-level upgrade) — by design, since the ERA
  rider claims the single rider slot on every existing and future tank.
- The three towers-on-tracks generals reuse the vanilla-China rider (Spec
  has no own variant; Kwai's is broken in ShockWave itself) — the only
  visible difference would have been house-color tinting behavior.
- AI generals never buy the tower (no AI scripting added); player-facing.
- Balance: a $500, per-tank aura that heals vehicles and boosts fire rate
  makes massed Battlemasters stronger — intentional, mirrors Overlord
  economics ($500 on a 700/500-cost chassis vs the Overlord's 1400).
