# Panzergrenadier Layer (ShockWave / GeneralsX)

The namesake unit layer of the Panzergrenadiers stack (Kwai / China Tank
General). Two features, shipped as top-layer file overrides + one new
object file:

1. **NEW UNIT `Tank_ChinaInfantryPanzergrenadier`** — Kwai elite assault
   infantry, replacing the Red Guard in his Barracks (slot 1, both set
   variants). Full clone of the effective vanilla `ChinaInfantryRedguard`
   with an HE rifle, an area-damage grenade launcher, +20% HP and an
   elite XP ladder. The Red Guard stub + its construct button **stay
   defined but unreferenced** (unbuildable — hotfix Hacker-Bunker
   dormancy idiom; the Barracks `QuantityModifier = Tank_ChinaInfantryRedguard 2`
   line also stays, inert).
2. **PANZERJÄGER RENAME (Kwai-scoped)** — Kwai's Tank Hunter stub
   (`Tank_ChinaInfantryTankHunter`) gains
   `DisplayName = OBJECT:TankPanzerjager` and its construct button is
   relabeled **"Panzerjäger"** with a new tooltip, via append-only
   `Generals.str` entries. The vanilla Tank Hunter object, its button and
   its labels are untouched (all 8 other generals' Tank Hunter buttons
   asserted byte-identical).

