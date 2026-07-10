# GeneralsX Mod Survey — Research Report (2026-07-10)

Compiled by research agent; cross-checked against the GenLauncher registry, live probes of
gen.insave.ovh, GeneralsX GitHub issues/discussions, and web/ModDB research.

**Compatibility caveat:** zero public reports of big mods on GeneralsX exist — our ShockWave
1.201 test is the only confirmed data point. "Inferred" = pure 1.04 game data, no binaries.

## A. Top recommendations

| Mod | Category | Why | Compatibility | How to get |
|---|---|---|---|---|
| Rise of the Reds 1.87 PB 2.0 (+ Hanpatch 32.2) | Overhaul (5 factions) | Community-standard overhaul; Hanpatch is its active continuation | Inferred-good (pure .big) | `rotr` bucket (1.53 GB) + `https://gen.insave.ovh/rotr/hanpatch/Hanpatch%20v32.2.zip` (140 MB) |
| The End of Days 0.98.6 P11 | Overhaul (adds Russia) | High-quality models/FX, active | Inferred-good (1.12 GB) | `teod` bucket, `teod-individual-files/` |
| Contra X 10.0.2 B2 P1 | Overhaul (hardest AI) | Best challenge AI; best-looking | Inferred-good, highest data volume (2.2 GB) | `https://gen.insave.ovh/contra/mod/ContraLatestBasic.rar` (1.06 GB) or `contra` bucket |
| ShockWave Single Player Experience 2.1.3 | Campaign for ShockWave | Full campaigns + Generals Challenge on ShockWave | Inferred-good (.big + .bik) | `shspe` bucket (0.87 GB, individual files) |
| Control Bar HD (xezon) 1.1 | Graphics/UI | Upscaled button/UI art; complements Control Bar Pro | Confirmed-safe class | `https://gen.insave.ovh/operationfirestorm/ofs-individual-files/ControlBarHDBaseZH.big` (29 MB) + `ControlBarHDEnglishZH.big` (63 MB); or gentool.net/download/controlbar/ |
| Fixed Cameo Pack v2 (n5p29) | Graphics | Fixes wrong-color/obsolete cameos, 13 MB | Inferred-good (TGA) | moddb.com/addons/fixed-cameo-pack-for-zh-v2 (browser) |
| Zero Hour Enhanced 1.0.0a (BIG Files) | Graphics overhaul | Vanilla gameplay, remade terrain/UI/lighting | Inferred-OK; renderer-heavy untested | ModDB browser (2.71 GB) — INSTALLED at ~/GeneralsX/mods/Enhanced/ZHE_BIG100a |
| NProject Mod 2.11 | QoL/bugfix | "Vanilla but better": bugfixes, completed AI, cut content | Inferred-good (279 MB) | `https://gen.insave.ovh/nproject/mod/n5p29-nprojectbeta-v211.zip` |

## B. Graphics-focused

- Control Bar HD — see table; GenTool itself NOT needed.
- ZHE addons (FHD UI, HD Cameo 45 MB, HD Faction/Civilian Textures, Animated Vanilla Water) — ModDB browser, ZHE-only.
- Contra HD Cameos: `https://gen.insave.ovh/contra/contra-addons/ContraCameosHD.rar` (requires Contra).
- Shellmaps: Modified Vanilla Shellmap (103 KB, ModDB); "Shell Map for ZH (No Mods)" (10 MB, ModDB).
- Vanilla Campaigns Remastered 1.87 — vanilla campaigns inside ROTR; requires ROTR + Hanpatch. `vcr` bucket (117 MB).
- 4X Upscale Graphics Overhaul (GameReplays, ~6.5 GB) — pure textures, WIP/unreleased; GeneralsX (64-bit) arguably its best platform.
- TheSuperHackers GeneralsGamePatch — data-only but no release artifact yet; watch repo.
- Widescreen for Zero Hour (0Widescreen.big, ModDB) — ships GameData.ini; prefer SagePatch; untested at 21:9.

