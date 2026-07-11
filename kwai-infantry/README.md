# Kwai Infantry (ShockWave / GeneralsX) — v2

Mini-mod for C&C Generals Zero Hour: ShockWave under GeneralsX. THREE new
Barracks infantry for **Kwai (China Tank General)**: two ShockWave
cross-general build stubs plus a **simple sniper cloned from the vanilla
USA Pathfinder**.

Output archive: **`zzz-ZZZZZZZLKwaiInfantry.big`** (6 files, ~1.7 MB —
INI/STR only; all art, sounds and mechanics are live references into the
effective space). Case-insensitively `zzz-zzzzzzzl…` sorts **after**
`zzz-ZZZZZZZKwaiPDL.big` (`k` < `l` at char 11; PDL owns the
CommandSet/CommandButton/Generals.str this layers on) and **before**
`zzz-ZZZZZZZTTeslaCoil.big` / `zzz-ZZZZZZZVehicleKit.big` /
`zzz-ZZZZZZZWEconomy.big` — three layers that embed files derived from
this one and are **rebuilt after it** (see Rebuild order), and before any
`zzz-ZZZZZZZR*` probe / `zzz_ControlBarPro*.big`. Verified against the
real directory listings of both mod dirs at build time.

## v2 — the ZHE Sharpshooter port was REMOVED

v1 shipped a full port of **Zero Hour Enhanced's ChinaInfantrySharpshooter**
(176 donor INI blocks — 4 build variations, prone rider-switch system,
claymore AP-mine mode, area recon, wounded bodies — plus 47 W3D files,
33 textures, 101 wav samples, 28 audio events, 18 string entries; 199
files, 29.6 MB). After **two mid-skirmish crashes with the port as prime
suspect** (user-observed "dark tile" under snipers pointing at shadow/
asset problems), the port was **removed in its entirety** — zero ZHE
machinery remains in this layer (build-asserted against a ZHE-marker
list). The replacement is a deliberately boring stock-mechanics clone.
v1's build script and README are archived at
`work/build_v1_zhe_port.py.bak` / `work/README_v1_zhe_port.md.bak`; the
`work/` closure-tracing tooling (`portset.py` etc.) is kept for reference
and for the residue sweep.

## The roster (Barracks, both set variants)

| Slot | Unit | Object | Mechanism | Cost / time (this layer) | Prerequisites |
|---|---|---|---|---|---|
| 6 | **Flame Trooper** | `Tank_ChinaInfantryFlameThrower` | stub → `Spec_ChinaInfantryFlameThrower` (Leang) | $350 / 8 s | Tank_ Barracks + Tank_ War Factory (donor Spec_ pair translated) |
| 7 | **Minigunner** | `Tank_ChinaInfantryMiniGunner` | stub → `Infa_ChinaInfantryMiniGunner` (Fai; donor name verified) | $550 / 14 s | Tank_ Barracks (donor Infa_ Barracks translated) |
| 8 | **Sharpshooter** | `Tank_ChinaInfantrySharpshooter` | **full CLONE** of `AmericaInfantryPathfinder` (vanilla USA, `zz_SPE_Shw_ini.big`) | $1200 / 30 s | Tank_ Barracks + Tank_ Propaganda Center |

**NOTE — w-economy override**: the `zzz-ZZZZZZZWEconomy.big` layer above
this one halves ALL buildable China infantry; in the final effective space
the three units cost **$175/4s, $275/7s and $600/15s**. This layer
deliberately ships the donor-parity 350/550/1200 values; the halving is
w-economy's business (coordinated — its build re-derives from our files).

Barracks occupancy: roster's Siege Soldier holds slot 5; 6–8 now used,
**9–11 remain free**; 12–14 untouched.

## The v2 Sharpshooter (Pathfinder clone)

kwai-roster Scout Car idiom: a full copy of the effective vanilla-USA
Pathfinder with an exact line-multiset-audited edit list — **stock
stealth-sniper mechanics, nothing exotic** (no prone system, no mines, no
recon pulse, no wounded bodies):