Output archive: **`zzz-ZZZZZZZZPanzergrenadier.big`** (6 files, ~2.9 MB —
INI/STR only, all art/sounds are live references; no new assets).
Case-insensitively `zzz-zzzzzzzz…` sorts **after** `zzz-ZZZZZZZXHotfix.big`
(`z` 0x7A > `x` 0x78 at char 12) and — because `-` (0x2D) < `_` (0x5F) <
`z` — **before** `zzz_ControlBarPro*.big` and `zzzz_FXEnhance.big`,
verified against the real directory listings of both mod dirs at build
time (plus the invariant that no archive sorting after ours claims any
path we ship). This is now the **last INI layer of the stack chain**
(fx-enhance is another session's layer and stays above by design).

## The unit card

| | Panzergrenadier | (Red Guard it replaces) |
|---|---|---|
| Object | `Tank_ChinaInfantryPanzergrenadier` (concrete clone, no stub) | `Tank_ChinaInfantryRedguard` → vanilla RG |
| Cost / time | **$225 / 6 s** (⇒ spec $450/12 s, see *w-economy parity*) | $200 / 6 s **for 2 men** |
| HP | **144** (+20% over the ShockWave RG's 120) | 120 |
| Rifle | **22.5 dmg / 1 s, range 135, EXPLOSION** | 18 / 1 s, range 110, SMALL_ARMS |
| Grenade | **60 dmg r15 + 25 r30, range 135, one per 8 s** (auto) | — (inert stun bullet) |
| Bayonet | donor `RedguardBayonet` (TERTIARY, manual) | same |
| XP | value 6/6/12/24, ladder 0/25/50/100 (elite: RG is 0/20/40/80) | 5/5/10/20, 0/20/40/80 |
| Vision | 135 (= rifle range; RG 100), shroud clear 200 | 100 / 200 |
| Prereq | `Tank_ChinaBarracks` | same |
| Model | **Nuke-general RG reskin** `NINRDGRD_SKN`/`_F_SKN` on the same `NICNSC` skeletons/animations — the mesh's under-barrel grenade-launcher subobject `WeaponA` is visible by default (no `HideSubObject`), plus the `Nuke_RedGuard` cameo/portrait. Zero new art. | `NICNSC_SKN` |
| Kept from donor | capture-building ability + research hook, taunt gimmick, horde bonus, parachutable, all 14 death modules, doctrine hooks (armor tiers rescaled 18 → **21.6** = 15% of 144; `WeaponBonusUpgrade`), `VeterancyGainCreate` on `SCIENCE_RedGuardTraining` (inert if Kwai can't buy it), `ChinaInfantryRedguardCommandSet` | — |
| Dropped from donor | the `RedguardStunBulletMachineGun` SECONDARY (`AutoChooseSources = SECONDARY NONE`, effectively dead on the donor; its command-set button is commented out in base data) | — |

### The rifle (`Tank_PanzergrenadierRifle`) — why EXPLOSION, not "GUN"

The spec suggested `DamageType = GUN`; **no GUN damage type exists in this
engine** (`Core/GameEngine/Include/GameLogic/Damage.h` enum — verified).
Armor-table study of the effective `Armor.ini` (unlisted type = 100%):

| DamageType | HumanArmor | HumveeArmor | TankArmor | StructureArmor |
|---|---|---|---|---|
| SMALL_ARMS (std rifles) | 100% | 50% | 25% | 50% |
| GATTLING | 100% | 50% | 10% | (100%) |
| COMANCHE_VULCAN | 100% | 50% | 25% | (100%) |
| INFANTRY_MISSILE (Tank Hunter) | 10% | 50% | 80% | 50% |
| **EXPLOSION (chosen)** | **100%** | **100%** | **100%** | **100%** |

EXPLOSION ("HE rounds") is the only type that keeps the full +25%
anti-infantry damage AND gives real vehicle/structure damage without
touching any shared armor table. 22.5 damage / 1000 ms / range 135,
donor FireFX/tracers/sound; carries the kwai-doctrine
`PLAYER_UPGRADE DAMAGE 125% / RANGE 120%` bonus lines like its sibling
weapons (post-research: 28.1 dmg, range 162).

### The grenade (`Tank_PanzergrenadierGrenade`) — and the PreferredAgainst deviation

60 EXPLOSION r15 + 25 r30 secondary, range 135 (min 5), `ClipSize 1` /
8 s auto-reload / 0.5 s aim, arcing `InfantryGrenade` projectile (Burton
OICW grenade family: `FX_OICWGrenadeImpact` detonation,
`FireOICWGrenadeBurton` launcher sound), `DeathType = EXPLODED`.

**Selection behavior (engine-verified, `WeaponSet.cpp
chooseBestWeaponForTarget`)**: the AI re-chooses weapons every frame by
single-shot damage estimate and never returns a reloading weapon while
another is ready — so the unit **opens with a grenade** on any target
(60 > 22.5) and **rifles during the 8 s reload**. The spec's
`PreferredAgainst` idiom was deliberately **not** used: a slot whose
PreferredAgainst mask matches the victim stays chosen **even while merely
reloading** ("preferred weapons are also kept if they are merely
reloading") — pinning the grenade on structures would have capped the
unit at 7.5 dps vs buildings instead of ~30. Also note
`PreferredAgainst` multi-KindOf masks are **AND**-tested
(`isKindOfMulti(mustBeSet, …)` → `testForAll`), so "INFANTRY VEHICLE"
would never match anything. The engine cannot detect *clusters*; the
grenade's area value comes from splash whenever the target has company.

### DPS / time-to-kill (base, solo, no doctrine/veterancy/horde)

"Sustained" ≈ rifle 22.5 dps + grenade (60−22.5)/8 ≈ **27 dps** vs
everything (EXPLOSION = 100% across the board).

| Target | Panzergrenadier | Red Guard rifle | Tank Hunter |
|---|---|---|---|
| Infantry (RG, 120 HP) | grenade + 3 rifle shots ≈ **3.5 s** (22.5 dps sustained +25% over RG; grenade one-shots nothing standard but splashes r15/r30) | 18 dps, 6.7 s | 4 dps (10%) |
| Humvee (240 HP) | ~27 dps → **~8 s** | 9 dps → 27 s | 20 dps → 12 s |
| Battlemaster (660 HP) | ~27 dps → **~24 s** (5-man squad ~5 s) | 4.5 dps → 147 s | 32 dps → 21 s |
| Structures | ~27 dps + r30 splash | 9 dps | 20 dps |

So vs armor one Panzergrenadier ≈ 0.85 Tank Hunters while also being the
best anti-infantry rifleman — the elite premium the $450 sticker pays for.

### w-economy parity (the baked half price)

`zzz-ZZZZZZZWEconomy.big` halves all buildable China infantry, but its
build gate **re-enumerates exactly 32 objects** and fails on a 33rd — it
cannot admit this unit without its own rebuild. So this layer bakes the
**final** halved numbers directly: `BuildCost = 225 / BuildTime = 6.0`
(= spec $450/12 s pre-halved, commented as such in the object file).
No w-economy rebuild needed; effective prices are consistent with every
other China infantryman. **If w-economy is ever rebuilt, delete this
archive from both mod dirs first** (its post-install re-enumeration would
otherwise see the Panzergrenadier and stop) — that is the standard
lower-layer rebuild rule anyway, see *Rebuild*.

## Feature 2 — the Panzerjäger rename (details)

- `Tank_ChinaInfantryTankHunter` stub: **+1 line**
  `DisplayName = OBJECT:TankPanzerjager` (the stub had no DisplayName).
- `Tank_Command_ConstructChinaInfantryTankHunter` button:
  `TextLabel` → `CONTROLBAR:ConstructTankPanzerjager` ("Panzer&jäger"),
  `DescriptLabel` → `CONTROLBAR:ToolTipTankBuildPanzerjager`. Button
  image (`SNTankHunter`), price hunks and BuildVariations untouched.
- The ä is written as latin-1 0xE4 — `GameTextManager::translateCopy`
  widens .str bytes 1:1 into widechars (`*outbuf++ = *inbuf & 0x00FF`),
  so it renders correctly.
- **Scope**: Kwai only. The 8 other Tank Hunter construct buttons and the
  vanilla labels are asserted byte-identical. **Known limitation**: the
  stub spawns the shared vanilla `ChinaInfantryTankHunter`, so a selected
  unit still reads "Tank Hunter" — the rename covers the build button,
  tooltip and queue (renaming the vanilla object would leak into vanilla
  China, out of scope per spec).

## Button / slot changes

| Command set | Slot | Was | Now |
|---|---|---|---|
| `Tank_ChinaBarracksCommandSet` | 1 | `Tank_Command_ConstructChinaInfantryRedguard` | `Tank_Command_ConstructChinaInfantryPanzergrenadier` |
| `Tank_ChinaBarracksCommandSetUpgrade` | 1 | same | same |

New button: `UNIT_BUILD`, `Nuke_RedGuard` image, "&Panzergrenadier"
(hotkey P free — Pyro holds 'y'; the TH button's freed '&T' is replaced by
'j'). Slots 2–14 byte-survive (asserted post-edit layout: 2 Panzerjäger,
3 Hacker, 4 Black Lotus, 5 Siege Soldier, 6 Flame Trooper, 7 Minigunner,
8 Sharpshooter, 9 Shmel, 10 Shock Trooper, 12 Capture research,
13 Mines/EMP-Mines, 14 Sell).

## Files in the archive (6)

| File | Effective source (owner archive) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZXHotfix.big` | 2 slot lines replaced (Barracks ×2 variants) |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZZZWEconomy.big` | +1 construct button appended; 2 label lines swapped inside the Kwai TH button |
| `Data\Generals.str` | `zzz-ZZZZZZZTTeslaCoil.big` | +6 entries appended (append-only) |
| `Data\INI\Weapon.ini` | `zzz-ZZZZZZZTTeslaCoil.big` | +2 weapon blocks appended (append-only) |
| `…\China\Tank\Infantry\Panzergrenadier.ini` | new file (clone of `zzz-ZZZZZZZWEconomy.big`'s vanilla `Redguard.ini`) | the unit |
| `…\China\Tank\Infantry\TankHunter.ini` | `zzz-ZZZZZZZWEconomy.big` | +1 DisplayName line |

New identifiers: `Tank_ChinaInfantryPanzergrenadier`,
`Tank_PanzergrenadierRifle`, `Tank_PanzergrenadierGrenade`,
`Tank_Command_ConstructChinaInfantryPanzergrenadier` + 6 string labels —
all word-boundary collision-checked against the whole effective INI/STR
space (including the bare words "Panzergrenadier"/"Panzerjager").

## Build-time verification (all enforced; build fails loudly otherwise)

- Sort position + effective ownership for all 6 sourced/guarded files;
  sources read **only** from archives sorting strictly below this one;
  no later archive claims any shipped path (both dirs).
- **Exact line-multiset diff audits on all 5 patched files** (clone vs
  donor: −29/+47 lines, all planned; CommandSet −2/+2; CommandButton
  −2/+15; TankHunter −0/+1; Weapon.ini/Generals.str append-only with
  block/entry-count balance).
- Donor drift guards: RG rifle 18/110/1000 ms/SMALL_ARMS + doctrine bonus
  lines; armor-table facts the EXPLOSION choice rests on (no explicit
  EXPLOSION row in Human/Humvee/Tank/Structure armor, TankArmor
  SMALL_ARMS 25%); Nuke-RG reskin facts (NINRDGRD meshes on NICNSC
  skeletons, WeaponA subobject idiom); `InfantryGrenade` arc behavior;
  FX/sounds/upgrades/science existence; Kwai TH button pre-edit labels.
- Clone integrity: module-tag census identical to donor; stun bullet
  gone; bayonet + donor command set + skeleton references kept; no
  vanilla mesh names left.
- Post-edit layouts: both Barracks sets exact (slots 5–10 siblings
  survive); dozer page 2 exact hotfix layout (Hacker Bunker button still
  removed, Tesla Coil at 9); WF page 2, CC UAV deploy, IC/HackerBunker
  sets, vanilla RG unit set — all asserted.
- Closure: every slot of the edited sets resolves to a CommandButton;
  new button → object → weapons → projectile/FX/sounds → labels all
  resolve in the shipped+effective space; dormant RG button/stub still
  defined with **zero** CommandSet references; 8 other TH buttons
  byte-identical.
- BIG round-trip byte-identity; installed archives re-read and
  byte-compared; post-install effective-space audit in both dirs (our 6
  paths owned by us with exact bytes, neighbours keep owners); rebuild is
  **hash-idempotent** (verified). **The game was deliberately not
  launched.**

## Rebuild

```
python3 build.py
```

Reads effective sources from `~/GeneralsX/mods/ShockWaveSPE` (excluding
its own archive and everything sorting above it), patches, verifies,
writes `zzz-ZZZZZZZZPanzergrenadier.big` here and installs to both mod
dirs. Depends on `../hotkey-addon/bigfile.py`.

**Rebuild-order note**: this is now the **last INI layer of the stack
chain**. If any lower layer is rebuilt (hotfix, w-economy, vehicle-kit,
tesla-coil, rotr-infantry, kwai-infantry, …), rebuild this archive
afterwards — it embeds full copies of their files (CommandSet.ini from
hotfix, CommandButton.ini/TankHunter.ini from w-economy,
Weapon.ini/Generals.str from tesla-coil). Conversely, lower layers'
builds must not see this archive: **delete
`zzz-ZZZZZZZZPanzergrenadier.big` from both mod dirs first** (w-economy's
32-infantry enumeration gate in particular would fail while our unit is
installed), rebuild the lower chain in its documented order (… →
w-economy → hotfix), then rerun this build. (`zzzz_FXEnhance.big` belongs
to another session and is never read or rebuilt by this layer.)

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZZPanzergrenadier.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZZPanzergrenadier.big`

## Uninstall

Delete `zzz-ZZZZZZZZPanzergrenadier.big` from both directories above. No
other files are touched. (Uninstalling restores the Red Guard in Barracks
slot 1 and the "Tank Hunter" button labels; Panzergrenadiers in old saves
become undefined — start fresh.)

## Known limitations / balance

- **Kwai loses the Red Guard entirely** (by design): the ×2-per-purchase
  $200 pair is replaced by one $225 elite. The dormant stub, button and
  `QuantityModifier` line remain for a clean uninstall.
- The grenade is auto-chosen vs **any** target when loaded, including a
  single infantryman (the engine estimates single-shot damage and cannot
  see clusters) — mildly wasteful, self-corrects in 8 s; the rifle covers
  the reload. `MinimumAttackRange 5` can make the unit nudge back a step
  at point-blank (flashbang-Ranger precedent).
- EXPLOSION rifle rounds do full damage to everything, including
  structures — intended (HE flavor); it still cannot attack aircraft
  (no anti-air flags, donor parity).
- A selected Panzerjäger still reads "Tank Hunter" (shared vanilla object
  spawned by the stub; rename is Kwai-scoped by spec).
- The `WeaponA` launcher tube shows on the Nuke-RG mesh at all times
  (deliberate — the unit always owns the grenade launcher). Firing
  animations reuse the rifle pose for grenade throws (donor stun-bullet
  precedent, cosmetic).
- Panzergrenadier grenade/rifle benefit from kwai-doctrine research and
  the capture ability uses the shared Barracks research — no new AI
  behavior anywhere (AI never builds the unit; no build-list changes).
- Save games crossing an install/uninstall boundary may not load (new
  object type, command-set line changed). Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes and the GeneralsX engine source
  (GeneralsMD + Core trees).