## C. Other gameplay/overhauls

Scriptable: Operation Firestorm Alpha 0.3.17.1 (599 MB, C&C3-in-SAGE), Zero Hour Reborn V7a0.3 (0.5 GB),
C&C Untitled 3.85 (1.37 GB), Shockwave Chaos 48.2, ShockWave Public Beta 1.25 B8
(`shockwave-public-beta-individual-files/`), ROTR Anti-Thesis Patch 0.6.5 (`atp`, 0.75 GB).
Manual (browser): Project Raptor V10a0.3, Condition Zero 0.915.1, ZH Escalated 7.1.2, Generals V2.0 1.10,
Tiberian Dawn Redux 1.5.5, Power Play 1.7.2, Revolution Project 3.06, Generals Continue 3.52,
Power of the West 1.7.5, WW2 0.28.

## D. AI / QoL

- Improved AI for ZH v1.2 (Jan 2026, ModDB browser) — reworked Hard AI, all 9 generals; REPACK AS .BIG first.
- Advanced AI Mod v2.8.9 (AEI, 1.5 MB, ModDB) — same repack advice.
- NProject 2.11 — best QoL/bugfix layer.
- SagePatch (built-in) — camera height/pitch, scroll speed, F11 screenshots; INI in ~/Library/Application Support/GeneralsX/.

### Comp-stomp / AOD maps (INSTALLED 2026-07-10 → ~/Library/Application Support/GeneralsX/GeneralsZH/Maps/)
Dark Fortress v2.0 (cnclabs id 574), Matt's Monster 1v7 mk2 (3143), Death Star (406),
AOD Pasha Challenges You (2214), Centerfold 2v6 (1590), Time To Kill + Testing Grounds (3123).
More: cnclabs.com/maps/generals/zerohour-maps.aspx?tags=8&sort=-downloads
C&C Labs curl recipe: `TOKEN=$(curl -s "https://www.cnclabs.com/downloads/details/$ID/" | grep -oE "/downloads/file/$ID/\?token=[^\"]*" | head -1); curl -L -o map.zip "https://www.cnclabs.com$TOKEN"`

## E. Download automation (gen.insave.ovh)

- List: `http://gen.insave.ovh:9000/<bucket>?list-type=2` (plain HTTP only). Fetch:
  `https://gen.insave.ovh/<bucket>/<key>` — works even for private buckets when key is known.
- Listable buckets: shockwave, rotr, contra, teod, nproject, untitled, zhreborn, operationfirestorm,
  vcr, atp, shspe, shockwavechaos, genlauncher. Private: conditionzero, projectraptor, escalatedmod,
  tbredux, cncpowerplay, revolutionproject, gencon, tpotw, ww2.
- `.gib` files = renamed `.big`.
- Registry: `https://raw.githubusercontent.com/p0ls3r/GenLauncherModsData/master/ReposModificationDataZH{,2,3,4}.yaml`
- ModDB 403s non-browser clients.

## F. Avoid / warnings

- GenTool/GenPatcher/dgVoodoo/4GB patch/GeneralsGameCode exe — Windows-only, unnecessary.
- Loose-file installs BROKEN on GeneralsX: loose Data/INI/GameData.ini crashes at launch even empty
  (discussion #118); loose .wnd silently ignored (#195). Always pack as .big via -mod.
- Known engine bugs at 3440x1440: black skirmish minimap (#187), tiny tooltip font (#183),
  ultrawide is pillarboxed not native 21:9 (PR #92).
- Dependency traps: VCR needs ROTR+Hanpatch; ZHE addons are ZHE-only.

## Engine load-order facts (confirmed from source, see hotkey-addon README)

- Game dir archives: EARLIER-alphabetical name wins (multimap append, first-found returned).
- `-mod` dir archives: prepend semantics → LATER-alphabetical name wins (reversed!).
- Loose files in game dir beat archives (but see loose-INI crash warning above).