- `USAPathfinderSniperRifle` (stock SNIPER weapon), 120 HP, innate
  stealth while stationary (reveals on move/fire), stealth detector,
  `AmericaInfantryPathfinderCommandSet` (attack-move/guard/stop), donor
  AIPFDR/ASPFDR models + snow variant + `SAPathfinder1`/`_L` cameo — all
  live references, **no new assets shipped**.
- Documented edits (the only diffs vs the donor): renamed;
  `Side = ChinaTankGeneral`; prereqs `Tank_ChinaBarracks` +
  `Tank_ChinaPropagandaCenter` (donor's `SCIENCE_Pathfinder` gate
  **dropped** — Kwai's promotion tree can't buy it, kwai-artillery
  precedent); $1200 / 30 s per spec (donor 600/10); **RedGuard voice set
  wholesale** (`RedGuardVoiceSelect/Move/Attack/Fear/Create/Garrison` —
  China-ish voices per spec; drift-guarded against the effective
  Redguard); USA-only upgrade-cameo hints commented out (the inert
  `ArmorUpgrade`/`ExperienceScalarUpgrade` modules stay — those upgrades
  are unresearchable for Kwai).
- Strings: this layer authors its own three entries
  (`OBJECT:KwaiSharpshooter`, `CONTROLBAR:ConstructKwaiSharpshooter`,
  `CONTROLBAR:ToolTipKwaiBuildSharpshooter`) — fresh label names, no ZHE
  text or ZHE label names.
- The construct button keeps its v1 name
  `Tank_Command_ConstructChinaInfantrySharpshooter` (so the CommandSet
  slot-8 lines are byte-identical to v1 — zero churn in the layers above).
- Donor-parity danglers (ShockWave's own, pre-existing): the donor text
  references `FX_IfantryTeslaDie` / `OCL_TeslaDeathInfantry` on its
  EXTRA_3 death module without defining them anywhere — dozens of stock
  USA infantry share this; the clone keeps the lines (build-verified as
  donor-parity-only).

## Files in the archive (6)

| File | Based on (effective owner) | Change |
|---|---|---|
| `Data\INI\CommandSet.ini` | `zzz-ZZZZZZZKwaiPDL.big` | +6 lines (Barracks slots 6–8, both variants), 0 removed |
| `Data\INI\CommandButton.ini` | `zzz-ZZZZZZZKwaiPDL.big` | +3 construct buttons appended |
| `Data\Generals.str` | `zzz-ZZZZZZZKwaiPDL.big` | +3 entries appended (own text) |
| `…\China\Tank\Infantry\FlameTrooper.ini` | new file | stub |
| `…\China\Tank\Infantry\MiniGunner.ini` | new file | stub |
| `…\China\Tank\Infantry\Sharpshooter.ini` | new file | the Pathfinder clone |

## Build-time verification (all enforced; build fails loudly otherwise)

- **ZHE-residue guard**: shipped text asserted free of every v1 ZHE marker
  (object/weapon/voice/cameo/label names); exactly 6 files, none of them
  art/audio.
- Sources are read ONLY from archives sorting **strictly below** this one
  (tesla-coil/vehicle-kit/w-economy/VetInsignia/fx-enhance/ControlBarPro
  are excluded — the first three embed our files and are rebuilt after).
- Ownership asserted (CS/CB/STR = PDL; donor files incl. the vanilla
  Pathfinder = zz_SPE_Shw_ini, Redguard = kwai-doctrine, roster
  SiegeSoldier); 3 new INI paths unclaimed; 6 new identifiers + 3 new
  labels collision-checked.
- Donor drift guards: flame trooper 350/8 + Spec_ prereqs, minigunner
  550/14 + Infa_ prereq, Pathfinder 600/10 + Barracks + the
  `SCIENCE_Pathfinder` line we drop (and that Kwai's rank sets can't buy),
  RedGuard voice events defined AND in use by the effective Redguard.
- Clone audit: exact line-multiset diff vs the donor (only the documented
  transforms + header); stub/clone closure (BuildVariations targets,
  prereqs, weapon/armor/locomotor/commandset/FX/OCL/labels/cameos resolve;
  cameo lookups case-insensitive like the engine); exactly one
  BuildCost/BuildTime line in the sniper block (w-economy's patch
  contract).
- Sibling survival on shipped and installed bytes: PDL 17 slot-9 buttons +
  7 state sets, roster WF page 2 / Airfield 3–4 / Barracks 5, UAV IC sets,
  doctrine's 50 prop-center sets, artillery, mammoth-bunker stems, dozer
  pages, basetech, emperor-bunker, garrisons ≥60 Evacuates, proptower ERA
  — and the v1 ZHE command sets asserted GONE.
- Sort position vs both real listings; installed archives re-read and
  byte-compared; rebuild idempotent (hash-stable).
  **The game was deliberately not launched.**

## Rebuild ORDER (this layer + the chain above it)

```
python3 build.py                  # this layer (installs to both mod dirs)
cd ../tesla-coil   && python3 build.py
cd ../vehicle-kit  && python3 build.py
cd ../w-economy    && python3 build.py
```

The three upper layers embed full copies of files this layer owns
(CommandSet/CommandButton/Generals.str and, for w-economy, the three
infantry object files) — **always rebuild them, in that order, after
rebuilding this layer**. Their build scripts source only archives sorting
strictly below themselves (fixed as part of the v2 chain rebuild), so no
manual archive deletion is needed. `zzz-ZZZZZZZVetInsignia.big` shares no
INI files (verified — 1 texture + its own MappedImages INI) and needs no
rebuild. `zzzz_FXEnhance.big` is owned by another session: as of this
rebuild it still embeds stale v1 ZHE FXList/ParticleSystem blocks
(orphaned definitions, nothing references them — dormant); its own
rebuild will clear them.

Conversely, if any layer BELOW is rebuilt (kwai-pdl, kwai-uav,
kwai-roster, chaos-units, …), rebuild this layer and then the chain above
in the documented order.

## Install locations

- `~/GeneralsX/mods/ShockWaveSPE/zzz-ZZZZZZZLKwaiInfantry.big`
- `~/GeneralsX/mods/ShockWave/zzz-ZZZZZZZLKwaiInfantry.big`

## Uninstall

Delete `zzz-ZZZZZZZLKwaiInfantry.big` from both directories above, then
rebuild tesla-coil, vehicle-kit and w-economy (their embedded copies
reference the three units' buttons/slots). No other files are touched.

## Notes / accepted limitations / balance

- The Sharpshooter is exactly a re-badged Pathfinder: same rifle, same
  stealth profile, same 120 HP, same counters. At $1200/30s (donor
  600/10) it is priced as a specialist; w-economy then halves it to
  600/15 like all China infantry.
- RedGuard voices on a sniper are a flavor remap (the Pathfinder voice
  set stays defined and in use by real Pathfinders).
- Flame Trooper: Leang's White Napalm tier is Leang-only research — the
  unit fires base napalm for Kwai (inert hook, roster precedent).
  Minigunner: benefits from Chain Guns (Kwai researches it at his
  Propaganda Center) and the shared Capture Building research.
- Pathfinder cameo (`SAPathfinder1`) on a China unit is reused stock art
  (per spec: no new assets).
- AI never builds any of the three (no AI build-list changes).
- Save games crossing the v1→v2 boundary will NOT load (hundreds of
  object/module types removed). Start fresh.
- NOT verified in-game (deliberately not launched); all verification is
  static against the installed bytes.

## v1 asset provenance (historical)

v1's Sharpshooter was ported from **Zero Hour Enhanced** (local archives
at `~/GeneralsX/mods/Enhanced/ZHE_BIG100a/`); all ZHE-derived content was
removed in v2. Flame Trooper / Minigunner remain **C&C ShockWave**
(SWR Productions) donor units referenced in place. Personal use only.
